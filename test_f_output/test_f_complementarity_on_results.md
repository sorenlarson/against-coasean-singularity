# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1908.91 | 2062.81 | 2323.85 |
| Ownership cost | 0.0 | 0.0 | 76.31 |
| Net surplus | 1908.91 | 2062.81 | 2247.53 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.8123 | 0.8463 | 0.8458 |
| Avg leakage cost | 0.2364 | 0.1981 | 0.1086 |
| Avg trust context | 0.4315 | 0.4836 | 0.465 |
| Final policy quality | 0.3762 | 0.6586 | 1.0 |
| Num owned | 0 | 0 | 12 |
| Portfolio value | 0 | 0 | 8.9986 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.1774
- **rollup_vs_router_ratio**: 1.0895
- **router_vs_market_ratio**: 1.0806
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 157.35
- **value_b**: 118.72
- **value_ab**: 413.37
- **sum_parts**: 276.07
- **superlinearity_ratio**: 1.4973
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
- **avg_trust_ctx_owned**: 0.7426
- **avg_trust_ctx_external**: 0.4275
- **diag3_pass**: True
- **actuator_exec_loss_corr**: -0.2624
- **diag4_pass**: True
- **rollup_policy_quality**: 1.0
- **router_policy_quality**: 0.6586
- **diag5_pass**: True
- **early_external_surplus**: 3.4347
- **late_external_surplus**: 3.6859
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: PASS
- **P4_cross_node_learning**: PASS
- **P5_superlinearity_emergent**: PASS
