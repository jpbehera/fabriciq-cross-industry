# Construction Site Operations — Ontology Package Guide

## Overview

This guide walks through building the **ConstructionSiteOpsOntology** in Microsoft Fabric IQ. It covers loading dimension and fact data into Lakehouse and Eventhouse, defining entity types, relationship types, and contextualizations, and creating the ontology programmatically using the `fabricontology` package.

**Industry Focus:** Construction documentation burden — tracking how much time field supervisors spend on daily logs, RFIs, safety inspections, change orders, and phase handoffs versus actual field supervision time.

---

## Prerequisites

| Component     | Name                        | Purpose                                           |
|---------------|-----------------------------|---------------------------------------------------|
| Lakehouse     | `ConstructionLakehouse`     | Stores dimension tables and batch fact tables      |
| Eventhouse    | `ConstructionEventhouse`    | Stores event fact tables and real-time streams     |
| KQL Database  | `ConstructionKQLDB`         | KQL database within the Eventhouse                 |
| Data Files    | `datasets/construction_site_operations/data/` | Source CSV files             |
| Python Package| `fabricontology`            | Fabric IQ ontology creation SDK                    |

### Fabric Workspace Setup Checklist
- [ ] Fabric workspace with Fabric IQ capacity enabled
- [ ] Lakehouse `ConstructionLakehouse` created
- [ ] Eventhouse `ConstructionEventhouse` created with KQL DB `ConstructionKQLDB`
- [ ] CSV files uploaded to Lakehouse Files area under `Files/construction_site_operations/data/`

---

## Step 1: Prepare Lakehouse (Dimension + Batch Fact Tables)

Load all dimension tables and batch fact tables into the Lakehouse as Delta tables using PySpark.

### 1.1 Load Dimension Tables

```python
# Run in a Fabric Notebook attached to ConstructionLakehouse
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

base_path = "Files/construction_site_operations/data"

# --- Dimension Tables ---
dim_tables = [
    ("dim_supervisors",      f"{base_path}/dim_supervisors.csv"),
    ("dim_projects",         f"{base_path}/dim_projects.csv"),
    ("dim_project_sites",    f"{base_path}/dim_project_sites.csv"),
    ("dim_inspection_types", f"{base_path}/dim_inspection_types.csv"),
    ("dim_subcontractors",   f"{base_path}/dim_subcontractors.csv"),
    ("dim_trade_phases",     f"{base_path}/dim_trade_phases.csv"),
]

for table_name, csv_path in dim_tables:
    df = spark.read.option("header", True).option("inferSchema", True).csv(csv_path)
    df.write.format("delta").mode("overwrite").saveAsTable(table_name)
    print(f"✓ Loaded {table_name}: {df.count()} rows, {len(df.columns)} columns")
```

### 1.2 Load Batch Fact Tables

```python
# --- Batch Fact Tables (Lakehouse) ---
batch_fact_tables = [
    ("fact_supervisor_wellness",        f"{base_path}/fact_supervisor_wellness.csv"),
    ("fact_inspection_quality",         f"{base_path}/fact_inspection_quality.csv"),
    ("fact_subcontractor_satisfaction", f"{base_path}/fact_subcontractor_satisfaction.csv"),
    ("fact_project_performance",        f"{base_path}/fact_project_performance.csv"),
]

for table_name, csv_path in batch_fact_tables:
    df = spark.read.option("header", True).option("inferSchema", True).csv(csv_path)
    df.write.format("delta").mode("overwrite").saveAsTable(table_name)
    print(f"✓ Loaded {table_name}: {df.count()} rows, {len(df.columns)} columns")
```

### 1.3 Verify Lakehouse Tables

```python
# Verify all tables
tables = spark.sql("SHOW TABLES").collect()
print(f"\nTotal tables in Lakehouse: {len(tables)}")
for t in sorted(tables, key=lambda x: x.tableName):
    count = spark.sql(f"SELECT COUNT(*) as cnt FROM {t.tableName}").collect()[0].cnt
    print(f"  {t.tableName}: {count} rows")
```

**Expected Output:** 10 tables (6 dim + 4 batch fact)

---

## Step 2: Prepare Eventhouse (Event Fact + Stream Tables)

Ingest event fact tables and streaming data into the Eventhouse KQL database.

### 2.1 Create KQL Tables

Run these commands in the KQL Database `ConstructionKQLDB`:

```kql
// === Event Fact Tables ===

.create table daily_logs (
    log_id: string,
    supervisor_id: string,
    project_id: string,
    date: datetime,
    weather: string,
    crew_count: int,
    work_summary: string,
    doc_time_min: int,
    photos_attached: int,
    safety_incidents: int
)

.create table pm_interactions (
    interaction_id: string,
    supervisor_id: string,
    timestamp: datetime,
    system: string,
    module: string,
    action: string,
    duration_ms: int,
    document_type: string
)

.create table rfi_events (
    rfi_id: string,
    supervisor_id: string,
    project_id: string,
    timestamp: datetime,
    question: string,
    status: string,
    response_time_hours: real,
    doc_time_min: int,
    trade: string
)

.create table safety_inspections (
    inspection_id: string,
    supervisor_id: string,
    site_id: string,
    date: datetime,
    type: string,
    findings_count: int,
    critical_count: int,
    doc_time_min: int,
    corrective_actions: int
)

.create table change_orders (
    change_order_id: string,
    project_id: string,
    supervisor_id: string,
    timestamp: datetime,
    description: string,
    cost_impact: real,
    schedule_impact_days: int,
    doc_time_min: int
)

.create table phase_handoffs (
    handoff_id: string,
    project_id: string,
    from_trade: string,
    to_trade: string,
    timestamp: datetime,
    punch_list_items: int,
    doc_time_min: int,
    approved: string
)

.create table safety_alerts (
    alert_id: string,
    site_id: string,
    supervisor_id: string,
    timestamp: datetime,
    alert_type: string,
    severity: string,
    description: string,
    immediate_action: string,
    osha_reportable: string
)

.create table site_location (
    ping_id: string,
    supervisor_id: string,
    timestamp: datetime,
    site_id: string,
    zone: string,
    floor: int,
    activity_type: string,
    dwell_minutes: real
)

// === Stream Tables ===

.create table stream_safety_events (
    event_id: string,
    site_id: string,
    timestamp: datetime,
    event_type: string,
    zone: string,
    severity: string,
    worker_count: int
)

.create table stream_equipment_telemetry (
    telemetry_id: string,
    equipment_id: string,
    site_id: string,
    timestamp: datetime,
    utilization_pct: real,
    fuel_level: real,
    maintenance_flag: string
)

.create table stream_rfi_status (
    rfi_id: string,
    project_id: string,
    timestamp: datetime,
    status: string,
    assigned_to: string,
    days_open: int,
    priority: string
)

.create table stream_weather_conditions (
    reading_id: string,
    site_id: string,
    timestamp: datetime,
    temp_f: real,
    wind_mph: real,
    precip_in: real,
    lightning_flag: string
)

.create table stream_daily_log_activity (
    log_id: string,
    supervisor_id: string,
    timestamp: datetime,
    project_id: string,
    section: string,
    entry_type: string,
    photo_count: int
)
```

