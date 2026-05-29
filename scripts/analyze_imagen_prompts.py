"""
Comprehensive analysis of LLM-generated imagen prompts:
  1. Per-task split (jar vs skii)
  2. Source-text → imagen-prompt → i2t-description three-stage AL trajectory
  3. Lexical/embedding similarity between paired NC and VC prompts
  4. Brysbaert vs AL divergence on prompts
"""
import json, sys, statistics, math
from pathlib import Path
sys.path.insert(0, "/Users/noman/Documents/Thesis/Apps/StimuliGenerator/semantic_analyzer")
from main import extract_all_nouns, abstraction_score
from brysbaert_data import get_concreteness
import scipy.stats as st

LOG_PATH = "/Users/noman/Documents/Thesis/Apps/StimuliGenerator/generation_log.jsonl"
OUT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/results/imagen_prompts")
OUT_DIR.mkdir(parents=True, exist_ok=True)
# Exclude the 2 sessions corresponding to the dropped skii runs (Skii 9, skii 10)
EXCLUDED_SESSIONS = {"20260508_012334_453481", "20260508_012549_834081"}

# Load
sessions = []
with open(LOG_PATH) as f:
    for line in f:
        d = json.loads(line)
        if d.get("paired_prompts") and len(d["paired_prompts"]) == 5 and d.get("session_id") not in EXCLUDED_SESSIONS:
            sessions.append(d)

def task_kind(task: str) -> str:
    t = task.lower()
    return "skii" if "skii" in t or "skiing" in t or "snowboard" in t else "jar"

def analyse(text):
    nouns = extract_all_nouns(text)
    al = [abstraction_score(l, "wordnet_min") for _, l in nouns]
    br = [get_concreteness(l) for _, l in nouns]
    al = [v for v in al if v is not None]
    br = [v for v in br if v is not None]
    return (statistics.mean(al) if al else None,
            statistics.mean(br) if br else None,
            len(nouns), len(al), len(br))

# Build per-prompt records
rows = []
for si, s in enumerate(sessions):
    task = s.get("frontend_request", {}).get("task", "")
    tk = task_kind(task)
    for pp in s["paired_prompts"]:
        for cond in ("nc", "vc"):
            text = pp.get(f"{cond}_prompt", "")
            al, br, n_n, n_al, n_br = analyse(text)
            rows.append({"si": si, "task": task[:50], "task_kind": tk,
                         "position": pp["position"], "condition": cond,
                         "text": text, "n_words": len(text.split()),
                         "al": al, "brys": br, "n_nouns": n_n})

print("=" * 78)
print("1. PER-TASK SPLIT (jar 22 sessions, skii 10 sessions — 32 total in log)")
print("=" * 78)
print(f"{'Task':<8}{'n_pairs':>10}{'NC AL':>10}{'VC AL':>10}{'Δ AL':>10}{'NC Brys':>10}{'VC Brys':>10}{'Δ Brys':>10}{'NC>VC %':>10}")
print("-" * 88)
for tk in ("jar", "skii"):
    nc_rows = [r for r in rows if r["task_kind"]==tk and r["condition"]=="nc" and r["al"] is not None]
    vc_rows = [r for r in rows if r["task_kind"]==tk and r["condition"]=="vc" and r["al"] is not None]
    by_key_nc = {(r["si"], r["position"]): r for r in nc_rows}
    by_key_vc = {(r["si"], r["position"]): r for r in vc_rows}
    pairs = sorted(set(by_key_nc) & set(by_key_vc))
    al_diffs = [by_key_nc[k]["al"] - by_key_vc[k]["al"] for k in pairs]
    br_diffs = [by_key_nc[k]["brys"] - by_key_vc[k]["brys"] for k in pairs if by_key_nc[k]["brys"] and by_key_vc[k]["brys"]]
    nc_more = sum(1 for d in al_diffs if d > 0)
    nc_al = statistics.mean(r["al"] for r in nc_rows)
    vc_al = statistics.mean(r["al"] for r in vc_rows)
    nc_br = statistics.mean(r["brys"] for r in nc_rows if r["brys"])
    vc_br = statistics.mean(r["brys"] for r in vc_rows if r["brys"])
    print(f"{tk:<8}{len(pairs):>10}{nc_al:>10.4f}{vc_al:>10.4f}{nc_al-vc_al:>+10.4f}{nc_br:>10.3f}{vc_br:>10.3f}{nc_br-vc_br:>+10.3f}{nc_more/len(pairs)*100:>9.1f}%")
    if len(al_diffs) > 1:
        t,p = st.ttest_rel([by_key_nc[k]["al"] for k in pairs], [by_key_vc[k]["al"] for k in pairs])
        m,s_ = statistics.mean(al_diffs), statistics.stdev(al_diffs)
        d = m/s_ if s_ else None
        print(f"        AL paired t={t:+.2f}, p={p:.2e}, d={d:.3f}")
        t,p = st.ttest_rel([by_key_nc[k]["brys"] for k in pairs if by_key_nc[k]["brys"] and by_key_vc[k]["brys"]],
                            [by_key_vc[k]["brys"] for k in pairs if by_key_nc[k]["brys"] and by_key_vc[k]["brys"]])
        m,s_ = statistics.mean(br_diffs), statistics.stdev(br_diffs)
        d = m/s_ if s_ else None
        print(f"        Brys paired t={t:+.2f}, p={p:.2e}, d={d:.3f}")

