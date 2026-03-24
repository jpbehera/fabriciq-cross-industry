# Law Firm Operations — Ontology Design

## Overview

**Ontology Name:** `LawFirmOpsOntology`

This ontology models law firm operations with a focus on **documentation burden** —
quantifying how much attorney time is consumed by time entries, document management,
court filings, discovery reviews, and contract drafting versus substantive legal
analysis and client advisory work.

The design captures **6 entity types**, **5 relationship types**, and **13
contextualizations** spanning real-time event streams and batch analytical facts.

| Metric | Count |
|--------|-------|
| Entity Types | 6 |
| Relationship Types | 5 |
| Event Fact Tables (Eventhouse) | 8 |
| Batch Fact Tables (Lakehouse) | 4 |
| Stream Tables (Eventhouse) | 5 |
| Total Contextualizations | 13 |

---

## Concept Mapping

| RDF / OWL Concept | Fabric IQ Equivalent | Description |
|--------------------|----------------------|-------------|
| `owl:Class` | Entity Type | Attorney, Client, Matter, etc. |
| `owl:DatatypeProperty` | Property | Columns on dimension tables |
| `owl:ObjectProperty` | Relationship Type | Links between entity types |
| `rdf:type` | Entity Instance | Row in a dimension table |
| Named Graph / Context | Contextualization | Fact or stream table binding |
| `rdfs:label` | Display Name | Human-readable name |
| `rdfs:comment` | Description | Detailed explanation |
| `xsd:dateTime` | Timestamp Column | Event time in fact/stream tables |

---

## Entity Types

### ENT-001: Attorney

| Property | Type | Description |
|----------|------|-------------|
| attorney_id | string | Primary key |
| name | string | Full name |
| role | string | Partner, Associate, Counsel, etc. |
| practice_group | string | Practice group assignment |
| bar_admission | string | State bar admission(s) |
| years_experience | integer | Years since bar admission |
| billing_rate | decimal | Hourly billing rate (USD) |
| hire_date | date | Date hired at the firm |

**Source:** `dim_attorneys.csv`
**Key:** `attorney_id`

---

### ENT-002: Client

| Property | Type | Description |
|----------|------|-------------|
| client_id | string | Primary key |
| name | string | Client / organization name |
| industry | string | Client industry vertical |
| relationship_start | date | Date relationship began |
| billing_arrangement | string | Hourly, flat-fee, contingency, etc. |
| annual_revenue | decimal | Estimated annual revenue from client |
| matter_count | integer | Active matter count |

**Source:** `dim_clients.csv`
**Key:** `client_id`

---

### ENT-003: Matter

| Property | Type | Description |
|----------|------|-------------|
| matter_id | string | Primary key |
| client_id | string | Foreign key → Client |
| name | string | Matter name / description |
| practice_area | string | Litigation, Corporate, IP, etc. |
| matter_type | string | Type classification |
| open_date | date | Date matter was opened |
| status | string | Open, Closed, On-Hold |
| budget | decimal | Approved budget (USD) |
| lead_attorney_id | string | Foreign key → Attorney |

**Source:** `dim_matters.csv`
**Key:** `matter_id`

---

### ENT-004: LegalTaskType

| Property | Type | Description |
|----------|------|-------------|
| task_type_id | string | Primary key |
| name | string | Task type label |
| category | string | Substantive, Administrative, Research, etc. |
| billable_flag | boolean | Whether task is billable |
| avg_duration_min | integer | Average duration in minutes |
| requires_review | boolean | Whether output requires partner review |

**Source:** `dim_legal_task_types.csv`
**Key:** `task_type_id`

---

### ENT-005: PracticeGroup

| Property | Type | Description |
|----------|------|-------------|
| practice_group_id | string | Primary key |
| name | string | Practice group name |
| office | string | Office location |
| attorney_count | integer | Number of attorneys |
| revenue_target | decimal | Annual revenue target (USD) |
| specializations | string | Comma-separated specializations |