### 2.2 Ingest CSV Data into KQL Tables

```kql
// --- Event Fact Ingestion ---

.ingest into table daily_logs (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/fact_daily_logs.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table pm_interactions (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/fact_pm_interactions.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table rfi_events (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/fact_rfi_events.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table safety_inspections (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/fact_safety_inspections.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table change_orders (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/fact_change_orders.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table phase_handoffs (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/fact_phase_handoffs.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table safety_alerts (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/fact_safety_alerts.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table site_location (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/fact_site_location.csv'
) with (format='csv', ignoreFirstRecord=true)

// --- Stream Table Ingestion ---

.ingest into table stream_safety_events (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/stream_safety_events.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table stream_equipment_telemetry (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/stream_equipment_telemetry.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table stream_rfi_status (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/stream_rfi_status.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table stream_weather_conditions (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/stream_weather_conditions.csv'
) with (format='csv', ignoreFirstRecord=true)

.ingest into table stream_daily_log_activity (
    h'abfss://your-lakehouse-path/Files/construction_site_operations/data/stream_daily_log_activity.csv'
) with (format='csv', ignoreFirstRecord=true)
```

### 2.3 Verify Eventhouse Tables

```kql
// Check row counts for all tables
.show tables
| project TableName
| extend RowCount = toscalar(
    union daily_logs, pm_interactions, rfi_events, safety_inspections,
          change_orders, phase_handoffs, safety_alerts, site_location,
          stream_safety_events, stream_equipment_telemetry,
          stream_rfi_status, stream_weather_conditions,
          stream_daily_log_activity
    | count)
```

**Expected Output:** 13 KQL tables (8 event fact + 5 stream)

---

## Step 3: Entity Type Definitions

Define all 6 entity types as JSON structures for the ontology package.

### 3.1 Supervisor Entity

```json
{
    "entityTypeName": "Supervisor",
    "primaryKey": "supervisor_id",
    "dataBinding": {
        "sourceType": "Lakehouse",
        "tableName": "dim_supervisors"
    },
    "properties": [
        {"name": "supervisor_id", "type": "String", "isPrimaryKey": true},
        {"name": "name", "type": "String"},
        {"name": "role", "type": "String"},
        {"name": "certifications", "type": "String"},
        {"name": "years_experience", "type": "Integer"},
        {"name": "project_id", "type": "String"},
        {"name": "hire_date", "type": "Date"},
        {"name": "department", "type": "String"},
        {"name": "region", "type": "String"},
        {"name": "email", "type": "String"},
        {"name": "phone", "type": "String"},
        {"name": "status", "type": "String"}
    ]
}
```

### 3.2 Project Entity

```json
{
    "entityTypeName": "Project",
    "primaryKey": "project_id",
    "dataBinding": {
        "sourceType": "Lakehouse",
        "tableName": "dim_projects"
    },
    "properties": [
        {"name": "project_id", "type": "String", "isPrimaryKey": true},
        {"name": "name", "type": "String"},
        {"name": "type", "type": "String"},
        {"name": "value", "type": "Float"},
        {"name": "start_date", "type": "Date"},
        {"name": "est_completion", "type": "Date"},
        {"name": "owner", "type": "String"},
        {"name": "gc_name", "type": "String"},
        {"name": "status", "type": "String"},
        {"name": "contract_type", "type": "String"},
        {"name": "city", "type": "String"},
        {"name": "state", "type": "String"}
    ]
}
```

### 3.3 ProjectSite Entity

```json
{
    "entityTypeName": "ProjectSite",
    "primaryKey": "site_id",
    "dataBinding": {
        "sourceType": "Lakehouse",
        "tableName": "dim_project_sites"
    },
    "properties": [
        {"name": "site_id", "type": "String", "isPrimaryKey": true},
        {"name": "project_id", "type": "String"},
        {"name": "address", "type": "String"},
        {"name": "region", "type": "String"},
        {"name": "active_trades", "type": "Integer"},
        {"name": "total_area_sqft", "type": "Integer"},
        {"name": "floors", "type": "Integer"},
        {"name": "site_status", "type": "String"},
        {"name": "lat", "type": "Float"},
        {"name": "lon", "type": "Float"}
    ]
}
```

### 3.4 InspectionType Entity

```json
{
    "entityTypeName": "InspectionType",
    "primaryKey": "inspection_type_id",
    "dataBinding": {
        "sourceType": "Lakehouse",
        "tableName": "dim_inspection_types"
    },
    "properties": [
        {"name": "inspection_type_id", "type": "String", "isPrimaryKey": true},
        {"name": "name", "type": "String"},
        {"name": "category", "type": "String"},
        {"name": "required_frequency", "type": "String"},
        {"name": "avg_duration_min", "type": "Integer"},
        {"name": "checklist_items", "type": "Integer"}
    ]
}
```

