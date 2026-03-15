# Test F: Cybernetic Arbitrage Simulation

## Objective

Test whether ownership of edge nodes changes the economics of coordination beyond what can be explained by lower transaction costs alone.

The purpose of Test F is not to show that AI agents can trade. It is to compare three institutional forms under the same economic environment:

- fragmented market coordination
- external non-owning router
- owning cybernetic rollup

The hypothesis is that when coordination depends on local context, leakage, trust, actuator access, and learning, the owning rollup captures more value than either markets alone or a non-owning router.

## Questions

Test F should answer five questions:

1. Does lower bargaining/search cost alone produce thick, efficient decentralized coordination?
2. When transactions require revealing local context, how much value is lost to leakage?
3. Does a trusted edge interface generate context that is unavailable to external coordinators?
4. Does ownership of adjacent nodes create more-than-additive value?
5. How much of the gain comes from better routing versus actuator access and cumulative learning?

## Institutional worlds

### World A: Fragmented market

Independent firms transact bilaterally.

- each node sees only its own local state
- external transactions require partial context revelation
- counterparties may learn from revealed context
- coordination quality depends on what firms are willing to disclose
- no central entity has privileged cross-node visibility

### World B: External router

A non-owning router improves matching across firms.

- the router sees what firms choose to reveal
- it can recommend or route counterparties toward one another
- it does not own the nodes
- it has limited or no actuator control
- it cannot automatically internalize context from outcomes across all nodes

### World C: Cybernetic rollup

A rollup owns a subset of nodes and coordinates internally across them.

- owned nodes can share richer state internally
- internal coordination has lower leakage cost
- the rollup has actuator access within owned nodes
- outcomes from owned nodes update shared policies
- the rollup may acquire more nodes over time

## Economic environment

The economy is modeled as a directed graph of firms.

Each node represents a firm, operating unit, or asset with:

- local private state
- sensors that reveal noisy information about conditions at that node
- actuators that can fulfill, route, reallocate, or transform work
- economic specialization or vertical identity
- trust relationships with other nodes

Each edge represents a possible transaction, routing relationship, or operational dependency.

Each edge has:

- base economic surplus if coordination is successful
- information requirement
- leakage risk
- latency or coordination delay
- execution risk

## State variables

Each node has a private context vector. The exact implementation may vary, but it should include variables such as:

- demand state
- capacity state
- urgency
- exception burden
- quality or failure risk
- price sensitivity
- domain-specific hidden conditions

These states change over time.

Some fraction of state is:

- legible internally without cost
- partially revealable externally at a cost
- only generated through trusted interaction

## Trust-generated context

This is the key extension beyond a standard market simulation.

Some context should only appear when a node interacts through a trusted interface. For example:

- a customer reveals urgency only to a trusted operator
- an employee reveals a workflow exception only to an internal tool
- a physician reveals uncertainty only to a trusted clinical interface

The simulation should explicitly distinguish:

- pre-existing hidden state
- interaction-generated state

External routers should have much weaker access to the second category.

## Leakage mechanism

External coordination requires revealing some fraction of local context.

Greater revelation:

- improves match quality
- increases execution success probability
- increases leakage cost

Leakage cost can operate through one or more mechanisms:

- future price discrimination
- competitor learning
- erosion of local informational advantage
- reduction in future routing surplus

Leakage should persist over time, not just affect the current transaction.

## Actuator access

Worlds should differ not just in information, but in actionability.

In fragmented markets:

- nodes can only act on their own state and negotiated external commitments

In the external router:

- the router can recommend matches but cannot reliably enforce internal change

In the rollup:

- the rollup can redirect workflows, reallocate capacity, standardize playbooks, and internalize operational change across owned nodes

## Learning mechanism

Outcomes should update future coordination quality.

Possible learning channels:

- improved routing priors
- improved handling of exception-heavy flows
- improved pricing
- improved trust calibration
- improved policy transfer across similar owned nodes

The rollup should have the strongest learning channel because it retains richer outcome data across owned nodes with lower leakage.

## Simulation procedure

### Step 1: initialize the graph

Create `N` firms with:

- vertical labels
- local context-generating processes
- sensor quality
- actuator strength
- trust relationships
- candidate edges to transact over

### Step 2: define transaction opportunities

