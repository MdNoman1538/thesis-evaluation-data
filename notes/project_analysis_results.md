---
name: Analysis results (Tier 1 + 2 + 3) — May 9 backup
description: Headline empirical findings from running the full evaluation+analysis pipeline against 661 stimuli, 211 multi-vendor model outputs, and 1285 image-gen timings
type: project
originSessionId: bbbadae9-84a4-47b2-bba0-361434859e37
---
All analyses run on 2026-05-09. Outputs saved at `/Users/noman/Documents/Thesis/evaluation/`. This file is a backup so the next session can pick up without re-running anything.

## Files produced

```
/Users/noman/Documents/Thesis/evaluation/
├── README.md
├── evaluate_priors.py            # generates evaluation_log.jsonl
├── summarize_eval.py             # generates evaluation_summary.{md,json}
├── analysis_tier1.py             # A1 distributions, A2 t-tests, A3 effect sizes, E1 repeatability
├── analysis_tier2.py             # B1 pre/post Rule 8, C1 per-model, A6 spread, H4 top nouns
├── analysis_tier3.py             # C2 multi-vendor, F1 image latency
├── evaluation_log.jsonl          # 661 records, one per stimulus set
├── evaluation_summary.{md,json}
├── tier1_results.{md,json}
├── tier2_results.{md,json}
├── tier3_results.{md,json}
└── figures/
    ├── brysbaert_distribution.{pdf,png}
    ├── wordnet_distribution.{pdf,png}
    ├── per_condition_box.{pdf,png}
    ├── word_count_spread_distribution.{pdf,png}
    ├── top_nouns_per_condition.{pdf,png}
    ├── multivendor_brysbaert.{pdf,png}
    ├── image_latency_distribution.{pdf,png}
    ├── image_latency_per_model.{pdf,png}
    └── image_success_over_time.{pdf,png}
```

## Tier 1 — empirical core (Chapter 4)

**A1. Distributions (n=661, all conditions present):**

| Cond | Brysbaert mean ± SD | WordNet depth mean ± SD |
|---|---|---|
| NC | 3.004 ± 0.100 | 5.924 ± 0.218 |
| MC | 3.310 ± 0.097 | 6.041 ± 0.265 |
| VC | 3.943 ± 0.126 | 6.484 ± 0.260 |

Brysbaert distributions narrow (SD~0.1), well-separated. WordNet wider, MC overlaps NC heavily.

**A2/A3. Paired t-tests + Cohen's d (all p < 0.001):**

| Pair | Brysbaert d | WordNet d |
|---|---|---|
| NC↔MC | 2.30 (large) | 0.36 (small) |
| MC↔VC | 4.52 (large) | 1.59 (large) |
| NC↔VC | **6.34 (extraordinary)** | 1.79 (large) |

NC↔MC WordNet d=0.36 is the weak link — the MC condition isn't pulling away from NC ontologically.

**E1. Repeatability across regenerations.** 20 (task, model) groups with ≥2 runs. Within-group Brysbaert SD typically 0.05-0.15; WordNet SD 0.10-0.30. Word-count SD is high (often 5-30 words) — the structural skeleton stays stable, paragraph length doesn't. Largest groups: peanut sheller × gemini-3.1-pro-preview = 302 runs; amphibious bike × same = 183 runs.

## Tier 2 — sharpens the why (Chapter 4 + Implementation)

**B1. ✦ Rule 8 effect (May 8 cutoff):**

| Group | n | Rule 8 (≤2 spread) pass |
|---|---|---|
| Pre-Rule-8 | 624 | 40.5% |
| Post-Rule-8 | 37 | **94.6%** |

**+54 percentage points** improvement. Caveat: post-Rule-8 sample only 37 records.

**C1. Per-model breakdown (only models with n ≥ 10):**

| Model | n | Rule 8 % | Brys order % | WN order % |
|---|---|---|---|---|
| gemini-3.1-pro-preview | 609 | 43.2 | **99.7** | 57.0 |
| gemini-2.5-pro | 25 | 4.0 | 92.0 | 60.0 |
| gemini-3-flash-preview | 25 | **96.0** | 100.0 | 52.0 |

Headline: chosen primary `gemini-3.1-pro-preview` is best at Brysbaert ordering (99.7%) but only middling at length parity (43%). `gemini-3-flash-preview` is dramatically better at length parity (96%) — flash variants enforce length constraints more literally. Tiny n on flash, treat as preliminary.

**A6. Spread distribution.** Mean 7.54 words; median 3; p90=15; p95=22; p99=97; max=99. Histogram is bimodal — most stimuli cluster near 0, smaller mode around 6, long sparse tail. 19% have spread=0 (perfect parity), 43.6% pass Rule 8 (≤2).