### 3.5 Subcontractor Entity

```json
{
    "entityTypeName": "Subcontractor",
    "primaryKey": "subcontractor_id",
    "dataBinding": {
        "sourceType": "Lakehouse",
        "tableName": "dim_subcontractors"
    },
    "properties": [
        {"name": "subcontractor_id", "type": "String", "isPrimaryKey": true},
        {"name": "name", "type": "String"},
        {"name": "trade", "type": "String"},
        {"name": "license_no", "type": "String"},
        {"name": "safety_rating", "type": "Float"},
        {"name": "projects_completed", "type": "Integer"}
    ]
}
```

### 3.6 TradePhase Entity

```json
{
    "entityTypeName": "TradePhase",
    "primaryKey": "phase_id",
    "dataBinding": {
        "sourceType": "Lakehouse",
        "tableName": "dim_trade_phases"
    },
    "properties": [
        {"name": "phase_id", "type": "String", "isPrimaryKey": true},
        {"name": "name", "type": "String"},
        {"name": "project_id", "type": "String"},
        {"name": "sequence", "type": "Integer"},
        {"name": "planned_start", "type": "Date"},
        {"name": "planned_end", "type": "Date"},
        {"name": "budget", "type": "Float"}
    ]
}
```

---

## Step 4: Relationship Type Definitions

```json
[
    {
        "relationshipTypeName": "supervises",
        "relationshipId": "REL-001",
        "sourceEntityType": "Supervisor",
        "targetEntityType": "Project",
        "cardinality": "Many:Many",
        "description": "Supervisor oversees one or more projects",
        "sourceKeyProperty": "project_id",
        "targetKeyProperty": "project_id"
    },
    {
        "relationshipTypeName": "located_at",
        "relationshipId": "REL-002",
        "sourceEntityType": "Project",
        "targetEntityType": "ProjectSite",
        "cardinality": "1:Many",
        "description": "Project has one or more physical sites",
        "sourceKeyProperty": "project_id",
        "targetKeyProperty": "project_id"
    },
    {
        "relationshipTypeName": "works_on",
        "relationshipId": "REL-003",
        "sourceEntityType": "Subcontractor",
        "targetEntityType": "Project",
        "cardinality": "Many:Many",
        "description": "Subcontractor is contracted to a project",
        "sourceKeyProperty": "subcontractor_id",
        "targetKeyProperty": "project_id"
    },
    {
        "relationshipTypeName": "belongs_to",
        "relationshipId": "REL-004",
        "sourceEntityType": "TradePhase",
        "targetEntityType": "Project",
        "cardinality": "Many:1",
        "description": "Trade phase is part of a project schedule",
        "sourceKeyProperty": "project_id",
        "targetKeyProperty": "project_id"
    },
    {
        "relationshipTypeName": "assigned_to",
        "relationshipId": "REL-005",
        "sourceEntityType": "Supervisor",
        "targetEntityType": "ProjectSite",
        "cardinality": "Many:Many",
        "description": "Supervisor is assigned to oversee a site",
        "sourceKeyProperty": "supervisor_id",
        "targetKeyProperty": "site_id"
    }
]
```

---

## Step 5: Contextualization Definitions

### 5.1 Event Fact Contextualizations

