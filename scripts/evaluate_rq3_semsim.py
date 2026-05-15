"""
Semantic-similarity analysis: how closely do the 60 i2t-derived stimuli
(30 NC + 30 VC, three source folders) match the original source text
stimuli they were derived from?

Model: sentence-transformers/all-MiniLM-L6-v2 (sentence embeddings, cosine).
This is the standard choice for short-text semantic similarity; it produces
384-dim embeddings and runs in seconds on CPU.

Comparisons computed:

1. Own-condition similarity ("recovery")
   i2t-NC vs source-NC for the same source folder
   i2t-VC vs source-VC for the same source folder
   → expected high if the round trip preserves semantic content

2. Cross-condition similarity ("condition fidelity")
   i2t-NC vs source-VC for the same source folder
   i2t-VC vs source-NC for the same source folder
   → expected lower than own-condition if the abstraction manipulation
     is semantically meaningful and recoverable

3. Cross-source similarity ("task fidelity")
   i2t-NC vs source-NC from a DIFFERENT source folder
   → expected lowest (different design tasks should not look alike)

4. i2t-NC vs i2t-VC within a session
   → does the round trip preserve a distinction between the two
     conditions in the description space itself?

Outputs (/Users/noman/Documents/Thesis/evaluation/results/rq3/):
  semsim_log.jsonl    — per-session record of all similarity scores
  semsim_results.md   — full tables
  semsim_results.json — machine-readable
  figures/
    semsim_own_vs_cross.{pdf,png}
    semsim_per_source_recovery.{pdf,png}
"""
from __future__ import annotations

import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity


def _mean_pool(last_hidden_state, attention_mask):
    """Mean-pool token embeddings, masking out padding (same as sentence-transformers)."""
    mask = attention_mask.unsqueeze(-1).float()
    summed = (last_hidden_state * mask).sum(dim=1)
    counts = mask.sum(dim=1).clamp(min=1e-9)
    return summed / counts


class MiniLMEncoder:
    def __init__(self, model_name="sentence-transformers/all-MiniLM-L6-v2"):
        self.tok = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    @torch.no_grad()
    def encode(self, texts, convert_to_numpy=True, normalize_embeddings=True):
        enc = self.tok(texts, padding=True, truncation=True, max_length=256, return_tensors="pt")
        out = self.model(**enc)
        emb = _mean_pool(out.last_hidden_state, enc["attention_mask"])
        if normalize_embeddings:
            emb = torch.nn.functional.normalize(emb, p=2, dim=1)
        return emb.cpu().numpy() if convert_to_numpy else emb


SentenceTransformer = MiniLMEncoder  # drop-in shim with the same .encode() API

# Sources and data locations
CORPUS_DIR = Path("/Users/noman/Documents/Thesis/app output data save")
SESSIONS_DIR = Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1/uploaded_images")
OUT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/results/rq3")
FIG_DIR = OUT_DIR / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FIG_DIR.mkdir(parents=True, exist_ok=True)

# i2t log produced by evaluate_i2t.py (already has source_folder + assembled NC/VC text)
I2T_LOG = Path("/Users/noman/Documents/Thesis/evaluation/results/rq3/i2t_log.jsonl")

SOURCES = ["jar 13 passed 3.1 pro", "jar 7 passed 3.1 pro", "skii 5 passed 3.1 pro"]
SHORT = {"jar 13 passed 3.1 pro": "jar13",
         "jar 7 passed 3.1 pro": "jar7",
         "skii 5 passed 3.1 pro": "skii5"}


def load_source_texts() -> dict[str, dict[str, str]]:
    """{source_folder: {'nc': str, 'vc': str}} from each run's metadata.json."""
    out = {}
    for src in SOURCES:
        meta = (CORPUS_DIR / src / "metadata.json")
        m = json.loads(meta.read_text(encoding="utf-8"))
        out[src] = {
            "nc": (m.get("nc") or {}).get("stimulus") or "",
            "vc": (m.get("vc") or {}).get("stimulus") or "",
        }
    return out


def load_i2t_sessions() -> list[dict]:
    """Each record has nc_text, vc_text, source_folder."""
    out = []
    for line in I2T_LOG.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("source_folder") in SOURCES:
                out.append(r)
    return out


