# Rejected RQ3 Methods — Log of Explored-but-Excluded Visual Abstraction Analyses

This document records the visual-abstraction measurement methods that were
implemented and run during the development of RQ3 but were **not** included in
the final thesis. The thesis (§4.4) reports only the Gemini i2t (image-to-text
description) analysis. This log exists so that, if asked, the author can
demonstrate that alternative methods were considered, the data exists, and
that the exclusion is principled rather than convenient.

All numbers below were computed on the same 31-source corpus used in the final
thesis.

---

## Method 1 — ImageNet ResNet-50 + WordNet AL on predicted classes

### What it does
Every image in the corpus (310 images = 31 × 10) is passed through a
pretrained ResNet-50 ImageNet-1K classifier. The top-1 predicted class is
looked up in WordNet and its hypernym depth is converted to the same
normalised AL scale used in RQ2.

### Result
- Paragraph-level top-1 AL: mean Δ = +0.0411, d = 1.20, NC > VC in 26/31 sources, p = 2.3 × 10⁻¹¹
- Paragraph-level confidence-weighted top-5 AL: mean Δ = +0.0359, d = 1.69, NC > VC in 29/31 sources
- Per-task split: jar d = 1.04, skii d = 1.72
- Slot-level paired: d = 0.50, n = 155, p = 5.7 × 10⁻¹⁰

### Why not used in the thesis
1. **Domain-shift bias.** ImageNet was trained on natural photographs. The
   stimuli are stylised low-poly clay renders. Top-1 confidence is very low
   (~0.05–0.30, mean ≈ 0.14), and the classifier is operating well outside
   its training distribution.
2. **Fixed-taxonomy bias.** The 1000-class ImageNet taxonomy is heavy on
   household objects, animals, vehicles, food, instruments, etc. It is light
   on conceptual or abstract referents. The classifier therefore has
   substantially more "concrete" anchors than "abstract" anchors, and any
   image it doesn't recognise as a specific object gets pushed toward the
   shallower / more generic synsets by default. This is structural bias toward
   finding NC images "more abstract."
3. **Reframing as a real-object probe is post-hoc.** The argument that the
   ImageNet classifier should be read as a "calibrated real-object recognition
   probe" (after Skulmowski 2021 and Singer 2023) is conceptually defensible
   but was developed only after the bias critique was raised. A reviewer who
   reads the methodology critically will see the reframing as retroactive.
4. **No independence from the image generator.** While the classifier is not
   Gemini, its predictions on stylised renders are unreliable enough that
   confident interpretation requires either domain-adaptation or human
   validation.

### Data location
`evaluation/data/image_classifier_al/` — `per_image.jsonl`, `per_source.json`,
`summary.json`, `predictions_sample.md`.

### Script
`evaluation/scripts/image_classifier_al.py`

---

## Method 2 — DINOv2 self-supervised cluster separability

### What it does
Every image is encoded by DINOv2 (`facebook/dinov2-base`), a self-supervised
vision transformer trained without any labels or text. For each source, the
mean pairwise cosine distance within the NC cluster, within the VC cluster,
and across NC × VC pairs is computed. The separation ratio
S = mean_inter / mean(mean_intra_nc, mean_intra_vc) is reported, with S > 1
indicating the conditions form distinguishable clusters.

### Result
- Mean separation ratio S = 1.072 (SD = 0.053), 28/31 sources have S > 1.0
- One-sample t-test against S = 1.0: t = 7.65, p = 2.1 × 10⁻¹⁴, d = 1.37
- Mean NC-VC centroid cosine distance = 0.412
- Per-task: jar mean S = 1.062 (19/22 above 1), skii mean S = 1.097 (9/9)

### Why not used in the thesis
1. **Distinguishability is not abstractness.** DINOv2 cluster separation tells
   us NC and VC images sit in different regions of the visual feature space.
   It does **not** tell us that the NC region is more abstract than the VC
   region in any specific sense. The two conditions could be distinguishable
   for many reasons (composition, palette balance, ratio of empty space to
   filled space) that do not correspond to the abstract-vs-concrete axis the
   thesis cares about.
2. **No direction**: the separation ratio is a magnitude, not a signed
   difference. The thesis claim is "NC is more abstract than VC", which
   DINOv2 cannot operationalise without an external label to project the
   embeddings onto.
3. **Self-supervision bias.** DINOv2 was trained on 142 million curated
   web images. Its feature space prioritises whatever properties were useful
   for its self-distillation objective; there is no guarantee that those
   properties align with concreteness as defined in cognitive science.
