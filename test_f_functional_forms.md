# Test F Functional Forms

## Implementable First-Pass Equations for the Cybernetic Arbitrage Simulation

This document specifies first-pass functional forms for the primitives defined in:

- [test_f_model_primitives.md](/Users/soren/Downloads/aivc-action-log-codex/outputs/test_f_model_primitives.md)

The goal is not to claim these equations are uniquely correct. The goal is to choose forms that:

- preserve the theory note's logic
- isolate the important channels
- are easy to implement and debug
- are flexible enough for later sensitivity analysis

## 1. General design principles

The first implementation should prefer:

- bounded functions
- low-dimensional parameters
- monotonic relationships that are economically interpretable
- no black-box learning model in v1

Recommended implementation primitives:

- linear combinations for latent scores
- logistic transforms for probabilities
- capped linear functions for realization terms
- exponential decay for persistence

## 2. Match quality

We want match quality to rise with:

- base compatibility
- more revealed context
- more trust-generated context
- better policy quality
- stronger actuator realization

We also want diminishing returns to revelation.

### Proposed form

Define a context-fit term:

`context_fit_ij(t) = w_d * match(demand_i, capacity_j) + w_u * urgency_i + w_q * (1 - quality_risk_j) + w_e * (1 - exception_i)`

where `match(demand_i, capacity_j)` can be:

`match(demand_i, capacity_j) = 1 - abs(demand_i - capacity_j)`

assuming variables are normalized to `[0, 1]`.

Then define:

`z_match_ij(t) = a0 + a1 * log(1 + b_r * r_ij(t)) + a2 * trust_context_ij(t) + a3 * policy_quality_term(t) + a4 * actuator_term_ij(t) + a5 * complementarity_ij + a6 * context_fit_ij(t)`

Finally:

`match_quality_ij(t) = sigmoid(z_match_ij(t))`

where:

`sigmoid(x) = 1 / (1 + exp(-x))`

### Why this works

- `log(1 + b_r * r)` gives diminishing returns to revelation
- policy, trust, and actuator effects remain additive and interpretable
- output is bounded between `0` and `1`

## 3. Leakage cost

Leakage should:

- rise with revelation
- rise with edge-specific leakage sensitivity
- rise with price sensitivity and hidden alpha
- persist through time

### Proposed instantaneous form

`instant_leakage_ij(t) = lambda_L * r_ij(t)^gamma * leakage_sensitivity_ij * (0.5 * price_sensitivity_i(t) + 0.5 * hidden_alpha_i(t)) * market_visibility_ij(t)`

where:

- `gamma > 1` makes leakage convex in revelation
- `market_visibility_ij(t)` is a scalar in `[0, 1]`

### Persistent stock

`leak_stock_i(t+1) = rho_L * leak_stock_i(t) + instant_leakage_ij(t)`

with `rho_L` in `[0, 1]`.

### Cost realized in current period

`leakage_cost_ij(t) = instant_leakage_ij(t) + phi_L * leak_stock_i(t)`

This means each new disclosure is costly now and also raises the future cost of transacting externally.

## 4. Trust-generated context

We want trust-generated context to emerge only when:

- trust is high enough
- the edge requires trust
- the node is capable of generating such context
- the interaction mode supports it

### Interaction mode

Set:

- `interaction_mode = 1.0` for owned internal interaction
- `interaction_mode = 0.6` for trusted edge-router interaction
- `interaction_mode = 0.2` for ordinary external market interaction

### Proposed form

`z_trust_ij(t) = beta0 + beta1 * trust_ij(t) + beta2 * trust_profile_i - beta3 * trust_requirement_ij + beta4 * interaction_mode_ij(t)`

`trust_activation_ij(t) = sigmoid(z_trust_ij(t))`

Then:

`trust_context_ij(t) = trust_activation_ij(t) * hidden_alpha_i(t)`

This means:

- trust-generated context is proportional to the high-value hidden context available at the node
- but it only becomes legible when the trust/interaction conditions are right

## 5. Actuator term

Actuator access should raise the conversion of matched intent into realized execution.

### Regime multipliers

Let:

- `regime_mult = 0.5` for fragmented market
- `regime_mult = 0.7` for external router
- `regime_mult = 1.0` for internal rollup coordination

### Proposed form

`actuator_term_ij(t) = regime_mult * (0.5 * actuator_strength_i + 0.5 * actuator_strength_j)`

Bound to `[0, 1]`.

This gives the rollup an execution advantage even with identical local actuator strengths because its regime allows deeper control.

## 6. Execution loss

Execution loss should:

- rise with baseline execution risk
- rise with exceptions and quality risk
- fall with stronger actuator term

### Proposed form

`execution_loss_ij(t) = lambda_E * exec_risk_ij * (0.5 * exception_i(t) + 0.5 * quality_risk_j(t)) * (1 - actuator_term_ij(t))`

This makes actuator access valuable even when routing quality is the same.

## 7. Gross and net surplus

### Gross surplus

`gross_surplus_ij(t) = base_surplus_ij * match_quality_ij(t)`

### Net surplus

