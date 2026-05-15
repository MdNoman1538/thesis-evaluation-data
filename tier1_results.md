# Tier 1 Analyses — Empirical Core of Chapter 4

Inputs: 661 stimulus records from `evaluation_log.jsonl`.
All values computed with the project's `semantic_analyzer` module (Brysbaert 40 k-word ratings on the original 1–5 scale; WordNet hypernym depth using the shortest path to root for the most-abstract synset).

## A1. Per-condition distributions

Figures saved as `figures/brysbaert_distribution.pdf`, `figures/wordnet_distribution.pdf`, `figures/per_condition_box.pdf` (PNG copies for previewing).

### Brysbaert

| Cond | n | mean | SD | min | Q25 | median | Q75 | max |
|------|---|------|----|-----|-----|--------|-----|-----|
| NC | 661 | 3.004 | 0.100 | 2.717 | 2.935 | 3.008 | 3.066 | 3.318 |
| MC | 661 | 3.310 | 0.097 | 3.003 | 3.255 | 3.305 | 3.362 | 3.648 |
| VC | 661 | 3.943 | 0.126 | 3.381 | 3.854 | 3.934 | 4.034 | 4.322 |

### WordNet

| Cond | n | mean | SD | min | Q25 | median | Q75 | max |
|------|---|------|----|-----|-----|--------|-----|-----|
| NC | 661 | 5.924 | 0.218 | 5.289 | 5.775 | 5.949 | 6.075 | 6.658 |
| MC | 661 | 6.041 | 0.265 | 5.522 | 5.861 | 6.045 | 6.220 | 6.969 |
| VC | 661 | 6.484 | 0.260 | 5.675 | 6.295 | 6.447 | 6.644 | 7.170 |

## A2/A3. Paired t-tests and effect sizes

Each row is a paired comparison across the 661 records that have all three conditions. *p* < 0.05 starred; Cohen's d uses standard deviation of the paired differences.

### Brysbaert

| Comparison | n | mean diff | t | p | Cohen's d | Effect |
|------------|---|-----------|---|---|-----------|--------|
| NC vs MC | 661 | +0.305 | -59.098 | 8.57e-266 * | -2.300 | large |
| MC vs VC | 661 | +0.634 | -116.018 | 0 * | -4.516 | large |
| NC vs VC | 661 | +0.939 | -162.920 | 0 * | -6.342 | large |

### WordNet

| Comparison | n | mean diff | t | p | Cohen's d | Effect |
|------------|---|-----------|---|---|-----------|--------|
| NC vs MC | 661 | +0.117 | -9.289 | 2.22e-19 * | -0.362 | small |
| MC vs VC | 661 | +0.443 | -40.729 | 2.98e-182 * | -1.585 | large |
| NC vs VC | 661 | +0.560 | -45.960 | 7.28e-208 * | -1.789 | large |

## E1. Repeatability across regenerations

Each row is a (task, model) group with 2+ runs. SD = standard deviation of the per-stimulus mean across those runs. Low SD = stable behaviour.

