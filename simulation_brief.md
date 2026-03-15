# Simulation Brief: Event-Sourced Action Log

*Handoff document for Claude Code*

| | |
|---|---|
| **Status** | Draft |
| **Date** | March 2026 |
| **Companion docs** | `strategy.md` (stakeholder context, task catalog), `technical_spec.md` (schema, vocabulary, queries, task execution steps) |

---

## Purpose

We have designed a measurement apparatus — an event-sourced action log with seven analytical tasks — for the AIVC platform. Before instrumenting real portcos, we want to validate that the apparatus works. This simulation stress-tests the schema, the queries, and the analytical methods against synthetic data.

**What we are testing:**
- Does the schema support the queries required by all seven tasks?
- Given realistic portfolio sizes and noise levels, can the analytical methods detect effects?
- How does the analysis degrade as data quality worsens?

**What we are NOT testing:**
- Whether the platform actually produces EBITDA uplift. The simulation assumes a data-generating process with known causal parameters. If the analysis recovers those parameters, the apparatus works. If it doesn't, the apparatus has a problem. We are testing the measurement tool, not the thing being measured.

**The tautology guardrail:** Every claim the simulation produces must be about the apparatus, not about the platform. Valid: "With 15 portcos, DiD detects a $200k effect with 80% power." Invalid: "The platform produces $200k of EBITDA uplift." The first is a statement about our ability to measure. The second is a claim about reality that only real data can support.

---

## Data-Generating Process

### Portfolio

Generate a portfolio of **20 portcos** with the following characteristics, drawn from plausible distributions:

| Characteristic | Distribution | Notes |
|---|---|---|
| Vertical | Uniform over: manufacturing, healthcare, financial_services, logistics, professional_services | |
| Revenue | LogNormal(μ=16.5, σ=0.5), yielding ~$10M–$50M range | Annual, at acquisition |
| Headcount | Revenue / uniform(80k, 150k) | Rough revenue-per-head |
| System landscape | Sample 2–4 from: sap, oracle, netsuite, quickbooks, salesforce, hubspot, workday, adp, jira, asana | |
| Acquisition date | Staggered monthly over months 1–12 | |
| Platform deploy date | Acquisition date + uniform(2, 5) months | Not all portcos deployed — hold out 5 as controls |

15 portcos receive platform deployment. 5 are controls (acquired but not yet deployed). This gives the DiD its control group.

### Operational Activity

For each portco, generate a stream of tuples populating the schema from `technical_spec.md`. The activity should simulate realistic operational processes:

**Core processes to simulate (per portco):**

| Process | Frequency | Canonical sequence | Variance |
|---|---|---|---|
| Purchase order cycle | 100–200/month | created → submitted → approved → released → settled | Low: 85% follow canonical path. 10% require escalation (second approval). 5% rejected and resubmitted. |
| Invoice reconciliation | 150–300/month | created → reconciled → settled | Low: 90% straightforward. 10% exceptions requiring manual review. |
| Vendor onboarding | 5–15/month | created → submitted → approved → closed | Moderate: 70% canonical. 30% require additional compliance steps that vary by vertical. |
| Campaign management | 3–8/month | created → set_target → set_budget → approved → launched | Moderate: 60% run without changes. 40% retargeted mid-flight. |
| Contract negotiation | 1–3/month | created → assigned → amended → approved → closed | High: No two follow the same path beyond the first two predicates. Duration varies widely (5–60 days). |
| Employee onboarding | 2–5/month | created → assigned → approved → closed | Moderate: Varies by role level and vertical. |

**Generating tuples:**
- Each process instance gets a unique entity (e.g., `purchase_order_00142`).
- For each step in the sequence, emit a tuple with a realistic timestamp gap (e.g., approval takes 1–5 days after submission).
- Assign actors from a pool of ~15–40 people per portco, with role assignments (from `actor_roles`).
- Add noise: 5% of tuples should be missing (dropped from the log). 3% should have slightly wrong timestamps (±1 hour jitter). This simulates real instrumentation imperfections.

