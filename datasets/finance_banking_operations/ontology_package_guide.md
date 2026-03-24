# Finance Banking Operations — Ontology Package Guide

## Overview

This guide walks through creating the **FinanceBankingOpsOntology** in Fabric IQ, covering Lakehouse ingestion, Eventhouse KQL table setup, entity types, relationship types, contextualizations, and verification.

The ontology models financial services documentation burden — quantifying how much time advisors spend on compliance documentation, KYC verifications, trade compliance filings, loan processing paperwork, and regulatory exam preparation vs. actual client advisory and relationship management activities.

---

## Prerequisites

| Component       | Name                   | Description                                    |
|-----------------|------------------------|------------------------------------------------|
| **Lakehouse**   | `FinanceLakehouse`     | Stores dim tables and batch fact tables (Delta) |
| **Eventhouse**  | `FinanceEventhouse`    | Stores event facts and real-time streams (KQL) |
| **KQL Database**| `FinanceKQLDB`         | KQL database inside the Eventhouse             |

Ensure all three resources are created in your Fabric workspace before proceeding.

---

## Step 1: Prepare Lakehouse (Spark Ingestion)

Load dimension tables and batch fact tables from CSV into Delta tables in `FinanceLakehouse`.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

base_path = "Files/finance_banking_operations/data"

# --- Dimension Tables ---
dim_tables = [
    "dim_advisors",
    "dim_clients",
    "dim_branches",
    "dim_document_types",
    "dim_products",
    "dim_regulations",
]

for table in dim_tables:
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{base_path}/{table}.csv")
    df.write.mode("overwrite").format("delta").saveAsTable(table)
    print(f"✓ Loaded {table}: {df.count()} rows")

# --- Batch Fact Tables ---
batch_facts = [
    "fact_advisor_wellness",
    "fact_document_quality",
    "fact_client_satisfaction",
    "fact_exam_readiness",
]

for table in batch_facts:
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{base_path}/{table}.csv")
    df.write.mode("overwrite").format("delta").saveAsTable(table)
    print(f"✓ Loaded {table}: {df.count()} rows")
```

---

## Step 2: Prepare Eventhouse (KQL Ingestion)

Ingest event fact tables and streaming tables into `FinanceKQLDB`.

```kql
// --- Event Fact Tables ---

.create table compliance_doc_events (
    event_id: string, advisor_id: string, client_id: string, doc_type_id: string,
    start_time: datetime, duration_minutes: real, status: string,
    error_count: int, regulatory_body: string
)

.create table core_banking_interactions (
    interaction_id: string, advisor_id: string, timestamp: datetime,
    system_module: string, action: string, click_count: int,
    idle_seconds: int, error_code: string
)

.create table kyc_verifications (
    kyc_id: string, advisor_id: string, client_id: string, timestamp: datetime,
    verification_type: string, source: string, result: string,
    time_to_complete_min: real
)

.create table loan_processing (
    loan_id: string, officer_id: string, client_id: string, stage: string,
    start_date: datetime, stage_duration_days: real, doc_count: int,
    rejection_reason: string
)

.create table trade_compliance (
    trade_id: string, advisor_id: string, client_id: string, timestamp: datetime,
    trade_type: string, pre_trade_doc_time_min: real, post_trade_doc_time_min: real
)

.create table case_escalations (
    escalation_id: string, advisor_id: string, client_id: string,
    from_stage: string, to_stage: string, timestamp: datetime,
    reason: string, doc_delay_minutes: real
)

.create table regulatory_alerts (
    alert_id: string, advisor_id: string, client_id: string, timestamp: datetime,
    alert_type: string, severity: string, action_taken: string,
    response_time_min: real
)

.create table branch_presence (
    presence_id: string, advisor_id: string, branch_id: string, date: datetime,
    arrival_time: datetime, departure_time: datetime, remote_hours: real,
    meeting_hours: real
)

// --- Real-Time Stream Tables ---

.create table core_banking_clicks (
    click_id: string, advisor_id: string, timestamp: datetime,
    module: string, screen: string, action: string,
    duration_ms: int, idle_before_ms: int, error_code: string
)

