"""Public interfaces for the Streamlit app and evaluation scripts."""
from __future__ import annotations

import json
import re
from time import perf_counter
from typing import TypedDict

from model_api import RAGError, complete
from settings import Settings, load_settings
from vector_store import retrieve_many

CITATION = re.compile(r"(?<!!)\[([0-9]+)\](?!\()")
CODE_OR_PROSE = re.compile(r"(```[\s\S]*?(?:```|\Z)|~~~[\s\S]*?(?:~~~|\Z)|`[^`\n]*`)")
REFUSAL = "INSUFFICIENT_EVIDENCE"


class Source(TypedDict):
    section_id: str
    heading_path: str
    url: str


class Citation(TypedDict):
    n: int
    chunk_id: str
    doc_id: str
    title: str
    url: str
    section_id: str
    section_ids: list[str]
    score: float
    text: str
    sources: list[Source]


class Answer(TypedDict):
    answer: str
    refused: bool
    latency_ms: int
    citations: list[Citation]


def retrieve_chunks(question: str, k: int = 5, *, strategy: str | None = None,
                    settings: Settings | None = None) -> list[dict]:
    """Return ranked hits with stable chunk, page, and section identifiers."""
    settings = settings or load_settings()
    strategy = strategy or settings.default_strategy
    return retrieve_many(question, k, (strategy,), settings)[strategy]


def query(question: str, k: int = 5, *, strategy: str | None = None,
          settings: Settings | None = None) -> Answer:
    """Retrieve evidence and return a cited answer or an explicit refusal."""
    started = perf_counter()
    settings = settings or load_settings()
    hits = retrieve_chunks(question, k, strategy=strategy, settings=settings)
    return answer_from_hits(question, hits, settings, started=started)


def answer_from_hits(question: str, hits: list[dict], settings: Settings, *, started: float | None = None) -> Answer:
    started = perf_counter() if started is None else started
    answer, citations = generate_answer(question, hits, settings) if hits else (REFUSAL, [])
    refused = answer == REFUSAL
    return {
        "answer": "I couldn't find enough evidence in the pandas documentation to answer this."
                  if refused else answer,
        "refused": refused,
        "citations": citations,
        "latency_ms": round((perf_counter() - started) * 1000),
    }


def generate_answer(question: str, hits: list[dict], settings: Settings) -> tuple[str, list[Citation]]:
    evidence = [
        {"citation": index, "title": hit["title"],
         "sections": [source["heading_path"] for source in hit["sources"]], "text": hit["text"]}
        for index, hit in enumerate(hits, 1)
    ]
    messages = [
        {"role": "system", "content": settings.system_prompt},
        {"role": "user", "content": json.dumps({"question": question, "evidence": evidence}, ensure_ascii=False)},
    ]
    for _ in range(2):
        answer = complete(settings, messages)
        if answer.strip("`* .\t\r\n") == REFUSAL:
            return REFUSAL, []
        prose = CODE_OR_PROSE.split(answer)[::2]
        references = list(dict.fromkeys(
            int(value) for paragraph in prose for value in CITATION.findall(paragraph)
        ))
        if references and all(1 <= index <= len(hits) for index in references):
            numbers = {previous: ordinal for ordinal, previous in enumerate(references, 1)}
            parts = CODE_OR_PROSE.split(answer)
            for offset in range(0, len(parts), 2):
                parts[offset] = CITATION.sub(lambda match: f"[{numbers[int(match[1])]}]", parts[offset])
            return "".join(parts), [Citation(n=numbers[index], **hits[index - 1]) for index in references]
        messages.append({"role": "assistant", "content": answer})
        messages.append({"role": "user", "content": (
            "Return the answer with valid [n] references outside code blocks, "
            "or return only INSUFFICIENT_EVIDENCE."
        )})
    raise RAGError("The answer could not be shown because its citations were missing or invalid.")
