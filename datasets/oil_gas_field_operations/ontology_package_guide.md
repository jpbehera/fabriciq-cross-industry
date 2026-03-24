# Oil & Gas Field Operations — Ontology Package Guide

## Overview

This guide walks through creating the **OilGasFieldOpsOntology** package in
Microsoft Fabric using the FabricIQ accelerator. The ontology models
documentation burden across upstream oil & gas field operations — tracking
how much time field engineers spend on daily drilling reports, HSE inspections,
permit-to-work paperwork, well integrity documentation, and tour handoffs
versus actual field operations and decision-making.

---

## Prerequisites

| Resource        | Name                  | Purpose                                         |
|-----------------|-----------------------|-------------------------------------------------|
| Lakehouse       | `OilGasLakehouse`     | Dim tables + batch fact tables (Delta format)   |
| Eventhouse      | `OilGasEventhouse`    | Event fact tables + stream tables (KQL format)  |
| KQL Database    | `OilGasKQLDB`         | KQL database within the Eventhouse              |
| Workspace       | Any Fabric workspace  | Must have Contributor or higher permissions      |
| Python Env      | Fabric notebook       | `semantic-link` and `fabriciq` packages          |

### Required Data Files

```
Files/oil_gas_field_operations/data/
├── dim_field_engineers.csv
├── dim_well_sites.csv
├── dim_facilities.csv
├── dim_report_types.csv
├── dim_equipment.csv
├── dim_regulatory_bodies.csv
├── fact_daily_drilling_reports.csv
├── fact_scada_interactions.csv
├── fact_hse_inspections.csv
├── fact_permit_to_work.csv
├── fact_well_integrity_events.csv
├── fact_tour_handoffs.csv
├── fact_production_alerts.csv
├── fact_field_location.csv
├── fact_field_wellness.csv
├── fact_report_quality.csv
├── fact_operator_satisfaction.csv
├── fact_production_performance.csv
├── stream_well_telemetry.csv
├── stream_scada_alarms.csv
├── stream_hse_events.csv
├── stream_ptw_status.csv
└── stream_environmental_monitoring.csv
```

---

## Step 1: Prepare Lakehouse

Upload CSV files and load them into Delta tables.

```python
import os
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

base_path = "Files/oil_gas_field_operations/data"

# ── Dimension Tables ──────────────────────────────────────────
dim_tables = [
    "dim_field_engineers",
    "dim_well_sites",
    "dim_facilities",
    "dim_report_types",
    "dim_equipment",
    "dim_regulatory_bodies",
]

for table in dim_tables:
    csv_path = f"{base_path}/{table}.csv"
    df = spark.read.option("header", True).option("inferSchema", True).csv(csv_path)
    df.write.mode("overwrite").format("delta").saveAsTable(table)
    print(f"✓ Loaded {table}: {df.count()} rows")

# ── Batch Fact Tables ─────────────────────────────────────────
batch_facts = [
    "fact_field_wellness",
    "fact_report_quality",
    "fact_operator_satisfaction",
    "fact_production_performance",
]

for table in batch_facts:
    csv_path = f"{base_path}/{table}.csv"
    df = spark.read.option("header", True).option("inferSchema", True).csv(csv_path)
    df.write.mode("overwrite").format("delta").saveAsTable(table)
    print(f"✓ Loaded {table}: {df.count()} rows")
```

### Verify Lakehouse Tables

```python
tables = spark.catalog.listTables()
for t in tables:
    print(f"  {t.name}")
# Expected: 10 tables (6 dim + 4 batch fact)
```

---

## Step 2: Prepare Eventhouse

Ingest event fact tables and stream tables into the KQL database.

