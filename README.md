# Evaluation Pipeline — Thesis Reproduction Bundle

This directory holds the complete reproduction bundle for every numerical
result in Chapter 4 of the thesis *Semantic and Visual Stimuli Generation with
Large Language Models: A System for Augmenting Design Creativity* (M.\,A.\,A.
Noman, University of Oulu, 2026).

All numbers, tables, and figures referenced in Chapter 4 and the related
appendices are produced by the scripts in `scripts/` from the source data in
the StimuliGenerator app's persistent logs and the trimmed 31-generation
corpus included here. The outputs are written deterministically into
`results/`.

> **Companion repository:** the source code of the stimulus generation system itself is published separately at [MdNoman1538/StimuliGenerator](https://github.com/MdNoman1538/StimuliGenerator). This evaluation bundle was produced from logs emitted by that system.

## Directory layout

```
evaluation/
├── README.md                          ← this file
├── DATA.md                            data-and-script index
├── scripts/                           ← analysis scripts (deterministic)
│   ├── evaluate_rq1_rq2_paragraph.py        RQ1 + RQ2 paragraph
│   ├── evaluate_rq1_semsim_cross_runs.py    RQ1 SBERT cross-regeneration
│   ├── rq1_semsim_detail.py                 RQ1 SBERT detail
│   ├── rq1_semsim_figure.py                 RQ1 SBERT figure
│   ├── produce_rq2_mat.py                   RQ2 .mat preparation
│   ├── evaluate_rq2_slotwise.py             RQ2 slot-wise pooled (712 pairs)
│   ├── evaluate_rq2_slotwise_trimmed.py     RQ2 slot-wise on trimmed corpus
│   ├── run_31_matched_i2t.py                Generates 31 i2t descriptions
│   ├── evaluate_rq3_i2t_slotwise.py         RQ3 §4.4.2 sentence-position pairwise
│   ├── evaluate_rq3_i2t_31matched.py        RQ3 §4.4.3 per-generation paragraph-level
│   ├── trim_corpus.py                       Trim 33 → 31 corpus
│   ├── run_trimmed_analyses.py              Re-run RQ1/RQ2 on trimmed corpus
│   ├── build_imagen_prompt_dataset.py       §4.5 prompt dataset extraction
│   └── analyze_imagen_prompts.py            §4.5 prompt-stage analysis
├── data/                              ← inputs
│   ├── corpus/                              31 stimulus generations (22 jar + 9 skii)
│   ├── i2t_31matched/                       31 i2t descriptions (one per generation)
│   ├── i2t_31matched_slotwise/              per-pair and per-generation outputs
│   └── logs/                                generation_log.jsonl, stimuli_log.jsonl
├── notes/
│   └── rejected_methods_log.md              methods explored but not used
└── results/                           ← deterministic outputs
    ├── rq1/                                 final_results.{json,md}, figures/
    ├── rq2/                                 rq2_slotwise_results.{json,md}, rq2_paragraph_pooled.json, mat_files/, figures/
    ├── rq3/                                 per-pair and per-generation outputs
    └── imagen_prompts/                      paired_prompts.{jsonl,csv}, per_prompt.json
```

## How to reproduce every Chapter 4 number

From the repository root:

```bash
cd evaluation
python3 scripts/run_trimmed_analyses.py           # RQ1 + RQ2 paragraph (trimmed n=31, thesis numbers)
python3 scripts/evaluate_rq1_rq2_paragraph.py     # RQ1 + RQ2 paragraph (full n=33, pre-trim provenance)
python3 scripts/evaluate_rq1_semsim_cross_runs.py # RQ1 SBERT within / across task
python3 scripts/produce_rq2_mat.py                # RQ2 .mat
python3 scripts/evaluate_rq2_slotwise_trimmed.py  # RQ2 slot-wise pooled
python3 scripts/evaluate_rq3_i2t_slotwise.py      # §4.4.2 sentence-position pairwise
python3 scripts/evaluate_rq3_i2t_31matched.py     # §4.4.3 per-generation paragraph
python3 scripts/build_imagen_prompt_dataset.py    # §4.5 dataset extraction
python3 scripts/analyze_imagen_prompts.py         # §4.5 prompt-stage analysis
```

The `run_31_matched_i2t.py` script is the only one that calls the Gemini
API. It is included for completeness; it is **not** required to reproduce
any of the chapter numbers because the i2t descriptions it produced are
already cached in `data/i2t_31matched/`.

## Headline numbers (for fast verification)

| Where | What | Value |
|---|---|---|
| §RQ1 | Rule 8 pass rate (n = 31 generations) | 100 % |
| §RQ1 | WordNet ordering abstract > concrete | 100 % (31/31) |
| §RQ2 | Paragraph AL paired Cohen's *d* | 2.19 |
| §RQ2 | Slot-wise pooled *d* (712 paired observations) | 0.393 |
| §RQ3 (§4.4.2) | Sentence-position pairwise i2t AL *d* (n = 155) | 0.29 |
| §RQ3 (§4.4.3) | Per-generation paragraph-level i2t AL *d* (n = 31) | 0.67 |
| §RQ3 (§4.4.3) | Within-generation ordering on AL | 23 / 31 |
| §4.5 | Prompt paired AL *d* (n = 150) | 0.65 |
| §4.5 | Source → prompt → i2t Δ trajectory (jar) | +0.0370 → +0.0025 → +0.0126 |
| §4.5 | Pair-level Jaccard token overlap | 0.694 ± 0.031 |

## Methods explored but not used in the thesis

During the RQ3 design phase, several alternative visual-abstraction
measurements were implemented and evaluated. They are not part of the
final thesis. A summary of what was tried and why each alternative was
discarded is documented in `notes/rejected_methods_log.md`.
