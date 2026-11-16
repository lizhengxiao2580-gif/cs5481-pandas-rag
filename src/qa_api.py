"""Shared QA contract between the UI (A) and retrieval/generation (B).

B implements ``answer()``; the Streamlit app only depends on this interface.
Keep the shape stable: the UI renders these fields directly.
"""
from __future__ import annotations

from typing import TypedDict


class Citation(TypedDict):
    n: int            # 1-based marker used in the answer text, e.g. [1]
    doc_id: str       # e.g. "user_guide/groupby"
    title: str        # page title
    url: str          # deep link with #anchor
    section_id: str   # e.g. "user_guide/groupby#aggregation"
    score: float      # retrieval similarity, 0..1
    text: str         # chunk text shown in the citation panel


class Answer(TypedDict):
    answer: str
    refused: bool     # True when the corpus has no answer
    latency_ms: int
    citations: list[Citation]


def answer(question: str, k: int = 5) -> Answer:
    """Retrieve top-k chunks and generate a grounded, cited answer.

    B: wire this to retrieve.py + generate.py. Until then the UI shows a notice.
    """
    raise NotImplementedError("retrieval/generation not wired yet (owner: B)")
