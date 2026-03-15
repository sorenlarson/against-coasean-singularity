# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1859.21 | 1605.48 | 2195.33 |
| Ownership cost | 0.0 | 0.0 | 76.31 |
| Net surplus | 1859.21 | 1605.48 | 2119.02 |
| Total coordinations | 603 | 586 | 638 |
| Avg match quality | 0.7672 | 0.8035 | 0.8117 |
| Avg leakage cost | 0.2517 | 0.7566 | 0.1203 |
| Avg trust context | 0.4476 | 0.4828 | 0.4655 |
| Final policy quality | 0.3634 | 0.6386 | 1.0 |
| Num owned | 0 | 0 | 12 |
| Portfolio value | 0 | 0 | 8.9986 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.1397
- **rollup_vs_router_ratio**: 1.3199
- **router_vs_market_ratio**: 0.8635
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 126.36
- **value_b**: 98.76
- **value_ab**: 332.83
- **sum_parts**: 225.12
- **superlinearity_ratio**: 1.4784
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
- **avg_trust_ctx_owned**: 0.7469
- **avg_trust_ctx_external**: 0.4324
- **diag3_pass**: True
- **actuator_exec_loss_corr**: -0.3265
- **diag4_pass**: True
- **rollup_policy_quality**: 1.0
- **router_policy_quality**: 0.6386
- **diag5_pass**: True
- **early_external_surplus**: 3.2644
- **late_external_surplus**: 3.5572
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: PASS
- **P4_cross_node_learning**: PASS
- **P5_superlinearity_emergent**: PASS
