# Tier 3 Analyses

Quantitative backing for the model-selection narrative (C2) and the
empirical-timeout claim in Implementation §3.7.5 (F1).

## C2. Multi-vendor archive re-evaluation

Source: 23 files in `testBench/exports/stimuli_all_models_*.txt`. 211 model entries parsed.

### Per-vendor summary

| Vendor | Attempts | Success | Scored | Success % | Brys mean | WN depth | Word count | Sent count |
|--------|----------|---------|--------|-----------|-----------|----------|------------|------------|
| CLAUDE | 45 | 42 | 42 | 93.3% | 3.240 | 5.991 | 163.238 | 6.000 |
| GEMINI | 72 | 31 | 31 | 43.1% | 3.266 | 5.932 | 126.871 | 5.000 |
| GROK | 28 | 0 | 0 | 0.0% | — | — | — | — |
| OLLAMA | 20 | 20 | 20 | 100.0% | 3.069 | 5.875 | 169.050 | 8.750 |
| OPENAI | 46 | 28 | 28 | 60.9% | 3.217 | 5.889 | 182.179 | 7.393 |

### Per-model summary (only models with ≥ 3 attempts shown)

| Vendor | Model | Attempts | Success % | Brys mean | WN depth | Word count |
|--------|-------|----------|-----------|-----------|----------|------------|
| CLAUDE | claude-haiku-4-5-20251001 | 15 | 93.3% | 3.219 | 5.965 | 157.929 |
| CLAUDE | claude-opus-4-6 | 15 | 93.3% | 3.281 | 6.078 | 161.929 |
| CLAUDE | claude-sonnet-4-6 | 15 | 93.3% | 3.221 | 5.930 | 169.857 |
| GEMINI | gemini-1.5-flash | 6 | 0.0% | — | — | — |
| GEMINI | gemini-1.5-flash-8b | 6 | 0.0% | — | — | — |
| GEMINI | gemini-1.5-pro | 6 | 0.0% | — | — | — |
| GEMINI | gemini-2.0-flash | 6 | 0.0% | — | — | — |
| GEMINI | gemini-2.0-flash-lite | 6 | 0.0% | — | — | — |
| GEMINI | gemini-2.0-pro-exp | 6 | 0.0% | — | — | — |
| GEMINI | gemini-2.5-pro | 17 | 94.1% | 3.238 | 5.825 | 127.688 |
| GEMINI | gemini-3.1-pro | 3 | 0.0% | — | — | — |
| GEMINI | gemini-3.1-pro-preview | 16 | 93.8% | 3.295 | 6.046 | 126.000 |
| GROK | grok-2 | 7 | 0.0% | — | — | — |
| GROK | grok-2-mini | 7 | 0.0% | — | — | — |
| GROK | grok-3 | 7 | 0.0% | — | — | — |
| GROK | grok-3-mini | 7 | 0.0% | — | — | — |
| OLLAMA | gemma2:9b | 4 | 100.0% | 3.027 | 5.747 | 119.250 |
| OLLAMA | llama3.1:8b | 4 | 100.0% | 3.021 | 5.922 | 219.750 |
| OLLAMA | llama3:latest | 4 | 100.0% | 3.002 | 5.743 | 171.500 |
| OLLAMA | mistral:latest | 4 | 100.0% | 3.161 | 5.992 | 182.000 |
| OLLAMA | qwen2.5:7b | 4 | 100.0% | 3.136 | 5.969 | 152.750 |
| OPENAI | gpt-5.1 | 7 | 85.7% | 3.299 | 6.034 | 200.333 |
| OPENAI | gpt-5.2-pro | 7 | 42.9% | 3.239 | 5.892 | 244.333 |
| OPENAI | gpt-5.3-chat-latest | 7 | 57.1% | 3.207 | 5.889 | 171.500 |
| OPENAI | gpt-5.4 | 15 | 80.0% | 3.213 | 5.862 | 151.750 |
| OPENAI | gpt-5.4-pro | 10 | 30.0% | 3.063 | 5.700 | 219.667 |

Boxplot at `figures/multivendor_brysbaert.pdf`.

## F1. Image generation latency

Total entries: **1285**, success: 1038 (80.8%), failure: 247.

### Successful-call duration percentiles

- n = 1038
- mean = 27.90s
- p50 = 19.17s
- p90 = 23.21s
- p95 = 28.08s
- p99 = 419.54s
- max = 724.36s

Implementation §3.7.5 sets the operating timeout as 1.5× the empirical mean: **42s** would be the corresponding bound.

### Failed-call duration percentiles (how fast/slow failures happen)

- n = 247, mean = 100.73s, p50 = 0.27s, p95 = 790.80s, max = 3079.65s

### Per-model timing

| Model | n | Success % | n success | mean (s) | p50 | p90 | p95 | p99 | max |
|-------|---|-----------|-----------|----------|-----|-----|-----|-----|-----|
| gemini-3-pro-image-preview | 1047 | 93.0% | 974 | 28.56 | 19.27 | 23.19 | 27.55 | 438.75 | 724.36 |
| gemini-3.1-pro-preview | 80 | 0.0% | 0 | — | — | — | — | — | — |
| imagen-3.0-generate-002 | 80 | 0.0% | 0 | — | — | — | — | — | — |
| gemini-2.5-flash-image | 54 | 100.0% | 54 | 6.67 | 6.38 | 7.72 | 7.97 | 8.67 | 9.15 |
| gemini-3.1-flash-image-preview | 13 | 76.9% | 10 | 77.74 | 66.20 | 134.60 | 154.28 | 170.02 | 173.96 |
| gemini-3.1-flash-image | 11 | 0.0% | 0 | — | — | — | — | — | — |

Histograms at `figures/image_latency_distribution.pdf`, `figures/image_latency_per_model.pdf`, `figures/image_success_over_time.pdf`.