**Generating meetings:**
- 8–20 meetings/month per portco.
- Each produces a tier 1 artifact (transcript stub — just an ID and timestamp; no need to generate actual text).
- LM-extracted tuples from meetings: 0–4 tuples per meeting, with confidence scores drawn from Beta(α=8, β=3), roughly centering around 0.7–0.8. Predicates are mostly `assigned` and `proposed`, with descriptive-string objects (no system-of-record referents).
- 40% of meeting assignments should result in a follow-on baptism (task creation in a system of record within 1–5 days). 60% are dead ends.

### Treatment Effect

This is the part that must be handled carefully to avoid tautology. The treatment effect is a **known input parameter** — we set it, the analysis tries to recover it.

**Effect specification:**

For deployed portcos, after the platform deploy date:
- **Verb compression:** Certain processes transition from human-executed to agent-executed. The compression schedule:
  - Invoice reconciliation: begins compressing at deploy + 2 months. Agent share ramps from 0% to 70% over 4 months. Override rate: 6%.
  - PO approval routing: begins at deploy + 3 months. Agent share ramps to 55% over 3 months. Override rate: 10%.
  - Other processes: not compressed in this simulation.
- **Cycle time reduction:** For compressed verbs, median duration drops by 40–60% (draw per portco from this range).
- **Human time freed:** Compressed verb instances that are agent-executed take 0 human time (plus override instances at ~15 min each).

**Confounds to include (things that happen independent of the platform):**
- All portcos experience a secular trend: operational metrics improve by ~2% per quarter regardless of platform deployment (macro/learning effects).
- 3 portcos (2 treated, 1 control) hire a strong operations director during the observation period, producing a one-time 8–12% improvement in cycle times unrelated to the platform.
- 1 treated portco has an ERP migration during months 8–10, causing a temporary degradation in all metrics.

These confounds are what the DiD must handle. If the DiD estimate is close to the true treatment effect despite the confounds, the apparatus works.

**Dose-response variation:** Among the 15 deployed portcos, adoption intensity should vary. Some ramp quickly (agent share reaches 70% within 3 months), others slowly (agent share reaches 30% over 6 months). Adoption speed correlates with portco size (smaller portcos adopt faster) — this is the endogeneity the dose-response analysis must contend with.

**Compounding effect:** The true integration cost and time-to-first-compression should decline with deployment order, but noisily. True values:
- Integration cost: $160k for portco 1, declining ~$8k per subsequent deployment, plus noise (σ=$20k).
- Time to first compression: 12 weeks for portco 1, declining ~0.6 weeks per deployment, plus noise (σ=2 weeks).
- Module reuse: portco 1 reuses 0%. Portco 15 reuses ~60%. Linear ramp with noise.

---

## Test Battery

### Test A: Pipeline Validation

**Objective.** Verify that the schema supports the seven tasks end-to-end.

**Procedure.**
1. Populate the database from `technical_spec.md` with the synthetic data.
2. Execute each of the seven tasks from the technical spec's Task Execution Reference (§5).
3. For each task, report: executed successfully (yes/no), and if no, what failed and why (schema gap, query failure, missing data).

**Success criteria.** All seven tasks execute and produce output. If a task fails, identify whether the issue is in the schema, the query patterns, or the task specification, and propose a fix.

### Test B: Power Analysis

**Objective.** Determine the minimum detectable effect size for the causal tasks, given the simulated portfolio size and noise.

**Procedure.** Run the simulation 500 times with different random seeds, varying the true treatment effect size:

| Effect size (cycle time reduction) | True value |
|---|---|
| Zero (null) | 0% |
| Small | 15% |
| Medium | 35% |
| Large | 55% |

For each effect size, run Task 3 (DiD) and report:
- Mean estimated effect across 500 runs
- Standard deviation of estimates
- Rejection rate at α=0.05 (this is the power)
- Bias: mean estimate minus true value

Repeat at different portfolio sizes: 8, 12, 15, 20 portcos (holding out proportionally for controls).

**Deliverable.** A power table:

| Portcos | True effect | Mean estimate | SD | Power | Bias |
|---|---|---|---|---|---|
| 8 | 0% | ... | ... | ... | ... |
| 8 | 15% | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |

**Success criteria.** Power ≥ 0.80 for the medium effect at 15+ portcos. If not, the fund needs more portcos before the LP headline number is credible — and the strategy doc's roadmap should be updated accordingly.

### Test C: Robustness / Degradation

