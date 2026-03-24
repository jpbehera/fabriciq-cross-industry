# Telecom Network Operations — Ontology Package Guide

## Overview

This guide provides step-by-step instructions for creating the **TelecomNetworkOpsOntology** in Microsoft Fabric Real-Time Intelligence using the `fabricontology` Python package.

---

## Prerequisites

| Fabric Item       | Name / Notes                                       |
|-------------------|----------------------------------------------------|
| **Lakehouse**     | `TelecomLakehouse` — stores dimension + batch fact tables |
| **Eventhouse**    | `TelecomEventhouse` — stores event fact + stream tables   |
| **KQL Database**  | `TelecomKQLDB` — inside Eventhouse                        |
| **Notebook**      | Fabric notebook with Spark + KQL access                   |

> Upload all CSV files from `datasets/telecom_network_operations/data/` to Lakehouse **Files** section before starting.

---

## Step 1: Prepare Lakehouse Delta Tables

Load dimension and batch fact CSVs into Lakehouse Delta tables:

```python
# List of dimension + batch fact tables to load into Lakehouse
lakehouse_tables = [
    "dim_engineers",
    "dim_enterprise_customers",
    "dim_equipment",
    "dim_network_segments",
    "dim_service_areas",
    "dim_ticket_types",
    "fact_technician_wellness",
    "fact_ticket_quality",
    "fact_customer_satisfaction",
    "fact_network_performance",
    "fact_field_dispatches",
    "fact_trouble_tickets"
]

base_path = "Files/telecom_network_operations/data"

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
    "fact_nms_interactions",
    "fact_outage_events",
    "fact_rca_documents",
    "fact_ticket_escalations",
    "fact_sla_alerts",
    "fact_field_location",
    "stream_network_alarms",
    "stream_ticket_activity",
    "stream_field_dispatch",
    "stream_performance_metrics",
    "stream_customer_impact"
]

kql_database = "TelecomKQLDB"
base_path = "Files/telecom_network_operations/data"

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

### Engineer Entity
```json
{
  "entityTypeName": "Engineer",
  "tableName": "dim_engineers",
  "storageType": "Lakehouse",
  "primaryKey": "engineer_id",
  "displayName": "engineer_id",
  "properties": [
    { "name": "engineer_id", "type": "String", "isPrimaryKey": true },
    { "name": "first_name", "type": "String" },
    { "name": "last_name", "type": "String" },
    { "name": "role", "type": "String" },
    { "name": "tier", "type": "String" },
    { "name": "certifications", "type": "String" },
    { "name": "region", "type": "String" },
    { "name": "hire_date", "type": "String" },
    { "name": "on_call_schedule", "type": "String" },
    { "name": "specialty", "type": "String" },
    { "name": "email", "type": "String" },
    { "name": "years_experience", "type": "Integer" }
  ]
}
```

### EnterpriseCustomer Entity
```json
{
  "entityTypeName": "EnterpriseCustomer",
  "tableName": "dim_enterprise_customers",
  "storageType": "Lakehouse",
  "primaryKey": "customer_id",
  "displayName": "name",
  "properties": [
    { "name": "customer_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "industry", "type": "String" },
    { "name": "contract_value", "type": "Real" },
    { "name": "sla_tier", "type": "String" },
    { "name": "circuit_count", "type": "Integer" },
    { "name": "region", "type": "String" },
    { "name": "contract_start", "type": "String" },
    { "name": "contract_end", "type": "String" },
    { "name": "account_manager", "type": "String" }
  ]
}
```

### Equipment Entity
```json
{
  "entityTypeName": "Equipment",
  "tableName": "dim_equipment",
  "storageType": "Lakehouse",
  "primaryKey": "equipment_id",
  "displayName": "name",
  "properties": [
    { "name": "equipment_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "vendor", "type": "String" },
    { "name": "model", "type": "String" },
    { "name": "site_id", "type": "String" },
    { "name": "site_type", "type": "String" },
    { "name": "region", "type": "String" },
    { "name": "install_date", "type": "String" },
    { "name": "firmware_version", "type": "String" },
    { "name": "criticality", "type": "String" },
    { "name": "status", "type": "String" }
  ]
}
```

### NetworkSegment Entity
```json
{
  "entityTypeName": "NetworkSegment",
  "tableName": "dim_network_segments",
  "storageType": "Lakehouse",
  "primaryKey": "segment_id",
  "displayName": "name",
  "properties": [
    { "name": "segment_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "type", "type": "String" },
    { "name": "technology", "type": "String" },
    { "name": "region", "type": "String" },
    { "name": "node_count", "type": "Integer" },
    { "name": "circuit_count", "type": "Integer" },
    { "name": "capacity_gbps", "type": "Real" },
    { "name": "redundancy_level", "type": "String" }
  ]
}
```

### ServiceArea Entity
```json
{
  "entityTypeName": "ServiceArea",
  "tableName": "dim_service_areas",
  "storageType": "Lakehouse",
  "primaryKey": "area_id",
  "displayName": "name",
  "properties": [
    { "name": "area_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "region", "type": "String" },
    { "name": "customer_count", "type": "Integer" },
    { "name": "technology", "type": "String" },
    { "name": "capacity_gbps", "type": "Real" },
    { "name": "last_upgrade", "type": "String" },
    { "name": "pop_count", "type": "Integer" },
    { "name": "fiber_miles", "type": "Real" }
  ]
}
```

### TicketType Entity
```json
{
  "entityTypeName": "TicketType",
  "tableName": "dim_ticket_types",
  "storageType": "Lakehouse",
  "primaryKey": "ticket_type_id",
  "displayName": "name",
  "properties": [
    { "name": "ticket_type_id", "type": "String", "isPrimaryKey": true },
    { "name": "name", "type": "String" },
    { "name": "category", "type": "String" },
    { "name": "priority_levels", "type": "String" },
    { "name": "avg_resolution_min", "type": "Integer" },
    { "name": "sla_target_hours", "type": "Real" },
    { "name": "documentation_template", "type": "String" },
    { "name": "requires_rca", "type": "String" }
  ]
}
```

---

## Step 4: Relationship Type Definitions

```json
[
  {
    "relationshipTypeName": "operates_in",
    "sourceEntityType": "Engineer",
    "sourceProperty": "region",
    "targetEntityType": "ServiceArea",
    "targetProperty": "region"
  },
  {
    "relationshipTypeName": "manages",
    "sourceEntityType": "Engineer",
    "sourceProperty": "engineer_id",
    "targetEntityType": "NetworkSegment",
    "targetProperty": "segment_id"
  },
  {
    "relationshipTypeName": "serves",
    "sourceEntityType": "ServiceArea",
    "sourceProperty": "region",
    "targetEntityType": "EnterpriseCustomer",
    "targetProperty": "region"
  },
  {
    "relationshipTypeName": "hosts",
    "sourceEntityType": "NetworkSegment",
    "sourceProperty": "segment_id",
    "targetEntityType": "Equipment",
    "targetProperty": "site_id"
  },
  {
    "relationshipTypeName": "monitors",
    "sourceEntityType": "Engineer",
    "sourceProperty": "engineer_id",
    "targetEntityType": "Equipment",
    "targetProperty": "equipment_id"
  }
]
```

---

## Step 5: Contextualization Definitions

### TroubleTicket Contextualization
```json
{
  "contextualizationName": "TroubleTicket",
  "tableName": "fact_trouble_tickets",
  "storageType": "Lakehouse",
  "timestampProperty": "ticket_date",
  "entityBindings": [
    { "entityTypeName": "Engineer", "contextualizationProperty": "engineer_id", "entityProperty": "engineer_id" },
    { "entityTypeName": "TicketType", "contextualizationProperty": "ticket_type_id", "entityProperty": "ticket_type_id" },
    { "entityTypeName": "NetworkSegment", "contextualizationProperty": "segment_id", "entityProperty": "segment_id" },
    { "entityTypeName": "Equipment", "contextualizationProperty": "equipment_id", "entityProperty": "equipment_id" },
    { "entityTypeName": "ServiceArea", "contextualizationProperty": "area_id", "entityProperty": "area_id" }
  ]
}
```

### NMSInteraction Contextualization
```json
{
  "contextualizationName": "NMSInteraction",
  "tableName": "nms_interactions",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Engineer", "contextualizationProperty": "engineer_id", "entityProperty": "engineer_id" }
  ]
}
```

### OutageEvent Contextualization
```json
{
  "contextualizationName": "OutageEvent",
  "tableName": "outage_events",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "NetworkSegment", "contextualizationProperty": "segment_id", "entityProperty": "segment_id" },
    { "entityTypeName": "Equipment", "contextualizationProperty": "equipment_id", "entityProperty": "equipment_id" },
    { "entityTypeName": "ServiceArea", "contextualizationProperty": "area_id", "entityProperty": "area_id" }
  ]
}
```

### RCADocument Contextualization
```json
{
  "contextualizationName": "RCADocument",
  "tableName": "rca_documents",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Engineer", "contextualizationProperty": "engineer_id", "entityProperty": "engineer_id" }
  ]
}
```

### TicketEscalation Contextualization
```json
{
  "contextualizationName": "TicketEscalation",
  "tableName": "ticket_escalations",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Engineer", "contextualizationProperty": "engineer_from", "entityProperty": "engineer_id" }
  ]
}
```

### SLAAlert Contextualization
```json
{
  "contextualizationName": "SLAAlert",
  "tableName": "sla_alerts",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "EnterpriseCustomer", "contextualizationProperty": "customer_id", "entityProperty": "customer_id" },
    { "entityTypeName": "ServiceArea", "contextualizationProperty": "area_id", "entityProperty": "area_id" }
  ]
}
```

### FieldLocation Contextualization
```json
{
  "contextualizationName": "FieldLocation",
  "tableName": "field_location",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Engineer", "contextualizationProperty": "technician_id", "entityProperty": "engineer_id" }
  ]
}
```

### NetworkAlarm Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "NetworkAlarm",
  "tableName": "network_alarms",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Equipment", "contextualizationProperty": "equipment_id", "entityProperty": "equipment_id" }
  ]
}
```

