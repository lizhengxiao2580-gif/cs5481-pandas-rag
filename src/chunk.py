"""Build both chunking strategies with the same tokenizer and token budget."""
from __future__ import annotations

from collections import defaultdict
from functools import lru_cache

STRATEGIES = {"fixed_size": "Fixed window", "structure_aware": "Structure-aware"}


@lru_cache(maxsize=4)
def get_tokenizer(name: str):
    import tiktoken

    return tiktoken.get_encoding(name)


def chunk_documents(docs: list[dict], sections: list[dict], strategy: str, settings):
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
    if not 0 <= settings.overlap < settings.chunk_size:
        raise ValueError("Chunk overlap must be smaller than the token budget.")
    tokenizer = get_tokenizer(settings.tokenizer)
    by_doc = defaultdict(list)
    for section in sections:
        by_doc[section["doc_id"]].append(section)

    for doc in docs:
        doc_id = doc["doc_id"]
        ordered = sorted(by_doc[doc_id], key=lambda row: row["order"])
        groups = [ordered] if strategy == "fixed_size" else ([row] for row in ordered)
        ordinal = 0
        for group in groups:
            pieces, spans = [], []
            offset = 0
            for section in group:
                text = section["text"].strip()
                if not text:
                    continue
                pieces.append(text)
                spans.append((offset, offset + len(text), section))
                offset += len(text) + 2
            text = "\n\n".join(pieces)
            tokens = tokenizer.encode_ordinary(text)
            if not tokens:
                continue
            _, offsets = tokenizer.decode_with_offsets(tokens)
            for start in range(0, len(tokens), settings.chunk_size - settings.overlap):
                end = min(start + settings.chunk_size, len(tokens))
                left = offsets[start]
                right = offsets[end] if end < len(tokens) else len(text)
                excerpt = text[left:right].strip()
                sources = [
                    {key: section[key] for key in ("section_id", "heading_path", "url")}
                    for begin, finish, section in spans if begin < right and finish > left
                ]
                if excerpt and sources:
                    ordinal += 1
                    yield {
                        "chunk_id": f"{strategy}:{doc_id}:{ordinal:04d}",
                        "doc_id": doc_id,
                        "title": doc["title"],
                        "text": excerpt,
                        "sources": sources,
                        "section_ids": [source["section_id"] for source in sources],
                        "section_id": sources[0]["section_id"],
                        "url": sources[0]["url"],
                    }
                if end == len(tokens):
                    break
