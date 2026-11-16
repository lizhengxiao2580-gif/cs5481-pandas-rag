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
src/app.py                         Streamlit 界面（含文档导入按钮）
tests/smoke_ui.py                  无头冒烟测试
config.yaml                        （待创建）切块/检索/模型参数
eval/questions.jsonl               （待创建）≥20 条评测问题
```

## 跑起来

```bash
pip install -r requirements.txt
python src/ingest.py          # 重新生成 docs.jsonl / sections.jsonl
streamlit run src/app.py      # 打开界面（http://localhost:8501）
```

首次运行需下载原始语料：
```bash
# 从 https://pandas.pydata.org/docs/pandas.zip 下载并解压到 data/raw/
```

### GCP Vertex AI（B 用）

B 的 embedding/generation 依赖 Vertex AI，需设置：
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GOOGLE_CLOUD_PROJECT=cs5481-<eid>-a
export GOOGLE_CLOUD_REGION=asia-east2
```

本地调试可用 fake embedding 跳过认证，见 `config.yaml`。

## 数据字段

`docs.jsonl`：`doc_id, title, url, scope, path, doc_version, n_sections, n_chars, n_pre, n_tables`
`sections.jsonl`：`doc_id, section_id, order, heading, heading_path, anchor, url, n_chars, text`

`url` 是带锚点的原文链接，引用可以直接点回 pandas 文档对应小节。

## 两种切块策略（T5 核心要求）

| 策略 | 描述 | 适用场景 |
|------|------|----------|
| **A: Fixed-size** | 固定 500 token，overlap 100 | 基线，简单可复现 |
| **B: Structure-aware** | 按 h2/h3 标题切分，保留 heading_path | 保留语义边界，适合技术文档 |

B 需在 `src/chunk.py`（待创建）中实现两种策略，输出统一格式：
```json
{"chunk_id": "...", "strategy": "A|B", "text": "...", "heading_path": "...", "doc_id": "..."}
```

评测时必须对比 A/B 在相同 k 下的 Hit@k / MRR / 答案正确率。

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

**引用验证规则（T5 要求）：**
- 每个事实性声明必须有 `[n]` 引用
- `[n]` 必须能在 citations 中找到对应条目
- 无法支撑的声明必须删除或改为拒绝
- 拒绝时使用固定语句：`无法从知识库中找到答案`

界面只依赖这个函数，B 换实现即可，A 不用改 UI。

## 评估方法（T5 要求）

`eval/questions.jsonl`（C 负责编写，≥20 条）：
```json
{"id": "q01", "question": "...", "category": "direct|cross_chunk|terminology|no_answer", "keypoints": ["..."]}
```

评测指标：
| 指标 | 计算方式 | 目标 |
|------|----------|------|
| Hit@k | 至少一个相关 chunk 在 top-k 中 | ≥0.8 |
| MRR | 首个相关 chunk 排名的倒数 | ≥0.6 |
| Keypoint correctness | 人工判断答案是否覆盖关键点 | ≥0.7 |
| Refusal correctness | no_answer 类问题是否正确拒绝 | ≥0.9 |
| Citation precision | 引用编号是否真实支撑声明 | ≥0.8 |

运行评测：
```bash
python src/evaluate.py --questions eval/questions.jsonl --output eval/report.md
```

## 分工

| 角色 | 职责 | 交付物 |
|------|------|--------|
| **A** | 语料收集/清洗、导入功能、演示界面 | docs.jsonl, sections.jsonl, app.py, ingest.py |
| **B** | 两种切块、embedding、检索、生成、引用 | chunk.py, embed.py, retrieve.py, generate.py, qa_api.py 实现 |
| **C** | 评测问题、检索验证、正式评测、错误分析 | questions.jsonl, evaluate.py, report.md |

最终报告末页需附贡献比例表 + 全员签名。

## 已知取舍

- 跳过 2 个 meta refresh 跳转页（`copy_on_write.html`、`migration-3-strings.html`）。
- 保留 8 条小于 100 字符的小节，评测阶段可按 `n_chars` 过滤。
- `user_guide/io.html` 单页 26 万字符、314 个代码块，按 h2 切成 24 个小节，块内再切由 B 的 chunker 负责。
- API reference 未纳入（3812 页多为签名 stub），如需加入请限定 ≤50 个高频方法页。
