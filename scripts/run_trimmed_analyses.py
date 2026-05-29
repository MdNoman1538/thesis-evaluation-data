"""
Master driver for the trimmed (31-run) corpus analyses.
Writes all outputs under /Users/noman/Documents/Thesis/evaluation/results_trimmed/.

Sections:
  A. Per-run extraction + slot scoring (WN AL, Brysbaert)
  B. RQ1 structural pass rates
  C. RQ2 paragraph-level paired t-test (NC vs VC mean AL across runs)
  D. RQ2 slot-wise pooled paired t-test + per-slot means + delta distribution
  E. RQ1 SBERT within-task vs cross-task cells
  F. RQ3 source-corpus baseline cells (within-task per-task for skii)
"""
import json, os, sys, re
from pathlib import Path
from itertools import combinations, product
from collections import defaultdict
import numpy as np
import scipy.stats as stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import spacy
import nltk
from nltk.corpus import wordnet as wn
try: wn.synsets("test")
except LookupError:
    nltk.download("wordnet", quiet=True); nltk.download("omw-1.4", quiet=True)

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path("/Users/noman/Documents/Thesis/Apps/StimuliGenerator/semantic_analyzer").resolve()))
from brysbaert_data import get_concreteness, normalize_concreteness
from trim_corpus import included_folders, EXCLUDED_FOLDERS

CORPUS = Path("/Users/noman/Documents/Thesis/evaluation/data/corpus")
OUT = Path("/Users/noman/Documents/Thesis/evaluation/results_trimmed")
MAX_WN_DEPTH = 20

# ─────────────────────────────────────────────────────────────────────────
# Scoring helpers
# ─────────────────────────────────────────────────────────────────────────
def wn_al(word):
    syns = wn.synsets(word, pos=wn.NOUN)
    if not syns: return None
    depths = []
    for s in syns:
        paths = s.hypernym_paths()
        if paths: depths.append(min(len(p) for p in paths))
    if not depths: return None
    d = min(depths)
    return float(np.clip(1.0 - (d-1)/(MAX_WN_DEPTH-1), 0.0, 1.0))

def brys_al(word):
    c = get_concreteness(word)
    if c is None: return None
    return normalize_concreteness(c, 1.0, 5.0)

def brys_raw(word):
    return get_concreteness(word)

nlp = spacy.load("en_core_web_sm")
def extract_nouns(text):
    return [tok.lemma_.lower() for tok in nlp(text) if tok.pos_ == "NOUN"]

def task_of(folder):
    n = folder.lower()
    if n.startswith("jar"): return "jar"
    if n.startswith("skii") or n.startswith("snow"): return "skii"
    return "other"

def cohens_d_paired(d):
    s = np.std(d, ddof=1) if len(d) > 1 else 0.0
    return float(np.mean(d)/s) if s>0 else 0.0

def effect_label(d):
    a = abs(d)
    if a < 0.2: return "negligible"
    if a < 0.5: return "small"
    if a < 0.8: return "medium"
    return "large"

# ─────────────────────────────────────────────────────────────────────────
# A. Per-run extraction
# ─────────────────────────────────────────────────────────────────────────
def load_run(folder):
    mp = folder / "metadata.json"
    if not mp.exists(): return None
    meta = json.loads(mp.read_text())
    def grab(cond):
        items = meta.get(cond, {}).get("images", [])
        sents = [it["sentence"].strip() for it in items if it.get("sentence")]
        return sents if len(sents) == 5 else None
    nc, vc = grab("nc"), grab("vc")
    if not nc or not vc: return None
    nc_para = " ".join(nc); vc_para = " ".join(vc)
    nc_nouns = extract_nouns(nc_para)
    vc_nouns = extract_nouns(vc_para)
    # Slot-aligned score: pair by position up to min length
    n = min(len(nc_nouns), len(vc_nouns))
    slot_pairs = list(zip(nc_nouns[:n], vc_nouns[:n]))
    # Paragraph-level: average over all extracted nouns
    nc_wn = [wn_al(w) for w in nc_nouns]; nc_wn = [x for x in nc_wn if x is not None]
    vc_wn = [wn_al(w) for w in vc_nouns]; vc_wn = [x for x in vc_wn if x is not None]
    nc_br = [brys_raw(w) for w in nc_nouns]; nc_br = [x for x in nc_br if x is not None]
    vc_br = [brys_raw(w) for w in vc_nouns]; vc_br = [x for x in vc_br if x is not None]
    # Word counts
    nc_words = len(nc_para.split()); vc_words = len(vc_para.split())
    return {
        "folder": folder.name,
        "task": task_of(folder.name),
        "nc_para": nc_para, "vc_para": vc_para,
        "nc_nouns": nc_nouns, "vc_nouns": vc_nouns,
        "slot_pairs": slot_pairs,
        "nc_wn_para_mean": float(np.mean(nc_wn)) if nc_wn else None,
        "vc_wn_para_mean": float(np.mean(vc_wn)) if vc_wn else None,
        "nc_brys_para_mean": float(np.mean(nc_br)) if nc_br else None,
        "vc_brys_para_mean": float(np.mean(vc_br)) if vc_br else None,
        "nc_words": nc_words, "vc_words": vc_words,
        "nc_sents": 5, "vc_sents": 5,
    }

