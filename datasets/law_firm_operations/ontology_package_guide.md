# Law Firm Operations — Ontology Package Guide

## Prerequisites

| Resource | Name | Purpose |
|----------|------|---------|
| Lakehouse | `LawFirmLakehouse` | Dimension tables + batch fact tables (Delta) |
| Eventhouse | `LawFirmEventhouse` | Event fact tables + stream tables (KQL) |
| KQL Database | `LawFirmKQLDB` | Query engine for Eventhouse data |
| Eventstream | (per stream table) | Real-time ingestion for 5 stream tables |

Ensure the Fabric workspace has all four resources provisioned before proceeding.

---

## Step 1: Prepare Lakehouse

Upload CSV files to the Lakehouse under the base path:

```
Files/law_firm_operations/data/
```

### Dimension Tables

| File | Target Delta Table | Row Key |
|------|--------------------|---------|
| `dim_attorneys.csv` | dim_attorneys | attorney_id |
| `dim_clients.csv` | dim_clients | client_id |
| `dim_matters.csv` | dim_matters | matter_id |
| `dim_legal_task_types.csv` | dim_legal_task_types | task_type_id |
| `dim_practice_groups.csv` | dim_practice_groups | practice_group_id |
| `dim_courts.csv` | dim_courts | court_id |

### Batch Fact Tables

| File | Target Delta Table | Row Key |
|------|--------------------|---------|
| `fact_attorney_wellness.csv` | fact_attorney_wellness | survey_id |
| `fact_work_product_quality.csv` | fact_work_product_quality | quality_id |
| `fact_client_satisfaction.csv` | fact_client_satisfaction | survey_id |
| `fact_matter_performance.csv` | fact_matter_performance | perf_id |

### Load Notebook Snippet

```python
base_path = "Files/law_firm_operations/data"

dim_tables = [
    "dim_attorneys", "dim_clients", "dim_matters",
    "dim_legal_task_types", "dim_practice_groups", "dim_courts"
]
batch_facts = [
    "fact_attorney_wellness", "fact_work_product_quality",
    "fact_client_satisfaction", "fact_matter_performance"
]

for table in dim_tables + batch_facts:
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{base_path}/{table}.csv")
    df.write.mode("overwrite").format("delta").saveAsTable(table)
    print(f"Loaded {table}: {df.count()} rows")
```

---

## Step 2: Prepare Eventhouse

Ingest event fact CSVs and configure stream tables in the KQL database.

### Event Fact Tables

| File | KQL Table | Timestamp Column |
|------|-----------|------------------|
| `fact_time_entries.csv` | fact_time_entries | date |
| `fact_dms_interactions.csv` | fact_dms_interactions | timestamp |
| `fact_filing_events.csv` | fact_filing_events | timestamp |
| `fact_discovery_events.csv` | fact_discovery_events | date |
| `fact_contract_events.csv` | fact_contract_events | timestamp |
| `fact_matter_transfers.csv` | fact_matter_transfers | timestamp |
| `fact_billing_events.csv` | fact_billing_events | timestamp |
| `fact_deadline_alerts.csv` | fact_deadline_alerts | timestamp |

### Stream Tables

| Stream | KQL Table | Timestamp Column | Source |
|--------|-----------|------------------|--------|
| DMS Activity | stream_dms_activity | timestamp | Eventstream |
| Court Deadlines | stream_court_deadlines | timestamp | Eventstream |
| Discovery Progress | stream_discovery_progress | timestamp | Eventstream |
| Client Comms | stream_client_communications | timestamp | Eventstream |
| Time Tracking | stream_time_tracking | timestamp | Eventstream |

### KQL Table Creation (example)

```kql
.create table fact_time_entries (
    entry_id: string,
    attorney_id: string,
    matter_id: string,
    ['date']: datetime,
    task_type: string,
    hours_worked: real,
    hours_billed: real,
    narrative: string,
    entry_time_min: int,
    write_down_pct: real
)

.create table stream_time_tracking (
    entry_id: string,
    attorney_id: string,
    timestamp: datetime,
    matter_id: string,
    task_type: string,
    duration_min: int,
    billable_flag: bool
)
```

