# Event-Sourced Action Log: Technical Specification

*Companion to `strategy.md`*

| | |
|---|---|
| **Status** | Draft |
| **Date** | March 2026 |

---

## Purpose

This document specifies the data model, predicate vocabulary, extraction process, and interface for the event-sourced action log. It is intended to be machine-readable — a Claude Code instance with access to this spec and the log should be able to execute any task in the strategy document's task catalog.

---

## 1. Schema

### 1.1 Tier 1: Raw Artifacts

Tier 1 artifacts are stored as-is. Each has a header record:

```json
{
  "artifact_id": "string — unique identifier (e.g., meeting_4827, email_thread_991)",
  "artifact_type": "transcript | audit_log | email_thread | commit_log | document",
  "source_system": "string — originating system (e.g., zoom, sap, gmail, github)",
  "portco_id": "string — which portfolio company",
  "created_at": "ISO 8601 timestamp",
  "participants": ["string — actor identifiers involved"],
  "content_ref": "string — path or URI to the raw artifact"
}
```

Tier 1 artifacts are immutable after creation. The content is the system of record.

### 1.2 Tier 2: Extracted Tuples

```json
{
  "tuple_id": "string — unique identifier",
  "timestamp": "ISO 8601 — when the action occurred",
  "subject": "string — actor or entity identifier",
  "predicate": "string — from the controlled vocabulary (§2)",
  "object": "string — actor, entity identifier, or descriptive string",
  "portco_id": "string",
  "duration_minutes": "number | null — optional for executed/overrode tuples where human effort is measured directly",
  "related_entity_id": "string | null — optional link from a verb execution to the process instance/entity it acted on",
  "provenance": {
    "source_artifact": "string — artifact_id of the tier 1 artifact",
    "source_span": "string | null — location within the artifact (e.g., timestamp range, line number, message index)",
    "confidence": "number — 0.0 to 1.0 (1.0 for system-sourced, <1.0 for LM-extracted)",
    "extraction_method": "deterministic | llm_v2 | manual",
    "extracted_at": "ISO 8601 — when the tuple was extracted"
  }
}
```

**Naming rules.** The `subject` and `object` fields contain one of:
- A **system identifier** — an entity created in a system of record (e.g., `purchase_order_312`, `task_4812`, `campaign_55`). Valid only if a tuple with predicate `created` exists for this identifier.
- An **actor identifier** — a person, team, or agent (e.g., `alice`, `ap_team`, `agent_reconciler_v1`). Sourced from HRIS or platform identity.
- A **descriptive string** — free text enclosed in double quotes (e.g., `"switch to Vendor X"`). Used only for tuples extracted from unstructured artifacts. Must have a non-null `source_span`.

### 1.3 Entities

Every system identifier that appears in tuples must have an entity record:

```json
{
  "entity_id": "string — the identifier used in tuples",
  "entity_type": "string — e.g., purchase_order, task, campaign, invoice, contract, lead, deal, payment",
  "workflow_family": "string — stable process family used for task-level and sequence-level analysis",
  "source_system": "string — system where it was created",
  "portco_id": "string",
  "baptism_tuple_id": "string — tuple_id of the creating event"
}
```

### 1.4 Actors

```json
{
  "actor_id": "string — identifier used in tuples",
  "actor_type": "person | team | agent",
  "portco_id": "string",
  "roles": [
    {
      "role": "string — e.g., ap_clerk, sales_manager, cfo",
      "source": "hris | inferred",
      "effective_from": "ISO 8601",
      "effective_to": "ISO 8601 | null"
    }
  ]
}
```

---

## 2. Predicate Vocabulary

### 2.1 Starter Vocabulary

These are the canonical predicates. Source-system-specific events must be mapped to one of these before entering the tuple store. The vocabulary will grow; additions require a definition, at least one source system mapping, and a category.

**Lifecycle predicates** — an entity changes state:

