# RQ2 — Slot-wise pairwise evaluation of the textual stimuli

33 source runs × 25 noun-phrase slots per run = **712 paired slot observations**.

Each source pair is one (NC, VC) text comparison from the 33-run participant-facing corpus. The locked five-sentence skeleton guarantees that slot $N_i$ in every run refers to the same conceptual noun position, so the slot index is comparable across runs. The metric is the normalised abstraction level (AL) on $[0, 1]$, with 1 = most abstract.

## Pooled (all 825 slot pairs)

| Statistic | Value |
|---|---|
| NC mean AL | 0.7444  (SD 0.0675) |
| VC mean AL | 0.7059  (SD 0.0713) |
| mean delta (NC − VC) | **+0.0385**  (SD 0.0979) |
| paired t-test | t = +10.496,  p = 4.66e-24 |
| Cohen's d | **0.393**  (small) |
| slots where NC > VC | 426  (59.8\%) |
| slots where NC < VC | 206 |
| slots tied | 80 |

## Per task

| Task | n runs | n pairs | NC mean | VC mean | delta mean | t | p | Cohen's d | Effect | NC>VC % |
|---|---|---|---|---|---|---|---|---|---|---|
| jar | 22 | 509 | 0.7427 | 0.7074 | +0.0353 | +7.933 | 1.37e-14 | 0.352 | small | 58.7 |
| skii | 9 | 203 | 0.7486 | 0.7021 | +0.0465 | +7.282 | 7.18e-12 | 0.511 | medium | 62.6 |

## Per slot mean across 33 source runs

Slots with large positive delta mean are the slots where the methodology produces the strongest abstraction shift in practice. Slots near zero are weakest.

| Slot | n | NC mean | VC mean | delta mean | delta SD | NC>VC % |
|---|---|---|---|---|---|---|
| N1 | 24 | 0.7445 | 0.6754 | +0.0690 | 0.0956 | 58.3 |
| N2 | 26 | 0.7338 | 0.6802 | +0.0536 | 0.0824 | 69.2 |
| N3 | 27 | 0.7388 | 0.7164 | +0.0224 | 0.0896 | 48.1 |
| N4 | 28 | 0.7265 | 0.7121 | +0.0144 | 0.1287 | 60.7 |
| N5 | 30 | 0.7456 | 0.7456 | +0.0000 | 0.0957 | 33.3 |
| N6 | 29 | 0.7495 | 0.7160 | +0.0336 | 0.1098 | 55.2 |
| N7 | 28 | 0.7378 | 0.7027 | +0.0351 | 0.0905 | 57.1 |
| N8 | 27 | 0.7495 | 0.6699 | +0.0796 | 0.0687 | 81.5 |
| N9 | 29 | 0.7423 | 0.6633 | +0.0789 | 0.0898 | 75.9 |
| N10 | 23 | 0.7425 | 0.6899 | +0.0526 | 0.1119 | 60.9 |
| N11 | 29 | 0.7604 | 0.6863 | +0.0741 | 0.0860 | 72.4 |
| N12 | 31 | 0.7827 | 0.7784 | +0.0043 | 0.0781 | 58.1 |
| N13 | 31 | 0.7275 | 0.6692 | +0.0583 | 0.0609 | 80.6 |
| N14 | 31 | 0.7394 | 0.6893 | +0.0501 | 0.0748 | 67.7 |
| N15 | 31 | 0.7173 | 0.6862 | +0.0311 | 0.1083 | 58.1 |
| N16 | 31 | 0.7351 | 0.7241 | +0.0110 | 0.0587 | 38.7 |
| N17 | 29 | 0.7468 | 0.7541 | -0.0073 | 0.0747 | 44.8 |
| N18 | 29 | 0.7250 | 0.7032 | +0.0218 | 0.0920 | 55.2 |
| N19 | 29 | 0.7486 | 0.6897 | +0.0590 | 0.0849 | 65.5 |
| N20 | 27 | 0.7437 | 0.7008 | +0.0429 | 0.1017 | 63.0 |
| N21 | 27 | 0.7300 | 0.7222 | +0.0078 | 0.1072 | 44.4 |
| N22 | 25 | 0.7116 | 0.7154 | -0.0039 | 0.0941 | 48.0 |
| N23 | 30 | 0.7123 | 0.7447 | -0.0325 | 0.1214 | 30.0 |
| N24 | 31 | 0.8090 | 0.7148 | +0.0942 | 0.0867 | 80.6 |
| N25 | 30 | 0.7974 | 0.6822 | +0.1152 | 0.1003 | 86.7 |

## Per run (analyzer's own paired t-test on 25 slots within that run)

