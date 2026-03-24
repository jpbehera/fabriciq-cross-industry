# Ontology Package Mapping Guide

## How to Create the `.iq` Package for Healthcare Nursing Documentation

This guide maps the healthcare data model to the Fabric IQ accelerator's `.iq` package format, following the patterns used by the existing sample packages (airline, retail, robotics, loan).

---

## Prerequisites

1. **Fabric Workspace** with:
   - A **Lakehouse** (for dimension/static data as Delta tables)
   - An **Eventhouse** (for event/streaming data as KQL tables)
2. **fabriciq_ontology_accelerator** package (v0.1.0+) installed
3. CSV files uploaded to Lakehouse Files area

---

## Step 1: Prepare Lakehouse Delta Tables

Upload all CSVs to `/lakehouse/default/Files/healthcare_data/` and run the following in a Fabric notebook:

```python
from pyspark.sql import SparkSession

base_path = "/lakehouse/default/Files/healthcare_data"
schema = "dbo"  # or your lakehouse schema

# Dimension tables
for table_name in [
    "dim_nurses", "dim_patients", "dim_hospital_units",
    "dim_documentation_types", "dim_medications", "dim_diagnoses"
]:
    df = spark.read.option("header", True).option("inferSchema", True).csv(f"{base_path}/{table_name}.csv")
    df.write.mode("overwrite").saveAsTable(f"{schema}.{table_name}")

# Fact tables (Lakehouse-bound)
for table_name in [
    "fact_shifts", "fact_patient_encounters", "fact_care_plans",
    "fact_burnout_surveys", "fact_patient_satisfaction", "fact_documentation_quality"
]:
    df = spark.read.option("header", True).option("inferSchema", True).csv(f"{base_path}/{table_name}.csv")
    df.write.mode("overwrite").saveAsTable(f"{schema}.{table_name}")
```

## Step 2: Prepare Eventhouse KQL Tables

For each event table, ingest into Eventhouse using the KQL ingestion workflow:

```python
from fabricontology.generate_data import generate_events_data
from notebookutils import mssparkutils

eventhouse_cluster_uri = "<your-eventhouse-cluster-uri>"
eventhouse_database = "<your-eventhouse-database>"
access_token = mssparkutils.credentials.getToken(eventhouse_cluster_uri)

# Or manually ingest each event CSV:
import pandas as pd
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder
from azure.kusto.ingest import QueuedIngestClient, IngestionProperties

# Tables to ingest into Eventhouse
event_tables = [
    "fact_documentation_events",
    "fact_medication_administration",
    "fact_vital_signs",
    "fact_assessments",
    "fact_ehr_interactions",
    "fact_handoff_reports"
]
```

## Step 3: Entity Type Definitions

The `.iq` package defines entity types with their properties. Here is the mapping for each entity:

### Nurse Entity Type
```json
{
  "entityTypeName": "Nurse",
  "tableName": "dim_nurses",
  "storageType": "Lakehouse",
  "primaryKey": "nurse_id",
  "displayName": "nurse_id",
  "properties": [
    {"name": "nurse_id", "type": "String", "isKey": true},
    {"name": "first_name", "type": "String"},
    {"name": "last_name", "type": "String"},
    {"name": "unit_id", "type": "String"},
    {"name": "role", "type": "String"},
    {"name": "credentials", "type": "String"},
    {"name": "years_experience", "type": "Int32"},
    {"name": "certifications", "type": "String"},
    {"name": "shift_preference", "type": "String"}
  ]
}
```

### Patient Entity Type
```json
{
  "entityTypeName": "Patient",
  "tableName": "dim_patients",
  "storageType": "Lakehouse",
  "primaryKey": "patient_id",
  "displayName": "patient_id",
  "properties": [
    {"name": "patient_id", "type": "String", "isKey": true},
    {"name": "first_name", "type": "String"},
    {"name": "last_name", "type": "String"},
    {"name": "age", "type": "Int32"},
    {"name": "gender", "type": "String"},
    {"name": "acuity_level", "type": "Int32"},
    {"name": "primary_diagnosis_id", "type": "String"},
    {"name": "insurance_type", "type": "String"}
  ]
}
```

### HospitalUnit Entity Type
```json
{
  "entityTypeName": "HospitalUnit",
  "tableName": "dim_hospital_units",
  "storageType": "Lakehouse",
  "primaryKey": "unit_id",
  "displayName": "unit_name",
  "properties": [
    {"name": "unit_id", "type": "String", "isKey": true},
    {"name": "unit_name", "type": "String"},
    {"name": "unit_type", "type": "String"},
    {"name": "bed_count", "type": "Int32"},
    {"name": "target_nurse_ratio", "type": "String"},
    {"name": "ehr_system", "type": "String"}
  ]
}
```

