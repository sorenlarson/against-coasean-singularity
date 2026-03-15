# Test F: Cybernetic Arbitrage Results

## Regime Comparison

| Metric | Market | Router | Rollup |
|---|---|---|---|
| Gross surplus | 1806.98 | 1901.88 | 1873.52 |
| Ownership cost | 0.0 | 0.0 | 0.0 |
| Net surplus | 1806.98 | 1901.88 | 1873.52 |
| Total coordinations | 616 | 625 | 638 |
| Avg match quality | 0.6822 | 0.7028 | 0.6766 |
| Avg leakage cost | 0.0 | 0.0 | 0.0 |
| Avg trust context | 0.0 | 0.0 | 0.0 |
| Final policy quality | 0.3383 | 0.5971 | 0.3369 |
| Num owned | 0 | 0 | 0 |
| Portfolio value | 0 | 0 | 0 |

## Cross-Regime Comparisons

- **rollup_vs_market_ratio**: 1.0368
- **rollup_vs_router_ratio**: 0.9851
- **router_vs_market_ratio**: 1.0525
- **router_trust_investment_cost**: 97.0

## Superlinearity Test

- **tested**: False
- **reason**: too few owned nodes

## Diagnostic Checks

- **revelation_mq_increase_rate**: 1.0
- **diag1_pass**: True
- **revelation_leak_increase_rate**: 0.0
- **diag2_pass**: False
- **diag3_pass**: None
- **actuator_exec_loss_corr**: -0.2232
- **diag4_pass**: True
- **rollup_policy_quality**: 0.3369
- **router_policy_quality**: 0.5971
- **diag5_pass**: False
- **early_external_surplus**: 2.8817
- **late_external_surplus**: 2.9914
- **diag6_pass**: True

## Proposition Verdicts

- **P1_rollup_highest_surplus**: FAIL
- **P2_leakage_advantage**: FAIL
- **P3_trust_context_ownership**: FAIL
- **P4_cross_node_learning**: FAIL
- **P5_superlinearity_emergent**: FAIL
