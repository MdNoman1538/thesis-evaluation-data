# RQ2 — Slot-wise pairwise evaluation of the textual stimuli

33 source runs × 25 noun-phrase slots per run = **757 paired slot observations**.

Each source pair is one (NC, VC) text comparison from the 33-run participant-facing corpus. The locked five-sentence skeleton guarantees that slot $N_i$ in every run refers to the same conceptual noun position, so the slot index is comparable across runs. The metric is the normalised abstraction level (AL) on $[0, 1]$, with 1 = most abstract.

## Pooled (all 825 slot pairs)

| Statistic | Value |
|---|---|
| NC mean AL | 0.7444  (SD 0.0670) |
| VC mean AL | 0.7061  (SD 0.0712) |
| mean delta (NC − VC) | **+0.0383**  (SD 0.0970) |
| paired t-test | t = +10.855,  p = 1.3e-25 |
| Cohen's d | **0.395**  (small) |
| slots where NC > VC | 452  (59.7\%) |
| slots where NC < VC | 220 |
| slots tied | 85 |

## Per task

| Task | n runs | n pairs | NC mean | VC mean | delta mean | t | p | Cohen's d | Effect | NC>VC % |
|---|---|---|---|---|---|---|---|---|---|---|
| jar | 22 | 509 | 0.7427 | 0.7074 | +0.0353 | +7.933 | 1.37e-14 | 0.352 | small | 58.7 |
| skii | 11 | 248 | 0.7480 | 0.7036 | +0.0444 | +7.806 | 1.67e-13 | 0.496 | small | 61.7 |

## Per slot mean across 33 source runs

Slots with large positive delta mean are the slots where the methodology produces the strongest abstraction shift in practice. Slots near zero are weakest.

| Slot | n | NC mean | VC mean | delta mean | delta SD | NC>VC % |
|---|---|---|---|---|---|---|
| N1 | 26 | 0.7378 | 0.6741 | +0.0637 | 0.0948 | 57.7 |
| N2 | 28 | 0.7340 | 0.6786 | +0.0554 | 0.0799 | 71.4 |
| N3 | 29 | 0.7396 | 0.7151 | +0.0245 | 0.0867 | 51.7 |
| N4 | 29 | 0.7250 | 0.7129 | +0.0121 | 0.1269 | 58.6 |
| N5 | 32 | 0.7450 | 0.7475 | -0.0025 | 0.0932 | 31.2 |
| N6 | 31 | 0.7470 | 0.7156 | +0.0314 | 0.1073 | 54.8 |
| N7 | 30 | 0.7386 | 0.7032 | +0.0354 | 0.0874 | 60.0 |
| N8 | 29 | 0.7513 | 0.6736 | +0.0777 | 0.0698 | 79.3 |
| N9 | 31 | 0.7445 | 0.6613 | +0.0832 | 0.0884 | 77.4 |
| N10 | 24 | 0.7434 | 0.6897 | +0.0537 | 0.1096 | 62.5 |
| N11 | 30 | 0.7579 | 0.6880 | +0.0699 | 0.0877 | 70.0 |
| N12 | 33 | 0.7767 | 0.7775 | -0.0008 | 0.0807 | 57.6 |
| N13 | 33 | 0.7304 | 0.6685 | +0.0619 | 0.0630 | 81.8 |
| N14 | 33 | 0.7408 | 0.6938 | +0.0470 | 0.0735 | 63.6 |
| N15 | 33 | 0.7161 | 0.6861 | +0.0300 | 0.1062 | 57.6 |
| N16 | 33 | 0.7352 | 0.7249 | +0.0104 | 0.0584 | 39.4 |
| N17 | 30 | 0.7482 | 0.7517 | -0.0035 | 0.0763 | 46.7 |
| N18 | 31 | 0.7241 | 0.7080 | +0.0161 | 0.0916 | 51.6 |
| N19 | 31 | 0.7479 | 0.6893 | +0.0586 | 0.0831 | 64.5 |
| N20 | 28 | 0.7453 | 0.7021 | +0.0432 | 0.0998 | 64.3 |
| N21 | 29 | 0.7323 | 0.7214 | +0.0109 | 0.1040 | 48.3 |
| N22 | 27 | 0.7134 | 0.7190 | -0.0055 | 0.0909 | 44.4 |
| N23 | 32 | 0.7204 | 0.7475 | -0.0271 | 0.1200 | 31.2 |
| N24 | 33 | 0.8086 | 0.7169 | +0.0917 | 0.0856 | 78.8 |
| N25 | 32 | 0.7952 | 0.6741 | +0.1211 | 0.1018 | 87.5 |

## Per run (analyzer's own paired t-test on 25 slots within that run)

| Run folder | Task | AL_NC | AL_VC | delta | t | p |
|---|---|---|---|---|---|---|
| source_Skii_9_new_wordnetfailed_2_passed_3_1_pro | skii | 0.7384 | 0.6970 | +0.0414 | +2.099 | 0.047 |
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
| source_skii_10_1_old_wordnetfailed_2_passed_3_1_pro | skii | 0.7493 | 0.7187 | +0.0306 | +1.839 | 0.0808 |
| source_skii_2_passed_3_1 | skii | 0.7430 | 0.6970 | +0.0460 | +2.778 | 0.011 |
| source_skii_3_passed_but_new_wordnet_fail_3_1 | skii | 0.7523 | 0.6935 | +0.0588 | +3.182 | 0.00415 |
| source_skii_4_passed_3_1 | skii | 0.7539 | 0.6789 | +0.0750 | +4.053 | 0.000621 |
| source_skii_5_passed_3_1_pro | skii | 0.7599 | 0.7090 | +0.0509 | +2.405 | 0.025 |
| source_skii_6_passed_3_1_pro | skii | 0.7386 | 0.7072 | +0.0314 | +2.236 | 0.0376 |
| source_skii_7_2_passed_old_woprdnet_fail_3_1_pro | skii | 0.7474 | 0.7074 | +0.0400 | +1.407 | 0.172 |
| source_skii_8_2failed_bci_passed_3_1_pro | skii | 0.7436 | 0.7060 | +0.0376 | +1.779 | 0.0904 |
| source_snow0_passed_3_1_pro | skii | 0.7570 | 0.6934 | +0.0636 | +3.250 | 0.00383 |