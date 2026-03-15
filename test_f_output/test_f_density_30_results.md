# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1773.51 | 1941.8 | 2237.97 |
| Ownership cost | 0.0 | 0.0 | 67.5 |
| Net surplus | 1773.51 | 1941.8 | 2170.47 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.7689 | 0.8079 | 0.8165 |
| Avg leakage cost | 0.2516 | 0.2064 | 0.1156 |
| Avg trust context | 0.4317 | 0.4839 | 0.4665 |
| Final policy quality | 0.3638 | 0.6431 | 1.0 |
| Num owned | 0 | 0 | 9 |
| Portfolio value | 0 | 0 | 7.1721 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.2238
- **rollup_vs_router_ratio**: 1.1178
- **router_vs_market_ratio**: 1.0949
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 79.1
- **value_b**: 126.18
- **value_ab**: 309.01
- **sum_parts**: 205.28
- **superlinearity_ratio**: 1.5053
- **is_superlinear**: True

## Diagnostic Checks

- **revelation_mq_increase_rate**: 1.0
- **diag1_pass**: True
- **revelation_leak_increase_rate**: 1.0
- **diag2_pass**: True
- **avg_trust_ctx_owned**: 0.7619
- **avg_trust_ctx_external**: 0.4272
- **diag3_pass**: True
- **actuator_exec_loss_corr**: -0.1879
- **diag4_pass**: True
- **rollup_policy_quality**: 1.0
- **router_policy_quality**: 0.6431
- **diag5_pass**: True
- **early_external_surplus**: 3.2785
- **late_external_surplus**: 3.5734
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: PASS
- **P4_cross_node_learning**: PASS
- **P5_superlinearity_emergent**: PASS
