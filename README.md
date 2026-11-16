# pandas 文档 RAG（CS5481 项目，Topic 5）

知识库：pandas 3.1.1 官方文档（2026-11-04 构建，BSD 许可）。
范围：`user_guide` 32 页 + `getting_started` 20 页 + 高频 API reference 30 页，共 82 页 / 412 小节；完整 API reference（2500+ 页）暂不纳入。

## 我完成了什么

角色 A：语料收集与清洗、数据导入、演示界面、接口契约。

| 交付物 | 状态 | 说明 |
|--------|------|------|
| `data/raw/pandas-docs-3.1.1/` | 完成 | 官方 HTML 包解压站点，34 MB，来源 https://pandas.pydata.org/docs/pandas.zip |
| `data/docs.jsonl` | 完成 | 82 条页面记录，含标题、带锚点的原文链接、字符数、代码块数、版本号 |
| `data/sections.jsonl` | 完成 | 412 条小节记录，按 h2 切分，每条带 heading_path 和可点击的原文 url |
| `src/ingest.py` | 完成 | HTML → jsonl 解析器，支持 `--from-file` 批量指定页面和 `--append` 增量追加 |
| `src/app.py` | 完成 | Streamlit 演示界面：文档库页签（筛选、度量、下载、HTML 导入）和问答页签（k 滑杆、引用展开） |
| `src/qa_api.py` | 完成 | `answer()` 的接口契约，与界面解耦 |
| `tests/smoke_ui.py` | 完成 | 无头冒烟测试，验证 82 行表格、度量值和问答页占位提示 |
| `config.yaml` | 完成 | 语料、切块、embedding、检索、生成、评测的参数模板 |
| `README.md` | 完成 | 数据字段、运行方式、接口契约、取舍记录 |

## 目录

```
data/raw/pandas-docs-3.1.1.zip     官方 HTML 包（34 MB）
data/raw/pandas-docs-3.1.1/        解压后的站点，语料在 user_guide/、getting_started/、reference/api/
data/docs.jsonl                    页面记录，82 条
data/sections.jsonl                小节记录，412 条
src/ingest.py                      HTML → 两份 jsonl
src/qa_api.py                      answer() 契约
src/app.py                         Streamlit 界面（含文档导入按钮）
tests/smoke_ui.py                  无头冒烟测试
config.yaml                        切块/检索/模型参数
```

## 跑起来

```bash
pip install -r requirements.txt
python src/ingest.py          # 重新生成 docs.jsonl / sections.jsonl（user_guide + getting_started）
python src/ingest.py --from-file data/raw/api_targets_prefixed.txt --append   # 追加高频 API 页
streamlit run src/app.py      # 打开界面（http://localhost:8501）
```

首次运行需下载原始语料：

```bash
# 从 https://pandas.pydata.org/docs/pandas.zip 下载并解压到 data/raw/
```

## 数据字段

`docs.jsonl`：`doc_id, title, url, scope, path, doc_version, n_sections, n_chars, n_pre, n_tables`

`sections.jsonl`：`doc_id, section_id, order, heading, heading_path, anchor, url, n_chars, text`

`url` 是带锚点的原文链接，引用可以直接点回 pandas 文档对应小节。

## 语料清洗做了什么

- 只取 `article.bd-article` 主体，丢掉导航、侧栏、页脚。
- 删掉每个标题里的 `a.headerlink`，否则每段都以 `#` 开头，会污染 embedding。
- 按叶子块（p、pre、ul、table 等）提取文本，不是整篇 `get_text()`。第一版用整篇提取，代码块被拆成 `grouped / = / df / .` 这样的单 token；换成块级提取后代码块完整。
- `pre` 保留换行，其余块折叠空白。
- 跳过 2 个 meta refresh 跳转存根页：`copy_on_write.html`、`migration-3-strings.html`（内容在真实页面里，不算缺失）。
- 切分粒度到 h2，`user_guide/io.html` 这种 26 万字符、314 个代码块的大页被切成 24 个小节，不会变成单个巨型块。

## 语料统计

| 指标 | 数值 |
|------|------|
| 页面 | 82 |
| 小节 | 412 |
| 字符 | 1,662,660 |
| 代码块 | 2,814 |
| 重复 section_id | 0 |
| 空小节 | 0 |
| 最长小节 | `user_guide/io#csv-text-files`，64,209 字符 |

## 接口契约

`src/qa_api.py::answer(question, k=5) -> Answer`

```python
{
  "answer": str,           # 带 [n] 引用的回答，或拒绝语句
  "refused": bool,         # True 表示无法从知识库找到答案
  "latency_ms": int,
  "citations": [
    {
      "n": 1,              # 引用编号，对应 answer 中的 [1]
      "doc_id": "...",
      "title": "...",
      "url": "...",        # 带锚点的原文链接
      "section_id": "...",
      "score": 0.83,       # 相似度分数
      "text": "..."        # 原文片段（≤1200 字符）
    }
  ]
}
```

界面只依赖这个函数，`answer()` 换实现不用改 UI。

## 已知取舍

- 跳过 2 个 meta refresh 跳转页（`copy_on_write.html`、`migration-3-strings.html`）。
- 保留 7 条小于 100 字符的小节，评测阶段可按 `n_chars` 过滤。
- API reference 仅纳入 30 个高频方法页（read_csv、merge、groupby、pivot_table、loc、iloc、dropna、fillna 等），完整 2500+ 页会稀释检索质量；如需扩展，编辑 `data/raw/api_targets_prefixed.txt` 后重跑 `--append`。
- 本机 pandas 3.0.6，文档版本 3.1.1，数据里已标 `doc_version`。
