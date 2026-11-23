# Judge provenance

The first attempt used the application's 40-second timeout and provider-default thinking; it was stopped before any judgments were saved. The saved judgments use DeepSeek V4 Pro, JSON output, thinking disabled, requested temperature 0, max_tokens 6000 and a 180-second timeout, with four workers. Formal generation had finished before grading started.

26 judgments passed the original verbatim-quote validation. Q07, Q15, Q18 and Q20 initially failed because a quote was not a literal source substring. They were rerun with normalized passage whitespace, a shorter contiguous-quote instruction and source text in repair feedback. The scoring criteria and system answers were not changed. Both prompt variants are retained, and each judgment records its version. This was a formatting repair, not retesting system outputs.

Final evidence-based corrections are in ../../review_overrides.json. This includes nine relevance/quote corrections and two strict-correctness reviews, with executable examples in ../local_checks.json. Original model labels were not overwritten.

Initial scores were produced with model assistance and checked against source evidence and reproducible examples. A project member subsequently completed human review and confirmed the existing scores. This is model-assisted evaluation with human review, rather than independent blind human ratings.

Human review of the original retrieval text confirmed that Q01's first structure-aware passage already explained usecols. We corrected this false-negative relevance label before computing the final MRR@5 of 0.9375 (0.938 rounded). Other metrics and the original system outputs remain unchanged.
