# Media Content Operations — Ontology Package Guide

## Overview

This guide provides step-by-step instructions for creating the **MediaContentOpsOntology** in Microsoft Fabric Real-Time Intelligence using the `fabricontology` Python package.

---

## Prerequisites

| Fabric Item       | Name / Notes                                       |
|-------------------|----------------------------------------------------|
| **Lakehouse**     | `MediaLakehouse` — stores dimension + batch fact tables   |
| **Eventhouse**    | `MediaEventhouse` — stores event fact + stream tables     |
| **KQL Database**  | `MediaKQLDB` — inside Eventhouse                          |
| **Notebook**      | Fabric notebook with Spark + KQL access                   |

> Upload all CSV files from `datasets/media_content_operations/data/` to Lakehouse **Files** section before starting.

---

## Step 1: Prepare Lakehouse Delta Tables

Load dimension and batch fact CSVs into Lakehouse Delta tables:

```python
# List of dimension + batch fact tables to load into Lakehouse
lakehouse_tables = [
    "dim_producers",
    "dim_shows",
    "dim_networks",
    "dim_content_task_types",
    "dim_rights_holders",
    "dim_platforms",
    "fact_crew_wellness",
    "fact_content_quality",
    "fact_client_satisfaction",
    "fact_production_performance"
]

base_path = "Files/media_content_operations/data"

for table_name in lakehouse_tables:
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{base_path}/{table_name}.csv")
    df.write.mode("overwrite").format("delta").saveAsTable(table_name)
    print(f"✅ Loaded {table_name}: {df.count()} rows")
```

---

## Step 2: Prepare Eventhouse KQL Tables

Ingest event fact and streaming CSVs into Eventhouse KQL tables:

```python
# Event fact + streaming tables for Eventhouse
eventhouse_tables = [
    "fact_content_doc_events",
    "fact_mam_interactions",
    "fact_metadata_entries",
    "fact_rights_clearance",
    "fact_content_handoffs",
    "fact_approval_workflows",
    "fact_regulatory_reviews",
    "fact_delivery_alerts",
    "stream_mam_activity",
    "stream_delivery_tracking",
    "stream_qc_results",
    "stream_rights_status",
    "stream_audience_metrics"
]

kql_database = "MediaKQLDB"
base_path = "Files/media_content_operations/data"

for table_name in eventhouse_tables:
    df = spark.read.option("header", True).option("inferSchema", True) \
        .csv(f"{base_path}/{table_name}.csv")
    
    # Write to KQL Database
    df.write \
        .format("com.microsoft.kusto.spark.synapse.datasource") \
        .option("kustoCluster", kql_database) \
        .option("kustoDatabase", kql_database) \
        .option("kustoTable", table_name.replace("fact_", "").replace("stream_", "")) \
        .option("tableCreateOptions", "CreateIfNotExist") \
        .mode("Append") \
        .save()
    print(f"✅ Ingested {table_name}: {df.count()} rows")
```

---

## Step 3: Entity Type Definitions

### Producer Entity
```json
{
  "entityTypeName": "Producer",
  "tableName": "dim_producers",
  "storageType": "Lakehouse",
  "primaryKey": "producer_id",
  "displayName": "name",
  "properties": [
    { "name": "producer_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "role", "type": "String" },
    { "name": "department", "type": "String" },
    { "name": "shows_assigned", "type": "Integer" },
    { "name": "hire_date", "type": "String" },
    { "name": "specialization", "type": "String" },
    { "name": "email", "type": "String" },
    { "name": "location", "type": "String" },
    { "name": "seniority_level", "type": "String" },
    { "name": "weekly_hours", "type": "Integer" },
    { "name": "certification", "type": "String" }
  ]
}
```

### Show Entity
```json
{
  "entityTypeName": "Show",
  "tableName": "dim_shows",
  "storageType": "Lakehouse",
  "primaryKey": "show_id",
  "displayName": "name",
  "properties": [
    { "name": "show_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "genre", "type": "String" },
    { "name": "network", "type": "String" },
    { "name": "platform", "type": "String" },
    { "name": "season", "type": "Integer" },
    { "name": "episode_count", "type": "Integer" },
    { "name": "production_budget", "type": "Real" },
    { "name": "show_type", "type": "String" },
    { "name": "status", "type": "String" },
    { "name": "premiere_date", "type": "String" },
    { "name": "content_rating", "type": "String" }
  ]
}
```