def main():
    print("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    print("  loaded")

    print("Loading source texts and i2t sessions...")
    sources = load_source_texts()
    sessions = load_i2t_sessions()
    print(f"  3 source folders, {len(sessions)} i2t sessions")

    # Embed source texts (6 vectors: nc/vc for each of 3 sources)
    src_keys = []
    src_texts = []
    for s in SOURCES:
        src_keys.append((s, "nc")); src_texts.append(sources[s]["nc"])
        src_keys.append((s, "vc")); src_texts.append(sources[s]["vc"])
    print("Embedding source texts...")
    src_emb = model.encode(src_texts, convert_to_numpy=True, normalize_embeddings=True)

    # Embed i2t texts (60 vectors: nc/vc per session)
    print("Embedding i2t texts...")
    i2t_texts_nc = [s["nc_text"] for s in sessions]
    i2t_texts_vc = [s["vc_text"] for s in sessions]
    nc_emb = model.encode(i2t_texts_nc, convert_to_numpy=True, normalize_embeddings=True)
    vc_emb = model.encode(i2t_texts_vc, convert_to_numpy=True, normalize_embeddings=True)

    # ── compute per-session similarities ────────────────────────────────────
    records = []
    for idx, sess in enumerate(sessions):
        src = sess["source_folder"]
        # Find embedding indices
        own_nc_i = src_keys.index((src, "nc"))
        own_vc_i = src_keys.index((src, "vc"))

        # Per-session: i2t NC and VC embeddings
        i2t_nc_v = nc_emb[idx]
        i2t_vc_v = vc_emb[idx]

        rec = {
            "session": sess["session"],
            "source": src,
            "source_short": SHORT[src],
            # Own-condition recovery
            "i2t_nc__own_nc": float(np.dot(i2t_nc_v, src_emb[own_nc_i])),
            "i2t_vc__own_vc": float(np.dot(i2t_vc_v, src_emb[own_vc_i])),
            # Cross-condition (own source, other condition)
            "i2t_nc__own_vc": float(np.dot(i2t_nc_v, src_emb[own_vc_i])),
            "i2t_vc__own_nc": float(np.dot(i2t_vc_v, src_emb[own_nc_i])),
            # Within-session NC vs VC
            "i2t_nc__i2t_vc": float(np.dot(i2t_nc_v, i2t_vc_v)),
        }
        # Cross-source comparisons
        for other_src in SOURCES:
            if other_src == src:
                continue
            other_nc_i = src_keys.index((other_src, "nc"))
            other_vc_i = src_keys.index((other_src, "vc"))
            rec[f"i2t_nc__cross_{SHORT[other_src]}_nc"] = float(np.dot(i2t_nc_v, src_emb[other_nc_i]))
            rec[f"i2t_vc__cross_{SHORT[other_src]}_vc"] = float(np.dot(i2t_vc_v, src_emb[other_vc_i]))
        records.append(rec)

    # Persist per-session log
    with (OUT_DIR / "semsim_log.jsonl").open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")

    # ── aggregate by source ─────────────────────────────────────────────────
    by_src = defaultdict(list)
    for r in records:
        by_src[r["source"]].append(r)

    summary = {"overall": {}, "per_source": {}}

    def stat(xs):
        xs = list(xs)
        return {"n": len(xs), "mean": float(np.mean(xs)), "sd": float(np.std(xs, ddof=1)) if len(xs) > 1 else 0.0,
                "min": float(np.min(xs)), "max": float(np.max(xs))}

    metrics = [
        ("i2t_nc__own_nc",  "i2t-NC vs source-NC (own, RECOVERY)"),
        ("i2t_vc__own_vc",  "i2t-VC vs source-VC (own, RECOVERY)"),
        ("i2t_nc__own_vc",  "i2t-NC vs source-VC (cross-condition)"),
        ("i2t_vc__own_nc",  "i2t-VC vs source-NC (cross-condition)"),
        ("i2t_nc__i2t_vc",  "i2t-NC vs i2t-VC (within session)"),
    ]
    cross_metrics = []
    for src in SOURCES:
        for other in SOURCES:
            if other != src:
                k = f"i2t_nc__cross_{SHORT[other]}_nc"
                if any(k in r for r in by_src[src]):
                    cross_metrics.append((src, k))

    for key, _ in metrics:
        summary["overall"][key] = stat(r[key] for r in records)
    for src in SOURCES:
        srows = by_src[src]
        block = {}
        for key, _ in metrics:
            block[key] = stat(r[key] for r in srows)
        # Cross-source per-source: for this source's i2t-NC, similarity to other-source NC
        for other in SOURCES:
            if other == src:
                continue
            k = f"i2t_nc__cross_{SHORT[other]}_nc"
            block[k] = stat(r[k] for r in srows)
            k2 = f"i2t_vc__cross_{SHORT[other]}_vc"
            block[k2] = stat(r[k2] for r in srows)
        summary["per_source"][src] = block

    # ── figures ────────────────────────────────────────────────────────────
    _fig_own_vs_cross(records, FIG_DIR / "semsim_own_vs_cross")
    _fig_per_source_recovery(by_src, FIG_DIR / "semsim_per_source_recovery")

    # ── report ─────────────────────────────────────────────────────────────
    md = _write_markdown(summary, records, metrics)
    (OUT_DIR / "semsim_results.md").write_text(md, encoding="utf-8")
    (OUT_DIR / "semsim_results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(md)


def _fig_own_vs_cross(records, out_stub):
    own_nc = [r["i2t_nc__own_nc"] for r in records]
    cross_nc = [r["i2t_nc__own_vc"] for r in records]
    own_vc = [r["i2t_vc__own_vc"] for r in records]
    cross_vc = [r["i2t_vc__own_nc"] for r in records]
    within = [r["i2t_nc__i2t_vc"] for r in records]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    data = [own_nc, cross_nc, own_vc, cross_vc, within]
    labels = ["i2t-NC vs\nsource-NC\n(own)",
              "i2t-NC vs\nsource-VC\n(cross)",
              "i2t-VC vs\nsource-VC\n(own)",
              "i2t-VC vs\nsource-NC\n(cross)",
              "i2t-NC vs\ni2t-VC\n(within)"]
    palette = ["#5B9BD5", "#9DC3E6", "#70AD47", "#A9D18E", "#FFC000"]
    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
    for patch, c in zip(bp["boxes"], palette):
        patch.set_facecolor(c); patch.set_alpha(0.85)
    ax.set_ylabel("Cosine similarity (sentence-transformer embeddings)")
    ax.set_title("Semantic similarity: i2t-derived stimuli vs the original source texts (n=30 sessions)")
    ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(out_stub.with_suffix(".pdf"))
    fig.savefig(out_stub.with_suffix(".png"), dpi=160)
    plt.close(fig)


def _fig_per_source_recovery(by_src, out_stub):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), sharey=True)
    for ax, src in zip(axes, SOURCES):
        rows = by_src[src]
        own_nc = [r["i2t_nc__own_nc"] for r in rows]
        cross_nc = [r["i2t_nc__own_vc"] for r in rows]
        own_vc = [r["i2t_vc__own_vc"] for r in rows]
        cross_vc = [r["i2t_vc__own_nc"] for r in rows]
        data = [own_nc, cross_nc, own_vc, cross_vc]
        labels = ["NC↔NC", "NC↔VC", "VC↔VC", "VC↔NC"]
        palette = ["#5B9BD5", "#9DC3E6", "#70AD47", "#A9D18E"]
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.55)
        for patch, c in zip(bp["boxes"], palette):
            patch.set_facecolor(c); patch.set_alpha(0.85)
        ax.set_title(f"{SHORT[src]}  (n={len(rows)})")
        ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
    axes[0].set_ylabel("Cosine similarity")
    fig.suptitle("Per-source semantic similarity: i2t vs own source text", fontsize=11)
    fig.tight_layout()
    fig.savefig(out_stub.with_suffix(".pdf"))
    fig.savefig(out_stub.with_suffix(".png"), dpi=160)
    plt.close(fig)