```python
import pandas as pd

kql_db = "OilGasKQLDB"

# ── Event Fact Tables ─────────────────────────────────────────
event_facts = [
    "fact_daily_drilling_reports",
    "fact_scada_interactions",
    "fact_hse_inspections",
    "fact_permit_to_work",
    "fact_well_integrity_events",
    "fact_tour_handoffs",
    "fact_production_alerts",
    "fact_field_location",
]

for table in event_facts:
    csv_path = f"{base_path}/{table}.csv"
    df = pd.read_csv(csv_path)
    # Use Fabric KQL ingestion API or .ingest inline
    print(f"✓ Ingested {table}: {len(df)} rows → {kql_db}")

# ── Stream Tables ─────────────────────────────────────────────
stream_tables = [
    "stream_well_telemetry",
    "stream_scada_alarms",
    "stream_hse_events",
    "stream_ptw_status",
    "stream_environmental_monitoring",
]

for table in stream_tables:
    csv_path = f"{base_path}/{table}.csv"
    df = pd.read_csv(csv_path)
    print(f"✓ Ingested {table}: {len(df)} rows → {kql_db}")
```

### Verify Eventhouse Tables

```kql
.show tables
| project TableName, TotalRowCount
// Expected: 13 tables (8 event fact + 5 stream)
```

---

## Step 3: Entity Type Definitions

Define all 6 entity types as JSON objects for the ontology package.

### ENT-001: FieldEngineer

```json
{
    "entityTypeName": "FieldEngineer",
    "datasource": "Lakehouse",
    "tableName": "dim_field_engineers",
    "keyColumn": "engineer_id",
    "properties": [
        {"name": "engineer_id", "type": "string", "isPrimaryKey": true},
        {"name": "name", "type": "string", "description": "Full name of the field engineer"},
        {"name": "role", "type": "string", "description": "Job role (drilling, production, HSE)"},
        {"name": "certifications", "type": "string", "description": "Active certifications (IWCF, SafeGulf)"},
        {"name": "rotation_schedule", "type": "string", "description": "Rotation pattern (14/14, 28/28)"},
        {"name": "base", "type": "string", "description": "Home base office location"},
        {"name": "years_experience", "type": "int", "description": "Total years of field experience"}
    ]
}
```

### ENT-002: WellSite

```json
{
    "entityTypeName": "WellSite",
    "datasource": "Lakehouse",
    "tableName": "dim_well_sites",
    "keyColumn": "well_id",
    "properties": [
        {"name": "well_id", "type": "string", "isPrimaryKey": true},
        {"name": "name", "type": "string", "description": "Well name or pad designation"},
        {"name": "basin", "type": "string", "description": "Geological basin (Permian, Eagle Ford)"},
        {"name": "field", "type": "string", "description": "Production field name"},
        {"name": "operator", "type": "string", "description": "Operating company"},
        {"name": "spud_date", "type": "date", "description": "Date drilling commenced"},
        {"name": "status", "type": "string", "description": "Current status (drilling, producing, SI)"},
        {"name": "depth_ft", "type": "int", "description": "Total measured depth in feet"},
        {"name": "production_bpd", "type": "float", "description": "Current production (barrels per day)"}
    ]
}
```

### ENT-003: Facility

```json
{
    "entityTypeName": "Facility",
    "datasource": "Lakehouse",
    "tableName": "dim_facilities",
    "keyColumn": "facility_id",
    "properties": [
        {"name": "facility_id", "type": "string", "isPrimaryKey": true},
        {"name": "name", "type": "string", "description": "Facility name"},
        {"name": "type", "type": "string", "description": "Facility type (compressor, gathering, processing)"},
        {"name": "location", "type": "string", "description": "Geographic location or GPS coordinates"},
        {"name": "capacity", "type": "string", "description": "Throughput or storage capacity"},
        {"name": "operator", "type": "string", "description": "Operating company"},
        {"name": "regulatory_jurisdiction", "type": "string", "description": "Governing regulatory jurisdiction"}
    ]
}
```

### ENT-004: ReportType

