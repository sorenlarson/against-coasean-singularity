# TEST_E Results

Full instrumentation improved workflow selection and CFO estimation relative to weaker regimes. The staged ROI model suggests ops-focused instrumentation can clear breakeven earlier, while broader measurement layers need longer horizons or additional strategic value to justify their cost.

## Compression Prioritization

| Regime | Realized net value | Regret | Top-5 hit rate | Rank correlation |
|---|---|---|---|---|
| full_action_log | -26762.25 | 0.0 | 1.0 | 1.0 |
| weak_instrumentation | -62234.83 | 35472.58 | 0.6 | 0.982 |
| heuristic_baseline | -143056.15 | 116293.9 | 0.2 | None |

## CFO Estimation

| Regime | Estimated current hours | Hours error % | Threshold month error |
|---|---|---|---|
| full_action_log | 6.99 | 0.0 | 0.0 |
| weak_instrumentation | 27.67 | 295.76 | 0.0 |
| heuristic_baseline | 9.4 | 34.48 | 0.0 |

## Causal Support Quality

| Regime | Mean estimate hours | Mean bias hours | Mean abs bias % | Estimate SD | Sign accuracy | Mean p-value | Pretrend pass rate |
|---|---|---|---|---|---|---|---|
| full_action_log | 5.75 | 0.75 | 14.94 | 0.0 | 1.0 | 0.623 | 1.0 |
| weak_instrumentation | 3.59 | -1.41 | 28.14 | 0.0 | 1.0 | 0.366 | 1.0 |
| heuristic_baseline | 17.14 | 12.14 | 242.82 | 0.0 | 1.0 | None | None |

## Staged ROI

| Scenario | Tier | Horizon years | Total value | Cost | ROI | CFO error reduction | Causal bias reduction |
|---|---|---|---|---|---|---|---|
| conservative | ops_only | 1 | 109064.51 | 30000.0 | 2.635 | 34.48 | 227.88 |
| conservative | full_measurement | 1 | 110664.51 | 70000.0 | 0.581 | 34.48 | 227.88 |
| conservative | causal_ready | 1 | 112464.51 | 120000.0 | -0.063 | 34.48 | 227.88 |
| conservative | ops_only | 2 | 218129.02 | 30000.0 | 6.271 | 34.48 | 227.88 |
| conservative | full_measurement | 2 | 221329.02 | 70000.0 | 2.162 | 34.48 | 227.88 |
| conservative | causal_ready | 2 | 224929.02 | 120000.0 | 0.874 | 34.48 | 227.88 |
| base | ops_only | 1 | 365381.7 | 30000.0 | 11.179 | 34.48 | 227.88 |
| base | full_measurement | 1 | 372381.7 | 70000.0 | 4.32 | 34.48 | 227.88 |
| base | causal_ready | 1 | 383381.7 | 120000.0 | 2.195 | 34.48 | 227.88 |
| base | ops_only | 2 | 730763.4 | 30000.0 | 23.359 | 34.48 | 227.88 |
| base | full_measurement | 2 | 744763.4 | 70000.0 | 9.639 | 34.48 | 227.88 |
| base | causal_ready | 2 | 766763.4 | 120000.0 | 5.39 | 34.48 | 227.88 |
| aggressive | ops_only | 1 | 608469.5 | 30000.0 | 19.282 | 34.48 | 227.88 |
| aggressive | full_measurement | 1 | 624669.5 | 70000.0 | 7.924 | 34.48 | 227.88 |
| aggressive | causal_ready | 1 | 650769.5 | 120000.0 | 4.423 | 34.48 | 227.88 |
| aggressive | ops_only | 2 | 1216939.0 | 30000.0 | 39.565 | 34.48 | 227.88 |
| aggressive | full_measurement | 2 | 1249339.0 | 70000.0 | 16.848 | 34.48 | 227.88 |
| aggressive | causal_ready | 2 | 1301539.0 | 120000.0 | 9.846 | 34.48 | 227.88 |

## ROI Drivers

| Assumption | Full ROI base | Full ROI low/high | Full ROI swing | Causal ROI base | Causal ROI low/high | Causal ROI swing |
|---|---|---|---|---|---|---|
| workflow_selection_rounds_per_year | 4.32 | 2.654 / 5.986 | 1.666 | 2.195 | 1.223 / 3.167 | 0.972 |
| full_measurement_cost | 4.32 | 5.65 / 3.433 | 1.33 | 2.195 | 2.195 / 2.195 | 0.0 |
| decision_capture_multiplier | 4.32 | 3.074 / 5.566 | 1.246 | 2.195 | 1.468 / 2.922 | 0.727 |
| analytics_hourly_rate | 4.32 | 4.253 / 4.387 | 0.067 | 2.195 | 2.137 / 2.252 | 0.058 |
| causal_ready_cost | 4.32 | 4.32 / 4.32 | 0.0 | 2.195 | 2.994 / 1.662 | 0.799 |