| Predicate | Definition | Example |
|-----------|-----------|---------|
| `created` | Entity comes into existence | PO opened, task created, campaign created |
| `submitted` | Entity sent for review or approval | PO submitted, expense report filed |
| `approved` | Entity authorized by an actor with authority | PO approved, campaign approved |
| `rejected` | Entity denied authorization | PO rejected, leave request denied |
| `escalated` | Entity routed to higher authority | PO over threshold routed to VP |
| `released` | Entity cleared for execution | Payment released |
| `settled` | Entity's obligation fulfilled | Payment received, invoice matched |
| `launched` | Entity put into production or market execution | Campaign launched |
| `closed` | Entity completed or terminated | Task closed, ticket resolved |
| `cancelled` | Entity voided before completion | PO cancelled |

**Assignment predicates** — work is directed:

| Predicate | Definition | Example |
|-----------|-----------|---------|
| `assigned` | Actor given responsibility for entity or task | Task assigned to bob |
| `reassigned` | Responsibility transferred | Ticket reassigned from alice to carol |
| `delegated` | Authority transferred | Approval authority delegated |
| `proposed` | Candidate action suggested but not yet instantiated in a system of record | Meeting proposes follow-up |

**Modification predicates** — entity properties change:

| Predicate | Definition | Example |
|-----------|-----------|---------|
| `set_amount` | Monetary value set or changed | PO amount set to $42k |
| `set_target` | Target/audience set or changed | Campaign targeting changed |
| `set_budget` | Budget set or changed | Campaign budget set |
| `retargeted` | Target changed (alias for set_target with prior value) | Campaign retargeted to southeast |
| `amended` | Entity substantively modified | Contract terms amended |

**Execution predicates** — work is performed:

| Predicate | Definition | Example |
|-----------|-----------|---------|
| `executed` | Actor performed a verb | Agent reconciled invoice |
| `reconciled` | Matching/verification completed | Invoice matched to PO |
| `converted` | Entity transformed into another entity | Lead converted to deal |
| `generated` | Entity caused creation of another entity | Campaign generated lead |

**Override predicates** — human correction of agent action:

| Predicate | Definition | Example |
|-----------|-----------|---------|
| `overrode` | Human corrected an agent action | Human overrode agent reconciliation |

**Relation predicates** — static associations:

| Predicate | Definition | Example |
|-----------|-----------|---------|
| `references` | Entity linked to another entity | PO references contract |
| `includes` | Membership | Meeting includes bob |

### 2.2 Predicate Mapping

Each source system integration must provide a mapping file:

```json
{
  "source_system": "sap_erp",
  "portco_id": "portco_a",
  "mappings": [
    {
      "source_event": "BSEG-AUGBL posting",
      "canonical_predicate": "settled",
      "subject_field": "BSEG-USNAM",
      "object_field": "BSEG-BELNR",
      "notes": "Clearing document posted — indicates payment settlement"
    },
    {
      "source_event": "ME29N release",
      "canonical_predicate": "approved",
      "subject_field": "CDHDR-USERNAME",
      "object_field": "EKKO-EBELN",
      "notes": "Purchase order release strategy step"
    }
  ]
}
```

When a source event has no clear mapping, it is stored in a `_unmapped` queue for manual review. Unmapped events do not enter the tuple store.

---

## 3. Extraction Process

### 3.1 System-Sourced Extraction (Deterministic)

For tier 1 artifacts from systems of record (ERP, CRM, HRIS, ticketing):

1. Ingestion agent polls or receives webhooks from source system.
2. Source event is matched against the predicate mapping (§2.2).
3. If mapped, a tuple is emitted with `confidence: 1.0` and `extraction_method: deterministic`.
4. If unmapped, event enters the `_unmapped` queue.

### 3.2 LM-Sourced Extraction (Probabilistic)

For tier 1 artifacts from unstructured sources (transcripts, emails):

1. Artifact is processed by the extraction LM.
2. The LM is prompted to extract tuples using only predicates from the vocabulary (§2.1) and to provide a source span for each.
3. Each emitted tuple includes a confidence score.
4. Tuples below the confidence threshold (default: 0.7) enter a `_review` queue rather than the tuple store.
5. Tuples at or above the threshold enter the tuple store with `extraction_method: llm_v2` (or current version).

