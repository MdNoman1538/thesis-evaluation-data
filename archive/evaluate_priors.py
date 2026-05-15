"""
Evaluate prior generated stimuli using the semantic_analyzer's metrics.

Reads every stimuli_log.jsonl across the project's versions, scores each
NC/MC/VC paragraph on word count, sentence count, noun count, mean Brysbaert
concreteness (1-5 scale), and mean WordNet hypernym depth (smaller = more
abstract). Writes one evaluation record per source stimulus to
evaluation_log.jsonl, plus a summary CSV.
"""
from __future__ import annotations

import json
import sys
import statistics
from datetime import datetime
from pathlib import Path

# Allow `import brysbaert_data` and friends from the analyzer folder.
ANALYZER_DIR = Path(
    "/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1/semantic_analyzer"
)
sys.path.insert(0, str(ANALYZER_DIR))

import spacy
from nltk.corpus import wordnet as wn
from brysbaert_data import get_concreteness

NLP = spacy.load("en_core_web_sm")

# Keep settings consistent with semantic_analyzer/main.py
MAX_WN_DEPTH = 20


def wn_depth_min(word: str) -> int | None:
    syns = wn.synsets(word, pos=wn.NOUN)
    if not syns:
        return None
    depths = []
    for s in syns:
        paths = s.hypernym_paths()
        if paths:
            depths.append(min(len(p) for p in paths))
    return min(depths) if depths else None


def extract_nouns(text: str) -> list[str]:
    if not text:
        return []
    doc = NLP(text)
    return [tok.lemma_.lower() for tok in doc if tok.pos_ in ("NOUN", "PROPN")]


def count_sentences(text: str) -> int:
    if not text:
        return 0
    return sum(1 for s in NLP(text).sents if s.text.strip())


def count_words(text: str) -> int:
    if not text:
        return 0
    return sum(1 for tok in NLP(text) if tok.is_alpha)


def safe_mean(values: list[float | int | None]) -> float | None:
    nums = [v for v in values if v is not None]
    return statistics.fmean(nums) if nums else None


def metrics_for(text: str) -> dict:
    """Compute metrics for a single paragraph."""
    if not text or not text.strip():
        return {"present": False}
    nouns = extract_nouns(text)
    bry_scores = [get_concreteness(n) for n in nouns]
    wn_scores = [wn_depth_min(n) for n in nouns]
    return {
        "present": True,
        "word_count": count_words(text),
        "sentence_count": count_sentences(text),
        "noun_count": len(nouns),
        "noun_unique_count": len(set(nouns)),
        "brysbaert_mean": safe_mean(bry_scores),
        "brysbaert_coverage": sum(1 for b in bry_scores if b is not None) / max(1, len(bry_scores)),
        "wordnet_depth_mean": safe_mean(wn_scores),
        "wordnet_coverage": sum(1 for w in wn_scores if w is not None) / max(1, len(wn_scores)),
    }


def evaluate_entry(entry: dict, source: str) -> dict | None:
    """Evaluate one JSONL line; return record or None if no NC/MC/VC payload."""
    nc = entry.get("nc", "")
    mc = entry.get("mc", "")
    vc = entry.get("vc", "")
    if not (nc or mc or vc):
        return None

    nc_m = metrics_for(nc)
    mc_m = metrics_for(mc)
    vc_m = metrics_for(vc)

    record = {
        "source_file": source,
        "timestamp": entry.get("timestamp"),
        "task": entry.get("task"),
        "model": entry.get("model"),
        "format": entry.get("format"),
        "level": entry.get("level"),
        "nc": nc_m,
        "mc": mc_m,
        "vc": vc_m,
    }

    # Convenience: NC/MC/VC abstraction ordering checks where possible.
    bry = [m.get("brysbaert_mean") for m in (nc_m, mc_m, vc_m)]
    wnd = [m.get("wordnet_depth_mean") for m in (nc_m, mc_m, vc_m)]
    if all(b is not None for b in bry):
        record["brysbaert_ordered_nc_lt_mc_lt_vc"] = bry[0] < bry[1] < bry[2]
        record["brysbaert_diff_nc_to_vc"] = bry[2] - bry[0]
    if all(w is not None for w in wnd):
        record["wordnet_ordered_nc_lt_mc_lt_vc"] = wnd[0] < wnd[1] < wnd[2]
        record["wordnet_diff_nc_to_vc"] = wnd[2] - wnd[0]

    # Word-count parity check (Rule 8).
    wcs = [m.get("word_count") for m in (nc_m, mc_m, vc_m) if m.get("word_count")]
    if len(wcs) >= 2:
        record["word_count_spread"] = max(wcs) - min(wcs)

    return record


def find_logs() -> list[Path]:
    roots = [
        Path("/Users/noman/Projects/design stimuli"),
        Path("/Users/noman/Documents/Thesis/Apps/ImagenAndDescriptionV1"),
    ]
    out = []
    for root in roots:
        if not root.exists():
            continue
        for p in root.rglob("stimuli_log.jsonl"):
            out.append(p)
        for p in root.rglob("generation_log.jsonl"):
            out.append(p)
    return out


def main() -> int:
    out_dir = Path("/Users/noman/Documents/Thesis/evaluation")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_log = out_dir / "evaluation_log.jsonl"

    logs = find_logs()
    print(f"Found {len(logs)} log file(s):")
    for p in logs:
        print(f"  - {p}  ({p.stat().st_size:,} bytes)")

    n_total = 0
    n_eval = 0
    n_skipped = 0

    with out_log.open("w", encoding="utf-8") as outf:
        for log_path in logs:
            try:
                lines = log_path.read_text(encoding="utf-8").splitlines()
            except Exception as exc:
                print(f"  ! could not read {log_path}: {exc}")
                continue
            for raw in lines:
                if not raw.strip():
                    continue
                n_total += 1
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError:
                    n_skipped += 1
                    continue
                rec = evaluate_entry(entry, str(log_path))
                if rec is None:
                    n_skipped += 1
                    continue
                outf.write(json.dumps(rec, ensure_ascii=False) + "\n")
                n_eval += 1
                if n_eval % 25 == 0:
                    print(f"  ... {n_eval} stimuli evaluated")

    print(f"\nDone. {n_eval} evaluated, {n_skipped} skipped, {n_total} total lines processed.")
    print(f"Output: {out_log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