**H4. Top nouns per condition.** Three words appear in all conditions (`user`, `design`, `manufacturing`) — these are skeleton-frame artifacts, not signal. After stripping the frame:
- NC: `system, energy, material, dynamics` (physics/principles)
- MC: `processing, mechanism, components` (functional/architectural)
- VC: `hardware, seed, ...` (concrete artifacts; "seed" inflated by peanut-sheller corpus dominance, 302/661)

The methodology shifts vocabulary at the right grain.

## Tier 3 — model selection backing + latency (Chapter 3 §3.7.5)

**C2. Multi-vendor archive (testBench Apr 1–4, 211 model entries from 23 files):**

| Vendor | Attempts | Success % | Brysbaert mean |
|---|---|---|---|
| Claude | 45 | 93.3 | 3.240 |
| Gemini | 72 | **43.1** | 3.266 |
| Grok | 28 | **0.0** | — |
| Ollama (local) | 20 | 100.0 | 3.069 |
| OpenAI | 46 | 60.9 | 3.217 |

Two surprises:
1. **Gemini's success rate (43%) was the second-lowest** in the archive — most calls returned errors during the Apr 1–4 testing window (likely API key gating, Apr 1 evening had API key not set). The thesis can frame: Gemini was qualitatively preferred by Mengru/Georgiev/Politecnico despite higher reliability problems at the time.
2. **Quality (Brysbaert mean) is essentially uniform across vendors** at 3.07–3.27. The choice between vendors is *not* a quality difference — all working models produce similarly concrete output. So the selection had to come down to qualitative judgment. The thesis narrative for "why Gemini" is supported.
3. Grok produced zero successful outputs in the archive — formal confirmation of the chat-record observation that Grok was dropped early.

**F1. Image generation latency (1285 calls across 4 timing logs, 8 days):**

- **Overall success rate: 80.8%** (1038 ok, 247 fail)
- Successful-call duration: mean 27.9s, p50 19.2s, p90 ~25s, p95 28.1s, **p99 419.5s** (extreme tail), max larger
- Implementation §3.7.5's "1.5× mean" rule of thumb gives **42s** as the operating timeout — would catch p95 successes but cut off p99 cases. The long tail is real: roughly 1% of calls take 7+ minutes.

The bimodal latency pattern matches the country-restriction story — most calls succeed quickly, a small set takes minutes due to fallback retries.

## What this gives the thesis

1. **Chapter 4 has its empirical core.** Three figures (distributions, boxplots, top nouns) and four tables (effect sizes, repeatability, model breakdown, vendor comparison) ready to drop in.
2. **Chapter 3 §3.7 (Implementation Challenges) has its numbers:**
   - §3.7.1 (geographic availability): F1 daily success-rate timeline shows the failures.
   - §3.7.2 (Rule 8 word-count parity): B1's +54 pp finding.
   - §3.7.5 (timeout economics): F1 percentile distribution.
3. **Chapter 3 §3.2 (Why Gemini) backed quantitatively:** C2 shows quality parity across vendors — selection genuinely was qualitative.
4. **Chapter 5 (Discussion) gets:** the WordNet NC↔MC weak signal as a methodological limitation; the Rule 8 dramatic improvement as a contribution worth reporting; the long-tail latency as a remaining engineering challenge.

## Resume points for next session

- **Thesis source state:** compiles cleanly to 28 pages. All 11 BibTeX entries have full author lists. Implementation §3.7 has full draft prose. RQs reflect Mengru's controllability framing.
- **Pending tasks:** Overleaf git sync (need user's Overleaf project URL); expand thesis content to ~70 pages (deferred); draft Chapter 4 (Evaluation) prose using these results.
- **Known unknowns / follow-ups (not yet run):**
  - B2 pre/post FBS structure split (Apr 2 cutoff)
  - C2 deeper: per-model multi-vendor breakdown to see *which specific* OpenAI/Claude models did best
  - D1 per-task quality
  - E2 sentence-skeleton invariance check
  - F2 image-text alignment manual coding (needs user)
  - H1 noun-slot length matching (needs N1–N25 parser)
- **Next-session natural starting point:** Draft Chapter 4 (Evaluation) prose using the Tier 1+2+3 numbers, OR run the deeper analyses listed above.

## Re-run commands

```bash
cd /Users/noman/Documents/Thesis/evaluation
python3 evaluate_priors.py     # ~1.5 min, regenerates evaluation_log.jsonl
python3 summarize_eval.py      # < 1 sec
python3 analysis_tier1.py      # < 5 sec
python3 analysis_tier2.py      # ~30 sec (re-tokenizes for noun freq)
python3 analysis_tier3.py      # ~30 sec
```

All scripts are deterministic — same inputs produce same outputs.

## To recompile thesis

```bash
export PATH="/Library/TeX/texbin:$PATH"
cd "/Users/noman/Documents/Thesis/thesis writing"
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
