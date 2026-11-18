# pandas Docs QA

CS5481 Topic 5. Ask questions about pandas and check each answer against the cited documentation. The included corpus contains **82 pages and 412 sections** from pandas 3.1.1, including 30 API reference pages.

## Run the app

```bash
python -m pip install -r requirements.txt
python src/app.py
```

Open [http://127.0.0.1:8501](http://127.0.0.1:8501). FastAPI serves the built React app from `web/dist/`, so running the project only requires Python.

1. Open **Settings**. Set an OpenAI-compatible base URL and model ID under both **Embedding Model** and **Generation Model**. Click **Test Connection**, then **Save Settings** for each model. Embedding uses `/embeddings` and Generation uses `/chat/completions`.
2. Under **Library → Manage Libraries**, load the preset or create a library for your embedding model. **Update Index** adds missing pages to the active library. Pause or stop at the next batch or collection boundary. Resume from the controls or rerun an interrupted update to reuse saved vectors.
3. Open **Ask & Compare** and run a sample question. Choose a retrieval strategy next to **Ask** and follow inline citations to the source passage. Switch to **Compare** to browse both rankings without another model request. Starting in Compare mode runs retrieval without generating an answer.

### Edit the frontend

Keep `python src/app.py` running. In a second terminal, run the following from `web/` with a Node.js version supported by Vite (Node 22.12 or newer in the 22.x line):

```bash
npm ci
npm run dev
```

Vite opens a development address and proxies `/api` to the Python service on port 8501. After modifying the frontend, run `npm run build` in `web/` and include the updated `web/dist/` files in the submission. The bundled app and API can be checked with `python tests/smoke_ui.py`.

The UI saves settings and entered API keys to the Git-ignored `config.local.yaml`. The application and CLI load that file automatically after a restart. **Generation Model → Advanced Connection Parameters** contains the system prompt and the option to restore its default. You can also edit the file directly:

```yaml
embedding:
  base_url: "https://api.siliconflow.cn/v1"
  model: "Qwen/Qwen3-Embedding-8B"
  dimensions: 1024
  api_key_env: EMBEDDING_API_KEY
  query_instruction: "Given a pandas question, retrieve documentation passages that answer it."
generation:
  base_url: "https://openrouter.ai/api/v1"
  model: "replace-with-a-model-id-your-provider-supports"
  api_key_env: GENERATION_API_KEY
```

Leaving the API key field blank keeps an existing saved key. To switch to the named environment variable, click **Clear saved key from disk**, then **Save Settings**. A key entered in the app is saved as plain text in the local file. Omit `dimensions` or set it to `null` to use the provider's default. If a server rejects batches, lower `batch_size` (use `1` for single-text requests).

## Data and indexes

- [`data/docs.jsonl`](data/docs.jsonl) contains page IDs, titles, official URLs, scope and counts.
- [`data/sections.jsonl`](data/sections.jsonl) contains ordered sections with stable IDs, heading paths, text and deep links.
- **Fixed window** joins sections in order within each page, then takes 500-token windows with 100-token overlap. **Structure-aware** starts at each section boundary and uses the same windows inside long sections. Both use `cl100k_base` for reproducible token counts. The tokenizer downloads its data on first use.
- Each vector library contains two Qdrant collections with chunk text, section IDs, and source URLs. Retrieval uses cosine similarity. Named libraries remember their embedding settings and can be switched independently of the answer strategy. Updating a library adds missing pages using its original chunking parameters. Editing the query instruction does not rebuild document vectors.
- **Library → Import HTML** accepts an official pandas HTML page. Preview it and confirm the import. Supply the official URL if it is absent from the HTML. The page and its sections are stored together in ignored `data/uploads/` and become searchable once **Update Index** succeeds for both strategies.
- The tracked corpus is enough to build the indexes. To regenerate the source corpus itself, download the [pandas HTML package](https://pandas.pydata.org/docs/pandas.zip) into `data/raw/` and use `src/ingest.py`. Run it with `--out-dir` when generating a separate copy. The standard ingestion run covers the user guide and getting started pages; `--from-file` with `--append` adds explicitly listed API pages.

### CLI and submission bundle

```bash
python src/index_cli.py build
python src/index_cli.py bundle
python src/index_cli.py install
```

`build` updates both indexes for the active embedding settings and includes any local imports. `bundle` exports existing vectors for the tracked corpus without calling the embedding API. The archive contains both Qdrant collections and an index manifest. Local imports and API keys are excluded.

The bundled `data/prebuilt-index.zip` contains both indexes for the public pandas corpus at 1,024 dimensions. Configure an embedding endpoint, then choose **Load preset** or **Verify & Load** under **Library → Manage Libraries**. The CLI equivalent is `python src/index_cli.py install`. The original embedding binding loads locally. When an endpoint, model alias, or default output dimension needs verification, the app compares three public passages against the stored vectors. A compatible endpoint can reuse the preset. If compatibility fails, create a separate library from the current embedding settings and build it explicitly. Each teammate supplies their own API credentials and can select their own generation model. Live questions still call the embedding and generation APIs. Use `--archive PATH` to write or read an archive at a different path.

## Evaluation interface

From the repository root, run evaluation with `src/` on the Python module path. For example, an evaluator under `src/` can import directly:

```python
from qa_api import query, retrieve_chunks

hits = retrieve_chunks("How do I group by two columns?", k=5, strategy="fixed_size")
result = query("How do I group by two columns?", k=5, strategy="structure_aware")
```

Both paths use `config.yaml` with optional `config.local.yaml` overrides. Valid strategy IDs are `fixed_size` and `structure_aware`. Each hit includes `chunk_id`, `doc_id`, `section_ids`, `score`, the text, and source links. A fixed window can touch more than one section. Label evaluation questions by page or section ID and count a hit if any of its IDs matches.

`query()` returns `answer`, `refused`, `latency_ms` and numbered `citations`. It validates that every emitted citation marker points to a retrieved chunk. Check whether each citation supports its claim when scoring answer correctness. For the strategy comparison, use the same questions, model, and `k` for both runs. The assignment asks for at least 20 question–answer pairs and reporting retrieval hit rate and answer correctness.
