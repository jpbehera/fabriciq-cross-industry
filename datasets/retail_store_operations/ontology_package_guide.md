# Retail Store Operations — Ontology Package Guide

This guide walks through building the **RetailStoreOpsOntology** package and deploying it
into Microsoft Fabric using the FabricIQ accelerator. The ontology models the documentation
and administrative burden on retail store managers — compliance reports, inventory audits,
scheduling overhead, incident documentation — and correlates that burden with store
performance, customer satisfaction, and manager wellness.

---

## Prerequisites

| Component        | Name                 | Notes                                                       |
|------------------|----------------------|-------------------------------------------------------------|
| **Lakehouse**    | RetailLakehouse      | Holds dimension tables and batch fact tables (Parquet)       |
| **Eventhouse**   | RetailEventhouse     | Holds event-level fact tables for KQL analytics              |
| **KQL Database** | RetailKQLDB          | Receives real-time stream ingestion via Eventstream          |
| **Workspace**    | _(your workspace)_   | Must have Contributor or higher role                         |
| **Python**       | 3.10+                | `semantic-link`, `azure-identity`, `requests` packages       |

---

## Step 1 — Prepare Lakehouse

Upload dimension CSV files and batch fact CSVs to the Lakehouse under the base path:

```
Files/retail_store_operations/data/
```

### Dimension Tables

| File                         | Target Table             | Row Key          |
|------------------------------|--------------------------|------------------|
| `dim_store_managers.csv`     | `dim_store_managers`     | `manager_id`     |
| `dim_stores.csv`             | `dim_stores`             | `store_id`       |
| `dim_districts.csv`          | `dim_districts`          | `district_id`    |
| `dim_report_types.csv`       | `dim_report_types`       | `report_type_id` |
| `dim_product_categories.csv` | `dim_product_categories` | `category_id`    |
| `dim_vendor_partners.csv`    | `dim_vendor_partners`    | `vendor_id`      |

### Batch Fact Tables

| File                           | Target Table                 | Row Key       |
|--------------------------------|------------------------------|---------------|
| `fact_manager_wellness.csv`    | `fact_manager_wellness`      | `survey_id`   |
| `fact_audit_quality.csv`       | `fact_audit_quality`         | `quality_id`  |
| `fact_customer_satisfaction.csv`| `fact_customer_satisfaction` | `survey_id`   |

### Load Notebook Snippet

```python
import pandas as pd
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

base_path = "Files/retail_store_operations/data"
dim_tables = [
    "dim_store_managers", "dim_stores", "dim_districts",
    "dim_report_types", "dim_product_categories", "dim_vendor_partners",
]
batch_facts = [
    "fact_manager_wellness", "fact_audit_quality", "fact_customer_satisfaction",
]

for table_name in dim_tables + batch_facts:
    df = spark.read.option("header", True).csv(f"{base_path}/{table_name}.csv")
    df.write.mode("overwrite").format("delta").saveAsTable(table_name)
    print(f"  ✓ Loaded {table_name} — {df.count()} rows")
```

---

## Step 2 — Prepare Eventhouse

Ingest event-level fact CSVs and configure Eventstream for the five real-time streams.

### Event Fact Tables → KQL DB

| File                              | KQL Table                      | Row Key        |
|-----------------------------------|--------------------------------|----------------|
| `fact_compliance_doc_events.csv`  | `fact_compliance_doc_events`   | `event_id`     |
| `fact_retail_system_clicks.csv`   | `fact_retail_system_clicks`    | `click_id`     |
| `fact_inventory_audits.csv`       | `fact_inventory_audits`        | `audit_id`     |
| `fact_inventory_scans.csv`        | `fact_inventory_scans`         | `scan_id`      |
| `fact_scheduling_events.csv`      | `fact_scheduling_events`       | `event_id`     |
| `fact_shift_handoffs.csv`         | `fact_shift_handoffs`          | `handoff_id`   |
| `fact_store_incidents.csv`        | `fact_store_incidents`         | `incident_id`  |
| `fact_associate_presence.csv`     | `fact_associate_presence`      | `presence_id`  |
| `fact_pos_transactions.csv`       | `fact_pos_transactions`        | `txn_id`       |

