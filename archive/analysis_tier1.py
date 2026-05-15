"""
Tier-1 analyses for the thesis Evaluation chapter.

Inputs : evaluation_log.jsonl (661 records produced by evaluate_priors.py)
Outputs:
  figures/brysbaert_distribution.pdf      — histograms NC/MC/VC overlaid
  figures/wordnet_distribution.pdf        — same for WordNet hypernym depth
  figures/per_condition_box.pdf           — boxplots side by side
  tier1_results.md                        — t-tests, Cohen's d, repeatability
  tier1_results.json                      — same data, machine-readable

Analyses performed:
  A1. Distribution per condition (histograms + boxplots, summary stats).
  A2. Paired t-tests for NC↔MC, MC↔VC, NC↔VC on both Brysbaert and WordNet.
  A3. Cohen's d effect size for each comparison.
  E1. Same-task, same-model repeatability — within-group standard deviation
      of mean abstraction scores across regenerations.

The script reuses scoring logic already produced by evaluate_priors.py;
no re-evaluation of raw stimuli is performed here.
"""
from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

EVAL_DIR = Path("/Users/noman/Documents/Thesis/evaluation")
LOG_PATH = EVAL_DIR / "evaluation_log.jsonl"
FIG_DIR = EVAL_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ── helpers ──────────────────────────────────────────────────────────────────


def load_records():
    out = []
    for raw in LOG_PATH.read_text(encoding="utf-8").splitlines():
        if raw.strip():
            out.append(json.loads(raw))
    return out


def per_condition(records, cond, key):
    """Return list of values (skipping missing) for given condition+key."""
    out = []
    for r in records:
        c = r.get(cond) or {}
        v = c.get(key)
        if v is not None:
            out.append(v)
    return out


def per_record_triplet(records, key):
    """Return list of (nc,mc,vc) triplets where all three are present."""
    out = []
    for r in records:
        nc = (r.get("nc") or {}).get(key)
        mc = (r.get("mc") or {}).get(key)
        vc = (r.get("vc") or {}).get(key)
        if nc is not None and mc is not None and vc is not None:
            out.append((nc, mc, vc))
    return out


def cohens_d_paired(x, y):
    """Cohen's d for paired samples — uses standard deviation of differences."""
    diffs = [a - b for a, b in zip(x, y)]
    if len(diffs) < 2:
        return None
    sd = statistics.pstdev(diffs)
    if sd == 0:
        return float("inf")
    return statistics.fmean(diffs) / sd


def effect_label(d):
    if d is None:
        return "—"
    a = abs(d)
    if a < 0.2:
        return "negligible"
    if a < 0.5:
        return "small"
    if a < 0.8:
        return "medium"
    return "large"


def paired_t(x, y):
    """Return (t-stat, p-value, n)."""
    if len(x) != len(y) or len(x) < 2:
        return None
    t, p = stats.ttest_rel(x, y)
    return float(t), float(p), len(x)


# ── A1. distributions ───────────────────────────────────────────────────────