---

## Step 3: Entity Type JSON Definitions

### ENT-001: Attorney

```json
{
    "entity_type_name": "Attorney",
    "entity_type_description": "Law firm attorney with billing rate and practice group assignment",
    "table_name": "dim_attorneys",
    "table_source": "Lakehouse",
    "key_column": "attorney_id",
    "properties": [
        {"name": "attorney_id", "type": "string", "description": "Unique attorney identifier"},
        {"name": "name", "type": "string", "description": "Full name"},
        {"name": "role", "type": "string", "description": "Partner, Associate, Counsel, Of Counsel"},
        {"name": "practice_group", "type": "string", "description": "Practice group assignment"},
        {"name": "bar_admission", "type": "string", "description": "State bar admission(s)"},
        {"name": "years_experience", "type": "integer", "description": "Years since bar admission"},
        {"name": "billing_rate", "type": "decimal", "description": "Hourly billing rate in USD"},
        {"name": "hire_date", "type": "date", "description": "Date hired at the firm"}
    ]
}
```

### ENT-002: Client

```json
{
    "entity_type_name": "Client",
    "entity_type_description": "Client organization with billing arrangement and revenue data",
    "table_name": "dim_clients",
    "table_source": "Lakehouse",
    "key_column": "client_id",
    "properties": [
        {"name": "client_id", "type": "string", "description": "Unique client identifier"},
        {"name": "name", "type": "string", "description": "Client organization name"},
        {"name": "industry", "type": "string", "description": "Client industry vertical"},
        {"name": "relationship_start", "type": "date", "description": "Date relationship began"},
        {"name": "billing_arrangement", "type": "string", "description": "Hourly, flat-fee, contingency, blended"},
        {"name": "annual_revenue", "type": "decimal", "description": "Estimated annual revenue from client"},
        {"name": "matter_count", "type": "integer", "description": "Number of active matters"}
    ]
}
```

### ENT-003: Matter

```json
{
    "entity_type_name": "Matter",
    "entity_type_description": "Legal matter with practice area, budget, and status tracking",
    "table_name": "dim_matters",
    "table_source": "Lakehouse",
    "key_column": "matter_id",
    "properties": [
        {"name": "matter_id", "type": "string", "description": "Unique matter identifier"},
        {"name": "client_id", "type": "string", "description": "Foreign key to Client entity"},
        {"name": "name", "type": "string", "description": "Matter name or description"},
        {"name": "practice_area", "type": "string", "description": "Litigation, Corporate, IP, Tax, etc."},
        {"name": "matter_type", "type": "string", "description": "Type classification"},
        {"name": "open_date", "type": "date", "description": "Date matter was opened"},
        {"name": "status", "type": "string", "description": "Open, Closed, On-Hold"},
        {"name": "budget", "type": "decimal", "description": "Approved budget in USD"},
        {"name": "lead_attorney_id", "type": "string", "description": "Foreign key to Attorney entity"}
    ]
}
```

### ENT-004: LegalTaskType

```json
{
    "entity_type_name": "LegalTaskType",
    "entity_type_description": "Classification of legal tasks by category and billability",
    "table_name": "dim_legal_task_types",
    "table_source": "Lakehouse",
    "key_column": "task_type_id",
    "properties": [
        {"name": "task_type_id", "type": "string", "description": "Unique task type identifier"},
        {"name": "name", "type": "string", "description": "Task type label"},
        {"name": "category", "type": "string", "description": "Substantive, Administrative, Research, etc."},
        {"name": "billable_flag", "type": "boolean", "description": "Whether task is billable"},
        {"name": "avg_duration_min", "type": "integer", "description": "Average duration in minutes"},
        {"name": "requires_review", "type": "boolean", "description": "Whether output requires partner review"}
    ]
}
```

### ENT-005: PracticeGroup