### Real-Time Streams → Eventstream → KQL DB

| Stream Source                  | KQL Table                    | Key Field      |
|--------------------------------|------------------------------|----------------|
| `stream_pos_transactions`      | `stream_pos_transactions`    | `txn_id`       |
| `stream_foot_traffic`          | `stream_foot_traffic`        | `sensor_id`    |
| `stream_inventory_scans`       | `stream_inventory_scans`     | `scan_id`      |
| `stream_store_incidents`       | `stream_store_incidents`     | `incident_id`  |
| `stream_associate_location`    | `stream_associate_location`  | `ping_id`      |

---

## Step 3 — Entity Type Definitions

Define all six entity types. Each maps to a Lakehouse dimension table.

### ENT-001 — StoreManager

```json
{
  "id": "StoreManager",
  "display_name": "Store Manager",
  "description": "Retail store manager responsible for daily operations, compliance reporting, and floor management.",
  "source": {
    "type": "lakehouse",
    "lakehouse": "RetailLakehouse",
    "table": "dim_store_managers"
  },
  "key_column": "manager_id",
  "properties": [
    { "name": "manager_id",             "type": "string",  "is_key": true  },
    { "name": "name",                   "type": "string",  "is_key": false },
    { "name": "store_id",               "type": "string",  "is_key": false },
    { "name": "region",                 "type": "string",  "is_key": false },
    { "name": "hire_date",              "type": "date",    "is_key": false },
    { "name": "certifications",         "type": "string",  "is_key": false },
    { "name": "avg_weekly_floor_hours", "type": "float",   "is_key": false }
  ]
}
```

### ENT-002 — Store

```json
{
  "id": "Store",
  "display_name": "Store",
  "description": "Physical retail store location with format, size, and staffing attributes.",
  "source": {
    "type": "lakehouse",
    "lakehouse": "RetailLakehouse",
    "table": "dim_stores"
  },
  "key_column": "store_id",
  "properties": [
    { "name": "store_id",     "type": "string",  "is_key": true  },
    { "name": "name",         "type": "string",  "is_key": false },
    { "name": "district_id",  "type": "string",  "is_key": false },
    { "name": "region",       "type": "string",  "is_key": false },
    { "name": "format",       "type": "string",  "is_key": false },
    { "name": "sq_footage",   "type": "int",     "is_key": false },
    { "name": "headcount",    "type": "int",     "is_key": false },
    { "name": "revenue_tier", "type": "string",  "is_key": false }
  ]
}
```

### ENT-003 — District

```json
{
  "id": "District",
  "display_name": "District",
  "description": "Geographic grouping of stores managed by a district manager.",
  "source": {
    "type": "lakehouse",
    "lakehouse": "RetailLakehouse",
    "table": "dim_districts"
  },
  "key_column": "district_id",
  "properties": [
    { "name": "district_id",        "type": "string",  "is_key": true  },
    { "name": "name",               "type": "string",  "is_key": false },
    { "name": "region",             "type": "string",  "is_key": false },
    { "name": "store_count",        "type": "int",     "is_key": false },
    { "name": "district_manager",   "type": "string",  "is_key": false },
    { "name": "performance_rating", "type": "string",  "is_key": false }
  ]
}
```

### ENT-004 — ReportType

```json
{
  "id": "ReportType",
  "display_name": "Report Type",
  "description": "A compliance, safety, or operational report that managers are required to file.",
  "source": {
    "type": "lakehouse",
    "lakehouse": "RetailLakehouse",
    "table": "dim_report_types"
  },
  "key_column": "report_type_id",
  "properties": [
    { "name": "report_type_id",           "type": "string",  "is_key": true  },
    { "name": "name",                     "type": "string",  "is_key": false },
    { "name": "category",                 "type": "string",  "is_key": false },
    { "name": "frequency",                "type": "string",  "is_key": false },
    { "name": "avg_completion_time_min",  "type": "float",   "is_key": false },
    { "name": "regulatory_required",      "type": "boolean", "is_key": false }
  ]
}
```