**Extraction prompt spec.** The LM receives:
- The tier 1 artifact content
- The predicate vocabulary with definitions
- The entity registry (known entities that may be referenced)
- The actor registry (known actors)
- Instructions to use descriptive strings (quoted) for any referent not in the entity registry, with a non-null source_span

### 3.3 Deduplication

Duplicate tuples (same timestamp, subject, predicate, object, portco_id) are collapsed. When a deterministic and LM-extracted tuple cover the same event, the deterministic version takes precedence.

### 3.4 Re-extraction

When the extraction LM is updated, or when an application produces suspicious results, tier 2 tuples derived from a given tier 1 artifact can be re-extracted. The previous tuples are soft-deleted (marked with `superseded_by: extraction_run_id`), not hard-deleted.

---

## 4. Interface

### 4.1 Query Interface

Claude Code accesses the log via SQL over a database with the following tables:

```sql
-- Tier 1 artifact headers
CREATE TABLE artifacts (
    artifact_id     TEXT PRIMARY KEY,
    artifact_type   TEXT NOT NULL,   -- transcript, audit_log, email_thread, commit_log, document
    source_system   TEXT NOT NULL,
    portco_id       TEXT NOT NULL,
    created_at      TIMESTAMP NOT NULL,
    participants    TEXT[],          -- array of actor_ids
    content_ref     TEXT NOT NULL    -- path or URI to raw content
);

-- Tier 2 extracted tuples
CREATE TABLE tuples (
    tuple_id            TEXT PRIMARY KEY,
    timestamp           TIMESTAMP NOT NULL,
    subject             TEXT NOT NULL,
    predicate           TEXT NOT NULL,
    object              TEXT NOT NULL,
    portco_id           TEXT NOT NULL,
    source_artifact     TEXT REFERENCES artifacts(artifact_id),
    source_span         TEXT,            -- null for system-sourced
    confidence          NUMERIC NOT NULL,
    extraction_method   TEXT NOT NULL,    -- deterministic, llm_v2, manual
    extracted_at        TIMESTAMP NOT NULL,
    duration_minutes    NUMERIC,          -- optional direct effort measure for executed/overrode tuples
    related_entity_id   TEXT              -- optional link from verb execution back to the entity timeline
);

-- Entity registry
CREATE TABLE entities (
    entity_id           TEXT PRIMARY KEY,
    entity_type         TEXT NOT NULL,
    workflow_family     TEXT NOT NULL,
    source_system       TEXT NOT NULL,
    portco_id           TEXT NOT NULL,
    baptism_tuple_id    TEXT REFERENCES tuples(tuple_id)
);

-- Actor registry
CREATE TABLE actors (
    actor_id    TEXT PRIMARY KEY,
    actor_type  TEXT NOT NULL,    -- person, team, agent
    portco_id   TEXT NOT NULL
);

-- Role assignments (time-varying)
CREATE TABLE actor_roles (
    actor_id        TEXT REFERENCES actors(actor_id),
    role            TEXT NOT NULL,
    source          TEXT NOT NULL,    -- hris, inferred
    effective_from  TIMESTAMP NOT NULL,
    effective_to    TIMESTAMP,
    PRIMARY KEY (actor_id, role, effective_from)
);

-- Predicate mappings per source system
CREATE TABLE predicate_mappings (
    source_system       TEXT NOT NULL,
    portco_id           TEXT NOT NULL,
    source_event        TEXT NOT NULL,
    canonical_predicate TEXT NOT NULL,
    subject_field       TEXT,
    object_field        TEXT,
    notes               TEXT,
    PRIMARY KEY (source_system, portco_id, source_event)
);

-- Portfolio companies
CREATE TABLE portcos (
    portco_id           TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    vertical            TEXT,            -- e.g., manufacturing, healthcare, financial_services
    revenue             NUMERIC,         -- annual, at time of acquisition
    headcount           INTEGER,
    system_landscape    TEXT[],          -- e.g., ['sap', 'salesforce', 'workday']
    acquisition_date    TIMESTAMP,
    platform_deploy_date TIMESTAMP,      -- null if not yet deployed
    notes               TEXT
);

-- Deployment metadata required for compounding analyses
CREATE TABLE platform_deployments (
    portco_id                        TEXT PRIMARY KEY REFERENCES portcos(portco_id),
    deployment_order                INTEGER,
    integration_start_date          TIMESTAMP,
    platform_deploy_date            TIMESTAMP,
    integration_cost                NUMERIC,
    module_reuse_rate_true          NUMERIC,
    time_to_first_compression_weeks_true NUMERIC
);

-- Module lineage and customization across deployments
CREATE TABLE platform_modules (
    module_deployment_id    TEXT PRIMARY KEY,
    portco_id               TEXT NOT NULL REFERENCES portcos(portco_id),
    module_name             TEXT NOT NULL,
    module_version          TEXT NOT NULL,
    originated_portco_id    TEXT,
    deployed_at             TIMESTAMP NOT NULL,
    customization_score     NUMERIC NOT NULL
);

-- Explicit override contract for agent interventions
CREATE TABLE override_events (
    override_event_id    TEXT PRIMARY KEY,
    portco_id            TEXT NOT NULL,
    related_entity_id    TEXT NOT NULL,
    workflow_family      TEXT NOT NULL,
    overridden_verb      TEXT NOT NULL,
    override_actor_id    TEXT NOT NULL,
    override_timestamp   TIMESTAMP NOT NULL,
    override_reason_code TEXT NOT NULL
);

-- Reproducible monthly panel metrics derived from the event log
CREATE TABLE metric_observations (
    observation_id       TEXT PRIMARY KEY,
    portco_id            TEXT NOT NULL,
    month                TIMESTAMP NOT NULL,
    metric_name          TEXT NOT NULL,
    metric_value         NUMERIC NOT NULL,
    workflow_family      TEXT,
    source_query_version TEXT NOT NULL
);
```