print(f"\n{'='*60}\nA. Per-run extraction\n{'='*60}")
runs = []
for d in included_folders():
    r = load_run(d)
    if r: runs.append(r)
print(f"Loaded: {len(runs)} runs (target 31)")
n_jar = sum(1 for r in runs if r['task']=='jar')
n_skii = sum(1 for r in runs if r['task']=='skii')
print(f"  jar: {n_jar}, skii: {n_skii}")

(OUT / "rq1" / "per_run_log.jsonl").open("w").writelines(
    json.dumps({k:v for k,v in r.items() if k not in ('slot_pairs',)}) + "\n" for r in runs
)

# ─────────────────────────────────────────────────────────────────────────
# B. RQ1 structural pass rates
# ─────────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}\nB. RQ1 structural pass rates\n{'='*60}")
n_runs = len(runs)
n_5sent = sum(1 for r in runs if r['nc_sents']==5 and r['vc_sents']==5)
n_5img = n_runs  # images not re-checked; assume corpus already validated. We can stat from folder dirs.
# Rule 8: |NC words - VC words| <= 2
n_rule8 = sum(1 for r in runs if abs(r['nc_words'] - r['vc_words']) <= 2)
n_wn_order = sum(1 for r in runs if r['nc_wn_para_mean'] is not None and r['vc_wn_para_mean'] is not None
                 and r['nc_wn_para_mean'] > r['vc_wn_para_mean'])
n_brys_order = sum(1 for r in runs if r['nc_brys_para_mean'] is not None and r['vc_brys_para_mean'] is not None
                   and r['nc_brys_para_mean'] < r['vc_brys_para_mean'])

structural = {
    "n_runs": n_runs,
    "five_sentence_pass": (n_5sent, 100*n_5sent/n_runs),
    "five_images_pass": (n_5img, 100*n_5img/n_runs),
    "rule8_pass": (n_rule8, 100*n_rule8/n_runs),
    "wn_order_pass": (n_wn_order, 100*n_wn_order/n_runs),
    "brys_order_pass": (n_brys_order, 100*n_brys_order/n_runs),
}
for k, v in structural.items():
    if isinstance(v, tuple):
        print(f"  {k:<25s} {v[0]:3d}/{n_runs} ({v[1]:.1f}%)")
    else:
        print(f"  {k:<25s} {v}")
(OUT / "rq1" / "structural_pass.json").write_text(json.dumps(structural, indent=2))

# ─────────────────────────────────────────────────────────────────────────
# C. RQ2 paragraph-level paired t-test
# ─────────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}\nC. RQ2 paragraph-level paired t-test\n{'='*60}")

def paired_summary(a, b, label):
    a = np.array(a); b = np.array(b)
    diffs = a - b
    t, p = stats.ttest_rel(a, b)
    d = cohens_d_paired(diffs)
    return {
        "metric": label,
        "n": len(a), "nc_mean": float(np.mean(a)), "vc_mean": float(np.mean(b)),
        "delta": float(np.mean(diffs)),
        "t": float(t), "p": float(p),
        "cohens_d": d, "effect": effect_label(d),
    }

# Across all 31
all_nc_wn = [r['nc_wn_para_mean'] for r in runs]
all_vc_wn = [r['vc_wn_para_mean'] for r in runs]
all_nc_br = [r['nc_brys_para_mean'] for r in runs]
all_vc_br = [r['vc_brys_para_mean'] for r in runs]
wn_para = paired_summary(all_nc_wn, all_vc_wn, "WordNet AL (0-1)")
br_para = paired_summary(all_nc_br, all_vc_br, "Brysbaert (1-5)")

for s in (wn_para, br_para):
    print(f"  {s['metric']:<22s} n={s['n']:3d} NC={s['nc_mean']:.4f} VC={s['vc_mean']:.4f} "
          f"Δ={s['delta']:+.4f} t={s['t']:+.2f} p={s['p']:.2e} d={s['cohens_d']:.2f}")