```json
{
    "entity_type_name": "PracticeGroup",
    "entity_type_description": "Practice group with revenue targets and specialization areas",
    "table_name": "dim_practice_groups",
    "table_source": "Lakehouse",
    "key_column": "practice_group_id",
    "properties": [
        {"name": "practice_group_id", "type": "string", "description": "Unique practice group identifier"},
        {"name": "name", "type": "string", "description": "Practice group name"},
        {"name": "office", "type": "string", "description": "Office location"},
        {"name": "attorney_count", "type": "integer", "description": "Number of attorneys in group"},
        {"name": "revenue_target", "type": "decimal", "description": "Annual revenue target in USD"},
        {"name": "specializations", "type": "string", "description": "Comma-separated specialization areas"}
    ]
}
```

### ENT-006: Court

```json
{
    "entity_type_name": "Court",
    "entity_type_description": "Court with jurisdiction, type, and electronic filing details",
    "table_name": "dim_courts",
    "table_source": "Lakehouse",
    "key_column": "court_id",
    "properties": [
        {"name": "court_id", "type": "string", "description": "Unique court identifier"},
        {"name": "name", "type": "string", "description": "Court name"},
        {"name": "jurisdiction", "type": "string", "description": "Federal, State, County, Municipal"},
        {"name": "type", "type": "string", "description": "Trial, Appellate, Bankruptcy, Administrative"},
        {"name": "filing_requirements", "type": "string", "description": "Filing format rules summary"},
        {"name": "efiling_system", "type": "string", "description": "Electronic filing system name"}
    ]
}
```

---

## Step 4: Relationship Type JSON Definitions

```json
[
    {
        "relationship_name": "represents",
        "source_entity": "Attorney",
        "target_entity": "Client",
        "cardinality": "many-to-many",
        "description": "Attorney represents client across one or more matters"
    },
    {
        "relationship_name": "works_on",
        "source_entity": "Attorney",
        "target_entity": "Matter",
        "cardinality": "many-to-many",
        "description": "Attorney performs billable and non-billable work on a matter"
    },
    {
        "relationship_name": "retained_by",
        "source_entity": "Matter",
        "target_entity": "Client",
        "cardinality": "many-to-one",
        "description": "Matter is retained by (belongs to) a client"
    },
    {
        "relationship_name": "member_of",
        "source_entity": "Attorney",
        "target_entity": "PracticeGroup",
        "cardinality": "many-to-one",
        "description": "Attorney belongs to a practice group"
    },
    {
        "relationship_name": "filed_in",
        "source_entity": "Matter",
        "target_entity": "Court",
        "cardinality": "many-to-one",
        "description": "Matter has filings in a specific court"
    }
]
```

---

## Step 5: Contextualization JSON Definitions

### Event Fact Contextualizations (Eventhouse)

```json
[
    {
        "context_name": "TimeEntryContext",
        "table_name": "fact_time_entries",
        "table_source": "Eventhouse",
        "primary_entity": "Attorney",
        "key_column": "attorney_id",
        "timestamp_column": "date",
        "related_entities": ["Matter"],
        "doc_burden_columns": ["entry_time_min", "write_down_pct"]
    },
    {
        "context_name": "DMSInteractionContext",
        "table_name": "fact_dms_interactions",
        "table_source": "Eventhouse",
        "primary_entity": "Attorney",
        "key_column": "attorney_id",
        "timestamp_column": "timestamp",
        "related_entities": [],
        "doc_burden_columns": ["duration_ms"]
    },
    {
        "context_name": "FilingEventContext",
        "table_name": "fact_filing_events",
        "table_source": "Eventhouse",
        "primary_entity": "Matter",
        "key_column": "matter_id",
        "timestamp_column": "timestamp",
        "related_entities": ["Attorney", "Court"],
        "doc_burden_columns": ["doc_time_min"]
    },
    {
        "context_name": "DiscoveryEventContext",
        "table_name": "fact_discovery_events",
        "table_source": "Eventhouse",
        "primary_entity": "Attorney",
        "key_column": "attorney_id",
        "timestamp_column": "date",
        "related_entities": ["Matter"],
        "doc_burden_columns": ["doc_time_min", "docs_reviewed"]
    },
    {
        "context_name": "ContractEventContext",
        "table_name": "fact_contract_events",
        "table_source": "Eventhouse",
        "primary_entity": "Matter",
        "key_column": "matter_id",
        "timestamp_column": "timestamp",
        "related_entities": ["Attorney"],
        "doc_burden_columns": ["doc_time_min", "redline_count"]
    },
    {
        "context_name": "MatterTransferContext",
        "table_name": "fact_matter_transfers",
        "table_source": "Eventhouse",
        "primary_entity": "Matter",
        "key_column": "matter_id",
        "timestamp_column": "timestamp",
        "related_entities": ["Attorney"],
        "doc_burden_columns": ["doc_time_min", "open_items"]
    },
    {
        "context_name": "BillingEventContext",
        "table_name": "fact_billing_events",
        "table_source": "Eventhouse",
        "primary_entity": "Matter",
        "key_column": "matter_id",
        "timestamp_column": "timestamp",
        "related_entities": ["Attorney"],
        "doc_burden_columns": ["write_down_amount"]
    },
    {
        "context_name": "DeadlineAlertContext",
        "table_name": "fact_deadline_alerts",
        "table_source": "Eventhouse",
        "primary_entity": "Matter",
        "key_column": "matter_id",
        "timestamp_column": "timestamp",
        "related_entities": ["Attorney"],
        "doc_burden_columns": ["days_remaining"]
    }
]
```