| Task | Model | n runs | NC Brys SD | MC Brys SD | VC Brys SD | NC WN SD | MC WN SD | VC WN SD | NC wc SD | VC wc SD |
|------|-------|--------|-----------|-----------|-----------|----------|----------|----------|---------|---------|
| A saree ( women cloathing) | gemini-3.1-pro-preview | 24 | 0.110 | 0.138 | 0.044 | 0.137 | 0.074 | 0.144 | 0.500 | 5.408 |
| Design a device to shell peanuts. | gemini-3.1-pro-preview | 302 | 0.088 | 0.081 | 0.104 | 0.222 | 0.198 | 0.189 | 2.293 | 4.752 |
| Design a rain coat | gemini-2.5-pro | 3 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
| Design a social-oriented furniture. | gemini-3.1-pro-preview | 32 | 0.067 | 0.056 | 0.125 | 0.150 | 0.230 | 0.128 | 2.193 | 6.544 |
| Design an amphibious bike. | gemini-3.1-pro-preview | 183 | 0.085 | 0.066 | 0.117 | 0.191 | 0.204 | 0.275 | 4.245 | 30.420 |
| Local rehabilitation center helps thousands of stroke patients each year. Many stroke patients are unable to perform bilateral tasks, meaning they have limited or no use of one upper extremity (arm/shoulder). Being able to open jars and lidded food containers is important for living independently. You are a designer, and your task is to design a personal tool that helps patients open lidded food containers | gemini-3-flash-preview | 3 | 0.008 | 0.108 | 0.050 | 0.096 | 0.277 | 0.102 | 2.055 | 2.055 |
| Local rehabilitation center helps thousands of stroke patients each year. Many stroke patients are unable to perform bilateral tasks, meaning they have limited or no use of one upper extremity (arm/shoulder). Being able to open jars and lidded food containers is important for living independently. You are a designer, and your task is to design a personal tool that helps patients open lidded food containers | gemini-3.1-pro-preview | 23 | 0.092 | 0.144 | 0.118 | 0.247 | 0.233 | 0.195 | 7.050 | 8.266 |
| Local rehabilitation center helps thousands of stroke patients each year. Many stroke patients are unable to perform bilateral tasks, meaning they have limited or no use of one upper extremity (arm/shoulder). Being able to open jars and lidded food containers is important for living independently. You are a designer, and your task is to design a personal tool that helps patients open lidded food containers. | gemini-2.5-pro | 4 | 0.160 | 0.050 | 0.091 | 0.297 | 0.092 | 0.155 | 10.425 | 10.607 |
| Local rehabilitation center helps thousands of stroke patients each year. Many stroke patients are unable to perform bilateral tasks, meaning they have limited or no use of one upper extremity (arm/shoulder). Being able to open jars and lidded food containers is important for living independently. You are a designer, and your task is to design a personal tool that helps patients open lidded food containers. | gemini-3-flash-preview | 3 | 0.159 | 0.010 | 0.019 | 0.069 | 0.024 | 0.159 | 10.143 | 10.614 |
| Local rehabilitation center helps thousands of stroke patients each year. Many stroke patients are unable to perform bilateral tasks, meaning they have limited or no use of one upper extremity (arm/shoulder). Being able to open jars and lidded food containers is important for living independently. You are a designer, and your task is to design a personal tool that helps patients open lidded food containers. | gemini-3.1-pro-preview | 5 | 0.088 | 0.130 | 0.109 | 0.146 | 0.138 | 0.135 | 1.744 | 4.940 |
| Local rehabilitation center helps thousands of stroke patients each year. Many stroke patients are unable to perform bilateral tasks, meaning they have limited or no use of one upper extremity (arm/shoulder). Being able to open jars and lidded food containers is important for living independently. You are a designer, and your task is to design a personal tool that helps patients open lidded food containers. The design should reach the following requirements: | gemini-3.1-pro-preview | 2 | 0.090 | 0.145 | 0.195 | 0.336 | 0.111 | 0.165 | 1.000 | 6.000 |
| The local rehabilitation center helps to treat thousands of stroke patients each year. Many individuals who have had a stroke are unable to perform bilateral tasks, meaning they have limited or no use of one upper extremity (arm/shoulder). A common issue the hospital has observed with their stroke patients is their inability to open jars and other lidded food containers, which is particularly important for patients living on their own. Your task is to design a personal tool that helps patients open lidded food containers. | gemini-2.5-pro | 2 | 0.023 | 0.154 | 0.037 | 0.172 | 0.127 | 0.134 | 1.500 | 5.000 |
| The local rehabilitation center helps to treat thousands of stroke patients each year. Many individuals who have had a stroke are unable to perform bilateral tasks, meaning they have limited or no use of one upper extremity (arm/shoulder). A common issue the hospital has observed with their stroke patients is their inability to open jars and other lidded food containers, which is particularly important for patients living on their own. Your task is to design a personal tool that helps patients open lidded food containers. | gemini-3.1-pro-preview | 8 | 0.085 | 0.098 | 0.117 | 0.125 | 0.102 | 0.179 | 4.689 | 7.280 |
| Today ski and snowboard are widely used as personal transportation tools on snow. But, to be able to use them, a lot of skill and experience is required that normally a user cannot learn within one day. Moreover, ski and snowboard cannot run uphill because they are moved by the gravity. Your task is to design other options of personal tools for transporting on snow. | gemini-2.5-pro | 8 | 0.094 | 0.046 | 0.125 | 0.192 | 0.165 | 0.196 | 4.166 | 7.017 |
| Today, skiing and snowboarding are widely used as personal transportation tools on snow. But to use them, a lot of skill and experience are required, which a user normally cannot learn in one day. Moreover, skis and snowboards cannot run uphill because they are moved by gravity. You are a designer, and your task is to design alternative personal tools for snow transport | gemini-2.5-flash | 2 | 0.072 | 0.079 | 0.087 | 0.155 | 0.199 | 0.177 | 4.500 | 5.500 |
| Today, skiing and snowboarding are widely used as personal transportation tools on snow. But to use them, a lot of skill and experience are required, which a user normally cannot learn in one day. Moreover, skis and snowboards cannot run uphill because they are moved by gravity. You are a designer, and your task is to design alternative personal tools for snow transport | gemini-2.5-pro | 5 | 0.116 | 0.057 | 0.051 | 0.206 | 0.180 | 0.211 | 5.154 | 2.135 |
| Today, skiing and snowboarding are widely used as personal transportation tools on snow. But to use them, a lot of skill and experience are required, which a user normally cannot learn in one day. Moreover, skis and snowboards cannot run uphill because they are moved by gravity. You are a designer, and your task is to design alternative personal tools for snow transport | gemini-3.1-pro-preview | 13 | 0.100 | 0.090 | 0.122 | 0.148 | 0.193 | 0.264 | 4.227 | 9.980 |
| Today, skiing and snowboarding are widely used as personal transportation tools on snow. But to use them, a lot of skill and experience are required, which a user normally cannot learn in one day. Moreover, skis and snowboards cannot run uphill because they are moved by gravity. You are a designer, and your task is to design alternative personal tools for snow transport. | gemini-2.5-pro | 3 | 0.130 | 0.017 | 0.141 | 0.373 | 0.117 | 0.366 | 5.907 | 7.846 |
| Today, skiing and snowboarding are widely used as personal transportation tools on snow. But to use them, a lot of skill and experience are required, which a user normally cannot learn in one day. Moreover, skis and snowboards cannot run uphill because they are moved by gravity. You are a designer, and your task is to design alternative personal tools for snow transport. | gemini-3-flash-preview | 18 | 0.104 | 0.152 | 0.140 | 0.225 | 0.226 | 0.260 | 4.716 | 4.604 |
| Today, skiing and snowboarding are widely used as personal transportation tools on snow. But to use them, a lot of skill and experience are required, which a user normally cannot learn in one day. Moreover, skis and snowboards cannot run uphill because they are moved by gravity. You are a designer, and your task is to design alternative personal tools for snow transport. | gemini-3.1-pro-preview | 11 | 0.091 | 0.099 | 0.065 | 0.107 | 0.231 | 0.186 | 4.070 | 4.070 |
| design a raincoat | gemini-3.1-pro-preview | 6 | 0.051 | 0.012 | 0.045 | 0.140 | 0.011 | 0.216 | 0.500 | 1.500 |