### 4.2 Indexes

```sql
-- Primary query patterns
CREATE INDEX idx_tuples_portco_time ON tuples(portco_id, timestamp);
CREATE INDEX idx_tuples_subject ON tuples(subject);
CREATE INDEX idx_tuples_object ON tuples(object);
CREATE INDEX idx_tuples_predicate ON tuples(predicate);
CREATE INDEX idx_tuples_predicate_portco ON tuples(predicate, portco_id);
CREATE INDEX idx_tuples_confidence ON tuples(confidence);

-- For sequence reconstruction: all events involving an entity
CREATE INDEX idx_tuples_entity_timeline ON tuples(object, timestamp) WHERE object NOT LIKE '"%';
CREATE INDEX idx_tuples_subject_timeline ON tuples(subject, timestamp);
```

### 4.3 Common Query Patterns

**Reconstruct an entity's full history:**
```sql
SELECT * FROM tuples
WHERE (subject = :entity_id OR object = :entity_id)
  AND confidence >= :threshold
ORDER BY timestamp;
```

**Derive state at time t:**
```sql
SELECT * FROM tuples
WHERE (subject = :entity_id OR object = :entity_id)
  AND timestamp <= :t
  AND confidence >= :threshold
ORDER BY timestamp;
```

**Find all instances of a predicate sequence across portcos:**
```sql
-- Step 1: Find entities that experienced predicate 'created'
-- Step 2: For each, check if subsequent predicates match pattern
-- (In practice, this is best done in application code / Claude Code
--  that queries per-entity timelines and does fuzzy sequence matching)
```

**Monthly panel metrics for causal analysis:**
```sql
SELECT portco_id, month, metric_name, metric_value, workflow_family
FROM metric_observations
WHERE metric_name = :metric_name
ORDER BY portco_id, month;
```

**Task portfolio for a role:**
```sql
SELECT t.object AS verb,
       COUNT(*) as freq,
       AVG(t.duration_minutes) as avg_duration_min,
       SUM(t.duration_minutes) / 60.0 as total_hours
FROM tuples t
JOIN actor_roles ar ON t.subject = ar.actor_id
  AND t.timestamp BETWEEN ar.effective_from AND COALESCE(ar.effective_to, t.timestamp)
WHERE ar.role = :role
  AND t.portco_id = :portco_id
  AND t.predicate = 'executed'
  AND t.confidence >= :threshold
GROUP BY t.object;
```