### ENT-005 — ProductCategory

```json
{
  "id": "ProductCategory",
  "display_name": "Product Category",
  "description": "Product category with planogram reset schedule and shrinkage risk classification.",
  "source": {
    "type": "lakehouse",
    "lakehouse": "RetailLakehouse",
    "table": "dim_product_categories"
  },
  "key_column": "category_id",
  "properties": [
    { "name": "category_id",                "type": "string",  "is_key": true  },
    { "name": "name",                       "type": "string",  "is_key": false },
    { "name": "department",                 "type": "string",  "is_key": false },
    { "name": "planogram_reset_frequency",  "type": "string",  "is_key": false },
    { "name": "shrinkage_risk_tier",        "type": "string",  "is_key": false }
  ]
}
```

### ENT-006 — VendorPartner

```json
{
  "id": "VendorPartner",
  "display_name": "Vendor Partner",
  "description": "External vendor or supplier partner that delivers products and requires receiving documentation.",
  "source": {
    "type": "lakehouse",
    "lakehouse": "RetailLakehouse",
    "table": "dim_vendor_partners"
  },
  "key_column": "vendor_id",
  "properties": [
    { "name": "vendor_id",                   "type": "string",  "is_key": true  },
    { "name": "name",                        "type": "string",  "is_key": false },
    { "name": "category",                    "type": "string",  "is_key": false },
    { "name": "delivery_frequency",          "type": "string",  "is_key": false },
    { "name": "documentation_requirements",  "type": "string",  "is_key": false }
  ]
}
```

---

## Step 4 — Relationship Type Definitions

```json
[
  {
    "id": "manages",
    "display_name": "Manages",
    "description": "A store manager is assigned to manage a store.",
    "from_entity": "StoreManager",
    "to_entity": "Store",
    "from_key": "store_id",
    "to_key": "store_id"
  },
  {
    "id": "belongs_to_district",
    "display_name": "Belongs to District",
    "description": "A store belongs to a geographic district.",
    "from_entity": "Store",
    "to_entity": "District",
    "from_key": "district_id",
    "to_key": "district_id"
  },
  {
    "id": "stocks",
    "display_name": "Stocks",
    "description": "A store stocks products from a product category.",
    "from_entity": "Store",
    "to_entity": "ProductCategory",
    "from_key": "store_id",
    "to_key": "category_id",
    "bridge_table": "fact_inventory_audits"
  },
  {
    "id": "partners_with",
    "display_name": "Partners With",
    "description": "A store receives deliveries from a vendor partner.",
    "from_entity": "Store",
    "to_entity": "VendorPartner",
    "from_key": "store_id",
    "to_key": "vendor_id"
  },
  {
    "id": "requires_report",
    "display_name": "Requires Report",
    "description": "A store must file specific report types per compliance schedule.",
    "from_entity": "Store",
    "to_entity": "ReportType",
    "from_key": "store_id",
    "to_key": "report_type_id",
    "bridge_table": "fact_compliance_doc_events"
  }
]
```

---

## Step 5 — Contextualization Definitions

### Event Contextualizations (Eventhouse)

