"""
Detailed within-task semantic similarity: per-run centrality + sorted pair distribution.
"""
import json, os
from itertools import combinations
import numpy as np
from sentence_transformers import SentenceTransformer

CORPUS = "/Users/noman/Documents/Thesis/evaluation/data/corpus"

def paragraph_from_metadata(meta, condition):
    items = meta.get(condition, {}).get("images", [])
    sentences = [it["sentence"].strip() for it in items if it.get("sentence")]
    if len(sentences) != 5:
        return None
    return " ".join(sentences)

# Load
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

# Short labels
def short(folder):
    # e.g. "jar 13 passed 3.1 pro" -> "jar13"
    s = folder.lower().replace("skii","skii ").replace("jar","jar ")
    parts = s.split()
    if len(parts) >= 2:
        return f"{parts[0]}{parts[1]}"
    return folder[:10]

model = SentenceTransformer('all-MiniLM-L6-v2')

def analyse(task, cond):
    items = groups[(task,cond)]
    if len(items) < 2: return
    labels = [short(f) for f,_ in items]
    texts  = [p for _,p in items]
    vecs   = model.encode(texts, normalize_embeddings=True)
    n = len(vecs)
    sim = vecs @ vecs.T  # full matrix
    # Per-run centrality: mean similarity to others (exclude self)
    centrality = []
    for i in range(n):
        others = np.concatenate([sim[i,:i], sim[i,i+1:]])
        centrality.append((labels[i], float(np.mean(others))))
    centrality.sort(key=lambda x: -x[1])

    pairs = []
    for i,j in combinations(range(n), 2):
        pairs.append((labels[i], labels[j], float(sim[i,j])))
    pairs.sort(key=lambda x: -x[2])

    arr = np.array([p[2] for p in pairs])
    print(f"\n===== {task.upper()} {cond.upper()} =====  n_runs={n}, n_pairs={len(pairs)}")
    print(f"  mean={arr.mean():.4f}  median={np.median(arr):.4f}  SD={arr.std():.4f}  range=[{arr.min():.4f}, {arr.max():.4f}]")

    print(f"\n  Per-run centrality (mean cosine to other {n-1} runs), sorted high to low:")
    for lab, c in centrality:
        bar = "█" * int(c*60)
        print(f"    {lab:<10}  {c:.4f}  {bar}")

    print(f"\n  Top-5 most similar pairs:")
    for a,b,s in pairs[:5]:
        print(f"    {a:<10} ↔ {b:<10}  {s:.4f}")
    print(f"\n  Bottom-5 least similar pairs:")
    for a,b,s in pairs[-5:]:
        print(f"    {a:<10} ↔ {b:<10}  {s:.4f}")

    # Distribution buckets
    bins = [(0.40,0.50),(0.50,0.60),(0.60,0.65),(0.65,0.70),(0.70,0.75),(0.75,0.80),(0.80,0.85),(0.85,0.90),(0.90,1.00)]
    print(f"\n  Distribution of pair cosines:")
    for lo,hi in bins:
        c = sum(1 for s in arr if lo<=s<hi)
        pct = 100*c/len(arr)
        bar = "▇" * int(pct/2)
        print(f"    [{lo:.2f}, {hi:.2f})  {c:>3}  {pct:5.1f}%  {bar}")

for t in ("jar","skii"):
    for c in ("nc","vc"):
        analyse(t,c)