**Source:** `dim_practice_groups.csv`
**Key:** `practice_group_id`

---

### ENT-006: Court

| Property | Type | Description |
|----------|------|-------------|
| court_id | string | Primary key |
| name | string | Court name |
| jurisdiction | string | Federal, State, County, etc. |
| type | string | Trial, Appellate, Bankruptcy, etc. |
| filing_requirements | string | Filing format / rules summary |
| efiling_system | string | Electronic filing system name |

**Source:** `dim_courts.csv`
**Key:** `court_id`

---

## Relationship Types

### REL-001: represents

| Field | Value |
|-------|-------|
| Name | represents |
| Source Entity | Attorney (ENT-001) |
| Target Entity | Client (ENT-002) |
| Cardinality | Many-to-Many |
| Description | Attorney represents client across one or more matters |
| Derived From | `dim_matters` (attorney ↔ client via matter assignments) |

### REL-002: works_on

| Field | Value |
|-------|-------|
| Name | works_on |
| Source Entity | Attorney (ENT-001) |
| Target Entity | Matter (ENT-003) |
| Cardinality | Many-to-Many |
| Description | Attorney performs billable and non-billable work on a matter |
| Derived From | `fact_time_entries` (attorney_id → matter_id) |

### REL-003: retained_by

| Field | Value |
|-------|-------|
| Name | retained_by |
| Source Entity | Matter (ENT-003) |
| Target Entity | Client (ENT-002) |
| Cardinality | Many-to-One |
| Description | Matter is retained by (belongs to) a client |
| Derived From | `dim_matters.client_id` |

### REL-004: member_of

| Field | Value |
|-------|-------|
| Name | member_of |
| Source Entity | Attorney (ENT-001) |
| Target Entity | PracticeGroup (ENT-005) |
| Cardinality | Many-to-One |
| Description | Attorney belongs to a practice group |
| Derived From | `dim_attorneys.practice_group` → `dim_practice_groups` |

### REL-005: filed_in

| Field | Value |
|-------|-------|
| Name | filed_in |
| Source Entity | Matter (ENT-003) |
| Target Entity | Court (ENT-006) |
| Cardinality | Many-to-One |
| Description | Matter has filings in a specific court |
| Derived From | `fact_filing_events.court_id` |

---

## Contextualizations

### Event Fact Contextualizations (Eventhouse — KQL DB)

| ID | Contextualization | Fact Table | Primary Entity | Timestamp | Doc Burden Metric |
|----|-------------------|------------|----------------|-----------|-------------------|
| CTX-001 | TimeEntryContext | fact_time_entries | Attorney | date | entry_time_min, write_down_pct |
| CTX-002 | DMSInteractionContext | fact_dms_interactions | Attorney | timestamp | duration_ms |
| CTX-003 | FilingEventContext | fact_filing_events | Matter | timestamp | doc_time_min |
| CTX-004 | DiscoveryEventContext | fact_discovery_events | Attorney | date | doc_time_min, docs_reviewed |
| CTX-005 | ContractEventContext | fact_contract_events | Matter | timestamp | doc_time_min, redline_count |
| CTX-006 | MatterTransferContext | fact_matter_transfers | Matter | timestamp | doc_time_min, open_items |
| CTX-007 | BillingEventContext | fact_billing_events | Matter | timestamp | write_down_amount |
| CTX-008 | DeadlineAlertContext | fact_deadline_alerts | Matter | timestamp | days_remaining |

### Batch Fact Contextualizations (Lakehouse)

| ID | Contextualization | Fact Table | Primary Entity | Grain |
|----|-------------------|------------|----------------|-------|
| CTX-009 | AttorneyWellnessContext | fact_attorney_wellness | Attorney | Monthly survey |
| CTX-010 | WorkProductQualityContext | fact_work_product_quality | Attorney | Per document |
| CTX-011 | ClientSatisfactionContext | fact_client_satisfaction | Client | Per survey |
| CTX-012 | MatterPerformanceContext | fact_matter_performance | Matter | Monthly |

