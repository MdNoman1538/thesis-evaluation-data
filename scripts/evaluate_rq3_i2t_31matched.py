"""
evaluate_rq3_i2t_31matched.py

Re-analyse the RQ3 secondary measurement (image-to-text round trip) using the
matched-n design: one i2t session per source for every source in the corpus.
Per source, the 5 i2t-nc descriptions are concatenated into one i2t-NC
paragraph and the 5 i2t-vc descriptions into one i2t-VC paragraph; both are
scored on WordNet AL and Brysbaert concreteness, mirroring the source-text
analysis of RQ2.

Outputs (under evaluation/data/i2t_31matched_analysis/):
  per_source.json    per-source nc/vc AL and Brysbaert means, plus source-text
                     gap and i2t gap for the source-text-vs-i2t correlation
  summary.json       paragraph-level paired t-test, per-task split, and the
                     Pearson r between source-text gap and i2t gap

Reads:
  i2t_31matched/<source>/descriptions.json     (1 record per source)
  data/corpus/<source>/{nc,vc}/stimulus.txt    (source-text paragraphs)
"""

from __future__ import annotations

import json
import statistics
import sys
from math import erf, sqrt
from pathlib import Path


ANALYZER_DIR = Path("/Users/noman/Documents/Thesis/Apps/StimuliGenerator/semantic_analyzer")
sys.path.insert(0, str(ANALYZER_DIR))

import spacy
from nltk.corpus import wordnet as wn
from brysbaert_data import get_concreteness

NLP = spacy.load("en_core_web_sm")

I2T_DIR = Path("/Users/noman/Documents/Thesis/evaluation/data/i2t_31matched")
CORPUS_DIR = Path("/Users/noman/Documents/Thesis/evaluation/data/corpus")
OUT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/data/i2t_31matched_analysis")
MAX_DEPTH = 20


def wn_depth_min(word: str):
    syns = wn.synsets(word, pos=wn.NOUN)
    depths = []
    for s in syns:
        paths = s.hypernym_paths()
        if paths:
            depths.append(min(len(p) for p in paths))
    return min(depths) if depths else None


def extract_nouns(text: str) -> list[str]:
    doc = NLP(text or "")
    return [tok.lemma_.lower() for tok in doc if tok.pos_ in ("NOUN", "PROPN")]


def al_from_depth(depth: int) -> float:
    return 1.0 - (depth - 1) / (MAX_DEPTH - 1)


def metrics_for(text: str) -> dict:
    nouns = extract_nouns(text)
    bry = [b for b in (get_concreteness(n) for n in nouns) if b is not None]
    wnd = [w for w in (wn_depth_min(n) for n in nouns) if w is not None]
    al = [al_from_depth(d) for d in wnd]
    return {
        "noun_count": len(nouns),
        "wordnet_depth_mean": statistics.fmean(wnd) if wnd else None,
        "al_mean": statistics.fmean(al) if al else None,
        "brysbaert_mean": statistics.fmean(bry) if bry else None,
    }


def paired_t(diffs: list[float]) -> tuple[float, float, float]:
    n = len(diffs)
    if n < 2:
        return 0.0, 1.0, 0.0
    m = statistics.fmean(diffs)
    s = statistics.stdev(diffs)
    se = s / (n ** 0.5)
    t = m / se if se else float("inf")
    p = 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))
    d = m / s if s else float("inf")
    return t, p, d


def pearson_r(xs: list[float], ys: list[float]) -> tuple[float, float]:
    n = len(xs)
    if n < 3:
        return 0.0, 1.0
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sx2 = sum((x - mx) ** 2 for x in xs)
    sy2 = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denom = (sx2 * sy2) ** 0.5
    if denom == 0:
        return 0.0, 1.0
    r = sxy / denom
    t = r * ((n - 2) / max(1 - r * r, 1e-12)) ** 0.5
    p = 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))
    return r, p


def load_source_text(source_dir: Path, condition: str) -> str:
    p = CORPUS_DIR / source_dir.name / condition / "stimulus.txt"
    if not p.is_file():
        raise FileNotFoundError(f"missing {p}")
    return p.read_text(encoding="utf-8").strip()