def a1_distributions(records):
    out = {}
    for label, key in [("Brysbaert", "brysbaert_mean"), ("WordNet", "wordnet_depth_mean")]:
        nc = per_condition(records, "nc", key)
        mc = per_condition(records, "mc", key)
        vc = per_condition(records, "vc", key)
        out[label] = {
            "NC": _stats_block(nc),
            "MC": _stats_block(mc),
            "VC": _stats_block(vc),
        }

        # Overlaid histograms
        fig, ax = plt.subplots(figsize=(8, 4.5))
        # Choose bin count based on Brysbaert vs WordNet range.
        all_v = nc + mc + vc
        lo, hi = min(all_v), max(all_v)
        bins = np.linspace(lo, hi, 30)
        for data, lab, c in [
            (nc, "NC", "#5B9BD5"),
            (mc, "MC", "#ED7D31"),
            (vc, "VC", "#70AD47"),
        ]:
            ax.hist(data, bins=bins, alpha=0.55, label=f"{lab}  (n={len(data)})", color=c, edgecolor="white", linewidth=0.4)
        ax.set_xlabel(
            "Mean Brysbaert concreteness (1 = abstract, 5 = concrete)"
            if label == "Brysbaert"
            else "Mean WordNet hypernym depth (smaller = more abstract)"
        )
        ax.set_ylabel("Number of stimulus sets")
        ax.set_title(f"Distribution of {label} mean per condition (n={len(nc)} stimulus sets)")
        ax.legend(frameon=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / f"{label.lower()}_distribution.pdf")
        fig.savefig(FIG_DIR / f"{label.lower()}_distribution.png", dpi=160)
        plt.close(fig)

    # Boxplot side-by-side for both metrics on shared figure
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for i, (label, key) in enumerate([("Brysbaert concreteness (1–5)", "brysbaert_mean"),
                                      ("WordNet hypernym depth", "wordnet_depth_mean")]):
        nc = per_condition(records, "nc", key)
        mc = per_condition(records, "mc", key)
        vc = per_condition(records, "vc", key)
        bp = axes[i].boxplot([nc, mc, vc], labels=["NC", "MC", "VC"], patch_artist=True, widths=0.55)
        for patch, c in zip(bp["boxes"], ["#5B9BD5", "#ED7D31", "#70AD47"]):
            patch.set_facecolor(c)
            patch.set_alpha(0.8)
        axes[i].set_title(label)
        axes[i].set_ylabel("Mean per stimulus set")
        axes[i].spines["top"].set_visible(False)
        axes[i].spines["right"].set_visible(False)
    fig.suptitle(f"Per-condition distributions across all {len(records)} stimulus sets", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "per_condition_box.pdf")
    fig.savefig(FIG_DIR / "per_condition_box.png", dpi=160)
    plt.close(fig)

    return out


def _stats_block(xs):
    if not xs:
        return None
    return {
        "n": len(xs),
        "mean": statistics.fmean(xs),
        "sd": statistics.pstdev(xs),
        "min": min(xs),
        "q25": float(np.percentile(xs, 25)),
        "median": statistics.median(xs),
        "q75": float(np.percentile(xs, 75)),
        "max": max(xs),
    }


# ── A2 + A3. paired t-tests + Cohen's d ─────────────────────────────────────


def a2a3_paired_tests(records):
    out = {}
    for label, key in [("Brysbaert", "brysbaert_mean"), ("WordNet", "wordnet_depth_mean")]:
        triples = per_record_triplet(records, key)
        nc = [t[0] for t in triples]
        mc = [t[1] for t in triples]
        vc = [t[2] for t in triples]

        comparisons = [
            ("NC vs MC", nc, mc),
            ("MC vs VC", mc, vc),
            ("NC vs VC", nc, vc),
        ]
        rows = []
        for name, a, b in comparisons:
            t = paired_t(a, b)
            d = cohens_d_paired(a, b)
            rows.append({
                "comparison": name,
                "n": t[2] if t else None,
                "mean_diff": statistics.fmean([y - x for x, y in zip(a, b)]) if len(a) == len(b) and a else None,
                "t": t[0] if t else None,
                "p": t[1] if t else None,
                "cohens_d": d,
                "effect": effect_label(d),
            })
        out[label] = rows
    return out


# ── E1. repeatability across regenerations ─────────────────────────────────


def e1_repeatability(records):
    """Group by (task, model). Within each group, measure variance of the
    per-stimulus mean abstraction scores. A stable rule-based system should
    produce low variance across regenerations of the same task with the same
    model."""
    groups = defaultdict(list)
    for r in records:
        task = (r.get("task") or "").strip()
        model = (r.get("model") or "").strip()
        if task and model:
            groups[(task, model)].append(r)

    summary = []
    for (task, model), recs in sorted(groups.items()):
        if len(recs) < 2:
            continue
        row = {"task": task, "model": model, "n_runs": len(recs)}
        for cond in ("nc", "mc", "vc"):
            for key, label in [("brysbaert_mean", "brysbaert"), ("wordnet_depth_mean", "wn"), ("word_count", "wc")]:
                vals = [(r.get(cond) or {}).get(key) for r in recs]
                vals = [v for v in vals if v is not None]
                if len(vals) >= 2:
                    row[f"{cond}_{label}_mean"] = statistics.fmean(vals)
                    row[f"{cond}_{label}_sd"] = statistics.pstdev(vals)
        summary.append(row)
    return summary


# ── reporting ───────────────────────────────────────────────────────────────


