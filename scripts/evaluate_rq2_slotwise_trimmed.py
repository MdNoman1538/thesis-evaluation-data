"""
RQ2 slot-wise pairwise evaluation.

Loads the 33 .mat files produced by produce_rq2_mat.py (each one is a
paired NC vs VC analysis of one source folder's text from the
participant-facing corpus) and aggregates the per-slot data across all
33 runs.

Each .mat file contains 25 noun-phrase slot pairs (N1..N25). Across 33
runs we have 33 * 25 = 825 paired slot observations. All 33 pairs share
the locked five-sentence skeleton, so slot N_i means the same conceptual
position in every run — pooling on slot index is methodologically valid.

The primary metric is normalised WordNet hypernym depth, called
"abstraction level" (AL) in the semantic_analyzer:

    AL = 1 - (depth - 1) / 19,  scaled to [0, 1] with 1 = most abstract.

Outputs (/Users/noman/Documents/Thesis/evaluation/results/rq2/):
  rq2_slotwise_log.jsonl       — 825 paired-slot rows
  rq2_slotwise_results.md      — full tables
  rq2_slotwise_results.json    — machine-readable
  figures/                      — per-slot mean, per-task split, delta distribution
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy.io
from scipy import stats

MAT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/results/rq2/mat_files")
OUT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/results_trimmed/rq2_original_script")
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


def unwrap(x):
    if hasattr(x, "shape") and x.shape == (1, 1):
        return x[0, 0]
    if hasattr(x, "shape") and x.shape == (1,):
        return x[0]
    return x


def task_of(folder: str) -> str:
    f = folder.lower()
    if f.startswith("source_jar"): return "jar"
    if f.startswith("source_skii") or f.startswith("source_snow"): return "skii"
    return "unknown"


def load_one(p: Path) -> dict:
    """Load one .mat into a Python dict with per-slot rows."""
    d = scipy.io.loadmat(p)
    folder = str(unwrap(d["label"]))
    n_slots = int(d["avg_slot_al_a"].shape[1])
    al_a = d["avg_slot_al_a"][0]
    al_b = d["avg_slot_al_b"][0]
    wn_a = d["wn_slot_a"][0]
    wn_b = d["wn_slot_b"][0]
    phrases_a = d["phrases_a"][0]
    phrases_b = d["phrases_b"][0]
    rows = []
    for i in range(n_slots):
        a = float(al_a[i]) if not np.isnan(al_a[i]) else None
        b = float(al_b[i]) if not np.isnan(al_b[i]) else None
        delta = (a - b) if (a is not None and b is not None) else None
        rows.append({
            "folder": folder,
            "task": task_of(folder),
            "slot": i + 1,
            "phrase_nc": str(phrases_a[i][0]) if phrases_a[i].size else "",
            "phrase_vc": str(phrases_b[i][0]) if phrases_b[i].size else "",
            "al_nc": a,
            "al_vc": b,
            "delta": delta,
            "wn_depth_nc": int(wn_a[i]) if int(wn_a[i]) >= 0 else None,
            "wn_depth_vc": int(wn_b[i]) if int(wn_b[i]) >= 0 else None,
        })
    return {
        "mat_file": p.name,
        "folder": folder,
        "task": task_of(folder),
        "n_slots": n_slots,
        "ttest_t": float(unwrap(d["ttest_t"])),
        "ttest_p": float(unwrap(d["ttest_p"])),
        "ttest_mean_diff": float(unwrap(d["ttest_mean_diff"])),
        "avg_al_nc": float(unwrap(d["avg_al_a"])),
        "avg_al_vc": float(unwrap(d["avg_al_b"])),
        "rows": rows,
    }


def cohens_d_paired(diffs):
    diffs = np.array([d for d in diffs if d is not None])
    if len(diffs) < 2:
        return None
    sd = np.std(diffs, ddof=1)
    return float(np.mean(diffs) / sd) if sd > 0 else float("inf")


def effect_label(d):
    if d is None: return "—"
    a = abs(d)
    if a < 0.2: return "negligible"
    if a < 0.5: return "small"
    if a < 0.8: return "medium"
    return "large"


def main():
    EXCLUDED = ("source_Skii_9_", "source_skii_10_")
    mats = [p for p in sorted(MAT_DIR.glob("source_*.mat")) if not p.name.startswith(EXCLUDED)]
    print(f"Loading {len(mats)} source .mat files...")
    runs = [load_one(p) for p in mats]
    all_rows = [r for run in runs for r in run["rows"]]

    with (OUT_DIR / "rq2_slotwise_log.jsonl").open("w", encoding="utf-8") as fh:
        for r in all_rows:
            fh.write(json.dumps(r) + "\n")

    # ── pooled stats across all slot pairs ──────────────────────────────────
    pairs = [(r["al_nc"], r["al_vc"]) for r in all_rows
             if r["al_nc"] is not None and r["al_vc"] is not None]
    nc = np.array([p[0] for p in pairs])
    vc = np.array([p[1] for p in pairs])
    deltas = nc - vc
    t, p = stats.ttest_rel(nc, vc)
    d = cohens_d_paired(deltas)
    pos = int(np.sum(deltas > 0))
    neg = int(np.sum(deltas < 0))
    tie = int(np.sum(deltas == 0))

    pooled = {
        "n_runs": len(runs),
        "n_pairs": len(pairs),
        "nc_mean": float(np.mean(nc)),
        "nc_sd": float(np.std(nc, ddof=1)),
        "vc_mean": float(np.mean(vc)),
        "vc_sd": float(np.std(vc, ddof=1)),
        "delta_mean": float(np.mean(deltas)),
        "delta_sd": float(np.std(deltas, ddof=1)),
        "t_statistic": float(t),
        "p_value": float(p),
        "cohens_d": d,
        "effect": effect_label(d),
        "slots_NC_more_abstract": pos,
        "slots_VC_more_abstract": neg,
        "slots_tied": tie,
        "pct_NC_more_abstract": 100.0 * pos / len(pairs),
    }

    # ── per-task ────────────────────────────────────────────────────────────
    per_task = {}
    for task in ("jar", "skii"):
        sub_runs = [r for r in runs if r["task"] == task]
        sub_pairs = [(r["al_nc"], r["al_vc"]) for r in all_rows
                     if r["task"] == task and r["al_nc"] is not None and r["al_vc"] is not None]
        if not sub_pairs:
            continue
        a = np.array([x[0] for x in sub_pairs])
        b = np.array([x[1] for x in sub_pairs])
        dd = a - b
        tt, pp = stats.ttest_rel(a, b)
        ddd = cohens_d_paired(dd)
        per_task[task] = {
            "n_runs": len(sub_runs),
            "n_pairs": len(sub_pairs),
            "nc_mean": float(np.mean(a)),
            "vc_mean": float(np.mean(b)),
            "delta_mean": float(np.mean(dd)),
            "delta_sd": float(np.std(dd, ddof=1)),
            "t_statistic": float(tt),
            "p_value": float(pp),
            "cohens_d": ddd,
            "effect": effect_label(ddd),
            "pct_NC_more_abstract": 100.0 * float(np.sum(dd > 0)) / len(sub_pairs),
        }

    # ── per-slot aggregation ────────────────────────────────────────────────
    per_slot = {}
    for i in range(1, 26):
        slot_pairs = [(r["al_nc"], r["al_vc"]) for r in all_rows
                      if r["slot"] == i and r["al_nc"] is not None and r["al_vc"] is not None]
        if not slot_pairs:
            continue
        a = np.array([x[0] for x in slot_pairs])
        b = np.array([x[1] for x in slot_pairs])
        dd = a - b
        per_slot[i] = {
            "n": len(slot_pairs),
            "nc_mean": float(np.mean(a)),
            "vc_mean": float(np.mean(b)),
            "delta_mean": float(np.mean(dd)),
            "delta_sd": float(np.std(dd, ddof=1)) if len(dd) > 1 else 0.0,
            "pct_NC_more_abstract": 100.0 * float(np.sum(dd > 0)) / len(slot_pairs),
        }

    # ── per-run summary ─────────────────────────────────────────────────────
    per_run = [{
        "folder": r["folder"],
        "task": r["task"],
        "avg_al_nc": r["avg_al_nc"],
        "avg_al_vc": r["avg_al_vc"],
        "delta_mean": r["avg_al_nc"] - r["avg_al_vc"],
        "ttest_t": r["ttest_t"],
        "ttest_p": r["ttest_p"],
    } for r in runs]

    summary = {
        "pooled": pooled,
        "per_task": per_task,
        "per_slot": per_slot,
        "per_run": per_run,
    }
    (OUT_DIR / "rq2_slotwise_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # ── figures ────────────────────────────────────────────────────────────
    _fig_delta_dist(deltas, FIG_DIR / "rq2_slotwise_delta_distribution")
    _fig_per_task(all_rows, FIG_DIR / "rq2_slotwise_per_task")
    _fig_per_slot(per_slot, FIG_DIR / "rq2_slotwise_per_slot_mean")

    md = _write_md(summary, runs)
    (OUT_DIR / "rq2_slotwise_results.md").write_text(md, encoding="utf-8")
    print(md)


def _fig_delta_dist(deltas, out_stub):
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.hist(deltas, bins=40, color="#5B9BD5", alpha=0.85, edgecolor="white")
    ax.axvline(0, color="black", linewidth=1.2)
    ax.axvline(np.mean(deltas), color="#C00000", linewidth=1.5, linestyle="--",
               label=f"mean = {np.mean(deltas):+.4f}")
    ax.set_xlabel("Per-slot delta (AL_NC − AL_VC)")
    ax.set_ylabel("Number of slot pairs")
    ax.set_title(f"RQ2 — distribution of per-slot abstraction deltas "
                 f"(n = {len(deltas)} pairs from 33 source runs × 25 slots)")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_stub.with_suffix(".pdf"))
    fig.savefig(out_stub.with_suffix(".png"), dpi=160)
    plt.close(fig)


def _fig_per_task(rows, out_stub):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    data, labels, palette = [], [], []
    for task, c in [("jar", "#5B9BD5"), ("skii", "#70AD47")]:
        ds = [r["delta"] for r in rows if r["task"] == task and r["delta"] is not None]
        data.append(ds); labels.append(f"{task}\n(n = {len(ds)})"); palette.append(c)
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
    for patch, c in zip(bp["boxes"], palette):
        patch.set_facecolor(c); patch.set_alpha(0.85)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_ylabel("Per-slot delta (AL_NC − AL_VC)")
    ax.set_title("RQ2 — per-slot abstraction deltas by task")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_stub.with_suffix(".pdf"))
    fig.savefig(out_stub.with_suffix(".png"), dpi=160)
    plt.close(fig)


def _fig_per_slot(per_slot, out_stub):
    slots = sorted(per_slot.keys())
    means = [per_slot[i]["delta_mean"] for i in slots]
    sds = [per_slot[i]["delta_sd"] for i in slots]
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(slots, means, yerr=sds, color="#5B9BD5", alpha=0.85, edgecolor="white",
           ecolor="#404040", capsize=2.5)
    ax.axhline(0, color="black", linewidth=0.7)
    ax.set_xlabel("Slot number $N_i$")
    ax.set_ylabel("Mean delta (NC − VC) ± SD across 33 runs")
    ax.set_title("RQ2 — per-slot mean abstraction delta across all 33 source runs")
    ax.set_xticks(slots)
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_stub.with_suffix(".pdf"))
    fig.savefig(out_stub.with_suffix(".png"), dpi=160)
    plt.close(fig)


def _write_md(summary, runs):
    p = summary["pooled"]
    L = []
    L.append("# RQ2 — Slot-wise pairwise evaluation of the textual stimuli")
    L.append("")
    L.append(f"33 source runs × 25 noun-phrase slots per run = **{p['n_pairs']} paired slot observations**.")
    L.append("")
    L.append(f"Each source pair is one (NC, VC) text comparison from the 33-run participant-facing corpus. The locked five-sentence skeleton guarantees that slot $N_i$ in every run refers to the same conceptual noun position, so the slot index is comparable across runs. The metric is the normalised abstraction level (AL) on $[0, 1]$, with 1 = most abstract.")
    L.append("")
    L.append("## Pooled (all 825 slot pairs)")
    L.append("")
    L.append("| Statistic | Value |")
    L.append("|---|---|")
    L.append(f"| NC mean AL | {p['nc_mean']:.4f}  (SD {p['nc_sd']:.4f}) |")
    L.append(f"| VC mean AL | {p['vc_mean']:.4f}  (SD {p['vc_sd']:.4f}) |")
    L.append(f"| mean delta (NC − VC) | **{p['delta_mean']:+.4f}**  (SD {p['delta_sd']:.4f}) |")
    L.append(f"| paired t-test | t = {p['t_statistic']:+.3f},  p = {p['p_value']:.3g} |")
    L.append(f"| Cohen's d | **{p['cohens_d']:.3f}**  ({p['effect']}) |")
    L.append(f"| slots where NC > VC | {p['slots_NC_more_abstract']}  ({p['pct_NC_more_abstract']:.1f}\\%) |")
    L.append(f"| slots where NC < VC | {p['slots_VC_more_abstract']} |")
    L.append(f"| slots tied | {p['slots_tied']} |")
    L.append("")
    L.append("## Per task")
    L.append("")
    L.append("| Task | n runs | n pairs | NC mean | VC mean | delta mean | t | p | Cohen's d | Effect | NC>VC % |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for task, b in summary["per_task"].items():
        L.append(f"| {task} | {b['n_runs']} | {b['n_pairs']} | {b['nc_mean']:.4f} | "
                 f"{b['vc_mean']:.4f} | {b['delta_mean']:+.4f} | {b['t_statistic']:+.3f} | "
                 f"{b['p_value']:.3g} | {b['cohens_d']:.3f} | {b['effect']} | {b['pct_NC_more_abstract']:.1f} |")
    L.append("")
    L.append("## Per slot mean across 33 source runs")
    L.append("")
    L.append("Slots with large positive delta mean are the slots where the methodology produces the strongest abstraction shift in practice. Slots near zero are weakest.")
    L.append("")
    L.append("| Slot | n | NC mean | VC mean | delta mean | delta SD | NC>VC % |")
    L.append("|---|---|---|---|---|---|---|")
    for i in sorted(summary["per_slot"].keys()):
        s = summary["per_slot"][i]
        L.append(f"| N{i} | {s['n']} | {s['nc_mean']:.4f} | {s['vc_mean']:.4f} | "
                 f"{s['delta_mean']:+.4f} | {s['delta_sd']:.4f} | {s['pct_NC_more_abstract']:.1f} |")
    L.append("")
    L.append("## Per run (analyzer's own paired t-test on 25 slots within that run)")
    L.append("")
    L.append("| Run folder | Task | AL_NC | AL_VC | delta | t | p |")
    L.append("|---|---|---|---|---|---|---|")
    for r in summary["per_run"]:
        L.append(f"| {r['folder']} | {r['task']} | {r['avg_al_nc']:.4f} | {r['avg_al_vc']:.4f} | "
                 f"{r['delta_mean']:+.4f} | {r['ttest_t']:+.3f} | {r['ttest_p']:.3g} |")
    return "\n".join(L)


if __name__ == "__main__":
    main()