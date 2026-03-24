# Advertising Campaign Operations — Ontology Package Guide

## Overview

This guide walks through creating the **AdvertisingCampaignOpsOntology** in Fabric IQ, covering Lakehouse ingestion, Eventhouse KQL table setup, entity types, relationship types, contextualizations, and verification.

The ontology models Out-of-Home (OOH) advertising documentation burden — quantifying how much time Account Executives spend on campaign orders, proof-of-performance reports, charting, contract changes, and work orders vs. actual client-facing selling activities.

---

## Prerequisites

| Component       | Name                      | Description                                    |
|-----------------|---------------------------|------------------------------------------------|
| **Lakehouse**   | `AdvertisingLakehouse`    | Stores dim tables and batch fact tables (Delta) |
| **Eventhouse**  | `AdvertisingEventhouse`   | Stores event facts and real-time streams (KQL) |
| **KQL Database**| `AdvertisingKQLDB`        | KQL database inside the Eventhouse             |

Ensure all three resources are created in your Fabric workspace before proceeding.

---

## Step 1: Prepare Lakehouse (Spark Ingestion)

Load dimension tables and batch fact tables from CSV into Delta tables in `AdvertisingLakehouse`.

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

base_path = "Files/advertising_campaign_operations/data"

# --- Dimension Tables ---
dim_tables = [
    "dim_account_executives",
    "dim_campaigns",
    "dim_inventory_units",
    "dim_markets",
    "dim_advertisers",
    "dim_vendors",
]

for table in dim_tables:
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{base_path}/{table}.csv")
    df.write.mode("overwrite").format("delta").saveAsTable(table)
    print(f"✓ Loaded {table}: {df.count()} rows")

# --- Batch Fact Tables ---
batch_facts = [
    "fact_ae_wellness",
    "fact_production_quality",
    "fact_advertiser_satisfaction",
]

for table in batch_facts:
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{base_path}/{table}.csv")
    df.write.mode("overwrite").format("delta").saveAsTable(table)
    print(f"✓ Loaded {table}: {df.count()} rows")
```

---

## Step 2: Prepare Eventhouse (KQL Ingestion)

Ingest event fact tables and streaming tables into `AdvertisingKQLDB`.

```kql
// --- Event Fact Tables ---

.create table campaign_orders (
    order_id: string, campaign_id: string, ae_id: string, date: datetime,
    order_type: string, units_booked: int, doc_time_min: real,
    proof_cycles: int, status: string, production_vendor_id: string
)

.create table oms_interactions (
    interaction_id: string, ae_id: string, timestamp: datetime,
    system: string, module: string, action: string,
    duration_ms: int, campaign_id: string
)

.create table charting_events (
    charting_id: string, campaign_id: string, chartist_id: string,
    date: datetime, charting_type: string, units_charted: int,
    manual_charts: int, auto_charts: int, doc_time_min: real, ccn_flag: string
)

.create table pop_reports (
    pop_id: string, campaign_id: string, ae_id: string, date: datetime,
    units_verified: int, photos_required: int, photos_submitted: int,
    compliance_pct: real, doc_time_min: real
)

.create table contract_changes (
    ccn_id: string, campaign_id: string, ae_id: string, timestamp: datetime,
    change_type: string, units_affected: int, revenue_impact: real,
    doc_time_min: real, approval_status: string
)

.create table work_orders (
    wo_id: string, campaign_id: string, unit_id: string, timestamp: datetime,
    wo_type: string, posting_instructions: string, vendor_id: string,
    install_status: string, doc_time_min: real
)

.create table proof_approvals (
    approval_id: string, order_id: string, ae_id: string, timestamp: datetime,
    proof_type: string, status: string, reviewer: string,
    cycle_time_hours: real, revision_count: int
)

.create table pop_alerts (
    alert_id: string, campaign_id: string, unit_id: string, timestamp: datetime,
    alert_type: string, severity: string, description: string,
    photos_missing: int, resolution_status: string
)

.create table inventory_tracking (
    tracking_id: string, unit_id: string, timestamp: datetime,
    event_type: string, market_id: string, previous_status: string,
    new_status: string, reason: string, doc_time_min: real
)

