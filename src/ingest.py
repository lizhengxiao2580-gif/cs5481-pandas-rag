#!/usr/bin/env python3
"""Ingest the pandas HTML documentation bundle into JSONL.

Outputs (default under rag-qa/data/):
  docs.jsonl      one record per page
  sections.jsonl  one record per h2 section, plus a page-level overview when present

Usage:
  python src/ingest.py                 # full corpus
  python src/ingest.py --limit 3       # smoke test on the first 3 pages
  python src/ingest.py --only user_guide/groupby.html
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "pandas-docs-3.1.1"
OUT_DIR = ROOT / "data"
DOC_VERSION = "3.1.1"
BASE_URL = "https://pandas.pydata.org/docs/"
SCOPES = ("user_guide", "getting_started")
MIN_PREAMBLE_CHARS = 40

# Block-level tags used to split text into readable units. Inline tags (span, code,
# em, a, ...) are ignored so syntax-highlighted code does not get shredded.
BLOCK_TAGS = (
    "p", "div", "pre", "ul", "ol", "li", "dl", "dt", "dd", "table",
    "thead", "tbody", "tr", "blockquote", "figure", "figcaption",
    "section", "h1", "h2", "h3", "h4", "h5", "h6", "aside", "details", "summary",
)


def clean(text: str) -> str:
    text = text.replace("\u200b", "").replace("\xa0", " ")
    return text.strip("\r\n")


def strip_heading(text: str) -> str:
    return re.sub(r"#+\s*$", "", text).strip()


def render_block(el) -> str:
    if el.name == "pre":
        lines = [line.rstrip() for line in el.get_text().splitlines()]
        return "\n".join(lines).strip("\n")
    return re.sub(r"\s+", " ", el.get_text("")).strip()


def block_texts(root) -> list[str]:
    blocks = [el for el in root.find_all(BLOCK_TAGS) if el.find(BLOCK_TAGS) is None]
    if not blocks:
        blocks = [root]
    return [text for text in (render_block(el) for el in blocks) if text]


def page_files(only: str | None, from_file: str | None = None) -> list[Path]:
    if from_file:
        lines = Path(from_file).read_text(encoding="utf-8").splitlines()
        return [RAW_DIR / line.strip() for line in lines if line.strip()]
    if only:
        return [RAW_DIR / only]
    files: list[Path] = []
    for scope in SCOPES:
        files.extend(sorted((RAW_DIR / scope).rglob("*.html")))
    return files


def build_page(path: Path) -> tuple[dict, list[dict]] | None:
    soup = BeautifulSoup(path.read_text(encoding="utf-8-sig"), "lxml")
    return parse_page(soup, path.relative_to(RAW_DIR).as_posix())


def parse_official_upload(html: bytes, source_url: str = "") -> tuple[dict, list[dict]]:
    soup = BeautifulSoup(html, "lxml")
    canonical = soup.find("link", rel="canonical")
    og_url = soup.find("meta", property="og:url")
    embedded_url = (canonical.get("href") if canonical else None) or (og_url.get("content") if og_url else None)
    embedded_path = official_path(embedded_url or "")
    supplied_path = official_path(source_url)
    if source_url and not supplied_path:
        raise ValueError("Enter the official pandas documentation page URL.")
    if embedded_path and supplied_path and embedded_path != supplied_path:
        raise ValueError("The entered URL differs from the official source in this HTML file.")
    rel = embedded_path or supplied_path
    if not rel:
        raise ValueError("This file does not identify its official source. Enter the pandas page URL.")
    parsed = parse_page(soup, rel)
    if parsed is None or not any(section["text"] for section in parsed[1]):
        raise ValueError("No pandas documentation content was found in this file.")
    return parsed


def official_path(url: str) -> str | None:
    try:
        address = urlsplit(url.strip())
    except ValueError:
        return None
    if address.scheme != "https" or address.netloc.lower() != "pandas.pydata.org":
        return None
    matched = re.fullmatch(r"/docs/((?:[\w.-]+/)*[\w.-]+\.html)", address.path)
    if matched and not {".", ".."}.intersection(matched[1].split("/")):
        return matched[1]
    return None


def parse_page(soup: BeautifulSoup, rel: str) -> tuple[dict, list[dict]] | None:
    article = soup.select_one("article.bd-article")
    if article is None:
        return None

    # pandas adds a '#' permalink inside every heading; drop it before extracting text.
    for anchor in article.select("a.headerlink"):
        anchor.decompose()

    h1 = article.find("h1")
    title = strip_heading(h1.get_text(" ", strip=True)) if h1 else Path(rel).stem

    doc_id = rel[: -len(".html")]
    page_url = BASE_URL + rel
    n_pre = len(article.find_all("pre"))
    n_tables = len(article.find_all("table"))

    wrapper = article.find("section")
    h2_sections: list = []
    for h2 in article.find_all("h2"):
        section = h2.find_parent("section")
        if section is not None and section not in h2_sections:
            h2_sections.append(section)

    sections: list[dict] = []
    order = 0

    if h2_sections:
        for section in h2_sections:
            section.extract()
        preamble_parts = block_texts(wrapper) if wrapper else []
        if preamble_parts and preamble_parts[0] == title:
            preamble_parts = preamble_parts[1:]
        preamble = clean("\n".join(preamble_parts))
        if len(preamble) >= MIN_PREAMBLE_CHARS:
            anchor = wrapper.get("id") if wrapper else None
            sections.append(
                {
                    "doc_id": doc_id,
                    "section_id": f"{doc_id}#{anchor}" if anchor else f"{doc_id}#s{order:02d}",
                    "order": order,
                    "heading": "Overview",
                    "heading_path": f"{title} > Overview",
                    "anchor": anchor,
                    "url": f"{page_url}#{anchor}" if anchor else page_url,
                    "n_chars": len(preamble),
                    "text": preamble,
                }
            )
            order += 1

        for section in h2_sections:
            h2 = section.find("h2")
            if h2 is None:
                continue
            heading = strip_heading(h2.get_text(" ", strip=True))
            parts = block_texts(section)
            if parts and parts[0] == heading:
                parts = parts[1:]
            body = clean("\n".join(parts))
            if not body:
                continue
            anchor = section.get("id")
            sections.append(
                {
                    "doc_id": doc_id,
                    "section_id": f"{doc_id}#{anchor}" if anchor else f"{doc_id}#s{order:02d}",
                    "order": order,
                    "heading": heading,
                    "heading_path": f"{title} > {heading}",
                    "anchor": anchor,
                    "url": f"{page_url}#{anchor}" if anchor else page_url,
                    "n_chars": len(body),
                    "text": body,
                }
            )
            order += 1

    if not sections:
        body = clean("\n".join(block_texts(article)))
        sections.append(
            {
                "doc_id": doc_id,
                "section_id": f"{doc_id}#page",
                "order": 0,
                "heading": title,
                "heading_path": title,
                "anchor": None,
                "url": page_url,
                "n_chars": len(body),
                "text": body,
            }
        )

    doc = {
        "doc_id": doc_id,
        "title": title,
        "url": page_url,
        "scope": doc_id.split("/")[0],
        "path": rel,
        "doc_version": DOC_VERSION,
        "n_sections": len(sections),
        "n_chars": sum(s["n_chars"] for s in sections),
        "n_pre": n_pre,
        "n_tables": n_tables,
    }
    return doc, sections


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="process only the first N pages")
    parser.add_argument("--only", default=None, help="process a single page, path relative to the docs root")
    parser.add_argument("--from-file", default=None, help="read page paths from a text file (one per line, relative to docs root)")
    parser.add_argument("--append", action="store_true", help="append to existing jsonl instead of overwriting")
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    args = parser.parse_args()

    if not RAW_DIR.is_dir():
        print(f"docs not found: {RAW_DIR}", file=sys.stderr)
        return 1

    files = page_files(args.only, args.from_file)
    if args.limit:
        files = files[: args.limit]

    docs: list[dict] = []
    sections: list[dict] = []
    skipped: list[str] = []
    for path in files:
        result = build_page(path)
        if result is None:
            skipped.append(path.name)
            continue
        doc, secs = result
        docs.append(doc)
        sections.extend(secs)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    docs_path = out_dir / "docs.jsonl"
    sections_path = out_dir / "sections.jsonl"

    if args.append:
        # Load existing and deduplicate by doc_id / section_id
        existing_docs = []
        existing_sections = []
        if docs_path.exists():
            existing_docs = [json.loads(l) for l in docs_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        if sections_path.exists():
            existing_sections = [json.loads(l) for l in sections_path.read_text(encoding="utf-8").splitlines() if l.strip()]
        existing_doc_ids = {d["doc_id"] for d in existing_docs}
        existing_section_ids = {s["section_id"] for s in existing_sections}
        new_docs = [d for d in docs if d["doc_id"] not in existing_doc_ids]
        new_sections = [s for s in sections if s["section_id"] not in existing_section_ids]
        all_docs = existing_docs + new_docs
        all_sections = existing_sections + new_sections
        write_jsonl(docs_path, all_docs)
        write_jsonl(sections_path, all_sections)
        print(f"appended {len(new_docs)} docs / {len(new_sections)} sections (total {len(all_docs)} / {len(all_sections)})")
    else:
        write_jsonl(docs_path, docs)
        write_jsonl(sections_path, sections)

    total_chars = sum(d["n_chars"] for d in docs)
    ids = [s["section_id"] for s in sections]
    print(f"pages: {len(docs)}  skipped: {len(skipped)}  sections: {len(sections)}  chars: {total_chars}")
    print(f"duplicate section ids: {len(ids) - len(set(ids))}")
    small = sorted(docs, key=lambda d: d["n_chars"])[:5]
    print("smallest pages:", [(d["doc_id"], d["n_chars"]) for d in small])
    if skipped:
        print("skipped:", skipped)
    print(f"wrote {out_dir / 'docs.jsonl'} and {out_dir / 'sections.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