**Agent vs. human execution share:**
```sql
SELECT
  a.actor_type,
  t.object AS verb,
  COUNT(*) as count
FROM tuples t
JOIN actors a ON t.subject = a.actor_id
WHERE t.portco_id = :portco_id
  AND t.predicate = 'executed'
  AND t.object = :verb
  AND t.timestamp BETWEEN :start AND :end
  AND t.confidence >= :threshold
GROUP BY a.actor_type, t.object;
```

---

## 5. Task Execution Reference

This section maps each task from the strategy document's task catalog to specific queries and analysis steps. A Claude Code instance should be able to execute any of these given access to the database.

### Task 1: Verb Compression Identification

```
Input:     portco_ids (list), date_range, confidence_threshold (default 0.7)
Steps:
  1. Query all tuples in range, grouped by object entity.
  2. For each entity, reconstruct the ordered predicate sequence.
  3. Cluster sequences by similarity (fuzzy — allow missing/extra events).
  4. For each cluster, compute:
     - instance count
     - median duration (first event to last event per instance)
     - canonical_path_pct (what fraction follow the modal sequence)
     - human time (sum of durations for 'executed' predicates by human actors)
  5. Rank clusters by: frequency × human_time × canonical_path_pct.
Output:    Ranked list of verb compression candidates with statistics.
Caveats:   Flag clusters with <30 instances as low-confidence.
           Sequences will be messy. Use fuzzy matching, not exact.
```

### Task 2: FTE Absorption

```
Input:     portco_id, role, date_range, confidence_threshold
Steps:
  1. Get all actors with the given role (from actor_roles).
  2. Query all 'executed' tuples for these actors in range.
  3. Group by predicate (verb). For each, compute frequency and avg duration.
  4. Sum to total monthly human hours.
  5. Identify which verbs have agent execution (actor_type = 'agent').
  6. For compressed verbs, compute remaining human hours (override load only).
  7. Report total hours before, current hours, and threshold gap.
Output:    Task portfolio table. Projected hours after next compression candidates.
Caveats:   If actors span multiple roles, hours may be double-counted.
           Flag verbs where duration comes from LM-extracted tuples.
```

### Task 3: Causal Attribution (DiD)

```
Input:     treated_portco_ids, control_portco_ids, per_portco_deployment_dates,
           metric_predicate (e.g., 'approved'), confidence_threshold
Steps:
  1. For each portco, compute monthly metric (e.g., median time from 'created'
     to 'approved' for all entities with both events).
  2. Verify parallel pre-trends: regress metric on time for treated and controls
     separately. Test that slopes are not significantly different.
  3. If parallel: compute DiD = (treated_post - treated_pre) - (control_post - control_pre),
     using each treated portco's own deployment date as the post-period boundary.
  4. Cluster standard errors at portco level.
  5. Report: estimate, standard error, p-value, pre-trend test results.
Output:    DiD estimate with confidence interval. Pre-trend diagnostic plot data.
Caveats:   If pre-trends are not parallel, state this and do not report DiD.
           This estimates operational metric change, not dollar EBITDA.
           Translating to dollars requires linking to Task 2 (hours freed × cost).
           Report portco count explicitly — underpowered results should be flagged.
```

### Task 4: Dose-Response

```
Input:     portco_ids (deployed), verb, date_range, outcome_metric, confidence_threshold
Steps:
  1. Per portco-month, compute adoption intensity:
     agent_count / (agent_count + human_count) for the given verb.
  2. Per portco-month, compute outcome metric.
  3. Plot and report correlation.
  4. Do NOT present as causal without an instrument.
  5. If instrument available (e.g., deployment order), run IV regression.
Output:    Scatter plot data. Correlation coefficient. IV estimate if applicable.
Caveats:   State endogeneity concern explicitly in output.
           Flag if fewer than 15 portco-month observations.
```

### Task 5: Cross-Portco Deployment Curves

