"""
Tier-3 analyses for the thesis Evaluation chapter.

Outputs:
  tier3_results.md / tier3_results.json
  figures/multivendor_brysbaert.pdf       — Brysbaert mean per vendor (boxplot)
  figures/multivendor_quality_table.png   — quick visual of pass rates
  figures/image_latency_distribution.pdf  — histogram of all generation times
  figures/image_latency_per_model.pdf     — boxplot per image model
  figures/image_success_over_time.pdf     — daily success rate timeline

Analyses:
  C2. Multi-vendor archive re-evaluation. Parses the 23 stimuli_all_models_*.txt
      files in testBench/exports. Extracts every per-model stimulus block
      (handles both Format A "Sentences:" form and Format B "MC Stimulus:" /
      "NC Stimulus:" / "VC Stimulus:" blocks). Scores each block with the same
      Brysbaert + WordNet pipeline used for the Gemini corpus, and produces a
      side-by-side table that backs the model selection decision quantitatively.

  F1. Image generation latency analysis. Reads all image_gen_timings.jsonl
      files. Reports overall success rate, p50/p90/p95/p99 latency for the
      successful subset, per-model breakdown, daily success-rate trend, and
      a histogram of successful-call durations.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# Reuse the analyzer's noun extractor + Brysbaert lookup
ANALYZER_DIR = Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1/semantic_analyzer")
sys.path.insert(0, str(ANALYZER_DIR))
import spacy  # noqa: E402
from nltk.corpus import wordnet as wn  # noqa: E402
from brysbaert_data import get_concreteness  # noqa: E402

NLP = spacy.load("en_core_web_sm")

EVAL_DIR = Path("/Users/noman/Documents/Thesis/evaluation")
FIG_DIR = EVAL_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)


# ── shared scoring (mirror of evaluate_priors.py) ────────────────────────────


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
    doc = NLP(text)
    return [tok.lemma_.lower() for tok in doc if tok.pos_ in ("NOUN", "PROPN") and tok.is_alpha]


def safe_mean(xs):
    xs = [x for x in xs if x is not None]
    return statistics.fmean(xs) if xs else None


def score_text(text: str) -> dict:
    nouns = extract_nouns(text)
    bry = [get_concreteness(n) for n in nouns]
    wnd = [wn_depth_min(n) for n in nouns]
    words = sum(1 for tok in NLP(text) if tok.is_alpha)
    sents = sum(1 for s in NLP(text).sents if s.text.strip())
    return {
        "word_count": words,
        "sentence_count": sents,
        "noun_count": len(nouns),
        "brysbaert_mean": safe_mean(bry),
        "wordnet_depth_mean": safe_mean(wnd),
    }


# ── C2. Parse multi-vendor archive files ───────────────────────────────────


VENDOR_HEADER_RE = re.compile(r"^\[([A-Z]+)\]\s*$")
MODEL_RE = re.compile(r"^\s*(?:-\s+)?Model:\s*(.+?)\s*$")
STATUS_RE = re.compile(r"^\s*Status:\s*(\w+)\s*$")
ERROR_RE = re.compile(r"^\s*Error:\s*(.*)$")
SENTENCES_HDR_RE = re.compile(r"^\s*Sentences:\s*(\d+)\s*$")
NUMBERED_LINE_RE = re.compile(r"^\s+\d+\.\s+(.*)$")
LEVEL_HDR_RE = re.compile(r"^(NC|MC|VC)\s+Stimulus:\s*$")


def parse_multivendor_file(path: Path) -> list[dict]:
    """Parse a single stimuli_all_models_*.txt file.

    Returns a list of records, one per model entry. Each record has:
      file, task, generated_at, vendor, model, status, error, paragraph.

    Handles Format A (numbered sentence lines under "Sentences: N") and
    Format B (paragraph blocks under "NC/MC/VC Stimulus:").
    For Format B, only the MC paragraph is taken if all three are present —
    matches the comparison frame the project actually used.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()

    # Parse header
    task = ""
    gen_at = ""
    for line in lines[:15]:
        if line.startswith("Task:"):
            task = line.split(":", 1)[1].strip()
        elif line.startswith("Generated at:"):
            gen_at = line.split(":", 1)[1].strip()

    out: list[dict] = []
    vendor = ""
    cur_model = None  # dict being built

    def flush():
        nonlocal cur_model
        if cur_model is not None:
            paragraph = ""
            # Format B: prefer MC, else VC, else NC
            for k in ("mc_text", "vc_text", "nc_text"):
                if cur_model.get(k):
                    paragraph = cur_model[k]
                    break
            # Format A: stitch numbered sentences together
            if not paragraph and cur_model.get("sentences"):
                paragraph = " ".join(cur_model["sentences"])
            cur_model["paragraph"] = paragraph
            out.append(cur_model)
        cur_model = None

    section = None  # current Format-B section (nc/mc/vc) or "sentences"

    for line in lines:
        m_vendor = VENDOR_HEADER_RE.match(line)
        if m_vendor:
            flush()
            vendor = m_vendor.group(1)
            section = None
            continue

        m_model = MODEL_RE.match(line)
        if m_model:
            flush()
            cur_model = {
                "file": path.name,
                "task": task,
                "generated_at": gen_at,
                "vendor": vendor,
                "model": m_model.group(1),
                "status": "",
                "error": "",
                "sentences": [],
                "nc_text": "", "mc_text": "", "vc_text": "",
            }
            section = None
            continue

        if cur_model is None:
            continue

        m_status = STATUS_RE.match(line)
        if m_status:
            cur_model["status"] = m_status.group(1).lower()
            continue

        m_error = ERROR_RE.match(line)
        if m_error:
            cur_model["error"] = m_error.group(1).strip()
            continue

        if SENTENCES_HDR_RE.match(line):
            section = "sentences"
            continue

        m_level = LEVEL_HDR_RE.match(line)
        if m_level:
            section = m_level.group(1).lower()  # nc / mc / vc
            continue

        if section == "sentences":
            m_num = NUMBERED_LINE_RE.match(line)
            if m_num:
                cur_model["sentences"].append(m_num.group(1).strip())
            continue

        if section in ("nc", "mc", "vc"):
            stripped = line.strip()
            if not stripped:
                # blank line ends the paragraph
                section = None
                continue
            key = f"{section}_text"
            cur_model[key] = (cur_model.get(key, "") + " " + stripped).strip()
            continue

    flush()
    return out