### Network Entity
```json
{
  "entityTypeName": "Network",
  "tableName": "dim_networks",
  "storageType": "Lakehouse",
  "primaryKey": "network_id",
  "displayName": "name",
  "properties": [
    { "name": "network_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "type", "type": "String" },
    { "name": "platform_count", "type": "Integer" },
    { "name": "content_hours_per_week", "type": "Integer" },
    { "name": "region", "type": "String" }
  ]
}
```

### ContentTaskType Entity
```json
{
  "entityTypeName": "ContentTaskType",
  "tableName": "dim_content_task_types",
  "storageType": "Lakehouse",
  "primaryKey": "task_type_id",
  "displayName": "name",
  "properties": [
    { "name": "task_type_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "category", "type": "String" },
    { "name": "avg_duration_min", "type": "Integer" },
    { "name": "requires_approval", "type": "String" },
    { "name": "regulatory_flag", "type": "String" }
  ]
}
```

### RightsHolder Entity
```json
{
  "entityTypeName": "RightsHolder",
  "tableName": "dim_rights_holders",
  "storageType": "Lakehouse",
  "primaryKey": "holder_id",
  "displayName": "name",
  "properties": [
    { "name": "holder_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "type", "type": "String" },
    { "name": "territory", "type": "String" },
    { "name": "content_count", "type": "Integer" },
    { "name": "avg_clearance_days", "type": "Real" },
    { "name": "contact_email", "type": "String" },
    { "name": "preferred_method", "type": "String" },
    { "name": "contract_status", "type": "String" },
    { "name": "response_reliability", "type": "String" }
  ]
}
```

### Platform Entity
```json
{
  "entityTypeName": "Platform",
  "tableName": "dim_platforms",
  "storageType": "Lakehouse",
  "primaryKey": "platform_id",
  "displayName": "name",
  "properties": [
    { "name": "platform_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "type", "type": "String" },
    { "name": "spec_requirements", "type": "String" },
    { "name": "delivery_format", "type": "String" },
    { "name": "region", "type": "String" },
    { "name": "resolution", "type": "String" },
    { "name": "audio_format", "type": "String" },
    { "name": "subtitle_required", "type": "String" },
    { "name": "turnaround_sla_hours", "type": "Real" }
  ]
}
```

---

## Step 4: Relationship Type Definitions

```json
[
  {
    "relationshipTypeName": "produces",
    "sourceEntityType": "Producer",
    "sourceProperty": "producer_id",
    "targetEntityType": "Show",
    "targetProperty": "show_id"
  },
  {
    "relationshipTypeName": "airs_on",
    "sourceEntityType": "Show",
    "sourceProperty": "network",
    "targetEntityType": "Network",
    "targetProperty": "name"
  },
  {
    "relationshipTypeName": "delivers_to",
    "sourceEntityType": "Show",
    "sourceProperty": "show_id",
    "targetEntityType": "Platform",
    "targetProperty": "platform_id"
  },
  {
    "relationshipTypeName": "clears_rights_with",
    "sourceEntityType": "Show",
    "sourceProperty": "show_id",
    "targetEntityType": "RightsHolder",
    "targetProperty": "holder_id"
  },
  {
    "relationshipTypeName": "categorized_by",
    "sourceEntityType": "ContentDocEvent",
    "sourceProperty": "task_type",
    "targetEntityType": "ContentTaskType",
    "targetProperty": "task_type_id"
  }
]
```

---

## Step 5: Contextualization Definitions

### ContentDocEvent Contextualization
```json
{
  "contextualizationName": "ContentDocEvent",
  "tableName": "content_doc_events",
  "storageType": "Eventhouse",
  "timestampProperty": "date",
  "entityBindings": [
    { "entityTypeName": "Producer", "contextualizationProperty": "producer_id", "entityProperty": "producer_id" },
    { "entityTypeName": "Show", "contextualizationProperty": "show_id", "entityProperty": "show_id" },
    { "entityTypeName": "ContentTaskType", "contextualizationProperty": "task_type", "entityProperty": "task_type_id" }
  ]
}
```

### MAMInteraction Contextualization
```json
{
  "contextualizationName": "MAMInteraction",
  "tableName": "mam_interactions",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Producer", "contextualizationProperty": "producer_id", "entityProperty": "producer_id" }
  ]
}
```

### MetadataEntry Contextualization
```json
{
  "contextualizationName": "MetadataEntry",
  "tableName": "metadata_entries",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Producer", "contextualizationProperty": "producer_id", "entityProperty": "producer_id" }
  ]
}
```