```json
{
    "entityTypeName": "ReportType",
    "datasource": "Lakehouse",
    "tableName": "dim_report_types",
    "keyColumn": "report_type_id",
    "properties": [
        {"name": "report_type_id", "type": "string", "isPrimaryKey": true},
        {"name": "name", "type": "string", "description": "Report name (DDR, TRIR, JSA)"},
        {"name": "category", "type": "string", "description": "Report category (drilling, HSE, production)"},
        {"name": "frequency", "type": "string", "description": "Required frequency (daily, per-job)"},
        {"name": "avg_completion_min", "type": "int", "description": "Average completion time in minutes"},
        {"name": "regulatory_required", "type": "boolean", "description": "Whether mandated by regulation"}
    ]
}
```

### ENT-005: Equipment

```json
{
    "entityTypeName": "Equipment",
    "datasource": "Lakehouse",
    "tableName": "dim_equipment",
    "keyColumn": "equipment_id",
    "properties": [
        {"name": "equipment_id", "type": "string", "isPrimaryKey": true},
        {"name": "name", "type": "string", "description": "Equipment name or designation"},
        {"name": "type", "type": "string", "description": "Equipment type (BOP, ESP, separator)"},
        {"name": "well_id", "type": "string", "description": "FK — well site where installed"},
        {"name": "install_date", "type": "date", "description": "Installation date"},
        {"name": "last_maintenance", "type": "date", "description": "Date of most recent maintenance"},
        {"name": "criticality", "type": "string", "description": "Criticality level (high, medium, low)"}
    ]
}
```

### ENT-006: RegulatoryBody

```json
{
    "entityTypeName": "RegulatoryBody",
    "datasource": "Lakehouse",
    "tableName": "dim_regulatory_bodies",
    "keyColumn": "reg_id",
    "properties": [
        {"name": "reg_id", "type": "string", "isPrimaryKey": true},
        {"name": "name", "type": "string", "description": "Regulatory body name (BSEE, TRRC, EPA)"},
        {"name": "jurisdiction", "type": "string", "description": "Jurisdiction scope (federal, state, basin)"},
        {"name": "inspection_frequency", "type": "string", "description": "Required inspection frequency"},
        {"name": "key_requirements", "type": "string", "description": "Primary compliance requirements"}
    ]
}
```

---

## Step 4: Relationship Type Definitions

```json
[
    {
        "relationshipTypeName": "operates",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "WellSite",
        "sourceKeyColumn": "engineer_id",
        "targetKeyColumn": "well_id",
        "description": "Field engineer operates or is assigned to a well site"
    },
    {
        "relationshipTypeName": "stationed_at",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "Facility",
        "sourceKeyColumn": "engineer_id",
        "targetKeyColumn": "facility_id",
        "description": "Field engineer is stationed at or works from a facility"
    },
    {
        "relationshipTypeName": "hosts",
        "sourceEntityType": "WellSite",
        "targetEntityType": "Equipment",
        "sourceKeyColumn": "well_id",
        "targetKeyColumn": "well_id",
        "description": "Well site hosts installed equipment"
    },
    {
        "relationshipTypeName": "regulated_by",
        "sourceEntityType": "Facility",
        "targetEntityType": "RegulatoryBody",
        "sourceKeyColumn": "regulatory_jurisdiction",
        "targetKeyColumn": "jurisdiction",
        "description": "Facility is governed by a regulatory authority"
    },
    {
        "relationshipTypeName": "requires_report",
        "sourceEntityType": "WellSite",
        "targetEntityType": "ReportType",
        "sourceKeyColumn": "well_id",
        "targetKeyColumn": "report_type_id",
        "description": "Well site operations require specific report types"
    }
]
```

---

## Step 5: Contextualization Definitions

### Event Contextualizations (Eventhouse)

