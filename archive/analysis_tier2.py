"""
Tier-2 analyses for the thesis Evaluation chapter.

Inputs:
  - evaluation_log.jsonl  (per-record metrics produced earlier)
  - raw stimuli_log.jsonl files (for noun extraction in H4)

Outputs:
  - tier2_results.md / tier2_results.json
  - figures/word_count_spread_distribution.pdf (.png)
  - figures/per_model_ordering.pdf (.png)
  - figures/top_nouns_per_condition.pdf (.png)

Analyses:
  B1.  Pre-Rule-8 vs post-Rule-8 word-count parity comparison.
       Cutoff: 2026-05-08T00:00:00 (rule was discussed and added that day).
  C1.  Per-model ordering pass rate (Brysbaert NC<MC<VC, WordNet NC<MC<VC,
       Rule 8 spread ≤ 2). Reports n, pass-rate, and mean abstraction shift
       per model.
  A6.  Distribution of word_count_spread across all 661 records — full
       breakdown per spread value, plus mean / median / max and percentile.
  H4.  Top-50 most-frequent nouns per NC / MC / VC condition. Source: raw
       stimuli logs. Output: text tables and a side-by-side bar chart of
       the top 15 each.
"""
from __future__ import annotations

import json
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Reuse the analyzer's noun extractor for H4
ANALYZER_DIR = Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1/semantic_analyzer")
sys.path.insert(0, str(ANALYZER_DIR))
import spacy  # noqa: E402

NLP = spacy.load("en_core_web_sm")

EVAL_DIR = Path("/Users/noman/Documents/Thesis/evaluation")
LOG_PATH = EVAL_DIR / "evaluation_log.jsonl"
FIG_DIR = EVAL_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

RULE8_CUTOFF = datetime(2026, 5, 8, 0, 0, 0)


# ── helpers ─────────────────────────────────────────────────────────────────


def load_eval():
    return [
        json.loads(l)
        for l in LOG_PATH.read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]


