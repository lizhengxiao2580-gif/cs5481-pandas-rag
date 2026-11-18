"""HTTP adapter for the local pandas Docs QA application."""
from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import asdict, replace
from threading import Lock
from time import perf_counter
from typing import Annotated, Literal
from urllib.parse import urlsplit
from uuid import uuid4
from zipfile import BadZipFile

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from chunk import STRATEGIES
from corpus import read_baseline, read_uploads, save_upload
from index_cli import BUNDLE, bundle_manifest, install_bundle
from index_job import ACTIVE, get_job, start_job
from model_api import RAGError, check_endpoint, complete, embed
from qa_api import answer_from_hits
from settings import (DEFAULT_SYSTEM_PROMPT, ROOT, Endpoint, Settings, library_bindings,
                      load_settings, save_endpoint, save_library, select_library, with_endpoint)
from vector_store import (index_path, library_path, locate_index, original_binding,
                          retrieve_many, stored_indexes, verify_binding)

DIST = ROOT / "web" / "dist"
app = FastAPI(title="pandas Docs QA", docs_url=None, redoc_url=None, openapi_url=None)
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "testserver"}
app.add_middleware(TrustedHostMiddleware, allowed_hosts=[*LOCAL_HOSTS, "[::1]"])
workspace_lock = Lock()
retrieval_lock = Lock()
retrievals: OrderedDict = OrderedDict()
Strategy = Literal["fixed_size", "structure_aware"]
Connection = Literal["embedding", "generation"]


@app.middleware("http")
async def protect_local_api(request: Request, call_next):
    if request.url.path.startswith("/api/") and request.method not in {"GET", "HEAD", "OPTIONS"}:
        origin = request.headers.get("origin")
        if origin and (urlsplit(origin).hostname not in LOCAL_HOSTS
                       or request.headers.get("sec-fetch-site") == "cross-site"):
            return JSONResponse({"detail": "Open the app locally to use this API."}, status_code=403)
    response = await call_next(request)
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RAGError)
@app.exception_handler(ValueError)
async def action_error(request: Request, exc: Exception):
    return JSONResponse({"detail": str(exc)}, status_code=400)


@app.exception_handler(RequestValidationError)
async def invalid_request(request: Request, exc: RequestValidationError):
    fields = [f"{error['loc'][-1]}: {error['msg']}" for error in exc.errors()]
    return JSONResponse({"detail": "; ".join(fields)}, status_code=422)


@app.exception_handler(OSError)
@app.exception_handler(BadZipFile)
async def storage_error(request: Request, exc: Exception):
    return JSONResponse({"detail": "A local file could not be read or written. Check the app folder and try again."},
                        status_code=409)


def configured(current: Settings, kind: Connection) -> bool:
    try:
        check_endpoint(getattr(current, kind), kind)
        return True
    except RAGError:
        return False


def current_index(current: Settings, corpus_hash: str):
    if current.embedding.base_url and current.embedding.model:
        return locate_index(current, corpus_hash)
    return None, {}


def remember_library(current: Settings, corpus_hash: str) -> None:
    try:
        path, state = current_index(current, corpus_hash)
    except RAGError:
        return
    if state and path.name not in library_bindings():
        save_library(current, path.name, current.embedding.model, activate=False)


def check_idle(current: Settings) -> None:
    job = get_job(current)
    if job and job.snapshot().state in ACTIVE:
        raise HTTPException(409, "Stop or finish the index update before changing vector libraries.")


def index_job_state(current: Settings) -> dict | None:
    job = get_job(current)
    return asdict(job.snapshot()) if job else None


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/workspace")
def workspace():
    current = load_settings()
    baseline, _, corpus_hash = read_baseline()
    public_ids = {doc["doc_id"] for doc in baseline}
    documents = baseline + [upload["doc"] for upload in read_uploads() if upload["doc"]["doc_id"] not in public_ids]
    problem = None
    try:
        path, state = current_index(current, corpus_hash)
    except RAGError as exc:
        path, state, problem = None, {}, str(exc)

    ready = set(state.get("documents", []))
    active = path.name if path and (state or current.library_id) else None
    bindings = library_bindings()
    indexes = stored_indexes(current)
    preset = None
    embed_ready = configured(current, "embedding")
    if BUNDLE.exists():
        manifest = bundle_manifest()
        preset = {"id": index_path(current, manifest["profile"]).name, "name": "Pandas documentation",
                  "pages": len(manifest["documents"]), "model": manifest["profile"]["model"],
                  "dimensions": manifest["dimensions"], "verify": not (embed_ready and original_binding(current, manifest))}
    available = []
    for library_id in dict.fromkeys([*bindings, *indexes]):
        index = indexes.get(library_id, {})
        binding = bindings.get(library_id, {})
        name = "Pandas documentation" if preset and library_id == preset["id"] else (
            binding.get("name") or index["profile"]["model"])
        available.append({"id": library_id, "name": name, "has_settings": library_id in bindings,
                          "pages": len(index.get("documents", [])), "dimensions": index.get("dimensions"),
                          "model": binding["embedding"]["model"] if binding else index["profile"]["model"]})
    return {
        "documents": [{"id": doc["doc_id"], "title": doc["title"], "scope": doc["scope"],
                       "url": doc["url"], "ready": doc["doc_id"] in ready} for doc in documents],
        "counts": state.get("chunks", {}), "dimensions": state.get("dimensions"),
        "libraries": available, "active": active, "preset": preset, "problem": problem,
        "job": index_job_state(current), "embedding_ready": embed_ready,
        "generation_ready": configured(current, "generation"), "default_strategy": current.default_strategy,
    }