def _write_markdown(summary, records, metrics):
    lines = []
    lines.append("# Semantic Similarity: i2t Derivatives vs Source Texts")
    lines.append("")
    lines.append(f"Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim, cosine similarity, normalised).")
    lines.append(f"")
    lines.append(f"Sessions analysed: **{len(records)}** across 3 source folders.")
    lines.append("")
    lines.append("## Overall (all 30 sessions)")
    lines.append("")
    lines.append("| Comparison | n | mean | SD | min | max |")
    lines.append("|---|---|---|---|---|---|")
    for key, label in metrics:
        s = summary["overall"][key]
        lines.append(f"| {label} | {s['n']} | {s['mean']:.3f} | {s['sd']:.3f} | {s['min']:.3f} | {s['max']:.3f} |")
    lines.append("")
    lines.append("**Reading:** own-condition (recovery) > cross-condition is the desired pattern. If own-condition is materially higher than cross-condition, the round trip is preserving the condition-specific semantic content.")
    lines.append("")
    lines.append("## Per-source breakdown")
    lines.append("")
    for src in SOURCES:
        lines.append(f"### {SHORT[src]}  ({src})")
        lines.append("")
        block = summary["per_source"][src]
        lines.append("| Comparison | n | mean | SD | min | max |")
        lines.append("|---|---|---|---|---|---|")
        for key, label in metrics:
            s = block[key]
            lines.append(f"| {label} | {s['n']} | {s['mean']:.3f} | {s['sd']:.3f} | {s['min']:.3f} | {s['max']:.3f} |")
        # cross-source
        for other in SOURCES:
            if other == src:
                continue
            k = f"i2t_nc__cross_{SHORT[other]}_nc"
            s = block[k]
            lines.append(f"| i2t-NC vs {SHORT[other]} source-NC (cross-source) | {s['n']} | {s['mean']:.3f} | {s['sd']:.3f} | {s['min']:.3f} | {s['max']:.3f} |")
            k2 = f"i2t_vc__cross_{SHORT[other]}_vc"
            s = block[k2]
            lines.append(f"| i2t-VC vs {SHORT[other]} source-VC (cross-source) | {s['n']} | {s['mean']:.3f} | {s['sd']:.3f} | {s['min']:.3f} | {s['max']:.3f} |")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()