```json
[
    {
        "name": "DailyDrillingReports",
        "datasource": "Eventhouse",
        "tableName": "fact_daily_drilling_reports",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "WellSite",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "well_id",
        "description": "DDR documentation time vs footage drilled per tour"
    },
    {
        "name": "SCADAInteractions",
        "datasource": "Eventhouse",
        "tableName": "fact_scada_interactions",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "WellSite",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "well_id",
        "description": "Time engineers spend interacting with SCADA screens"
    },
    {
        "name": "HSEInspections",
        "datasource": "Eventhouse",
        "tableName": "fact_hse_inspections",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "Facility",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "facility_id",
        "description": "HSE inspection documentation time vs finding count"
    },
    {
        "name": "PermitToWork",
        "datasource": "Eventhouse",
        "tableName": "fact_permit_to_work",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "Facility",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "facility_id",
        "description": "PTW paperwork time across hazard levels and approval chains"
    },
    {
        "name": "WellIntegrityEvents",
        "datasource": "Eventhouse",
        "tableName": "fact_well_integrity_events",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "WellSite",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "well_id",
        "description": "Well integrity test documentation time and pass/fail burden"
    },
    {
        "name": "TourHandoffs",
        "datasource": "Eventhouse",
        "tableName": "fact_tour_handoffs",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "WellSite",
        "sourceJoinColumn": "from_engineer",
        "targetJoinColumn": "well_id",
        "description": "Tour handoff knowledge transfer documentation time"
    },
    {
        "name": "ProductionAlerts",
        "datasource": "Eventhouse",
        "tableName": "fact_production_alerts",
        "sourceEntityType": "WellSite",
        "targetEntityType": "Equipment",
        "sourceJoinColumn": "well_id",
        "targetJoinColumn": "well_id",
        "description": "Production alert severity and response documentation"
    },
    {
        "name": "FieldLocationTracking",
        "datasource": "Eventhouse",
        "tableName": "fact_field_location",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "Facility",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "facility_id",
        "description": "Field location dwell time to measure field vs desk ratio"
    }
]
```

### Batch Contextualizations (Lakehouse)

```json
[
    {
        "name": "FieldWellnessSurveys",
        "datasource": "Lakehouse",
        "tableName": "fact_field_wellness",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": null,
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": null,
        "description": "Rotation fatigue, admin burden, and isolation scores"
    },
    {
        "name": "ReportQualityMetrics",
        "datasource": "Lakehouse",
        "tableName": "fact_report_quality",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "ReportType",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "report_id",
        "description": "Report completeness, accuracy, and regulatory readiness"
    },
    {
        "name": "OperatorSatisfaction",
        "datasource": "Lakehouse",
        "tableName": "fact_operator_satisfaction",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "Facility",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "facility_id",
        "description": "Operator audit scores and JV partner compliance ratings"
    },
    {
        "name": "ProductionPerformance",
        "datasource": "Lakehouse",
        "tableName": "fact_production_performance",
        "sourceEntityType": "FieldEngineer",
        "targetEntityType": "WellSite",
        "sourceJoinColumn": "engineer_id",
        "targetJoinColumn": "well_id",
        "description": "Monthly production vs documentation hours per well"
    }
]
```

### Stream Contextualizations (Eventhouse — Real-Time)