def embedding_identity(current: Settings) -> tuple:
    return (current.library_id, current.embedding.base_url, current.embedding.model,
            current.dimensions, current.query_instruction)


class Question(BaseModel):
    question: str = Field(min_length=1, max_length=6000)


class AnswerRequest(BaseModel):
    retrieval_id: str
    strategy: Strategy


@app.post("/api/retrieve")
def retrieve(request: Question):
    question = request.question.strip()
    if not question:
        raise ValueError("Enter a question.")
    current = load_settings()
    started = perf_counter()
    results = retrieve_many(question, 10, tuple(STRATEGIES), current)
    key = uuid4().hex
    with retrieval_lock:
        retrievals[key] = (question, embedding_identity(current), results)
        if len(retrievals) > 32:
            retrievals.popitem(last=False)
    return {"id": key, "question": question, "results": results,
            "latency_ms": round((perf_counter() - started) * 1000)}


@app.post("/api/answer")
def answer(request: AnswerRequest):
    current = load_settings()
    with retrieval_lock:
        result = retrievals.get(request.retrieval_id)
        if result:
            retrievals.move_to_end(request.retrieval_id)
    if not result or result[1] != embedding_identity(current):
        raise HTTPException(409, "This retrieval is no longer current. Run the question again.")
    question, _, hits = result
    return answer_from_hits(question, hits[request.strategy][:5], current)


class ConnectionInput(BaseModel):
    base_url: str = Field(max_length=2000)
    model: str = Field(max_length=300)
    api_key: str | None = Field(default=None, max_length=8000)
    dimensions: int | None = Field(default=None, ge=0)
    batch_size: int = Field(default=8, ge=1, le=1024)
    query_instruction: str = Field(default="", max_length=6000)
    system_prompt: str = Field(default="", max_length=24000)


def connection_data(current: Settings, kind: Connection) -> dict:
    endpoint = getattr(current, kind)
    data = {"base_url": endpoint.base_url, "model": endpoint.model, "has_key": bool(endpoint.key()),
            "stored_key": bool(endpoint.api_key), "key_env": endpoint.api_key_env,
            "configured": configured(current, kind)}
    if kind == "embedding":
        data.update(dimensions=current.dimensions, batch_size=current.batch_size,
                    query_instruction=current.query_instruction)
    else:
        data["system_prompt"] = current.system_prompt
    return data


def edited_connection(current: Settings, kind: Connection, payload: ConnectionInput) -> Settings:
    existing = getattr(current, kind)
    updated = with_endpoint(current, kind, Endpoint(
        payload.base_url.strip(), payload.model.strip(), existing.api_key_env,
        existing.api_key if payload.api_key is None else payload.api_key.strip(),
    ))
    if kind == "embedding":
        return replace(updated, dimensions=payload.dimensions or None, batch_size=payload.batch_size,
                       query_instruction=payload.query_instruction.strip())
    return replace(updated, system_prompt=payload.system_prompt.strip() or DEFAULT_SYSTEM_PROMPT)


@app.get("/api/settings")
def get_settings():
    current = load_settings()
    return {"embedding": connection_data(current, "embedding"), "generation": connection_data(current, "generation"),
            "default_prompt": DEFAULT_SYSTEM_PROMPT}


@app.put("/api/settings/{kind}")
def update_connection(kind: Connection, payload: ConnectionInput):
    with workspace_lock:
        current = load_settings()
        if kind == "embedding":
            check_idle(current)
            _, _, corpus_hash = read_baseline()
            remember_library(current, corpus_hash)
        save_endpoint(edited_connection(current, kind, payload), kind)
        return connection_data(load_settings(), kind)