.create table client_interactions (
    interaction_id: string, advisor_id: string, client_id: string,
    timestamp: datetime, channel: string, duration_sec: int,
    topic: string, outcome: string
)

.create table compliance_alerts (
    alert_id: string, advisor_id: string, client_id: string,
    timestamp: datetime, alert_type: string, risk_score: real,
    suppressed: string, action_taken: string
)

.create table trading_events (
    trade_id: string, advisor_id: string, client_id: string,
    timestamp: datetime, instrument: string, action: string,
    pre_trade_check: string, post_trade_filing_status: string
)

.create table branch_presence_stream (
    ping_id: string, advisor_id: string, branch_id: string,
    timestamp: datetime, location_type: string, zone: string,
    is_in_meeting: string
)
```

**Ingest CSV data** for each event fact table:

```kql
// Example: ingest compliance_doc_events from CSV
.ingest into table compliance_doc_events (
    h'abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>/Files/finance_banking_operations/data/fact_compliance_doc_events.csv'
) with (format='csv', ignoreFirstRecord=true)
```

Repeat for all 8 event fact tables and 5 stream tables.

---

## Step 3: Entity Type JSON Definitions

Define all 6 entity types for `FinanceBankingOpsOntology`.

### 3.1 Advisor

```json
{
  "entityTypeName": "Advisor",
  "primaryKey": "advisor_id",
  "properties": [
    {"name": "advisor_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "role", "type": "String"},
    {"name": "branch_id", "type": "String"},
    {"name": "license_type", "type": "String"},
    {"name": "hire_date", "type": "Date"},
    {"name": "AUM_millions", "type": "Float"},
    {"name": "certifications", "type": "String"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_advisors"
  }
}
```

### 3.2 Client

```json
{
  "entityTypeName": "Client",
  "primaryKey": "client_id",
  "properties": [
    {"name": "client_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "account_type", "type": "String"},
    {"name": "risk_profile", "type": "String"},
    {"name": "onboarding_date", "type": "Date"},
    {"name": "segment", "type": "String"},
    {"name": "relationship_manager", "type": "String"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_clients"
  }
}
```

### 3.3 Branch

```json
{
  "entityTypeName": "Branch",
  "primaryKey": "branch_id",
  "properties": [
    {"name": "branch_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "region", "type": "String"},
    {"name": "state", "type": "String"},
    {"name": "branch_type", "type": "String"},
    {"name": "headcount", "type": "Integer"},
    {"name": "compliance_rating", "type": "Float"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_branches"
  }
}
```

### 3.4 DocumentType

```json
{
  "entityTypeName": "DocumentType",
  "primaryKey": "doc_type_id",
  "properties": [
    {"name": "doc_type_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "category", "type": "String"},
    {"name": "regulatory_body", "type": "String"},
    {"name": "required_fields", "type": "String"},
    {"name": "avg_completion_time_min", "type": "Float"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_document_types"
  }
}
```

### 3.5 Product

```json
{
  "entityTypeName": "Product",
  "primaryKey": "product_id",
  "properties": [
    {"name": "product_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "category", "type": "String"},
    {"name": "risk_tier", "type": "String"},
    {"name": "regulatory_class", "type": "String"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_products"
  }
}
```

### 3.6 Regulation

```json
{
  "entityTypeName": "Regulation",
  "primaryKey": "regulation_id",
  "properties": [
    {"name": "regulation_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "body", "type": "String"},
    {"name": "effective_date", "type": "Date"},
    {"name": "documentation_requirements", "type": "String"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_regulations"
  }
}
```

---

## Step 4: Relationship Type JSON Definitions

```json
[
  {
    "relationshipTypeName": "advises",
    "sourceEntityType": "Advisor",
    "targetEntityType": "Client",
    "cardinality": "OneToMany",
    "description": "Advisor advises one or more clients"
  },
  {
    "relationshipTypeName": "stationed_at",
    "sourceEntityType": "Advisor",
    "targetEntityType": "Branch",
    "cardinality": "ManyToOne",
    "description": "Advisor is stationed at a branch"
  },
  {
    "relationshipTypeName": "holds",
    "sourceEntityType": "Client",
    "targetEntityType": "Product",
    "cardinality": "ManyToMany",
    "description": "Client holds one or more financial products"
  },
  {
    "relationshipTypeName": "governed_by",
    "sourceEntityType": "DocumentType",
    "targetEntityType": "Regulation",
    "cardinality": "ManyToOne",
    "description": "Document type is governed by a regulation"
  },
  {
    "relationshipTypeName": "complies_with",
    "sourceEntityType": "Branch",
    "targetEntityType": "Regulation",
    "cardinality": "ManyToMany",
    "description": "Branch must comply with applicable regulations"
  }
]
```

---

## Step 5: Contextualization JSON Definitions

### 5.1 Event Fact Contextualizations (Eventhouse)

```json
[
  {
    "contextualizationName": "ComplianceDocEvent",
    "sourceTable": "compliance_doc_events",
    "store": "Eventhouse",
    "timestampField": "start_time",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"},
      {"field": "doc_type_id", "entityType": "DocumentType"}
    ]
  },
  {
    "contextualizationName": "CoreBankingInteractionEvent",
    "sourceTable": "core_banking_interactions",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"}
    ]
  },
  {
    "contextualizationName": "KYCVerificationEvent",
    "sourceTable": "kyc_verifications",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"}
    ]
  },
  {
    "contextualizationName": "LoanProcessingEvent",
    "sourceTable": "loan_processing",
    "store": "Eventhouse",
    "timestampField": "start_date",
    "entityBindings": [
      {"field": "officer_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"}
    ]
  },
  {
    "contextualizationName": "TradeComplianceEvent",
    "sourceTable": "trade_compliance",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"}
    ]
  },
  {
    "contextualizationName": "CaseEscalationEvent",
    "sourceTable": "case_escalations",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"}
    ]
  },
  {
    "contextualizationName": "RegulatoryAlertEvent",
    "sourceTable": "regulatory_alerts",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"}
    ]
  },
  {
    "contextualizationName": "BranchPresenceEvent",
    "sourceTable": "branch_presence",
    "store": "Eventhouse",
    "timestampField": "date",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "branch_id", "entityType": "Branch"}
    ]
  }
]
```

### 5.2 Real-Time Stream Contextualizations (Eventhouse)

```json
[
  {
    "contextualizationName": "CoreBankingClickStream",
    "sourceTable": "core_banking_clicks",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"}
    ]
  },
  {
    "contextualizationName": "ClientInteractionStream",
    "sourceTable": "client_interactions",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"}
    ]
  },
  {
    "contextualizationName": "ComplianceAlertStream",
    "sourceTable": "compliance_alerts",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"}
    ]
  },
  {
    "contextualizationName": "TradingEventStream",
    "sourceTable": "trading_events",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "client_id", "entityType": "Client"}
    ]
  },
  {
    "contextualizationName": "BranchPresenceStream",
    "sourceTable": "branch_presence_stream",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "branch_id", "entityType": "Branch"}
    ]
  }
]
```

### 5.3 Batch Fact Contextualizations (Lakehouse)

```json
[
  {
    "contextualizationName": "AdvisorWellnessEvent",
    "sourceTable": "fact_advisor_wellness",
    "store": "Lakehouse",
    "timestampField": "date",
    "entityBindings": [
      {"field": "advisor_id", "entityType": "Advisor"},
      {"field": "branch_id", "entityType": "Branch"}
    ]
  },
  {
    "contextualizationName": "DocumentQualityEvent",
    "sourceTable": "fact_document_quality",
    "store": "Lakehouse",
    "timestampField": "date",
    "entityBindings": [
      {"field": "doc_type_id", "entityType": "DocumentType"},
      {"field": "advisor_id", "entityType": "Advisor"}
    ]
  },
  {
    "contextualizationName": "ClientSatisfactionEvent",
    "sourceTable": "fact_client_satisfaction",
    "store": "Lakehouse",
    "timestampField": "date",
    "entityBindings": [
      {"field": "client_id", "entityType": "Client"},
      {"field": "advisor_id", "entityType": "Advisor"}
    ]
  },
  {
    "contextualizationName": "ExamReadinessEvent",
    "sourceTable": "fact_exam_readiness",
    "store": "Lakehouse",
    "timestampField": "date",
    "entityBindings": [
      {"field": "branch_id", "entityType": "Branch"},
      {"field": "regulation_id", "entityType": "Regulation"}
    ]
  }
]
```

---

## Step 6: Create Ontology (Python)

```python
import requests
import json