### Batch Fact Contextualizations (Lakehouse)

```json
[
    {
        "context_name": "AttorneyWellnessContext",
        "table_name": "fact_attorney_wellness",
        "table_source": "Lakehouse",
        "primary_entity": "Attorney",
        "key_column": "attorney_id",
        "timestamp_column": "date",
        "grain": "Monthly survey",
        "doc_burden_columns": ["billable_pressure_score", "admin_burden_score"]
    },
    {
        "context_name": "WorkProductQualityContext",
        "table_name": "fact_work_product_quality",
        "table_source": "Lakehouse",
        "primary_entity": "Attorney",
        "key_column": "attorney_id",
        "timestamp_column": "date",
        "grain": "Per document",
        "doc_burden_columns": ["accuracy_score", "revision_count", "review_time_min"]
    },
    {
        "context_name": "ClientSatisfactionContext",
        "table_name": "fact_client_satisfaction",
        "table_source": "Lakehouse",
        "primary_entity": "Client",
        "key_column": "client_id",
        "timestamp_column": "date",
        "grain": "Per survey",
        "doc_burden_columns": ["responsiveness_score", "value_score"]
    },
    {
        "context_name": "MatterPerformanceContext",
        "table_name": "fact_matter_performance",
        "table_source": "Lakehouse",
        "primary_entity": "Matter",
        "key_column": "matter_id",
        "timestamp_column": "month",
        "grain": "Monthly",
        "doc_burden_columns": ["realization_pct", "wip_aging_days"]
    }
]
```

### Stream Contextualization (Eventhouse — real-time)

```json
{
    "context_name": "RealTimeActivityContext",
    "table_source": "Eventhouse",
    "streams": [
        {
            "table_name": "stream_dms_activity",
            "primary_entity": "Attorney",
            "key_column": "attorney_id",
            "timestamp_column": "timestamp"
        },
        {
            "table_name": "stream_court_deadlines",
            "primary_entity": "Matter",
            "key_column": "matter_id",
            "timestamp_column": "timestamp"
        },
        {
            "table_name": "stream_discovery_progress",
            "primary_entity": "Attorney",
            "key_column": "attorney_id",
            "timestamp_column": "timestamp"
        },
        {
            "table_name": "stream_client_communications",
            "primary_entity": "Attorney",
            "key_column": "attorney_id",
            "timestamp_column": "timestamp"
        },
        {
            "table_name": "stream_time_tracking",
            "primary_entity": "Attorney",
            "key_column": "attorney_id",
            "timestamp_column": "timestamp"
        }
    ]
}
```

---

## Step 6: Create Ontology