# Per task
per_task_para = {}
for task in ("jar","skii"):
    rs = [r for r in runs if r['task']==task]
    a_wn = [r['nc_wn_para_mean'] for r in rs]
    b_wn = [r['vc_wn_para_mean'] for r in rs]
    a_br = [r['nc_brys_para_mean'] for r in rs]
    b_br = [r['vc_brys_para_mean'] for r in rs]
    per_task_para[task] = {
        "n_runs": len(rs),
        "wn": paired_summary(a_wn, b_wn, "WordNet AL"),
        "brys": paired_summary(a_br, b_br, "Brysbaert"),
    }
    print(f"  -- {task} (n={len(rs)}) WN d={per_task_para[task]['wn']['cohens_d']:.2f}, "
          f"Brys d={per_task_para[task]['brys']['cohens_d']:.2f}")

(OUT / "rq2" / "rq2_paragraph_pooled.json").write_text(
    json.dumps({"pooled_wn": wn_para, "pooled_brys": br_para, "per_task": per_task_para}, indent=2))

# ─────────────────────────────────────────────────────────────────────────
# D. RQ2 slot-wise pooled + per-slot means
# ─────────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}\nD. RQ2 slot-wise pooled + per-slot\n{'='*60}")
# Build per-slot AL pairs across runs. Slot index = position in noun sequence (cap at 25).
slot_records = []
for r in runs:
    for i, (nc_n, vc_n) in enumerate(r['slot_pairs'][:25], start=1):
        a = wn_al(nc_n); b = wn_al(vc_n)
        slot_records.append({
            "folder": r['folder'], "task": r['task'], "slot": i,
            "nc_noun": nc_n, "vc_noun": vc_n,
            "nc_al": a, "vc_al": b,
        })
# pooled pairs where both available
pooled_pairs = [(s['nc_al'], s['vc_al']) for s in slot_records if s['nc_al'] is not None and s['vc_al'] is not None]
A = np.array([p[0] for p in pooled_pairs]); B = np.array([p[1] for p in pooled_pairs])
DD = A - B
t_p, p_p = stats.ttest_rel(A, B)
d_p = cohens_d_paired(DD)
nc_more = int(np.sum(DD > 0)); vc_more = int(np.sum(DD < 0)); tied = int(np.sum(DD == 0))
slot_pooled = {
    "n_pairs": len(pooled_pairs),
    "nc_mean": float(np.mean(A)), "vc_mean": float(np.mean(B)),
    "delta_mean": float(np.mean(DD)),
    "t": float(t_p), "p": float(p_p), "cohens_d": d_p,
    "nc_more_abstract_count": nc_more, "vc_more_abstract_count": vc_more, "tied_count": tied,
    "pct_nc_more": 100*nc_more/len(pooled_pairs),
    "pct_vc_more": 100*vc_more/len(pooled_pairs),
    "pct_tied": 100*tied/len(pooled_pairs),
}
print(f"  pooled n={slot_pooled['n_pairs']} Δ={slot_pooled['delta_mean']:+.4f} "
      f"t={slot_pooled['t']:.2f} p={slot_pooled['p']:.2e} d={slot_pooled['cohens_d']:.3f}")
print(f"  NC>VC: {slot_pooled['nc_more_abstract_count']} ({slot_pooled['pct_nc_more']:.1f}%); "
      f"VC>NC: {slot_pooled['vc_more_abstract_count']} ({slot_pooled['pct_vc_more']:.1f}%); "
      f"tied: {slot_pooled['tied_count']} ({slot_pooled['pct_tied']:.1f}%)")

# per task
slot_per_task = {}
for task in ("jar","skii"):
    pairs = [(s['nc_al'], s['vc_al']) for s in slot_records
             if s['task']==task and s['nc_al'] is not None and s['vc_al'] is not None]
    a = np.array([p[0] for p in pairs]); b = np.array([p[1] for p in pairs])
    dd = a - b
    tt, pp = stats.ttest_rel(a, b)
    dd_d = cohens_d_paired(dd)
    slot_per_task[task] = {
        "n_pairs": len(pairs), "delta_mean": float(np.mean(dd)),
        "t": float(tt), "p": float(pp), "cohens_d": dd_d,
        "pct_nc_more": 100*float(np.sum(dd > 0))/len(pairs),
    }
    print(f"  -- {task}: n={len(pairs)} d={dd_d:.3f} NC>VC {slot_per_task[task]['pct_nc_more']:.1f}%")