4. **The 1.072 separation ratio is statistically large (d = 1.37) but
   absolutely small (7.2% above the no-clustering baseline).** A pedantic
   reviewer will read 1.072 vs 1.0 as a small effect, regardless of the
   significance.

### Data location
`evaluation/data/dinov2_analysis/` — `per_image.jsonl`, `per_source.json`,
`summary.json`.

### Script
`evaluation/scripts/dinov2_analysis.py`

---

## Method 3 — SigLIP probe-similarity (CLIP-style)

### What it does
Every image is embedded by SigLIP (`google/siglip-base-patch16-224`). Two sets
of text-prompt embeddings are also computed: an "abstract" probe set (7
prompts) and a "concrete" probe set (7 prompts). The per-image abstraction
score is the mean cosine similarity to abstract probes minus the mean cosine
similarity to concrete probes. Per source, the 5 NC and 5 VC image scores are
averaged and compared.

### Result
- Pooled: mean Δ = +0.0029, d = 0.57, NC > VC in 23/31 sources
- Jar: d = +1.84, NC > VC in 21/22 sources (very strong predicted direction)
- Skii: d = −0.79, NC > VC in 2/9 sources (**reversed direction**)

### Why not used in the thesis
1. **Probe-design dependency.** The result depends heavily on which
   abstract and concrete probe words are chosen. The probes we used were
   biased toward industrial-tool semantics (`a manufactured item`,
   `a recognisable tool`, `a real-world product`), which matches the jar
   task imagery (handles, levers, mechanical parts) but does not match the
   skii task imagery (skis, bindings, snow surfaces).
2. **Skii task reverses direction.** With the industrial-tool probe set,
   skii NC images sit *closer* to concrete probes than skii VC images do —
   the opposite of the predicted direction. This reversal shows that what
   SigLIP measures is not "abstract-vs-concrete" in any general sense, but
   "closeness to industrial-tool semantics," which is task-dependent.
3. **A redesigned domain-neutral probe set was drafted but not run.**
   Possible neutral probes were proposed (`a generic form`, `a specific
   object`, etc.) but the iteration was paused before re-running. The
   probe-design sensitivity is a real methodological constraint of the
   SigLIP approach; it cannot be designed away cleanly.

### Data location
`evaluation/data/siglip_analysis/` — `per_image.jsonl`, `per_source.json`,
`summary.json`.

### Script
`evaluation/scripts/siglip_analysis.py`

---

## Method 4 — i2t paragraph-level pooled across 3 sources × 10 sessions (original design)

### What it does
For three selected source corpora (`jar 13`, `jar 7`, `skii 5`), every image
is re-described by the multimodal LLM ten times. The 5 NC descriptions of a
session are concatenated into an i2t-NC paragraph, and the 5 VC into an
i2t-VC paragraph. The 30 session-level paragraph paired comparisons are
pooled.

### Result
- Paragraph-level paired d = 1.50, n = 30 sessions, NC > VC in 27/30
- Brysbaert d = −0.77
- Per-source: jar 13 collapses (gap 0.004 vs source 0.036), jar 7 retains
  fully (0.060 vs 0.054), skii 5 retains fully (0.046 vs 0.040)

### Why not used in the thesis
1. **Selection bias on 3 sources.** Only three sources were sampled, chosen
   to span pass/fail combinations at the text stage. A reviewer can fairly
   ask why those three and not others.
2. **Inflated effect size by averaging.** The d = 1.50 result averages over
   10 redescriptions per source. With matched-n design (1 redescription per
   source, all 31), the paragraph-level d drops to 0.67 — half the
   originally reported magnitude. The 10×3 design over-reports.
3. **Per-source correlation between source-text gap and i2t gap is r ≈ −0.04
   on the matched 31-source data.** That is, the i2t method is a real
   on-average signal but does not faithfully track the source-text signal at
   the per-run level.

### Data location
`evaluation/data/i2t_sessions/` — 30 session folders, each with descriptions.

### Script
`evaluation/scripts/evaluate_rq3_paragraph.py`

---

## Method 5 — i2t paragraph-level matched-n (n = 31, replaces the 10×3)

### What it does
For each of the 31 sources, every image is re-described **once** by the
multimodal LLM. The 5 NC descriptions are concatenated into an i2t-NC
paragraph and the 5 VC into an i2t-VC paragraph. The 31 paired comparisons
are tested.