def c2_multivendor():
    archive_dir = Path("/Users/noman/Projects/design stimuli/testBench/exports")
    files = sorted(archive_dir.glob("stimuli_all_models_*.txt"))
    print(f"  parsing {len(files)} multi-vendor files...")
    all_entries: list[dict] = []
    for f in files:
        all_entries.extend(parse_multivendor_file(f))

    print(f"  parsed {len(all_entries)} model entries")

    # Score each successful entry that has a non-trivial paragraph
    for e in all_entries:
        text = (e.get("paragraph") or "").strip()
        if e.get("status") == "ok" and len(text) > 30:
            metrics = score_text(text)
            e.update(metrics)
        else:
            e["brysbaert_mean"] = None
            e["wordnet_depth_mean"] = None
            e["word_count"] = 0
            e["sentence_count"] = 0
            e["noun_count"] = 0

    # Per-vendor aggregates
    by_vendor = defaultdict(list)
    by_model = defaultdict(list)
    status_counter = Counter()
    for e in all_entries:
        by_vendor[e["vendor"]].append(e)
        by_model[(e["vendor"], e["model"])].append(e)
        status_counter[(e["vendor"], e["status"])] += 1

    vendor_rows = []
    for vendor in sorted(by_vendor):
        ent = by_vendor[vendor]
        successful = [e for e in ent if e["status"] == "ok" and e["brysbaert_mean"] is not None]
        n_total = len(ent)
        n_success = sum(1 for e in ent if e["status"] == "ok")
        n_scored = len(successful)
        bry_mean = safe_mean([e["brysbaert_mean"] for e in successful])
        wn_mean = safe_mean([e["wordnet_depth_mean"] for e in successful])
        wc_mean = safe_mean([e["word_count"] for e in successful])
        sc_mean = safe_mean([e["sentence_count"] for e in successful])
        vendor_rows.append({
            "vendor": vendor,
            "n_attempts": n_total,
            "n_success": n_success,
            "n_scored": n_scored,
            "success_rate": n_success / n_total * 100 if n_total else None,
            "brysbaert_mean": bry_mean,
            "wordnet_depth_mean": wn_mean,
            "word_count_mean": wc_mean,
            "sentence_count_mean": sc_mean,
        })

    model_rows = []
    for (vendor, model), ent in sorted(by_model.items()):
        successful = [e for e in ent if e["status"] == "ok" and e["brysbaert_mean"] is not None]
        n_total = len(ent)
        n_success = sum(1 for e in ent if e["status"] == "ok")
        model_rows.append({
            "vendor": vendor,
            "model": model,
            "n_attempts": n_total,
            "n_success": n_success,
            "success_rate": n_success / n_total * 100 if n_total else None,
            "brysbaert_mean": safe_mean([e["brysbaert_mean"] for e in successful]),
            "wordnet_depth_mean": safe_mean([e["wordnet_depth_mean"] for e in successful]),
            "word_count_mean": safe_mean([e["word_count"] for e in successful]),
            "sentence_count_mean": safe_mean([e["sentence_count"] for e in successful]),
        })

    # Plot per-vendor boxplots of Brysbaert means (where ≥ 3 successful entries)
    plot_data = []
    plot_labels = []
    for vendor in sorted(by_vendor):
        bs = [e["brysbaert_mean"] for e in by_vendor[vendor]
              if e.get("brysbaert_mean") is not None]
        if len(bs) >= 3:
            plot_data.append(bs)
            plot_labels.append(f"{vendor}\n(n={len(bs)})")

    if plot_data:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        bp = ax.boxplot(plot_data, tick_labels=plot_labels, patch_artist=True, widths=0.55)
        for patch in bp["boxes"]:
            patch.set_facecolor("#5B9BD5")
            patch.set_alpha(0.8)
        ax.set_ylabel("Mean Brysbaert concreteness (1–5)")
        ax.set_title("Per-vendor concreteness distribution (testBench multi-vendor archive)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "multivendor_brysbaert.pdf")
        fig.savefig(FIG_DIR / "multivendor_brysbaert.png", dpi=160)
        plt.close(fig)

    return {
        "n_files": len(files),
        "n_model_entries": len(all_entries),
        "status_breakdown": [
            {"vendor": v, "status": s, "count": c}
            for (v, s), c in sorted(status_counter.items())
        ],
        "per_vendor": vendor_rows,
        "per_model": model_rows,
    }


# ── F1. Image latency analysis ─────────────────────────────────────────────


def f1_image_latency():
    roots = [
        Path("/Users/noman/Projects/design stimuli"),
        Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1"),
    ]
    paths = []
    for r in roots:
        if r.exists():
            paths.extend(r.rglob("image_gen_timings.jsonl"))

    entries = []
    for p in paths:
        for raw in p.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not raw.strip():
                continue
            try:
                e = json.loads(raw)
            except json.JSONDecodeError:
                continue
            e["_source"] = str(p)
            entries.append(e)

    print(f"  parsed {len(entries)} timing entries from {len(paths)} files")

    # Overall stats
    successful_durs = [e["duration_s"] for e in entries if e.get("success") and e.get("duration_s") is not None]
    failed_durs = [e["duration_s"] for e in entries if not e.get("success") and e.get("duration_s") is not None]

    overall = {
        "n_entries": len(entries),
        "n_success": sum(1 for e in entries if e.get("success")),
        "n_failed": sum(1 for e in entries if not e.get("success")),
        "success_rate_pct": (sum(1 for e in entries if e.get("success")) / len(entries) * 100) if entries else None,
        "successful_duration": _percentiles(successful_durs),
        "failed_duration": _percentiles(failed_durs),
    }

    # Per-model
    by_model = defaultdict(list)
    for e in entries:
        m = (e.get("model") or "").strip() or "(unknown)"
        by_model[m].append(e)

    per_model = []
    for m, ent in sorted(by_model.items(), key=lambda x: -len(x[1])):
        ok = [x["duration_s"] for x in ent if x.get("success") and x.get("duration_s") is not None]
        n_ok = sum(1 for x in ent if x.get("success"))
        per_model.append({
            "model": m,
            "n": len(ent),
            "n_success": n_ok,
            "success_rate_pct": n_ok / len(ent) * 100 if ent else None,
            **{f"successful_{k}": v for k, v in _percentiles(ok).items()},
        })

    # Histogram (successful only)
    if successful_durs:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        cap = float(np.percentile(successful_durs, 99))
        bins = np.linspace(0, cap, 40)
        ax.hist(successful_durs, bins=bins, color="#70AD47", edgecolor="white", linewidth=0.5)
        for pct, color, label in [(50, "#666666", "p50"), (95, "#cc4125", "p95")]:
            v = float(np.percentile(successful_durs, pct))
            ax.axvline(v, color=color, linestyle="--", linewidth=1, label=f"{label} = {v:.1f}s")
        ax.set_xlabel("Generation time (seconds)")
        ax.set_ylabel("Number of successful image-gen calls")
        ax.set_title(f"Distribution of successful image-generation durations (n={len(successful_durs)})")
        ax.legend(frameon=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "image_latency_distribution.pdf")
        fig.savefig(FIG_DIR / "image_latency_distribution.png", dpi=160)
        plt.close(fig)

    # Per-model boxplot
    plot_data, plot_labels = [], []
    for m, ent in sorted(by_model.items(), key=lambda x: -len(x[1])):
        ok = [x["duration_s"] for x in ent if x.get("success") and x.get("duration_s") is not None]
        if len(ok) >= 5:
            plot_data.append(ok)
            plot_labels.append(f"{m}\n(n={len(ok)})")
    if plot_data:
        fig, ax = plt.subplots(figsize=(max(6, 1.5 * len(plot_data)), 4.5))
        bp = ax.boxplot(plot_data, tick_labels=plot_labels, patch_artist=True, widths=0.55, showfliers=False)
        for patch in bp["boxes"]:
            patch.set_facecolor("#ED7D31")
            patch.set_alpha(0.8)
        ax.set_ylabel("Generation time (seconds)")
        ax.set_title("Per-model image generation latency (successful calls, outliers hidden)")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
        fig.tight_layout()
        fig.savefig(FIG_DIR / "image_latency_per_model.pdf")
        fig.savefig(FIG_DIR / "image_latency_per_model.png", dpi=160)
        plt.close(fig)

    # Daily success-rate timeline
    by_day = defaultdict(lambda: {"ok": 0, "fail": 0})
    for e in entries:
        ts = e.get("timestamp")
        if not ts:
            continue
        try:
            day = datetime.fromisoformat(ts).date()
        except ValueError:
            continue
        if e.get("success"):
            by_day[day]["ok"] += 1
        else:
            by_day[day]["fail"] += 1

    if by_day:
        days_sorted = sorted(by_day)
        ok_counts = [by_day[d]["ok"] for d in days_sorted]
        fail_counts = [by_day[d]["fail"] for d in days_sorted]
        success_rates = [
            (o / (o + f) * 100) if (o + f) else 0 for o, f in zip(ok_counts, fail_counts)
        ]
        fig, ax = plt.subplots(figsize=(10, 4.5))
        # Stacked bars: ok green, fail red
        x = np.arange(len(days_sorted))
        ax.bar(x, ok_counts, color="#70AD47", label="Success", alpha=0.85)
        ax.bar(x, fail_counts, bottom=ok_counts, color="#cc4125", label="Failure", alpha=0.85)
        ax.set_xticks(x[::max(1, len(x) // 12)])
        ax.set_xticklabels([d.strftime("%m-%d") for d in days_sorted[::max(1, len(x) // 12)]], rotation=30, ha="right")
        ax.set_ylabel("Image generation calls")
        ax.set_title("Daily image-generation volume and success/failure breakdown")
        ax.legend(frameon=False, loc="upper left")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        # Secondary axis: success-rate line
        ax2 = ax.twinx()
        ax2.plot(x, success_rates, color="#1f77b4", linewidth=1.4, marker="o", markersize=3, label="Success rate %")
        ax2.set_ylabel("Success rate (%)", color="#1f77b4")
        ax2.set_ylim(0, 105)
        ax2.spines["top"].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG_DIR / "image_success_over_time.pdf")
        fig.savefig(FIG_DIR / "image_success_over_time.png", dpi=160)
        plt.close(fig)

    return {
        "overall": overall,
        "per_model": per_model,
        "n_days": len(by_day),
    }


def _percentiles(xs):
    if not xs:
        return {}
    arr = np.array(xs)
    return {
        "n": len(xs),
        "mean": float(arr.mean()),
        "median": float(np.percentile(arr, 50)),
        "p90": float(np.percentile(arr, 90)),
        "p95": float(np.percentile(arr, 95)),
        "p99": float(np.percentile(arr, 99)),
        "max": float(arr.max()),
    }


# ── reporting ─────────────────────────────────────────────────────────────


def write_report(c2, f1):
    L = []
    L.append("# Tier 3 Analyses")
    L.append("")
    L.append("Quantitative backing for the model-selection narrative (C2) and the")
    L.append("empirical-timeout claim in Implementation §3.7.5 (F1).")
    L.append("")

    # C2
    L.append("## C2. Multi-vendor archive re-evaluation")
    L.append("")
    L.append(f"Source: {c2['n_files']} files in `testBench/exports/stimuli_all_models_*.txt`. {c2['n_model_entries']} model entries parsed.")
    L.append("")
    L.append("### Per-vendor summary")
    L.append("")
    L.append("| Vendor | Attempts | Success | Scored | Success % | Brys mean | WN depth | Word count | Sent count |")
    L.append("|--------|----------|---------|--------|-----------|-----------|----------|------------|------------|")
    for r in c2["per_vendor"]:
        f = lambda x: f"{x:.3f}" if x is not None else "—"
        sr = f"{r['success_rate']:.1f}%" if r["success_rate"] is not None else "—"
        L.append(f"| {r['vendor']} | {r['n_attempts']} | {r['n_success']} | {r['n_scored']} | {sr} | {f(r['brysbaert_mean'])} | {f(r['wordnet_depth_mean'])} | {f(r['word_count_mean'])} | {f(r['sentence_count_mean'])} |")
    L.append("")
    L.append("### Per-model summary (only models with ≥ 3 attempts shown)")
    L.append("")
    L.append("| Vendor | Model | Attempts | Success % | Brys mean | WN depth | Word count |")
    L.append("|--------|-------|----------|-----------|-----------|----------|------------|")
    for r in c2["per_model"]:
        if r["n_attempts"] < 3:
            continue
        f = lambda x: f"{x:.3f}" if x is not None else "—"
        sr = f"{r['success_rate']:.1f}%" if r["success_rate"] is not None else "—"
        L.append(f"| {r['vendor']} | {r['model']} | {r['n_attempts']} | {sr} | {f(r['brysbaert_mean'])} | {f(r['wordnet_depth_mean'])} | {f(r['word_count_mean'])} |")
    L.append("")
    L.append("Boxplot at `figures/multivendor_brysbaert.pdf`.")
    L.append("")

    # F1
    L.append("## F1. Image generation latency")
    L.append("")
    o = f1["overall"]
    L.append(f"Total entries: **{o['n_entries']}**, success: {o['n_success']} ({o['success_rate_pct']:.1f}%), failure: {o['n_failed']}.")
    L.append("")
    if o["successful_duration"]:
        s = o["successful_duration"]
        L.append("### Successful-call duration percentiles")
        L.append("")
        L.append(f"- n = {s['n']}")
        L.append(f"- mean = {s['mean']:.2f}s")
        L.append(f"- p50 = {s['median']:.2f}s")
        L.append(f"- p90 = {s['p90']:.2f}s")
        L.append(f"- p95 = {s['p95']:.2f}s")
        L.append(f"- p99 = {s['p99']:.2f}s")
        L.append(f"- max = {s['max']:.2f}s")
        L.append("")
        L.append(f"Implementation §3.7.5 sets the operating timeout as 1.5× the empirical mean: **{s['mean'] * 1.5:.0f}s** would be the corresponding bound.")
        L.append("")
    if o["failed_duration"]:
        s = o["failed_duration"]
        L.append("### Failed-call duration percentiles (how fast/slow failures happen)")
        L.append("")
        L.append(f"- n = {s['n']}, mean = {s['mean']:.2f}s, p50 = {s['median']:.2f}s, p95 = {s['p95']:.2f}s, max = {s['max']:.2f}s")
        L.append("")

    L.append("### Per-model timing")
    L.append("")
    L.append("| Model | n | Success % | n success | mean (s) | p50 | p90 | p95 | p99 | max |")
    L.append("|-------|---|-----------|-----------|----------|-----|-----|-----|-----|-----|")
    for r in f1["per_model"]:
        if r["n"] < 3:
            continue
        sr = f"{r['success_rate_pct']:.1f}%"
        f_ = lambda v: f"{v:.2f}" if v is not None else "—"
        L.append(f"| {r['model']} | {r['n']} | {sr} | {r['n_success']} | "
                 f"{f_(r.get('successful_mean'))} | {f_(r.get('successful_median'))} | "
                 f"{f_(r.get('successful_p90'))} | {f_(r.get('successful_p95'))} | "
                 f"{f_(r.get('successful_p99'))} | {f_(r.get('successful_max'))} |")
    L.append("")
    L.append("Histograms at `figures/image_latency_distribution.pdf`, `figures/image_latency_per_model.pdf`, `figures/image_success_over_time.pdf`.")
    L.append("")

    return "\n".join(L)


def main():
    print("[C2] Multi-vendor archive…")
    c2 = c2_multivendor()

    print("[F1] Image latency…")
    f1 = f1_image_latency()

    md = write_report(c2, f1)
    (EVAL_DIR / "tier3_results.md").write_text(md, encoding="utf-8")
    (EVAL_DIR / "tier3_results.json").write_text(json.dumps({"C2": c2, "F1": f1}, indent=2), encoding="utf-8")

    # Highlights to stdout
    print("\n=== HIGHLIGHTS ===\n")
    print("C2 — Per-vendor success rates and Brysbaert means:")
    for r in c2["per_vendor"]:
        sr = f"{r['success_rate']:.1f}%" if r["success_rate"] is not None else "—"
        bm = f"{r['brysbaert_mean']:.3f}" if r["brysbaert_mean"] is not None else "—"
        print(f"  {r['vendor']:<10} attempts={r['n_attempts']:>4}  success={sr}  Brysbaert={bm}")
    print(f"\nF1 — overall: n={f1['overall']['n_entries']}, success={f1['overall']['success_rate_pct']:.1f}%")
    if f1["overall"]["successful_duration"]:
        s = f1["overall"]["successful_duration"]
        print(f"  successful: mean={s['mean']:.2f}s, p50={s['median']:.2f}s, p95={s['p95']:.2f}s, p99={s['p99']:.2f}s")
    print(f"  daily span: {f1['n_days']} days")
    print(f"\nFull report: {EVAL_DIR / 'tier3_results.md'}")


if __name__ == "__main__":
    main()