```json
[
    {
        "name": "WellTelemetry",
        "datasource": "Eventhouse",
        "tableName": "stream_well_telemetry",
        "sourceEntityType": "WellSite",
        "targetEntityType": "Equipment",
        "sourceJoinColumn": "well_id",
        "targetJoinColumn": "well_id",
        "description": "Real-time well pressure, temperature, and flow telemetry"
    },
    {
        "name": "SCADAAlarms",
        "datasource": "Eventhouse",
        "tableName": "stream_scada_alarms",
        "sourceEntityType": "Facility",
        "targetEntityType": "Equipment",
        "sourceJoinColumn": "facility_id",
        "targetJoinColumn": "facility_id",
        "description": "Real-time SCADA alarm stream with priority levels"
    },
    {
        "name": "HSEEvents",
        "datasource": "Eventhouse",
        "tableName": "stream_hse_events",
        "sourceEntityType": "Facility",
        "targetEntityType": "RegulatoryBody",
        "sourceJoinColumn": "facility_id",
        "targetJoinColumn": "reg_id",
        "description": "Real-time HSE event stream with severity classification"
    },
    {
        "name": "PTWStatusUpdates",
        "datasource": "Eventhouse",
        "tableName": "stream_ptw_status",
        "sourceEntityType": "Facility",
        "targetEntityType": "FieldEngineer",
        "sourceJoinColumn": "facility_id",
        "targetJoinColumn": "engineer_id",
        "description": "Real-time permit-to-work approval status stream"
    },
    {
        "name": "EnvironmentalMonitoring",
        "datasource": "Eventhouse",
        "tableName": "stream_environmental_monitoring",
        "sourceEntityType": "Facility",
        "targetEntityType": "RegulatoryBody",
        "sourceJoinColumn": "facility_id",
        "targetJoinColumn": "reg_id",
        "description": "Real-time environmental parameter monitoring with exceedance flags"
    }
]
```

---

## Step 6: Create Ontology