```json
[
    {
        "contextualizationName": "DailyLogEvent",
        "contextualizationId": "CTX-001",
        "sourceTable": "daily_logs",
        "sourceType": "Eventhouse",
        "timestampField": "date",
        "entityBindings": [
            {"entityType": "Supervisor", "bindingField": "supervisor_id"},
            {"entityType": "Project", "bindingField": "project_id"}
        ],
        "fields": [
            {"name": "log_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "project_id", "type": "String"},
            {"name": "date", "type": "DateTime"},
            {"name": "weather", "type": "String"},
            {"name": "crew_count", "type": "Integer"},
            {"name": "work_summary", "type": "String"},
            {"name": "doc_time_min", "type": "Integer"},
            {"name": "photos_attached", "type": "Integer"},
            {"name": "safety_incidents", "type": "Integer"}
        ]
    },
    {
        "contextualizationName": "PMInteractionEvent",
        "contextualizationId": "CTX-002",
        "sourceTable": "pm_interactions",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "entityBindings": [
            {"entityType": "Supervisor", "bindingField": "supervisor_id"}
        ],
        "fields": [
            {"name": "interaction_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "system", "type": "String"},
            {"name": "module", "type": "String"},
            {"name": "action", "type": "String"},
            {"name": "duration_ms", "type": "Integer"},
            {"name": "document_type", "type": "String"}
        ]
    },
    {
        "contextualizationName": "RFIEvent",
        "contextualizationId": "CTX-003",
        "sourceTable": "rfi_events",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "entityBindings": [
            {"entityType": "Supervisor", "bindingField": "supervisor_id"},
            {"entityType": "Project", "bindingField": "project_id"}
        ],
        "fields": [
            {"name": "rfi_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "project_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "question", "type": "String"},
            {"name": "status", "type": "String"},
            {"name": "response_time_hours", "type": "Float"},
            {"name": "doc_time_min", "type": "Integer"},
            {"name": "trade", "type": "String"}
        ]
    },
    {
        "contextualizationName": "SafetyInspectionEvent",
        "contextualizationId": "CTX-004",
        "sourceTable": "safety_inspections",
        "sourceType": "Eventhouse",
        "timestampField": "date",
        "entityBindings": [
            {"entityType": "Supervisor", "bindingField": "supervisor_id"},
            {"entityType": "ProjectSite", "bindingField": "site_id"}
        ],
        "fields": [
            {"name": "inspection_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "site_id", "type": "String"},
            {"name": "date", "type": "DateTime"},
            {"name": "type", "type": "String"},
            {"name": "findings_count", "type": "Integer"},
            {"name": "critical_count", "type": "Integer"},
            {"name": "doc_time_min", "type": "Integer"},
            {"name": "corrective_actions", "type": "Integer"}
        ]
    },
    {
        "contextualizationName": "ChangeOrderEvent",
        "contextualizationId": "CTX-005",
        "sourceTable": "change_orders",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "entityBindings": [
            {"entityType": "Project", "bindingField": "project_id"},
            {"entityType": "Supervisor", "bindingField": "supervisor_id"}
        ],
        "fields": [
            {"name": "change_order_id", "type": "String"},
            {"name": "project_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "description", "type": "String"},
            {"name": "cost_impact", "type": "Float"},
            {"name": "schedule_impact_days", "type": "Integer"},
            {"name": "doc_time_min", "type": "Integer"}
        ]
    },
    {
        "contextualizationName": "PhaseHandoffEvent",
        "contextualizationId": "CTX-006",
        "sourceTable": "phase_handoffs",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "entityBindings": [
            {"entityType": "Project", "bindingField": "project_id"}
        ],
        "fields": [
            {"name": "handoff_id", "type": "String"},
            {"name": "project_id", "type": "String"},
            {"name": "from_trade", "type": "String"},
            {"name": "to_trade", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "punch_list_items", "type": "Integer"},
            {"name": "doc_time_min", "type": "Integer"},
            {"name": "approved", "type": "String"}
        ]
    },
    {
        "contextualizationName": "SafetyAlertEvent",
        "contextualizationId": "CTX-007",
        "sourceTable": "safety_alerts",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "entityBindings": [
            {"entityType": "ProjectSite", "bindingField": "site_id"},
            {"entityType": "Supervisor", "bindingField": "supervisor_id"}
        ],
        "fields": [
            {"name": "alert_id", "type": "String"},
            {"name": "site_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "alert_type", "type": "String"},
            {"name": "severity", "type": "String"},
            {"name": "description", "type": "String"},
            {"name": "immediate_action", "type": "String"},
            {"name": "osha_reportable", "type": "String"}
        ]
    },
    {
        "contextualizationName": "SiteLocationPing",
        "contextualizationId": "CTX-008",
        "sourceTable": "site_location",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "entityBindings": [
            {"entityType": "Supervisor", "bindingField": "supervisor_id"},
            {"entityType": "ProjectSite", "bindingField": "site_id"}
        ],
        "fields": [
            {"name": "ping_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "site_id", "type": "String"},
            {"name": "zone", "type": "String"},
            {"name": "floor", "type": "Integer"},
            {"name": "activity_type", "type": "String"},
            {"name": "dwell_minutes", "type": "Float"}
        ]
    }
]
```

### 5.2 Stream Contextualizations

```json
[
    {
        "contextualizationName": "SafetyEventStream",
        "contextualizationId": "CTX-013a",
        "sourceTable": "stream_safety_events",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "isRealTime": true,
        "entityBindings": [
            {"entityType": "ProjectSite", "bindingField": "site_id"}
        ],
        "fields": [
            {"name": "event_id", "type": "String"},
            {"name": "site_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "event_type", "type": "String"},
            {"name": "zone", "type": "String"},
            {"name": "severity", "type": "String"},
            {"name": "worker_count", "type": "Integer"}
        ]
    },
    {
        "contextualizationName": "EquipmentTelemetryStream",
        "contextualizationId": "CTX-013b",
        "sourceTable": "stream_equipment_telemetry",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "isRealTime": true,
        "entityBindings": [
            {"entityType": "ProjectSite", "bindingField": "site_id"}
        ],
        "fields": [
            {"name": "telemetry_id", "type": "String"},
            {"name": "equipment_id", "type": "String"},
            {"name": "site_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "utilization_pct", "type": "Float"},
            {"name": "fuel_level", "type": "Float"},
            {"name": "maintenance_flag", "type": "String"}
        ]
    },
    {
        "contextualizationName": "RFIStatusStream",
        "contextualizationId": "CTX-013c",
        "sourceTable": "stream_rfi_status",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "isRealTime": true,
        "entityBindings": [
            {"entityType": "Project", "bindingField": "project_id"}
        ],
        "fields": [
            {"name": "rfi_id", "type": "String"},
            {"name": "project_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "status", "type": "String"},
            {"name": "assigned_to", "type": "String"},
            {"name": "days_open", "type": "Integer"},
            {"name": "priority", "type": "String"}
        ]
    },
    {
        "contextualizationName": "WeatherConditionsStream",
        "contextualizationId": "CTX-013d",
        "sourceTable": "stream_weather_conditions",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "isRealTime": true,
        "entityBindings": [
            {"entityType": "ProjectSite", "bindingField": "site_id"}
        ],
        "fields": [
            {"name": "reading_id", "type": "String"},
            {"name": "site_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "temp_f", "type": "Float"},
            {"name": "wind_mph", "type": "Float"},
            {"name": "precip_in", "type": "Float"},
            {"name": "lightning_flag", "type": "String"}
        ]
    },
    {
        "contextualizationName": "DailyLogActivityStream",
        "contextualizationId": "CTX-013e",
        "sourceTable": "stream_daily_log_activity",
        "sourceType": "Eventhouse",
        "timestampField": "timestamp",
        "isRealTime": true,
        "entityBindings": [
            {"entityType": "Supervisor", "bindingField": "supervisor_id"},
            {"entityType": "Project", "bindingField": "project_id"}
        ],
        "fields": [
            {"name": "log_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "timestamp", "type": "DateTime"},
            {"name": "project_id", "type": "String"},
            {"name": "section", "type": "String"},
            {"name": "entry_type", "type": "String"},
            {"name": "photo_count", "type": "Integer"}
        ]
    }
]
```

### 5.3 Batch Fact Contextualizations

