# Test F: Ablation Results

## Cross-Experiment Surplus Comparison

| Experiment | Market | Router | Rollup | Rollup/Router |
|---|---|---|---|---|
| baseline | 1787.27 | 1953.79 | 2155.03 | 1.103 |
| low_tx_costs | 1854.12 | 1990.89 | 2208.29 | 1.1092 |
| leakage_off | 1940.84 | 2083.37 | 2231.65 | 1.0712 |
| trust_context_off | 1550.76 | 1707.56 | 1930.96 | 1.1308 |
| actuator_off | 1787.27 | 1921.97 | 2147.14 | 1.1172 |
| learning_off | 1787.27 | 1953.79 | 2040.51 | 1.0444 |
| complementarity_on | 1908.91 | 2062.81 | 2247.53 | 1.0895 |
| all_off | 1806.98 | 1901.88 | 1873.52 | 0.9851 |
| router_no_shielding | 1787.27 | 1932.6 | 2155.03 | 1.1151 |

## Proposition Verdicts Across Experiments

| Experiment | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|
| baseline | PASS | PASS | PASS | PASS | PASS |
| low_tx_costs | PASS | PASS | PASS | PASS | PASS |
| leakage_off | PASS | FAIL | PASS | PASS | PASS |
| trust_context_off | PASS | PASS | FAIL | PASS | PASS |
| actuator_off | PASS | PASS | PASS | PASS | PASS |
| learning_off | PASS | PASS | PASS | FAIL | PASS |
| complementarity_on | PASS | PASS | PASS | PASS | PASS |
| all_off | FAIL | FAIL | FAIL | FAIL | FAIL |
| router_no_shielding | PASS | PASS | PASS | PASS | PASS |

## Rollup/Router Ratio Changes from Baseline

| Experiment | Ratio | Change |
|---|---|---|
| low_tx_costs | 1.1092 | 0.0062 |
| leakage_off | 1.0712 | -0.0318 |
| trust_context_off | 1.1308 | 0.0278 |
| actuator_off | 1.1172 | 0.0142 |
| learning_off | 1.0444 | -0.0586 |
| complementarity_on | 1.0895 | -0.0135 |
| all_off | 0.9851 | -0.1179 |
| router_no_shielding | 1.1151 | 0.0121 |

## All-Off Sanity Check

- Max/min surplus ratio: 1.0525
- Pass (< 1.3): YES

## Complementarity Effect on Superlinearity

- Baseline superlinearity ratio: 1.4982
- With complementarity: 1.4973

## Ownership Density Sweep

| Ownership % | Nodes | Rollup | Router | Market | Rollup/Router | Rollup/Market | Leakage | Superlinearity | P1 |
|---|---|---|---|---|---|---|---|---|---|
| 10% | 3 | 2139.29 | 1999.96 | 1831.38 | 1.0697 | 1.1681 | 0.1326 | None | PASS |
| 20% | 6 | 2148.81 | 1962.29 | 1795.14 | 1.0951 | 1.197 | 0.133 | 1.0 | PASS |
| 30% | 9 | 2170.47 | 1941.8 | 1773.51 | 1.1178 | 1.2238 | 0.1156 | 1.5053 | PASS |
| 50% | 15 | 2322.92 | 1805.68 | 1637.39 | 1.2865 | 1.4187 | 0.0815 | 2.4531 | PASS |
| 70% | 21 | 2487.46 | 1707.33 | 1540.58 | 1.4569 | 1.6146 | 0.0598 | 1.9571 | PASS |

## Ownership Cost Sensitivity

| Cost/Node/Step | Rollup Gross | Ownership Cost | Rollup Net | Router | Rollup/Router | P1 |
|---|---|---|---|---|---|---|
| 0.0 | 2231.35 | 57.56 | 2173.78 | 1953.79 | 1.1126 | PASS |
| 0.025 | 2231.35 | 66.94 | 2164.41 | 1953.79 | 1.1078 | PASS |
| 0.05 | 2231.35 | 76.31 | 2155.03 | 1953.79 | 1.103 | PASS |
| 0.075 | 2231.35 | 85.69 | 2145.66 | 1953.79 | 1.0982 | PASS |
| 0.1 | 2231.35 | 95.06 | 2136.28 | 1953.79 | 1.0934 | PASS |
| 0.15 | 2231.35 | 113.81 | 2117.53 | 1953.79 | 1.0838 | PASS |
| 0.2 | 2231.35 | 132.56 | 2098.78 | 1953.79 | 1.0742 | PASS |
| 0.3 | 2231.35 | 170.06 | 2061.28 | 1953.79 | 1.055 | PASS |
