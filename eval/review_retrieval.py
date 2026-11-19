"""Reproduce explicit evidence-based relevance-label corrections after inspecting full passages.

No model outputs or original judgments are modified. Every replacement quote is
looked up as a literal substring in the saved passage; assumptions about example
column names must not make an otherwise transferable pandas operation irrelevant.
"""
import json
from pathlib import Path
import re

EVAL = Path(__file__).resolve().parent
path = EVAL / "review_overrides.json"
overrides = json.loads(path.read_text())
CHANGES = [
    ("Q04", "fixed_size", 5, True, 'DataFrame.dropna() drops any rows that have missing data:',
     "The how='any' example supports the second required point even without illustrating subset; one supported required point is sufficient for relevance."),
    ("Q07", "structure_aware", 1, True, 'The method will melt all columns NOT mentioned in id_vars together into two columns:',
     "The full passage uses id_vars to retain date.utc and shows it in the long-format output. Identifier names need not literally be id; this supports the first required point."),
    ("Q07", "fixed_size", 3, True, 'cheese.melt(id_vars=["first", "last"])',
     "The full example preserves first/last identifier columns; it supports id_vars, not just the optional output-column renaming described in the initial judge quote."),
    ("Q16", "fixed_size", 5, False, '',
     "A signature listing low_memory=True, iterator=False and chunksize=None plus a general introduction does not establish the output behavior of the options; substantive explanatory evidence is required."),
    ("Q16", "structure_aware", 5, False, '',
     "The identical API-signature passage is not substantive evidence of low_memory/chunksize return behavior; apply the same relevance criterion to both strategies."),
    ("Q18", "structure_aware", 2, True, 's.loc[3:5]\nOut[75]:\n3 b\n2 c\n5 d',
     "The actual example includes both endpoint labels, substantiating inclusive label slicing. Replace the initial heading-only quote with this substantive example."),
    ("Q23", "fixed_size", 2, True, 'Generic rolling windows support specifying windows as a fixed number of observations or variable number of observations based on an offset.',
     "This explicitly explains the size of a rolling window and supports the first required point; evidence for expanding is not also required for relevance."),
    ("Q23", "fixed_size", 4, True, '# Window with 2 observations\nIn [25]: s.rolling(window=2).sum()',
     "The full worked output demonstrates the moving two-observation window, providing substantive evidence for the rolling-window point."),
]

for q, strategy, rank, relevant, quote, reason in CHANGES:
    original = json.loads((EVAL / f"results/judgments/{q}.json").read_text())["systems"][strategy]
    patch = overrides.setdefault(q, {}).setdefault(strategy, {})
    if "retrieval" not in patch:
        patch["retrieval"] = original["retrieval"]
    hit = json.loads((EVAL / f"results/{q}_{strategy}.json").read_text())["hits"][rank-1]
    if relevant:
        norm = lambda text: re.sub(r"\s+", " ", text).strip()
        assert norm(quote) in norm(hit["text"]), (q, strategy, rank)
    patch["retrieval"][rank-1] = {"rank":rank, "relevant":relevant, "quote":quote, "reason":reason}
    patch["review_reason"] = "The review checked the full saved passages and corrected relevance/quote consistency; original judge labels are preserved in results/judgments/."

path.write_text(json.dumps(overrides,ensure_ascii=False,indent=2)+"\n")
print("Applied",len(CHANGES),"explicit relevance/quote corrections")