`net_surplus_ij(t) = gross_surplus_ij(t) - latency_cost_ij - leakage_cost_ij(t) - execution_loss_ij(t)`

## 8. Router and rollup learning

For v1, avoid full reinforcement learning. Use policy-quality scalars.

### Observed learning signal

For any regime, define:

`observed_signal(t) = average(net_surplus realized per routed coordination in t)`

normalized to `[0, 1]`.

### Router update

`router_policy_quality(t+1) = min(1, router_policy_quality(t) + eta_r * observed_router_signal(t))`

### Rollup update

`rollup_policy_quality(t+1) = min(1, rollup_policy_quality(t) + eta_c * observed_rollup_signal(t) + transfer_bonus(t))`

where:

- `eta_c > eta_r`
- `transfer_bonus(t) = tau * similarity_weighted_success(t)`

`similarity_weighted_success(t)` can be the average success of owned-node pairs sharing the same vertical or edge type.

### Policy-quality term in matching

Use:

- `policy_quality_term = router_policy_quality(t)` in router world
- `policy_quality_term = rollup_policy_quality(t)` in rollup world
- `policy_quality_term = baseline_policy_quality` in fragmented market

## 9. Trust update

Trust should:

- rise after successful coordination
- fall after failure
- rise faster in owned/internal interactions

### Proposed form

`trust_ij(t+1) = clip(trust_ij(t) + eta_T_pos * success_ij(t) * trust_regime_bonus - eta_T_neg * failure_ij(t), 0, 1)`

where:

- `success_ij(t)` is `1` if the coordination event clears a threshold net surplus
- `failure_ij(t)` is `1` if the event fails or produces negative net surplus
- `trust_regime_bonus = 1.2` inside owned interactions, `1.0` otherwise

## 10. Opportunity generation

We need enough variation for topology to matter.

### Proposed form

At each time step, each node generates:

`num_opportunities_i(t) ~ Poisson(mu_i)`

For each opportunity:

- choose a required solution type from a node-specific distribution
- set:
  - `value_scale ~ Uniform(v_min, v_max)`
  - `urgency_scale ~ Uniform(0, 1)`
  - `required_context_depth ~ Uniform(0, 1)`

Candidate neighbors are those with matching edge types or vertical compatibility.

## 11. Revelation choice rule

For v1, let nodes choose revelation deterministically from a simple tradeoff score.

### Proposed form

For each candidate edge:

`score_ij(r) = expected_match_gain_ij(r) - expected_leakage_cost_ij(r)`

Evaluate this over a small discrete grid:

`r ∈ {0.0, 0.25, 0.5, 0.75, 1.0}`

Choose the `r` that maximizes the score.

This is simple, transparent, and sufficient for the first implementation.

## 12. Acquisition rule

### Exogenous mode

Predetermine an order based on:

- highest degree
- highest complementarity with currently owned set
- highest hidden alpha

### Endogenous mode

Define expected marginal value:

`EMV(j | owned_set_t) = expected increase in portfolio_value from acquiring j`

Approximate with:

`EMV(j) = c1 * adjacency_to_owned(j) + c2 * average_complementarity_to_owned(j) + c3 * hidden_alpha_j + c4 * actuator_strength_j`

Choose the node with highest `EMV`.

This is not fully optimal, but it is a strong first approximation.

## 13. Portfolio value decomposition

For interpretability, decompose:

`portfolio_value(t) = operating_value(t) + leakage_avoided_value(t) + learning_value(t) + adjacency_premium(t)`

### Suggested definitions

- `operating_value`
  - sum of net surplus on owned-internal coordinations
- `leakage_avoided_value`
  - counterfactual external leakage minus actual internal leakage
- `learning_value`
  - value attributable to higher rollup policy quality relative to baseline
- `adjacency_premium`
  - residual portfolio gain from complementary owned-node pairs

## 14. Parameter guidance

Recommended first-pass ranges:

- `a1, a2, a3, a4, a5, a6` in `[0.3, 1.5]`
- `lambda_L` in `[0.2, 1.0]`
- `gamma` in `[1.2, 2.0]`
- `rho_L` in `[0.5, 0.95]`
- `eta_r` in `[0.01, 0.05]`
- `eta_c` in `[0.03, 0.08]`
- `tau` in `[0.01, 0.05]`
- `eta_T_pos` in `[0.03, 0.08]`
- `eta_T_neg` in `[0.05, 0.12]`

The exact values should be tuned only after verifying that each channel behaves qualitatively as intended.

## 15. Diagnostics

Before running institutional comparisons, verify:

1. more revelation raises match quality
2. more revelation also raises leakage cost
3. trust-generated context is much higher in owned/internal interactions than in ordinary external ones
4. higher actuator strength lowers execution loss
5. rollup learning rises faster than router learning
6. leak stock persists and depresses future external coordination quality

If any of these fail, the simulation is not implementing the thesis correctly.

## 16. Recommended implementation note

The first code version should keep these functions explicit and inspectable.

Do not hide:

- matching
- leakage
- trust
- learning

inside a learned neural policy in v1.

If the explicit-form model produces the intended qualitative differences, richer learning models can be added later.
