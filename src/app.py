"""Streamlit entry point. Run with streamlit run src/app.py."""
from __future__ import annotations

from dataclasses import replace
from time import perf_counter
from uuid import uuid4
from zipfile import BadZipFile

import streamlit as st

from chunk import STRATEGIES
from corpus import read_baseline, read_uploads, save_upload
from index_cli import BUNDLE, bundle_manifest, install_bundle
from index_job import ACTIVE, get_job, start_job
from model_api import RAGError, check_endpoint, complete, embed
from qa_api import CITATION, CODE_OR_PROSE, answer_from_hits
from settings import (DEFAULT_SYSTEM_PROMPT, Endpoint, Settings, library_bindings, load_settings,
                      save_endpoint, save_library, select_library, with_endpoint)
from vector_store import (active_index_state, library_path, locate_index, original_binding,
                          retrieve_many, stored_indexes, verify_binding)

EXAMPLES = (
    "How do I group by two columns?",
    "How do I merge DataFrames on two keys?",
    "How can I read only specific columns from a CSV?",
)

st.set_page_config(page_title="pandas Docs QA", layout="wide")
st.html("""
<style>
.block-container { max-width: 1180px; padding-top: 3rem; }
.st-key-search-panel { background: #f4f7fd; border-color: #dbe4f4; }
.st-key-answer-panel, .st-key-source-panel { border-color: #dbe4f4; }
.st-key-source-panel [data-testid="stText"] pre,
.st-key-comparison-panel [data-testid="stText"] pre { white-space: pre-wrap; overflow-wrap: anywhere; }
@media (max-width: 700px) {
    [data-testid="stHorizontalBlock"] { flex-wrap: wrap; }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-width: 100%; }
}
</style>
""")


def settings() -> Settings:
    return st.session_state["model_settings"]


def index_status(current: Settings) -> dict:
    if not current.embedding.base_url or not current.embedding.model:
        return {}
    return active_index_state(current)


def current_library_id(current: Settings, corpus_hash: str) -> str | None:
    if current.library_id:
        return current.library_id
    if current.embedding.base_url and current.embedding.model:
        try:
            path, state = locate_index(current, corpus_hash)
        except RAGError:
            return None
        if state:
            return path.name
    return None


def remember_library(current: Settings, corpus_hash: str) -> None:
    library_id = current_library_id(current, corpus_hash)
    if library_id and library_id not in library_bindings():
        save_library(current, library_id, current.embedding.model, activate=False)


def refresh_library_selection(message: str) -> None:
    st.session_state["model_settings"] = load_settings()
    for key in ("ask_result", "ask_view"):
        st.session_state.pop(key, None)
    st.session_state["library_notice"] = message
    st.rerun()


