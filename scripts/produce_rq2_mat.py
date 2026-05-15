"""
Run the semantic_analyzer's /compare logic on every NC vs VC source-text
pair from the 33-run participant-facing corpus.

These are the locked-skeleton pairs where slot-wise comparison is
methodologically valid: each pair differs word-for-word only at the 25
noun-phrase positions, so the analyzer's diff-detector lands exactly on
N1..N25 in every run.

Output: 33 .mat files (one per source folder) saved into the analyzer's
output_mat/ directory, named so they are easy to load and aggregate.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path

ANALYZER_DIR = Path("/Users/noman/Downloads/ImagenAndDescriptionV1/semantic_analyzer")
sys.path.insert(0, str(ANALYZER_DIR))
os.chdir(ANALYZER_DIR)

import main as analyzer  # type: ignore
from main import compare, CompareRequest  # type: ignore

CORPUS_DIR = Path("/Users/noman/Documents/Thesis/app output data save")


def slugify(name: str) -> str:
    """folder name -> safe label for the .mat filename."""
    return re.sub(r"[^\w\-]+", "_", name).strip("_")


async def run_one(folder: Path) -> dict:
    meta_path = folder / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    nc_text = (meta.get("nc") or {}).get("stimulus") or ""
    vc_text = (meta.get("vc") or {}).get("stimulus") or ""
    if not nc_text or not vc_text:
        return {"folder": folder.name, "skipped": True}

    label = f"source_{slugify(folder.name)}"
    req = CompareRequest(
        text_a=nc_text,
        text_b=vc_text,
        label=label,
        formula="wordnet_min",
    )
    resp = await compare(req)
    return {
        "folder": folder.name,
        "label": label,
        "mat_file": resp.mat_file,
        "avg_al_nc": resp.avg_al_a,
        "avg_al_vc": resp.avg_al_b,
        "delta": (None if resp.avg_al_a is None or resp.avg_al_b is None
                  else round(resp.avg_al_a - resp.avg_al_b, 4)),
        "ttest_t": resp.ttest.t_statistic if resp.ttest else None,
        "ttest_p": resp.ttest.p_value if resp.ttest else None,
        "ttest_mean_diff": resp.ttest.mean_diff if resp.ttest else None,
    }


async def main():
    folders = sorted([p for p in CORPUS_DIR.iterdir() if p.is_dir()])
    print(f"Running compare() on {len(folders)} source folders...\n")

    summaries = []
    start = time.time()
    for f in folders:
        s = await run_one(f)
        summaries.append(s)
        if s.get("skipped"):
            print(f"  [{f.name}]  SKIPPED (missing nc/vc text)")
            continue
        d = s["delta"]; d_str = f"{d:+.4f}" if d is not None else "  ----"
        print(f"  [{s['label']:55s}]  AL_NC={s['avg_al_nc']:.4f}  "
              f"AL_VC={s['avg_al_vc']:.4f}  delta={d_str}  "
              f"t={s['ttest_t']:+.2f}  p={s['ttest_p']:.2g}")

    elapsed = time.time() - start
    n_ok = sum(1 for s in summaries if not s.get("skipped"))
    print(f"\nDone. {n_ok} .mat files written in {elapsed:.1f}s.")

    out_summary = Path("/Users/noman/Documents/Thesis/evaluation/results/rq1/analyzer_source_summary.jsonl")
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    with out_summary.open("w", encoding="utf-8") as fh:
        for s in summaries:
            fh.write(json.dumps(s) + "\n")
    print(f"Summary log: {out_summary}")


if __name__ == "__main__":
    asyncio.run(main())