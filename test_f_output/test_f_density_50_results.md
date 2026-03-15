# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1637.39 | 1805.68 | 2435.42 |
| Ownership cost | 0.0 | 0.0 | 112.5 |
| Net surplus | 1637.39 | 1805.68 | 2322.92 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.7672 | 0.8057 | 0.8328 |
| Avg leakage cost | 0.2521 | 0.208 | 0.0815 |
| Avg trust context | 0.4293 | 0.4827 | 0.4763 |
| Final policy quality | 0.3634 | 0.6423 | 1.0 |
| Num owned | 0 | 0 | 15 |
| Portfolio value | 0 | 0 | 10.9433 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.4187
- **rollup_vs_router_ratio**: 1.2865
- **router_vs_market_ratio**: 1.1028
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: True
- **value_a**: 76.22
- **value_b**: 344.01
- **value_ab**: 1030.86
- **sum_parts**: 420.23
- **superlinearity_ratio**: 2.4531
- **is_superlinear**: True

## Diagnostic Checks

- **revelation_mq_increase_rate**: 1.0
- **diag1_pass**: True
- **revelation_leak_increase_rate**: 1.0
- **diag2_pass**: True
- **avg_trust_ctx_owned**: 0.6998
- **avg_trust_ctx_external**: 0.3537
- **diag3_pass**: True
- **actuator_exec_loss_corr**: -0.3971
- **diag4_pass**: True
- **rollup_policy_quality**: 1.0
- **router_policy_quality**: 0.6423
- **diag5_pass**: True
- **early_external_surplus**: 3.2457
- **late_external_surplus**: 3.5725
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: PASS
- **P2_leakage_advantage**: PASS
- **P3_trust_context_ownership**: PASS
- **P4_cross_node_learning**: PASS
- **P5_superlinearity_emergent**: PASS
