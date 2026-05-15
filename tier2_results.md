# Tier 2 Analyses

Followups to Tier 1; tightens the *why* behind the headline numbers.

## B1. Pre-Rule-8 vs post-Rule-8 word-count parity

Cutoff: **2026-05-08T00:00:00** (Rule 8 was added in the system prompt on May 8, 2026).

| Group | n | n with NC/MC/VC | Rule 8 pass | Spread mean | Spread max | Brys NC<MC<VC | WN NC<MC<VC |
|-------|---|-----------------|-------------|-------------|-----------|---------------|-------------|
| Pre-Rule-8 | 624 | 624 | 253/624 (40.5%) | 7.95 | 99 | 621 (99.5%) | 350 (56.1%) |
| Post-Rule-8 | 37 | 37 | 35/37 (94.6%) | 0.70 | 19 | 36 (97.3%) | 26 (70.3%) |
| Undated | 0 | 0 | — | — | None | — | — |

## C1. Per-model breakdown

| Model | n | Rule 8 pass | Brys NC<MC<VC | WN NC<MC<VC | NC→VC Brys shift | Mean spread |
|-------|---|-------------|---------------|-------------|------------------|-------------|
| gemini-3.1-pro-preview | 609 | 43.2% | 99.7% | 57.0% | +0.947 | 7.76 |
| gemini-2.5-pro | 25 | 4.0% | 92.0% | 60.0% | +0.850 | 8.76 |
| gemini-3-flash-preview | 25 | 96.0% | 100.0% | 52.0% | +0.837 | 0.48 |
| gemini-2.5-flash | 2 | 0.0% | 100.0% | 50.0% | +0.979 | 15.00 |

## A6. Word-count spread — full distribution

n = 661; mean spread = 7.54 words; median = 3.0; 90th pct = 15.0; 95th pct = 22.0; 99th pct = 97.2; max = 99.

| Spread (words) | Count | Cumulative % |
|----------------|-------|--------------|
| 0 | 126 | 19.1% |
| 1 | 82 | 31.5% |
| 2 | 80 | 43.6% |
| 3 | 70 | 54.2% |
| 4 | 35 | 59.5% |
| 5 | 24 | 63.1% |
| 6 | 46 | 70.0% |
| 7 | 20 | 73.1% |
| 8 | 14 | 75.2% |
| 9 | 14 | 77.3% |
| 10 | 16 | 79.7% |
| 11 | 11 | 81.4% |
| 12 | 21 | 84.6% |
| 13 | 17 | 87.1% |
| 14 | 17 | 89.7% |
| 15 | 10 | 91.2% |
| 16 | 2 | 91.5% |
| 17 | 2 | 91.8% |
| 18 | 2 | 92.1% |
| 19 | 5 | 92.9% |
| 20 | 9 | 94.3% |
| 21 | 4 | 94.9% |
| 22 | 1 | 95.0% |
| 24 | 4 | 95.6% |
| 28 | 4 | 96.2% |
| … | (more 4 bins) | |

Histogram: `figures/word_count_spread_distribution.pdf`

## H4. Top-50 nouns per condition

Source: re-tokenized 698 stimulus entries across all log files.

### NC — top 50

| Rank | Noun | Count |
|------|------|-------|
| 1 | system | 970 |
| 2 | user | 727 |
| 3 | energy | 706 |
| 4 | material | 671 |
| 5 | manufacturing | 656 |
| 6 | design | 656 |
| 7 | force | 629 |
| 8 | displacement | 484 |
| 9 | interface | 479 |
| 10 | processing | 436 |
| 11 | volume | 425 |
| 12 | state | 405 |
| 13 | boundary | 386 |
| 14 | equilibrium | 344 |
| 15 | mass | 314 |
| 16 | interaction | 312 |
| 17 | solution | 310 |
| 18 | yield | 303 |
| 19 | property | 303 |
| 20 | element | 298 |
| 21 | transfer | 292 |
| 22 | input | 279 |
| 23 | resilience | 277 |
| 24 | degradation | 270 |
| 25 | payload | 260 |
| 26 | kinetic | 259 |
| 27 | load | 247 |
| 28 | integrity | 246 |
| 29 | resistance | 239 |
| 30 | flow | 238 |
| 31 | efficiency | 224 |
| 32 | momentum | 216 |
| 33 | zone | 214 |
| 34 | stability | 206 |
| 35 | platform | 204 |
| 36 | vector | 203 |
| 37 | damage | 199 |
| 38 | configuration | 192 |
| 39 | separation | 187 |
| 40 | stress | 181 |
| 41 | resource | 175 |
| 42 | output | 172 |
| 43 | control | 169 |
| 44 | surface | 168 |
| 45 | constraint | 167 |
| 46 | exertion | 167 |
| 47 | friction | 165 |
| 48 | distribution | 164 |
| 49 | transit | 162 |
| 50 | mobility | 159 |