print()
print("=" * 78)
print("2. THREE-STAGE AL TRAJECTORY: source-text → imagen-prompt → i2t-description")
print("=" * 78)
# Stage 1: source text (from analyzer_source_summary.jsonl), per task
# Stage 2: imagen prompts (computed above) per task
# Stage 3: i2t descriptions (from analyzer_i2t_summary.jsonl), three sources

import json as J
src_by_folder = {}
with open("/Users/noman/Documents/Thesis/evaluation/results/rq2/analyzer_source_summary.jsonl") as f:
    for line in f:
        d = J.loads(line)
        src_by_folder[d["folder"]] = d  # avg_al_nc / avg_al_vc

# Per-task pooled corpus source mean
src_jar  = [v for k,v in src_by_folder.items() if k.lower().startswith("jar")]
src_skii = [v for k,v in src_by_folder.items() if k.lower().startswith(("skii","snow"))]
def avg(values, field):
    vs = [v[field] for v in values]
    return statistics.mean(vs), statistics.stdev(vs), len(vs)

print(f"{'Stage':<22}{'Task':<8}{'n':>5}{'NC AL':>10}{'VC AL':>10}{'NC-VC':>10}")
print("-" * 65)
m,s,n = avg(src_jar, "avg_al_nc");  m2,s2,_ = avg(src_jar, "avg_al_vc")
print(f"{'1. source text':<22}{'jar':<8}{n:>5}{m:>10.4f}{m2:>10.4f}{m-m2:>+10.4f}")
m,s,n = avg(src_skii, "avg_al_nc"); m2,s2,_ = avg(src_skii, "avg_al_vc")
print(f"{'1. source text':<22}{'skii':<8}{n:>5}{m:>10.4f}{m2:>10.4f}{m-m2:>+10.4f}")

# Stage 2 from rows above
for tk in ("jar", "skii"):
    nc = [r["al"] for r in rows if r["task_kind"]==tk and r["condition"]=="nc" and r["al"] is not None]
    vc = [r["al"] for r in rows if r["task_kind"]==tk and r["condition"]=="vc" and r["al"] is not None]
    print(f"{'2. imagen prompt':<22}{tk:<8}{len(nc):>5}{statistics.mean(nc):>10.4f}{statistics.mean(vc):>10.4f}{statistics.mean(nc)-statistics.mean(vc):>+10.4f}")

# Stage 3 from i2t summary
i2t = []
with open("/Users/noman/Documents/Thesis/evaluation/results/rq3/analyzer_i2t_summary.jsonl") as f:
    for line in f:
        i2t.append(J.loads(line))
# Group by source: jar 13 + jar 7 are both jar, skii 5 is skii
for tk_name, src_keys in [("jar (jar 13, jar 7)", ["jar 13", "jar 7"]),
                          ("skii (skii 5)",       ["skii 5"])]:
    matched = [s for s in i2t if any(s["source"].startswith(k) for k in src_keys)]
    nc = [s["avg_al_a"] for s in matched]
    vc = [s["avg_al_b"] for s in matched]
    short = "jar" if tk_name.startswith("jar") else "skii"
    print(f"{'3. i2t description':<22}{short:<8}{len(nc):>5}{statistics.mean(nc):>10.4f}{statistics.mean(vc):>10.4f}{statistics.mean(nc)-statistics.mean(vc):>+10.4f}")

print()
print("Interpretation: the NC-VC gap (last column) at each stage shows where")
print("the abstraction signal is preserved, compressed, or amplified.")

print()
print("=" * 78)
print("3. LEXICAL & EMBEDDING SIMILARITY between paired NC and VC prompts")
print("=" * 78)
# Jaccard token overlap (lowercase, unique tokens)
import re
def tokens(t):
    return set(re.findall(r"\b[a-zA-Z]{2,}\b", t.lower()))
