# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1787.27 | 1953.79 | 2116.82 |
| Ownership cost | 0.0 | 0.0 | 76.31 |
| Net surplus | 1787.27 | 1953.79 | 2040.51 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.7676 | 0.8069 | 0.7728 |
| Avg leakage cost | 0.2467 | 0.2035 | 0.1159 |
| Avg trust context | 0.4308 | 0.4832 | 0.4654 |
| Final policy quality | 0.3634 | 0.6427 | 0.4191 |
| Num owned | 0 | 0 | 12 |
| Portfolio value | 0 | 0 | 8.9986 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.1417
- **rollup_vs_router_ratio**: 1.0444
- **router_vs_market_ratio**: 1.0932
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 160.28
- **value_b**: 109.78
- **value_ab**: 400.24
- **sum_parts**: 270.06
- **superlinearity_ratio**: 1.482
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
- **avg_trust_ctx_owned**: 0.7437
- **avg_trust_ctx_external**: 0.4255
- **diag3_pass**: True
- **actuator_exec_loss_corr**: -0.27
- **diag4_pass**: True
- **rollup_policy_quality**: 0.4191
- **router_policy_quality**: 0.6427
- **diag5_pass**: False
- **early_external_surplus**: 3.1686
- **late_external_surplus**: 3.2835
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: PASS
- **P4_cross_node_learning**: FAIL
- **P5_superlinearity_emergent**: PASS
