"""
Evaluate the FINAL experimental corpus (the runs in `app output data save/`).

This is distinct from `evaluate_priors.py`, which scores the 661-record
development corpus. The corpus here is the participant-facing material:
~33 runs across 2 tasks (jar; skii/snow), each containing only NC and VC
(MC is not part of the final pipeline). Each run also carries a per-folder
QC tag in its name ("passed", "2failed bci passed", "wordnetfailed", ...)
which we parse so the chapter can report production yield.

Outputs (under /Users/noman/Documents/Thesis/evaluation/results/rq1/):
  final_log.jsonl          — one record per run, scored
  final_results.md         — headline tables, ready to read
  final_results.json       — machine-readable
  figures/
    final_brysbaert_box.{pdf,png}
    final_wordnet_box.{pdf,png}
    final_per_task.{pdf,png}
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Reuse the analyzer module from the production app.
ANALYZER_DIR = Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1/semantic_analyzer")
sys.path.insert(0, str(ANALYZER_DIR))

import spacy
from nltk.corpus import wordnet as wn
from brysbaert_data import get_concreteness

NLP = spacy.load("en_core_web_sm")

CORPUS_DIR = Path("/Users/noman/Documents/Thesis/app output data save")
OUT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/results/rq1")
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ── scoring helpers (kept consistent with evaluate_priors.py) ───────────────

def wn_depth_min(word: str) -> int | None:
    syns = wn.synsets(word, pos=wn.NOUN)
    if not syns:
        return None
    depths = []
    for s in syns:
        paths = s.hypernym_paths()
        if paths:
            depths.append(min(len(p) for p in paths))
    return min(depths) if depths else None


def extract_nouns(text: str) -> list[str]:
    doc = NLP(text or "")
    return [tok.lemma_.lower() for tok in doc if tok.pos_ in ("NOUN", "PROPN")]


def metrics_for(text: str) -> dict:
    if not text or not text.strip():
        return {"present": False}
    doc = NLP(text)
    sents = [s.text.strip() for s in doc.sents if s.text.strip()]
    words = [tok for tok in doc if tok.is_alpha]
    nouns = extract_nouns(text)
    bry = [get_concreteness(n) for n in nouns]
    wnd = [wn_depth_min(n) for n in nouns]
    bry = [b for b in bry if b is not None]
    wnd = [w for w in wnd if w is not None]
    return {
        "present": True,
        "word_count": len(words),
        "sentence_count": len(sents),
        "noun_count": len(nouns),
        "brysbaert_mean": statistics.fmean(bry) if bry else None,
        "wordnet_depth_mean": statistics.fmean(wnd) if wnd else None,
        "sentences": sents,
    }


# ── corpus discovery ────────────────────────────────────────────────────────

def parse_folder_tag(name: str) -> dict:
    """Pull task, run number, and QC labels from the folder name."""
    n = name.lower()
    if n.startswith("jar"):
        task = "jar"
    elif n.startswith("skii") or n.startswith("ski "):
        task = "skii"
    elif n.startswith("snow"):
        task = "skii"  # user: snow + skii are the same task
    else:
        task = "unknown"

    m = re.search(r"\b(\d+)\b", name)
    run_no = int(m.group(1)) if m else None

    flags = {
        "passed": "passed" in n and "fail" not in n.split("passed")[0],
        "bci_failed": "bci" in n and "fail" in n,
        "wordnet_failed": "wordnet" in n and "fail" in n,
        "bad_image": "bad image" in n,
        "bad_text": re.search(r"\bbad\b(?! image)", n) is not None,
    }
    # "passed" cleanly = no failure markers anywhere
    flags["clean_pass"] = (
        not flags["bci_failed"]
        and not flags["wordnet_failed"]
        and not flags["bad_image"]
        and not flags["bad_text"]
    )
    return {"task": task, "run_no": run_no, "raw_tag": name, **flags}


def load_run(folder: Path) -> dict | None:
    meta_path = folder / "metadata.json"
    if not meta_path.exists():
        return None
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    nc_text = (meta.get("nc") or {}).get("stimulus") or ""
    vc_text = (meta.get("vc") or {}).get("stimulus") or ""
    nc_imgs = (meta.get("nc") or {}).get("images") or []
    vc_imgs = (meta.get("vc") or {}).get("images") or []
    return {
        "folder": folder.name,
        **parse_folder_tag(folder.name),
        "task_description": meta.get("task", ""),
        "nc_text": nc_text,
        "vc_text": vc_text,
        "nc_image_count": len(nc_imgs),
        "vc_image_count": len(vc_imgs),
        "nc": metrics_for(nc_text),
        "vc": metrics_for(vc_text),
    }


# ── analyses ────────────────────────────────────────────────────────────────

def cohens_d_paired(x, y):
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


def per_run_summary(records):
    """Per-run table: task, run, QC, n_words, brys NC/VC, wn NC/VC, ordering."""
    rows = []
    for r in records:
        nc = r["nc"]
        vc = r["vc"]
        if not (nc.get("present") and vc.get("present")):
            continue
        spread = abs(nc["word_count"] - vc["word_count"])
        brys_ok = (nc["brysbaert_mean"] is not None
                   and vc["brysbaert_mean"] is not None
                   and nc["brysbaert_mean"] < vc["brysbaert_mean"])
        wn_ok = (nc["wordnet_depth_mean"] is not None
                 and vc["wordnet_depth_mean"] is not None
                 and nc["wordnet_depth_mean"] < vc["wordnet_depth_mean"])
        rows.append({
            "task": r["task"],
            "run_no": r["run_no"],
            "folder": r["folder"],
            "clean_pass": r["clean_pass"],
            "nc_words": nc["word_count"],
            "vc_words": vc["word_count"],
            "word_spread": spread,
            "rule8_ok": spread <= 2,
            "nc_sents": nc["sentence_count"],
            "vc_sents": vc["sentence_count"],
            "five_sent_ok": nc["sentence_count"] == 5 and vc["sentence_count"] == 5,
            "nc_brys": nc["brysbaert_mean"],
            "vc_brys": vc["brysbaert_mean"],
            "brys_order_ok": brys_ok,
            "nc_wn": nc["wordnet_depth_mean"],
            "vc_wn": vc["wordnet_depth_mean"],
            "wn_order_ok": wn_ok,
            "nc_imgs": r["nc_image_count"],
            "vc_imgs": r["vc_image_count"],
            "five_imgs_ok": r["nc_image_count"] == 5 and r["vc_image_count"] == 5,
        })
    return rows


def headline_block(rows):
    n = len(rows)
    if n == 0:
        return {}

    def pct(key):
        return 100.0 * sum(1 for r in rows if r[key]) / n

    nc_brys = [r["nc_brys"] for r in rows if r["nc_brys"] is not None]
    vc_brys = [r["vc_brys"] for r in rows if r["vc_brys"] is not None]
    nc_wn = [r["nc_wn"] for r in rows if r["nc_wn"] is not None]
    vc_wn = [r["vc_wn"] for r in rows if r["vc_wn"] is not None]

    paired_brys = [(r["nc_brys"], r["vc_brys"]) for r in rows
                   if r["nc_brys"] is not None and r["vc_brys"] is not None]
    paired_wn = [(r["nc_wn"], r["vc_wn"]) for r in rows
                 if r["nc_wn"] is not None and r["vc_wn"] is not None]

    def paired_test(pairs):
        if len(pairs) < 2:
            return None
        a = [p[0] for p in pairs]
        b = [p[1] for p in pairs]
        t, p = stats.ttest_rel(a, b)
        d = cohens_d_paired(a, b)
        return {"n": len(pairs), "t": float(t), "p": float(p),
                "cohens_d": d, "effect": effect_label(d),
                "mean_diff_vc_minus_nc": statistics.fmean([y - x for x, y in pairs])}

    return {
        "n_runs": n,
        "five_sentence_pass_pct": pct("five_sent_ok"),
        "five_image_pass_pct": pct("five_imgs_ok"),
        "rule8_pass_pct": pct("rule8_ok"),
        "brys_order_pass_pct": pct("brys_order_ok"),
        "wn_order_pass_pct": pct("wn_order_ok"),
        "clean_pass_pct": pct("clean_pass"),
        "nc_brys_mean": statistics.fmean(nc_brys) if nc_brys else None,
        "vc_brys_mean": statistics.fmean(vc_brys) if vc_brys else None,
        "nc_wn_mean": statistics.fmean(nc_wn) if nc_wn else None,
        "vc_wn_mean": statistics.fmean(vc_wn) if vc_wn else None,
        "brys_paired_test": paired_test(paired_brys),
        "wn_paired_test": paired_test(paired_wn),
    }


def per_task_block(rows):
    out = {}
    by_task = defaultdict(list)
    for r in rows:
        by_task[r["task"]].append(r)
    for task, sub in by_task.items():
        out[task] = headline_block(sub)
    return out


# ── figures ─────────────────────────────────────────────────────────────────

def make_figures(rows):
    nc_brys = [r["nc_brys"] for r in rows if r["nc_brys"] is not None]
    vc_brys = [r["vc_brys"] for r in rows if r["vc_brys"] is not None]
    nc_wn = [r["nc_wn"] for r in rows if r["nc_wn"] is not None]
    vc_wn = [r["vc_wn"] for r in rows if r["vc_wn"] is not None]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    bp1 = axes[0].boxplot([nc_brys, vc_brys], tick_labels=["NC", "VC"],
                          patch_artist=True, widths=0.55)
    for patch, c in zip(bp1["boxes"], ["#5B9BD5", "#70AD47"]):
        patch.set_facecolor(c); patch.set_alpha(0.8)
    axes[0].set_title(f"Brysbaert concreteness  (n={len(nc_brys)} runs)")
    axes[0].set_ylabel("Mean per stimulus (1–5)")
    axes[0].spines["top"].set_visible(False); axes[0].spines["right"].set_visible(False)

    bp2 = axes[1].boxplot([nc_wn, vc_wn], tick_labels=["NC", "VC"],
                          patch_artist=True, widths=0.55)
    for patch, c in zip(bp2["boxes"], ["#5B9BD5", "#70AD47"]):
        patch.set_facecolor(c); patch.set_alpha(0.8)
    axes[1].set_title(f"WordNet hypernym depth  (n={len(nc_wn)} runs)")
    axes[1].set_ylabel("Mean per stimulus")
    axes[1].spines["top"].set_visible(False); axes[1].spines["right"].set_visible(False)

    fig.suptitle(f"Final experimental corpus (n={len(rows)} runs, NC vs VC)", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "final_brysbaert_wordnet_box.pdf")
    fig.savefig(FIG_DIR / "final_brysbaert_wordnet_box.png", dpi=160)
    plt.close(fig)

    # Per-task split
    by_task = defaultdict(list)
    for r in rows:
        by_task[r["task"]].append(r)
    if len(by_task) >= 2:
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        labels = []
        data = []
        colors = []
        palette = {"jar": ("#5B9BD5", "#70AD47"), "skii": ("#9DC3E6", "#A9D18E")}
        for task in sorted(by_task):
            nc = [r["nc_brys"] for r in by_task[task] if r["nc_brys"] is not None]
            vc = [r["vc_brys"] for r in by_task[task] if r["vc_brys"] is not None]
            data.extend([nc, vc])
            labels.extend([f"{task}\nNC", f"{task}\nVC"])
            colors.extend(list(palette.get(task, ("#888", "#bbb"))))
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c); patch.set_alpha(0.85)
        ax.set_ylabel("Brysbaert mean (1–5)")
        ax.set_title("Per-task NC vs VC concreteness — final corpus")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "final_per_task.pdf")
        fig.savefig(FIG_DIR / "final_per_task.png", dpi=160)
        plt.close(fig)


# ── reporting ───────────────────────────────────────────────────────────────

def write_markdown(rows, headline, per_task):
    lines = []
    lines.append("# Final Corpus Evaluation — Participant-Facing Stimuli")
    lines.append("")
    lines.append(f"Source: `{CORPUS_DIR}`")
    lines.append(f"Runs scored: **{len(rows)}** across {len(per_task)} task(s).")
    lines.append("")
    lines.append("Each run contains only NC and VC stimuli (the production pipeline does"
                 " not persist MC). All runs were generated by `gemini-3.1-pro-preview`"
                 " under the post–Rule-8, 5-sentence FBS regime.")
    lines.append("")
    lines.append("**Primary metric: WordNet hypernym depth.** Brysbaert concreteness is reported below as a secondary, complementary measure; see `feedback_wordnet_primary.md` in memory for the methodological rationale.")
    lines.append("")

    lines.append("## Headline pass rates")
    lines.append("")
    lines.append("| Check | Pass rate |")
    lines.append("|---|---|")
    lines.append(f"| Five-sentence structure (NC and VC both = 5 sents) | {headline['five_sentence_pass_pct']:.1f}% |")
    lines.append(f"| Five sentence-aligned images per condition | {headline['five_image_pass_pct']:.1f}% |")
    lines.append(f"| Rule 8 word-count parity (|NC−VC| ≤ 2) | {headline['rule8_pass_pct']:.1f}% |")
    lines.append(f"| **WordNet ordering (NC < VC) — primary** | **{headline['wn_order_pass_pct']:.1f}%** |")
    lines.append(f"| Brysbaert ordering (NC < VC) — secondary | {headline['brys_order_pass_pct']:.1f}% |")
    lines.append(f"| Clean pass (no QC flag in folder name) | {headline['clean_pass_pct']:.1f}% |")
    lines.append("")

    lines.append("## Means and paired tests (NC vs VC) — WordNet primary")
    lines.append("")
    lines.append("### WordNet hypernym depth (primary metric)")
    lines.append("")
    lines.append("| Metric | NC mean | VC mean | mean diff | t | p | Cohen's d | Effect |")
    lines.append("|---|---|---|---|---|---|---|---|")
    t = headline.get("wn_paired_test")
    if t:
        lines.append(f"| WordNet depth | {headline['nc_wn_mean']:.3f} | {headline['vc_wn_mean']:.3f} | "
                     f"{t['mean_diff_vc_minus_nc']:+.3f} | {t['t']:+.3f} | {t['p']:.3g} | "
                     f"{t['cohens_d']:.3f} | {t['effect']} |")
    lines.append("")

    lines.append("### Brysbaert concreteness (1–5) — secondary metric")
    lines.append("")
    lines.append("| Metric | NC mean | VC mean | mean diff | t | p | Cohen's d | Effect |")
    lines.append("|---|---|---|---|---|---|---|---|")
    t = headline.get("brys_paired_test")
    if t:
        lines.append(f"| Brysbaert (1–5) | {headline['nc_brys_mean']:.3f} | {headline['vc_brys_mean']:.3f} | "
                     f"{t['mean_diff_vc_minus_nc']:+.3f} | {t['t']:+.3f} | {t['p']:.3g} | "
                     f"{t['cohens_d']:.3f} | {t['effect']} |")
    lines.append("")

    lines.append("## Per-task breakdown")
    lines.append("")
    lines.append("WordNet first (primary), then Brysbaert below.")
    lines.append("")
    lines.append("### WordNet")
    lines.append("")
    lines.append("| Task | n | WN NC | WN VC | WN d | WN order % | Rule 8 % |")
    lines.append("|---|---|---|---|---|---|---|")
    for task in sorted(per_task):
        b = per_task[task]
        wd = (b["wn_paired_test"] or {}).get("cohens_d")
        lines.append(f"| {task} | {b['n_runs']} | "
                     f"{b['nc_wn_mean']:.3f} | {b['vc_wn_mean']:.3f} | "
                     f"{wd:.3f} | "
                     f"{b['wn_order_pass_pct']:.1f} | {b['rule8_pass_pct']:.1f} |")
    lines.append("")
    lines.append("### Brysbaert (secondary)")
    lines.append("")
    lines.append("| Task | n | Brys NC | Brys VC | Brys d | Brys order % |")
    lines.append("|---|---|---|---|---|---|")
    for task in sorted(per_task):
        b = per_task[task]
        bd = (b["brys_paired_test"] or {}).get("cohens_d")
        lines.append(f"| {task} | {b['n_runs']} | "
                     f"{b['nc_brys_mean']:.3f} | {b['vc_brys_mean']:.3f} | "
                     f"{bd:.3f} | "
                     f"{b['brys_order_pass_pct']:.1f} |")
    lines.append("")

    lines.append("## Per-run table")
    lines.append("")
    lines.append("| Folder | Task | Clean | 5-sent | 5-img | Spread | Rule8 | NC Brys | VC Brys | Brys< | NC WN | VC WN | WN< |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: (x["task"], x["run_no"] or 0)):
        def yn(v): return "✓" if v else "✗"
        lines.append(
            f"| {r['folder']} | {r['task']} | {yn(r['clean_pass'])} | "
            f"{yn(r['five_sent_ok'])} | {yn(r['five_imgs_ok'])} | "
            f"{r['word_spread']} | {yn(r['rule8_ok'])} | "
            f"{(r['nc_brys'] or 0):.3f} | {(r['vc_brys'] or 0):.3f} | {yn(r['brys_order_ok'])} | "
            f"{(r['nc_wn'] or 0):.3f} | {(r['vc_wn'] or 0):.3f} | {yn(r['wn_order_ok'])} |"
        )
    lines.append("")
    return "\n".join(lines)


# ── main ────────────────────────────────────────────────────────────────────

def main():
    folders = [p for p in CORPUS_DIR.iterdir() if p.is_dir()]
    records = []
    for f in sorted(folders):
        rec = load_run(f)
        if rec:
            records.append(rec)

    # Persist raw scored records
    with (OUT_DIR / "final_log.jsonl").open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")

    rows = per_run_summary(records)
    headline = headline_block(rows)
    per_task = per_task_block(rows)

    make_figures(rows)
    md = write_markdown(rows, headline, per_task)
    (OUT_DIR / "final_results.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "final_results.json").write_text(
        json.dumps({"headline": headline, "per_task": per_task, "rows": rows}, indent=2),
        encoding="utf-8",
    )
    print(md)


if __name__ == "__main__":
    main()
