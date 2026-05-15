"""
Evaluate the image-to-text (i2t) round-trip stimuli against:

Analysis A
  - 60 i2t stimuli (30 NC + 30 VC) vs. the 66 final-corpus text stimuli
    (33 NC + 33 VC) from `app output data save/`.

Analysis B
  - For each of the 3 source folders (jar 13, jar 7, skii 5), compare the
    10 i2t-NC and 10 i2t-VC stimuli derived from that source's images
    against the source's own original NC and VC text stimuli.

Inputs:
  uploaded_images/session_*/descriptions.txt    (30 sessions, 10 lines each)
  uploaded_images/session_*/s1..s10.png         (used to identify source via MD5)
  app output data save/*/{nc,vc}/stimulus.txt   (66 final-corpus text stimuli)

Outputs (/Users/noman/Documents/Thesis/evaluation/results/rq3/):
  i2t_log.jsonl                — per-session scored records
  i2t_results.{md,json}        — full tables for both analyses
  figures/
    i2t_vs_corpus_brys.{pdf,png}
    i2t_vs_corpus_wn.{pdf,png}
    i2t_vs_source_per_folder.{pdf,png}
"""
from __future__ import annotations

import hashlib
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

ANALYZER_DIR = Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1/semantic_analyzer")
sys.path.insert(0, str(ANALYZER_DIR))

import spacy
from nltk.corpus import wordnet as wn
from brysbaert_data import get_concreteness

NLP = spacy.load("en_core_web_sm")

CORPUS_DIR = Path("/Users/noman/Documents/Thesis/app output data save")
SESSIONS_DIR = Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1/uploaded_images")
OUT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/results/rq3")
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ── scoring helpers (kept consistent with evaluate_final.py) ────────────────

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
    bry = [b for b in (get_concreteness(n) for n in nouns) if b is not None]
    wnd = [w for w in (wn_depth_min(n) for n in nouns) if w is not None]
    return {
        "present": True,
        "word_count": len(words),
        "sentence_count": len(sents),
        "noun_count": len(nouns),
        "brysbaert_mean": statistics.fmean(bry) if bry else None,
        "wordnet_depth_mean": statistics.fmean(wnd) if wnd else None,
    }


# ── source-folder identification via image hash ─────────────────────────────

