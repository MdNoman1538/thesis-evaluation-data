# Data Layout

This repository is the full evaluation bundle for the thesis *Semantic
Stimuli Generation with Large Language Models: A System for Augmenting
Design Creativity* (Md Abdullah Al Noman, University of Oulu, 2026).
It contains every input file, every script, and every output file
referenced in Chapter 4 of the thesis.

## Directory layout

```
.
├── README.md                       overview + headline numbers
├── DATA.md                         this file
├── scripts/                        deterministic analysis scripts
├── lib/semantic_analyzer/          analyser module (bundled, not external)
├── data/
│   ├── logs/
│   │   ├── stimuli_log.jsonl       text-only generation log
│   │   └── generation_log.jsonl    paired text+image generation log
│   ├── corpus/                     33 stimulus sets (22 jar + 11 skii)
│   └── i2t_sessions/               30 image-to-text sessions
└── results/                        deterministic outputs
    ├── rq1/                        structural pass rates
    ├── rq2/                        textual abstraction (paragraph + slot-wise)
    ├── rq3/                        visual abstraction (i2t round-trip)
    └── imagen_prompts/             prompt-stage dataset (§4.5)
```

## Required inputs by script

| Script | Reads from |
|---|---|
| `evaluate_rq1_rq2_paragraph.py`  | `data/corpus/` |
| `produce_rq2_mat.py`             | `data/corpus/` |
| `evaluate_rq2_slotwise.py`       | `results/rq2/mat_files/` |
| `evaluate_rq3_paragraph.py`      | `data/i2t_sessions/` |
| `produce_rq3_mat.py`             | `results/rq3/analyzer_i2t_summary.jsonl` |
| `evaluate_rq3_semsim.py`         | `results/rq3/i2t_log.jsonl` |
| `build_imagen_prompt_dataset.py` | `data/logs/generation_log.jsonl` |
| `analyze_imagen_prompts.py`      | `data/logs/generation_log.jsonl` |

All scripts import `lib/semantic_analyzer/main.py` for noun extraction,
WordNet AL, and Brysbaert lookup.

## Reproducibility

Every script is deterministic given the same inputs. Running
`scripts/evaluate_rq1_rq2_paragraph.py`, for instance, will rewrite the
files in `results/rq1/` to be byte-identical to what is shipped in the
repository.

The original raw stimulus folders (the same 33 stimulus sets) are also
available as zipped archives in the StimuliGenerator app repository:
<https://github.com/MdNoman1538/StimuliGenerator> (pinned commit `7178012`).
This evaluation repository unpacks them already and removes the zip
duplicates to keep the repository under the practical GitHub size.