def library_manager(current: Settings, corpus_hash: str, public_ids: set[str]) -> None:
    records = library_bindings()
    indexes = stored_indexes(current)
    active = current_library_id(current, corpus_hash)
    job = get_job(current)
    busy = bool(job and job.snapshot().state in ACTIVE)
    names = {**{key: value["profile"]["model"] for key, value in indexes.items()},
             **{key: item["name"] for key, item in records.items()}}
    options = [None, *names]
    st.subheader("Vector libraries")
    st.caption(f"Active library: {names.get(active, 'None selected')}")
    chosen = st.selectbox("Local library", options, index=options.index(active) if active in options else 0,
                          format_func=lambda item: f"{names[item]} · {item[:6]}" if item else "Choose a library",
                          disabled=busy)
    can_switch = not busy and chosen is not None and chosen != active
    switch_saved = st.button("Switch library", disabled=not can_switch or chosen not in records)
    verify_current = st.button("Verify and use current embedding",
                               disabled=not can_switch or chosen not in indexes,
                               help="A different embedding binding is checked on up to three public passages.")
    if switch_saved or verify_current:
        try:
            if chosen in indexes and indexes[chosen]["profile"].get("corpus") != corpus_hash:
                raise RAGError("This library belongs to a different corpus version. Choose a matching library.")
            remember_library(current, corpus_hash)
            if switch_saved:
                select_library(chosen)
            else:
                check_endpoint(current.embedding, "embedding")
                with st.spinner("Checking the current embedding against this library..."):
                    verify_binding(current, library_path(current, chosen), indexes[chosen], public_ids)
                save_library(current, chosen, names[chosen])
            refresh_library_selection(f"Now using {names[chosen]}.")
        except (RAGError, RuntimeError, ValueError, OSError) as exc:
            st.error(str(exc))

    if BUNDLE.exists():
        try:
            manifest = bundle_manifest()
            already_matches = original_binding(current, manifest) if current.embedding.base_url and current.embedding.model else False
        except (RAGError, OSError, BadZipFile, ValueError, KeyError) as exc:
            st.error(f"Prebuilt library unavailable: {exc}")
        else:
            st.caption(f"Preset pandas library · {len(manifest['documents'])} pages · "
                       f"{manifest['profile']['model']} · {manifest['dimensions']:,} dimensions")
            label = "Load preset library" if already_matches else "Verify embedding and load preset library"
            if st.button(label, disabled=busy or not (current.embedding.base_url and current.embedding.model),
                         help="Verification uses up to three public passages when the embedding binding differs."):
                try:
                    check_endpoint(current.embedding, "embedding")
                    remember_library(current, corpus_hash)
                    with st.spinner("Checking embedding compatibility and loading the preset..."):
                        state = install_bundle(current)
                    save_library(current, state["library_id"], "Preset pandas library")
                    refresh_library_selection("Preset pandas library is ready.")
                except (RAGError, RuntimeError, OSError, BadZipFile, ValueError) as exc:
                    st.error(str(exc))

    with st.expander("Create a vector library"):
        st.caption("Uses the current embedding settings. Indexing starts when you select Update indexes.")
        with st.form("create-vector-library"):
            name = st.text_input("Library name", placeholder="Pandas with my embedding model")
            create = st.form_submit_button("Create library", disabled=busy)
        if create:
            try:
                if not name.strip():
                    raise ValueError("Enter a name for the library.")
                check_endpoint(current.embedding, "embedding")
                remember_library(current, corpus_hash)
                save_library(current, uuid4().hex[:24], name.strip())
                refresh_library_selection(f"Created {name.strip()}. Update indexes to build both strategies.")
            except (RAGError, ValueError, OSError) as exc:
                st.error(str(exc))


def search_source(hit: dict) -> None:
    for source in hit["sources"]:
        st.link_button(source["heading_path"], source["url"])
    st.text(hit["text"])


def render_answer(question: str, result: dict, strategy: str) -> None:
    if result["refused"]:
        st.subheader(question)
        st.warning(result["answer"])
        return
    answer_col, source_col = st.columns([3, 2], gap="medium")
    parts = CODE_OR_PROSE.split(result["answer"])
    for index in range(0, len(parts), 2):
        parts[index] = CITATION.sub(lambda match: f"[\\[{match[1]}\\]](#source-{int(match[1])})", parts[index])
    with answer_col:
        with st.container(key="answer-panel", border=True):
            st.caption(f"{STRATEGIES[strategy]} · {result['latency_ms'] / 1000:.2f} s")
            st.subheader(question)
            st.markdown("".join(parts))
    with source_col:
        with st.container(key="source-panel", border=True):
            st.subheader("Sources")
            for citation in result["citations"]:
                st.html(f'<span id="source-{citation["n"]}"></span>')
                with st.container(border=True):
                    st.markdown(f'**[{citation["n"]}] {citation["title"]}**')
                    excerpt = " ".join(citation["text"].split())
                    st.text(excerpt[:180] + ("…" if len(excerpt) > 180 else ""))
                    with st.expander("Read passage and source links"):
                        search_source(citation)


def compare(results: dict) -> None:
    with st.container(key="comparison-panel"):
        st.caption("Both rankings use the same question vector and corpus.")
        k = st.slider("Results per strategy", 1, 10, 5)
        for (strategy, label), column in zip(STRATEGIES.items(), st.columns(2, gap="medium"), strict=True):
            with column:
                st.subheader(label)
                for rank, hit in enumerate(results[strategy][:k], 1):
                    with st.container(border=True):
                        st.write(f"**{rank}.** {hit['sources'][0]['heading_path']}")
                        st.caption(f"Cosine similarity {hit['score']:.3f}")
                        excerpt = " ".join(hit["text"].split())
                        st.text(excerpt[:200] + ("…" if len(excerpt) > 200 else ""))
                        with st.expander("Read passage"):
                            search_source(hit)


def select_example(question: str) -> None:
    st.session_state["question_field"] = question
    st.session_state["example_question"] = question