```json
[
  {
    "id": "ctx_compliance_doc_events",
    "display_name": "Compliance Documentation Events",
    "description": "Compliance report filing events — duration, status, overdue flag.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_compliance_doc_events" },
    "entity_bindings": [
      { "entity": "StoreManager", "column": "manager_id" },
      { "entity": "Store",        "column": "store_id"   },
      { "entity": "ReportType",   "column": "report_type_id" }
    ]
  },
  {
    "id": "ctx_retail_system_clicks",
    "display_name": "Retail System Clicks",
    "description": "Clickstream events in retail admin systems (POS, WFM, inventory).",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_retail_system_clicks" },
    "entity_bindings": [
      { "entity": "StoreManager", "column": "manager_id" }
    ]
  },
  {
    "id": "ctx_inventory_audits",
    "display_name": "Inventory Audits",
    "description": "Inventory count/audit events with variance and documentation time.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_inventory_audits" },
    "entity_bindings": [
      { "entity": "Store",           "column": "store_id"    },
      { "entity": "StoreManager",    "column": "manager_id"  },
      { "entity": "ProductCategory", "column": "category_id" }
    ]
  },
  {
    "id": "ctx_inventory_scans",
    "display_name": "Inventory Scans",
    "description": "Individual product scan events during inventory counts.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_inventory_scans" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  },
  {
    "id": "ctx_scheduling_events",
    "display_name": "Scheduling Events",
    "description": "Scheduling tasks — shift planning, coverage gap resolution, overtime.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_scheduling_events" },
    "entity_bindings": [
      { "entity": "StoreManager", "column": "manager_id" },
      { "entity": "Store",        "column": "store_id"   }
    ]
  },
  {
    "id": "ctx_shift_handoffs",
    "display_name": "Shift Handoffs",
    "description": "End-of-shift handoff documentation between managers.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_shift_handoffs" },
    "entity_bindings": [
      { "entity": "Store",        "column": "store_id"       },
      { "entity": "StoreManager", "column": "from_manager_id" },
      { "entity": "StoreManager", "column": "to_manager_id"   }
    ]
  },
  {
    "id": "ctx_store_incidents",
    "display_name": "Store Incidents",
    "description": "Safety and security incident reports with documentation time.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_store_incidents" },
    "entity_bindings": [
      { "entity": "Store",        "column": "store_id"   },
      { "entity": "StoreManager", "column": "manager_id" }
    ]
  },
  {
    "id": "ctx_associate_presence",
    "display_name": "Associate Presence",
    "description": "Zone-level associate presence and dwell tracking.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_associate_presence" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  },
  {
    "id": "ctx_pos_transactions",
    "display_name": "POS Transactions",
    "description": "Point-of-sale transaction events.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "fact_pos_transactions" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  }
]
```

### Batch Contextualizations (Lakehouse)

```json
[
  {
    "id": "ctx_manager_wellness",
    "display_name": "Manager Wellness Surveys",
    "description": "Monthly manager wellness — admin burden score, overtime, floor time %.",
    "source": { "type": "lakehouse", "lakehouse": "RetailLakehouse", "table": "fact_manager_wellness" },
    "entity_bindings": [
      { "entity": "StoreManager", "column": "manager_id" },
      { "entity": "Store",        "column": "store_id"   }
    ]
  },
  {
    "id": "ctx_audit_quality",
    "display_name": "Audit Quality Scores",
    "description": "Audit quality — planogram compliance, inventory accuracy, safety checklist.",
    "source": { "type": "lakehouse", "lakehouse": "RetailLakehouse", "table": "fact_audit_quality" },
    "entity_bindings": [
      { "entity": "Store",           "column": "store_id"    },
      { "entity": "ProductCategory", "column": "category_id" }
    ]
  },
  {
    "id": "ctx_customer_satisfaction",
    "display_name": "Customer Satisfaction",
    "description": "Customer satisfaction surveys — NPS, mystery shopper, wait time.",
    "source": { "type": "lakehouse", "lakehouse": "RetailLakehouse", "table": "fact_customer_satisfaction" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  }
]
```

### Stream Contextualizations (Eventhouse — Real-Time)