### Stream Contextualization (Eventhouse — real-time)

| ID | Contextualization | Stream Table | Primary Entity | Latency |
|----|-------------------|-------------|----------------|---------|
| CTX-013 | RealTimeActivityContext | stream_dms_activity | Attorney | < 5 sec |
| CTX-013 | RealTimeActivityContext | stream_court_deadlines | Matter | < 5 sec |
| CTX-013 | RealTimeActivityContext | stream_discovery_progress | Attorney | < 5 sec |
| CTX-013 | RealTimeActivityContext | stream_client_communications | Attorney | < 5 sec |
| CTX-013 | RealTimeActivityContext | stream_time_tracking | Attorney | < 5 sec |

> CTX-013 is a composite contextualization binding all five real-time streams
> into a unified activity context for the Data Agent.

---

## Data Storage Mapping

```
┌──────────────────────────────────────────────────────────┐
│                    LAKEHOUSE                              │
│              (LawFirmLakehouse)                           │
│                                                          │
│  Dimension Tables (CSV → Delta):                         │
│    dim_attorneys          dim_clients                     │
│    dim_matters            dim_legal_task_types            │
│    dim_practice_groups    dim_courts                      │
│                                                          │
│  Batch Fact Tables (CSV → Delta):                        │
│    fact_attorney_wellness                                 │
│    fact_work_product_quality                              │
│    fact_client_satisfaction                               │
│    fact_matter_performance                                │
├──────────────────────────────────────────────────────────┤
│                   EVENTHOUSE                              │
│         (LawFirmEventhouse / LawFirmKQLDB)               │
│                                                          │
│  Event Fact Tables (KQL ingestion):                      │
│    fact_time_entries        fact_dms_interactions         │
│    fact_filing_events       fact_discovery_events         │
│    fact_contract_events     fact_matter_transfers         │
│    fact_billing_events      fact_deadline_alerts          │
│                                                          │
│  Stream Tables (Eventstream → KQL):                      │
│    stream_dms_activity                                   │
│    stream_court_deadlines                                │
│    stream_discovery_progress                             │
│    stream_client_communications                          │
│    stream_time_tracking                                  │
└──────────────────────────────────────────────────────────┘
```

---

## Ontology Visualization

```
                    ┌──────────────┐
                    │ PracticeGroup│
                    │  (ENT-005)   │
                    └──────┬───────┘
                           │
                     member_of (REL-004)
                           │
┌──────────┐    represents │    ┌──────────┐
│  Client  │←─────(REL-001)┼───→│ Attorney │
│ (ENT-002)│               │    │ (ENT-001)│
└────┬─────┘               │    └────┬─────┘
     │                     │         │
     │ retained_by         │    works_on (REL-002)
     │ (REL-003)           │         │
     │                     │         │
     └──────►┌─────────┐◄──┘────────┘
             │  Matter  │
             │ (ENT-003)│
             └────┬─────┘
                  │
            filed_in (REL-005)
                  │
             ┌────▼─────┐        ┌──────────────┐
             │  Court    │        │ LegalTaskType │
             │ (ENT-006) │        │  (ENT-004)    │
             └───────────┘        └───────────────┘

    Contextualizations (fact/stream tables):
    ─────────────────────────────────────────
    CTX-001  TimeEntryContext ─────────► Attorney × Matter
    CTX-002  DMSInteractionContext ────► Attorney
    CTX-003  FilingEventContext ───────► Matter × Court
    CTX-004  DiscoveryEventContext ────► Attorney × Matter
    CTX-005  ContractEventContext ─────► Matter × Attorney
    CTX-006  MatterTransferContext ────► Matter (from/to Attorney)
    CTX-007  BillingEventContext ──────► Matter × Attorney
    CTX-008  DeadlineAlertContext ─────► Matter × Attorney
    CTX-009  AttorneyWellnessContext ──► Attorney
    CTX-010  WorkProductQualityContext ► Attorney
    CTX-011  ClientSatisfactionContext ► Client × Matter
    CTX-012  MatterPerformanceContext ─► Matter × Attorney
    CTX-013  RealTimeActivityContext ──► Attorney × Matter (5 streams)
```