### RightsClearance Contextualization
```json
{
  "contextualizationName": "RightsClearance",
  "tableName": "rights_clearance",
  "storageType": "Eventhouse",
  "timestampProperty": "date",
  "entityBindings": [
    { "entityTypeName": "Producer", "contextualizationProperty": "rights_manager_id", "entityProperty": "producer_id" },
    { "entityTypeName": "Show", "contextualizationProperty": "show_id", "entityProperty": "show_id" },
    { "entityTypeName": "RightsHolder", "contextualizationProperty": "holder_id", "entityProperty": "holder_id" }
  ]
}
```

### ContentHandoff Contextualization
```json
{
  "contextualizationName": "ContentHandoff",
  "tableName": "content_handoffs",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Show", "contextualizationProperty": "show_id", "entityProperty": "show_id" }
  ]
}
```

### ApprovalWorkflow Contextualization
```json
{
  "contextualizationName": "ApprovalWorkflow",
  "tableName": "approval_workflows",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Show", "contextualizationProperty": "show_id", "entityProperty": "show_id" },
    { "entityTypeName": "Producer", "contextualizationProperty": "producer_id", "entityProperty": "producer_id" }
  ]
}
```

### RegulatoryReview Contextualization
```json
{
  "contextualizationName": "RegulatoryReview",
  "tableName": "regulatory_reviews",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Producer", "contextualizationProperty": "producer_id", "entityProperty": "producer_id" }
  ]
}
```

### DeliveryAlert Contextualization
```json
{
  "contextualizationName": "DeliveryAlert",
  "tableName": "delivery_alerts",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Show", "contextualizationProperty": "show_id", "entityProperty": "show_id" },
    { "entityTypeName": "Platform", "contextualizationProperty": "platform_id", "entityProperty": "platform_id" }
  ]
}
```

### MAMActivity Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "MAMActivity",
  "tableName": "mam_activity",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Producer", "contextualizationProperty": "producer_id", "entityProperty": "producer_id" }
  ]
}
```

### DeliveryTracking Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "DeliveryTracking",
  "tableName": "delivery_tracking",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Show", "contextualizationProperty": "show_id", "entityProperty": "show_id" },
    { "entityTypeName": "Platform", "contextualizationProperty": "platform_id", "entityProperty": "platform_id" }
  ]
}
```

### QCResult Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "QCResult",
  "tableName": "qc_results",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": []
}
```

### RightsStatus Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "RightsStatus",
  "tableName": "rights_status",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": []
}
```

### AudienceMetric Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "AudienceMetric",
  "tableName": "audience_metrics",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Show", "contextualizationProperty": "show_id", "entityProperty": "show_id" },
    { "entityTypeName": "Platform", "contextualizationProperty": "platform_id", "entityProperty": "platform_id" }
  ]
}
```

---

## Step 6: Create the Ontology

```python
from fabricontology import FabricOntologyManager

# Initialize the ontology manager
manager = FabricOntologyManager()

# Create the ontology
ontology = manager.create_ontology("MediaContentOpsOntology")

# --- Add Entity Types ---
producer = ontology.add_entity_type("Producer", "dim_producers", "Lakehouse", "producer_id")
producer.add_property("producer_id", "String", is_primary_key=True)
producer.add_property("name", "String")
producer.add_property("role", "String")
producer.add_property("department", "String")
producer.add_property("shows_assigned", "Integer")
producer.add_property("hire_date", "String")
producer.add_property("specialization", "String")
producer.add_property("email", "String")
producer.add_property("location", "String")
producer.add_property("seniority_level", "String")
producer.add_property("weekly_hours", "Integer")
producer.add_property("certification", "String")

show = ontology.add_entity_type("Show", "dim_shows", "Lakehouse", "show_id")
show.add_property("show_id", "String", is_primary_key=True)
show.add_property("name", "String")
show.add_property("genre", "String")
show.add_property("network", "String")
show.add_property("platform", "String")
show.add_property("season", "Integer")
show.add_property("episode_count", "Integer")
show.add_property("production_budget", "Real")
show.add_property("show_type", "String")
show.add_property("status", "String")
show.add_property("premiere_date", "String")
show.add_property("content_rating", "String")

network = ontology.add_entity_type("Network", "dim_networks", "Lakehouse", "network_id")
network.add_property("network_id", "String", is_primary_key=True)
network.add_property("name", "String")
network.add_property("type", "String")
network.add_property("platform_count", "Integer")
network.add_property("content_hours_per_week", "Integer")
network.add_property("region", "String")

