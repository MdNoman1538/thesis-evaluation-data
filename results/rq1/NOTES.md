# Notes — Which file matches Chapter 4?

The thesis reports numbers on the **trimmed 31-generation participant-facing
corpus** (22 jar + 9 skii). Two files in this directory may look interchangeable
but are computed on **different corpora**:

| File | Corpus | Use this for |
|---|---|---|
| `structural_pass.json` | trimmed n = 31 | Chapter 4 §4.2 structural pass rates |
| `final_results.json`   | full n = 33 (pre-trim) | bookkeeping only; not used in the thesis |

`final_results.json` is retained for provenance — it shows the
pre-trim numbers (Rule 8 = 97.0 %, paragraph WN d = −2.28) before the two
late-rerun duplicates were removed by `trim_corpus.py`. The thesis numbers
(Rule 8 = 100 %, paragraph WN d = +2.19) come from the trimmed analysis and
are persisted in:

- `results/rq1/structural_pass.json` — structural pass rates
- `results/rq2/rq2_paragraph_pooled.json` — RQ2 paragraph-level paired test
- `results/rq2/rq2_slotwise_results.json` — RQ2 slot-wise pooled

Re-running `scripts/run_trimmed_analyses.py` regenerates all trimmed outputs
under `results_trimmed/` (mirror copies live in this `results/` tree where
the thesis cites them directly).