def jaccard(a, b):
    A, B = tokens(a), tokens(b)
    return len(A & B) / len(A | B) if A | B else 0.0
nc_by_key = {(r["si"], r["position"]): r for r in rows if r["condition"]=="nc"}
vc_by_key = {(r["si"], r["position"]): r for r in rows if r["condition"]=="vc"}
pairs = sorted(set(nc_by_key) & set(vc_by_key))
jacc = [jaccard(nc_by_key[k]["text"], vc_by_key[k]["text"]) for k in pairs]
print(f"Jaccard token overlap (NC vs VC) across {len(pairs)} paired prompts:")
print(f"  mean: {statistics.mean(jacc):.4f}    sd: {statistics.stdev(jacc):.4f}")
print(f"  min:  {min(jacc):.4f}    max: {max(jacc):.4f}")
# Per position
for pos in ("S1","S2","S3","S4","S5"):
    js = [jaccard(nc_by_key[k]["text"], vc_by_key[k]["text"]) for k in pairs if k[1]==pos]
    print(f"  {pos}: mean {statistics.mean(js):.4f}")

# Sentence-embedding cosine
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    print("\nLoading sentence-transformers model all-MiniLM-L6-v2…")
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    nc_texts = [nc_by_key[k]["text"] for k in pairs]
    vc_texts = [vc_by_key[k]["text"] for k in pairs]
    nc_emb = model.encode(nc_texts, normalize_embeddings=True, show_progress_bar=False)
    vc_emb = model.encode(vc_texts, normalize_embeddings=True, show_progress_bar=False)
    cos = (nc_emb * vc_emb).sum(axis=1)
    print(f"Cosine similarity (NC vs VC) across {len(pairs)} paired prompts:")
    print(f"  mean: {cos.mean():.4f}    sd: {cos.std(ddof=1):.4f}")
    print(f"  min:  {cos.min():.4f}    max: {cos.max():.4f}")
    for pos in ("S1","S2","S3","S4","S5"):
        idxs = [i for i,k in enumerate(pairs) if k[1]==pos]
        cs = cos[idxs]
        print(f"  {pos}: mean {cs.mean():.4f}")
except Exception as e:
    print(f"(sentence-transformers unavailable: {e})")

print()
print("=" * 78)
print("4. BRYSBAERT vs AL DIVERGENCE on imagen prompts (n=160 paired)")
print("=" * 78)
# Same prompt: AL direction (NC more abstract?) and Brys direction (NC less concrete?)
agree, disagree, partial = 0, 0, 0
for k in pairs:
    a_nc, a_vc = nc_by_key[k]["al"],   vc_by_key[k]["al"]
    b_nc, b_vc = nc_by_key[k]["brys"], vc_by_key[k]["brys"]
    if None in (a_nc,a_vc,b_nc,b_vc): continue
    al_says_nc_more_abstract  = a_nc > a_vc
    brys_says_nc_more_abstract= b_nc < b_vc  # lower brys = more abstract
    if al_says_nc_more_abstract == brys_says_nc_more_abstract:
        agree += 1
    else:
        disagree += 1
print(f"On the per-pair direction question 'is NC more abstract than VC?':")
print(f"  AL and Brysbaert AGREE   : {agree}/{agree+disagree} = {agree/(agree+disagree)*100:.1f}%")
print(f"  AL and Brysbaert DISAGREE: {disagree}/{agree+disagree} = {disagree/(agree+disagree)*100:.1f}%")
# Correlation between per-pair AL delta and per-pair Brys delta
al_d = [nc_by_key[k]["al"]   - vc_by_key[k]["al"]   for k in pairs if nc_by_key[k]["al"]   and vc_by_key[k]["al"]   and nc_by_key[k]["brys"] and vc_by_key[k]["brys"]]
br_d = [nc_by_key[k]["brys"] - vc_by_key[k]["brys"] for k in pairs if nc_by_key[k]["al"]   and vc_by_key[k]["al"]   and nc_by_key[k]["brys"] and vc_by_key[k]["brys"]]
r, p = st.pearsonr(al_d, br_d)
print(f"Pearson(AL delta, Brys delta) = {r:+.3f}, p = {p:.2e}")
print(f"  Negative r is expected if NC more abstract on AL coincides with NC less concrete on Brys.")

# Persist
out = {"per_prompt_n": len(rows), "n_pairs": len(pairs)}
with open(OUT_DIR / "summary.json", "w") as f:
    json.dump(out, f, indent=2)
print(f"\nWritten: {OUT_DIR / 'summary.json'}")