```json
[
    {
        "contextualizationName": "SupervisorWellnessEvent",
        "contextualizationId": "CTX-009",
        "sourceTable": "fact_supervisor_wellness",
        "sourceType": "Lakehouse",
        "timestampField": "date",
        "entityBindings": [
            {"entityType": "Supervisor", "bindingField": "supervisor_id"}
        ],
        "fields": [
            {"name": "survey_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "date", "type": "Date"},
            {"name": "overtime_hours", "type": "Float"},
            {"name": "admin_burden_score", "type": "Integer"},
            {"name": "fatigue_score", "type": "Integer"},
            {"name": "work_life_balance", "type": "Integer"}
        ]
    },
    {
        "contextualizationName": "InspectionQualityEvent",
        "contextualizationId": "CTX-010",
        "sourceTable": "fact_inspection_quality",
        "sourceType": "Lakehouse",
        "timestampField": "date",
        "entityBindings": [
            {"entityType": "Supervisor", "bindingField": "supervisor_id"}
        ],
        "fields": [
            {"name": "quality_id", "type": "String"},
            {"name": "inspection_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "date", "type": "Date"},
            {"name": "completeness_pct", "type": "Float"},
            {"name": "photo_coverage_pct", "type": "Float"},
            {"name": "defect_identification_rate", "type": "Float"}
        ]
    },
    {
        "contextualizationName": "SubcontractorSatisfactionEvent",
        "contextualizationId": "CTX-011",
        "sourceTable": "fact_subcontractor_satisfaction",
        "sourceType": "Lakehouse",
        "timestampField": "date",
        "entityBindings": [
            {"entityType": "Subcontractor", "bindingField": "subcontractor_id"},
            {"entityType": "Project", "bindingField": "project_id"}
        ],
        "fields": [
            {"name": "survey_id", "type": "String"},
            {"name": "subcontractor_id", "type": "String"},
            {"name": "project_id", "type": "String"},
            {"name": "date", "type": "Date"},
            {"name": "coordination_score", "type": "Integer"},
            {"name": "payment_timeliness", "type": "Integer"},
            {"name": "communication_rating", "type": "Integer"}
        ]
    },
    {
        "contextualizationName": "ProjectPerformanceEvent",
        "contextualizationId": "CTX-012",
        "sourceTable": "fact_project_performance",
        "sourceType": "Lakehouse",
        "timestampField": "month",
        "entityBindings": [
            {"entityType": "Project", "bindingField": "project_id"},
            {"entityType": "Supervisor", "bindingField": "supervisor_id"}
        ],
        "fields": [
            {"name": "perf_id", "type": "String"},
            {"name": "project_id", "type": "String"},
            {"name": "supervisor_id", "type": "String"},
            {"name": "month", "type": "Date"},
            {"name": "budget_spent", "type": "Float"},
            {"name": "budget_remaining", "type": "Float"},
            {"name": "schedule_variance_days", "type": "Integer"},
            {"name": "rfi_count", "type": "Integer"},
            {"name": "change_order_count", "type": "Integer"}
        ]
    }
]
```

---

## Step 6: Create Ontology (Python — fabricontology)

