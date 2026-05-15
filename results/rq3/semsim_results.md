# Semantic Similarity: i2t Derivatives vs Source Texts

Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (384-dim, cosine similarity, normalised).

Sessions analysed: **30** across 3 source folders.

## Overall (all 30 sessions)

| Comparison | n | mean | SD | min | max |
|---|---|---|---|---|---|
| i2t-NC vs source-NC (own, RECOVERY) | 30 | 0.209 | 0.052 | 0.115 | 0.296 |
| i2t-VC vs source-VC (own, RECOVERY) | 30 | 0.285 | 0.062 | 0.159 | 0.373 |
| i2t-NC vs source-VC (cross-condition) | 30 | 0.179 | 0.041 | 0.104 | 0.286 |
| i2t-VC vs source-NC (cross-condition) | 30 | 0.286 | 0.061 | 0.164 | 0.366 |
| i2t-NC vs i2t-VC (within session) | 30 | 0.709 | 0.039 | 0.647 | 0.782 |

**Reading:** own-condition (recovery) > cross-condition is the desired pattern. If own-condition is materially higher than cross-condition, the round trip is preserving the condition-specific semantic content.

## Per-source breakdown

### jar13  (jar 13 passed 3.1 pro)

| Comparison | n | mean | SD | min | max |
|---|---|---|---|---|---|
| i2t-NC vs source-NC (own, RECOVERY) | 10 | 0.156 | 0.046 | 0.115 | 0.243 |
| i2t-VC vs source-VC (own, RECOVERY) | 10 | 0.212 | 0.026 | 0.159 | 0.255 |
| i2t-NC vs source-VC (cross-condition) | 10 | 0.175 | 0.065 | 0.104 | 0.286 |
| i2t-VC vs source-NC (cross-condition) | 10 | 0.208 | 0.022 | 0.164 | 0.237 |
| i2t-NC vs i2t-VC (within session) | 10 | 0.694 | 0.019 | 0.671 | 0.725 |
| i2t-NC vs jar7 source-NC (cross-source) | 10 | 0.167 | 0.040 | 0.123 | 0.237 |
| i2t-VC vs jar7 source-VC (cross-source) | 10 | 0.201 | 0.024 | 0.154 | 0.231 |
| i2t-NC vs skii5 source-NC (cross-source) | 10 | 0.162 | 0.023 | 0.141 | 0.202 |
| i2t-VC vs skii5 source-VC (cross-source) | 10 | 0.197 | 0.020 | 0.160 | 0.226 |

### jar7  (jar 7 passed 3.1 pro)

| Comparison | n | mean | SD | min | max |
|---|---|---|---|---|---|
| i2t-NC vs source-NC (own, RECOVERY) | 10 | 0.257 | 0.021 | 0.228 | 0.296 |
| i2t-VC vs source-VC (own, RECOVERY) | 10 | 0.294 | 0.029 | 0.233 | 0.326 |
| i2t-NC vs source-VC (cross-condition) | 10 | 0.178 | 0.025 | 0.148 | 0.213 |
| i2t-VC vs source-NC (cross-condition) | 10 | 0.339 | 0.024 | 0.289 | 0.366 |
| i2t-NC vs i2t-VC (within session) | 10 | 0.685 | 0.038 | 0.647 | 0.756 |
| i2t-NC vs jar13 source-NC (cross-source) | 10 | 0.231 | 0.039 | 0.162 | 0.284 |
| i2t-VC vs jar13 source-VC (cross-source) | 10 | 0.287 | 0.028 | 0.228 | 0.314 |
| i2t-NC vs skii5 source-NC (cross-source) | 10 | 0.235 | 0.027 | 0.185 | 0.268 |
| i2t-VC vs skii5 source-VC (cross-source) | 10 | 0.280 | 0.020 | 0.233 | 0.307 |

### skii5  (skii 5 passed 3.1 pro)

| Comparison | n | mean | SD | min | max |
|---|---|---|---|---|---|
| i2t-NC vs source-NC (own, RECOVERY) | 10 | 0.214 | 0.023 | 0.168 | 0.252 |
| i2t-VC vs source-VC (own, RECOVERY) | 10 | 0.348 | 0.016 | 0.317 | 0.373 |
| i2t-NC vs source-VC (cross-condition) | 10 | 0.183 | 0.021 | 0.145 | 0.211 |
| i2t-VC vs source-NC (cross-condition) | 10 | 0.312 | 0.010 | 0.290 | 0.328 |
| i2t-NC vs i2t-VC (within session) | 10 | 0.750 | 0.020 | 0.714 | 0.782 |
| i2t-NC vs jar13 source-NC (cross-source) | 10 | 0.182 | 0.029 | 0.119 | 0.225 |
| i2t-VC vs jar13 source-VC (cross-source) | 10 | 0.221 | 0.022 | 0.191 | 0.260 |
| i2t-NC vs jar7 source-NC (cross-source) | 10 | 0.242 | 0.027 | 0.182 | 0.281 |
| i2t-VC vs jar7 source-VC (cross-source) | 10 | 0.223 | 0.023 | 0.195 | 0.262 |