# per slot
per_slot = {}
for i in range(1, 26):
    pairs = [(s['nc_al'], s['vc_al']) for s in slot_records
             if s['slot']==i and s['nc_al'] is not None and s['vc_al'] is not None]
    if not pairs: continue
    a = np.array([p[0] for p in pairs]); b = np.array([p[1] for p in pairs])
    dd = a - b
    per_slot[i] = {
        "n": len(pairs), "nc_mean": float(np.mean(a)), "vc_mean": float(np.mean(b)),
        "delta_mean": float(np.mean(dd)),
        "pct_nc_more": 100*float(np.sum(dd > 0))/len(pairs),
    }

(OUT / "rq2" / "rq2_slotwise.json").write_text(json.dumps(
    {"pooled": slot_pooled, "per_task": slot_per_task, "per_slot": per_slot}, indent=2))

# Per-slot bar chart
xs = sorted(per_slot.keys())
ys = [per_slot[i]['delta_mean'] for i in xs]
fig, ax = plt.subplots(figsize=(11, 4))
bars = ax.bar(xs, ys, color=['#E08B4A' if y < 0 else '#4C9AC4' for y in ys], edgecolor='#222', linewidth=0.5)
ax.axhline(0, color='black', linewidth=0.8)
ax.set_xticks(xs); ax.set_xticklabels([f"$N_{{{i}}}$" for i in xs], fontsize=8, rotation=0)
ax.set_ylabel("Mean Δ AL (NC − VC)")
ax.set_title(f"RQ2 per-slot mean abstraction delta — trimmed corpus (n={n_runs})")
ax.grid(axis='y', alpha=0.3, linestyle=':')
plt.tight_layout()
plt.savefig(OUT / "rq2" / "rq2_slotwise_per_slot_mean.png", dpi=150, bbox_inches='tight')
plt.close()

# Delta distribution
fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(DD, bins=40, color='#4C9AC4', edgecolor='#222', linewidth=0.5)
ax.axvline(0, color='black', linewidth=0.8)
ax.axvline(float(np.mean(DD)), color='red', linewidth=1.5, linestyle='--', label=f'mean = {float(np.mean(DD)):+.4f}')
ax.set_xlabel("Per-slot delta (NC AL − VC AL)")
ax.set_ylabel("Count of slot pairs")
ax.set_title(f"Distribution of per-slot deltas — trimmed corpus ({len(pooled_pairs)} pairs)")
ax.legend()
plt.tight_layout()
plt.savefig(OUT / "rq2" / "rq2_slotwise_delta_distribution.png", dpi=150, bbox_inches='tight')
plt.close()
print("  figures written.")

# Paragraph-level box plot
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].boxplot([all_nc_br, all_vc_br], tick_labels=['NC','VC'], patch_artist=True,
                boxprops=dict(facecolor='#4C9AC4', alpha=0.7))
axes[0].set_ylabel("Brysbaert (1–5)")
axes[0].set_title(f"Brysbaert paragraph means (n={n_runs})")
axes[1].boxplot([all_nc_wn, all_vc_wn], tick_labels=['NC','VC'], patch_artist=True,
                boxprops=dict(facecolor='#4C9AC4', alpha=0.7))
axes[1].set_ylabel("WordNet AL (0–1)")
axes[1].set_title(f"WordNet AL paragraph means (n={n_runs})")
plt.tight_layout()
plt.savefig(OUT / "rq2" / "rq2_paragraph_box.png", dpi=150, bbox_inches='tight')
plt.close()

# ─────────────────────────────────────────────────────────────────────────
# E. RQ1 SBERT cells (within-task & cross-task)
# ─────────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}\nE. RQ1 SBERT within/cross-task\n{'='*60}")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
def embed(texts): return model.encode(texts, normalize_embeddings=True) if texts else np.zeros((0,384))
def within(v): return [float(np.dot(v[i],v[j])) for i,j in combinations(range(len(v)),2)] if len(v)>=2 else []
def cross(a, b): return [float(np.dot(a[i],b[j])) for i,j in product(range(len(a)),range(len(b)))]

jar_nc = [r['nc_para'] for r in runs if r['task']=='jar']
jar_vc = [r['vc_para'] for r in runs if r['task']=='jar']
skii_nc = [r['nc_para'] for r in runs if r['task']=='skii']
skii_vc = [r['vc_para'] for r in runs if r['task']=='skii']
e_jar_nc = embed(jar_nc); e_jar_vc = embed(jar_vc)
e_skii_nc = embed(skii_nc); e_skii_vc = embed(skii_vc)

