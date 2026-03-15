# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1795.14 | 1962.29 | 2193.81 |
| Ownership cost | 0.0 | 0.0 | 45.0 |
| Net surplus | 1795.14 | 1962.29 | 2148.81 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.7672 | 0.8059 | 0.8116 |
| Avg leakage cost | 0.246 | 0.2034 | 0.133 |
| Avg trust context | 0.4301 | 0.4832 | 0.4637 |
| Final policy quality | 0.3633 | 0.6423 | 1.0 |
| Num owned | 0 | 0 | 6 |
| Portfolio value | 0 | 0 | 4.9717 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.197
- **rollup_vs_router_ratio**: 1.0951
- **router_vs_market_ratio**: 1.0931
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 79.01
- **value_b**: 0
- **value_ab**: 79.01
- **sum_parts**: 79.01
- **superlinearity_ratio**: 1.0
- **is_superlinear**: False

## Diagnostic Checks

- **revelation_mq_increase_rate**: 1.0
- **diag1_pass**: True
- **revelation_leak_increase_rate**: 1.0
- **diag2_pass**: True
- **avg_trust_ctx_owned**: 0.833
- **avg_trust_ctx_external**: 0.4511
- **diag3_pass**: True
- **actuator_exec_loss_corr**: -0.2065
- **diag4_pass**: True
- **rollup_policy_quality**: 1.0
- **router_policy_quality**: 0.6423
- **diag5_pass**: True
- **early_external_surplus**: 3.2881
- **late_external_surplus**: 3.5666
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: PASS
- **P4_cross_node_learning**: PASS
- **P5_superlinearity_emergent**: FAIL