| Run folder | Task | AL_NC | AL_VC | delta | t | p |
|---|---|---|---|---|---|---|
| source_jar_10_2failed_bci_passed_3_1_pro | jar | 0.7246 | 0.6990 | +0.0256 | +1.658 | 0.112 |
| source_jar_11_2failed_bci_passed_3_1_pro | jar | 0.7384 | 0.7120 | +0.0264 | +1.241 | 0.228 |
| source_jar_12_2failed_bci_passed_3_1_pro | jar | 0.7514 | 0.7138 | +0.0376 | +2.044 | 0.0531 |
| source_jar_13_passed_3_1_pro | jar | 0.7368 | 0.6970 | +0.0398 | +2.687 | 0.0132 |
| source_jar_14_2failed_bci_passed_3_1_pro | jar | 0.7281 | 0.7068 | +0.0213 | +0.862 | 0.397 |
| source_jar_15_2failed_bci_passed_3_1_pro | jar | 0.7414 | 0.7137 | +0.0277 | +1.663 | 0.113 |
| source_jar_16_passed_3_1_pro | jar | 0.7724 | 0.6966 | +0.0758 | +4.394 | 0.000211 |
| source_jar_17_1_failed_new_2_passed_3_1_pro | jar | 0.7659 | 0.7150 | +0.0509 | +2.984 | 0.00644 |
| source_jar_18_2failed_bci_passed_3_1_pro | jar | 0.7406 | 0.6932 | +0.0474 | +1.779 | 0.0912 |
| source_jar_18_passed_3_1_pro | jar | 0.7496 | 0.6725 | +0.0771 | +4.217 | 0.000355 |
| source_jar_1_2failed_bci_passed_3_1 | jar | 0.7368 | 0.7193 | +0.0175 | +0.751 | 0.461 |
| source_jar_20_2failed_bci_passed_3_1_pro | jar | 0.7416 | 0.7181 | +0.0235 | +1.156 | 0.259 |
| source_jar_21_1failed_old_fail_2_passed_3_1_pro | jar | 0.7659 | 0.7119 | +0.0540 | +2.001 | 0.0579 |
| source_jar_22_2failed_bci_passed_3_1_pro | jar | 0.7504 | 0.7105 | +0.0399 | +1.809 | 0.0842 |
| source_jar_2_bad_2failed_bci_passed_3_1 | jar | 0.7401 | 0.7193 | +0.0208 | +0.923 | 0.367 |
| source_jar_3_2failed_bci_passed_3_1 | jar | 0.7384 | 0.7145 | +0.0239 | +0.994 | 0.331 |
| source_jar_4_passed_3_1 | jar | 0.7509 | 0.6881 | +0.0628 | +3.490 | 0.00207 |
| source_jar_5_2failed_bci_passed_3_1 | jar | 0.7444 | 0.6995 | +0.0449 | +1.482 | 0.156 |
| source_jar_6_2failed_bci_passed_3_1 | jar | 0.7158 | 0.7134 | +0.0024 | -0.172 | 0.865 |
| source_jar_7_passed_3_1_pro | jar | 0.7384 | 0.6842 | +0.0542 | +3.445 | 0.00221 |
| source_jar_8_bad_image_2failed_bci_passed_3_1_pro | jar | 0.7244 | 0.6959 | +0.0285 | +0.531 | 0.6 |
| source_jar_9_2failed_bci_passed_3_1_pro | jar | 0.7209 | 0.7086 | +0.0123 | +0.511 | 0.614 |
| source_skii_01_bci_only_passed_3_1_pro | skii | 0.7464 | 0.7119 | +0.0345 | +1.454 | 0.159 |
| source_skii_2_passed_3_1 | skii | 0.7430 | 0.6970 | +0.0460 | +2.778 | 0.011 |
| source_skii_3_passed_but_new_wordnet_fail_3_1 | skii | 0.7523 | 0.6935 | +0.0588 | +3.182 | 0.00415 |
| source_skii_4_passed_3_1 | skii | 0.7539 | 0.6789 | +0.0750 | +4.053 | 0.000621 |
| source_skii_5_passed_3_1_pro | skii | 0.7599 | 0.7090 | +0.0509 | +2.405 | 0.025 |
| source_skii_6_passed_3_1_pro | skii | 0.7386 | 0.7072 | +0.0314 | +2.236 | 0.0376 |
| source_skii_7_2_passed_old_woprdnet_fail_3_1_pro | skii | 0.7474 | 0.7074 | +0.0400 | +1.407 | 0.172 |
| source_skii_8_2failed_bci_passed_3_1_pro | skii | 0.7436 | 0.7060 | +0.0376 | +1.779 | 0.0904 |
| source_snow0_passed_3_1_pro | skii | 0.7570 | 0.6934 | +0.0636 | +3.250 | 0.00383 |