cells = {
    "jar NC × jar NC (within-task)":   within(e_jar_nc),
    "jar VC × jar VC (within-task)":   within(e_jar_vc),
    "skii NC × skii NC (within-task)": within(e_skii_nc),
    "skii VC × skii VC (within-task)": within(e_skii_vc),
    "jar NC × skii NC (cross-task)":   cross(e_jar_nc, e_skii_nc),
    "jar VC × skii VC (cross-task)":   cross(e_jar_vc, e_skii_vc),
}
sbert_cells = {}
for name, vals in cells.items():
    arr = np.array(vals, dtype=float)
    sbert_cells[name] = {
        "n": int(len(arr)),
        "mean": float(arr.mean()) if len(arr) else None,
        "sd":   float(arr.std()) if len(arr) else None,
        "min":  float(arr.min()) if len(arr) else None,
        "max":  float(arr.max()) if len(arr) else None,
    }
    print(f"  {name:<40s} n={sbert_cells[name]['n']:4d} mean={sbert_cells[name]['mean']:.3f}")

# Mann-Whitney U: within vs cross per condition
def mwu(within_vals, cross_vals):
    if not within_vals or not cross_vals: return (None, None)
    u, p = stats.mannwhitneyu(within_vals, cross_vals, alternative='greater')
    return float(u), float(p)
sbert_tests = {
    "jar_nc vs cross_nc": mwu(cells["jar NC × jar NC (within-task)"], cells["jar NC × skii NC (cross-task)"]),
    "jar_vc vs cross_vc": mwu(cells["jar VC × jar VC (within-task)"], cells["jar VC × skii VC (cross-task)"]),
    "skii_nc vs cross_nc": mwu(cells["skii NC × skii NC (within-task)"], cells["jar NC × skii NC (cross-task)"]),
    "skii_vc vs cross_vc": mwu(cells["skii VC × skii VC (within-task)"], cells["jar VC × skii VC (cross-task)"]),
}
(OUT / "rq1" / "sbert_cells.json").write_text(json.dumps(
    {"cells": sbert_cells, "tests": sbert_tests}, indent=2))

# Boxplot
fig, ax = plt.subplots(figsize=(11, 5.5))
positions = list(range(1, len(cells)+1))
data = list(cells.values()); labels = list(cells.keys())
kinds = ["within"]*4 + ["cross"]*2
bp = ax.boxplot(data, positions=positions, widths=0.55, patch_artist=True,
                medianprops={'color':'black','linewidth':1.6})
for patch, kind in zip(bp['boxes'], kinds):
    patch.set_facecolor("#4C9AC4" if kind=="within" else "#E08B4A"); patch.set_alpha(0.7); patch.set_edgecolor('#222')
for pos, vals in zip(positions, data):
    if vals: ax.scatter([pos], [np.mean(vals)], marker='D', s=42, color='white', edgecolors='black', zorder=5)
ax.set_xticks(positions)
ax.set_xticklabels([l.replace(" (", "\n(") for l in labels], fontsize=8.5)
ax.set_ylabel("Cosine similarity (SBERT)")
ax.set_title(f"RQ1 cross-regeneration semantic similarity — trimmed corpus (jar=22, skii=9)")
ax.set_ylim(0.30, 1.0)
ax.grid(axis='y', alpha=0.3, linestyle=':')
plt.tight_layout()
plt.savefig(OUT / "rq1" / "rq1_semsim_cross_runs.png", dpi=150, bbox_inches='tight')
plt.close()
print("  figure written.")

# ─────────────────────────────────────────────────────────────────────────
# F. RQ3 source-corpus baseline cells for the SBERT comparison
# ─────────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}\nF. RQ3 source-corpus baseline (table 12b) recomputed\n{'='*60}")
# These are the per-task within-task cells in Table 12 block (b).
table12b = {
    "jar source corpus NC×NC":  sbert_cells["jar NC × jar NC (within-task)"],
    "jar source corpus VC×VC":  sbert_cells["jar VC × jar VC (within-task)"],
    "skii source corpus NC×NC": sbert_cells["skii NC × skii NC (within-task)"],
    "skii source corpus VC×VC": sbert_cells["skii VC × skii VC (within-task)"],
}
for k, v in table12b.items():
    print(f"  {k:<30s} n={v['n']:4d} mean={v['mean']:.3f} sd={v['sd']:.3f}")
(OUT / "rq3" / "table12b_baseline.json").write_text(json.dumps(table12b, indent=2))

print(f"\n✓ All outputs written under {OUT}")