```python
from fabricontology import OntologyClient

# Initialize client (uses Fabric workspace authentication)
client = OntologyClient()

# --- Step 6.1: Create Ontology ---
ontology = client.create_ontology(
    name="ConstructionSiteOpsOntology",
    description="Construction site operations documentation burden ontology — "
                "tracking supervisor time on daily logs, RFIs, safety inspections, "
                "change orders, and phase handoffs vs. field supervision time."
)
ontology_id = ontology["id"]
print(f"✓ Created ontology: {ontology_id}")

# --- Step 6.2: Create Entity Types ---
entity_definitions = {
    "Supervisor": {
        "primaryKey": "supervisor_id",
        "tableName": "dim_supervisors",
        "sourceType": "Lakehouse",
        "properties": [
            {"name": "supervisor_id", "type": "String", "isPrimaryKey": True},
            {"name": "name", "type": "String"},
            {"name": "role", "type": "String"},
            {"name": "certifications", "type": "String"},
            {"name": "years_experience", "type": "Integer"},
            {"name": "project_id", "type": "String"},
            {"name": "hire_date", "type": "Date"},
            {"name": "department", "type": "String"},
            {"name": "region", "type": "String"},
            {"name": "email", "type": "String"},
            {"name": "phone", "type": "String"},
            {"name": "status", "type": "String"},
        ],
    },
    "Project": {
        "primaryKey": "project_id",
        "tableName": "dim_projects",
        "sourceType": "Lakehouse",
        "properties": [
            {"name": "project_id", "type": "String", "isPrimaryKey": True},
            {"name": "name", "type": "String"},
            {"name": "type", "type": "String"},
            {"name": "value", "type": "Float"},
            {"name": "start_date", "type": "Date"},
            {"name": "est_completion", "type": "Date"},
            {"name": "owner", "type": "String"},
            {"name": "gc_name", "type": "String"},
            {"name": "status", "type": "String"},
            {"name": "contract_type", "type": "String"},
            {"name": "city", "type": "String"},
            {"name": "state", "type": "String"},
        ],
    },
    "ProjectSite": {
        "primaryKey": "site_id",
        "tableName": "dim_project_sites",
        "sourceType": "Lakehouse",
        "properties": [
            {"name": "site_id", "type": "String", "isPrimaryKey": True},
            {"name": "project_id", "type": "String"},
            {"name": "address", "type": "String"},
            {"name": "region", "type": "String"},
            {"name": "active_trades", "type": "Integer"},
            {"name": "total_area_sqft", "type": "Integer"},
            {"name": "floors", "type": "Integer"},
            {"name": "site_status", "type": "String"},
            {"name": "lat", "type": "Float"},
            {"name": "lon", "type": "Float"},
        ],
    },
    "InspectionType": {
        "primaryKey": "inspection_type_id",
        "tableName": "dim_inspection_types",
        "sourceType": "Lakehouse",
        "properties": [
            {"name": "inspection_type_id", "type": "String", "isPrimaryKey": True},
            {"name": "name", "type": "String"},
            {"name": "category", "type": "String"},
            {"name": "required_frequency", "type": "String"},
            {"name": "avg_duration_min", "type": "Integer"},
            {"name": "checklist_items", "type": "Integer"},
        ],
    },
    "Subcontractor": {
        "primaryKey": "subcontractor_id",
        "tableName": "dim_subcontractors",
        "sourceType": "Lakehouse",
        "properties": [
            {"name": "subcontractor_id", "type": "String", "isPrimaryKey": True},
            {"name": "name", "type": "String"},
            {"name": "trade", "type": "String"},
            {"name": "license_no", "type": "String"},
            {"name": "safety_rating", "type": "Float"},
            {"name": "projects_completed", "type": "Integer"},
        ],
    },
    "TradePhase": {
        "primaryKey": "phase_id",
        "tableName": "dim_trade_phases",
        "sourceType": "Lakehouse",
        "properties": [
            {"name": "phase_id", "type": "String", "isPrimaryKey": True},
            {"name": "name", "type": "String"},
            {"name": "project_id", "type": "String"},
            {"name": "sequence", "type": "Integer"},
            {"name": "planned_start", "type": "Date"},
            {"name": "planned_end", "type": "Date"},
            {"name": "budget", "type": "Float"},
        ],
    },
}

for entity_name, entity_def in entity_definitions.items():
    result = client.create_entity_type(
        ontology_id=ontology_id,
        entity_type_name=entity_name,
        primary_key=entity_def["primaryKey"],
        properties=entity_def["properties"],
        data_binding={
            "sourceType": entity_def["sourceType"],
            "tableName": entity_def["tableName"],
        },
    )
    print(f"✓ Created entity type: {entity_name}")

# --- Step 6.3: Create Relationship Types ---
relationships = [
    {
        "name": "supervises",
        "sourceEntityType": "Supervisor",
        "targetEntityType": "Project",
        "cardinality": "Many:Many",
        "sourceKey": "project_id",
        "targetKey": "project_id",
    },
    {
        "name": "located_at",
        "sourceEntityType": "Project",
        "targetEntityType": "ProjectSite",
        "cardinality": "1:Many",
        "sourceKey": "project_id",
        "targetKey": "project_id",
    },
    {
        "name": "works_on",
        "sourceEntityType": "Subcontractor",
        "targetEntityType": "Project",
        "cardinality": "Many:Many",
        "sourceKey": "subcontractor_id",
        "targetKey": "project_id",
    },
    {
        "name": "belongs_to",
        "sourceEntityType": "TradePhase",
        "targetEntityType": "Project",
        "cardinality": "Many:1",
        "sourceKey": "project_id",
        "targetKey": "project_id",
    },
    {
        "name": "assigned_to",
        "sourceEntityType": "Supervisor",
        "targetEntityType": "ProjectSite",
        "cardinality": "Many:Many",
        "sourceKey": "supervisor_id",
        "targetKey": "site_id",
    },
]

for rel in relationships:
    result = client.create_relationship_type(
        ontology_id=ontology_id,
        relationship_type_name=rel["name"],
        source_entity_type=rel["sourceEntityType"],
        target_entity_type=rel["targetEntityType"],
        cardinality=rel["cardinality"],
        source_key_property=rel["sourceKey"],
        target_key_property=rel["targetKey"],
    )
    print(f"✓ Created relationship: {rel['name']}")

# --- Step 6.4: Create Contextualizations ---
# (Event facts — Eventhouse)
eventhouse_contextualizations = [
    {"name": "DailyLogEvent",           "table": "daily_logs",          "timestamp": "date",      "bindings": [("Supervisor", "supervisor_id"), ("Project", "project_id")]},
    {"name": "PMInteractionEvent",      "table": "pm_interactions",     "timestamp": "timestamp", "bindings": [("Supervisor", "supervisor_id")]},
    {"name": "RFIEvent",                "table": "rfi_events",          "timestamp": "timestamp", "bindings": [("Supervisor", "supervisor_id"), ("Project", "project_id")]},
    {"name": "SafetyInspectionEvent",   "table": "safety_inspections",  "timestamp": "date",      "bindings": [("Supervisor", "supervisor_id"), ("ProjectSite", "site_id")]},
    {"name": "ChangeOrderEvent",        "table": "change_orders",       "timestamp": "timestamp", "bindings": [("Project", "project_id"), ("Supervisor", "supervisor_id")]},
    {"name": "PhaseHandoffEvent",       "table": "phase_handoffs",      "timestamp": "timestamp", "bindings": [("Project", "project_id")]},
    {"name": "SafetyAlertEvent",        "table": "safety_alerts",       "timestamp": "timestamp", "bindings": [("ProjectSite", "site_id"), ("Supervisor", "supervisor_id")]},
    {"name": "SiteLocationPing",        "table": "site_location",       "timestamp": "timestamp", "bindings": [("Supervisor", "supervisor_id"), ("ProjectSite", "site_id")]},
]

# (Streams — Eventhouse real-time)
stream_contextualizations = [
    {"name": "SafetyEventStream",        "table": "stream_safety_events",        "timestamp": "timestamp", "bindings": [("ProjectSite", "site_id")]},
    {"name": "EquipmentTelemetryStream", "table": "stream_equipment_telemetry",  "timestamp": "timestamp", "bindings": [("ProjectSite", "site_id")]},
    {"name": "RFIStatusStream",          "table": "stream_rfi_status",           "timestamp": "timestamp", "bindings": [("Project", "project_id")]},
    {"name": "WeatherConditionsStream",  "table": "stream_weather_conditions",   "timestamp": "timestamp", "bindings": [("ProjectSite", "site_id")]},
    {"name": "DailyLogActivityStream",   "table": "stream_daily_log_activity",   "timestamp": "timestamp", "bindings": [("Supervisor", "supervisor_id"), ("Project", "project_id")]},
]

# (Batch facts — Lakehouse)
batch_contextualizations = [
    {"name": "SupervisorWellnessEvent",       "table": "fact_supervisor_wellness",        "timestamp": "date",  "bindings": [("Supervisor", "supervisor_id")], "sourceType": "Lakehouse"},
    {"name": "InspectionQualityEvent",        "table": "fact_inspection_quality",         "timestamp": "date",  "bindings": [("Supervisor", "supervisor_id")], "sourceType": "Lakehouse"},
    {"name": "SubcontractorSatisfactionEvent","table": "fact_subcontractor_satisfaction", "timestamp": "date",  "bindings": [("Subcontractor", "subcontractor_id"), ("Project", "project_id")], "sourceType": "Lakehouse"},
    {"name": "ProjectPerformanceEvent",       "table": "fact_project_performance",        "timestamp": "month", "bindings": [("Project", "project_id"), ("Supervisor", "supervisor_id")], "sourceType": "Lakehouse"},
]

all_ctx = (
    [(c, "Eventhouse") for c in eventhouse_contextualizations]
    + [(c, "Eventhouse") for c in stream_contextualizations]
    + [(c, c.get("sourceType", "Lakehouse")) for c in batch_contextualizations]
)

for ctx_def, default_source in all_ctx:
    source = ctx_def.get("sourceType", default_source)
    entity_bindings = [
        {"entityType": et, "bindingField": bf}
        for et, bf in ctx_def["bindings"]
    ]
    result = client.create_contextualization(
        ontology_id=ontology_id,
        contextualization_name=ctx_def["name"],
        source_table=ctx_def["table"],
        source_type=source,
        timestamp_field=ctx_def["timestamp"],
        entity_bindings=entity_bindings,
    )
    print(f"✓ Created contextualization: {ctx_def['name']}")

print(f"\n{'='*60}")
print(f"Ontology '{ontology['name']}' created successfully!")
print(f"  Ontology ID: {ontology_id}")
print(f"  Entity Types: 6")
print(f"  Relationships: 5")
print(f"  Contextualizations: 13 (8 event + 5 stream)")
print(f"{'='*60}")
```

