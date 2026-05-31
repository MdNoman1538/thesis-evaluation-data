"""
evaluate_rq3_i2t_slotwise.py

Slot-wise pairwise i2t analysis. For each of the 31 generations and each of
the 5 slots, score the NC and VC descriptions individually on WordNet AL and
Brysbaert concreteness, then form the paired comparison NC_Si vs VC_Si.

Aggregations reported:
  - Per-generation: 5 slot pairs per generation, with mean delta and the count
    of slots where NC > VC out of 5.
  - Corpus-wide: 155 pooled slot pairs with paired t-test on AL and Brysbaert.

Inputs:
  i2t_31matched/<source>/descriptions.json    (one record per source)

Outputs (evaluation/data/i2t_31matched_slotwise/):
  per_pair.jsonl       155 records, one per (source, slot)
  per_generation.json  31 records, one per source, with 5 pair deltas and gen summary
  summary.json         corpus-wide pooled stats
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
OUT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/data/i2t_31matched_slotwise")
SLOTS = ["S1", "S2", "S3", "S4", "S5"]
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
        "al_mean": statistics.fmean(al) if al else None,
        "brys_mean": statistics.fmean(bry) if bry else None,
    }


def paired_t(values: list[float]) -> dict:
    n = len(values)
    if n < 2:
        return {"n": n, "mean": None, "sd": None, "t": None, "p": None, "cohen_d": None,
                "above_zero": None}
    m = statistics.fmean(values)
    s = statistics.stdev(values)
    se = s / (n ** 0.5)
    t = m / se if se else float("inf")
    p = 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))
    d = m / s if s else float("inf")
    return {
        "n": n,
        "mean": m,
        "sd": s,
        "t": t,
        "p": p,
        "cohen_d": d,
        "above_zero": sum(1 for v in values if v > 0),
    }


def task_for(source_name: str) -> str:
    if source_name.startswith("jar"):
        return "jar"
    if source_name.startswith("skii") or source_name.startswith("snow"):
        return "skii"
    return "other"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sources = sorted(p for p in I2T_DIR.iterdir() if p.is_dir())
    print(f"Found {len(sources)} sources")

    per_pair_records: list[dict] = []
    per_generation: list[dict] = []

    # Display ordering matches the per-run text-summary table
    jar_count = 0
    skii_count = 0

    for src_dir in sources:
        rec_path = src_dir / "descriptions.json"
        if not rec_path.is_file():
            print(f"  skip {src_dir.name}")
            continue
        rec = json.loads(rec_path.read_text(encoding="utf-8"))
        src_name = rec["source"]
        task = task_for(src_name)

        if task == "jar":
            jar_count += 1
            display_run = f"jar {jar_count}"
        else:
            skii_count += 1
            display_run = f"skii {skii_count}"

        nc_by_slot = {d["slot"]: d for d in rec["nc"]}
        vc_by_slot = {d["slot"]: d for d in rec["vc"]}

        gen_pair_deltas_al: list[float] = []
        gen_pair_deltas_brys: list[float] = []
        gen_pair_details: list[dict] = []

        for slot in SLOTS:
            nc_desc = nc_by_slot.get(slot, {}).get("description", "")
            vc_desc = vc_by_slot.get(slot, {}).get("description", "")
            nc_m = metrics_for(nc_desc)
            vc_m = metrics_for(vc_desc)
            nc_al = nc_m["al_mean"]
            vc_al = vc_m["al_mean"]
            nc_brys = nc_m["brys_mean"]
            vc_brys = vc_m["brys_mean"]
            delta_al = (nc_al - vc_al) if (nc_al is not None and vc_al is not None) else None
            delta_brys = (nc_brys - vc_brys) if (nc_brys is not None and vc_brys is not None) else None

            pair_rec = {
                "source": src_name,
                "display_run": display_run,
                "task": task,
                "slot": slot,
                "nc_al": nc_al, "vc_al": vc_al, "delta_al": delta_al,
                "nc_brys": nc_brys, "vc_brys": vc_brys, "delta_brys": delta_brys,
                "nc_noun_count": nc_m["noun_count"], "vc_noun_count": vc_m["noun_count"],
                "nc_description": nc_desc, "vc_description": vc_desc,
            }
            per_pair_records.append(pair_rec)
            gen_pair_details.append({
                "slot": slot,
                "nc_al": nc_al, "vc_al": vc_al, "delta_al": delta_al,
                "nc_brys": nc_brys, "vc_brys": vc_brys, "delta_brys": delta_brys,
            })
            if delta_al is not None:
                gen_pair_deltas_al.append(delta_al)
            if delta_brys is not None:
                gen_pair_deltas_brys.append(delta_brys)

        slots_with_data_al = sum(1 for d in gen_pair_deltas_al)
        nc_more_abstract_al = sum(1 for d in gen_pair_deltas_al if d > 0)

        per_generation.append({
            "source": src_name,
            "display_run": display_run,
            "task": task,
            "n_slots_scored_al": slots_with_data_al,
            "nc_more_abstract_count_al": nc_more_abstract_al,
            "mean_delta_al": statistics.fmean(gen_pair_deltas_al) if gen_pair_deltas_al else None,
            "mean_delta_brys": statistics.fmean(gen_pair_deltas_brys) if gen_pair_deltas_brys else None,
            "slot_pairs": gen_pair_details,
        })

    # Corpus-wide pooled
    all_delta_al = [r["delta_al"] for r in per_pair_records if r["delta_al"] is not None]
    all_delta_brys = [r["delta_brys"] for r in per_pair_records if r["delta_brys"] is not None]

    summary = {
        "n_generations": len(per_generation),
        "n_slot_pairs_attempted": len(per_pair_records),
        "n_slot_pairs_scored_al": len(all_delta_al),
        "n_slot_pairs_scored_brys": len(all_delta_brys),
        "corpus_pooled_al": paired_t(all_delta_al),
        "corpus_pooled_brys": paired_t(all_delta_brys),
    }

    # Write outputs
    with (OUT_DIR / "per_pair.jsonl").open("w", encoding="utf-8") as f:
        for r in per_pair_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (OUT_DIR / "per_generation.json").write_text(
        json.dumps(per_generation, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (OUT_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Print headline
    print("\n=== Corpus-wide pooled (155 pairs) ===")
    al = summary["corpus_pooled_al"]
    print(f"WordNet AL: n={al['n']}, mean Δ={al['mean']:+.4f}, sd={al['sd']:.4f}, "
          f"t={al['t']:+.2f}, p={al['p']:.2e}, d={al['cohen_d']:.2f}, NC>VC in {al['above_zero']}/{al['n']}")
    brys = summary["corpus_pooled_brys"]
    print(f"Brysbaert : n={brys['n']}, mean Δ={brys['mean']:+.4f}, sd={brys['sd']:.4f}, "
          f"t={brys['t']:+.2f}, p={brys['p']:.2e}, d={brys['cohen_d']:.2f}, NC>VC in {brys['above_zero']}/{brys['n']}")

    print("\n=== Per-generation (5 slot pairs each) ===")
    print(f"{'#':>3} {'gen':<10} {'NC>VC':>6}  {'meanΔAL':>10}  {'meanΔBrys':>10}")
    for i, g in enumerate(per_generation, start=1):
        mal = g['mean_delta_al']
        mbr = g['mean_delta_brys']
        nca = g['nc_more_abstract_count_al']
        n   = g['n_slots_scored_al']
        print(f"{i:>3} {g['display_run']:<10} {nca:>2}/{n:<2}  "
              f"{(f'{mal:+.4f}' if mal is not None else 'n/a'):>10}  "
              f"{(f'{mbr:+.4f}' if mbr is not None else 'n/a'):>10}")

    print(f"\nOutput at {OUT_DIR}")


if __name__ == "__main__":
    main()
