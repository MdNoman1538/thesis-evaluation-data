# Data Layout

This repository is the full evaluation bundle for the thesis *Semantic
and Visual Stimuli Generation with Large Language Models: A System for
Augmenting Design Creativity* (Md Abdullah Al Noman, University of Oulu,
2026). It contains every input file, every script, and every output file
referenced in Chapter 4 of the thesis.

## Directory layout

```
.
├── README.md                          overview + headline numbers
├── DATA.md                            this file
├── scripts/                           deterministic analysis scripts
├── lib/semantic_analyzer/             analyser module (bundled, not external)
├── data/
│   ├── logs/
│   │   ├── stimuli_log.jsonl          text-only generation log
│   │   └── generation_log.jsonl       paired text+image generation log
│   ├── corpus/                        31 stimulus generations (22 jar + 9 skii)
│   ├── i2t_31matched/                 31 image-to-text descriptions (one
│   │                                  redescription per source generation)
│   └── i2t_31matched_slotwise/        per-pair and per-generation outputs
│                                      of the sentence-position pairwise analysis
└── results/                           deterministic outputs
    ├── rq1/                           structural pass rates
    ├── rq2/                           textual abstraction (paragraph + slot-wise)
    ├── rq3/                           visual abstraction (i2t round-trip,
    │                                  sentence-position pairwise + per-generation)
    └── imagen_prompts/                prompt-stage dataset (§4.5)
```

## Required inputs by script

| Script | Reads from |
|---|---|
| `evaluate_rq1_rq2_paragraph.py`     | `data/corpus/` |
| `produce_rq2_mat.py`                | `data/corpus/` |
| `evaluate_rq2_slotwise.py`          | `results/rq2/mat_files/` |
| `run_31_matched_i2t.py`             | `data/corpus/` (calls the LLM, writes `data/i2t_31matched/`) |
| `evaluate_rq3_i2t_slotwise.py`      | `data/i2t_31matched/` (produces the §4.4.2 sentence-position pairwise numbers) |
| `evaluate_rq3_i2t_31matched.py`     | `data/i2t_31matched/` (produces the §4.4.3 per-generation paragraph-level numbers) |
| `build_imagen_prompt_dataset.py`    | `data/logs/generation_log.jsonl` |
| `analyze_imagen_prompts.py`         | `data/logs/generation_log.jsonl` |

All scripts import `lib/semantic_analyzer/main.py` for noun extraction,
WordNet AL, and Brysbaert lookup.

## Reproducibility

Every script is deterministic given the same inputs. Running
`scripts/evaluate_rq1_rq2_paragraph.py`, for instance, will rewrite the
files in `results/rq1/` to be byte-identical to what is shipped in the
repository. The two RQ3 scripts (`evaluate_rq3_i2t_slotwise.py` and
`evaluate_rq3_i2t_31matched.py`) reproduce the headline §4.4 numbers
from the 31 i2t descriptions in `data/i2t_31matched/`.

The `run_31_matched_i2t.py` script is the only script that calls an
external API (Gemini). It is included for completeness but is **not**
required to reproduce any of the numbers in Chapter 4: the cached
descriptions in `data/i2t_31matched/` are the inputs the analysis
scripts use directly.

The original raw stimulus folders (the same 31 stimulus generations) are
also available in the StimuliGenerator app repository:
<https://github.com/MdNoman1538/StimuliGenerator>. This evaluation
repository contains the trimmed-corpus subset used in the thesis.

## Methods explored but not used in the thesis

During the development of the RQ3 analysis pipeline, several alternative
visual-abstraction measurements were implemented and evaluated. They are
not part of the final thesis. A summary of what was tried and why each
alternative was discarded is documented in `notes/rejected_methods_log.md`.