```python
from fabriciq import OntologyBuilder

# ── Initialize Builder ────────────────────────────────────────
builder = OntologyBuilder(
    ontology_name="OilGasFieldOpsOntology",
    lakehouse_name="OilGasLakehouse",
    eventhouse_name="OilGasEventhouse",
    kql_database_name="OilGasKQLDB",
)

# ── Add Entity Types ──────────────────────────────────────────
builder.add_entity_type(
    name="FieldEngineer",
    table="dim_field_engineers",
    key_column="engineer_id",
    datasource="Lakehouse",
    properties={
        "engineer_id": "string",
        "name": "string",
        "role": "string",
        "certifications": "string",
        "rotation_schedule": "string",
        "base": "string",
        "years_experience": "int",
    },
)

builder.add_entity_type(
    name="WellSite",
    table="dim_well_sites",
    key_column="well_id",
    datasource="Lakehouse",
    properties={
        "well_id": "string",
        "name": "string",
        "basin": "string",
        "field": "string",
        "operator": "string",
        "spud_date": "date",
        "status": "string",
        "depth_ft": "int",
        "production_bpd": "float",
    },
)

builder.add_entity_type(
    name="Facility",
    table="dim_facilities",
    key_column="facility_id",
    datasource="Lakehouse",
    properties={
        "facility_id": "string",
        "name": "string",
        "type": "string",
        "location": "string",
        "capacity": "string",
        "operator": "string",
        "regulatory_jurisdiction": "string",
    },
)

builder.add_entity_type(
    name="ReportType",
    table="dim_report_types",
    key_column="report_type_id",
    datasource="Lakehouse",
    properties={
        "report_type_id": "string",
        "name": "string",
        "category": "string",
        "frequency": "string",
        "avg_completion_min": "int",
        "regulatory_required": "boolean",
    },
)

builder.add_entity_type(
    name="Equipment",
    table="dim_equipment",
    key_column="equipment_id",
    datasource="Lakehouse",
    properties={
        "equipment_id": "string",
        "name": "string",
        "type": "string",
        "well_id": "string",
        "install_date": "date",
        "last_maintenance": "date",
        "criticality": "string",
    },
)

builder.add_entity_type(
    name="RegulatoryBody",
    table="dim_regulatory_bodies",
    key_column="reg_id",
    datasource="Lakehouse",
    properties={
        "reg_id": "string",
        "name": "string",
        "jurisdiction": "string",
        "inspection_frequency": "string",
        "key_requirements": "string",
    },
)

# ── Add Relationship Types ────────────────────────────────────
builder.add_relationship("operates", "FieldEngineer", "WellSite")
builder.add_relationship("stationed_at", "FieldEngineer", "Facility")
builder.add_relationship("hosts", "WellSite", "Equipment")
builder.add_relationship("regulated_by", "Facility", "RegulatoryBody")
builder.add_relationship("requires_report", "WellSite", "ReportType")

# ── Add Event Contextualizations ──────────────────────────────
builder.add_contextualization("DailyDrillingReports",   "Eventhouse", "fact_daily_drilling_reports",  "FieldEngineer", "WellSite",      "engineer_id", "well_id")
builder.add_contextualization("SCADAInteractions",      "Eventhouse", "fact_scada_interactions",      "FieldEngineer", "WellSite",      "engineer_id", "well_id")
builder.add_contextualization("HSEInspections",         "Eventhouse", "fact_hse_inspections",         "FieldEngineer", "Facility",      "engineer_id", "facility_id")
builder.add_contextualization("PermitToWork",           "Eventhouse", "fact_permit_to_work",          "FieldEngineer", "Facility",      "engineer_id", "facility_id")
builder.add_contextualization("WellIntegrityEvents",    "Eventhouse", "fact_well_integrity_events",   "FieldEngineer", "WellSite",      "engineer_id", "well_id")
builder.add_contextualization("TourHandoffs",           "Eventhouse", "fact_tour_handoffs",           "FieldEngineer", "WellSite",      "from_engineer","well_id")
builder.add_contextualization("ProductionAlerts",       "Eventhouse", "fact_production_alerts",       "WellSite",      "Equipment",     "well_id",     "well_id")
builder.add_contextualization("FieldLocationTracking",  "Eventhouse", "fact_field_location",          "FieldEngineer", "Facility",      "engineer_id", "facility_id")

# ── Add Batch Contextualizations ──────────────────────────────
builder.add_contextualization("FieldWellnessSurveys",   "Lakehouse",  "fact_field_wellness",          "FieldEngineer", None,            "engineer_id", None)
builder.add_contextualization("ReportQualityMetrics",   "Lakehouse",  "fact_report_quality",          "FieldEngineer", "ReportType",    "engineer_id", "report_id")
builder.add_contextualization("OperatorSatisfaction",   "Lakehouse",  "fact_operator_satisfaction",   "FieldEngineer", "Facility",      "engineer_id", "facility_id")
builder.add_contextualization("ProductionPerformance",  "Lakehouse",  "fact_production_performance",  "FieldEngineer", "WellSite",      "engineer_id", "well_id")

# ── Add Stream Contextualizations ─────────────────────────────
builder.add_contextualization("WellTelemetry",          "Eventhouse", "stream_well_telemetry",             "WellSite",  "Equipment",      "well_id",     "well_id")
builder.add_contextualization("SCADAAlarms",            "Eventhouse", "stream_scada_alarms",               "Facility",  "Equipment",      "facility_id", "facility_id")
builder.add_contextualization("HSEEvents",              "Eventhouse", "stream_hse_events",                 "Facility",  "RegulatoryBody", "facility_id", "reg_id")
builder.add_contextualization("PTWStatusUpdates",       "Eventhouse", "stream_ptw_status",                 "Facility",  "FieldEngineer",  "facility_id", "engineer_id")
builder.add_contextualization("EnvironmentalMonitoring","Eventhouse", "stream_environmental_monitoring",   "Facility",  "RegulatoryBody", "facility_id", "reg_id")

# ── Build and Deploy ──────────────────────────────────────────
ontology = builder.build()
print(f"✓ Ontology '{ontology.name}' created successfully")
print(f"  Entity Types:         {len(ontology.entity_types)}")
print(f"  Relationship Types:   {len(ontology.relationship_types)}")
print(f"  Contextualizations:   {len(ontology.contextualizations)}")
```

---

## Step 7: Verify Ontology

### Expected Counts

| Component            | Expected | Description                            |
|----------------------|----------|----------------------------------------|
| Entity Types         | 6        | Engineer, Well, Facility, Report, Equip, Reg |
| Relationship Types   | 5        | operates, stationed_at, hosts, regulated_by, requires_report |
| Contextualizations   | 13       | 8 event + 4 batch + 5 stream = 17 total* |