### Result
- Paragraph-level (concatenated-then-scored): d = 0.67, n = 31, NC > VC in
  23/31 sources, p = 2.0 × 10⁻⁴
- Brysbaert: d = −0.45, n = 31, VC > NC in 21/31 sources
- Per-source correlation between source-text gap and i2t gap: r = −0.04
  (essentially zero)

### Why not used as the headline in the final thesis
This method was the planned headline, but on further reflection it does not
preserve the experimental pairing structure. The system generated NC_S1 and
VC_S1 as a *paired* output from the same source sentence; pooling the 5 NC
descriptions into one paragraph and scoring as a whole loses that slot-level
pairing information. The slot-wise pairwise design (Method 6 below) does
preserve it and is therefore the more methodologically appropriate test.

### Data location
`evaluation/data/i2t_31matched_analysis/` — `per_source.json`, `summary.json`.

### Script
`evaluation/scripts/evaluate_rq3_i2t_31matched.py`

---

## Method 6 — i2t slot-wise pairwise (**this is what the final thesis reports**)

### What it does
For each of the 31 sources and each of the 5 slots, the NC_Si description is
compared directly with the VC_Si description from the same source sentence.
Each individual description is scored on WordNet AL and Brysbaert. 31 × 5 =
155 paired observations.

Two aggregations are reported in the thesis: (i) the corpus-pooled paired
test across all 155 slot pairs, and (ii) the per-generation average (mean
across the 5 slot ALs per condition) giving 31 paired observations at the
run-aggregate level.

### Result
- **Slot-level (n = 155):** WordNet AL mean Δ = +0.013, d = 0.29,
  NC > VC in 97/155 (62.6%), p = 2.7 × 10⁻⁴.
  Brysbaert mean Δ = −0.071, d = −0.20, VC > NC in 91/155 (58.7%),
  p = 1.3 × 10⁻².
- **Per-generation (n = 31):** WordNet AL mean Δ = +0.013, d = 0.58,
  NC > VC in 24/31 (77.4%), p = 1.3 × 10⁻³.
  Brysbaert mean Δ = −0.071, d = −0.41, VC > NC in 21/31 (67.7%).
- Reversals at the per-generation level: 7 sources have negative mean Δ AL
  (jar 1: −0.053 is the only clear-magnitude reversal; jar 3, jar 5, jar 8,
  jar 9, jar 22, skii 7 are all near-zero).

### Why chosen
1. The slot-wise pairwise design preserves the experimental pairing as it was
   generated by the system.
2. Both WordNet AL and Brysbaert independently agree on the predicted
   direction across both aggregation levels.
3. The result is honest — moderate effect sizes (d = 0.29 to 0.58 on AL),
   not the inflated d = 1.50 from the 10×3 design.

### Limitations acknowledged in the thesis
1. The image-generation and description steps both involve Gemini; this is
   the "AI-describes-AI" concern. Partially defended by external scoring
   (WordNet, Brysbaert) but not eliminated.
2. The per-generation effect size is medium (d = 0.58), not large.
3. 7 of 31 generations (22.6%) do not satisfy the predicted ordering at the
   run-aggregate level, though 5 of those 7 are near-zero "ties."

### Data location
`evaluation/data/i2t_31matched_slotwise/` — `per_pair.jsonl`,
`per_generation.json`, `summary.json`.

### Script
`evaluation/scripts/evaluate_rq3_i2t_slotwise.py`

---

## Summary table — methods explored vs used

| Method | n | Headline effect | Used in thesis? | Primary reason for exclusion |
|---|---|---|---|---|
| ImageNet ResNet-50 + WordNet AL | 31 paragraph-level | d = 1.20–1.69 | No | Domain-shift + fixed-taxonomy bias |
| DINOv2 self-supervised separability | 31 sources | S = 1.072, d = 1.37 | No | Measures distinguishability, not abstractness, with no direction |
| SigLIP probe similarity | 31 sources | Jar d = +1.84, skii d = −0.79 | No | Probe-design sensitivity, skii task reverses |
| i2t paragraph (3 sources × 10 sessions) | 30 sessions | d = 1.50 | No | Inflated by averaging; selection bias on 3 sources |
| i2t paragraph (matched n = 31, concat-then-score) | 31 | d = 0.67 | No | Loses slot pairing structure |
| **i2t slot-wise pairwise (chosen)** | **155 / 31** | **d = 0.29 / 0.58** | **Yes** | — |

---

*This log is internal documentation. None of the rejected methods appear in
the final thesis text.*
