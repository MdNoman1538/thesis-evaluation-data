"""
Generate the figure for RQ1 cross-regeneration semantic similarity.
Boxplot of all 6 cells (4 within-task in blue, 2 cross-task in orange).
"""
import json, os
from itertools import combinations, product
import numpy as np
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer

CORPUS = "/Users/noman/Documents/Thesis/evaluation/data/corpus"
OUT_PNG = "/Users/noman/Documents/Thesis/thesis writing/Figures/evaluation/rq1_semsim_cross_runs.png"

def paragraph_from_metadata(meta, condition):
    items = meta.get(condition, {}).get("images", [])
    sentences = [it["sentence"].strip() for it in items if it.get("sentence")]
    if len(sentences) != 5: return None
    return " ".join(sentences)

groups = {("jar","nc"):[], ("jar","vc"):[], ("skii","nc"):[], ("skii","vc"):[]}
for folder in sorted(os.listdir(CORPUS)):
    fp = os.path.join(CORPUS, folder, "metadata.json")
    if not os.path.exists(fp): continue
    task = "skii" if folder.lower().startswith("skii") else ("jar" if folder.lower().startswith("jar") else None)
    if task is None: continue
    with open(fp) as f: meta = json.load(f)
    for cond in ("nc","vc"):
        p = paragraph_from_metadata(meta, cond)
        if p: groups[(task,cond)].append(p)

model = SentenceTransformer('all-MiniLM-L6-v2')
emb = {k: model.encode(v, normalize_embeddings=True) for k,v in groups.items() if v}

def within(v): return [float(np.dot(v[i],v[j])) for i,j in combinations(range(len(v)),2)]
def cross(a,b): return [float(np.dot(a[i],b[j])) for i,j in product(range(len(a)),range(len(b)))]

cells = [
    ("jar abstract × jar abstract\n(within-task)",     within(emb[("jar","nc")]), "within"),
    ("jar concrete × jar concrete\n(within-task)",     within(emb[("jar","vc")]), "within"),
    ("skii abstract × skii abstract\n(within-task)",   within(emb[("skii","nc")]), "within"),
    ("skii concrete × skii concrete\n(within-task)",   within(emb[("skii","vc")]), "within"),
    ("jar abstract × skii abstract\n(cross-task)",     cross(emb[("jar","nc")], emb[("skii","nc")]), "cross"),
    ("jar concrete × skii concrete\n(cross-task)",     cross(emb[("jar","vc")], emb[("skii","vc")]), "cross"),
]

fig, ax = plt.subplots(figsize=(11, 5.5))
positions = list(range(1, len(cells)+1))
data      = [c[1] for c in cells]
labels    = [c[0] for c in cells]
kinds     = [c[2] for c in cells]

bp = ax.boxplot(data, positions=positions, widths=0.55, patch_artist=True,
                medianprops={'color':'black','linewidth':1.6},
                whiskerprops={'color':'#444'},
                capprops={'color':'#444'},
                flierprops={'marker':'o','markersize':3,'markerfacecolor':'#999','markeredgecolor':'#666','alpha':0.6})

within_color = "#4C9AC4"   # blue
cross_color  = "#E08B4A"   # orange
for patch, kind in zip(bp['boxes'], kinds):
    patch.set_facecolor(within_color if kind=="within" else cross_color)
    patch.set_alpha(0.7)
    patch.set_edgecolor('#222')
    patch.set_linewidth(0.8)

# Mean diamonds
for pos, vals in zip(positions, data):
    ax.scatter([pos], [np.mean(vals)], marker='D', s=42, color='white', edgecolors='black', zorder=5, linewidths=0.9)

ax.set_xticks(positions)
ax.set_xticklabels(labels, fontsize=8.5)
ax.set_ylabel("Cosine similarity (SBERT all-MiniLM-L6-v2)", fontsize=10)
ax.set_title("RQ1 cross-regeneration semantic similarity: within-task vs cross-task", fontsize=11)
ax.set_ylim(0.30, 1.0)
ax.grid(axis='y', alpha=0.3, linestyle=':')

# Legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor=within_color, alpha=0.7, edgecolor='#222', label='Within-task pairs (consistency)'),
    Patch(facecolor=cross_color,  alpha=0.7, edgecolor='#222', label='Cross-task pairs (negative control)'),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=9, frameon=True)

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=150, bbox_inches='tight')
print(f"Saved: {OUT_PNG}")
print(f"Cells: {[f'{l.split(chr(10))[0]}: n={len(d)}, mean={np.mean(d):.3f}' for l,d,_ in zip(labels,data,kinds)]}")
