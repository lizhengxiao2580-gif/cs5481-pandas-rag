"""Aggregate the six agreed metrics from reviewed per-question judgments (no API calls)."""
import csv
import hashlib
import json
import re
from pathlib import Path
from statistics import mean, median
from review_status import human_review_statement

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT / "eval"
RESULTS = EVAL / "results"
STRATEGIES = ("fixed_size", "structure_aware")


def metrics(rows):
    positive = [r for r in rows if r["answerable"]]
    negative = [r for r in rows if not r["answerable"]]
    answered = [r for r in positive if r["status"] == "ok" and not r["refused"]]
    success = [r for r in rows if r["status"] == "ok"]
    return {
        "n_answerable": len(positive), "n_unanswerable": len(negative),
        "retrieval_hits": sum(r["hit_at_5"] for r in positive),
        "hit_at_5": mean(r["hit_at_5"] for r in positive),
        "mrr_at_5": mean(r["reciprocal_rank_at_5"] for r in positive),
        "correct_answers": sum(r["correct"] for r in positive),
        "answer_correctness": mean(r["correct"] for r in positive),
        "faithful_answers": sum(r["faithful"] is True for r in answered),
        "faithfulness_denominator": len(answered),
        "faithfulness": mean(r["faithful"] is True for r in answered) if answered else None,
        "correct_refusals": sum(r["status"] == "ok" and r["refused"] for r in negative),
        "refusal_success": mean(r["status"] == "ok" and r["refused"] for r in negative),
        "false_refusals": sum(r["status"] == "ok" and r["refused"] for r in positive),
        "latency_mean_s": mean(r["wall_latency_ms"]/1000 for r in success),
        "latency_median_s": median(r["wall_latency_ms"]/1000 for r in success),
        "errors": len(rows)-len(success),
    }


def main():
    questions = [json.loads(l) for l in (EVAL / "questions.jsonl").read_text().splitlines()]
    metadata = json.loads((RESULTS / "metadata.json").read_text())
    assert hashlib.sha256((EVAL / "questions.jsonl").read_bytes()).hexdigest() == metadata["configuration"]["questions_sha256"], "The frozen benchmark changed"
    assert len(list(RESULTS.glob("Q*.json"))) == 2*len(questions), "Incomplete system results"
    overrides_path = EVAL / "review_overrides.json"
    overrides = json.loads(overrides_path.read_text()) if overrides_path.exists() else {}
    rows, audit, detail, issues = [], [], [], []
    for q in questions:
        judgment = json.loads((RESULTS / "judgments" / f"{q['id']}.json").read_text())
        if judgment["benchmark_issue"]:
            issues.append(q["id"]+": "+judgment["benchmark_issue"])
        audit.append(f"## {q['id']} — {q['category']}\n\n{q['question']}\n\n**Gold answer:** {q['gold_answer']}\n\n**Required points:** "+"; ".join(q["required_points"])+"\n")
        pair = {}
        for strategy in STRATEGIES:
            result = json.loads((RESULTS / f"{q['id']}_{strategy}.json").read_text())
            grade = judgment["systems"][strategy]
            if patch := overrides.get(q["id"], {}).get(strategy):
                grade = {**grade, **{k:v for k,v in patch.items() if k != "review_reason"}}
            assert len(grade["retrieval"]) == len(result["hits"]) == 5
            for label, hit in zip(grade["retrieval"], result["hits"]):
                if label["relevant"]:
                    quote = re.sub(r"\s+", " ", label["quote"]).strip()
                    assert quote and quote in re.sub(r"\s+", " ", hit["text"]), "Review evidence must be verbatim"
            relevant_ranks = [g["rank"] for g in grade["retrieval"] if g["relevant"]]
            first = min(relevant_ranks, default=0)
            row = {"question_id": q["id"], "category": q["category"], "answerable": q["answerable"],
                   "strategy": strategy, "status": result["status"], "hit_at_5": int(bool(first)),
                   "first_relevant_rank": first, "reciprocal_rank_at_5": 1/first if first else 0,
                   "correct": grade["correct"], "faithful": grade["faithful"], "refused": result["refused"],
                   "wall_latency_ms": result["wall_latency_ms"], "reason": grade["reason"],
                   "unsupported_claims": " | ".join(grade["unsupported_claims"])}
            rows.append(row)
            pair[strategy] = row
            audit.append(f"### {strategy}\n\n{result['answer']}\n\nCorrect: **{grade['correct']}**; faithful: **{grade['faithful']}**; refused: **{result['refused']}**; first relevant rank: **{first}**.\n\n{grade['reason']}\n")
            if grade["unsupported_claims"]:
                audit.append("Unsupported claims: "+"; ".join(grade["unsupported_claims"])+"\n")
            audit.append("| Rank | Relevant | Source | Evidence / reason |\n|---|---|---|---|")
            for g,h in zip(grade["retrieval"],result["hits"]):
                quote = (g["quote"] if g["relevant"] else g["reason"]).replace("\n"," ").replace("|","\\|")
                audit.append(f"| {g['rank']} | {g['relevant']} | [{h['doc_id']}]({h['url']}) | {quote} |")
                detail.append({"question_id": q["id"], "strategy": strategy, "rank": g["rank"],
                               "chunk_id": h["chunk_id"], "relevant": g["relevant"], "quote": g["quote"], "reason": g["reason"]})
            audit.append("")
        # Identical retrieved texts must receive the same relevance label in a pair.
        labels = {}
        for strategy in STRATEGIES:
            result = json.loads((RESULTS / f"{q['id']}_{strategy}.json").read_text())
            grade = judgment["systems"][strategy]
            grade = {**grade, **overrides.get(q["id"], {}).get(strategy, {})}
            for h,g in zip(result["hits"],grade["retrieval"]):
                if h["text"] in labels and labels[h["text"]] != g["relevant"]:
                    issues.append(q["id"]+": identical text has inconsistent relevance labels")
                labels[h["text"]] = g["relevant"]
    for name, data in (("scores.csv",rows),("retrieval_labels.csv",detail)):
        with (RESULTS/name).open("w", newline="",encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f,fieldnames=list(data[0])); writer.writeheader(); writer.writerows(data)
    summary = {s: metrics([r for r in rows if r["strategy"]==s]) for s in STRATEGIES}
    (RESULTS / "summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    (EVAL / "audit.md").write_text("# Per-question grading audit\n\nInitial model-assisted judgments and evidence-based corrections are preserved separately.\n\n"+human_review_statement()+"\n\n"+"\n".join(audit),encoding="utf-8")
    (RESULTS / "review_flags.json").write_text(json.dumps(issues,indent=2)+"\n")
    (EVAL / "questions.md").write_text(("# Frozen evaluation questions\n\n"+"\n\n".join(f"## {q['id']} ({q['category']})\n\n{q['question']}\n\n**Reference answer:** {q['gold_answer']}\n\n"+"\n".join(f"- {p}" for p in q["required_points"])+"\n\n"+"\n".join(f"- [{e['section_id']}]({e['url']})" for e in q["gold_evidence"]) for q in questions)).rstrip()+"\n", encoding="utf-8")
    print(json.dumps(summary,indent=2))
    print("REVIEW FLAGS",json.dumps(issues))


if __name__ == "__main__":
    main()
