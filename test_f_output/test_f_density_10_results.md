# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1831.38 | 1999.96 | 2161.79 |
| Ownership cost | 0.0 | 0.0 | 22.5 |
| Net surplus | 1831.38 | 1999.96 | 2139.29 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.7661 | 0.8048 | 0.8021 |
| Avg leakage cost | 0.2467 | 0.2041 | 0.1326 |
| Avg trust context | 0.432 | 0.4835 | 0.4638 |
| Final policy quality | 0.363 | 0.6419 | 0.8866 |
| Num owned | 0 | 0 | 3 |
| Portfolio value | 0 | 0 | 2.583 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.1681
- **rollup_vs_router_ratio**: 1.0697
- **router_vs_market_ratio**: 1.0921
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 0
- **value_b**: 0
- **value_ab**: 77.96
- **sum_parts**: 0
- **superlinearity_ratio**: None
- **is_superlinear**: False

## Diagnostic Checks

- **revelation_mq_increase_rate**: 1.0
- **diag1_pass**: True
- **revelation_leak_increase_rate**: 1.0
- **diag2_pass**: True
- **avg_trust_ctx_owned**: 0.8297
- **avg_trust_ctx_external**: 0.4507
- **diag3_pass**: True
- **actuator_exec_loss_corr**: -0.1993
- **diag4_pass**: True
- **rollup_policy_quality**: 0.8866
- **router_policy_quality**: 0.6419
- **diag5_pass**: True
- **early_external_surplus**: 3.2625
- **late_external_surplus**: 3.5032
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: PASS
- **P4_cross_node_learning**: PASS
- **P5_superlinearity_emergent**: FAIL
