"""Lightweight startup check. Run python tests/smoke_ui.py from the repository."""
from pathlib import Path
import sys

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
app = AppTest.from_file(str(ROOT / "src" / "app.py")).run()
assert not app.exception, app.exception
assert app.title[0].value == "Ask the pandas docs"
assert any(button.label == "Ask pandas" for button in app.button)
print("SMOKE OK")