### DocumentationType Entity Type
```json
{
  "entityTypeName": "DocumentationType",
  "tableName": "dim_documentation_types",
  "storageType": "Lakehouse",
  "primaryKey": "doc_type_id",
  "displayName": "doc_type_name",
  "properties": [
    {"name": "doc_type_id", "type": "String", "isKey": true},
    {"name": "doc_type_name", "type": "String"},
    {"name": "category", "type": "String"},
    {"name": "avg_time_minutes", "type": "Int32"},
    {"name": "is_duplicative", "type": "String"},
    {"name": "duplicative_reason", "type": "String"}
  ]
}
```

### Medication Entity Type
```json
{
  "entityTypeName": "Medication",
  "tableName": "dim_medications",
  "storageType": "Lakehouse",
  "primaryKey": "medication_id",
  "displayName": "medication_name",
  "properties": [
    {"name": "medication_id", "type": "String", "isKey": true},
    {"name": "medication_name", "type": "String"},
    {"name": "drug_class", "type": "String"},
    {"name": "route", "type": "String"},
    {"name": "high_alert", "type": "String"}
  ]
}
```

### Diagnosis Entity Type
```json
{
  "entityTypeName": "Diagnosis",
  "tableName": "dim_diagnoses",
  "storageType": "Lakehouse",
  "primaryKey": "diagnosis_id",
  "displayName": "diagnosis_name",
  "properties": [
    {"name": "diagnosis_id", "type": "String", "isKey": true},
    {"name": "diagnosis_name", "type": "String"},
    {"name": "icd10_code", "type": "String"},
    {"name": "typical_los_days", "type": "Int32"},
    {"name": "acuity_level", "type": "Int32"}
  ]
}
```

## Step 4: Relationship Type Definitions

```json
[
  {
    "relationshipTypeName": "AssignedTo",
    "sourceEntityType": "Nurse",
    "sourceProperty": "unit_id",
    "targetEntityType": "HospitalUnit",
    "targetProperty": "unit_id"
  },
  {
    "relationshipTypeName": "AdmittedTo",
    "sourceEntityType": "Patient",
    "sourceProperty": "unit_id",
    "targetEntityType": "HospitalUnit",
    "targetProperty": "unit_id"
  },
  {
    "relationshipTypeName": "HasDiagnosis",
    "sourceEntityType": "Patient",
    "sourceProperty": "primary_diagnosis_id",
    "targetEntityType": "Diagnosis",
    "targetProperty": "diagnosis_id"
  }
]
```

## Step 5: Contextualization Definitions (Events)

Each contextualization links an Eventhouse event table to one or more entity types:

```json
[
  {
    "contextualizationName": "DocumentationEvent",
    "tableName": "documentation_events",
    "storageType": "Eventhouse",
    "timestampProperty": "timestamp",
    "entityBindings": [
      {"entityType": "Nurse", "property": "nurse_id"},
      {"entityType": "Patient", "property": "patient_id"},
      {"entityType": "DocumentationType", "property": "doc_type_id"}
    ]
  },
  {
    "contextualizationName": "MedicationAdministration",
    "tableName": "medication_administration",
    "storageType": "Eventhouse",
    "timestampProperty": "timestamp",
    "entityBindings": [
      {"entityType": "Nurse", "property": "nurse_id"},
      {"entityType": "Patient", "property": "patient_id"},
      {"entityType": "Medication", "property": "medication_id"}
    ]
  },
  {
    "contextualizationName": "VitalSignsRecording",
    "tableName": "vital_signs",
    "storageType": "Eventhouse",
    "timestampProperty": "timestamp",
    "entityBindings": [
      {"entityType": "Nurse", "property": "nurse_id"},
      {"entityType": "Patient", "property": "patient_id"}
    ]
  },
  {
    "contextualizationName": "AssessmentEvent",
    "tableName": "assessments",
    "storageType": "Eventhouse",
    "timestampProperty": "timestamp",
    "entityBindings": [
      {"entityType": "Nurse", "property": "nurse_id"},
      {"entityType": "Patient", "property": "patient_id"}
    ]
  },
  {
    "contextualizationName": "EHRInteraction",
    "tableName": "ehr_interactions",
    "storageType": "Eventhouse",
    "timestampProperty": "timestamp",
    "entityBindings": [
      {"entityType": "Nurse", "property": "nurse_id"}
    ]
  },
  {
    "contextualizationName": "HandoffReport",
    "tableName": "handoff_reports",
    "storageType": "Eventhouse",
    "timestampProperty": "timestamp",
    "entityBindings": [
      {"entityType": "Nurse", "property": "outgoing_nurse_id"},
      {"entityType": "Patient", "property": "patient_id"}
    ]
  }
]
```

