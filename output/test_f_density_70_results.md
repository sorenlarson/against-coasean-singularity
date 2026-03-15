# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1540.58 | 1707.33 | 2644.96 |
| Ownership cost | 0.0 | 0.0 | 157.5 |
| Net surplus | 1540.58 | 1707.33 | 2487.46 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.7672 | 0.8061 | 0.8447 |
| Avg leakage cost | 0.2523 | 0.2081 | 0.0598 |
| Avg trust context | 0.4295 | 0.4827 | 0.487 |
| Final policy quality | 0.3633 | 0.6424 | 1.0 |
| Num owned | 0 | 0 | 21 |
| Portfolio value | 0 | 0 | 13.674 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.6146
- **rollup_vs_router_ratio**: 1.4569
- **router_vs_market_ratio**: 1.1082
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 388.86
- **value_b**: 519.88
- **value_ab**: 1778.51
- **sum_parts**: 908.74
- **superlinearity_ratio**: 1.9571
- **is_superlinear**: True

## Diagnostic Checks

- **revelation_mq_increase_rate**: 1.0
- **diag1_pass**: True
- **revelation_leak_increase_rate**: 1.0
- **diag2_pass**: True
- **avg_trust_ctx_owned**: 0.611
- **avg_trust_ctx_external**: 0.309
- **diag3_pass**: True
- **actuator_exec_loss_corr**: -0.4344
- **diag4_pass**: True
- **rollup_policy_quality**: 1.0
- **router_policy_quality**: 0.6424
- **diag5_pass**: True
- **early_external_surplus**: 3.1511
- **late_external_surplus**: 3.463
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: PASS
- **P4_cross_node_learning**: PASS
- **P5_superlinearity_emergent**: PASS
