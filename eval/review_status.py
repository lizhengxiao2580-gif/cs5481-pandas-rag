"""Read the project member review confirmation for this exact experiment."""
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent

def human_review_complete():
    path = BASE / "human_review.json"
    if not path.exists():
        return False
    record = json.loads(path.read_text(encoding="utf-8"))
    if record.get("status") != "completed":
        return False
    for name, expected in record.get("artifact_sha256", {}).items():
        item = BASE / name
        if not item.is_file() or hashlib.sha256(item.read_bytes()).hexdigest() != expected:
            return False
    return bool(record.get("artifact_sha256"))

def human_review_statement():
    if human_review_complete():
        return ("Initial scores were produced with model assistance and checked against source evidence "
                "and reproducible examples. A project member subsequently completed human review "
                "and confirmed the existing scores. This is model-assisted evaluation with human "
                "review, rather than independent blind human ratings.")
    return ("Initial scores are model-assisted and evidence-based corrections are recorded separately. "
            "Human review has not been confirmed for the current experiment artifacts.")