@app.post("/api/settings/{kind}/test")
def test_connection(kind: Connection, payload: ConnectionInput):
    candidate = edited_connection(load_settings(), kind, payload)
    if kind == "embedding":
        vector, = embed(candidate, ["How do I group pandas rows?"], query=True)
        return {"message": f"Connection verified · {len(vector):,} dimensions"}
    complete(candidate, [{"role": "user", "content": "Reply with OK."}], probe=True)
    return {"message": "Connection verified"}


class LibraryInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class LibraryActivation(BaseModel):
    use_current_embedding: bool = False


@app.post("/api/libraries")
def create_library(payload: LibraryInput):
    name = payload.name.strip()
    if not name:
        raise ValueError("Enter a library name.")
    with workspace_lock:
        current = load_settings()
        check_idle(current)
        check_endpoint(current.embedding, "embedding")
        _, _, corpus_hash = read_baseline()
        remember_library(current, corpus_hash)
        library_id = uuid4().hex[:24]
        save_library(current, library_id, name)
    return {"id": library_id, "message": f"Created {name}. Run Update index to add the documents."}


@app.post("/api/libraries/preset")
def load_preset():
    with workspace_lock:
        current = load_settings()
        check_idle(current)
        check_endpoint(current.embedding, "embedding")
        _, _, corpus_hash = read_baseline()
        remember_library(current, corpus_hash)
        state = install_bundle(current)
        save_library(current, state["library_id"], "Pandas documentation")
    return {"id": state["library_id"], "message": "The preset library is ready."}


@app.post("/api/libraries/{library_id}/activate")
def activate_library(library_id: str, payload: LibraryActivation):
    if not re.fullmatch(r"[0-9a-f]{24}", library_id):
        raise HTTPException(404, "Library not found.")
    with workspace_lock:
        current = load_settings()
        check_idle(current)
        docs, _, corpus_hash = read_baseline()
        indexes = stored_indexes(current)
        bindings = library_bindings()
        state = indexes.get(library_id)
        if state and state["profile"]["corpus"] != corpus_hash:
            raise RAGError("This library was built for a different corpus version.")
        remember_library(current, corpus_hash)
        if not payload.use_current_embedding and library_id in bindings:
            select_library(library_id)
        elif state:
            check_endpoint(current.embedding, "embedding")
            verify_binding(current, library_path(current, library_id), state, {doc["doc_id"] for doc in docs})
            name = bindings.get(library_id, {}).get("name") or state["profile"]["model"]
            save_library(current, library_id, name)
        else:
            raise HTTPException(404, "Library not found.")
    return {"message": "Library switched."}


@app.post("/api/index/update")
def update_index():
    with workspace_lock:
        current = load_settings()
        check_endpoint(current.embedding, "embedding")
        start_job(current)
        return index_job_state(current)


@app.post("/api/index/{action}")
def control_index(action: Literal["pause", "resume", "stop"]):
    current = load_settings()
    job = get_job(current)
    if not job or job.snapshot().state not in ACTIVE:
        raise HTTPException(409, "There is no running index update.")
    getattr(job, action)()
    return index_job_state(current)


@app.post("/api/documents/import")
def import_document(file: Annotated[UploadFile, File()], source_url: Annotated[str, Form()] = "",
                    commit: Annotated[bool, Form()] = False):
    from ingest import parse_official_upload

    limit = 200 * 1024 * 1024
    content = file.file.read(limit + 1)
    if len(content) > limit:
        raise HTTPException(413, "The HTML file exceeds the 200 MB limit.")
    doc, sections = parse_official_upload(content, source_url.strip())
    if commit:
        if not save_upload(doc, sections):
            raise HTTPException(409, "This page is already in the library.")
        return {"message": "Document imported. Update the index to make it searchable."}
    baseline, _, _ = read_baseline()
    known = {item["doc_id"] for item in baseline} | {item["doc"]["doc_id"] for item in read_uploads()}
    return {"title": doc["title"], "url": doc["url"], "sections": len(sections),
            "duplicate": doc["doc_id"] in known}


@app.get("/", include_in_schema=False)
@app.get("/library", include_in_schema=False)
@app.get("/settings", include_in_schema=False)
def frontend():
    entry = DIST / "index.html"
    if not entry.exists():
        raise HTTPException(503, "Build the frontend first: run npm install and npm run build in web/.")
    return FileResponse(entry, headers={"Cache-Control": "no-cache"})


app.mount("/assets", StaticFiles(directory=DIST / "assets", check_dir=False), name="assets")