def build_source_hash_map() -> dict[str, str]:
    """MD5 hash -> 'runfolder/cond/filename' for every image in the corpus."""
    out = {}
    for run_dir in sorted(CORPUS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        for cond in ("nc", "vc"):
            cdir = run_dir / cond
            if not cdir.is_dir():
                continue
            for img in cdir.glob("*.png"):
                h = hashlib.md5(img.read_bytes()).hexdigest()
                out[h] = f"{run_dir.name}/{cond}/{img.name}"
    return out


def identify_session_source(sess_dir: Path, src_map: dict[str, str]) -> str | None:
    """Return the source folder name for a session, by hashing s1.png."""
    s1 = sess_dir / "s1.png"
    if not s1.exists():
        return None
    h = hashlib.md5(s1.read_bytes()).hexdigest()
    src = src_map.get(h)
    return src.split("/")[0] if src else None


# ── parse descriptions ──────────────────────────────────────────────────────

DESC_LINE_RE = re.compile(r"^s(\d+):\s*(.+)$", re.IGNORECASE)


def read_descriptions(sess_dir: Path) -> dict[int, str]:
    """Return {position_index: description_text}."""
    f = sess_dir / "descriptions.txt"
    if not f.exists():
        return {}
    out = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        m = DESC_LINE_RE.match(line.strip())
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out


def assemble_stimuli(descs: dict[int, str]) -> tuple[str, str]:
    """Upload order is interleaved: s1=NC S1, s2=VC S1, s3=NC S2, s4=VC S2, ...
    So odd slots (1, 3, 5, 7, 9) are the NC sequence and even slots
    (2, 4, 6, 8, 10) are the VC sequence."""
    nc = " ".join(descs.get(i, "") for i in (1, 3, 5, 7, 9)).strip()
    vc = " ".join(descs.get(i, "") for i in (2, 4, 6, 8, 10)).strip()
    return nc, vc


# ── corpus loading ──────────────────────────────────────────────────────────

def load_corpus_stimuli() -> dict[str, dict[str, str]]:
    """Returns {run_folder: {'nc': text, 'vc': text}} for every run."""
    out = {}
    for run_dir in sorted(CORPUS_DIR.iterdir()):
        if not run_dir.is_dir():
            continue
        meta = run_dir / "metadata.json"
        if not meta.exists():
            continue
        m = json.loads(meta.read_text(encoding="utf-8"))
        nc = (m.get("nc") or {}).get("stimulus") or ""
        vc = (m.get("vc") or {}).get("stimulus") or ""
        out[run_dir.name] = {"nc": nc, "vc": vc}
    return out


# ── stats helpers ───────────────────────────────────────────────────────────

def cohens_d_independent(x, y):
    if len(x) < 2 or len(y) < 2:
        return None
    sd_pooled = np.sqrt((np.var(x, ddof=1) + np.var(y, ddof=1)) / 2)
    if sd_pooled == 0:
        return float("inf")
    return float((np.mean(x) - np.mean(y)) / sd_pooled)


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


def desc_stats(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"n": 0}
    return {
        "n": len(xs),
        "mean": float(np.mean(xs)),
        "sd": float(np.std(xs, ddof=1)) if len(xs) >= 2 else 0.0,
        "min": float(np.min(xs)),
        "max": float(np.max(xs)),
    }


# ── main ────────────────────────────────────────────────────────────────────

def main():
    print("Building source-image hash map...")
    src_map = build_source_hash_map()
    print(f"  {len(src_map)} corpus images indexed")

    print("Loading corpus text stimuli...")
    corpus = load_corpus_stimuli()
    print(f"  {len(corpus)} runs loaded")

    # Score every corpus stimulus (NC and VC). Cache by run_folder.
    print("Scoring corpus stimuli...")
    corpus_scores = {}
    for run, texts in corpus.items():
        corpus_scores[run] = {
            "nc": metrics_for(texts["nc"]),
            "vc": metrics_for(texts["vc"]),
        }
    print(f"  scored {len(corpus_scores)} runs (66 stimuli)")

    print("Processing 30 i2t sessions...")
    i2t_records = []
    for sess in sorted(SESSIONS_DIR.iterdir()):
        if not sess.is_dir():
            continue
        src = identify_session_source(sess, src_map)
        descs = read_descriptions(sess)
        if not descs:
            continue
        nc_text, vc_text = assemble_stimuli(descs)
        nc_m = metrics_for(nc_text)
        vc_m = metrics_for(vc_text)
        i2t_records.append({
            "session": sess.name,
            "source_folder": src,
            "nc_text": nc_text,
            "vc_text": vc_text,
            "nc": nc_m,
            "vc": vc_m,
        })
    print(f"  {len(i2t_records)} sessions scored")

    # Persist per-session log
    with (OUT_DIR / "i2t_log.jsonl").open("w", encoding="utf-8") as fh:
        for r in i2t_records:
            fh.write(json.dumps(r) + "\n")

    # ── Analysis A: i2t vs. full corpus ────────────────────────────────────
    print("\n=== Analysis A: i2t vs full corpus ===")
    i2t_nc_brys = [r["nc"]["brysbaert_mean"] for r in i2t_records if r["nc"].get("brysbaert_mean") is not None]
    i2t_vc_brys = [r["vc"]["brysbaert_mean"] for r in i2t_records if r["vc"].get("brysbaert_mean") is not None]
    i2t_nc_wn = [r["nc"]["wordnet_depth_mean"] for r in i2t_records if r["nc"].get("wordnet_depth_mean") is not None]
    i2t_vc_wn = [r["vc"]["wordnet_depth_mean"] for r in i2t_records if r["vc"].get("wordnet_depth_mean") is not None]

    corpus_nc_brys = [s["nc"].get("brysbaert_mean") for s in corpus_scores.values()]
    corpus_vc_brys = [s["vc"].get("brysbaert_mean") for s in corpus_scores.values()]
    corpus_nc_wn = [s["nc"].get("wordnet_depth_mean") for s in corpus_scores.values()]
    corpus_vc_wn = [s["vc"].get("wordnet_depth_mean") for s in corpus_scores.values()]
    corpus_nc_brys = [x for x in corpus_nc_brys if x is not None]
    corpus_vc_brys = [x for x in corpus_vc_brys if x is not None]
    corpus_nc_wn = [x for x in corpus_nc_wn if x is not None]
    corpus_vc_wn = [x for x in corpus_vc_wn if x is not None]

    analysis_a = {
        "brysbaert": {
            "i2t_nc": desc_stats(i2t_nc_brys),
            "i2t_vc": desc_stats(i2t_vc_brys),
            "corpus_nc": desc_stats(corpus_nc_brys),
            "corpus_vc": desc_stats(corpus_vc_brys),
            "nc_vs_nc_indep_t": _indep_test(i2t_nc_brys, corpus_nc_brys),
            "vc_vs_vc_indep_t": _indep_test(i2t_vc_brys, corpus_vc_brys),
            "i2t_nc_vs_vc_paired": _paired_test(
                [r["nc"].get("brysbaert_mean") for r in i2t_records],
                [r["vc"].get("brysbaert_mean") for r in i2t_records],
            ),
        },
        "wordnet": {
            "i2t_nc": desc_stats(i2t_nc_wn),
            "i2t_vc": desc_stats(i2t_vc_wn),
            "corpus_nc": desc_stats(corpus_nc_wn),
            "corpus_vc": desc_stats(corpus_vc_wn),
            "nc_vs_nc_indep_t": _indep_test(i2t_nc_wn, corpus_nc_wn),
            "vc_vs_vc_indep_t": _indep_test(i2t_vc_wn, corpus_vc_wn),
            "i2t_nc_vs_vc_paired": _paired_test(
                [r["nc"].get("wordnet_depth_mean") for r in i2t_records],
                [r["vc"].get("wordnet_depth_mean") for r in i2t_records],
            ),
        },
    }

    # ── Analysis B: per-source comparison ──────────────────────────────────
    print("=== Analysis B: i2t per-source vs source text ===")
    by_source = defaultdict(list)
    for r in i2t_records:
        if r["source_folder"]:
            by_source[r["source_folder"]].append(r)

    analysis_b = {}
    for src, rows in by_source.items():
        source_scores = corpus_scores.get(src, {})
        i2t_nc_b = [r["nc"]["brysbaert_mean"] for r in rows if r["nc"].get("brysbaert_mean") is not None]
        i2t_vc_b = [r["vc"]["brysbaert_mean"] for r in rows if r["vc"].get("brysbaert_mean") is not None]
        i2t_nc_w = [r["nc"]["wordnet_depth_mean"] for r in rows if r["nc"].get("wordnet_depth_mean") is not None]
        i2t_vc_w = [r["vc"]["wordnet_depth_mean"] for r in rows if r["vc"].get("wordnet_depth_mean") is not None]
        analysis_b[src] = {
            "n_sessions": len(rows),
            "source_nc": {
                "brysbaert": source_scores.get("nc", {}).get("brysbaert_mean"),
                "wordnet": source_scores.get("nc", {}).get("wordnet_depth_mean"),
                "word_count": source_scores.get("nc", {}).get("word_count"),
            },
            "source_vc": {
                "brysbaert": source_scores.get("vc", {}).get("brysbaert_mean"),
                "wordnet": source_scores.get("vc", {}).get("wordnet_depth_mean"),
                "word_count": source_scores.get("vc", {}).get("word_count"),
            },
            "i2t_nc_brys": desc_stats(i2t_nc_b),
            "i2t_vc_brys": desc_stats(i2t_vc_b),
            "i2t_nc_wn": desc_stats(i2t_nc_w),
            "i2t_vc_wn": desc_stats(i2t_vc_w),
            "i2t_nc_word_count": desc_stats([r["nc"].get("word_count") for r in rows]),
            "i2t_vc_word_count": desc_stats([r["vc"].get("word_count") for r in rows]),
            "ordering_nc_lt_vc_pct": 100.0 * sum(
                1 for r in rows
                if (r["nc"].get("brysbaert_mean") is not None
                    and r["vc"].get("brysbaert_mean") is not None
                    and r["nc"]["brysbaert_mean"] < r["vc"]["brysbaert_mean"])
            ) / len(rows),
        }

    # ── figures ────────────────────────────────────────────────────────────
    print("Generating figures...")
    _fig_corpus_compare(i2t_nc_brys, i2t_vc_brys, corpus_nc_brys, corpus_vc_brys,
                        "Brysbaert concreteness (1–5)", FIG_DIR / "i2t_vs_corpus_brys")
    _fig_corpus_compare(i2t_nc_wn, i2t_vc_wn, corpus_nc_wn, corpus_vc_wn,
                        "WordNet hypernym depth", FIG_DIR / "i2t_vs_corpus_wn")
    _fig_per_source(by_source, corpus_scores, FIG_DIR / "i2t_vs_source_per_folder")

    # ── report ─────────────────────────────────────────────────────────────
    md = _write_markdown(analysis_a, analysis_b, i2t_records)
    (OUT_DIR / "i2t_results.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "i2t_results.json").write_text(
        json.dumps({"analysis_a": analysis_a, "analysis_b": analysis_b}, indent=2),
        encoding="utf-8",
    )
    print(md)


def _indep_test(x, y):
    x = [v for v in x if v is not None]
    y = [v for v in y if v is not None]
    if len(x) < 2 or len(y) < 2:
        return None
    t, p = stats.ttest_ind(x, y, equal_var=False)
    d = cohens_d_independent(x, y)
    return {"n_x": len(x), "n_y": len(y), "t": float(t), "p": float(p),
            "cohens_d": d, "effect": effect_label(d),
            "mean_diff": float(np.mean(x) - np.mean(y))}


def _paired_test(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    if len(pairs) < 2:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    t, p = stats.ttest_rel(xs, ys)
    d = cohens_d_paired(xs, ys)
    return {"n": len(pairs), "t": float(t), "p": float(p),
            "cohens_d": d, "effect": effect_label(d),
            "mean_diff_vc_minus_nc": float(np.mean(ys) - np.mean(xs))}


def _fig_corpus_compare(i2t_nc, i2t_vc, corp_nc, corp_vc, ylabel, out_stub):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    data = [corp_nc, i2t_nc, corp_vc, i2t_vc]
    labels = [f"corpus-NC\n(n={len(corp_nc)})", f"i2t-NC\n(n={len(i2t_nc)})",
              f"corpus-VC\n(n={len(corp_vc)})", f"i2t-VC\n(n={len(i2t_vc)})"]
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
    palette = ["#5B9BD5", "#9DC3E6", "#70AD47", "#A9D18E"]
    for patch, c in zip(bp["boxes"], palette):
        patch.set_facecolor(c); patch.set_alpha(0.85)
    ax.set_ylabel(ylabel)
    ax.set_title(f"i2t derived stimuli vs full corpus  —  {ylabel}")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_stub.with_suffix(".pdf"))
    fig.savefig(out_stub.with_suffix(".png"), dpi=160)
    plt.close(fig)


def _fig_per_source(by_source, corpus_scores, out_stub):
    sources = sorted(by_source.keys())
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    for ax, metric, title in [
        (axes[0], "brysbaert_mean", "Brysbaert concreteness (1–5)"),
        (axes[1], "wordnet_depth_mean", "WordNet hypernym depth"),
    ]:
        data, labels, colors = [], [], []
        for src in sources:
            rows = by_source[src]
            src_nc = corpus_scores.get(src, {}).get("nc", {}).get(metric)
            src_vc = corpus_scores.get(src, {}).get("vc", {}).get(metric)
            i2t_nc = [r["nc"].get(metric) for r in rows if r["nc"].get(metric) is not None]
            i2t_vc = [r["vc"].get(metric) for r in rows if r["vc"].get(metric) is not None]
            data.extend([i2t_nc, i2t_vc])
            short = src.split()[0] + " " + src.split()[1] if " " in src else src
            labels.extend([f"{short}\ni2t-NC", f"{short}\ni2t-VC"])
            colors.extend(["#5B9BD5", "#70AD47"])
            if src_nc is not None:
                ax.scatter([len(data) - 1], [src_nc], marker="D", color="#1F4E79", s=60, zorder=3)
            if src_vc is not None:
                ax.scatter([len(data)], [src_vc], marker="D", color="#385723", s=60, zorder=3)
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
        for patch, c in zip(bp["boxes"], colors):
            patch.set_facecolor(c); patch.set_alpha(0.7)
        ax.set_title(title)
        ax.set_ylabel("mean")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    fig.suptitle("Per-source i2t recovery — diamonds mark the original source text values", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_stub.with_suffix(".pdf"))
    fig.savefig(out_stub.with_suffix(".png"), dpi=160)
    plt.close(fig)


def _write_markdown(a, b, recs):
    lines = []
    lines.append("# Image-to-Text (i2t) Round-Trip Evaluation")
    lines.append("")
    lines.append(f"Sessions: **{len(recs)}** · derived stimuli: **{len(recs)*2}** (NC + VC per session)")
    lines.append("")
    lines.append("**Primary metric: WordNet hypernym depth.** Brysbaert concreteness is reported below for completeness but is not the headline metric — image descriptions are uniformly concrete-vocabulary, so Brysbaert collapses while WordNet preserves the hierarchical-specificity signal.")
    lines.append("")

    lines.append("## Analysis A — i2t derived stimuli vs full corpus (n=33 runs)")
    lines.append("")
    for label, key in [("WordNet hypernym depth (primary)", "wordnet"),
                       ("Brysbaert concreteness (1–5) — secondary", "brysbaert")]:
        ax = a[key]
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Group | n | mean | SD | min | max |")
        lines.append("|---|---|---|---|---|---|")
        for grp, key2 in [("corpus NC", "corpus_nc"), ("i2t NC", "i2t_nc"),
                          ("corpus VC", "corpus_vc"), ("i2t VC", "i2t_vc")]:
            d = ax[key2]
            if d["n"] == 0:
                continue
            lines.append(f"| {grp} | {d['n']} | {d['mean']:.3f} | {d['sd']:.3f} | {d['min']:.3f} | {d['max']:.3f} |")
        lines.append("")
        t1 = ax["nc_vs_nc_indep_t"]
        t2 = ax["vc_vs_vc_indep_t"]
        tp = ax["i2t_nc_vs_vc_paired"]
        lines.append("**Independent t-tests (i2t vs corpus):**")
        if t1:
            lines.append(f"- NC: t={t1['t']:+.3f}, p={t1['p']:.3g}, mean diff (i2t–corpus)={t1['mean_diff']:+.3f}, d={t1['cohens_d']:.3f} ({t1['effect']})")
        if t2:
            lines.append(f"- VC: t={t2['t']:+.3f}, p={t2['p']:.3g}, mean diff (i2t–corpus)={t2['mean_diff']:+.3f}, d={t2['cohens_d']:.3f} ({t2['effect']})")
        if tp:
            lines.append("")
            lines.append("**Paired i2t NC vs i2t VC (within-session abstraction separation):**")
            lines.append(f"- t={tp['t']:+.3f}, p={tp['p']:.3g}, mean diff (VC–NC)={tp['mean_diff_vc_minus_nc']:+.3f}, d={tp['cohens_d']:.3f} ({tp['effect']})")
        lines.append("")

    lines.append("## Analysis B — per-source recovery")
    lines.append("")
    lines.append("For each source folder: 10 i2t sessions were derived from that source's 10 images.")
    lines.append("Comparison: i2t-derived NC/VC stimuli (n=10) vs the source's original NC/VC text.")
    lines.append("")
    lines.append("| Source | n | metric | source text | i2t mean ± SD | drift (i2t mean − source) | order NC<VC pass |")
    lines.append("|---|---|---|---|---|---|---|")
    for src in sorted(b.keys()):
        d = b[src]
        for cond, key_b, key_w, src_key in [
            ("NC", "i2t_nc_brys", "i2t_nc_wn", "source_nc"),
            ("VC", "i2t_vc_brys", "i2t_vc_wn", "source_vc"),
        ]:
            sb = d[key_b]; sw = d[key_w]
            src_b = d[src_key]["brysbaert"]
            src_w = d[src_key]["wordnet"]
            if sb["n"]:
                lines.append(f"| {src} | {d['n_sessions']} | Brys {cond} | {src_b:.3f} | {sb['mean']:.3f} ± {sb['sd']:.3f} | {sb['mean']-src_b:+.3f} | {d['ordering_nc_lt_vc_pct']:.0f}% |")
            if sw["n"]:
                lines.append(f"| {src} | {d['n_sessions']} | WN {cond} | {src_w:.3f} | {sw['mean']:.3f} ± {sw['sd']:.3f} | {sw['mean']-src_w:+.3f} | — |")
    lines.append("")

    lines.append("## Word count drift (for reference)")
    lines.append("")
    lines.append("| Source | source NC words | i2t NC words mean ± SD | source VC words | i2t VC words mean ± SD |")
    lines.append("|---|---|---|---|---|")
    for src in sorted(b.keys()):
        d = b[src]
        src_nc_w = d["source_nc"]["word_count"]
        src_vc_w = d["source_vc"]["word_count"]
        nc_wc = d["i2t_nc_word_count"]
        vc_wc = d["i2t_vc_word_count"]
        lines.append(f"| {src} | {src_nc_w} | {nc_wc['mean']:.1f} ± {nc_wc['sd']:.1f} | {src_vc_w} | {vc_wc['mean']:.1f} ± {vc_wc['sd']:.1f} |")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    main()