"""Optional local checks for two claims found during answer review.

This is outside the timed benchmark. It requires pandas and numpy, and does not
call a model or modify the benchmark. The observed version is recorded in output.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd

result = {"pandas_version": pd.__version__}
result["Q14_nan_key_mapping"] = {
    "code": "pd.Series([np.nan]).map({np.nan: 7}).tolist()",
    "observed": pd.Series([np.nan]).map({np.nan: 7}).tolist(),
    "meaning": "A plain dictionary can contain a missing-value key; existing missing values do not universally stay NaN.",
}
try:
    pd.Series([1], index=["a"]).iloc["a"]
except Exception as exc:
    result["Q18_invalid_iloc_label"] = {
        "code": "pd.Series([1], index=['a']).iloc['a']",
        "observed_exception": type(exc).__name__,
        "meaning": "The cited user-guide sentence says IndexError, while the installed version raises TypeError for this scalar string label.",
    }
path = Path(__file__).resolve().parent / "results/local_checks.json"
path.write_text(json.dumps(result, indent=2)+"\n")
print(json.dumps(result, indent=2))