### MC — top 50

| Rank | Noun | Count |
|------|------|-------|
| 1 | user | 866 |
| 2 | processing | 677 |
| 3 | design | 667 |
| 4 | manufacturing | 658 |
| 5 | mechanism | 589 |
| 6 | system | 567 |
| 7 | layout | 488 |
| 8 | assembly | 486 |
| 9 | module | 458 |
| 10 | surface | 384 |
| 11 | control | 382 |
| 12 | content | 342 |
| 13 | linkage | 336 |
| 14 | material | 333 |
| 15 | framework | 318 |
| 16 | extraction | 308 |
| 17 | separation | 306 |
| 18 | component | 304 |
| 19 | volume | 293 |
| 20 | drive | 272 |
| 21 | damage | 259 |
| 22 | platform | 247 |
| 23 | fabrication | 244 |
| 24 | chamber | 241 |
| 25 | support | 231 |
| 26 | mode | 228 |
| 27 | durability | 211 |
| 28 | device | 210 |
| 29 | interface | 209 |
| 30 | frame | 206 |
| 31 | chassis | 201 |
| 32 | casing | 193 |
| 33 | terrain | 190 |
| 34 | effort | 189 |
| 35 | force | 188 |
| 36 | friction | 181 |
| 37 | flotation | 177 |
| 38 | transit | 176 |
| 39 | input | 176 |
| 40 | travel | 174 |
| 41 | unit | 166 |
| 42 | steering | 161 |
| 43 | motion | 157 |
| 44 | yield | 154 |
| 45 | propulsion | 153 |
| 46 | traction | 153 |
| 47 | batch | 143 |
| 48 | alignment | 143 |
| 49 | transport | 143 |
| 50 | balance | 143 |

### VC — top 50

| Rank | Noun | Count |
|------|------|-------|
| 1 | user | 741 |
| 2 | design | 649 |
| 3 | hardware | 648 |
| 4 | manufacturing | 641 |
| 5 | seed | 570 |
| 6 | steel | 538 |
| 7 | hand | 426 |
| 8 | system | 398 |
| 9 | rubber | 378 |
| 10 | part | 376 |
| 11 | crank | 357 |
| 12 | roller | 295 |
| 13 | processing | 285 |
| 14 | volume | 255 |
| 15 | surface | 253 |
| 16 | metal | 252 |
| 17 | bolt | 245 |
| 18 | mesh | 244 |
| 19 | shelf | 243 |
| 20 | rotation | 242 |
| 21 | aluminum | 234 |
| 22 | grip | 230 |
| 23 | frame | 227 |
| 24 | platform | 215 |
| 25 | damage | 212 |
| 26 | wire | 207 |
| 27 | husk | 207 |
| 28 | foam | 206 |
| 29 | hopper | 205 |
| 30 | motion | 205 |
| 31 | plastic | 204 |
| 32 | component | 200 |
| 33 | speed | 199 |
| 34 | arm | 191 |
| 35 | tool | 188 |
| 36 | machine | 181 |
| 37 | leg | 181 |
| 38 | casing | 176 |
| 39 | resistance | 172 |
| 40 | steering | 169 |
| 41 | tubing | 165 |
| 42 | spinning | 162 |
| 43 | chain | 161 |
| 44 | assembly | 158 |
| 45 | gear | 152 |
| 46 | pontoon | 149 |
| 47 | pipe | 143 |
| 48 | pod | 140 |
| 49 | turning | 138 |
| 50 | bracket | 137 |

Bar chart of top 15 each: `figures/top_nouns_per_condition.pdf`
