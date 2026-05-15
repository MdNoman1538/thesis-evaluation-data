"""
Run the semantic_analyzer's paired-comparison logic on all 30 i2t sessions.

For each session, the script invokes the same code path the analyzer app's
/compare endpoint runs when the user clicks "Compare" in the web UI.
Text A = the i2t-NC stimulus assembled from the 5 NC-image descriptions.
Text B = the i2t-VC stimulus assembled from the 5 VC-image descriptions.

The .mat outputs go into the analyzer's own output_mat/ folder, exactly as
if the user had clicked the web UI thirty times. The .mat file format is
the standard one the app produces (per-slot AL, paired t-test, raw nouns).
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# The semantic_analyzer module lives under the StimuliGenerator app folder.
# The Downloads/ copy has the same code and the output_mat the user has been
# writing to — point to that one so the new outputs sit alongside the existing.
ANALYZER_DIR = Path("/Users/noman/Downloads/ImagenAndDescriptionV1/semantic_analyzer")
sys.path.insert(0, str(ANALYZER_DIR))
os.chdir(ANALYZER_DIR)  # so OUTPUT_DIR resolves to the right place

# Import the analyzer's compare() coroutine + its request model.
import main as analyzer  # type: ignore
from main import compare, CompareRequest  # type: ignore

# Load the 30 i2t sessions (assembled NC/VC text already in i2t_log.jsonl)
I2T_LOG = Path("/Users/noman/Documents/Thesis/evaluation/results/rq3/i2t_log.jsonl")
SHORT = {"jar 13 passed 3.1 pro": "jar13",
         "jar 7 passed 3.1 pro": "jar7",
         "skii 5 passed 3.1 pro": "skii5"}


async def run_one(sess: dict, idx: int) -> dict:
    """Run /compare for one i2t session. Returns a summary record."""
    label = f"i2t_{SHORT[sess['source_folder']]}_run{idx:02d}"
    req = CompareRequest(
        text_a=sess["nc_text"],
        text_b=sess["vc_text"],
        label=label,
        formula="wordnet_min",
    )
    resp = await compare(req)
    # CompareResponse object — extract a few headline numbers for stdout
    return {
        "label": label,
        "source": sess["source_folder"],
        "session": sess["session"],
        "mat_file": resp.mat_file,
        "avg_al_a": resp.avg_al_a,
        "avg_al_b": resp.avg_al_b,
        "delta": (None if resp.avg_al_a is None or resp.avg_al_b is None
                  else round(resp.avg_al_a - resp.avg_al_b, 4)),
        "ttest_t": resp.ttest.t_statistic if resp.ttest else None,
        "ttest_p": resp.ttest.p_value if resp.ttest else None,
        "ttest_mean_diff": resp.ttest.mean_diff if resp.ttest else None,
    }


async def main():
    sessions = [json.loads(l) for l in I2T_LOG.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"Running compare() on {len(sessions)} i2t sessions...\n")

    # Group sessions by source so the per-source run numbering is stable
    by_source: dict[str, list[dict]] = {}
    for s in sessions:
        by_source.setdefault(s["source_folder"], []).append(s)

    summaries = []
    start = time.time()
    for src, rows in by_source.items():
        rows.sort(key=lambda r: r["session"])
        for i, sess in enumerate(rows, start=1):
            summary = await run_one(sess, i)
            summaries.append(summary)
            d = summary["delta"]
            d_str = f"{d:+.4f}" if d is not None else "  ----"
            print(f"  [{summary['label']}]  AL_NC={summary['avg_al_a']:.4f}  "
                  f"AL_VC={summary['avg_al_b']:.4f}  delta={d_str}  "
                  f"→ {Path(summary['mat_file']).name}")

    elapsed = time.time() - start
    print(f"\nDone. {len(summaries)} .mat files written in {elapsed:.1f}s.")

    # Persist the summary as JSON alongside the .mat files
    out_summary = Path("/Users/noman/Documents/Thesis/evaluation/results/rq3/analyzer_i2t_summary.jsonl")
    out_summary.parent.mkdir(parents=True, exist_ok=True)
    with out_summary.open("w", encoding="utf-8") as fh:
        for s in summaries:
            fh.write(json.dumps(s) + "\n")
    print(f"Summary log: {out_summary}")


if __name__ == "__main__":
    asyncio.run(main())