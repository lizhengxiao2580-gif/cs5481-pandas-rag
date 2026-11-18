"""Read the tracked pandas corpus and keep local imports as paired records."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from threading import Lock

from settings import ROOT

DATA = ROOT / "data"
DOCS = DATA / "docs.jsonl"
SECTIONS = DATA / "sections.jsonl"
UPLOADS = DATA / "uploads"
UPLOAD_LOCK = Lock()


def read_baseline() -> tuple[list[dict], list[dict], str]:
    docs, sections = DOCS.read_text(encoding="utf-8"), SECTIONS.read_text(encoding="utf-8")
    fingerprint = hashlib.sha256((docs + "\0" + sections).encode()).hexdigest()
    return (
        [json.loads(line) for line in docs.split("\n") if line.strip()],
        [json.loads(line) for line in sections.split("\n") if line.strip()],
        fingerprint,
    )


def read_uploads() -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(UPLOADS.glob("*.json"))]


def save_upload(doc: dict, sections: list[dict]) -> bool:
    """Publish the page and its sections together, once per source."""
    doc_id = doc["doc_id"]
    if any(row["doc_id"] == doc_id for row in read_baseline()[0]):
        return False
    UPLOADS.mkdir(parents=True, exist_ok=True)
    target = UPLOADS / (hashlib.sha256(doc_id.encode()).hexdigest() + ".json")
    payload = {"doc": doc, "sections": sections}
    with UPLOAD_LOCK:
        if target.exists():
            return False
        fd, name = tempfile.mkstemp(dir=UPLOADS, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                json.dump(payload, output, ensure_ascii=False)
            os.replace(name, target)
            return True
        finally:
            Path(name).unlink(missing_ok=True)