---

## Step 7: Verify Ontology

```python
# Verify ontology completeness
ontology_details = client.get_ontology(ontology_id)

entity_types = client.list_entity_types(ontology_id)
relationship_types = client.list_relationship_types(ontology_id)
contextualizations = client.list_contextualizations(ontology_id)

print(f"Ontology: {ontology_details['name']}")
print(f"  Entity Types: {len(entity_types)} (expected: 6)")
print(f"  Relationship Types: {len(relationship_types)} (expected: 5)")
print(f"  Contextualizations: {len(contextualizations)} (expected: 13)")

# Detailed verification
print("\n--- Entity Types ---")
for et in entity_types:
    print(f"  {et['entityTypeName']}: {len(et['properties'])} properties")

print("\n--- Relationship Types ---")
for rt in relationship_types:
    print(f"  {rt['relationshipTypeName']}: {rt['sourceEntityType']} → {rt['targetEntityType']}")

print("\n--- Contextualizations ---")
for ctx in contextualizations:
    bindings = ", ".join([b['entityType'] for b in ctx['entityBindings']])
    print(f"  {ctx['contextualizationName']}: [{bindings}] → {ctx['sourceTable']}")
```

**Expected Verification Output:**
```
Ontology: ConstructionSiteOpsOntology
  Entity Types: 6 (expected: 6)
  Relationship Types: 5 (expected: 5)
  Contextualizations: 13 (expected: 13)

--- Entity Types ---
  Supervisor: 12 properties
  Project: 12 properties
  ProjectSite: 10 properties
  InspectionType: 6 properties
  Subcontractor: 6 properties
  TradePhase: 7 properties

--- Relationship Types ---
  supervises: Supervisor → Project
  located_at: Project → ProjectSite
  works_on: Subcontractor → Project
  belongs_to: TradePhase → Project
  assigned_to: Supervisor → ProjectSite

--- Contextualizations ---
  DailyLogEvent: [Supervisor, Project] → daily_logs
  PMInteractionEvent: [Supervisor] → pm_interactions
  RFIEvent: [Supervisor, Project] → rfi_events
  SafetyInspectionEvent: [Supervisor, ProjectSite] → safety_inspections
  ChangeOrderEvent: [Project, Supervisor] → change_orders
  PhaseHandoffEvent: [Project] → phase_handoffs
  SafetyAlertEvent: [ProjectSite, Supervisor] → safety_alerts
  SiteLocationPing: [Supervisor, ProjectSite] → site_location
  SafetyEventStream: [ProjectSite] → stream_safety_events
  EquipmentTelemetryStream: [ProjectSite] → stream_equipment_telemetry
  RFIStatusStream: [Project] → stream_rfi_status
  WeatherConditionsStream: [ProjectSite] → stream_weather_conditions
  DailyLogActivityStream: [Supervisor, Project] → stream_daily_log_activity
```

---

## Data Binding Summary

| Data Layer  | Source               | Tables | Purpose                                      |
|-------------|----------------------|--------|----------------------------------------------|
| Lakehouse   | Delta Tables         | 10     | 6 dimension entities + 4 batch fact analytics |
| Eventhouse  | KQL Tables (Event)   | 8      | Event facts (daily logs, RFIs, inspections)   |
| Eventhouse  | KQL Tables (Stream)  | 5      | Real-time streams (safety, weather, telemetry)|
| **Total**   |                      | **23** | Complete construction ops data model          |

### Entity-to-Table Quick Reference

| Entity Type     | Lakehouse Table        | Primary Key          |
|-----------------|------------------------|----------------------|
| Supervisor      | dim_supervisors        | supervisor_id        |
| Project         | dim_projects           | project_id           |
| ProjectSite     | dim_project_sites      | site_id              |
| InspectionType  | dim_inspection_types   | inspection_type_id   |
| Subcontractor   | dim_subcontractors     | subcontractor_id     |
| TradePhase      | dim_trade_phases       | phase_id             |

