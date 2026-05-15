# Evaluation Pipeline — Thesis Reproduction Bundle

This directory holds the complete reproduction bundle for every numerical
result in Chapter 4 of the thesis *Semantic Stimuli Generation with Large
Language Models: A System for Augmenting Design Creativity* (M.\,A.\,A. Noman,
University of Oulu, 2026).

All numbers, tables, and figures referenced in Chapter 4 and the related
appendices are produced by the scripts in `scripts/` from the source data in
the StimuliGenerator app's persistent logs. The outputs are written
deterministically into `results/`.

> **Companion repository:** the source code of the stimulus generation system itself is published separately at [MdNoman1538/StimuliGenerator](https://github.com/MdNoman1538/StimuliGenerator). This evaluation bundle was produced from logs emitted by that system.

## Directory layout

```
evaluation/
├── README.md                       ← this file
├── scripts/                        ← analysis scripts (deterministic)
│   ├── evaluate_rq1_rq2_paragraph.py    RQ1 + RQ2 paragraph
│   ├── produce_rq2_mat.py               RQ2 .mat preparation
│   ├── evaluate_rq2_slotwise.py         RQ2 slot-wise pooled (n_pairs = 757)
│   ├── evaluate_rq3_paragraph.py        RQ3 i2t paragraph
│   ├── produce_rq3_mat.py               RQ3 .mat preparation
│   ├── evaluate_rq3_semsim.py           RQ3 sentence-embedding cosine
│   ├── build_imagen_prompt_dataset.py   §4.5 prompt dataset extraction
│   └── analyze_imagen_prompts.py        §4.5 prompt-stage analysis
├── results/                        ← deterministic outputs
│   ├── rq1/        final_results.{json,md}, final_log.jsonl, figures/
│   ├── rq2/        rq2_slotwise_results.{json,md}, mat_files/, figures/
│   ├── rq3/        i2t_results.{json,md}, semsim_results.{json,md}, mat_files/
│   └── imagen_prompts/  paired_prompts.{jsonl,csv}, per_prompt.json, README.md
├── figures/                        ← additional shared figures
├── archive/                        ← prior-iteration outputs (kept for audit)
├── tier1_results.{json,md}         ← model-selection background analyses
├── tier2_results.{json,md}         ← (referenced by Implementation §3.7.5)
└── tier3_results.{json,md}         ← multi-vendor archive re-evaluation
```

## Source data

All scripts read from one of three places in the StimuliGenerator app:

| Source | Used by |
|---|---|
| `Apps/StimuliGenerator/stimuli_log.jsonl`     | RQ1, RQ2 (text-only generation) |
| `Apps/StimuliGenerator/generation_log.jsonl`  | RQ3 (i2t round-trip), §4.5 (paired prompts) |
| `Apps/StimuliGenerator/image_backups/`        | RQ3 per-source recovery |

The corpus on which the thesis's primary claims are made is 33 generation
runs (22 jar + 11 skii) plus 30 image-to-text sessions across 3 source
folders.

## How to reproduce every Chapter 4 number

From the repository root:

```bash
cd evaluation
python3 scripts/evaluate_rq1_rq2_paragraph.py   # RQ1 + RQ2 paragraph
python3 scripts/produce_rq2_mat.py              # RQ2 .mat
python3 scripts/evaluate_rq2_slotwise.py        # RQ2 slot-wise pooled
python3 scripts/produce_rq3_mat.py              # RQ3 .mat
python3 scripts/evaluate_rq3_paragraph.py       # RQ3 i2t paragraph
python3 scripts/evaluate_rq3_semsim.py          # RQ3 semantic similarity
python3 scripts/build_imagen_prompt_dataset.py  # §4.5 dataset extraction
python3 scripts/analyze_imagen_prompts.py       # §4.5 prompt-stage analysis
```

Every numerical claim in Chapter 4 and Appendices 3–5 and 7 is grounded in
one of the resulting JSON files.

## Headline numbers (for fast verification)

| Where | What | Value |
|---|---|---|
| §RQ1   | Rule 8 pass rate (n=33)               | 97.0 % |
| §RQ1   | WordNet ordering NC<VC                | 100 % (33/33) |
| §RQ2   | Paragraph AL paired Cohen's d         | 2.28 |
| §RQ2   | Slot-wise pooled d (n_pairs = 757)    | 0.395 |
| §RQ3   | i2t paragraph AL paired Cohen's d     | 1.50 |
| §RQ3   | Within-session AL ordering            | 27/30 = 90 % |
| §4.5   | Prompt paired AL d (n_pairs = 160)    | 0.67 |
| §4.5   | Source → prompt → i2t Δ trajectory    | +0.037 → +0.003 → +0.035 (jar) |
| §4.5   | Pair-level Jaccard token overlap      | 0.693 ± 0.032 |

## Audit trail

The thesis chapter (`Chapters/experiments.tex`) reports each of these
numbers with its provenance (which script, which JSON field). Cross-checks
were run on 2026-05-15: 36 / 36 numerical claims in Chapter 4 and the
appendices verified within rounding tolerance against the source-of-truth
files in `results/`.