// --- Real-Time Stream Tables ---

.create table campaign_pacing (
    pacing_id: string, campaign_id: string, timestamp: datetime,
    impressions_delivered: int, impressions_target: int,
    spend_pct: real, pacing_status: string
)

.create table creative_status (
    status_id: string, order_id: string, campaign_id: string,
    timestamp: datetime, creative_status: string, proof_stage: string,
    days_pending: int, blocker_type: string
)

.create table digital_impressions (
    impression_id: string, campaign_id: string, unit_id: string,
    timestamp: datetime, impressions_count: int,
    dwell_time_sec: real, audience_segment: string
)

.create table installation_events (
    event_id: string, wo_id: string, unit_id: string, timestamp: datetime,
    event_type: string, crew_id: string, status: string,
    photo_uploaded: string, gps_lat: real, gps_lng: real
)

.create table inventory_availability (
    avail_id: string, unit_id: string, market_id: string, timestamp: datetime,
    availability_status: string, hold_type: string,
    campaign_id: string, days_available: int
)
```

**Ingest CSV data** for each event fact table:

```kql
// Example: ingest campaign_orders from CSV
.ingest into table campaign_orders (
    h'abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>/Files/advertising_campaign_operations/data/fact_campaign_orders.csv'
) with (format='csv', ignoreFirstRecord=true)
```

Repeat for all 9 event fact tables and 5 stream tables.

---

## Step 3: Entity Type JSON Definitions

Define all 6 entity types for `AdvertisingCampaignOpsOntology`.

### 3.1 AccountExecutive

```json
{
  "entityTypeName": "AccountExecutive",
  "primaryKey": "ae_id",
  "properties": [
    {"name": "ae_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "role", "type": "String"},
    {"name": "market_id", "type": "String"},
    {"name": "team", "type": "String"},
    {"name": "quota_target", "type": "Float"},
    {"name": "hire_date", "type": "Date"},
    {"name": "specialization", "type": "String"},
    {"name": "active_campaigns", "type": "Integer"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_account_executives"
  }
}
```

### 3.2 Campaign

```json
{
  "entityTypeName": "Campaign",
  "primaryKey": "campaign_id",
  "properties": [
    {"name": "campaign_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "advertiser_id", "type": "String"},
    {"name": "market_id", "type": "String"},
    {"name": "start_date", "type": "Date"},
    {"name": "end_date", "type": "Date"},
    {"name": "budget", "type": "Float"},
    {"name": "media_type", "type": "String"},
    {"name": "contract_value", "type": "Float"},
    {"name": "status", "type": "String"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_campaigns"
  }
}
```

### 3.3 InventoryUnit

```json
{
  "entityTypeName": "InventoryUnit",
  "primaryKey": "unit_id",
  "properties": [
    {"name": "unit_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "type", "type": "String"},
    {"name": "market_id", "type": "String"},
    {"name": "address", "type": "String"},
    {"name": "lat", "type": "Float"},
    {"name": "lng", "type": "Float"},
    {"name": "faces", "type": "Integer"},
    {"name": "illuminated", "type": "String"},
    {"name": "digital", "type": "String"},
    {"name": "size", "type": "String"},
    {"name": "monthly_rate", "type": "Float"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_inventory_units"
  }
}
```

### 3.4 Market

```json
{
  "entityTypeName": "Market",
  "primaryKey": "market_id",
  "properties": [
    {"name": "market_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "region", "type": "String"},
    {"name": "dma_rank", "type": "Integer"},
    {"name": "population", "type": "Integer"},
    {"name": "total_units", "type": "Integer"},
    {"name": "digital_pct", "type": "Float"},
    {"name": "avg_occupancy_rate", "type": "Float"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_markets"
  }
}
```

### 3.5 Advertiser

```json
{
  "entityTypeName": "Advertiser",
  "primaryKey": "advertiser_id",
  "properties": [
    {"name": "advertiser_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "industry", "type": "String"},
    {"name": "annual_spend", "type": "Float"},
    {"name": "campaigns_ytd", "type": "Integer"},
    {"name": "tenure_years", "type": "Integer"},
    {"name": "agency_name", "type": "String"},
    {"name": "contact", "type": "String"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_advertisers"
  }
}
```

### 3.6 Vendor

```json
{
  "entityTypeName": "Vendor",
  "primaryKey": "vendor_id",
  "properties": [
    {"name": "vendor_id", "type": "String"},
    {"name": "name", "type": "String"},
    {"name": "type", "type": "String"},
    {"name": "region", "type": "String"},
    {"name": "specialization", "type": "String"},
    {"name": "avg_turnaround_days", "type": "Float"},
    {"name": "quality_rating", "type": "Float"}
  ],
  "dataBinding": {
    "store": "Lakehouse",
    "tableName": "dim_vendors"
  }
}
```

---

## Step 4: Relationship Type JSON Definitions

```json
[
  {
    "relationshipTypeName": "manages_campaign",
    "sourceEntityType": "AccountExecutive",
    "targetEntityType": "Campaign",
    "cardinality": "OneToMany",
    "description": "AE manages one or more campaigns"
  },
  {
    "relationshipTypeName": "belongs_to_market",
    "sourceEntityType": "Campaign",
    "targetEntityType": "Market",
    "cardinality": "ManyToOne",
    "description": "Campaign runs in a specific market"
  },
  {
    "relationshipTypeName": "placed_by",
    "sourceEntityType": "Campaign",
    "targetEntityType": "Advertiser",
    "cardinality": "ManyToOne",
    "description": "Campaign is placed by an advertiser"
  },
  {
    "relationshipTypeName": "located_in",
    "sourceEntityType": "InventoryUnit",
    "targetEntityType": "Market",
    "cardinality": "ManyToOne",
    "description": "Inventory unit is physically located in a market"
  },
  {
    "relationshipTypeName": "fulfilled_by",
    "sourceEntityType": "Campaign",
    "targetEntityType": "Vendor",
    "cardinality": "ManyToMany",
    "description": "Campaign production/installation fulfilled by vendor(s)"
  }
]
```

---

## Step 5: Contextualization JSON Definitions

### 5.1 Event Fact Contextualizations (Eventhouse)

```json
[
  {
    "contextualizationName": "CampaignOrderEvent",
    "sourceTable": "campaign_orders",
    "store": "Eventhouse",
    "timestampField": "date",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"},
      {"field": "ae_id", "entityType": "AccountExecutive"},
      {"field": "production_vendor_id", "entityType": "Vendor"}
    ]
  },
  {
    "contextualizationName": "OMSInteractionEvent",
    "sourceTable": "oms_interactions",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "ae_id", "entityType": "AccountExecutive"},
      {"field": "campaign_id", "entityType": "Campaign"}
    ]
  },
  {
    "contextualizationName": "ChartingEvent",
    "sourceTable": "charting_events",
    "store": "Eventhouse",
    "timestampField": "date",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"}
    ]
  },
  {
    "contextualizationName": "POPReportEvent",
    "sourceTable": "pop_reports",
    "store": "Eventhouse",
    "timestampField": "date",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"},
      {"field": "ae_id", "entityType": "AccountExecutive"}
    ]
  },
  {
    "contextualizationName": "ContractChangeEvent",
    "sourceTable": "contract_changes",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"},
      {"field": "ae_id", "entityType": "AccountExecutive"}
    ]
  },
  {
    "contextualizationName": "WorkOrderEvent",
    "sourceTable": "work_orders",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"},
      {"field": "unit_id", "entityType": "InventoryUnit"},
      {"field": "vendor_id", "entityType": "Vendor"}
    ]
  },
  {
    "contextualizationName": "ProofApprovalEvent",
    "sourceTable": "proof_approvals",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "ae_id", "entityType": "AccountExecutive"}
    ]
  },
  {
    "contextualizationName": "POPAlertEvent",
    "sourceTable": "pop_alerts",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"},
      {"field": "unit_id", "entityType": "InventoryUnit"}
    ]
  },
  {
    "contextualizationName": "InventoryTrackingEvent",
    "sourceTable": "inventory_tracking",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "unit_id", "entityType": "InventoryUnit"},
      {"field": "market_id", "entityType": "Market"}
    ]
  }
]
```

### 5.2 Real-Time Stream Contextualizations (Eventhouse)

```json
[
  {
    "contextualizationName": "CampaignPacingStream",
    "sourceTable": "campaign_pacing",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"}
    ]
  },
  {
    "contextualizationName": "CreativeStatusStream",
    "sourceTable": "creative_status",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"}
    ]
  },
  {
    "contextualizationName": "DigitalImpressionsStream",
    "sourceTable": "digital_impressions",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "campaign_id", "entityType": "Campaign"},
      {"field": "unit_id", "entityType": "InventoryUnit"}
    ]
  },
  {
    "contextualizationName": "InstallationEventStream",
    "sourceTable": "installation_events",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "unit_id", "entityType": "InventoryUnit"}
    ]
  },
  {
    "contextualizationName": "InventoryAvailabilityStream",
    "sourceTable": "inventory_availability",
    "store": "Eventhouse",
    "timestampField": "timestamp",
    "entityBindings": [
      {"field": "unit_id", "entityType": "InventoryUnit"},
      {"field": "market_id", "entityType": "Market"},
      {"field": "campaign_id", "entityType": "Campaign"}
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
ONTOLOGY_NAME  = "AdvertisingCampaignOpsOntology"
FABRIC_API     = f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}"

headers = {
    "Authorization": "Bearer <your-token>",
    "Content-Type": "application/json"
}

# --- 1. Create the Ontology ---
ontology_payload = {
    "displayName": ONTOLOGY_NAME,
    "description": "OOH Advertising Campaign Operations — AE documentation burden ontology"
}

resp = requests.post(f"{FABRIC_API}/ontologies", headers=headers, json=ontology_payload)
ontology_id = resp.json()["id"]
print(f"✓ Created ontology: {ontology_id}")

ONTOLOGY_API = f"{FABRIC_API}/ontologies/{ontology_id}"

# --- 2. Create Entity Types ---
entity_types = [
    {
        "entityTypeName": "AccountExecutive",
        "primaryKey": "ae_id",
        "properties": [
            {"name": "ae_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "role", "type": "String"}, {"name": "market_id", "type": "String"},
            {"name": "team", "type": "String"}, {"name": "quota_target", "type": "Float"},
            {"name": "hire_date", "type": "Date"}, {"name": "specialization", "type": "String"},
            {"name": "active_campaigns", "type": "Integer"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_account_executives"}
    },
    {
        "entityTypeName": "Campaign",
        "primaryKey": "campaign_id",
        "properties": [
            {"name": "campaign_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "advertiser_id", "type": "String"}, {"name": "market_id", "type": "String"},
            {"name": "start_date", "type": "Date"}, {"name": "end_date", "type": "Date"},
            {"name": "budget", "type": "Float"}, {"name": "media_type", "type": "String"},
            {"name": "contract_value", "type": "Float"}, {"name": "status", "type": "String"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_campaigns"}
    },
    {
        "entityTypeName": "InventoryUnit",
        "primaryKey": "unit_id",
        "properties": [
            {"name": "unit_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "type", "type": "String"}, {"name": "market_id", "type": "String"},
            {"name": "address", "type": "String"}, {"name": "lat", "type": "Float"},
            {"name": "lng", "type": "Float"}, {"name": "faces", "type": "Integer"},
            {"name": "illuminated", "type": "String"}, {"name": "digital", "type": "String"},
            {"name": "size", "type": "String"}, {"name": "monthly_rate", "type": "Float"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_inventory_units"}
    },
    {
        "entityTypeName": "Market",
        "primaryKey": "market_id",
        "properties": [
            {"name": "market_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "region", "type": "String"}, {"name": "dma_rank", "type": "Integer"},
            {"name": "population", "type": "Integer"}, {"name": "total_units", "type": "Integer"},
            {"name": "digital_pct", "type": "Float"}, {"name": "avg_occupancy_rate", "type": "Float"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_markets"}
    },
    {
        "entityTypeName": "Advertiser",
        "primaryKey": "advertiser_id",
        "properties": [
            {"name": "advertiser_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "industry", "type": "String"}, {"name": "annual_spend", "type": "Float"},
            {"name": "campaigns_ytd", "type": "Integer"}, {"name": "tenure_years", "type": "Integer"},
            {"name": "agency_name", "type": "String"}, {"name": "contact", "type": "String"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_advertisers"}
    },
    {
        "entityTypeName": "Vendor",
        "primaryKey": "vendor_id",
        "properties": [
            {"name": "vendor_id", "type": "String"}, {"name": "name", "type": "String"},
            {"name": "type", "type": "String"}, {"name": "region", "type": "String"},
            {"name": "specialization", "type": "String"}, {"name": "avg_turnaround_days", "type": "Float"},
            {"name": "quality_rating", "type": "Float"}
        ],
        "dataBinding": {"store": "Lakehouse", "tableName": "dim_vendors"}
    }
]

for et in entity_types:
    resp = requests.post(f"{ONTOLOGY_API}/entityTypes", headers=headers, json=et)
    print(f"  ✓ Entity type: {et['entityTypeName']}")

# --- 3. Create Relationship Types ---
relationships = [
    {"relationshipTypeName": "manages_campaign", "sourceEntityType": "AccountExecutive",
     "targetEntityType": "Campaign", "cardinality": "OneToMany"},
    {"relationshipTypeName": "belongs_to_market", "sourceEntityType": "Campaign",
     "targetEntityType": "Market", "cardinality": "ManyToOne"},
    {"relationshipTypeName": "placed_by", "sourceEntityType": "Campaign",
     "targetEntityType": "Advertiser", "cardinality": "ManyToOne"},
    {"relationshipTypeName": "located_in", "sourceEntityType": "InventoryUnit",
     "targetEntityType": "Market", "cardinality": "ManyToOne"},
    {"relationshipTypeName": "fulfilled_by", "sourceEntityType": "Campaign",
     "targetEntityType": "Vendor", "cardinality": "ManyToMany"}
]

for rel in relationships:
    resp = requests.post(f"{ONTOLOGY_API}/relationshipTypes", headers=headers, json=rel)
    print(f"  ✓ Relationship: {rel['relationshipTypeName']}")

# --- 4. Create Contextualizations ---
contextualizations = [
    # Event facts (Eventhouse)
    {"contextualizationName": "CampaignOrderEvent", "sourceTable": "campaign_orders",
     "store": "Eventhouse", "timestampField": "date",
     "entityBindings": [
         {"field": "campaign_id", "entityType": "Campaign"},
         {"field": "ae_id", "entityType": "AccountExecutive"},
         {"field": "production_vendor_id", "entityType": "Vendor"}]},
    {"contextualizationName": "OMSInteractionEvent", "sourceTable": "oms_interactions",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "ae_id", "entityType": "AccountExecutive"},
         {"field": "campaign_id", "entityType": "Campaign"}]},
    {"contextualizationName": "ChartingEvent", "sourceTable": "charting_events",
     "store": "Eventhouse", "timestampField": "date",
     "entityBindings": [{"field": "campaign_id", "entityType": "Campaign"}]},
    {"contextualizationName": "POPReportEvent", "sourceTable": "pop_reports",
     "store": "Eventhouse", "timestampField": "date",
     "entityBindings": [
         {"field": "campaign_id", "entityType": "Campaign"},
         {"field": "ae_id", "entityType": "AccountExecutive"}]},
    {"contextualizationName": "ContractChangeEvent", "sourceTable": "contract_changes",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "campaign_id", "entityType": "Campaign"},
         {"field": "ae_id", "entityType": "AccountExecutive"}]},
    {"contextualizationName": "WorkOrderEvent", "sourceTable": "work_orders",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "campaign_id", "entityType": "Campaign"},
         {"field": "unit_id", "entityType": "InventoryUnit"},
         {"field": "vendor_id", "entityType": "Vendor"}]},
    {"contextualizationName": "ProofApprovalEvent", "sourceTable": "proof_approvals",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [{"field": "ae_id", "entityType": "AccountExecutive"}]},
    {"contextualizationName": "POPAlertEvent", "sourceTable": "pop_alerts",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "campaign_id", "entityType": "Campaign"},
         {"field": "unit_id", "entityType": "InventoryUnit"}]},
    {"contextualizationName": "InventoryTrackingEvent", "sourceTable": "inventory_tracking",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "unit_id", "entityType": "InventoryUnit"},
         {"field": "market_id", "entityType": "Market"}]},
    # Real-time streams (Eventhouse)
    {"contextualizationName": "CampaignPacingStream", "sourceTable": "campaign_pacing",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [{"field": "campaign_id", "entityType": "Campaign"}]},
    {"contextualizationName": "CreativeStatusStream", "sourceTable": "creative_status",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [{"field": "campaign_id", "entityType": "Campaign"}]},
    {"contextualizationName": "DigitalImpressionsStream", "sourceTable": "digital_impressions",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "campaign_id", "entityType": "Campaign"},
         {"field": "unit_id", "entityType": "InventoryUnit"}]},
    {"contextualizationName": "InstallationEventStream", "sourceTable": "installation_events",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [{"field": "unit_id", "entityType": "InventoryUnit"}]},
    {"contextualizationName": "InventoryAvailabilityStream", "sourceTable": "inventory_availability",
     "store": "Eventhouse", "timestampField": "timestamp",
     "entityBindings": [
         {"field": "unit_id", "entityType": "InventoryUnit"},
         {"field": "market_id", "entityType": "Market"},
         {"field": "campaign_id", "entityType": "Campaign"}]}
]

for ctx in contextualizations:
    resp = requests.post(f"{ONTOLOGY_API}/contextualizations", headers=headers, json=ctx)
    print(f"  ✓ Contextualization: {ctx['contextualizationName']}")

print(f"\n✅ Ontology '{ONTOLOGY_NAME}' created with all components.")
```

---

## Step 7: Verify Ontology

After creation, verify all components are registered:

| Component            | Expected Count | Verification Query                                     |
|----------------------|----------------|--------------------------------------------------------|
| Entity Types         | 6              | AccountExecutive, Campaign, InventoryUnit, Market, Advertiser, Vendor |
| Relationship Types   | 5              | manages_campaign, belongs_to_market, placed_by, located_in, fulfilled_by |
| Contextualizations   | 14             | 9 event facts + 5 real-time streams                   |

```python
# Verify entity types
resp = requests.get(f"{ONTOLOGY_API}/entityTypes", headers=headers)
entity_types_list = resp.json()["value"]
print(f"Entity Types: {len(entity_types_list)}")
for et in entity_types_list:
    print(f"  - {et['entityTypeName']} ({len(et['properties'])} properties)")

# Verify relationship types
resp = requests.get(f"{ONTOLOGY_API}/relationshipTypes", headers=headers)
rels_list = resp.json()["value"]
print(f"Relationship Types: {len(rels_list)}")
for r in rels_list:
    print(f"  - {r['relationshipTypeName']}: {r['sourceEntityType']} → {r['targetEntityType']}")

# Verify contextualizations
resp = requests.get(f"{ONTOLOGY_API}/contextualizations", headers=headers)
ctx_list = resp.json()["value"]
print(f"Contextualizations: {len(ctx_list)}")
for c in ctx_list:
    bindings = ", ".join([b["entityType"] for b in c.get("entityBindings", [])])
    print(f"  - {c['contextualizationName']} → [{bindings}]")
```

**Expected Output:**
```
Entity Types: 6
  - AccountExecutive (9 properties)
  - Campaign (10 properties)
  - InventoryUnit (12 properties)
  - Market (8 properties)
  - Advertiser (8 properties)
  - Vendor (7 properties)
Relationship Types: 5
  - manages_campaign: AccountExecutive → Campaign
  - belongs_to_market: Campaign → Market
  - placed_by: Campaign → Advertiser
  - located_in: InventoryUnit → Market
  - fulfilled_by: Campaign → Vendor
Contextualizations: 14
  - CampaignOrderEvent → [Campaign, AccountExecutive, Vendor]
  - OMSInteractionEvent → [AccountExecutive, Campaign]
  - ChartingEvent → [Campaign]
  - POPReportEvent → [Campaign, AccountExecutive]
  - ContractChangeEvent → [Campaign, AccountExecutive]
  - WorkOrderEvent → [Campaign, InventoryUnit, Vendor]
  - ProofApprovalEvent → [AccountExecutive]
  - POPAlertEvent → [Campaign, InventoryUnit]
  - InventoryTrackingEvent → [InventoryUnit, Market]
  - CampaignPacingStream → [Campaign]
  - CreativeStatusStream → [Campaign]
  - DigitalImpressionsStream → [Campaign, InventoryUnit]
  - InstallationEventStream → [InventoryUnit]
  - InventoryAvailabilityStream → [InventoryUnit, Market, Campaign]
```

---

## Data Binding Summary

| Binding Target          | Tables | Store      | Purpose                                |
|-------------------------|--------|------------|----------------------------------------|
| Entity dimensions       | 6      | Lakehouse  | AE, Campaign, Unit, Market, Advertiser, Vendor |
| Batch facts             | 3      | Lakehouse  | Wellness, quality, satisfaction surveys |
| Event facts             | 9      | Eventhouse | Campaign ops documentation events      |
| Real-time streams       | 5      | Eventhouse | Pacing, creative, impressions, installs, availability |
| **Total tables**        | **23** |            |                                        |

---

## Built-In Data Patterns

The ontology is designed to surface the following advertising-specific documentation burden patterns:

### Pattern 1: AE Overload Detection
**Signal:** AEs with `active_campaigns > 8` AND total `doc_time_min` exceeding 60 min/day across campaign_orders + pop_reports + contract_changes.
**Query Approach:** Aggregate `doc_time_min` from CTX-001, CTX-004, CTX-005 grouped by `ae_id`, join with `dim_account_executives.active_campaigns`. Flag AEs where documentation time exceeds 40% of their total work hours.
**Business Impact:** Identifies AEs spending more time on paperwork than selling, enabling workload redistribution.

### Pattern 2: POP Documentation Cascade
**Signal:** A single contract change (CTX-005) triggers recharting (CTX-003 with `ccn_flag=Yes`) which triggers re-verification (CTX-004) which triggers new POP alerts (CTX-008).
**Query Approach:** Trace `campaign_id` across contract_changes → charting_events (ccn_flag=Yes) → pop_reports → pop_alerts within a 72-hour window. Sum `doc_time_min` across all stages.
**Business Impact:** Quantifies the ripple effect of mid-campaign changes — a single CCN can generate 3–5× its own documentation time in downstream rework.

### Pattern 3: Proof Cycle Delays
**Signal:** Proof approvals (CTX-007) with `cycle_time_hours > 48` AND `revision_count >= 3` correlating with creative status (CTX-011) blockers of type `ClientFeedback`.
**Query Approach:** Join proof_approvals with creative_status on `order_id`, filter for extended cycles. Aggregate by `ae_id` to find AEs most impacted by proof delays.
**Business Impact:** Proof revision loops consume AE time on follow-ups, emails, and re-submissions — often the single largest hidden documentation cost.

### Pattern 4: Contract Change Documentation Burden
**Signal:** Campaigns with `change_type=UnitSwap` in contract_changes (CTX-005) generating disproportionate `doc_time_min` relative to `units_affected`.
**Query Approach:** Calculate doc_time_per_unit = `doc_time_min / units_affected` from contract_changes. Identify campaigns where unit-swap changes take 3× longer per unit than date changes.
**Business Impact:** Unit swaps require recharting, new work orders, updated POP, and new proofs — the most documentation-intensive change type.

### Pattern 5: Digital vs. Traditional Campaign Documentation Time
**Signal:** Compare total `doc_time_min` across all contextualizations for campaigns where `dim_campaigns.media_type = 'Digital'` vs. `'Bulletin'` or `'Poster'`.
**Query Approach:** Join campaign_orders, pop_reports, charting_events, and work_orders with dim_campaigns on `campaign_id`. Group by `media_type`, normalize by `units_booked`.
**Business Impact:** Digital campaigns typically require less installation documentation but more pacing/impression reporting. Quantifies the documentation trade-off as operators shift to digital inventory.
