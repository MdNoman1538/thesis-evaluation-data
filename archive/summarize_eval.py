"""
Summarise evaluation_log.jsonl into per-source statistics.
Outputs:
  - evaluation_summary.json (machine-readable, with all aggregates)
  - evaluation_summary.md (thesis-friendly tables)
"""
from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

EVAL_DIR = Path("/Users/noman/Documents/Thesis/evaluation")
LOG_PATH = EVAL_DIR / "evaluation_log.jsonl"


def short_source(p: str) -> str:
    """Compact label for a log path."""
    p = p.replace("/Users/noman/", "")
    p = p.replace("Projects/design stimuli/", "")
    p = p.replace("Documents/Thesis/Apps/", "")
    p = p.replace("/stimuli_log.jsonl", " (stimuli)")
    p = p.replace("/generation_log.jsonl", " (gen)")
    return p


def safe_mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def safe_std(xs):
    xs = [x for x in xs if x is not None]
    return statistics.pstdev(xs) if len(xs) > 1 else None


def main():
    by_source = defaultdict(list)
    for raw in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        rec = json.loads(raw)
        by_source[rec["source_file"]].append(rec)

    summary = {"sources": {}, "overall": {}}

    overall_records = []

    for src, records in sorted(by_source.items()):
        overall_records.extend(records)

        n = len(records)
        # Word-count spread (Rule 8 tolerance is 2)
        spreads = [r.get("word_count_spread") for r in records if "word_count_spread" in r]
        rule8_pass = sum(1 for s in spreads if s is not None and s <= 2)

        # Ordering checks
        bry_ord = [r.get("brysbaert_ordered_nc_lt_mc_lt_vc") for r in records if "brysbaert_ordered_nc_lt_mc_lt_vc" in r]
        wn_ord = [r.get("wordnet_ordered_nc_lt_mc_lt_vc") for r in records if "wordnet_ordered_nc_lt_mc_lt_vc" in r]

        # Per-condition aggregates
        def per_cond(cond, key):
            return [r[cond].get(key) for r in records if r.get(cond, {}).get("present")]

        s = {
            "n_stimuli": n,
            "rule8_word_count_spread_le_2": (rule8_pass, len(spreads)),
            "rule8_pct": (rule8_pass / len(spreads) * 100) if spreads else None,
            "spread_mean": safe_mean(spreads),
            "spread_max": max([s for s in spreads if s is not None], default=None),
            "brysbaert_nc_lt_mc_lt_vc": (sum(1 for x in bry_ord if x), len(bry_ord)) if bry_ord else None,
            "wordnet_nc_lt_mc_lt_vc": (sum(1 for x in wn_ord if x), len(wn_ord)) if wn_ord else None,
            "nc_brysbaert_mean": safe_mean(per_cond("nc", "brysbaert_mean")),
            "mc_brysbaert_mean": safe_mean(per_cond("mc", "brysbaert_mean")),
            "vc_brysbaert_mean": safe_mean(per_cond("vc", "brysbaert_mean")),
            "nc_wordnet_mean": safe_mean(per_cond("nc", "wordnet_depth_mean")),
            "mc_wordnet_mean": safe_mean(per_cond("mc", "wordnet_depth_mean")),
            "vc_wordnet_mean": safe_mean(per_cond("vc", "wordnet_depth_mean")),
            "nc_word_count_mean": safe_mean(per_cond("nc", "word_count")),
            "mc_word_count_mean": safe_mean(per_cond("mc", "word_count")),
            "vc_word_count_mean": safe_mean(per_cond("vc", "word_count")),
            "nc_sentence_count_mean": safe_mean(per_cond("nc", "sentence_count")),
            "vc_sentence_count_mean": safe_mean(per_cond("vc", "sentence_count")),
        }
        summary["sources"][short_source(src)] = s

    # Overall (across all sources combined)
    def per_cond_all(cond, key):
        return [r[cond].get(key) for r in overall_records if r.get(cond, {}).get("present")]

    spreads_all = [r.get("word_count_spread") for r in overall_records if "word_count_spread" in r]
    bry_ord_all = [r.get("brysbaert_ordered_nc_lt_mc_lt_vc") for r in overall_records if "brysbaert_ordered_nc_lt_mc_lt_vc" in r]
    wn_ord_all = [r.get("wordnet_ordered_nc_lt_mc_lt_vc") for r in overall_records if "wordnet_ordered_nc_lt_mc_lt_vc" in r]

    summary["overall"] = {
        "n_total": len(overall_records),
        "n_with_nc_mc_vc": len(spreads_all),
        "rule8_pass_count": sum(1 for s in spreads_all if s is not None and s <= 2),
        "rule8_pct": (sum(1 for s in spreads_all if s is not None and s <= 2) / len(spreads_all) * 100) if spreads_all else None,
        "brysbaert_ordering_pass_count": sum(1 for x in bry_ord_all if x),
        "brysbaert_ordering_total": len(bry_ord_all),
        "brysbaert_ordering_pct": (sum(1 for x in bry_ord_all if x) / len(bry_ord_all) * 100) if bry_ord_all else None,
        "wordnet_ordering_pass_count": sum(1 for x in wn_ord_all if x),
        "wordnet_ordering_total": len(wn_ord_all),
        "wordnet_ordering_pct": (sum(1 for x in wn_ord_all if x) / len(wn_ord_all) * 100) if wn_ord_all else None,
        "nc_brysbaert_mean": safe_mean(per_cond_all("nc", "brysbaert_mean")),
        "mc_brysbaert_mean": safe_mean(per_cond_all("mc", "brysbaert_mean")),
        "vc_brysbaert_mean": safe_mean(per_cond_all("vc", "brysbaert_mean")),
        "nc_wordnet_mean": safe_mean(per_cond_all("nc", "wordnet_depth_mean")),
        "mc_wordnet_mean": safe_mean(per_cond_all("mc", "wordnet_depth_mean")),
        "vc_wordnet_mean": safe_mean(per_cond_all("vc", "wordnet_depth_mean")),
    }

    (EVAL_DIR / "evaluation_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Markdown report
    lines = ["# Evaluation Summary — Prior Generated Stimuli", ""]
    o = summary["overall"]
    lines.append(f"**{o['n_total']} stimulus records evaluated; {o['n_with_nc_mc_vc']} have all three NC/MC/VC paragraphs.**")
    lines.append("")
    lines.append("## Rule 8 (word-count parity within ±2 across NC/MC/VC)")
    if o["rule8_pct"] is not None:
        lines.append(f"- Pass rate: **{o['rule8_pass_count']}/{o['n_with_nc_mc_vc']} = {o['rule8_pct']:.1f}%**")
    lines.append("")
    lines.append("## Abstraction-ordering (NC < MC < VC)")
    lines.append(f"- Brysbaert concreteness ordering correct: **{o['brysbaert_ordering_pass_count']}/{o['brysbaert_ordering_total']} = {o['brysbaert_ordering_pct']:.1f}%**" if o.get('brysbaert_ordering_pct') is not None else "- (no Brysbaert ordering data)")
    lines.append(f"- WordNet hypernym-depth ordering correct: **{o['wordnet_ordering_pass_count']}/{o['wordnet_ordering_total']} = {o['wordnet_ordering_pct']:.1f}%**" if o.get('wordnet_ordering_pct') is not None else "- (no WordNet ordering data)")
    lines.append("")
    lines.append("## Mean abstraction scores per condition (across all sources)")
    lines.append("")
    lines.append("| Condition | Brysbaert (1=abstract … 5=concrete) | WordNet hypernym depth (smaller = more abstract) |")
    lines.append("|---|---|---|")
    fmt = lambda x: f"{x:.3f}" if x is not None else "—"
    lines.append(f"| NC | {fmt(o['nc_brysbaert_mean'])} | {fmt(o['nc_wordnet_mean'])} |")
    lines.append(f"| MC | {fmt(o['mc_brysbaert_mean'])} | {fmt(o['mc_wordnet_mean'])} |")
    lines.append(f"| VC | {fmt(o['vc_brysbaert_mean'])} | {fmt(o['vc_wordnet_mean'])} |")
    lines.append("")
    lines.append("## Per-source breakdown")
    lines.append("")
    lines.append("| Source | n | Rule 8 pass % | Brysbaert NC<MC<VC % | WordNet NC<MC<VC % | NC Brys | MC Brys | VC Brys |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for src, s in summary["sources"].items():
        rule8 = f"{s['rule8_pct']:.1f}%" if s.get("rule8_pct") is not None else "—"
        bry_ord_pct = (s["brysbaert_nc_lt_mc_lt_vc"][0] / s["brysbaert_nc_lt_mc_lt_vc"][1] * 100) if s.get("brysbaert_nc_lt_mc_lt_vc") and s["brysbaert_nc_lt_mc_lt_vc"][1] else None
        wn_ord_pct = (s["wordnet_nc_lt_mc_lt_vc"][0] / s["wordnet_nc_lt_mc_lt_vc"][1] * 100) if s.get("wordnet_nc_lt_mc_lt_vc") and s["wordnet_nc_lt_mc_lt_vc"][1] else None
        lines.append(
            f"| {src} | {s['n_stimuli']} | {rule8} | "
            f"{f'{bry_ord_pct:.1f}%' if bry_ord_pct is not None else '—'} | "
            f"{f'{wn_ord_pct:.1f}%' if wn_ord_pct is not None else '—'} | "
            f"{fmt(s['nc_brysbaert_mean'])} | {fmt(s['mc_brysbaert_mean'])} | {fmt(s['vc_brysbaert_mean'])} |"
        )
    (EVAL_DIR / "evaluation_summary.md").write_text("\n".join(lines), encoding="utf-8")

    print((EVAL_DIR / "evaluation_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
