"""
run_31_matched_i2t.py

Generate one image-to-text (i2t) record per source for the matched-n RQ3
analysis. Reads the nc and vc image folders for every source in the corpus,
calls gemini_client.describe_image() sequentially for each image, and saves
the result in a per-source folder.

The output layout is designed for RQ3 directly, not for legacy compatibility:

    evaluation/data/i2t_31matched/
        <source name>/
            descriptions.json    canonical record (nc[5] + vc[5])
            nc.txt               5 human-readable lines S1..S5
            vc.txt               5 human-readable lines S1..S5
        all_descriptions.jsonl   one source per line, easy to stream
        summary.json             completed / failed / timing

Resumable: a source whose descriptions.json already exists is skipped.

Usage:
    python evaluation/scripts/run_31_matched_i2t.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path


APP_DIR = Path("/Users/noman/Documents/Thesis/Apps/StimuliGenerator")
CORPUS_DIR = Path("/Users/noman/Documents/Thesis/evaluation/data/corpus")
OUTPUT_DIR = Path("/Users/noman/Documents/Thesis/evaluation/data/i2t_31matched")
SLOTS = ["S1", "S2", "S3", "S4", "S5"]

INTER_CALL_DELAY_S = 0.5
INTER_SOURCE_DELAY_S = 1.0


sys.path.insert(0, str(APP_DIR))
os.chdir(APP_DIR)  # so config can locate .env

from gemini_client import describe_image, last_model_used  # noqa: E402
from config import GEMINI_MODEL  # noqa: E402


def collect_images(source_dir: Path, condition: str) -> list[tuple[str, Path]]:
    """Return [(slot, image_path)] for condition in S1..S5 order."""
    cond_dir = source_dir / condition
    if not cond_dir.is_dir():
        raise FileNotFoundError(f"Missing {condition}/ in {source_dir}")
    pairs: list[tuple[str, Path]] = []
    for slot in SLOTS:
        matches = sorted(cond_dir.glob(f"*_{condition}_{slot}.png"))
        if not matches:
            raise FileNotFoundError(f"No {condition} {slot} image in {cond_dir}")
        pairs.append((slot, matches[0]))
    return pairs


async def describe_one(image_path: Path) -> str:
    data = image_path.read_bytes()
    return await describe_image(data, mime_type="image/png")


async def process_source(source_dir: Path) -> dict | None:
    source_name = source_dir.name
    out_dir = OUTPUT_DIR / source_name
    record_path = out_dir / "descriptions.json"

    if record_path.is_file():
        print(f"  [skip] {source_name} (descriptions.json exists)")
        return json.loads(record_path.read_text(encoding="utf-8"))

    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"  [run]  {source_name}")

    nc_pairs = collect_images(source_dir, "nc")
    vc_pairs = collect_images(source_dir, "vc")

    nc_items: list[dict] = []
    for slot, image_path in nc_pairs:
        t0 = time.monotonic()
        desc = await describe_one(image_path)
        dt = time.monotonic() - t0
        print(f"    nc {slot} ({dt:4.1f}s) {image_path.name}")
        nc_items.append({"slot": slot, "image": image_path.name, "description": desc})
        await asyncio.sleep(INTER_CALL_DELAY_S)

    vc_items: list[dict] = []
    for slot, image_path in vc_pairs:
        t0 = time.monotonic()
        desc = await describe_one(image_path)
        dt = time.monotonic() - t0
        print(f"    vc {slot} ({dt:4.1f}s) {image_path.name}")
        vc_items.append({"slot": slot, "image": image_path.name, "description": desc})
        await asyncio.sleep(INTER_CALL_DELAY_S)

    record = {
        "source": source_name,
        "model_preferred": GEMINI_MODEL,
        "model_last_used": last_model_used,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "nc": nc_items,
        "vc": vc_items,
    }
    record_path.write_text(
        json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (out_dir / "nc.txt").write_text(
        "\n".join(f"{d['slot']}: {d['description']}" for d in nc_items) + "\n",
        encoding="utf-8",
    )
    (out_dir / "vc.txt").write_text(
        "\n".join(f"{d['slot']}: {d['description']}" for d in vc_items) + "\n",
        encoding="utf-8",
    )
    return record


def write_aggregate(records: list[dict]) -> None:
    """Re-emit a JSONL file with one source per line for the analysis step."""
    with (OUTPUT_DIR / "all_descriptions.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


async def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = sorted(p for p in CORPUS_DIR.iterdir() if p.is_dir())
    print(f"Found {len(sources)} source folders in {CORPUS_DIR}\n")

    records: list[dict] = []
    failed: list[tuple[str, str]] = []
    started_at = time.monotonic()

    for i, source_dir in enumerate(sources, start=1):
        elapsed = time.monotonic() - started_at
        avg_per_done = elapsed / max(i - 1, 1) if i > 1 else 0
        eta_min = avg_per_done * (len(sources) - i + 1) / 60 if i > 1 else 0
        print(f"[{i}/{len(sources)}] elapsed {elapsed/60:4.1f}m  eta ~{eta_min:4.1f}m")
        try:
            record = await process_source(source_dir)
            if record is not None:
                records.append(record)
        except Exception as exc:
            print(f"  ERROR: {exc!r}")
            failed.append((source_dir.name, repr(exc)))
        await asyncio.sleep(INTER_SOURCE_DELAY_S)

    write_aggregate(records)
    (OUTPUT_DIR / "summary.json").write_text(
        json.dumps(
            {
                "total_sources": len(sources),
                "completed": [r["source"] for r in records],
                "failed": failed,
                "elapsed_minutes": round((time.monotonic() - started_at) / 60, 2),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"\nDone. {len(records)}/{len(sources)} sources completed.")
    if failed:
        print(f"{len(failed)} failed:")
        for name, err in failed:
            print(f"  - {name}: {err}")
    print(f"Output at {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())