At each time step, nodes experience operational or commercial opportunities that can be:

- fulfilled internally
- transacted externally
- routed through an external router
- routed internally within the rollup if both nodes are owned

### Step 3: choose revelation level

For each potential coordination event, determine how much context must be revealed to improve execution.

This should create a tradeoff:

- more revelation improves immediate match quality
- more revelation increases future leakage cost

### Step 4: execute coordination

Depending on institutional world:

- fragmented market negotiates bilaterally
- router suggests counterparties or solutions
- rollup coordinates directly within owned nodes

### Step 5: realize outcomes

Each coordination event yields:

- gross surplus
- leakage cost
- execution quality
- latency
- learning signal

### Step 6: update trust, policies, and state

Outcomes affect:

- future trust
- future routing priors
- future willingness to reveal context
- future node productivity

### Step 7: acquisition path for rollup

The rollup should be allowed to acquire nodes over time according to one of two methods:

- exogenous acquisition sequence
- endogenous acquisition rule based on expected marginal value

This allows the simulation to measure whether the value of the owned subgraph accelerates as adjacent nodes are internalized.

## Outputs

At minimum, Test F should report:

- total gross surplus
- leakage-adjusted surplus
- surplus captured by each institutional form
- average match quality
- coordination latency
- failed coordination rate
- revealed-context volume
- leakage cost
- learning rate over time
- marginal value of the next acquired node
- value of owned subgraph as portfolio size increases

Additional outputs that would be especially useful:

- proportion of trust-generated context captured
- actuator utilization
- policy-transfer benefit across owned nodes
- edge density inside versus outside the owned subgraph

## Key comparisons

### Comparison 1: Lower transaction costs vs ownership

Hold bargaining/search cost low across all worlds and test whether ownership still matters.

### Comparison 2: Leakage-free vs leakage-prone world

Turn leakage cost on and off to see how much of the rollup advantage depends on internalizing context.

### Comparison 3: Trust-generated context on vs off

Turn trusted-context generation on and off to test whether edge routers and rollups gain most when high-value context is constituted in use.

### Comparison 4: Actuator access on vs off

Let the router observe more information but not act, then compare it to the rollup with actuator access.

### Comparison 5: Learning on vs off

Disable cross-node learning to isolate how much of the rollup advantage comes from cumulative policy improvement.

## Success criteria

The cybernetic-arbitrage thesis is supported if the simulation shows some version of the following:

1. Lower transaction costs alone do not produce the best coordination outcome.
2. Leakage costs materially reduce the value of external coordination.
3. Trust-generated context increases the advantage of edge ownership over external routing.
4. The value of the owned subgraph grows faster than linearly as complementary nodes are acquired.
5. Actuator access and learning materially increase the rollup's share of surplus relative to a non-owning router.

## Failure criteria

The thesis is weakened if:

- the fragmented market performs as well as the rollup once transaction costs are low
- the router matches the rollup once it sees the same information
- leakage has little effect on long-run value
- ownership adds no superlinear benefit as adjacent nodes are acquired

## Minimal first implementation

Start with a stripped-down model:

- `30` nodes
- directed graph
- one hidden demand/capacity vector per node
- one leakage function
- one trust-generated context channel
- one router
- one rollup that acquires nodes in fixed order

Measure:

- leakage-adjusted surplus
- match quality
- rollup surplus capture
- marginal value of each acquisition

Only after this works should the model be expanded with richer domain-specific structure.

## Relation to the theory note

Test F is designed to test the propositions in:

- [cybernetic_arbitrage_theory_note.md](/Users/soren/Downloads/aivc-action-log-codex/outputs/cybernetic_arbitrage_theory_note.md)

Specifically:

- Proposition 1 maps to decentralized-coordination outcomes under low transaction costs
- Proposition 2 maps to the leakage mechanism
- Proposition 3 maps to trust-generated context
- Proposition 4 maps to acquisition-path and superlinear portfolio value
- Proposition 5 maps to actuator-access comparisons

## Recommended next step

Before implementation, define the minimal mathematical forms for:

- context revelation benefit
- leakage penalty
- trust-generated context probability
- actuator effectiveness
- learning update rule

Those choices will determine whether Test F is a genuine institutional simulation or just a graph with labels.
