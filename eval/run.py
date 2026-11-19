"""Run paired RAG evaluation, resume completed pairs, and preserve original evidence.

Usage: python eval/run.py [--workers 2]
No production code or user settings are modified. No keys are written to outputs.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from corpus import read_baseline
from model_api import RAGError
from qa_api import query
from settings import load_settings
from vector_store import active_index_state

STRATEGIES = ("fixed_size", "structure_aware")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    settings = load_settings()
    docs, sections, corpus_hash = read_baseline()
    state = active_index_state(settings)
    if len(state.get("documents", [])) != len(docs):
        raise SystemExit("Use the public-only preset library, with no uploaded pages, for this benchmark.")
    settings = replace(settings, temperature=0)
    questions_path = ROOT / "eval/questions.jsonl"
    questions = [json.loads(line) for line in questions_path.read_text().splitlines()]
    out = ROOT / "eval/results"
    out.mkdir(exist_ok=True)
    metadata = {
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "questions_sha256": hashlib.sha256(questions_path.read_bytes()).hexdigest(),
        "corpus_sha256": corpus_hash, "documents": len(docs), "sections": len(sections),
        "chunk_counts": state["chunks"], "chunking": {k: state["profile"][k] for k in ("tokenizer", "chunk_size", "overlap")},
        "embedding_model": settings.embedding.model, "embedding_dimensions": settings.dimensions,
        "query_instruction": settings.query_instruction, "generation_model": settings.generation.model,
        "generation_temperature": settings.temperature, "generation_max_tokens": settings.max_tokens,
        "system_prompt": settings.system_prompt, "k": 5, "workers": args.workers,
        "latency_definition": "perf_counter around qa_api.query, including question embedding, local retrieval, answer generation and any SDK/citation retries; excludes grading; up to two concurrent questions",
        "order": "Even-numbered questions fixed_size first, odd-numbered questions structure_aware first",
        "python_version": sys.version.split()[0],
    }
    metadata_path = out / "metadata.json"
    if metadata_path.exists():
        previous = json.loads(metadata_path.read_text())
        if previous["configuration"] != metadata:
            raise SystemExit("Run configuration changed; preserve the old results and start a new output directory.")
    else:
        metadata_path.write_text(json.dumps({"started_utc": datetime.now(timezone.utc).isoformat(), "configuration": metadata}, indent=2)+"\n")

    def run_question(q):
        n = int(q["id"][1:])
        order = STRATEGIES if n % 2 == 0 else STRATEGIES[::-1]
        for strategy in order:
            path = out / f"{q['id']}_{strategy}.json"
            if path.exists():
                continue
            start = perf_counter()
            row = {"question_id": q["id"], "strategy": strategy, "started_utc": datetime.now(timezone.utc).isoformat()}
            try:
                # query() is the existing application interface; keep all ranked hits
                # by capturing retrieve_chunks without changing retrieval behavior.
                import qa_api
                # Retrieval is instrumented once globally below, with thread-local state.
                capture.hits = []
                answer = query(q["question"], k=5, strategy=strategy, settings=settings)
                row.update(answer)
                row["hits"] = capture.hits
                row["status"] = "ok"
            except Exception as exc:
                # API wrapper messages are sanitized. Never serialize arbitrary exception bodies.
                row.update(status="error", error=str(exc) if isinstance(exc, RAGError) else type(exc).__name__,
                           hits=getattr(capture, "hits", []), answer="", refused=False, citations=[])
            row["wall_latency_ms"] = round((perf_counter()-start)*1000)
            tmp = path.with_suffix(".tmp")
            tmp.write_text(json.dumps(row, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            tmp.replace(path)
            print(q["id"], strategy, row["status"], f"{row['wall_latency_ms']/1000:.2f}s", "refused" if row["refused"] else "answered", flush=True)

    # Capture the actual top-5 used by query (one embedding call per strategy),
    # including its original order; avoid an extra retrieval request for scoring.
    import threading
    import qa_api
    capture = threading.local()
    original = qa_api.retrieve_chunks

    def recorded(*a, **kw):
        hits = original(*a, **kw)
        capture.hits = hits
        return hits

    qa_api.retrieve_chunks = recorded
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for future in as_completed([pool.submit(run_question, q) for q in questions]):
                future.result()
    finally:
        qa_api.retrieve_chunks = original
    rows = [json.loads(p.read_text()) for p in sorted(out.glob("Q*.json"))]
    (out / "raw_results.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False)+"\n" for r in rows))
    print("COMPLETE", len(rows), "results; errors", sum(r["status"] != "ok" for r in rows), flush=True)


if __name__ == "__main__":
    main()