**Objective.** Determine how the analysis degrades as data quality worsens.

**Procedure.** Fix the treatment effect at the medium level. Then vary data quality parameters:

| Degradation | Levels to test |
|---|---|
| Missing tuple rate | 5% (baseline), 10%, 20%, 30% |
| Predicate inconsistency (% of tuples with wrong predicate) | 0% (baseline), 5%, 10%, 20% |
| Confidence threshold for LM-extracted tuples | 0.5, 0.6, 0.7 (baseline), 0.8, 0.9 |
| Entity resolution failure (% of entities appearing under duplicate IDs) | 0% (baseline), 5%, 10% |

For each degradation level, run all seven tasks and report:
- Task 1 (Verb compression): How does the ranking of compression candidates change? At what degradation does the ranking become unreliable (top candidates shift by >3 positions)?
- Task 2 (FTE absorption): How does the hours estimate drift? At what degradation is the estimate off by >20%?
- Task 3 (DiD): How does bias and power change?
- Task 5 (Deployment curves): At what degradation does the compounding trend become undetectable?
- Tasks 6, 7: At what degradation do similarity scores become unreliable?

**Deliverable.** A degradation table per task showing the metric of interest at each quality level. Highlight the "cliff" — the quality level below which the task output is unreliable.

**Success criteria.** Tasks 1 and 2 (descriptive) should tolerate 10% missing tuples without major drift. Task 3 (DiD) should tolerate 10% missing tuples with modest power loss. If any task fails at baseline quality levels, the issue is in the task design, not the data — fix the task.

### Test D: Confound Recovery

**Objective.** Verify that the DiD correctly handles the planted confounds.

**Procedure.** Run Task 3 with and without the confounds (new-hire effect, ERP migration, secular trend). Compare:
- DiD estimate without confounds (should recover true effect cleanly)
- DiD estimate with confounds (should still recover true effect if the design is working — confounds affect both treated and control or are portco-specific shocks)
- Naive pre-post estimate with confounds (should be biased — this is the straw man)

**Deliverable.** A table:

| Method | Confounds | Estimate | True effect | Bias |
|---|---|---|---|---|
| DiD | No | ... | ... | ... |
| DiD | Yes | ... | ... | ... |
| Naive pre-post | Yes | ... | ... | ... |

**Success criteria.** DiD bias should be small (<15% of true effect) even with confounds. Naive pre-post should show large bias. This demonstrates why DiD matters — and gives the AIVC operating team a concrete argument for why the action log is worth building.

---

## Deliverables

Claude Code should produce:

1. **Synthetic data generator.** A script that populates the database schema from `technical_spec.md` with configurable parameters (portfolio size, noise levels, treatment effect, confounds on/off). Should be rerunnable with different seeds.

2. **Task implementations.** Working code for all seven tasks from the technical spec's Task Execution Reference, executed against the synthetic database.

3. **Test results.** Tables and plots for Tests A–D.

4. **Findings report.** A brief document summarizing:
   - Which tasks executed successfully and which required schema or query modifications (with the modifications noted)
   - The power table: at what portfolio size does the LP headline number become credible?
   - The degradation table: where are the quality cliffs, and what engineering investment do they imply?
   - The confound recovery result: does DiD work as designed?
   - Any recommended changes to the strategy doc or technical spec based on what was learned.

---

## Guidance for Claude Code

- **Start with Test A.** Get the data generated and the tasks running before worrying about monte carlo. If the schema or queries need fixes, fix them first.
- **Use SQLite or DuckDB** for the database — lightweight, no infrastructure, and sufficient for this scale.
- **The data-generating process is the hardest part.** The tuples need to be realistic enough that the analysis is meaningful. Spend time getting the temporal structure right — events should chain causally (a PO can't be approved before it's created), gaps should be realistic, and the treatment effect should ramp gradually, not switch on overnight.
- **The tautology guardrail applies to the findings report.** Every finding should be stated as a property of the apparatus ("DiD recovers a 35% effect with 82% power at n=15") not a property of the platform ("the platform produces 35% cycle time improvement").
- **If something in the technical spec is broken, fix it and note the fix.** The point of the simulation is to find these problems early. Schema modifications, query rewrites, and task execution changes are expected outputs, not failures.