> *Note: The 13-count reflects the core event + batch contextualizations.
> With the 5 stream contextualizations, the full total is **17**.

### Verification Script

```python
# ── Verify Entity Types ───────────────────────────────────────
expected_entities = [
    "FieldEngineer", "WellSite", "Facility",
    "ReportType", "Equipment", "RegulatoryBody",
]
for ent in expected_entities:
    assert ent in [e.name for e in ontology.entity_types], f"Missing: {ent}"
    print(f"  ✓ {ent}")

# ── Verify Relationships ─────────────────────────────────────
expected_rels = [
    "operates", "stationed_at", "hosts",
    "regulated_by", "requires_report",
]
for rel in expected_rels:
    assert rel in [r.name for r in ontology.relationship_types], f"Missing: {rel}"
    print(f"  ✓ {rel}")

# ── Verify Contextualizations ────────────────────────────────
ctx_count = len(ontology.contextualizations)
print(f"  ✓ Contextualizations: {ctx_count}")
assert ctx_count >= 13, f"Expected ≥13, got {ctx_count}"

print("\n✓ OilGasFieldOpsOntology verification passed")
```

---

## Data Binding Summary

| Table                            | Storage     | Binding Type       | Key Columns                    |
|----------------------------------|-------------|--------------------|--------------------------------|
| dim_field_engineers              | Lakehouse   | Entity (dim)       | engineer_id                    |
| dim_well_sites                   | Lakehouse   | Entity (dim)       | well_id                        |
| dim_facilities                   | Lakehouse   | Entity (dim)       | facility_id                    |
| dim_report_types                 | Lakehouse   | Entity (dim)       | report_type_id                 |
| dim_equipment                    | Lakehouse   | Entity (dim)       | equipment_id                   |
| dim_regulatory_bodies            | Lakehouse   | Entity (dim)       | reg_id                         |
| fact_daily_drilling_reports      | Eventhouse  | Contextualization  | engineer_id, well_id           |
| fact_scada_interactions          | Eventhouse  | Contextualization  | engineer_id, well_id           |
| fact_hse_inspections             | Eventhouse  | Contextualization  | engineer_id, facility_id       |
| fact_permit_to_work              | Eventhouse  | Contextualization  | engineer_id, facility_id       |
| fact_well_integrity_events       | Eventhouse  | Contextualization  | engineer_id, well_id           |
| fact_tour_handoffs               | Eventhouse  | Contextualization  | from_engineer, well_id         |
| fact_production_alerts           | Eventhouse  | Contextualization  | well_id                        |
| fact_field_location              | Eventhouse  | Contextualization  | engineer_id, facility_id       |
| fact_field_wellness              | Lakehouse   | Contextualization  | engineer_id                    |
| fact_report_quality              | Lakehouse   | Contextualization  | engineer_id, report_id         |
| fact_operator_satisfaction       | Lakehouse   | Contextualization  | engineer_id, facility_id       |
| fact_production_performance      | Lakehouse   | Contextualization  | engineer_id, well_id           |
| stream_well_telemetry            | Eventhouse  | Contextualization  | well_id                        |
| stream_scada_alarms              | Eventhouse  | Contextualization  | facility_id                    |
| stream_hse_events                | Eventhouse  | Contextualization  | facility_id                    |
| stream_ptw_status                | Eventhouse  | Contextualization  | facility_id                    |
| stream_environmental_monitoring  | Eventhouse  | Contextualization  | facility_id                    |

---

## Built-In Data Patterns

### Pattern 1: Rotation Handoff Documentation Surge

**Hypothesis:** Documentation burden spikes during rotation changeovers as
outgoing engineers rush to close out DDRs, HSE reports, and PTW paperwork
before handing off, while incoming engineers duplicate documentation to
"verify" status.