task_type = ontology.add_entity_type("ContentTaskType", "dim_content_task_types", "Lakehouse", "task_type_id")
task_type.add_property("task_type_id", "String", is_primary_key=True)
task_type.add_property("name", "String")
task_type.add_property("category", "String")
task_type.add_property("avg_duration_min", "Integer")
task_type.add_property("requires_approval", "String")
task_type.add_property("regulatory_flag", "String")

rights_holder = ontology.add_entity_type("RightsHolder", "dim_rights_holders", "Lakehouse", "holder_id")
rights_holder.add_property("holder_id", "String", is_primary_key=True)
rights_holder.add_property("name", "String")
rights_holder.add_property("type", "String")
rights_holder.add_property("territory", "String")
rights_holder.add_property("content_count", "Integer")
rights_holder.add_property("avg_clearance_days", "Real")
rights_holder.add_property("contact_email", "String")
rights_holder.add_property("preferred_method", "String")
rights_holder.add_property("contract_status", "String")
rights_holder.add_property("response_reliability", "String")

platform = ontology.add_entity_type("Platform", "dim_platforms", "Lakehouse", "platform_id")
platform.add_property("platform_id", "String", is_primary_key=True)
platform.add_property("name", "String")
platform.add_property("type", "String")
platform.add_property("spec_requirements", "String")
platform.add_property("delivery_format", "String")
platform.add_property("region", "String")
platform.add_property("resolution", "String")
platform.add_property("audio_format", "String")
platform.add_property("subtitle_required", "String")
platform.add_property("turnaround_sla_hours", "Real")

# --- Add Relationship Types ---
ontology.add_relationship_type("produces", "Producer", "producer_id", "Show", "show_id")
ontology.add_relationship_type("airs_on", "Show", "network", "Network", "name")
ontology.add_relationship_type("delivers_to", "Show", "show_id", "Platform", "platform_id")
ontology.add_relationship_type("clears_rights_with", "Show", "show_id", "RightsHolder", "holder_id")
ontology.add_relationship_type("categorized_by", "ContentDocEvent", "task_type", "ContentTaskType", "task_type_id")

# --- Add Contextualizations ---
ctx_doc = ontology.add_contextualization("ContentDocEvent", "content_doc_events", "Eventhouse", "date")
ctx_doc.add_entity_binding("Producer", "producer_id", "producer_id")
ctx_doc.add_entity_binding("Show", "show_id", "show_id")
ctx_doc.add_entity_binding("ContentTaskType", "task_type", "task_type_id")

ctx_mam = ontology.add_contextualization("MAMInteraction", "mam_interactions", "Eventhouse", "timestamp")
ctx_mam.add_entity_binding("Producer", "producer_id", "producer_id")

ctx_meta = ontology.add_contextualization("MetadataEntry", "metadata_entries", "Eventhouse", "timestamp")
ctx_meta.add_entity_binding("Producer", "producer_id", "producer_id")

ctx_rights = ontology.add_contextualization("RightsClearance", "rights_clearance", "Eventhouse", "date")
ctx_rights.add_entity_binding("Producer", "rights_manager_id", "producer_id")
ctx_rights.add_entity_binding("Show", "show_id", "show_id")
ctx_rights.add_entity_binding("RightsHolder", "holder_id", "holder_id")

ctx_handoff = ontology.add_contextualization("ContentHandoff", "content_handoffs", "Eventhouse", "timestamp")
ctx_handoff.add_entity_binding("Show", "show_id", "show_id")

ctx_approval = ontology.add_contextualization("ApprovalWorkflow", "approval_workflows", "Eventhouse", "timestamp")
ctx_approval.add_entity_binding("Show", "show_id", "show_id")
ctx_approval.add_entity_binding("Producer", "producer_id", "producer_id")

ctx_reg = ontology.add_contextualization("RegulatoryReview", "regulatory_reviews", "Eventhouse", "timestamp")
ctx_reg.add_entity_binding("Producer", "producer_id", "producer_id")

ctx_delivery = ontology.add_contextualization("DeliveryAlert", "delivery_alerts", "Eventhouse", "timestamp")
ctx_delivery.add_entity_binding("Show", "show_id", "show_id")
ctx_delivery.add_entity_binding("Platform", "platform_id", "platform_id")