def ask_page() -> None:
    current = settings()
    st.title("Ask the pandas docs")
    st.write("Find an answer with citations you can check in the official documentation.")
    can_retrieve = False
    try:
        check_endpoint(current.embedding, "embedding")
        can_retrieve = bool(index_status(current).get("documents"))
        if not can_retrieve:
            st.info("Build or load the indexes for this embedding model.")
            st.page_link(library, label="Open Library")
    except RAGError as exc:
        st.info(str(exc))
        st.page_link(model_settings, label="Open Settings")

    can_answer = False
    if can_retrieve:
        try:
            check_endpoint(current.generation, "generation")
            can_answer = True
        except RAGError as exc:
            st.info(f"{exc} You can still compare retrieval.")
            st.page_link(model_settings, label="Open Settings")

    st.session_state.setdefault("question_field", st.session_state.get("question_draft", ""))
    with st.container(key="search-panel", border=True):
        with st.form("question-form", border=False):
            typed = st.text_input("Question", key="question_field",
                                  placeholder="How do I merge two DataFrames?")
            strategy = st.selectbox("Answer strategy", tuple(STRATEGIES), format_func=STRATEGIES.__getitem__,
                                    index=tuple(STRATEGIES).index(current.default_strategy))
            answer_col, compare_col = st.columns(2)
            submitted = answer_col.form_submit_button("Ask pandas", type="primary", disabled=not can_answer)
            compare_only = compare_col.form_submit_button("Compare retrieval only", disabled=not can_retrieve)
        for sample, column in zip(EXAMPLES, st.columns(3, gap="small"), strict=True):
            column.button(sample, width="stretch", disabled=not can_answer, on_click=select_example, args=(sample,))

    example = st.session_state.pop("example_question", "")
    question = example or (typed.strip() if submitted or compare_only else "")
    if (submitted or compare_only) and not question:
        st.info("Enter a question to get started.")
    if question:
        st.session_state["question_draft"] = question
        st.session_state.pop("ask_result", None)
        st.session_state["ask_view"] = "Compare retrieval" if compare_only else "Answer"
        started = perf_counter()
        try:
            with st.spinner("Retrieving passages from both indexes..."):
                results = retrieve_many(question, 10, tuple(STRATEGIES), current)
        except (RAGError, RuntimeError, OSError) as exc:
            st.error(str(exc))
        else:
            run = {"question": question, "strategy": strategy, "results": results}
            if not compare_only:
                try:
                    with st.spinner("Generating a cited answer..."):
                        run["answer"] = answer_from_hits(question, results[strategy][:5], current, started=started)
                except (RAGError, RuntimeError, OSError) as exc:
                    run["error"] = str(exc)
            st.session_state["ask_result"] = run

    run = st.session_state.get("ask_result")
    if run:
        if error := run.get("error"):
            st.error(error)
        if "answer" in run:
            view = st.segmented_control("Result view", ("Answer", "Compare retrieval"),
                                        key="ask_view", label_visibility="collapsed")
            if view == "Compare retrieval":
                compare(run["results"])
            else:
                render_answer(run["question"], run["answer"], run["strategy"])
        else:
            st.subheader("Compare retrieval")
            st.caption(run["question"])
            compare(run["results"])

def upload_html(existing_ids: set[str]) -> None:
    st.subheader("Import a pandas page")
    st.caption("Upload an HTML file from the official pandas documentation.")
    revision = st.session_state.get("upload_revision", 0)
    with st.form(f"document-upload-{revision}"):
        upload = st.file_uploader("Pandas HTML file", type=["html"])
        source_url = st.text_input("Official page URL (if missing from HTML)", placeholder="https://pandas.pydata.org/docs/…")
        if st.form_submit_button("Preview import"):
            st.session_state.pop("upload_preview", None)
            if upload is None:
                st.info("Choose an HTML file.")
            else:
                try:
                    from ingest import parse_official_upload

                    st.session_state["upload_preview"] = parse_official_upload(upload.getvalue(), source_url.strip())
                except ValueError as exc:
                    st.error(str(exc))
    preview = st.session_state.get("upload_preview")
    if preview:
        doc, sections = preview
        with st.container(border=True):
            st.markdown(f'**{doc["title"]}**')
            st.link_button("Open official page", doc["url"])
            duplicate = doc["doc_id"] in existing_ids
            if duplicate:
                st.info("This page is already in the library.")
            else:
                st.caption(f"{len(sections)} sections will be added.")
            import_col, discard_col = st.columns(2)
            if import_col.button("Import page", type="primary", disabled=duplicate):
                if not save_upload(doc, sections):
                    st.warning("This page is already in the library.")
                else:
                    st.session_state.pop("upload_preview")
                    st.session_state["upload_revision"] = revision + 1
                    st.session_state["library_notice"] = "Page imported. Update indexes to make it searchable."
                    st.rerun()
            if discard_col.button("Discard preview"):
                st.session_state.pop("upload_preview", None)
                st.session_state["upload_revision"] = revision + 1
                st.rerun()


