"""Shared helper: defines the 31-run trimmed corpus subset (22 jar + 9 skii)."""
import os
from pathlib import Path

CORPUS_ROOT = Path("/Users/noman/Documents/Thesis/evaluation/data/corpus")

# Folders to EXCLUDE from the trimmed corpus.
EXCLUDED_FOLDERS = {
    "Skii 9 new wordnetfailed 2 passed 3.1 pro",
    "skii 10 1 old wordnetfailed 2 passed 3.1 pro",
}

def included_folders():
    out = []
    for d in sorted(CORPUS_ROOT.iterdir()):
        if not d.is_dir(): continue
        if d.name in EXCLUDED_FOLDERS: continue
        out.append(d)
    return out

def is_included(folder_name: str) -> bool:
    return folder_name not in EXCLUDED_FOLDERS

if __name__ == "__main__":
    inc = included_folders()
    print(f"Included: {len(inc)} folders")
    for d in inc:
        print(f"  {d.name}")
    print(f"\nExcluded: {len(EXCLUDED_FOLDERS)}")
    for f in EXCLUDED_FOLDERS:
        print(f"  {f}")
