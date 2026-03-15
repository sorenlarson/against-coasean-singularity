# Test F Model Primitives

## Full Graph-Based Economy for Cybernetic Arbitrage

This document defines the full model primitives for implementing:

- [test_f_cybernetic_arbitrage_spec.md](/Users/soren/Downloads/aivc-action-log-codex/outputs/test_f_cybernetic_arbitrage_spec.md)

The goal is to specify a graph-heavy institutional simulation in which:

- firms are nodes
- transactions and dependencies are directed edges
- valuable coordination depends on local private context
- external coordination requires context revelation
- revelation creates leakage
- ownership changes what information can move internally and what actions can be taken
- learning accumulates differently in fragmented, routed, and rolled-up systems

## 1. Core sets

Let:

- `V = {1, ..., N}` be the set of firms or operating nodes
- `E ⊆ V × V` be the directed edge set
- `T = {1, ..., H}` be discrete time steps

Each directed edge `(i, j)` means node `i` can potentially route work, transact, or depend operationally on node `j`.

## 2. Node primitives

Each node `i ∈ V` has:

- `vertical_i`
  - categorical vertical or domain identity
- `owned_i(t)`
  - binary indicator for whether the node is owned by the rollup at time `t`
- `sensor_quality_i`
  - quality of the node's observation of its own local state
- `actuator_strength_i`
  - ability to change operations, fulfill work, or execute routed decisions
- `trust_profile_i`
  - baseline ability to generate trust-sensitive context
- `policy_i(t)`
  - routing or coordination policy used by the node
- `context_state_i(t)`
  - latent vector of local economic state

### 2.1 Context state

Define:

`context_state_i(t) = [demand_i(t), capacity_i(t), urgency_i(t), exception_i(t), quality_risk_i(t), price_sensitivity_i(t), hidden_alpha_i(t)]`

Interpretation:

- `demand_i(t)`
  - current demand pressure or inflow
- `capacity_i(t)`
  - available productive or operational capacity
- `urgency_i(t)`
  - time sensitivity of current opportunities
- `exception_i(t)`
  - burden of non-standard cases
- `quality_risk_i(t)`
  - current operational risk or failure propensity
- `price_sensitivity_i(t)`
  - how costly adverse pricing or bargaining outcomes are
- `hidden_alpha_i(t)`
  - idiosyncratic local information valuable for high-quality matching

The node itself sees a noisy version of this state:

`observed_self_i(t) = context_state_i(t) + sensor_noise_i(t)`

where noise declines as `sensor_quality_i` rises.

## 3. Edge primitives

Each edge `(i, j) ∈ E` has:

- `edge_type_ij`
  - transaction, routing, supplier relationship, workflow dependency, etc.
- `base_surplus_ij`
  - potential gross value from successful coordination
- `info_requirement_ij`
  - amount of context needed for high-quality coordination
- `latency_cost_ij`
  - time or friction cost of coordination
- `exec_risk_ij`
  - baseline probability of poor execution
- `leakage_sensitivity_ij`
  - how costly revealed context is on this edge
- `trust_requirement_ij`
  - how much trusted interaction is needed to surface valuable context
- `complementarity_ij`
  - strength of superadditive value if both nodes are owned

## 4. Institutional layers

The same graph is evaluated under three coordination regimes.

### 4.1 Fragmented market regime

- nodes coordinate bilaterally over edges
- external transactions require context revelation
- revealed context can leak across the market
- no internalization of cross-node state beyond what is explicitly shared

### 4.2 External router regime

- a router sees revealed context from participating nodes
- router proposes matches or coordination decisions
- router cannot fully act inside nodes
- router does not internalize the full private state of nodes
- router learns from observed outcomes, but only on the revealed layer

### 4.3 Cybernetic rollup regime

- a subset of nodes is owned at each time `t`
- owned nodes share richer internal state
- coordination inside the owned subgraph has lower leakage
- the rollup can act through node actuators
- the rollup updates a shared policy using owned-node outcomes

## 5. Opportunity generation

At each time step, each node `i` generates one or more coordination opportunities.

Define:

`opportunity_i(t) ~ O(context_state_i(t), vertical_i)`

Each opportunity has:

- `required_solution_type`
- `value_scale`
- `urgency_scale`
- `required_context_depth`
- `candidate_neighbors_i(t) ⊆ {j : (i, j) ∈ E}`

An opportunity can be:

- handled locally
- sent externally to a neighbor
- routed by the external router
- routed internally inside the rollup if the chosen counterparty is owned

## 6. Context revelation

For any coordination attempt from node `i` to node `j`, define a revelation choice:

`r_ij(t) ∈ [0, 1]`

where:

- `0` means no meaningful context revealed
- `1` means maximal revelation of relevant local state

Revealed context improves matching quality but increases leakage.

### 6.1 Match-quality function

Define:

`match_quality_ij(t) = f(base_surplus_ij, r_ij(t), trust_context_ij(t), policy_quality(t), actuator_term_ij(t), complementarity_ij, context_fit_ij(t))`

with:

- `∂ match_quality / ∂ r > 0`
- diminishing returns to revelation

### 6.2 Leakage-cost function

Define:

`leakage_cost_ij(t) = g(r_ij(t), leakage_sensitivity_ij, price_sensitivity_i(t), hidden_alpha_i(t), market_visibility_ij(t))`

with:

- `∂ leakage_cost / ∂ r > 0`
- leakage cost persisting over time through state updates

This persistence can be modeled by updating a node-level leakage stock:

`leak_stock_i(t+1) = rho * leak_stock_i(t) + leakage_cost_ij(t)`

where `rho` governs how long leaked information continues to erode rents.

## 7. Trust-generated context

This is the central non-Coasean mechanism.

Define:

`trust_context_ij(t) = h(trust_ij(t), trust_requirement_ij, trust_profile_i, interaction_mode_ij(t))`

Interpretation:

- some valuable context is only generated if trust crosses a threshold
- internal/owned interactions can have systematically higher trust access
- some routers may build trust over time, but less than owned interfaces

This context is additive to ordinary revealed state:

`effective_context_ij(t) = revealed_context_ij(t) + trust_context_ij(t)`

The key distinction:

- `revealed_context`
  - existed already and was disclosed
- `trust_context`
  - only exists because a trusted interaction occurred

## 8. Routing and coordination policies

### 8.1 Node-local policy

Each node uses:

`policy_i(t)` to decide whether to:

- handle locally
- coordinate externally
- reveal more or less context
- accept a router suggestion

### 8.2 External router policy

The router uses:

`router_policy(t)`

to choose counterparties using only:

- revealed context
- observed outcome history
- edge structure

### 8.3 Rollup policy

The rollup uses:

`rollup_policy(t)`

to choose counterparties among owned nodes using:

- richer internal context
- internal outcome history
- cross-node policy transfer

The rollup may also coordinate with external nodes, but only with external leakage costs.

## 9. Actuator access

Actuator access changes how much of potential match quality becomes realized value.

Define:

`actuator_term_ij(t) = k(actuator_strength_i, actuator_strength_j, regime, owned_i(t), owned_j(t))`

Interpretation:

- fragmented market:
  coordination quality can still fail in execution
- external router:
  recommendations may not be fully implemented
- rollup:
  internal control can push execution quality closer to matched intent

## 10. Realized surplus

For any executed coordination event:

`gross_surplus_ij(t) = base_surplus_ij * match_quality_ij(t)`

`net_surplus_ij(t) = gross_surplus_ij(t) - latency_cost_ij - leakage_cost_ij(t) - execution_loss_ij(t)`

where:

`execution_loss_ij(t) = q(exec_risk_ij, actuator_term_ij(t), exception_i(t), quality_risk_j(t))`

This gives each event a leakage-adjusted economic value.

## 11. Learning dynamics

Policies should update from outcomes.

### 11.1 Router learning

The router updates only on:

- revealed-context events
- visible outcomes

### 11.2 Rollup learning

The rollup updates on:

- richer owned-node internal state
- deeper outcome data
- transfer learning across owned nodes with similar verticals or edge types

Define generic policy-quality states:

- `router_policy_quality(t)`
- `rollup_policy_quality(t)`

with updates:

`router_policy_quality(t+1) = router_policy_quality(t) + eta_r * observed_router_signal(t)`

`rollup_policy_quality(t+1) = rollup_policy_quality(t) + eta_c * observed_rollup_signal(t) + transfer_bonus(t)`

where:

- `eta_c >= eta_r`
- `transfer_bonus(t)` is positive when knowledge from one owned node improves another

## 12. Trust dynamics

Trust should evolve with repeated successful coordination.

Define pairwise trust:

`trust_ij(t+1) = m(trust_ij(t), success_ij(t), failure_ij(t), regime, owned_i(t), owned_j(t))`

Ownership can affect trust through:

- repeated interaction
- standardized interfaces
- stronger institutional guarantees

This matters because trust raises the probability that trust-generated context appears.

## 13. Acquisition dynamics

The rollup acquires nodes over time.

### 13.1 Exogenous mode

Predetermine an acquisition sequence:

`A(1), A(2), ..., A(K)`

and flip `owned_i(t)` when acquired.

### 13.2 Endogenous mode

At decision times, choose the node with highest expected marginal value:

`argmax_j E[portfolio_value(t+1) - portfolio_value(t) | acquire j]`

The critical result to track is whether:

- marginal acquisition value rises when neighboring or complementary nodes are already owned

That is the superlinearity test.

## 14. Portfolio value

Define owned-subgraph portfolio value:

`portfolio_value(t) = sum of net surplus captured inside the owned subgraph + future policy value + reduced leakage value`

Potential decomposition:

- direct operating value
- leakage avoided
- learning value
- adjacency/complementarity premium

This allows the simulation to show whether:

- `Value(A ∪ B) > Value(A) + Value(B)`

for complementary subsets of nodes.

## 15. Observables / metrics

At each time step and cumulatively, record:

- total gross surplus
- total net surplus
- total leakage cost
- net surplus by regime
- net surplus captured by rollup
- revealed-context volume
- trust-generated-context volume
- average match quality
- average coordination latency
- failure rate
- router policy quality
- rollup policy quality
- trust levels
- portfolio value
- marginal value of acquisition

## 16. Ablation switches

To test the theory rigorously, the following switches should be available:

- `leakage_on`
- `trust_generated_context_on`
- `actuator_access_on`
- `cross_node_learning_on`
- `endogenous_acquisition_on`

These support the comparisons required in Test F.

## 17. Interpretation mapping

The model is meant to isolate the following causal channels:

- transaction-cost reduction
  - lower search/matching friction
- leakage
  - external revelation reduces future rents
- trust-generated context
  - ownership and trusted interfaces create new information
- actuator control
  - ownership improves realization of matched intent
- cumulative learning
  - owned systems compound faster from outcomes

The cybernetic-arbitrage thesis is supported if ownership changes not just coordination cost, but the long-run information and action topology of the system.

## 18. Recommended implementation order

Implement the full model in this order:

1. graph, node states, and edge parameters
2. opportunity generation
3. revelation and leakage functions
4. match-quality and surplus realization
5. router and rollup policies
6. learning updates
7. acquisition dynamics
8. ablation controls

The first production run should use:

- moderate `N`
- exogenous acquisitions
- a small number of verticals
- deterministic or low-noise learning rules

Only after the model behaves sensibly should complexity be expanded.