```python
import json

ontology_name = "LawFirmOpsOntology"
ontology_description = (
    "Law firm operations ontology tracking documentation burden — "
    "time entries, DMS interactions, court filings, discovery reviews, "
    "contract drafting, and their impact on attorney productivity, "
    "client satisfaction, and billing realization."
)

# --- Entity Types ---
entity_types = [
    # paste ENT-001 through ENT-006 JSON objects from Step 3
]

# --- Relationship Types ---
relationship_types = [
    # paste relationships array from Step 4
]

# --- Contextualizations ---
contextualizations = {
    "event_facts": [
        # paste 8 event fact contexts from Step 5
    ],
    "batch_facts": [
        # paste 4 batch fact contexts from Step 5
    ],
    "streams": {
        # paste stream contextualization from Step 5
    }
}

# --- Build Ontology Package ---
ontology_package = {
    "ontology_name": ontology_name,
    "ontology_description": ontology_description,
    "entity_types": entity_types,
    "relationship_types": relationship_types,
    "contextualizations": contextualizations
}

# Save to Lakehouse
package_path = "Files/law_firm_operations/LawFirmOpsOntology_package.json"
with open(f"/lakehouse/default/{package_path}", "w") as f:
    json.dump(ontology_package, f, indent=2)

print(f"Ontology package saved to {package_path}")
print(f"  Entity Types:        {len(entity_types)}")
print(f"  Relationship Types:  {len(relationship_types)}")
print(f"  Event Fact Contexts: {len(contextualizations['event_facts'])}")
print(f"  Batch Fact Contexts: {len(contextualizations['batch_facts'])}")
print(f"  Stream Tables:       {len(contextualizations['streams']['streams'])}")
```

### Create via Fabric API (alternative)

```python
from fabriciq import OntologyBuilder

builder = OntologyBuilder(
    workspace_id="<YOUR_WORKSPACE_ID>",
    lakehouse_name="LawFirmLakehouse",
    eventhouse_name="LawFirmEventhouse",
    kql_db_name="LawFirmKQLDB"
)

# Register entity types
for et in entity_types:
    builder.add_entity_type(**et)

# Register relationships
for rel in relationship_types:
    builder.add_relationship(**rel)

# Register contextualizations
for ctx in contextualizations["event_facts"]:
    builder.add_contextualization(**ctx)
for ctx in contextualizations["batch_facts"]:
    builder.add_contextualization(**ctx)
builder.add_stream_contextualization(**contextualizations["streams"])

# Deploy
result = builder.deploy(ontology_name=ontology_name)
print(f"Ontology '{result['name']}' created: {result['id']}")
```

---

## Step 7: Verify

After creation, verify the ontology components:

```
Expected Counts:
  Entity Types:          6  (Attorney, Client, Matter, LegalTaskType, PracticeGroup, Court)
  Relationship Types:    5  (represents, works_on, retained_by, member_of, filed_in)
  Contextualizations:   13  (8 event facts + 4 batch facts + 1 composite stream)
```

### Verification Checklist

| # | Check | Expected |
|---|-------|----------|
| 1 | Entity types created | 6 |
| 2 | All dim tables bound | dim_attorneys, dim_clients, dim_matters, dim_legal_task_types, dim_practice_groups, dim_courts |
| 3 | Relationship types created | 5 |
| 4 | Event fact contextualizations | 8 (CTX-001 through CTX-008) |
| 5 | Batch fact contextualizations | 4 (CTX-009 through CTX-012) |
| 6 | Stream contextualization | 1 composite (CTX-013) with 5 streams |
| 7 | Total contextualizations | 13 |
| 8 | Lakehouse tables accessible | 10 (6 dim + 4 batch fact) |
| 9 | Eventhouse tables accessible | 13 (8 event fact + 5 stream) |
| 10 | KQL queries return data | Spot-check each event/stream table |

---