---

## Built-In Data Patterns

### Pattern 1: Supervisor Documentation Overload

**Signal:** Supervisors spending >40% of their day on documentation instead of field supervision.

**Detection Query (KQL):**
```kql
site_location
| where timestamp > ago(30d)
| summarize doc_minutes = sumif(dwell_minutes, activity_type == "Documentation"),
            field_minutes = sumif(dwell_minutes, activity_type == "Supervision"),
            total_minutes = sum(dwell_minutes)
  by supervisor_id
| extend doc_pct = round(100.0 * doc_minutes / total_minutes, 1)
| where doc_pct > 40
| order by doc_pct desc
```

**Impact:** Supervisors in the documentation overload zone show higher fatigue scores (from `fact_supervisor_wellness`) and lower inspection quality scores (from `fact_inspection_quality`). This pattern identifies candidates for documentation workflow improvement or administrative support.

### Pattern 2: RFI Documentation Cascade

**Signal:** Projects with high RFI volume show exponentially increasing documentation time as open RFIs compound.

**Detection Query (KQL):**
```kql
rfi_events
| where timestamp > ago(90d)
| summarize rfi_count = count(),
            total_doc_min = sum(doc_time_min),
            avg_doc_min = avg(doc_time_min),
            overdue_count = countif(status == "Overdue"),
            avg_response_hrs = avg(response_time_hours)
  by project_id, bin(timestamp, 7d)
| order by project_id, timestamp asc
```

**Impact:** Projects with >15 open RFIs simultaneously show a documentation cascade where each new RFI takes 30-50% longer to prepare because supervisors must cross-reference existing open items. Combined with `stream_rfi_status` real-time data, this detects cascades before they reach critical mass.

### Pattern 3: Safety Inspection Documentation Burden

**Signal:** Safety inspection documentation time exceeds actual inspection time, particularly for complex inspection types.

**Detection Query (KQL):**
```kql
safety_inspections
| where date > ago(60d)
| join kind=inner (
    daily_logs | summarize daily_doc = sum(doc_time_min) by supervisor_id, date
) on supervisor_id, date
| summarize avg_inspection_doc = avg(doc_time_min),
            avg_daily_doc = avg(daily_doc),
            total_findings = sum(findings_count),
            total_critical = sum(critical_count)
  by supervisor_id, type
| extend inspection_burden_pct = round(100.0 * avg_inspection_doc / avg_daily_doc, 1)
| order by inspection_burden_pct desc
```

**Impact:** When inspection documentation exceeds 25% of total daily documentation time, inspection quality (`fact_inspection_quality.completeness_pct`) drops below 80%. Identifies inspection types that need streamlined documentation templates.

### Pattern 4: Change Order Cost-Documentation Correlation

**Signal:** High-value change orders generate disproportionate documentation overhead relative to their cost impact.

**Detection Query (KQL):**
```kql
change_orders
| where timestamp > ago(180d)
| summarize co_count = count(),
            total_cost = sum(cost_impact),
            total_schedule_days = sum(schedule_impact_days),
            total_doc_min = sum(doc_time_min),
            avg_doc_per_co = avg(doc_time_min)
  by project_id
| join kind=inner (
    daily_logs | summarize total_daily_doc = sum(doc_time_min) by project_id
) on project_id
| extend co_doc_pct = round(100.0 * total_doc_min / total_daily_doc, 1),
         doc_per_dollar = round(total_doc_min / total_cost * 10000, 2)
| order by co_doc_pct desc
```

**Impact:** Projects where change order documentation exceeds 20% of total documentation time show schedule variance exceeding +15 days (`fact_project_performance.schedule_variance_days`). Identifies projects that need change order workflow automation.

### Pattern 5: Weather-Driven Documentation Delays

**Signal:** Adverse weather conditions increase daily log documentation time by 40-60% due to safety reports, work stoppage documentation, and schedule impact assessments.

**Detection Query (Cross-Source — SQL + KQL):**
```sql
-- Lakehouse SQL: Weather impact on documentation times
SELECT dl.weather,
       COUNT(*) as log_count,
       AVG(dl.doc_time_min) as avg_doc_time_min,
       AVG(dl.crew_count) as avg_crew,
       AVG(dl.safety_incidents) as avg_safety_incidents,
       AVG(dl.photos_attached) as avg_photos
FROM fact_daily_logs dl
GROUP BY dl.weather
ORDER BY avg_doc_time_min DESC
```

```kql
// KQL: Real-time weather correlation with documentation burst
stream_weather_conditions
| where timestamp > ago(7d) and (lightning_flag == "Yes" or wind_mph > 30 or precip_in > 0.5)
| join kind=inner (
    stream_daily_log_activity
    | where timestamp > ago(7d)
    | summarize entries = count(), photos = sum(photo_count) by supervisor_id, bin(timestamp, 1h)
) on $left.timestamp == $right.timestamp
| summarize weather_events = count(), avg_log_entries = avg(entries)
  by site_id, bin(timestamp, 1d)
```

**Impact:** Rain and high-wind days generate 45% more daily log entries and 60% more photo documentation. When combined with safety event streams (`stream_safety_events`), weather-driven days show 3x the documentation burden. This pattern enables proactive staffing of administrative support on forecasted adverse weather days.

---

## Next Steps

1. **Deploy Data Agent:** Use `deploy_data_agent_notebook.py` with the ontology to create a construction-specific data agent
2. **Create Dashboard:** Build Power BI reports using the semantic model created from this ontology
3. **Set Up Real-Time Alerts:** Configure Eventhouse streaming ingestion for live safety events, equipment telemetry, and weather data
4. **Tune Documentation Thresholds:** Calibrate overload thresholds (40% doc time, 25% inspection burden) based on actual project data
5. **Cross-Industry Comparison:** Compare documentation burden patterns with other industries using the cross-industry notebook framework
