"""Streamlit UI: document library + QA over the pandas docs corpus.

Run from rag-qa/:
    streamlit run src/app.py
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import streamlit as st

from qa_api import answer
from ingest import build_page, write_jsonl

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "data" / "docs.jsonl"
SECTIONS = ROOT / "data" / "sections.jsonl"

st.set_page_config(page_title="pandas docs RAG", layout="wide")


@st.cache_data
def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def append_to_jsonl(path: Path, rows: list[dict]) -> None:
    """Append rows to a JSONL file, creating it if missing."""
    existing = load_jsonl(path)
    all_rows = existing + rows
    write_jsonl(path, all_rows)
    st.cache_data.clear()


def import_html(uploaded_file) -> tuple[int, int]:
    """Parse an uploaded HTML file and append to docs/sections. Returns (n_docs, n_sections)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = Path(tmp.name)
    try:
        result = build_page(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)
    if result is None:
        return 0, 0
    doc, secs = result
    append_to_jsonl(DOCS, [doc])
    append_to_jsonl(SECTIONS, secs)
    return 1, len(secs)


docs = load_jsonl(DOCS)
sections = load_jsonl(SECTIONS)
version = docs[0]["doc_version"] if docs else "未导入"

st.title("pandas 文档问答")
st.caption(f"文档版本 {version} · {len(docs)} 页 · {len(sections)} 小节")

tab_docs, tab_qa = st.tabs(["文档库", "问答"])

with tab_docs:
    c1, c2, c3 = st.columns(3)
    c1.metric("页面", len(docs))
    c2.metric("小节", len(sections))
    c3.metric("字符", f"{sum(d['n_chars'] for d in docs):,}")

    if not docs:
        st.warning("没有数据，先运行 `python src/ingest.py`。")
    else:
        scope = st.selectbox("范围", ["全部", "user_guide", "getting_started"])
        rows = [d for d in docs if scope == "全部" or d["scope"] == scope]
        st.dataframe(
            rows,
            column_order=["title", "doc_id", "scope", "n_sections", "n_chars", "url"],
            column_config={"url": st.column_config.LinkColumn("链接", display_text="打开")},
            hide_index=True,
            width="stretch",
        )
        st.download_button("下载 docs.jsonl", DOCS.read_bytes(), "docs.jsonl", "application/jsonl")

    uploaded = st.file_uploader(
        "导入新文档（HTML）",
        type=["html"],
        accept_multiple_files=False,
        help="选择本地 HTML 文件，解析后追加到语料库。",
    )
    if uploaded is not None:
        with st.spinner(f"正在解析 {uploaded.name} ..."):
            n_docs, n_secs = import_html(uploaded)
        if n_docs == 0:
            st.error("解析失败：未找到 article.bd-article 或内容为空。")
        else:
            st.success(f"已导入 {n_docs} 页 / {n_secs} 小节，刷新页面查看更新。")
            st.rerun()

with tab_qa:
    question = st.text_input("问题", placeholder="例如：How do I group by two columns?")
    k = st.slider("检索条数 k", 3, 10, 5)
    if st.button("提问", type="primary") and question.strip():
        try:
            result = answer(question.strip(), k=k)
        except NotImplementedError:
            st.info("检索与生成模块还没接入（B 负责）。接口见 `src/qa_api.py`。")
        except Exception as exc:  # surface backend errors instead of a blank page
            st.error(f"出错了：{exc}")
        else:
            if result["refused"]:
                st.warning(result["answer"])
            else:
                st.markdown(result["answer"])
            st.caption(f"{result['latency_ms']} ms")
            for cite in result["citations"]:
                label = f"[{cite['n']}] {cite['title']} · {cite['section_id']} · {cite['score']:.3f}"
                with st.expander(label):
                    st.markdown(f"[原文]({cite['url']})")
                    st.text(cite["text"][:1200])
