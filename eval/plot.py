"""Create shareable figures after summarize.py. Requires matplotlib (plotting only)."""
import json
from review_status import human_review_complete
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

EVAL = Path(__file__).resolve().parent
data = json.loads((EVAL / "results/summary.json").read_text())
out = EVAL / "figures"
out.mkdir(exist_ok=True)
plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":11, "axes.spines.top":False,
                     "axes.spines.right":False, "figure.dpi":150, "savefig.dpi":200})
strategies = ("fixed_size", "structure_aware")
colors = ("#3264b7", "#16836e")
metrics = [("Hit@5", "hit_at_5"), ("MRR@5", "mrr_at_5"), ("Answer\ncorrectness", "answer_correctness"),
           ("Citation\nfaithfulness", "faithfulness"), ("Refusal\nsuccess", "refusal_success")]
fig,ax=plt.subplots(figsize=(10.4,4.8),layout="constrained")
x=np.arange(len(metrics))
for i,s in enumerate(strategies):
    vals=[data[s][key] for _,key in metrics]
    bars=ax.bar(x+(i-.5)*.34,vals,width=.34,label=("Fixed window" if i==0 else "Structure aware"),color=colors[i])
    ax.bar_label(bars,labels=[f"{v:.3f}" if j==1 else f"{v:.1%}" for j,v in enumerate(vals)],padding=3,fontsize=9)
ax.set(xticks=x,xticklabels=[label for label,_ in metrics],ylim=(0,1.18),ylabel="Score (0–1)",
       title="Pandas RAG: paired chunking comparison")
ax.legend(loc="upper right",frameon=False,ncol=2)
ax.set_yticks(np.linspace(0,1,6)); ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
review_label = "human review" if human_review_complete() else "evidence-based checks"
fig.text(.015,.005,f"24 answerable + 6 unanswerable questions. Model-assisted scores with {review_label}; one run per strategy.",fontsize=8,color="#555555")
fig.savefig(out/"quality_comparison.png",bbox_inches="tight")
fig.savefig(out/"quality_comparison.svg",bbox_inches="tight")
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.6,4.4),layout="constrained")
for i,s in enumerate(strategies):
    vals=[data[s][k] for k in ("latency_mean_s","latency_median_s")]
    bars=ax.bar(np.arange(2)+(i-.5)*.34,vals,width=.34,label=("Fixed window" if i==0 else "Structure aware"),color=colors[i])
    ax.bar_label(bars,fmt="%.2f s",padding=3,fontsize=10)
ax.set(xticks=[0,1],xticklabels=["Mean","Median"],ylabel="Seconds",title="Observed end-to-end response latency")
ax.set_ylim(0,max(data[s]["latency_mean_s"] for s in strategies)*1.28)
ax.legend(frameon=False);ax.grid(axis="y",alpha=.18);ax.set_axisbelow(True)
fig.text(.015,.005,"30 requests per strategy; up to two concurrent questions; includes remote API and retry time.",fontsize=8,color="#555555")
fig.savefig(out/"latency_comparison.png",bbox_inches="tight")
fig.savefig(out/"latency_comparison.svg",bbox_inches="tight")
plt.close(fig)
print("Saved figures to",out)
