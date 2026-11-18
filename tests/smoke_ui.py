"""Check the prebuilt frontend and its HTTP contract without calling any models."""
from pathlib import Path
import re
import sys
from unittest.mock import patch

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from web_api import app

client = TestClient(app)
assert client.get("/api/health").json() == {"ok": True}
for route in ("/", "/library", "/settings"):
    page = client.get(route)
    assert page.status_code == 200 and "pandas Docs QA" in page.text
asset = re.search(r'src="(/assets/[^"]+\.js)"', page.text).group(1)
assert client.get(asset).status_code == 200
workspace = client.get("/api/workspace").json()
assert len(workspace["documents"]) >= 82
connection = client.get("/api/settings").json()
assert all("api_key" not in connection[kind] for kind in ("embedding", "generation"))

passages = {"fixed_size": [{"text": "fixed excerpt"}], "structure_aware": [{"text": "structured excerpt"}]}
reply = {"answer": "A cited answer [1].", "refused": False, "latency_ms": 0, "citations": []}
with patch("web_api.retrieve_many", return_value=passages) as retrieve, patch("web_api.answer_from_hits", return_value=reply) as answer:
    response = client.post("/api/retrieve", json={"question": "How do I group rows?"})
    assert response.status_code == 200 and response.json()["results"] == passages
    response = client.post("/api/answer", json={"retrieval_id": response.json()["id"], "strategy": "fixed_size"})
    assert response.status_code == 200 and response.json() == reply
    assert retrieve.call_count == 1 and answer.call_args.args[1] == passages["fixed_size"]

print("SMOKE OK")
