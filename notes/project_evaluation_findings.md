---
name: Evaluation findings (prior generated stimuli)
description: Headline numbers from the May 9 evaluation pass over 661 prior NC/MC/VC stimulus records
type: project
originSessionId: bbbadae9-84a4-47b2-bba0-361434859e37
---
Evaluation pass run 2026-05-09 over every prior `stimuli_log.jsonl` and `generation_log.jsonl` across all versions of the project, using the current `semantic_analyzer` module. Outputs at `/Users/noman/Documents/Thesis/evaluation/`.

## Headline numbers

- **661 stimulus records** evaluated, all with NC/MC/VC paragraphs present.
- **Brysbaert concreteness ordering (NC < MC < VC) holds in 99.4%** of records (657/661). The single-noun concreteness manipulation is robust.
- **WordNet hypernym-depth ordering (NC < MC < VC) holds in 56.9%** of records (376/661). The ontological-depth axis is much noisier and disagrees with concreteness on roughly 4 out of 10 stimuli.
- **Rule 8 (word-count parity within ±2 across the three paragraphs) holds in only 43.6%** of records (288/661). Word-count drift across conditions is more common than not, even after Rule 8 was added.

## Mean scores per condition (across all sources)

| Condition | Brysbaert (1 = abstract … 5 = concrete) | WordNet depth (smaller = more abstract) |
|---|---|---|
| NC | 3.004 | 5.924 |
| MC | 3.310 | 6.041 |
| VC | 3.943 | 6.484 |

Brysbaert shows a clean monotonic shift (≈+0.94 from NC to VC). WordNet depth shows a smaller shift (≈+0.56) and is the metric that drives the lower ordering pass rate.

## Why this matters for the thesis

1. **Chapter 4 (Evaluation)** now has empirical content. The headline numbers above can be the chapter's opening table.
2. **Triangulation argument is strengthened**: Brysbaert and WordNet *do not* agree, and that disagreement is informative. The thesis Implementation chapter's claim — "where they disagree, the disagreement itself is informative about where the manipulation is fragile" — has supporting numbers (43% disagreement on the ordering check).
3. **Rule 8 was insufficient**: 56.4% of generations failed the ±2 word-count parity even though the rule was in the system prompt. This is a candid finding the thesis should report rather than hide. Possible explanations to discuss: rule introduced late so older logs predate it; LLM doesn't reliably enforce length constraints even when explicitly instructed; manual revision step (Step 11) wasn't strong enough.
4. **The pre-Rule-8 era is in the data**: separating the records by date will sharpen the picture (records before May 8 likely have lower Rule 8 pass rate; those after, higher). Worth running a date-split analysis as a second pass.

## Open follow-ups for the thesis Evaluation chapter

- Split the data by date (pre-Rule 8 vs post-Rule 8) to show the rule's effect.
- Split by model (Gemini 2.5-pro vs 3.1-pro-preview) to show whether the newer model adheres better.
- Look at the specific 4 records where Brysbaert ordering failed — likely informative outliers.
- Compute pairwise t-tests on NC vs MC, MC vs VC, NC vs VC for both Brysbaert and WordNet (the analyzer module already has `paired_ttest`).