# --- Configuration ---
WORKSPACE_ID   = "<your-workspace-id>"
ONTOLOGY_NAME  = "FinanceBankingOpsOntology"
FABRIC_API     = f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}"

headers = {
    "Authorization": "Bearer <your-token>",
    "Content-Type": "application/json"
}

# --- 1. Create the Ontology ---
ontology_payload = {
    "displayName": ONTOLOGY_NAME,
    "description": "Finance Banking Operations — advisor documentation burden ontology"
}

resp = requests.post(f"{FABRIC_API}/ontologies", headers=headers, json=ontology_payload)
ontology_id = resp.json()["id"]
print(f"✓ Created ontology: {ontology_id}")

ONTOLOGY_API = f"{FABRIC_API}/ontologies/{ontology_id}"

# --- 2. Create Entity Types ---
entity_types = [
    {
        "entityTypeName": "Advisor",
        "primaryKey": "advisor_id",
        "properties": [
            {"name": "advisor_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "role", "type": "String"}, {"name": "branch_id", "type": "String"},
            {"name": "license_type", "type": "String"}, {"name": "hire_date", "type": "Date"},
            {"name": "AUM_millions", "type": "Float"}, {"name": "certifications", "type": "String"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_advisors"}
    },
    {
        "entityTypeName": "Client",
        "primaryKey": "client_id",
        "properties": [
            {"name": "client_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "account_type", "type": "String"}, {"name": "risk_profile", "type": "String"},
            {"name": "onboarding_date", "type": "Date"}, {"name": "segment", "type": "String"},
            {"name": "relationship_manager", "type": "String"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_clients"}
    },
    {
        "entityTypeName": "Branch",
        "primaryKey": "branch_id",
        "properties": [
            {"name": "branch_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "region", "type": "String"}, {"name": "state", "type": "String"},
            {"name": "branch_type", "type": "String"}, {"name": "headcount", "type": "Integer"},
            {"name": "compliance_rating", "type": "Float"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_branches"}
    },
    {
        "entityTypeName": "DocumentType",
        "primaryKey": "doc_type_id",
        "properties": [
            {"name": "doc_type_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "category", "type": "String"}, {"name": "regulatory_body", "type": "String"},
            {"name": "required_fields", "type": "String"},
            {"name": "avg_completion_time_min", "type": "Float"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_document_types"}
    },
    {
        "entityTypeName": "Product",
        "primaryKey": "product_id",
        "properties": [
            {"name": "product_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "category", "type": "String"}, {"name": "risk_tier", "type": "String"},
            {"name": "regulatory_class", "type": "String"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_products"}
    },
    {
        "entityTypeName": "Regulation",
        "primaryKey": "regulation_id",
        "properties": [
            {"name": "regulation_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "body", "type": "String"}, {"name": "effective_date", "type": "Date"},
            {"name": "documentation_requirements", "type": "String"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_regulations"}
    }
]

for et in entity_types:
    resp = requests.post(f"{ONTOLOGY_API}/entityTypes", headers=headers, json=et)
    print(f"  ✓ Entity type: {et['entityTypeName']}")

# --- 3. Create Relationship Types ---
relationships = [
    {"relationshipTypeName": "advises", "sourceEntityType": "Advisor",
     "targetEntityType": "Client", "cardinality": "OneToMany"},
    {"relationshipTypeName": "stationed_at", "sourceEntityType": "Advisor",
     "targetEntityType": "Branch", "cardinality": "ManyToOne"},
    {"relationshipTypeName": "holds", "sourceEntityType": "Client",
     "targetEntityType": "Product", "cardinality": "ManyToMany"},
    {"relationshipTypeName": "governed_by", "sourceEntityType": "DocumentType",
     "targetEntityType": "Regulation", "cardinality": "ManyToOne"},
    {"relationshipTypeName": "complies_with", "sourceEntityType": "Branch",
     "targetEntityType": "Regulation", "cardinality": "ManyToMany"}
]

for rel in relationships:
    resp = requests.post(f"{ONTOLOGY_API}/relationshipTypes", headers=headers, json=rel)
    print(f"  ✓ Relationship: {rel['relationshipTypeName']}")

# --- 4. Create Contextualizations ---
contextualizations = [
    # Event facts (Eventhouse)
    {"contextualizationName": "ComplianceDocEvent", "sourceTable": "compliance_doc_events",
     "store": "Eventhouse", "timestampField": "start_time",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"},
         {"field": "doc_type_id", "entityType": "DocumentType"}]},
    {"contextualizationName": "CoreBankingInteractionEvent", "sourceTable": "core_banking_interactions",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"}]},
    {"contextualizationName": "KYCVerificationEvent", "sourceTable": "kyc_verifications",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"}]},
    {"contextualizationName": "LoanProcessingEvent", "sourceTable": "loan_processing",
     "store": "Eventhouse", "timestampField": "start_date",
     "entityBindings": [
         {"field": "officer_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"}]},
    {"contextualizationName": "TradeComplianceEvent", "sourceTable": "trade_compliance",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"}]},
    {"contextualizationName": "CaseEscalationEvent", "sourceTable": "case_escalations",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"}]},
    {"contextualizationName": "RegulatoryAlertEvent", "sourceTable": "regulatory_alerts",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"}]},
    {"contextualizationName": "BranchPresenceEvent", "sourceTable": "branch_presence",
     "store": "Eventhouse", "timestampField": "date",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "branch_id", "entityType": "Branch"}]},
    # Real-time streams (Eventhouse)
    {"contextualizationName": "CoreBankingClickStream", "sourceTable": "core_banking_clicks",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"}]},
    {"contextualizationName": "ClientInteractionStream", "sourceTable": "client_interactions",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"}]},
    {"contextualizationName": "ComplianceAlertStream", "sourceTable": "compliance_alerts",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"}]},
    {"contextualizationName": "TradingEventStream", "sourceTable": "trading_events",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "client_id", "entityType": "Client"}]},
    {"contextualizationName": "BranchPresenceStream", "sourceTable": "branch_presence_stream",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "advisor_id", "entityType": "Advisor"},
         {"field": "branch_id", "entityType": "Branch"}]},
]

for ctx in contextualizations:
    resp = requests.post(f"{ONTOLOGY_API}/contextualizations", headers=headers, json=ctx)
    print(f"  ✓ Contextualization: {ctx['contextualizationName']}")

print(f"\n✅ Ontology '{ONTOLOGY_NAME}' created successfully!")
```

---

## Step 7: Verify Ontology

After creation, verify the ontology components:

```python
# --- Verify Ontology ---
resp = requests.get(f"{ONTOLOGY_API}/entityTypes", headers=headers)
entity_types_created = resp.json().get("value", [])
print(f"Entity Types: {len(entity_types_created)} (expected: 6)")
for et in entity_types_created:
    print(f"  • {et['entityTypeName']} — PK: {et['primaryKey']}")

resp = requests.get(f"{ONTOLOGY_API}/relationshipTypes", headers=headers)
relationships_created = resp.json().get("value", [])
print(f"\nRelationship Types: {len(relationships_created)} (expected: 5)")
for rel in relationships_created:
    print(f"  • {rel['relationshipTypeName']}: {rel['sourceEntityType']} → {rel['targetEntityType']}")

resp = requests.get(f"{ONTOLOGY_API}/contextualizations", headers=headers)
ctx_created = resp.json().get("value", [])
print(f"\nContextualizations: {len(ctx_created)} (expected: 13)")
for ctx in ctx_created:
    print(f"  • {ctx['contextualizationName']} — {ctx['store']}")
```

**Expected Output:**
```
Entity Types: 6 (expected: 6)
  • Advisor — PK: advisor_id
  • Client — PK: client_id
  • Branch — PK: branch_id
  • DocumentType — PK: doc_type_id
  • Product — PK: product_id
  • Regulation — PK: regulation_id

Relationship Types: 5 (expected: 5)
  • advises: Advisor → Client
  • stationed_at: Advisor → Branch
  • holds: Client → Product
  • governed_by: DocumentType → Regulation
  • complies_with: Branch → Regulation

Contextualizations: 13 (expected: 13)
  • ComplianceDocEvent — Eventhouse
  • CoreBankingInteractionEvent — Eventhouse
  • KYCVerificationEvent — Eventhouse
  • LoanProcessingEvent — Eventhouse
  • TradeComplianceEvent — Eventhouse
  • CaseEscalationEvent — Eventhouse
  • RegulatoryAlertEvent — Eventhouse
  • BranchPresenceEvent — Eventhouse
  • CoreBankingClickStream — Eventhouse
  • ClientInteractionStream — Eventhouse
  • ComplianceAlertStream — Eventhouse
  • TradingEventStream — Eventhouse
  • BranchPresenceStream — Eventhouse
```

---

## Data Binding Summary

| Component           | Store      | Table Count | Description                                         |
|---------------------|------------|-------------|-----------------------------------------------------|
| Dimension Tables    | Lakehouse  | 6           | Advisor, Client, Branch, DocumentType, Product, Regulation |
| Batch Fact Tables   | Lakehouse  | 4           | Wellness, Document Quality, Client Satisfaction, Exam Readiness |
| Event Fact Tables   | Eventhouse | 8           | Compliance docs, Banking interactions, KYC, Loans, Trade, Escalations, Alerts, Presence |
| Stream Tables       | Eventhouse | 5           | Banking clicks, Client interactions, Compliance alerts, Trading events, Branch presence |
| **Total**           | **Both**   | **23**      | Full advisor documentation burden data model         |

---

## Built-In Data Patterns

The `FinanceBankingOpsOntology` is designed to surface these key documentation burden patterns:

### Pattern 1: Advisor Compliance Overload
**Signal:** `compliance_doc_events` → high `duration_minutes` per advisor, correlated with `error_count` and `regulatory_body` distribution.
**Insight:** Identifies advisors spending disproportionate time on compliance documentation — especially multi-regulatory-body advisors serving clients subject to SEC, FINRA, and state regulations simultaneously. High error counts signal documentation fatigue.

### Pattern 2: KYC Documentation Cascade
**Signal:** `kyc_verifications` → `result == "Fail"` or `result == "Escalated"` → triggers additional documentation cycles in `compliance_doc_events`.
**Insight:** Failed KYC verifications cascade into re-verification documentation, additional compliance doc events, and case escalations. Manual verifications (`source == "Manual"`) take 3–5× longer than automated checks — opportunity for automation ROI.

### Pattern 3: Trade Pre/Post Documentation Gap
**Signal:** `trade_compliance` → `pre_trade_doc_time_min` vs. `post_trade_doc_time_min` imbalance, correlated with `trade_type`.
**Insight:** Post-trade documentation often exceeds pre-trade due to regulatory filing requirements. Rebalance and Transfer trades carry 2× the post-trade burden of simple Buy/Sell trades. Links to `regulatory_alerts` when filings are overdue.

### Pattern 4: Loan Processing Doc Bottleneck
**Signal:** `loan_processing` → `stage_duration_days` spikes at Underwriting and Closing stages, driven by `doc_count` requirements and `rejection_reason` rework loops.
**Insight:** Loan officers spend 40–60% of processing time on documentation gathering and submission. Rejection-driven rework in the Underwriting stage doubles the documentation load — each rejection cycle adds 5–8 additional documents.

### Pattern 5: Exam Readiness Documentation Sprints
**Signal:** `fact_exam_readiness` → `days_to_exam < 30` with `doc_completion_pct < 85%` triggers documentation sprints that spike `compliance_doc_events` volume for affected branches.
**Insight:** Branches entering the 30-day exam window with documentation gaps trigger advisor reassignment to compliance documentation, pulling advisors away from client-facing activities. Pre-exam sprints correlate with drops in `fact_client_satisfaction.nps_score`.