### TicketActivity Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "TicketActivity",
  "tableName": "ticket_activity",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Engineer", "contextualizationProperty": "engineer_id", "entityProperty": "engineer_id" }
  ]
}
```

### FieldDispatch Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "FieldDispatch",
  "tableName": "field_dispatch",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Engineer", "contextualizationProperty": "technician_id", "entityProperty": "engineer_id" }
  ]
}
```

### PerformanceMetric Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "PerformanceMetric",
  "tableName": "performance_metrics",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "Equipment", "contextualizationProperty": "equipment_id", "entityProperty": "equipment_id" }
  ]
}
```

### CustomerImpact Contextualization (Real-Time Stream)
```json
{
  "contextualizationName": "CustomerImpact",
  "tableName": "customer_impact",
  "storageType": "Eventhouse",
  "timestampProperty": "timestamp",
  "entityBindings": [
    { "entityTypeName": "EnterpriseCustomer", "contextualizationProperty": "customer_id", "entityProperty": "customer_id" }
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
ontology = manager.create_ontology("TelecomNetworkOpsOntology")

# --- Add Entity Types ---
engineer = ontology.add_entity_type("Engineer", "dim_engineers", "Lakehouse", "engineer_id")
engineer.add_property("engineer_id", "String", is_primary_key=True)
engineer.add_property("first_name", "String")
engineer.add_property("last_name", "String")
engineer.add_property("role", "String")
engineer.add_property("tier", "String")
engineer.add_property("certifications", "String")
engineer.add_property("region", "String")
engineer.add_property("hire_date", "String")
engineer.add_property("on_call_schedule", "String")
engineer.add_property("specialty", "String")
engineer.add_property("email", "String")
engineer.add_property("years_experience", "Integer")

customer = ontology.add_entity_type("EnterpriseCustomer", "dim_enterprise_customers", "Lakehouse", "customer_id")
customer.add_property("customer_id", "String", is_primary_key=True)
customer.add_property("name", "String")
customer.add_property("industry", "String")
customer.add_property("contract_value", "Real")
customer.add_property("sla_tier", "String")
customer.add_property("circuit_count", "Integer")
customer.add_property("region", "String")
customer.add_property("contract_start", "String")
customer.add_property("contract_end", "String")
customer.add_property("account_manager", "String")

equipment = ontology.add_entity_type("Equipment", "dim_equipment", "Lakehouse", "equipment_id")
equipment.add_property("equipment_id", "String", is_primary_key=True)
equipment.add_property("name", "String")
equipment.add_property("vendor", "String")
equipment.add_property("model", "String")
equipment.add_property("site_id", "String")
equipment.add_property("site_type", "String")
equipment.add_property("region", "String")
equipment.add_property("install_date", "String")
equipment.add_property("firmware_version", "String")
equipment.add_property("criticality", "String")
equipment.add_property("status", "String")

segment = ontology.add_entity_type("NetworkSegment", "dim_network_segments", "Lakehouse", "segment_id")
segment.add_property("segment_id", "String", is_primary_key=True)
segment.add_property("name", "String")
segment.add_property("type", "String")
segment.add_property("technology", "String")
segment.add_property("region", "String")
segment.add_property("node_count", "Integer")
segment.add_property("circuit_count", "Integer")
segment.add_property("capacity_gbps", "Real")
segment.add_property("redundancy_level", "String")

area = ontology.add_entity_type("ServiceArea", "dim_service_areas", "Lakehouse", "area_id")
area.add_property("area_id", "String", is_primary_key=True)
area.add_property("name", "String")
area.add_property("region", "String")
area.add_property("customer_count", "Integer")
area.add_property("technology", "String")
area.add_property("capacity_gbps", "Real")
area.add_property("last_upgrade", "String")
area.add_property("pop_count", "Integer")
area.add_property("fiber_miles", "Real")

ticket_type = ontology.add_entity_type("TicketType", "dim_ticket_types", "Lakehouse", "ticket_type_id")
ticket_type.add_property("ticket_type_id", "String", is_primary_key=True)
ticket_type.add_property("name", "String")
ticket_type.add_property("category", "String")
ticket_type.add_property("priority_levels", "String")
ticket_type.add_property("avg_resolution_min", "Integer")
ticket_type.add_property("sla_target_hours", "Real")
ticket_type.add_property("documentation_template", "String")
ticket_type.add_property("requires_rca", "String")

# --- Add Relationship Types ---
ontology.add_relationship_type("operates_in", "Engineer", "region", "ServiceArea", "region")
ontology.add_relationship_type("manages", "Engineer", "engineer_id", "NetworkSegment", "segment_id")
ontology.add_relationship_type("serves", "ServiceArea", "region", "EnterpriseCustomer", "region")
ontology.add_relationship_type("hosts", "NetworkSegment", "segment_id", "Equipment", "site_id")
ontology.add_relationship_type("monitors", "Engineer", "engineer_id", "Equipment", "equipment_id")

# --- Add Contextualizations ---
ctx_ticket = ontology.add_contextualization("TroubleTicket", "fact_trouble_tickets", "Lakehouse", "ticket_date")
ctx_ticket.add_entity_binding("Engineer", "engineer_id", "engineer_id")
ctx_ticket.add_entity_binding("TicketType", "ticket_type_id", "ticket_type_id")
ctx_ticket.add_entity_binding("NetworkSegment", "segment_id", "segment_id")
ctx_ticket.add_entity_binding("Equipment", "equipment_id", "equipment_id")
ctx_ticket.add_entity_binding("ServiceArea", "area_id", "area_id")

ctx_nms = ontology.add_contextualization("NMSInteraction", "nms_interactions", "Eventhouse", "timestamp")
ctx_nms.add_entity_binding("Engineer", "engineer_id", "engineer_id")

ctx_outage = ontology.add_contextualization("OutageEvent", "outage_events", "Eventhouse", "timestamp")
ctx_outage.add_entity_binding("NetworkSegment", "segment_id", "segment_id")
ctx_outage.add_entity_binding("Equipment", "equipment_id", "equipment_id")
ctx_outage.add_entity_binding("ServiceArea", "area_id", "area_id")

ctx_rca = ontology.add_contextualization("RCADocument", "rca_documents", "Eventhouse", "timestamp")
ctx_rca.add_entity_binding("Engineer", "engineer_id", "engineer_id")

ctx_escl = ontology.add_contextualization("TicketEscalation", "ticket_escalations", "Eventhouse", "timestamp")
ctx_escl.add_entity_binding("Engineer", "engineer_from", "engineer_id")

ctx_sla = ontology.add_contextualization("SLAAlert", "sla_alerts", "Eventhouse", "timestamp")
ctx_sla.add_entity_binding("EnterpriseCustomer", "customer_id", "customer_id")
ctx_sla.add_entity_binding("ServiceArea", "area_id", "area_id")

ctx_field = ontology.add_contextualization("FieldLocation", "field_location", "Eventhouse", "timestamp")
ctx_field.add_entity_binding("Engineer", "technician_id", "engineer_id")

ctx_alarm = ontology.add_contextualization("NetworkAlarm", "network_alarms", "Eventhouse", "timestamp")
ctx_alarm.add_entity_binding("Equipment", "equipment_id", "equipment_id")

ctx_activity = ontology.add_contextualization("TicketActivity", "ticket_activity", "Eventhouse", "timestamp")
ctx_activity.add_entity_binding("Engineer", "engineer_id", "engineer_id")

ctx_dispatch = ontology.add_contextualization("FieldDispatch", "field_dispatch", "Eventhouse", "timestamp")
ctx_dispatch.add_entity_binding("Engineer", "technician_id", "engineer_id")

ctx_perf = ontology.add_contextualization("PerformanceMetric", "performance_metrics", "Eventhouse", "timestamp")
ctx_perf.add_entity_binding("Equipment", "equipment_id", "equipment_id")

ctx_impact = ontology.add_contextualization("CustomerImpact", "customer_impact", "Eventhouse", "timestamp")
ctx_impact.add_entity_binding("EnterpriseCustomer", "customer_id", "customer_id")

# Save / publish
ontology.save()
print("✅ TelecomNetworkOpsOntology created successfully!")
```

---

## Step 7: Verify the Ontology

1. Open **Fabric Portal** → navigate to your workspace
2. Open the **Real-Time Intelligence** experience
3. Find **TelecomNetworkOpsOntology** in the ontology list
4. Verify:
   - **6 Entity Types** displayed (Engineer, EnterpriseCustomer, Equipment, NetworkSegment, ServiceArea, TicketType)
   - **5 Relationship Types** connecting entities
   - **12 Contextualizations** binding events to entities
   - Data bindings show Lakehouse and Eventhouse connections with live data

---

## Data Binding Summary

| Binding Target       | Storage      | Entity / CTX Bindings            |
|----------------------|--------------|----------------------------------|
| dim_engineers        | Lakehouse    | Engineer entity                  |
| dim_enterprise_customers | Lakehouse | EnterpriseCustomer entity       |
| dim_equipment        | Lakehouse    | Equipment entity                 |
| dim_network_segments | Lakehouse    | NetworkSegment entity            |
| dim_service_areas    | Lakehouse    | ServiceArea entity               |
| dim_ticket_types     | Lakehouse    | TicketType entity                |
| fact_trouble_tickets | Lakehouse    | CTX: Engineer, TicketType, NetworkSegment, Equipment, ServiceArea |
| nms_interactions     | Eventhouse   | CTX: Engineer                    |
| outage_events        | Eventhouse   | CTX: NetworkSegment, Equipment, ServiceArea |
| rca_documents        | Eventhouse   | CTX: Engineer                    |
| ticket_escalations   | Eventhouse   | CTX: Engineer                    |
| sla_alerts           | Eventhouse   | CTX: EnterpriseCustomer, ServiceArea |
| field_location       | Eventhouse   | CTX: Engineer                    |
| network_alarms       | Eventhouse   | CTX: Equipment                   |
| ticket_activity      | Eventhouse   | CTX: Engineer                    |
| field_dispatch       | Eventhouse   | CTX: Engineer                    |
| performance_metrics  | Eventhouse   | CTX: Equipment                   |
| customer_impact      | Eventhouse   | CTX: EnterpriseCustomer          |

---

## Built-In Data Patterns for Demo

The telecom sample data includes intentional correlation patterns to showcase documentation burden insights:

1. **Engineer overload pattern** — Engineers ENG-001, 003, 007 have 3× documentation time due to Tier 1 → Tier 3 escalations
2. **SLA breach cascade** — Platinum customers in Northeast show correlated SLA breaches during major outage events
3. **Field vs. desk documentation gap** — Field technicians average 2× documentation time per ticket vs. NOC analysts
4. **Alarm storm correlation** — Performance metric threshold crossings precede network alarms → trouble tickets → escalations → RCA documents
5. **Night shift burden** — On-call engineers document 40% more per ticket during overnight hours due to limited NOC staffing