## Step 6: Create the Ontology

Use the accelerator notebook pattern from `Create_Ontology_from_Package.ipynb`:

```python
import sempy.fabric as fabric
from fabricontology import create_ontology_item, generate_definition_from_package

workspace_id = fabric.get_workspace_id()
access_token = notebookutils.credentials.getToken('pbi')

ontology_item_name = "NursingDocBurdenOntology"
ontology_package_path = "/lakehouse/default/Files/nursing_doc_burden_ontology_package.iq"

binding_lakehouse_name = "<your-lakehouse-name>"
binding_lakehouse_schema_name = "dbo"
binding_eventhouse_name = "<your-eventhouse-name>"
binding_eventhouse_cluster_uri = "<your-eventhouse-cluster-uri>"
binding_eventhouse_database_name = "<your-eventhouse-database>"

items_df = fabric.list_items()
binding_lakehouse_item_id = str(items_df[
    (items_df["Type"] == "Lakehouse") &
    (items_df["Display Name"] == binding_lakehouse_name)
].iloc[0].Id)
binding_eventhouse_item_id = str(items_df[
    (items_df["Type"] == "Eventhouse") &
    (items_df["Display Name"] == binding_eventhouse_name)
].iloc[0].Id)

ontology_definition, entity_types, relationship_types, data_bindings, contextualizations = \
    generate_definition_from_package(
        ontology_package_path=ontology_package_path,
        ontology_name=ontology_item_name,
        binding_workspace_id=workspace_id,
        binding_lakehouse_item_id=binding_lakehouse_item_id,
        binding_lakehouse_schema_name=binding_lakehouse_schema_name,
        binding_eventhouse_item_id=binding_eventhouse_item_id,
        binding_eventhouse_cluster_uri=binding_eventhouse_cluster_uri,
        binding_eventhouse_database_name=binding_eventhouse_database_name
    )

response = create_ontology_item(
    workspace_id=workspace_id,
    access_token=access_token,
    ontology_item_name=ontology_item_name,
    ontology_definition=ontology_definition
)
print(response.json())
```

## Step 7: Verify the Ontology

After creation, verify in the Fabric portal:
1. Navigate to your workspace
2. Find the `NursingDocBurdenOntology` item
3. Open it to see the entity graph
4. Verify all 6 entity types appear with relationships
5. Check that contextualizations show event streams

---

## Data Binding Summary

| Binding Target | Item Type  | Tables Bound                                                                 |
|----------------|------------|-----------------------------------------------------------------------------|
| Lakehouse      | Delta      | dim_nurses, dim_patients, dim_hospital_units, dim_documentation_types, dim_medications, dim_diagnoses, fact_shifts, fact_patient_encounters, fact_care_plans, fact_burnout_surveys, fact_patient_satisfaction, fact_documentation_quality |
| Eventhouse     | KQL        | documentation_events, medication_administration, vital_signs, assessments, ehr_interactions, handoff_reports |

---

## Built-In Data Patterns for Demo

The synthetic data includes intentional correlation patterns for compelling demo narratives:

| Pattern | Nurses | Signal |
|---------|--------|--------|
| High burnout + high doc burden | NRS-002, NRS-006, NRS-014, NRS-017 | EE score > 30, overtime > 12h, doc satisfaction 1-2 |
| Low burnout + efficient charting | NRS-003, NRS-010, NRS-016 | EE score < 16, minimal overtime, doc satisfaction 4-5 |
| Junior nurse struggle | NRS-006, NRS-017 | Intent to leave, highest EHR frustration, error corrections |
| ICU high intensity/low volume | NRS-009, NRS-012 | Fewer patients, more doc per patient, longer assessments |
| ED high volume/doc backlog | NRS-017, NRS-019 | Multiple admissions, delayed documentation, incomplete handoffs |
| Duplicate documentation waste | All nurses | `is_duplicate_entry=Yes` flags across progress notes, vitals re-entry |
| Patient satisfaction correlation | Unit-level | Units with higher doc burden → lower nurse communication scores |