```json
[
  {
    "id": "ctx_stream_pos_transactions",
    "display_name": "POS Transactions (Stream)",
    "description": "Real-time point-of-sale transaction feed.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "stream_pos_transactions" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  },
  {
    "id": "ctx_stream_foot_traffic",
    "display_name": "Foot Traffic (Stream)",
    "description": "Real-time foot traffic sensor data by store zone.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "stream_foot_traffic" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  },
  {
    "id": "ctx_stream_inventory_scans",
    "display_name": "Inventory Scans (Stream)",
    "description": "Real-time inventory scan events with discrepancy detection.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "stream_inventory_scans" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  },
  {
    "id": "ctx_stream_store_incidents",
    "display_name": "Store Incidents (Stream)",
    "description": "Real-time incident reporting stream.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "stream_store_incidents" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  },
  {
    "id": "ctx_stream_associate_location",
    "display_name": "Associate Location (Stream)",
    "description": "Real-time associate location pings by zone.",
    "source": { "type": "eventhouse", "database": "RetailKQLDB", "table": "stream_associate_location" },
    "entity_bindings": [
      { "entity": "Store", "column": "store_id" }
    ]
  }
]
```

---

## Step 6 — Create Ontology

```python
import json
import requests
from azure.identity import DefaultAzureCredential

# ── Configuration ─────────────────────────────────────────────
WORKSPACE_ID   = "<your-workspace-id>"
ONTOLOGY_NAME  = "RetailStoreOpsOntology"
ONTOLOGY_DESC  = (
    "Models store manager documentation burden — compliance reports, "
    "inventory audits, scheduling, incident documentation — and correlates "
    "administrative overhead with store performance and customer satisfaction."
)

# ── Auth ──────────────────────────────────────────────────────
credential = DefaultAzureCredential()
token = credential.get_token("https://api.fabric.microsoft.com/.default").token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type":  "application/json",
}
BASE = f"https://api.fabric.microsoft.com/v1/workspaces/{WORKSPACE_ID}"

# ── 1. Create Ontology ───────────────────────────────────────
ontology_payload = {
    "displayName": ONTOLOGY_NAME,
    "description": ONTOLOGY_DESC,
}
resp = requests.post(f"{BASE}/ontologies", headers=headers, json=ontology_payload)
resp.raise_for_status()
ontology_id = resp.json()["id"]
print(f"Created ontology: {ontology_id}")

# ── 2. Entity Types ──────────────────────────────────────────
entity_types = [
    # ... (load from Step 3 JSON definitions above)
]
for et in entity_types:
    resp = requests.post(
        f"{BASE}/ontologies/{ontology_id}/entityTypes",
        headers=headers, json=et,
    )
    resp.raise_for_status()
    print(f"  ✓ Entity type: {et['id']}")

# ── 3. Relationship Types ────────────────────────────────────
relationship_types = [
    # ... (load from Step 4 JSON definitions above)
]
for rt in relationship_types:
    resp = requests.post(
        f"{BASE}/ontologies/{ontology_id}/relationshipTypes",
        headers=headers, json=rt,
    )
    resp.raise_for_status()
    print(f"  ✓ Relationship: {rt['id']}")

# ── 4. Contextualizations ────────────────────────────────────
contextualizations = [
    # ... (load from Step 5 JSON definitions — event + batch + stream)
]
for ctx in contextualizations:
    resp = requests.post(
        f"{BASE}/ontologies/{ontology_id}/contextualizations",
        headers=headers, json=ctx,
    )
    resp.raise_for_status()
    print(f"  ✓ Contextualization: {ctx['id']}")

print(f"\n✅ RetailStoreOpsOntology deployed — {ontology_id}")
```

---

## Step 7 — Verify

After deployment, confirm the following counts:

| Component            | Expected Count | Verify Command                                              |
|----------------------|----------------|-------------------------------------------------------------|
| Entity Types         | 6              | `GET /ontologies/{id}/entityTypes`                           |
| Relationship Types   | 5              | `GET /ontologies/{id}/relationshipTypes`                     |
| Contextualizations   | 17             | `GET /ontologies/{id}/contextualizations`                    |

**Entity types:** StoreManager, Store, District, ReportType, ProductCategory, VendorPartner

**Relationships:** manages, belongs_to_district, stocks, partners_with, requires_report

**Contextualizations:** 9 event + 3 batch + 5 stream = 17 total

---

## Data Binding Summary