## Data Binding Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    LawFirmOpsOntology                           │
│                                                                 │
│  Entity Types (6)              Lakehouse Delta Tables           │
│  ├─ Attorney ──────────────── dim_attorneys                     │
│  ├─ Client ────────────────── dim_clients                       │
│  ├─ Matter ────────────────── dim_matters                       │
│  ├─ LegalTaskType ─────────── dim_legal_task_types              │
│  ├─ PracticeGroup ─────────── dim_practice_groups               │
│  └─ Court ─────────────────── dim_courts                        │
│                                                                 │
│  Batch Facts (4)               Lakehouse Delta Tables           │
│  ├─ AttorneyWellnessCtx ───── fact_attorney_wellness            │
│  ├─ WorkProductQualityCtx ─── fact_work_product_quality         │
│  ├─ ClientSatisfactionCtx ─── fact_client_satisfaction          │
│  └─ MatterPerformanceCtx ──── fact_matter_performance           │
│                                                                 │
│  Event Facts (8)               Eventhouse KQL Tables            │
│  ├─ TimeEntryCtx ──────────── fact_time_entries                 │
│  ├─ DMSInteractionCtx ─────── fact_dms_interactions             │
│  ├─ FilingEventCtx ────────── fact_filing_events                │
│  ├─ DiscoveryEventCtx ─────── fact_discovery_events             │
│  ├─ ContractEventCtx ──────── fact_contract_events              │
│  ├─ MatterTransferCtx ─────── fact_matter_transfers             │
│  ├─ BillingEventCtx ───────── fact_billing_events               │
│  └─ DeadlineAlertCtx ──────── fact_deadline_alerts              │
│                                                                 │
│  Streams (5)                   Eventhouse KQL Tables            │
│  ├─ stream_dms_activity                                         │
│  ├─ stream_court_deadlines                                      │
│  ├─ stream_discovery_progress                                   │
│  ├─ stream_client_communications                                │
│  └─ stream_time_tracking                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Built-In Data Patterns

### Pattern 1: Attorney Overload Detection

**Signal:** Attorney with billable_pressure_score > 8 AND admin_burden_score > 7
from `fact_attorney_wellness`, combined with entry_time_min consistently > 20 min
per time entry from `fact_time_entries`.

**Action:** Flag for practice group lead review. Consider reallocating matters
or providing paralegal support for administrative documentation tasks.

**Tables:** fact_attorney_wellness, fact_time_entries, dim_attorneys

---

### Pattern 2: Discovery Document Review Cascade

**Signal:** Rising docs_reviewed throughput in `stream_discovery_progress` but
declining accuracy_score in `fact_work_product_quality` for the same attorney.

**Action:** Speed-accuracy tradeoff alert. Discovery review volume is outpacing
quality — increase review checkpoints or add reviewers to the matter.

**Tables:** stream_discovery_progress, fact_work_product_quality, fact_discovery_events

---

### Pattern 3: Filing Deadline Crunch

**Signal:** `stream_court_deadlines` shows days_remaining < 3 AND corresponding
`fact_filing_events` shows doc_time_min increasing (attorney still preparing).

**Action:** Escalation alert to matter lead. Ensure filing is on track and
consider requesting an extension if preparation time is insufficient.

**Tables:** stream_court_deadlines, fact_filing_events, fact_deadline_alerts

---

### Pattern 4: Contract Redline Burden

**Signal:** High redline_count (> 10 per version) in `fact_contract_events`
with increasing doc_time_min across versions for the same contract_id.

**Action:** Negotiation complexity alert. Consider senior attorney involvement
or business-terms escalation when redline cycles exceed 3 rounds with
doc_time_min growth > 25% per round.

**Tables:** fact_contract_events, dim_matters, dim_attorneys

---

### Pattern 5: Billing Write-Down Correlation with Documentation Quality

**Signal:** Matters with high write_down_amount in `fact_billing_events`
correlate with low accuracy_score in `fact_work_product_quality` and high
revision_count. Time entry narratives (entry_time_min) are short, suggesting
insufficient detail.

**Action:** Documentation quality initiative — attorneys with chronic write-downs
need narrative training. Poor time entry descriptions lead to billing disputes
and reduced realization_pct in `fact_matter_performance`.

**Tables:** fact_billing_events, fact_work_product_quality, fact_time_entries,
fact_matter_performance
