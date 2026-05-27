"""
RQ1 strengthening — pairwise SBERT cosine similarity:
  (a) within-task across regenerations (consistency)
  (b) across tasks (negative control — should be lower)

Outputs per-cell mean ± SD + significance test (within > across).
"""
import json, glob, os, re
from itertools import combinations, product
import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.stats import mannwhitneyu

CORPUS = "/Users/noman/Documents/Thesis/evaluation/data/corpus"

def paragraph_from_metadata(meta, condition):
    items = meta.get(condition, {}).get("images", [])
    sentences = [it["sentence"].strip() for it in items if it.get("sentence")]
    if len(sentences) != 5:
        return None
    return " ".join(sentences)

# Load all runs grouped by (task, condition)
groups = {("jar","nc"):[], ("jar","vc"):[], ("skii","nc"):[], ("skii","vc"):[]}
for folder in sorted(os.listdir(CORPUS)):
    fp = os.path.join(CORPUS, folder, "metadata.json")
    if not os.path.exists(fp): continue
    task = "skii" if folder.lower().startswith("skii") else ("jar" if folder.lower().startswith("jar") else None)
    if task is None: continue
    with open(fp) as f: meta = json.load(f)
    for cond in ("nc","vc"):
        p = paragraph_from_metadata(meta, cond)
        if p: groups[(task,cond)].append((folder, p))

print("Loaded:")
for k,v in groups.items(): print(f"  {k}: {len(v)} paragraphs")

# Embed
model = SentenceTransformer('all-MiniLM-L6-v2')
emb = {}
for k, paras in groups.items():
    if not paras: continue
    texts = [p for _,p in paras]
    vecs = model.encode(texts, normalize_embeddings=True)
    emb[k] = vecs

def cosines_within(vecs):
    return [float(np.dot(vecs[i], vecs[j])) for i,j in combinations(range(len(vecs)), 2)]

def cosines_cross(vA, vB):
    return [float(np.dot(vA[i], vB[j])) for i,j in product(range(len(vA)), range(len(vB)))]

cells = {}
cells["jar NC × jar NC (within-task)"]   = cosines_within(emb[("jar","nc")])
cells["jar VC × jar VC (within-task)"]   = cosines_within(emb[("jar","vc")])
cells["skii NC × skii NC (within-task)"] = cosines_within(emb[("skii","nc")])
cells["skii VC × skii VC (within-task)"] = cosines_within(emb[("skii","vc")])
cells["jar NC × skii NC (cross-task)"]   = cosines_cross(emb[("jar","nc")], emb[("skii","nc")])
cells["jar VC × skii VC (cross-task)"]   = cosines_cross(emb[("jar","vc")], emb[("skii","vc")])

print()
print(f"{'Cell':<42}  {'n':>4}  {'mean':>6}  {'SD':>6}  {'min':>6}  {'max':>6}")
print('-'*78)
for name, vals in cells.items():
    a = np.array(vals)
    print(f"{name:<42}  {len(a):>4}  {a.mean():.4f}  {a.std():.4f}  {a.min():.4f}  {a.max():.4f}")

# Mann-Whitney U: within-task NC > cross-task NC?
def mw(a, b, label):
    u, p = mannwhitneyu(a, b, alternative='greater')
    diff = np.mean(a) - np.mean(b)
    print(f"{label:<55}  Δ={diff:+.4f}  U={u:.0f}  p={p:.2e}")

print()
print("Mann-Whitney U (within > across, one-sided):")
mw(cells["jar NC × jar NC (within-task)"], cells["jar NC × skii NC (cross-task)"], "jar NC within  >  jar-NC vs skii-NC")
mw(cells["skii NC × skii NC (within-task)"], cells["jar NC × skii NC (cross-task)"], "skii NC within  >  skii-NC vs jar-NC")
mw(cells["jar VC × jar VC (within-task)"], cells["jar VC × skii VC (cross-task)"], "jar VC within  >  jar-VC vs skii-VC")
mw(cells["skii VC × skii VC (within-task)"], cells["jar VC × skii VC (cross-task)"], "skii VC within  >  skii-VC vs jar-VC")

# Save JSON
out_path = "/Users/noman/Documents/Thesis/evaluation/results/rq1_semsim_cross_runs.json"
out = {"per_cell": {k: {"n": len(v), "mean": float(np.mean(v)), "sd": float(np.std(v)),
                        "min": float(np.min(v)), "max": float(np.max(v))} for k,v in cells.items()}}
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path,"w") as f: json.dump(out, f, indent=2)
print(f"\nSaved: {out_path}")
