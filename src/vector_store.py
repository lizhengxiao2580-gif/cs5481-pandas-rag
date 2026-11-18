"""Persistent Qdrant indexes, with a shared committed set of indexed pages."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
import uuid
from array import array
from contextlib import closing, contextmanager
from dataclasses import replace
from pathlib import Path
from math import fsum, sqrt
from threading import RLock
from typing import TYPE_CHECKING

from chunk import STRATEGIES, chunk_documents
from corpus import read_baseline, read_uploads
from model_api import RAGError, check_endpoint, embed, endpoint_url
from settings import Settings

if TYPE_CHECKING:
    from qdrant_client import QdrantClient

LOCK = RLock()
BUILD_LOCK = RLock()
STATE_FILE = "index.json"
FORMAT_VERSION = 1


def index_profile(settings: Settings, corpus_hash: str) -> dict:
    if not settings.embedding.model:
        raise RAGError("Configure an embedding model in Settings.")
    # Bind the index to the endpoint without publishing a private base URL.
    address_hash = hashlib.sha256(endpoint_url(settings.embedding).encode()).hexdigest()
    return {
        "format": FORMAT_VERSION,
        "endpoint": address_hash,
        "model": settings.embedding.model,
        "requested_dimensions": settings.dimensions,
        "query_instruction": settings.query_instruction,
        "tokenizer": settings.tokenizer,
        "chunk_size": settings.chunk_size,
        "overlap": settings.overlap,
        "corpus": corpus_hash,
    }


def index_path(settings: Settings, profile: dict) -> Path:
    digest = hashlib.sha256(json.dumps(profile, sort_keys=True).encode()).hexdigest()[:24]
    return settings.store / digest


def library_path(settings: Settings, library_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{24}", library_id):
        raise RAGError("Invalid vector library ID.")
    return settings.store / library_id


def stored_indexes(settings: Settings) -> dict[str, dict]:
    return {path.parent.name: read_index_state(path.parent)
            for path in sorted(settings.store.glob(f"*/{STATE_FILE}"))
            if re.fullmatch(r"[0-9a-f]{24}", path.parent.name)}


def locate_index(settings: Settings, corpus_hash: str) -> tuple[Path, dict]:
    """Resolve an explicit library or keep existing implicit on-disk IDs working."""
    profile = index_profile(settings, corpus_hash)
    if settings.library_id:
        path = library_path(settings, settings.library_id)
        state = read_index_state(path)
        if state and state["profile"]["corpus"] != corpus_hash:
            raise RAGError("This library was built for another corpus version. Select or create a matching library.")
        return path, state

    path = index_path(settings, profile)
    if state := read_index_state(path):
        return path, state
    for library_id, state in stored_indexes(settings).items():
        original = state["profile"]
        candidate = index_path(settings, original)
        if candidate.name == library_id and all(
            original.get(key) == value for key, value in profile.items() if key != "query_instruction"
        ):
            return candidate, state
    return path, {}


def read_index_state(directory: Path) -> dict:
    path = directory / STATE_FILE
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def active_index_state(settings: Settings) -> dict:
    _, _, corpus_hash = read_baseline()
    _, state = locate_index(settings, corpus_hash)
    return state


def original_binding(settings: Settings, state: dict) -> bool:
    profile = state["profile"]
    candidate = index_profile(settings, profile["corpus"])
    return (candidate["endpoint"] == profile["endpoint"] and candidate["model"] == profile["model"]
            and settings.dimensions in (profile["requested_dimensions"], state["dimensions"]))


def verify_binding(settings: Settings, directory: Path, state: dict, public_ids: set[str]) -> None:
    """Calibrate a different endpoint against stored document embeddings."""
    if settings.dimensions is not None and settings.dimensions != state["dimensions"]:
        raise RAGError(f"This library requires {state['dimensions']:,} dimensions. Update the embedding settings.")
    if original_binding(settings, state):
        return

    from qdrant_client import models

    samples = {}
    with open_store(directory) as client:
        # Sample only tracked public documents, never local uploads, across several pages.
        for doc_id in sorted(public_ids)[::max(1, len(public_ids) // 3)][:3]:
            points, _ = client.scroll("fixed_size", limit=1, with_vectors=True, scroll_filter=models.Filter(must=[
                models.FieldCondition(key="doc_id", match=models.MatchValue(value=doc_id))
            ]))
            if points:
                samples[points[0].payload["text"]] = points[0].vector
    if len(samples) < min(3, len(public_ids)) or not samples:
        raise RAGError("The library does not contain enough public samples to check compatibility.")

    texts = list(samples)
    batch_size = max(1, settings.batch_size)
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        for text, vector in zip(batch, embed(settings, batch), strict=True):
            reference = samples[text]
            if len(vector) != len(reference):
                raise RAGError(f"This endpoint returned {len(vector):,} dimensions. The library requires {len(reference):,}.")
            dot = fsum(a * b for a, b in zip(vector, reference, strict=True))
            norm = sqrt(fsum(x * x for x in vector) * fsum(x * x for x in reference))
            if not norm or dot / norm < 0.999:
                raise RAGError("The sample vectors differ from this library. Use a compatible model or create a new library.")


@contextmanager
def open_store(directory: Path):
    from qdrant_client import QdrantClient

    # The embedded Qdrant client allows one open client per directory.
    with LOCK:
        client = QdrantClient(path=str(directory / "qdrant"), force_disable_check_same_thread=True)
        try:
            yield client
        finally:
            client.close()


def ensure_collections(client: QdrantClient, dimension: int) -> None:
    from qdrant_client import models

    for strategy in STRATEGIES:
        if not client.collection_exists(strategy):
            client.create_collection(
                collection_name=strategy,
                vectors_config=models.VectorParams(size=dimension, distance=models.Distance.COSINE),
            )
            continue
        params = client.get_collection(strategy).config.params.vectors
        if params.size != dimension:
            raise RAGError("The endpoint now returns a different vector dimension. Update the embedding profile.")


def update_indexes(settings: Settings, *, public_only: bool = False, progress=None,
                   report=None, checkpoint=None) -> dict:
    from qdrant_client import models

    check_endpoint(settings.embedding, "embedding")
    if settings.batch_size < 1:
        raise RAGError("Embedding batch size must be at least one.")
    docs, sections, corpus_hash = read_baseline()
    directory, _ = locate_index(settings, corpus_hash)
    if not public_only:
        current_ids = {doc["doc_id"] for doc in docs}
        for upload in read_uploads():
            if upload["doc"]["doc_id"] not in current_ids:
                docs.append(upload["doc"])
                sections.extend(upload["sections"])

    with BUILD_LOCK:
        if checkpoint:
            checkpoint()
        state = read_index_state(directory)
        profile = state.get("profile") or index_profile(settings, corpus_hash)
        settings = replace(settings, tokenizer=profile["tokenizer"], chunk_size=profile["chunk_size"],
                           overlap=profile["overlap"])
        ready = set(state.get("documents", []))
        pending = [doc for doc in docs if doc["doc_id"] not in ready]
        if not pending:
            return state
        pending_ids = {doc["doc_id"] for doc in pending}
        sections = [row for row in sections if row["doc_id"] in pending_ids]
        chunks = {
            strategy: list(chunk_documents(pending, sections, strategy, settings))
            for strategy in STRATEGIES
        }
        texts = list(dict.fromkeys(chunk["text"] for rows in chunks.values() for chunk in rows))
        if not texts:
            raise RAGError("The selected documents contain no indexable text.")

        vectors, dimension = embed_pending(settings, directory, texts, state.get("dimensions"),
                                           progress, report, checkpoint)

        for strategy, rows in chunks.items():
            if checkpoint:
                checkpoint()
            if report:
                report(strategy, 0, len(rows))
            with open_store(directory) as client:
                ensure_collections(client, dimension)
                for start in range(0, len(rows), 128):
                    batch = rows[start:start + 128]
                    client.upsert(
                        collection_name=strategy,
                        points=[
                            models.PointStruct(
                                id=str(uuid.uuid5(uuid.NAMESPACE_URL, row["chunk_id"])),
                                vector=vectors[row["text"]].tolist(),
                                payload=row,
                            )
                            for row in batch
                        ],
                    )
                    if report:
                        report(strategy, start + len(batch), len(rows))

        if report:
            report("publish", 0, 0)
        if checkpoint:
            checkpoint()
        state = {
            "profile": profile,
            "dimensions": dimension,
            "documents": sorted(ready | pending_ids),
            "chunks": {strategy: state.get("chunks", {}).get(strategy, 0) + len(rows)
                       for strategy, rows in chunks.items()},
        }
        temporary = directory / "index.tmp"
        temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, directory / STATE_FILE)
        return state


def embed_pending(settings: Settings, directory: Path, texts: list[str], dimension: int | None,
                  progress, report, checkpoint) -> tuple[dict[str, array], int]:
    # A sidecar holds completed batches. Existing Qdrant files and index IDs are unchanged.
    cache_dir = directory.parent.with_name(directory.parent.name + "-work")
    cache_dir.mkdir(parents=True, exist_ok=True)
    keys = {text: hashlib.sha256(text.encode()).hexdigest() for text in texts}
    vectors = {}
    with closing(sqlite3.connect(cache_dir / f"{directory.name}.sqlite")) as cache:
        cache.execute("CREATE TABLE IF NOT EXISTS embeddings (digest TEXT PRIMARY KEY, vector BLOB NOT NULL)")
        wanted = {digest: text for text, digest in keys.items()}
        for digest, blob in cache.execute("SELECT digest, vector FROM embeddings"):
            if digest in wanted:
                vector = array("f")
                vector.frombytes(blob)
                vectors[wanted[digest]] = vector
        pending = [text for text in texts if text not in vectors]
        dimension = dimension or settings.dimensions or (len(next(iter(vectors.values()))) if vectors else None)
        if any(len(vector) != dimension for vector in vectors.values()):
            raise RAGError("Cached vectors have a different dimension from the active index.")

        if report:
            report("embedding", len(vectors), len(texts))
        for start in range(0, len(pending), settings.batch_size):
            if checkpoint:
                checkpoint()
            batch = pending[start:start + settings.batch_size]
            embedded = embed(settings, batch)
            dimension = dimension or len(embedded[0])
            if any(len(vector) != dimension for vector in embedded):
                raise RAGError("The embedding endpoint returned a different vector dimension.")
            entries = {text: array("f", vector) for text, vector in zip(batch, embedded, strict=True)}
            with cache:
                cache.executemany("INSERT OR REPLACE INTO embeddings VALUES (?, ?)",
                                  ((keys[text], vector.tobytes()) for text, vector in entries.items()))
            vectors.update(entries)
            if progress:
                progress(len(vectors), len(texts))
            if report:
                report("embedding", len(vectors), len(texts))
    assert dimension is not None
    return vectors, dimension


def retrieve_many(question: str, k: int, strategies: tuple[str, ...], settings: Settings) -> dict:
    if k < 1 or not question.strip():
        raise ValueError("Provide a non-empty question and k >= 1.")
    if any(strategy not in STRATEGIES for strategy in strategies):
        raise ValueError("Unknown chunking strategy.")
    _, _, corpus_hash = read_baseline()
    directory, state = locate_index(settings, corpus_hash)
    if not state.get("documents"):
        raise RAGError("No index matches these embedding settings. Open Library to build the indexes.")
    vector, = embed(settings, [question.strip()], query=True)
    if len(vector) != state["dimensions"]:
        raise RAGError("The current embedding dimension differs from the index. Update the embedding profile.")

    from qdrant_client import models

    # A page is searchable only after both collections have been written.
    committed = models.Filter(must=[
        models.FieldCondition(key="doc_id", match=models.MatchAny(any=state["documents"]))
    ])
    with open_store(directory) as client:
        results = {}
        for strategy in strategies:
            hits = client.query_points(
                collection_name=strategy,
                query=vector,
                query_filter=committed,
                limit=k,
                with_payload=True,
            ).points
            results[strategy] = [{**hit.payload, "score": hit.score} for hit in hits]
    return results