ctx_mam_rt = ontology.add_contextualization("MAMActivity", "mam_activity", "Eventhouse", "timestamp")
ctx_mam_rt.add_entity_binding("Producer", "producer_id", "producer_id")

ctx_del_track = ontology.add_contextualization("DeliveryTracking", "delivery_tracking", "Eventhouse", "timestamp")
ctx_del_track.add_entity_binding("Show", "show_id", "show_id")
ctx_del_track.add_entity_binding("Platform", "platform_id", "platform_id")

ctx_qc = ontology.add_contextualization("QCResult", "qc_results", "Eventhouse", "timestamp")

ctx_rights_rt = ontology.add_contextualization("RightsStatus", "rights_status", "Eventhouse", "timestamp")

ctx_audience = ontology.add_contextualization("AudienceMetric", "audience_metrics", "Eventhouse", "timestamp")
ctx_audience.add_entity_binding("Show", "show_id", "show_id")
ctx_audience.add_entity_binding("Platform", "platform_id", "platform_id")

# Save / publish
ontology.save()
print("✅ MediaContentOpsOntology created successfully!")
```

---

## Step 7: Verify the Ontology

1. Open **Fabric Portal** → navigate to your workspace
2. Open the **Real-Time Intelligence** experience
3. Find **MediaContentOpsOntology** in the ontology list
4. Verify:
   - **6 Entity Types** displayed (Producer, Show, Network, ContentTaskType, RightsHolder, Platform)
   - **5 Relationship Types** connecting entities
   - **13 Contextualizations** binding events to entities
   - Data bindings show Lakehouse and Eventhouse connections with live data

---

## Data Binding Summary

| Binding Target            | Storage      | Entity / CTX Bindings                              |
|---------------------------|--------------|-----------------------------------------------------|
| dim_producers             | Lakehouse    | Producer entity                                     |
| dim_shows                 | Lakehouse    | Show entity                                         |
| dim_networks              | Lakehouse    | Network entity                                      |
| dim_content_task_types    | Lakehouse    | ContentTaskType entity                              |
| dim_rights_holders        | Lakehouse    | RightsHolder entity                                 |
| dim_platforms             | Lakehouse    | Platform entity                                     |
| fact_crew_wellness        | Lakehouse    | Wellness analytics (batch)                          |
| fact_content_quality      | Lakehouse    | Quality analytics (batch)                           |
| fact_client_satisfaction  | Lakehouse    | Satisfaction analytics (batch)                      |
| fact_production_performance | Lakehouse  | Performance analytics (batch)                       |
| content_doc_events        | Eventhouse   | CTX: Producer, Show, ContentTaskType                |
| mam_interactions          | Eventhouse   | CTX: Producer                                       |
| metadata_entries          | Eventhouse   | CTX: Producer                                       |
| rights_clearance          | Eventhouse   | CTX: Producer, Show, RightsHolder                   |
| content_handoffs          | Eventhouse   | CTX: Show                                           |
| approval_workflows        | Eventhouse   | CTX: Show, Producer                                 |
| regulatory_reviews        | Eventhouse   | CTX: Producer                                       |
| delivery_alerts           | Eventhouse   | CTX: Show, Platform                                 |
| mam_activity              | Eventhouse   | CTX: Producer                                       |
| delivery_tracking         | Eventhouse   | CTX: Show, Platform                                 |
| qc_results                | Eventhouse   | CTX: (asset-level)                                  |
| rights_status             | Eventhouse   | CTX: (clearance-level)                              |
| audience_metrics          | Eventhouse   | CTX: Show, Platform                                 |

---

## Built-In Data Patterns for Demo

The media content sample data includes intentional correlation patterns to showcase documentation burden insights:

1. **Rights clearance bottleneck** — Shows SHW-003, SHW-007, SHW-012 have 3× documentation time due to multi-territory music clearance cycles with low-reliability rights holders
2. **Metadata entry burden spike** — Producers handling unscripted content average 2× manual metadata entry time vs. scripted show producers due to unpredictable asset volumes
3. **Delivery rejection cascade** — Platform spec mismatches on 4K HDR deliveries cause rejection → re-QC → re-package → re-deliver cycles that triple documentation overhead
4. **Approval workflow stall** — Regulatory reviews for children's content (COPPA) create 5-day approval queues, during which producers accumulate documentation backlog on other shows
5. **Post-production handoff gap** — Content handoffs from editing to finishing roles show 40% longer documentation time when handoff notes are under 200 characters, indicating undocumented tribal knowledge