def index_controls(current: Settings, pending: set[str]) -> bool:
    job = get_job(current)
    status = job.snapshot() if job else None
    watching = bool(status and status.state in ACTIVE)

    @st.fragment(run_every=1 if watching else None)
    def render_controls() -> None:
        status = job.snapshot() if job else None
        active = status is not None and status.state in ACTIVE
        if watching and not active:
            st.rerun()

        if active:
            label = {
                "prepare": "Preparing both chunking strategies",
                "embedding": "Generating vectors",
                "fixed_size": "Writing the fixed-window index",
                "structure_aware": "Writing the structure-aware index",
                "publish": "Publishing both indexes",
            }[status.stage]
            if status.total:
                label += f" · {status.done:,} / {status.total:,}"
            fraction = status.done / status.total if status.total else float(status.stage == "publish")
            st.progress(fraction, text=label)
            messages = {
                "pausing": "Pausing after the current batch or index write.",
                "paused": "Paused. Completed vectors are saved locally.",
                "stopping": "Stopping after the current batch or index write.",
            }
            if status.state in messages:
                st.info(messages[status.state])
            left, right = st.columns(2)
            if status.state in {"paused", "pausing"}:
                left.button("Resume", on_click=job.resume)
            else:
                left.button("Pause", on_click=job.pause,
                            disabled=status.state != "running" or status.stage == "publish")
            right.button("Stop", on_click=job.stop,
                         disabled=status.state == "stopping" or status.stage == "publish",
                         help="Stop this run and keep completed vectors for the next update.")
            return

        if status and status.state == "complete":
            st.success("Index update finished.")
        elif status and status.state == "stopped":
            st.info("Update stopped. Start another update to reuse the completed vectors.")
        elif status and status.state == "failed":
            st.error(f"Index update failed: {status.error}")
            st.caption("Retrying reuses completed vectors.")

        if st.button("Update indexes", type="primary", disabled=not pending):
            start_job(current)
            st.rerun()

    render_controls()
    return bool(status and status.state == "failed")

def library_page() -> None:
    st.title("Document library")
    current = settings()
    docs, sections, corpus_hash = read_baseline()
    baseline_ids = {doc["doc_id"] for doc in docs}
    for upload in read_uploads():
        if upload["doc"]["doc_id"] not in baseline_ids:
            docs.append(upload["doc"])
            sections.extend(upload["sections"])
    try:
        index = index_status(current)
    except RAGError as exc:
        st.error(str(exc))
        index = {}
    ready = set(index.get("documents", []))

    if message := st.session_state.pop("library_notice", None):
        st.success(message)
    try:
        library_manager(current, corpus_hash, baseline_ids)
    except (RAGError, OSError, ValueError) as exc:
        st.error(str(exc))
    a, b, c = st.columns(3)
    a.metric("Pages", len(docs))
    b.metric("Sections", len(sections))
    c.metric("Searchable pages", len(ready))
    if ready:
        counts = " · ".join(f"{label}: {index['chunks'][key]:,}" for key, label in STRATEGIES.items())
        st.caption(f"{current.embedding.model} · {index['dimensions']:,} dimensions · {counts}")

    document_ids = {doc["doc_id"] for doc in docs}
    pending = document_ids - ready
    failed = set()
    try:
        check_endpoint(current.embedding, "embedding")
    except RAGError as exc:
        st.info(str(exc))
        st.page_link(model_settings, label="Open Settings")
    else:
        if index_controls(current, pending):
            failed = pending
    scope = st.selectbox("Document scope", ["All", *sorted({doc["scope"] for doc in docs})])
    rows = []
    for doc in docs:
        if scope == "All" or doc["scope"] == scope:
            doc_id = doc["doc_id"]
            status = "Searchable" if doc_id in ready else "Index failed" if doc_id in failed else "Pending"
            rows.append({"Page": doc["title"], "Scope": doc["scope"], "Sections": doc["n_sections"],
                         "Index status": status, "Source": doc["url"]})
    st.dataframe(rows, hide_index=True, width="stretch", column_config={
        "Source": st.column_config.LinkColumn("Source", display_text="Official documentation")
    })
    upload_html(document_ids)