def parse_ts(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def extract_nouns(text: str) -> list[str]:
    if not text:
        return []
    doc = NLP(text)
    return [tok.lemma_.lower() for tok in doc if tok.pos_ in ("NOUN", "PROPN") and tok.is_alpha]


# ── B1. Pre-Rule-8 vs post-Rule-8 ──────────────────────────────────────────


def b1_rule8_split(records):
    pre, post, undated = [], [], []
    for r in records:
        ts = parse_ts(r.get("timestamp"))
        if ts is None:
            undated.append(r)
        elif ts < RULE8_CUTOFF:
            pre.append(r)
        else:
            post.append(r)

    def stats_for(group):
        spreads = [r.get("word_count_spread") for r in group if "word_count_spread" in r and r["word_count_spread"] is not None]
        bry_ord = [r.get("brysbaert_ordered_nc_lt_mc_lt_vc") for r in group if "brysbaert_ordered_nc_lt_mc_lt_vc" in r]
        wn_ord = [r.get("wordnet_ordered_nc_lt_mc_lt_vc") for r in group if "wordnet_ordered_nc_lt_mc_lt_vc" in r]

        def pct(passed, total):
            return None if not total else passed / total * 100

        return {
            "n": len(group),
            "n_with_spread": len(spreads),
            "rule8_pass": sum(1 for s in spreads if s <= 2),
            "rule8_pct": pct(sum(1 for s in spreads if s <= 2), len(spreads)),
            "spread_mean": statistics.fmean(spreads) if spreads else None,
            "spread_median": statistics.median(spreads) if spreads else None,
            "spread_max": max(spreads) if spreads else None,
            "brysbaert_pass": sum(1 for x in bry_ord if x),
            "brysbaert_pct": pct(sum(1 for x in bry_ord if x), len(bry_ord)),
            "wordnet_pass": sum(1 for x in wn_ord if x),
            "wordnet_pct": pct(sum(1 for x in wn_ord if x), len(wn_ord)),
        }

    return {
        "cutoff": RULE8_CUTOFF.isoformat(),
        "pre_rule8": stats_for(pre),
        "post_rule8": stats_for(post),
        "undated": stats_for(undated),
    }


# ── C1. Per-model breakdown ────────────────────────────────────────────────


def c1_per_model(records):
    by_model = defaultdict(list)
    for r in records:
        m = (r.get("model") or "").strip() or "(unknown)"
        by_model[m].append(r)

    rows = []
    for m, recs in sorted(by_model.items(), key=lambda x: -len(x[1])):
        spreads = [r.get("word_count_spread") for r in recs if "word_count_spread" in r and r["word_count_spread"] is not None]
        bry = [r.get("brysbaert_ordered_nc_lt_mc_lt_vc") for r in recs if "brysbaert_ordered_nc_lt_mc_lt_vc" in r]
        wn = [r.get("wordnet_ordered_nc_lt_mc_lt_vc") for r in recs if "wordnet_ordered_nc_lt_mc_lt_vc" in r]

        nc_b = [(r.get("nc") or {}).get("brysbaert_mean") for r in recs]
        vc_b = [(r.get("vc") or {}).get("brysbaert_mean") for r in recs]
        # NC→VC shift per record
        shifts = []
        for n, v in zip(nc_b, vc_b):
            if n is not None and v is not None:
                shifts.append(v - n)

        rows.append({
            "model": m,
            "n": len(recs),
            "rule8_pct": (sum(1 for s in spreads if s <= 2) / len(spreads) * 100) if spreads else None,
            "spread_mean": statistics.fmean(spreads) if spreads else None,
            "brysbaert_pct": (sum(1 for x in bry if x) / len(bry) * 100) if bry else None,
            "wordnet_pct": (sum(1 for x in wn if x) / len(wn) * 100) if wn else None,
            "nc_to_vc_shift_mean": statistics.fmean(shifts) if shifts else None,
        })
    return rows


# ── A6. Word-count-spread distribution ─────────────────────────────────────


def a6_spread_distribution(records):
    spreads = [r.get("word_count_spread") for r in records if "word_count_spread" in r and r["word_count_spread"] is not None]
    counts = Counter(spreads)
    breakdown = sorted(counts.items())  # list of (spread_value, count)

    summary = {
        "n": len(spreads),
        "mean": statistics.fmean(spreads) if spreads else None,
        "median": statistics.median(spreads) if spreads else None,
        "p90": float(np.percentile(spreads, 90)) if spreads else None,
        "p95": float(np.percentile(spreads, 95)) if spreads else None,
        "p99": float(np.percentile(spreads, 99)) if spreads else None,
        "max": max(spreads) if spreads else None,
        "spread_breakdown": [{"spread": k, "count": v, "cumulative_pct": None} for k, v in breakdown],
    }
    cum = 0
    for entry in summary["spread_breakdown"]:
        cum += entry["count"]
        entry["cumulative_pct"] = cum / len(spreads) * 100

    # Histogram
    fig, ax = plt.subplots(figsize=(8, 4.5))
    max_x = max(spreads) if spreads else 0
    bins = np.arange(0, min(max_x + 2, 50) + 1) - 0.5
    ax.hist(spreads, bins=bins, color="#4472C4", edgecolor="white", linewidth=0.5)
    ax.axvline(x=2.5, color="red", linestyle="--", linewidth=1, label="Rule 8 boundary (≤2)")
    ax.set_xlabel("Word-count spread (max − min across NC/MC/VC paragraphs)")
    ax.set_ylabel("Number of stimulus sets")
    ax.set_title(f"Distribution of word-count spread (n={len(spreads)})")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "word_count_spread_distribution.pdf")
    fig.savefig(FIG_DIR / "word_count_spread_distribution.png", dpi=160)
    plt.close(fig)

    return summary


# ── H4. Top nouns per condition ────────────────────────────────────────────


def h4_top_nouns(top_n=50):
    """Re-tokenize raw stimuli from all stimuli_log.jsonl files."""
    roots = [
        Path("/Users/noman/Projects/design stimuli"),
        Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1"),
    ]
    sources = []
    for r in roots:
        if r.exists():
            sources.extend(r.rglob("stimuli_log.jsonl"))
            sources.extend(r.rglob("generation_log.jsonl"))

    counter_nc, counter_mc, counter_vc = Counter(), Counter(), Counter()
    n_seen = 0
    for src in sources:
        for raw in src.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not raw.strip():
                continue
            try:
                e = json.loads(raw)
            except json.JSONDecodeError:
                continue
            for cond, ctr in [("nc", counter_nc), ("mc", counter_mc), ("vc", counter_vc)]:
                txt = e.get(cond)
                if txt:
                    for n in extract_nouns(txt):
                        ctr[n] += 1
            n_seen += 1
            if n_seen % 200 == 0:
                print(f"  ...processed {n_seen} stimulus entries for noun frequencies")

    return {
        "n_processed": n_seen,
        "NC": counter_nc.most_common(top_n),
        "MC": counter_mc.most_common(top_n),
        "VC": counter_vc.most_common(top_n),
    }