---

## Key Analytical Queries

### 1. Billable vs. Administrative Time Ratio

**Question:** What percentage of attorney time is spent on administrative
documentation (time entries, DMS, emails) versus substantive legal work?

```
Entities:   Attorney, LegalTaskType
Contexts:   CTX-001 (TimeEntryContext), CTX-002 (DMSInteractionContext)
Metrics:    hours_worked, hours_billed, entry_time_min, duration_ms
Pattern:    Aggregate entry_time_min from time entries + DMS duration_ms
            per attorney, compare to total hours_worked. Flag attorneys
            where admin ratio > 35%.
```

### 2. Discovery Document Review Burden

**Question:** How much attorney time is consumed by document review in
discovery matters, and what is the coding throughput per attorney?

```
Entities:   Attorney, Matter
Contexts:   CTX-004 (DiscoveryEventContext), CTX-013 (stream_discovery_progress)
Metrics:    docs_reviewed, docs_coded, privilege_flags, doc_time_min
Pattern:    Calculate docs_reviewed / doc_time_min throughput per attorney.
            Identify attorneys with high privilege_flags rate that slows
            review velocity. Cross-reference with CTX-009 wellness scores.
```

### 3. Filing Deadline Compliance

**Question:** How often are court filings submitted close to or past the
deadline, and what is the documentation preparation time?

```
Entities:   Matter, Court, Attorney
Contexts:   CTX-003 (FilingEventContext), CTX-008 (DeadlineAlertContext)
Metrics:    deadline_date, submitted_date, doc_time_min, days_remaining
Pattern:    Calculate (deadline_date - submitted_date) as buffer_days.
            Flag filings with buffer < 2 days. Correlate doc_time_min
            with buffer_days — shorter prep time = tighter deadlines.
```

### 4. Time Entry Narrative Burden

**Question:** How much time do attorneys spend writing time entry narratives
relative to the actual billable work performed?

```
Entities:   Attorney, Matter, LegalTaskType
Contexts:   CTX-001 (TimeEntryContext)
Metrics:    entry_time_min, hours_worked, narrative, write_down_pct
Pattern:    Ratio = entry_time_min / (hours_worked × 60). Flag entries
            where narrative documentation exceeds 15% of task time.
            Correlate high write_down_pct with poor narrative quality
            (insufficient detail triggers billing disputes).
```

### 5. Matter Transfer Documentation Overhead

**Question:** When matters are transferred between attorneys, how much
documentation overhead is created and how many items are left open?

```
Entities:   Matter, Attorney
Contexts:   CTX-006 (MatterTransferContext), CTX-010 (WorkProductQualityContext)
Metrics:    doc_time_min, open_items, transfer reason
Pattern:    Aggregate doc_time_min per transfer. Track open_items at
            transfer vs. 30 days later. High open_items + high doc_time
            suggests poor knowledge management. Cross-reference with
            work product quality scores for the receiving attorney.
```

---

## Notes

- **Documentation Burden Index (DBI):** A composite score derived from
  entry_time_min + DMS duration + filing doc_time + discovery doc_time
  per attorney per week. Target: DBI < 20% of total billable hours.
- **Ethical Walls:** The ontology supports practice-group-level data
  isolation. Multi-entity queries must respect client confidentiality
  boundaries enforced by matter-level access controls.
- **Billing Realization:** CTX-007 and CTX-012 together enable analysis
  of the write-down → realization pipeline, linking documentation quality
  (CTX-010) to revenue recovery rates.