def endpoint_form(kind: str) -> None:
    current = settings()
    endpoint = getattr(current, kind)
    job = get_job(current) if kind == "embedding" else None
    busy = bool(job and job.snapshot().state in ACTIVE)
    with st.form(f"settings-{kind}"):
        st.subheader(kind.title())
        base_url = st.text_input("Base URL", value=endpoint.base_url, placeholder="https://provider.example/v1")
        model = st.text_input("Model ID", value=endpoint.model)
        key = st.text_input("API key", type="password", value=endpoint.api_key,
                            help=f"Leave blank to read {endpoint.api_key_env} from the local environment.")
        candidate = with_endpoint(current, kind, Endpoint(
            base_url.strip(), model.strip(), endpoint.api_key_env, key.strip()
        ))
        if kind == "embedding":
            dimensions = st.number_input("Dimensions (0 uses provider default)", min_value=0,
                                         value=current.dimensions or 0, step=1)
            batch_size = st.number_input("Texts per request", min_value=1, value=current.batch_size, step=1)
            instruction = st.text_input("Query instruction (optional)", value=current.query_instruction,
                                        placeholder="Retrieve pandas documentation relevant to the question.")
            candidate = replace(candidate, dimensions=dimensions or None, batch_size=batch_size,
                                query_instruction=instruction.strip())
        else:
            st.session_state.setdefault("generation_prompt", current.system_prompt)
            prompt = st.text_area("System prompt", key="generation_prompt", height=240,
                                  help="Keep [n] citations and the INSUFFICIENT_EVIDENCE response in the prompt.")
            candidate = replace(candidate, system_prompt=prompt.strip() or DEFAULT_SYSTEM_PROMPT)
        a, b = st.columns(2)
        save = a.form_submit_button("Save settings", type="primary", disabled=busy)
        probe = b.form_submit_button("Test connection")
        if kind == "generation":
            st.form_submit_button("Reset prompt to default", on_click=reset_generation_prompt)
        if busy:
            st.caption("Finish or stop the index update before changing embedding settings.")
    if save:
        try:
            if kind == "embedding":
                _, _, corpus_hash = read_baseline()
                remember_library(current, corpus_hash)
            save_endpoint(candidate, kind)
        except (OSError, ValueError, RAGError) as exc:
            st.error(f"Could not save settings: {exc}")
        else:
            st.session_state["model_settings"] = load_settings()
            for key in ("ask_result", "ask_view"):
                st.session_state.pop(key, None)
            st.success(f"{kind.title()} settings saved locally.")
    if probe:
        try:
            with st.spinner(f"Testing {kind}..."):
                if kind == "embedding":
                    vector, = embed(candidate, ["How do I group pandas rows?"], query=True)
                    message = f"Embedding connection works. Returned {len(vector):,} dimensions."
                else:
                    complete(candidate, [{"role": "user", "content": "Reply with OK."}], probe=True)
                    message = "Generation connection works."
            st.success(message)
        except RAGError as exc:
            st.error(str(exc))


def reset_generation_prompt() -> None:
    st.session_state["generation_prompt"] = DEFAULT_SYSTEM_PROMPT


def settings_page() -> None:
    st.title("Model settings")
    st.write("Connect the OpenAI-compatible endpoints you want to use for embeddings and answers.")
    st.caption("Saved settings and API keys are stored in config.local.yaml and loaded automatically on restart.")
    endpoint_form("embedding")
    endpoint_form("generation")


if "model_settings" not in st.session_state:
    st.session_state["model_settings"] = load_settings()

ask = st.Page(ask_page, title="Ask", default=True)
library = st.Page(library_page, title="Library", url_path="library")
model_settings = st.Page(settings_page, title="Settings", url_path="settings")
st.navigation([ask, library, model_settings], position="top").run()
