# Image-to-Text (i2t) Round-Trip Evaluation

Sessions: **30** · derived stimuli: **60** (NC + VC per session)

**Primary metric: WordNet hypernym depth.** Brysbaert concreteness is reported below for completeness but is not the headline metric — image descriptions are uniformly concrete-vocabulary, so Brysbaert collapses while WordNet preserves the hierarchical-specificity signal.

## Analysis A — i2t derived stimuli vs full corpus (n=33 runs)

### WordNet hypernym depth (primary)

| Group | n | mean | SD | min | max |
|---|---|---|---|---|---|
| corpus NC | 33 | 5.992 | 0.225 | 5.439 | 6.405 |
| i2t NC | 30 | 5.478 | 0.357 | 4.875 | 6.042 |
| corpus VC | 33 | 6.659 | 0.198 | 6.324 | 7.070 |
| i2t VC | 30 | 6.176 | 0.195 | 5.750 | 6.469 |

**Independent t-tests (i2t vs corpus):**
- NC: t=-6.760, p=1.72e-08, mean diff (i2t–corpus)=-0.514, d=-1.723 (large)
- VC: t=-9.772, p=4.59e-14, mean diff (i2t–corpus)=-0.483, d=-2.464 (large)

**Paired i2t NC vs i2t VC (within-session abstraction separation):**
- t=-8.060, p=6.89e-09, mean diff (VC–NC)=+0.698, d=-1.497 (large)

### Brysbaert concreteness (1–5) — secondary

| Group | n | mean | SD | min | max |
|---|---|---|---|---|---|
| corpus NC | 33 | 3.070 | 0.092 | 2.852 | 3.226 |
| i2t NC | 30 | 3.808 | 0.176 | 3.489 | 4.145 |
| corpus VC | 33 | 3.983 | 0.108 | 3.809 | 4.322 |
| i2t VC | 30 | 3.941 | 0.061 | 3.817 | 4.042 |

**Independent t-tests (i2t vs corpus):**
- NC: t=+20.518, p=8.49e-24, mean diff (i2t–corpus)=+0.738, d=5.246 (large)
- VC: t=-1.929, p=0.0592, mean diff (i2t–corpus)=-0.042, d=-0.481 (small)

**Paired i2t NC vs i2t VC (within-session abstraction separation):**
- t=-4.163, p=0.000257, mean diff (VC–NC)=+0.132, d=-0.773 (medium)

## Analysis B — per-source recovery

For each source folder: 10 i2t sessions were derived from that source's 10 images.
Comparison: i2t-derived NC/VC stimuli (n=10) vs the source's original NC/VC text.

| Source | n | metric | source text | i2t mean ± SD | drift (i2t mean − source) | order NC<VC pass |
|---|---|---|---|---|---|---|
| jar 13 passed | 10 | Brys NC | 3.175 | 3.905 ± 0.113 | +0.730 | 80% |
| jar 13 passed | 10 | WN NC | 6.116 | 5.888 ± 0.098 | -0.229 | — |
| jar 13 passed | 10 | Brys VC | 4.090 | 3.985 ± 0.039 | -0.106 | 80% |
| jar 13 passed | 10 | WN VC | 6.804 | 5.968 ± 0.130 | -0.836 | — |
| jar 7 passed | 10 | Brys NC | 3.007 | 3.590 ± 0.074 | +0.583 | 100% |
| jar 7 passed | 10 | WN NC | 6.053 | 5.054 ± 0.093 | -0.999 | — |
| jar 7 passed | 10 | Brys VC | 4.322 | 3.923 ± 0.058 | -0.399 | 100% |
| jar 7 passed | 10 | WN VC | 7.070 | 6.202 ± 0.120 | -0.868 | — |
| skii 5 passed | 10 | Brys NC | 2.950 | 3.929 ± 0.045 | +0.979 | 50% |
| skii 5 passed | 10 | WN NC | 5.737 | 5.492 ± 0.083 | -0.244 | — |
| skii 5 passed | 10 | Brys VC | 4.023 | 3.914 ± 0.063 | -0.109 | 50% |
| skii 5 passed | 10 | WN VC | 6.487 | 6.357 ± 0.077 | -0.130 | — |

## Word count drift (for reference)

| Source | source NC words | i2t NC words mean ± SD | source VC words | i2t VC words mean ± SD |
|---|---|---|---|---|
| jar 13 passed | 133 | 88.3 ± 5.0 | 133 | 106.1 ± 5.3 |
| jar 7 passed | 111 | 88.0 ± 4.5 | 111 | 97.0 ± 2.2 |
| skii 5 passed | 118 | 110.2 ± 2.3 | 118 | 92.9 ± 2.5 |
