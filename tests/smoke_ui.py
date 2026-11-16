"""Headless smoke test for the Streamlit UI (no browser needed).

Usage (from rag-qa/):  python tests/smoke_ui.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from streamlit.testing.v1 import AppTest  # noqa: E402

at = AppTest.from_file(str(ROOT / "src" / "app.py"), default_timeout=120).run()

print("page title :", at.title[0].value if at.title else "(none)")
print("metrics    :", [(m.label, m.value) for m in at.metric])
print("exceptions :", list(at.exception))
assert not at.exception, at.exception

rows = at.dataframe[0].value
print("table rows :", len(rows))
print("columns    :", list(rows.columns))
assert len(rows) == 82, f"expected 82 pages, got {len(rows)}"

# QA tab: submitting a question should hit the not-implemented notice from B's stub.
at.text_input[0].input("How do I group by two columns?")
at.button[0].click()
at.run()
print("info       :", [i.value for i in at.info])
print("errors     :", [e.value for e in at.error])
assert at.info and "还没接入" in at.info[0].value

print("SMOKE OK")
