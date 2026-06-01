# Notes — Pair count in this directory vs Chapter 4 §4.5

The thesis reports **150 paired prompts (30 generations × 5 positions)** in
§4.5. The archived dataset in this directory contains **160 paired prompts
(32 sessions × 5 positions)**:

- 22 jar sessions × 5 = 110 prompt pairs
- 10 skii sessions × 5 = 50 prompt pairs
- 32 sessions × 5 = 160 paired prompts (320 individual prompts)

The thesis number reflects the intersection with the trimmed 31-generation
corpus (22 jar + 9 skii) that the thesis uses for RQ1–RQ3, minus one
generation in the trimmed corpus whose `paired_prompts[]` array in
`generation_log.jsonl` is incomplete. The two sessions in this dataset that
are not part of the thesis-reported 150 are:

1. one skii session outside the trimmed 31-generation corpus, retained here
   for completeness of the prompt log;
2. one skii session inside the trimmed corpus but excluded from the §4.5
   analysis because its paired-prompt record is partial.

Both the 150-pair (thesis) and 160-pair (full log) analyses produce the same
headline numbers to within rounding:

| Quantity | 150 pairs (thesis) | 160 pairs (full log) |
|---|---|---|
| Paragraph-paired AL d | 0.65 | 0.643 |
| Δ AL | +0.0026 | +0.0025 |
| Jaccard token overlap | 0.694 ± 0.031 | 0.6928 ± 0.0316 |
| Abstract > concrete ordering | 77.4 % | 77.3 % |

The numbers in §4.5 and Table 8 of the thesis are the 150-pair results; the
data in this directory is the 160-pair superset for users who want to re-run
the analysis on the full available prompt log.