def plot_top_nouns(top_n_dict):
    """Side-by-side bar charts of the top 15 nouns in each condition."""
    fig, axes = plt.subplots(1, 3, figsize=(13, 6), sharey=False)
    colors = {"NC": "#5B9BD5", "MC": "#ED7D31", "VC": "#70AD47"}
    for ax, cond in zip(axes, ("NC", "MC", "VC")):
        items = top_n_dict[cond][:15]
        words = [w for w, _ in items][::-1]
        counts = [c for _, c in items][::-1]
        ax.barh(words, counts, color=colors[cond], alpha=0.85)
        ax.set_title(f"Top 15 nouns in {cond}")
        ax.set_xlabel("Frequency")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("Most frequent nouns per condition (across all evaluated stimulus sets)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "top_nouns_per_condition.pdf")
    fig.savefig(FIG_DIR / "top_nouns_per_condition.png", dpi=160)
    plt.close(fig)


# ── reporting ───────────────────────────────────────────────────────────────


def write_report(b1, c1, a6, h4):
    L = []
    L.append("# Tier 2 Analyses")
    L.append("")
    L.append("Followups to Tier 1; tightens the *why* behind the headline numbers.")
    L.append("")

    # B1
    L.append("## B1. Pre-Rule-8 vs post-Rule-8 word-count parity")
    L.append("")
    L.append(f"Cutoff: **{b1['cutoff']}** (Rule 8 was added in the system prompt on May 8, 2026).")
    L.append("")
    L.append("| Group | n | n with NC/MC/VC | Rule 8 pass | Spread mean | Spread max | Brys NC<MC<VC | WN NC<MC<VC |")
    L.append("|-------|---|-----------------|-------------|-------------|-----------|---------------|-------------|")
    for label, key in [("Pre-Rule-8", "pre_rule8"), ("Post-Rule-8", "post_rule8"), ("Undated", "undated")]:
        s = b1[key]
        rule8 = f"{s['rule8_pass']}/{s['n_with_spread']} ({s['rule8_pct']:.1f}%)" if s.get("rule8_pct") is not None else "—"
        sm = f"{s['spread_mean']:.2f}" if s.get("spread_mean") is not None else "—"
        smax = s.get("spread_max", "—")
        bp = f"{s['brysbaert_pass']} ({s['brysbaert_pct']:.1f}%)" if s.get("brysbaert_pct") is not None else "—"
        wp = f"{s['wordnet_pass']} ({s['wordnet_pct']:.1f}%)" if s.get("wordnet_pct") is not None else "—"
        L.append(f"| {label} | {s['n']} | {s['n_with_spread']} | {rule8} | {sm} | {smax} | {bp} | {wp} |")
    L.append("")

    # C1
    L.append("## C1. Per-model breakdown")
    L.append("")
    L.append("| Model | n | Rule 8 pass | Brys NC<MC<VC | WN NC<MC<VC | NC→VC Brys shift | Mean spread |")
    L.append("|-------|---|-------------|---------------|-------------|------------------|-------------|")
    for r in c1:
        rp = f"{r['rule8_pct']:.1f}%" if r.get("rule8_pct") is not None else "—"
        bp = f"{r['brysbaert_pct']:.1f}%" if r.get("brysbaert_pct") is not None else "—"
        wp = f"{r['wordnet_pct']:.1f}%" if r.get("wordnet_pct") is not None else "—"
        sh = f"{r['nc_to_vc_shift_mean']:+.3f}" if r.get("nc_to_vc_shift_mean") is not None else "—"
        sm = f"{r['spread_mean']:.2f}" if r.get("spread_mean") is not None else "—"
        L.append(f"| {r['model']} | {r['n']} | {rp} | {bp} | {wp} | {sh} | {sm} |")
    L.append("")

    # A6
    L.append("## A6. Word-count spread — full distribution")
    L.append("")
    L.append(
        f"n = {a6['n']}; mean spread = {a6['mean']:.2f} words; median = {a6['median']:.1f}; "
        f"90th pct = {a6['p90']:.1f}; 95th pct = {a6['p95']:.1f}; 99th pct = {a6['p99']:.1f}; max = {a6['max']}."
    )
    L.append("")
    L.append("| Spread (words) | Count | Cumulative % |")
    L.append("|----------------|-------|--------------|")
    for entry in a6["spread_breakdown"][:25]:  # show first 25 spread values
        L.append(f"| {entry['spread']} | {entry['count']} | {entry['cumulative_pct']:.1f}% |")
    if len(a6["spread_breakdown"]) > 25:
        L.append(f"| … | (more {len(a6['spread_breakdown'])-25} bins) | |")
    L.append("")
    L.append("Histogram: `figures/word_count_spread_distribution.pdf`")
    L.append("")

    # H4
    L.append("## H4. Top-50 nouns per condition")
    L.append("")
    L.append(f"Source: re-tokenized {h4['n_processed']} stimulus entries across all log files.")
    L.append("")
    for cond in ("NC", "MC", "VC"):
        L.append(f"### {cond} — top 50")
        L.append("")
        L.append("| Rank | Noun | Count |")
        L.append("|------|------|-------|")
        for i, (w, c) in enumerate(h4[cond][:50], start=1):
            L.append(f"| {i} | {w} | {c} |")
        L.append("")
    L.append("Bar chart of top 15 each: `figures/top_nouns_per_condition.pdf`")
    L.append("")

    return "\n".join(L)


def main():
    records = load_eval()
    print(f"Loaded {len(records)} evaluation records")

    print("\n[B1] Pre-Rule-8 vs post-Rule-8…")
    b1 = b1_rule8_split(records)

    print("[C1] Per-model breakdown…")
    c1 = c1_per_model(records)

    print("[A6] Word-count-spread distribution…")
    a6 = a6_spread_distribution(records)

    print("[H4] Top-50 nouns per condition (re-tokenizing raw stimuli)…")
    h4 = h4_top_nouns(top_n=50)
    plot_top_nouns(h4)

    md = write_report(b1, c1, a6, h4)
    (EVAL_DIR / "tier2_results.md").write_text(md, encoding="utf-8")
    (EVAL_DIR / "tier2_results.json").write_text(json.dumps({
        "B1": b1, "C1": c1, "A6": a6, "H4": h4,
    }, indent=2), encoding="utf-8")

    print("\n=== HIGHLIGHTS ===\n")
    # Compact highlights printed to stdout
    pre = b1["pre_rule8"]; post = b1["post_rule8"]
    print(f"B1: Rule 8 pass — pre={pre['rule8_pct']:.1f}% (n={pre['n_with_spread']}), "
          f"post={post['rule8_pct']:.1f}% (n={post['n_with_spread']}); "
          f"delta = {(post['rule8_pct'] or 0) - (pre['rule8_pct'] or 0):+.1f} pts")
    print(f"A6: Spread distribution — mean={a6['mean']:.2f}, median={a6['median']:.1f}, max={a6['max']}")
    print(f"C1: Models with ≥10 records:")
    for r in c1:
        if r["n"] >= 10:
            print(f"   {r['model']:<35} n={r['n']:>4}  Rule8={r.get('rule8_pct') or 0:.1f}%  "
                  f"BrysOrd={r.get('brysbaert_pct') or 0:.1f}%  WnOrd={r.get('wordnet_pct') or 0:.1f}%")
    print(f"H4: Top-5 NC nouns: {[w for w,_ in h4['NC'][:5]]}")
    print(f"H4: Top-5 MC nouns: {[w for w,_ in h4['MC'][:5]]}")
    print(f"H4: Top-5 VC nouns: {[w for w,_ in h4['VC'][:5]]}")
    print(f"\nFull report: {EVAL_DIR / 'tier2_results.md'}")


if __name__ == "__main__":
    main()