```
Input:     portco_ids in deployment order, confidence_threshold
Steps:
  1. Per portco, compute:
     - Time to first compression: gap from platform_deployments.integration_start_date to first
       (agent, executed, verb) tuple.
     - Module reuse rate: fraction of platform_modules at this portco whose
       originated_portco_id is an earlier-deployed portco.
  2. Plot metrics against deployment order.
  3. Fit trend. Test for significance.
  4. Control for portco characteristics (vertical, size, system complexity)
     if available in actor/entity metadata.
Output:    Deployment curve data. Trend estimate. Module reuse trajectory.
Caveats:   Flag selection bias risk if portcos are not randomly ordered.
           Distinguish module reuse (platform compounding) from team learning.
           Exclude deployments that have not yet reached first compression when fitting the time trend.
```

### Task 6: Acquisition Target Scoring

```
Input:     target_characteristics (vertical, revenue, headcount, system_landscape,
           operational_complexity), confidence_threshold
Steps:
  1. Retrieve characteristics for all portcos with completed deployments.
  2. For each, retrieve: uplift trajectory (from Task 3), time to first
     compression (from Task 5), verb compression profile (from Task 1).
  3. Compute similarity between target and each prior portco on observable
     characteristics.
  4. For the k most similar portcos, report:
     - Observed uplift range and trajectory
     - Time to first compression
     - Which verbs compressed first
     - Integration cost (from platform_deployments)
  5. Present as a prediction interval, not a point estimate.
Output:    Predicted uplift range with confidence interval.
           Comparable portco profiles.
           Key risk factors (e.g., target uses an ERP not previously integrated).
Caveats:   With <10 prior deployments, the prediction is rough. State this.
           Observable characteristics may not capture what drives uplift
           (management quality, change tolerance). Flag unobservables.
           The model improves with each deployment — report expected
           prediction accuracy trajectory.
```

### Task 7: Studio Seed Scoring

```
Input:     verb (compressed), portco_ids where deployed, confidence_threshold
Steps:
  1. Per portco, reconstruct the predicate sequence for all instances of this verb.
  2. Compute pairwise edit distance (normalized) across portcos.
  3. Report: mean pairwise distance, reuse rate, customization surface.
Output:    Similarity matrix. Product candidate score. Customization profile.
Caveats:   Edit distance is coarse. Flag sequences that are quantitatively
           similar but differ in exception handling paths.
           This produces a quantitative signal, not a final decision.
```

---

## 6. Sequencing

| Phase | Months | Deliverables |
|-------|--------|-------------|
| 1 | 1–3 | Predicate mapping layer for first 3–5 portcos. Deterministic extraction pipeline for ERP/CRM/HRIS. Artifact storage. CFO-signed baselines. |
| 2 | 3–6 | LM extraction pipeline for transcripts/emails. Tasks 1 and 2 operational (verb compression, FTE absorption). |
| 3 | 6–12 | 6+ months of pre-deployment data accumulated. Task 3 (DiD) first run. Task 4 (dose-response) descriptive pass. Task 6 (acquisition scoring) initial pass with limited comparables. |
| 4 | 12+ | 10+ sequential deployments. Tasks 5, 6, and 7 (deployment curves, acquisition scoring with more data, seed scoring). |

---

## 7. Open Implementation Questions

**Predicate mapping maintenance.** Who owns the mapping when a source system updates its event types? Need a process for detecting unmapped events and updating the vocabulary.

**Confidence threshold tuning.** The default 0.7 is arbitrary. Needs calibration against a labeled set of tier 1 artifacts where a human has verified the correct tuples.

**Snapshot strategy.** For log volumes beyond ~10M tuples, replaying from origin becomes expensive. Periodic materialized snapshots of common projections (entity state, role task portfolios) will be needed, with the constraint that the econometrician must still be able to query arbitrary historical states.

**Multi-system entities.** A single real-world entity may appear in multiple source systems with different identifiers (e.g., the same vendor in SAP and Salesforce). Entity resolution across systems is required for cross-system sequence reconstruction.

**Privacy and access control.** Tier 1 artifacts (transcripts, emails) contain sensitive content. The tuple store is an abstraction that may be more broadly accessible, but access to tier 1 content for audit/re-extraction must be governed.