def task_for(source_name: str) -> str:
    if source_name.startswith("jar"):
        return "jar"
    if source_name.startswith("skii") or source_name.startswith("snow"):
        return "skii"
    return "other"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = sorted(p for p in I2T_DIR.iterdir() if p.is_dir())
    print(f"Found {len(sources)} i2t source folders")

    per_source: list[dict] = []
    skipped: list[str] = []

    for i, src_dir in enumerate(sources, start=1):
        rec_path = src_dir / "descriptions.json"
        if not rec_path.is_file():
            skipped.append(src_dir.name)
            continue
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        src_name = rec["source"]
        task = task_for(src_name)

        nc_i2t_para = " ".join(d["description"] for d in rec["nc"])
        vc_i2t_para = " ".join(d["description"] for d in rec["vc"])

        nc_src_para = load_source_text(src_dir, "nc")
        vc_src_para = load_source_text(src_dir, "vc")

        m_nc_i2t = metrics_for(nc_i2t_para)
        m_vc_i2t = metrics_for(vc_i2t_para)
        m_nc_src = metrics_for(nc_src_para)
        m_vc_src = metrics_for(vc_src_para)

        delta_al_i2t = (m_nc_i2t["al_mean"] or 0) - (m_vc_i2t["al_mean"] or 0)
        delta_brys_i2t = (m_nc_i2t["brysbaert_mean"] or 0) - (m_vc_i2t["brysbaert_mean"] or 0)
        delta_al_src = (m_nc_src["al_mean"] or 0) - (m_vc_src["al_mean"] or 0)
        delta_brys_src = (m_nc_src["brysbaert_mean"] or 0) - (m_vc_src["brysbaert_mean"] or 0)

        per_source.append({
            "source": src_name,
            "task": task,
            "i2t_nc_al": m_nc_i2t["al_mean"],
            "i2t_vc_al": m_vc_i2t["al_mean"],
            "i2t_delta_al": delta_al_i2t,
            "i2t_nc_brys": m_nc_i2t["brysbaert_mean"],
            "i2t_vc_brys": m_vc_i2t["brysbaert_mean"],
            "i2t_delta_brys": delta_brys_i2t,
            "src_nc_al": m_nc_src["al_mean"],
            "src_vc_al": m_vc_src["al_mean"],
            "src_delta_al": delta_al_src,
            "src_nc_brys": m_nc_src["brysbaert_mean"],
            "src_vc_brys": m_vc_src["brysbaert_mean"],
            "src_delta_brys": delta_brys_src,
        })

        print(f"  [{i:2d}/{len(sources)}] {src_name:50s} i2t Δ={delta_al_i2t:+.4f}  src Δ={delta_al_src:+.4f}")

    if not per_source:
        print("No sources analysed; exiting.")
        return

    # Paragraph-level paired tests
    i2t_al_diffs = [r["i2t_delta_al"] for r in per_source]
    i2t_brys_diffs = [r["i2t_delta_brys"] for r in per_source]

    t_al, p_al, d_al = paired_t(i2t_al_diffs)
    t_brys, p_brys, d_brys = paired_t(i2t_brys_diffs)

    # Per-task split (top-1 AL)
    per_task_summary: dict[str, dict] = {}
    for task in ("jar", "skii"):
        ds = [r["i2t_delta_al"] for r in per_source if r["task"] == task]
        if len(ds) < 2:
            continue
        t_, p_, dc_ = paired_t(ds)
        per_task_summary[task] = {
            "n": len(ds),
            "mean_delta_al": statistics.fmean(ds),
            "sd_delta_al": statistics.stdev(ds),
            "t": t_,
            "p": p_,
            "cohen_d": dc_,
            "nc_more_abstract_count": sum(1 for x in ds if x > 0),
        }

    # Per-source correlation: source-text gap vs i2t gap
    src_al = [r["src_delta_al"] for r in per_source]
    i2t_al = [r["i2t_delta_al"] for r in per_source]
    r_al, p_r_al = pearson_r(src_al, i2t_al)

    src_brys = [r["src_delta_brys"] for r in per_source]
    i2t_brys = [r["i2t_delta_brys"] for r in per_source]
    r_brys, p_r_brys = pearson_r(src_brys, i2t_brys)

    summary = {
        "n_sources": len(per_source),
        "paragraph_level_al": {
            "i2t_nc_mean": statistics.fmean(r["i2t_nc_al"] for r in per_source),
            "i2t_vc_mean": statistics.fmean(r["i2t_vc_al"] for r in per_source),
            "mean_delta_nc_minus_vc": statistics.fmean(i2t_al_diffs),
            "sd_delta": statistics.stdev(i2t_al_diffs),
            "t": t_al,
            "p": p_al,
            "cohen_d": d_al,
            "nc_more_abstract_count": sum(1 for x in i2t_al_diffs if x > 0),
            "total": len(i2t_al_diffs),
        },
        "paragraph_level_brysbaert": {
            "i2t_nc_mean": statistics.fmean(r["i2t_nc_brys"] for r in per_source),
            "i2t_vc_mean": statistics.fmean(r["i2t_vc_brys"] for r in per_source),
            "mean_delta_nc_minus_vc": statistics.fmean(i2t_brys_diffs),
            "sd_delta": statistics.stdev(i2t_brys_diffs),
            "t": t_brys,
            "p": p_brys,
            "cohen_d": d_brys,
        },
        "per_task_al": per_task_summary,
        "source_text_vs_i2t_correlation": {
            "al_pearson_r": r_al,
            "al_pearson_p": p_r_al,
            "brysbaert_pearson_r": r_brys,
            "brysbaert_pearson_p": p_r_brys,
            "n_pairs": len(src_al),
        },
        "skipped_sources": skipped,
    }

    (OUT_DIR / "per_source.json").write_text(
        json.dumps(per_source, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print("\nSummary")
    print(f"  n sources analysed: {summary['n_sources']}")
    print(f"  Paragraph AL: mean Δ = {summary['paragraph_level_al']['mean_delta_nc_minus_vc']:+.4f}, "
          f"d = {summary['paragraph_level_al']['cohen_d']:.2f}, "
          f"NC > VC in {summary['paragraph_level_al']['nc_more_abstract_count']}/{summary['paragraph_level_al']['total']}")
    print(f"  Paragraph Brys: mean Δ = {summary['paragraph_level_brysbaert']['mean_delta_nc_minus_vc']:+.4f}, "
          f"d = {summary['paragraph_level_brysbaert']['cohen_d']:.2f}")
    for task, s in per_task_summary.items():
        print(f"  Per-task {task} (n={s['n']}): Δ AL = {s['mean_delta_al']:+.4f}, d = {s['cohen_d']:.2f}, "
              f"NC > VC in {s['nc_more_abstract_count']}/{s['n']}")
    print(f"  Source-text vs i2t correlation (AL): r = {r_al:+.3f}, p = {p_r_al:.2e}, n = {len(src_al)}")
    print(f"  Output at {OUT_DIR}")


if __name__ == "__main__":
    main()