| Entity Type       | Dim Table                | Event / Stream Bindings                                                                |
|-------------------|--------------------------|----------------------------------------------------------------------------------------|
| StoreManager      | `dim_store_managers`     | compliance_doc_events, system_clicks, inventory_audits, scheduling_events, shift_handoffs, store_incidents, manager_wellness |
| Store             | `dim_stores`             | All 17 contextualizations bind via `store_id`                                          |
| District          | `dim_districts`          | Reachable via Store → belongs_to_district                                              |
| ReportType        | `dim_report_types`       | compliance_doc_events                                                                  |
| ProductCategory   | `dim_product_categories` | inventory_audits, audit_quality                                                        |
| VendorPartner     | `dim_vendor_partners`    | Reachable via Store → partners_with                                                    |

---

## Built-In Data Patterns

The ontology enables the data agent to detect and surface these retail-specific patterns
without manual query authoring:

### Pattern 1 — Manager Floor-Time Erosion

**Signal:** `fact_manager_wellness.floor_time_pct` declining over consecutive months while
`fact_compliance_doc_events` volume or `duration_minutes` increases.

**Insight:** Identifies managers whose customer-facing floor time is being consumed by
growing compliance documentation demands. Cross-references with `avg_weekly_floor_hours`
from the dimension to measure erosion against baseline.

**Action:** Flag managers below a configurable floor-time threshold; recommend report
consolidation or delegation strategies.

### Pattern 2 — Compliance Documentation Cascade

**Signal:** `fact_compliance_doc_events.overdue_flag = true` clustered around specific
`report_type_id` values, correlated with high `fact_scheduling_events.duration_minutes`.

**Insight:** Overdue compliance reports often cascade — a missed daily checklist forces
a larger weekly reconciliation, which delays scheduling tasks. The ontology traces the
chain from overdue doc → scheduling delay → coverage gap → overtime approval.

**Action:** Identify cascade-prone report types; recommend pre-populated templates or
auto-filling from POS/inventory system data.

### Pattern 3 — Inventory Audit Shrinkage Correlation

**Signal:** `fact_inventory_audits.variance_pct` exceeding threshold for specific
`category_id` values, combined with low `fact_audit_quality.planogram_compliance_pct`.

**Insight:** Product categories with high shrinkage risk (`dim_product_categories.shrinkage_risk_tier`)
that also have low planogram compliance tend to show higher inventory variance. The
ontology links audit documentation effort (doc_time_min, scan_count) to actual accuracy
outcomes, revealing whether more thorough audits reduce shrinkage.

**Action:** Prioritise audit effort toward high-risk categories; auto-schedule more
frequent audits for categories below accuracy thresholds.

### Pattern 4 — Seasonal Scheduling Burden Spikes

**Signal:** `fact_scheduling_events.duration_minutes` and `overtime_approved` counts
spiking during known seasonal periods (back-to-school, holiday, end-of-quarter).

**Insight:** Scheduling documentation burden is not uniform — it spikes predictably during
high-traffic periods when managers are also most needed on the floor. The ontology
correlates scheduling burden with `stream_foot_traffic` volume and
`fact_customer_satisfaction.wait_time_rating` to quantify the cost of admin overhead
during peak periods.

**Action:** Pre-build scheduling templates for known seasonal patterns; auto-approve
standard overtime during peak weeks to reduce approval documentation loops.

### Pattern 5 — High-Traffic Store Incident Rates

**Signal:** `stream_store_incidents` per-hour rate correlated with `stream_foot_traffic`
enter_count, segmented by `dim_stores.format` and `sq_footage`.

**Insight:** Stores with higher foot traffic per square foot generate more incidents
(spills, customer altercations, equipment issues), each requiring manager documentation
time. The ontology measures `documentation_time_min` per incident against real-time
traffic volume to identify stores where incident documentation load is disproportionate.

**Action:** Deploy self-service incident kiosks in high-traffic stores; route low-severity
incidents to associate-level documentation with manager sign-off.
