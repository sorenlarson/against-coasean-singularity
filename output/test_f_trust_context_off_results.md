# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1550.76 | 1707.56 | 2007.27 |
| Ownership cost | 0.0 | 0.0 | 76.31 |
| Net surplus | 1550.76 | 1707.56 | 1930.96 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.6836 | 0.7206 | 0.7363 |
| Avg leakage cost | 0.246 | 0.2031 | 0.1118 |
| Avg trust context | 0.0 | 0.0 | 0.0 |
| Final policy quality | 0.3388 | 0.6052 | 1.0 |
| Num owned | 0 | 0 | 12 |
| Portfolio value | 0 | 0 | 8.9986 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.2452
- **rollup_vs_router_ratio**: 1.1308
- **router_vs_market_ratio**: 1.1011
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 153.14
- **value_b**: 100.8
- **value_ab**: 407.58
- **sum_parts**: 253.94
- **superlinearity_ratio**: 1.605
- **is_superlinear**: True

## Acquisition Path

| Time Step | Node | EMV Score | Owned After |
|---|---|---|---|
| 5 | 18 | 2.1578 | 4 |
| 10 | 23 | 2.1585 | 5 |
| 15 | 8 | 2.2608 | 6 |
| 20 | 7 | 2.0378 | 7 |
| 25 | 17 | 2.1324 | 8 |
| 30 | 21 | 2.0881 | 9 |
| 35 | 9 | 2.0313 | 10 |
| 40 | 13 | 1.9488 | 11 |
| 45 | 2 | 2.1735 | 12 |

## Diagnostic Checks

- **revelation_mq_increase_rate**: 1.0
- **diag1_pass**: True
- **revelation_leak_increase_rate**: 1.0
- **diag2_pass**: True
- **avg_trust_ctx_owned**: 0.0
- **avg_trust_ctx_external**: 0.0
- **diag3_pass**: False
- **actuator_exec_loss_corr**: -0.2604
- **diag4_pass**: True
- **rollup_policy_quality**: 1.0
- **router_policy_quality**: 0.6052
- **diag5_pass**: True
- **early_external_surplus**: 2.883
- **late_external_surplus**: 3.2454
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: FAIL
- **P4_cross_node_learning**: PASS
- **P5_superlinearity_emergent**: PASS