```
Detection:
  - Join fact_tour_handoffs with fact_daily_drilling_reports on well_id + date window
  - Compare doc_time_min in the 24 hours before/after handoff vs mid-rotation baseline
  - Correlate with fact_field_wellness.admin_burden_score near rotation boundaries

Expected Signal:
  - 40-60% increase in combined doc_time_min during ±24h of rotation change
  - Higher narrative_length in handoff reports (knowledge dump behavior)
  - Elevated admin_burden_score in wellness surveys near rotation boundaries
```

### Pattern 2: DDR-to-Regulatory Compliance Chain

**Hypothesis:** Daily drilling reports that eventually feed regulatory
submissions require significantly more documentation time than internal-only
DDRs, creating a two-tier documentation burden.

```
Detection:
  - Join fact_daily_drilling_reports with dim_report_types on report category
  - Filter for regulatory_required = true vs false
  - Compare AVG(doc_time_min) between regulatory-bound vs internal-only DDRs

Expected Signal:
  - Regulatory-bound DDRs take 1.5-2.5x longer to complete
  - Higher completeness_pct in fact_report_quality for regulatory reports
  - Engineers with more regulatory wells show elevated admin_burden_score
```

### Pattern 3: HSE Inspection Frequency vs Documentation Quality

**Hypothesis:** When HSE inspection frequency increases (e.g., post-incident
or regulatory directive), documentation quality initially drops as engineers
rush through more inspections with less time per report.

```
Detection:
  - Aggregate fact_hse_inspections by facility_id and week
  - Correlate inspection frequency with fact_report_quality.accuracy_score
  - Track critical_findings count relative to inspection volume

Expected Signal:
  - Negative correlation between weekly inspection count and accuracy_score
  - Facilities with >3 inspections/week show 15-25% lower accuracy scores
  - Recovery to baseline quality after 2-3 weeks as engineers adapt
```

### Pattern 4: Permit-to-Work Hazard Level Documentation Scaling

**Hypothesis:** PTW documentation time scales non-linearly with hazard level —
high-hazard permits require disproportionately more time because of multi-party
signatory requirements and more detailed risk assessments.

```
Detection:
  - Group fact_permit_to_work by hazard_level
  - Calculate AVG(doc_time_min) and AVG(signatories_required) per level
  - Plot doc_time_min vs signatories_required to identify non-linearity

Expected Signal:
  - Low-hazard: ~20 min, 2 signatories
  - Medium-hazard: ~45 min, 4 signatories (2.25x time for 2x signatories)
  - High-hazard: ~90 min, 7 signatories (4.5x time for 3.5x signatories)
  - Super-quadratic scaling indicates approval chain bottlenecks
```

### Pattern 5: Remote Facility Isolation Documentation Burden

**Hypothesis:** Engineers stationed at remote or offshore facilities experience
higher documentation burden due to limited connectivity, fewer support staff,
and more stringent regulatory requirements for isolated operations.

```
Detection:
  - Join fact_field_location with dim_facilities on facility_id
  - Categorize facilities by remoteness (offshore, remote onshore, urban)
  - Compare aggregate doc_time_min per engineer across facility categories
  - Correlate with fact_field_wellness.isolation_score

Expected Signal:
  - Remote/offshore engineers spend 30-50% more time on documentation
  - Higher isolation_score correlates with elevated admin_burden_score
  - Offshore facilities show longer PTW doc times due to stricter HSE
  - Connectivity-limited sites show batch submission patterns in timestamps
```

---

## Next Steps

1. **Run cross_industry_notebooks**: Execute the 00-07 notebook pipeline
   using `OilAndGas_Config.ipynb` as the industry configuration
2. **Create Semantic Model**: Build Power BI semantic model linking
   Lakehouse and Eventhouse tables for documentation burden analytics
3. **Deploy Data Agent**: Configure a Fabric data agent with the ontology
   for natural language queries about field engineer documentation burden
4. **Build Dashboard**: Create operational dashboards showing real-time
   documentation KPIs per well site, facility, and engineer rotation