def write_markdown(distros, tests, repeat):
    lines = []
    lines.append("# Tier 1 Analyses — Empirical Core of Chapter 4")
    lines.append("")
    lines.append("Inputs: 661 stimulus records from `evaluation_log.jsonl`.")
    lines.append("All values computed with the project's `semantic_analyzer` module"
                 " (Brysbaert 40 k-word ratings on the original 1–5 scale; WordNet"
                 " hypernym depth using the shortest path to root for the most-abstract synset).")
    lines.append("")

    # A1
    lines.append("## A1. Per-condition distributions")
    lines.append("")
    lines.append("Figures saved as `figures/brysbaert_distribution.pdf`, `figures/wordnet_distribution.pdf`, `figures/per_condition_box.pdf` (PNG copies for previewing).")
    lines.append("")
    for label, blocks in distros.items():
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Cond | n | mean | SD | min | Q25 | median | Q75 | max |")
        lines.append("|------|---|------|----|-----|-----|--------|-----|-----|")
        for cond in ("NC", "MC", "VC"):
            b = blocks[cond]
            if not b:
                continue
            lines.append(f"| {cond} | {b['n']} | {b['mean']:.3f} | {b['sd']:.3f} | "
                         f"{b['min']:.3f} | {b['q25']:.3f} | {b['median']:.3f} | "
                         f"{b['q75']:.3f} | {b['max']:.3f} |")
        lines.append("")

    # A2 + A3
    lines.append("## A2/A3. Paired t-tests and effect sizes")
    lines.append("")
    lines.append("Each row is a paired comparison across the 661 records that have all three conditions. *p* < 0.05 starred; Cohen's d uses standard deviation of the paired differences.")
    lines.append("")
    for label, rows in tests.items():
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Comparison | n | mean diff | t | p | Cohen's d | Effect |")
        lines.append("|------------|---|-----------|---|---|-----------|--------|")
        for r in rows:
            p_disp = f"{r['p']:.3g}" if r['p'] is not None else "—"
            star = " *" if (r['p'] is not None and r['p'] < 0.05) else ""
            d_disp = f"{r['cohens_d']:.3f}" if r['cohens_d'] is not None else "—"
            lines.append(f"| {r['comparison']} | {r['n']} | {r['mean_diff']:+.3f} | "
                         f"{r['t']:+.3f} | {p_disp}{star} | {d_disp} | {r['effect']} |")
        lines.append("")

    # E1
    lines.append("## E1. Repeatability across regenerations")
    lines.append("")
    lines.append("Each row is a (task, model) group with 2+ runs. SD = standard deviation of the per-stimulus mean across those runs. Low SD = stable behaviour.")
    lines.append("")
    if not repeat:
        lines.append("*No (task, model) group had ≥2 regenerations in the logs.*")
    else:
        lines.append("| Task | Model | n runs | NC Brys SD | MC Brys SD | VC Brys SD | NC WN SD | MC WN SD | VC WN SD | NC wc SD | VC wc SD |")
        lines.append("|------|-------|--------|-----------|-----------|-----------|----------|----------|----------|---------|---------|")
        for r in repeat:
            def f(k):
                return f"{r[k]:.3f}" if k in r else "—"
            lines.append(f"| {r['task']} | {r['model']} | {r['n_runs']} | "
                         f"{f('nc_brysbaert_sd')} | {f('mc_brysbaert_sd')} | {f('vc_brysbaert_sd')} | "
                         f"{f('nc_wn_sd')} | {f('mc_wn_sd')} | {f('vc_wn_sd')} | "
                         f"{f('nc_wc_sd')} | {f('vc_wc_sd')} |")
    lines.append("")

    return "\n".join(lines)


def main():
    records = load_records()
    distros = a1_distributions(records)
    tests = a2a3_paired_tests(records)
    repeat = e1_repeatability(records)

    md = write_markdown(distros, tests, repeat)
    (EVAL_DIR / "tier1_results.md").write_text(md, encoding="utf-8")
    (EVAL_DIR / "tier1_results.json").write_text(json.dumps(
        {"distributions": distros, "paired_tests": tests, "repeatability": repeat},
        indent=2,
    ), encoding="utf-8")

    print(md)


if __name__ == "__main__":
    main()
