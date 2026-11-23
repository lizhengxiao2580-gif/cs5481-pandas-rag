# C: Evaluation

This directory adds the evaluation work only. It uses the existing backend and the public preset indexes. Application model settings stay in the ignored `config.local.yaml`; no keys belong in this directory.

## Reproduce

From the repository root, after installing `requirements.txt` and configuring both endpoints:

```bash
python src/index_cli.py install
python eval/prepare.py
python eval/run.py --workers 2
python eval/grade.py
python eval/summarize.py
```

`run.py` makes real API calls. The 30 questions produce 60 system runs. `grade.py` makes about 30 additional grading requests (plus repairs if needed). `summarize.py` is entirely local. Completed results and judgments are reused on restart. To deliberately run a fresh experiment, preserve the existing results directory under another name before starting. Do not mix results from changed models, corpus, questions or prompts.

The included `review_overrides.json` contains evidence-based corrections for the saved run, so `summarize.py` reproduces the reviewed results. For a genuinely new run, preserve that file with the old results and perform a fresh review. Overrides should not be applied to new model outputs automatically. The original model judgments remain unchanged, with the quote-format versions documented under `results/judgments/`.

`prepare.py` verifies gold source excerpts and freezes the questions before system outputs are examined. Its regexes locate the gold evidence; they are not used to score retrieval or answers. Changing the question set invalidates the existing experiment. Questions were authored for this local benchmark, not taken from an established external benchmark.

The first unscored warm-up was: “What does a pandas DataFrame represent?”

## Read the results

- `questions.md` / `questions.jsonl`: test questions, standard answers, required points and sources.
- `results/metadata.json`: code/corpus/benchmark versions, model names and experimental settings, without credentials.
- `results/Q*_*.json` / `results/raw_results.jsonl`: original outputs, all five retrieved passages, citations and timing.
- `results/judgments/`: anonymous model-assisted grading and the exact judging prompt.
- `review_overrides.json`: explicit evidence-based review changes with reasons; original judgments are retained.
- `audit.md`: question-by-question answers, scores, relevance labels and supporting quotes.
- `results/scores.csv` / `retrieval_labels.csv`: machine-readable per-answer and per-passage judgments.
- `results/summary.json`: the six agreed evaluation metrics.
- `figures/`: PNG/SVG quality and latency comparisons for the report or slides.

The evidence-based judge uses the same configured generation model as the system. `grade.py` targets the DeepSeek endpoint configured for this experiment, requests JSON output with thinking disabled, and uses four grading workers with a 180-second timeout. The original evaluation received project-member review. A later evidence check on 2026-11-22 corrected Q01 structure-aware rank 1 from irrelevant to relevant, and the project member accepted the correction. The method is model-assisted initial scoring followed by human review of the existing scores, rather than independent blind human ratings. The confirmation is recorded in `human_review.json` and tied to this experiment's artifact hashes; changing the results invalidates it. End-to-end latency is measured during system runs only; grading occurs afterwards.

`python eval/check_examples.py` optionally reproduces two review findings; it additionally requires pandas and numpy (the recorded run used pandas 3.1.1). `python eval/plot.py` creates PNG/SVG figures and additionally requires matplotlib. Neither is required to run the backend.

## Human review confirmation

A project member confirmed the original scores on 2026-11-19. The later Q01 correction changes structure-aware MRR@5 to 0.9375. The project member accepted this correction on 2026-11-22. The current confirmation is tied to the revised artifact hashes; the earlier confirmation is preserved in its history. `human_review.json` records this confirmation. Model judgments and evidence-based corrections remain separate from the human confirmation.

The local correction is documented in `results/label_correction_2026-11-22.json`. No system answers were rerun or changed.
