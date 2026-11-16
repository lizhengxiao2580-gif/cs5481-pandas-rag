# pandas 文档 RAG（CS5481 项目，Topic 5）

知识库：pandas 3.1.1 官方文档（2026-11-04 构建，BSD 许可）。
范围：`user_guide` 32 页 + `getting_started` 20 页，共 52 页；API reference 暂不纳入。

## 目录

```
data/raw/pandas-docs-3.1.1.zip     官方 HTML 包（34 MB）
data/raw/pandas-docs-3.1.1/        解压后的站点，语料在 user_guide/ 和 getting_started/
data/docs.jsonl                    页面记录，52 条
data/sections.jsonl                小节记录，382 条（B 的切块输入）
src/ingest.py                      HTML → 两份 jsonl
src/qa_api.py                      answer() 契约，B 实现
src/app.py                         Streamlit 界面
```

## 跑起来

```bash
pip install -r requirements.txt
python src/ingest.py          # 重新生成 docs.jsonl / sections.jsonl
streamlit run src/app.py      # 打开界面
```

## 数据字段

`docs.jsonl`：`doc_id, title, url, scope, path, doc_version, n_sections, n_chars, n_pre, n_tables`
`sections.jsonl`：`doc_id, section_id, order, heading, heading_path, anchor, url, n_chars, text`

`url` 是带锚点的原文链接，引用可以直接点回 pandas 文档对应小节。

## 接口契约

`src/qa_api.py::answer(question, k=5) -> Answer`

```python
{
  "answer": str, "refused": bool, "latency_ms": int,
  "citations": [{"n": 1, "doc_id": ..., "title": ..., "url": ...,
                 "section_id": ..., "score": 0.83, "text": ...}]
}
```

界面只依赖这个函数，B 换实现即可，A 不用改 UI。

## 已知取舍

- 跳过 2 个 meta refresh 跳转页（`copy_on_write.html`、`migration-3-strings.html`）。
- 保留 8 条小于 100 字符的小节，评测阶段可按 `n_chars` 过滤。
- `user_guide/io.html` 单页 26 万字符、314 个代码块，按 h2 切成 24 个小节，块内再切由 B 的 chunker 负责。
