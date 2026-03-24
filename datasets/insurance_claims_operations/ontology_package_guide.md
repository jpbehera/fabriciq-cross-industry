# Insurance Claims Operations — Ontology Package Guide

## Prerequisites

| Resource         | Name                    | Purpose                                           |
|------------------|-------------------------|---------------------------------------------------|
| **Lakehouse**    | InsuranceLakehouse      | Stores dimension tables and batch fact tables      |
| **Eventhouse**   | InsuranceEventhouse     | Stores event fact tables for real-time analytics   |
| **KQL Database** | InsuranceKQLDB          | Stores stream tables for live telemetry            |

Ensure all three resources are provisioned in your Microsoft Fabric workspace before proceeding.

---

## Step 1: Prepare Lakehouse

Upload CSV files from the dataset to the Lakehouse under the base path:

```
Files/insurance_claims_operations/data
```

### Dimension Tables

| File                          | Target Table              | Row Scope               |
|-------------------------------|---------------------------|-------------------------|
| `dim_adjusters.csv`           | dim_adjusters             | All adjusters           |
| `dim_policyholders.csv`       | dim_policyholders         | All policyholders       |
| `dim_claims_departments.csv`  | dim_claims_departments    | All departments         |
| `dim_claim_form_types.csv`    | dim_claim_form_types      | All form types          |
| `dim_coverage_types.csv`      | dim_coverage_types        | All coverage types      |
| `dim_service_providers.csv`   | dim_service_providers     | All service providers   |

### Batch Fact Tables

| File                                 | Target Table                     | Row Scope                    |
|--------------------------------------|----------------------------------|------------------------------|
| `fact_adjuster_wellness.csv`         | fact_adjuster_wellness           | Monthly wellness surveys     |
| `fact_claim_accuracy.csv`            | fact_claim_accuracy              | Per-claim accuracy audits    |
| `fact_policyholder_satisfaction.csv`  | fact_policyholder_satisfaction   | Post-claim CSAT surveys      |

### Load into Lakehouse Tables

```python
import pandas as pd
from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()

base_path = "Files/insurance_claims_operations/data"
lakehouse_tables = [
    "dim_adjusters",
    "dim_policyholders",
    "dim_claims_departments",
    "dim_claim_form_types",
    "dim_coverage_types",
    "dim_service_providers",
    "fact_adjuster_wellness",
    "fact_claim_accuracy",
    "fact_policyholder_satisfaction",
]

for table in lakehouse_tables:
    df = spark.read.option("header", True).csv(f"{base_path}/{table}.csv")
    df.write.mode("overwrite").format("delta").saveAsTable(table)
    print(f"Loaded {table}: {df.count()} rows")
```

---

## Step 2: Prepare Eventhouse

Ingest event fact tables and stream tables into the Eventhouse / KQL Database.

### Event Fact Tables → InsuranceEventhouse

| File                              | Target Table                 | Row Scope                          |
|-----------------------------------|------------------------------|------------------------------------|
| `fact_claims_doc_events.csv`      | fact_claims_doc_events       | Per-form documentation events      |
| `fact_claims_system_clicks.csv`   | fact_claims_system_clicks    | Per-click system interactions      |
| `fact_claim_lifecycle.csv`        | fact_claim_lifecycle         | Per-claim lifecycle milestones     |
| `fact_claim_status_changes.csv`   | fact_claim_status_changes    | Per-claim status transitions       |
| `fact_field_inspections.csv`      | fact_field_inspections       | Per-inspection field visits        |
| `fact_claim_handoffs.csv`         | fact_claim_handoffs          | Per-handoff claim transfers        |
| `fact_fraud_alerts.csv`           | fact_fraud_alerts            | Per-alert fraud events             |
| `fact_verification_scans.csv`     | fact_verification_scans      | Per-scan verification events       |
| `fact_underwriting_docs.csv`      | fact_underwriting_docs       | Per-document underwriting events   |

### Stream Tables → InsuranceKQLDB

| File                                  | Target Table                       | Row Scope                       |
|---------------------------------------|------------------------------------|----------------------------------|
| `stream_claims_system_clicks.csv`     | stream_claims_system_clicks        | Real-time click telemetry        |
| `stream_claim_status_changes.csv`     | stream_claim_status_changes        | Real-time status transitions     |
| `stream_customer_contacts.csv`        | stream_customer_contacts           | Real-time customer interactions  |
| `stream_field_adjuster_location.csv`  | stream_field_adjuster_location     | Real-time adjuster GPS pings     |
| `stream_fraud_alerts.csv`             | stream_fraud_alerts                | Real-time fraud alert stream     |

### KQL Ingestion Command

```kql
.ingest into table fact_claims_doc_events
    (@"Files/insurance_claims_operations/data/fact_claims_doc_events.csv")
    with (format="csv", ignoreFirstRecord=true)
```

Repeat for each event fact and stream table listed above.

---

## Step 3: Entity Type Definitions

### ENT-001: Adjuster

```json
{
    "name": "Adjuster",
    "description": "Insurance claims adjuster who evaluates and processes claims",
    "table": "dim_adjusters",
    "storage": "Lakehouse",
    "key": "adjuster_id",
    "properties": [
        {"name": "adjuster_id", "type": "string", "key": true},
        {"name": "name", "type": "string"},
        {"name": "role", "type": "string"},
        {"name": "department", "type": "string"},
        {"name": "region", "type": "string"},
        {"name": "license_state", "type": "string"},
        {"name": "hire_date", "type": "date"},
        {"name": "claim_authority_limit", "type": "decimal"}
    ]
}
```

### ENT-002: Policyholder

```json
{
    "name": "Policyholder",
    "description": "Insurance policyholder who files claims",
    "table": "dim_policyholders",
    "storage": "Lakehouse",
    "key": "policyholder_id",
    "properties": [
        {"name": "policyholder_id", "type": "string", "key": true},
        {"name": "name", "type": "string"},
        {"name": "policy_type", "type": "string"},
        {"name": "effective_date", "type": "date"},
        {"name": "risk_tier", "type": "string"},
        {"name": "segment", "type": "string"},
        {"name": "state", "type": "string"}
    ]
}
```

### ENT-003: ClaimsDepartment

```json
{
    "name": "ClaimsDepartment",
    "description": "Department within the insurance company that handles specific claim types",
    "table": "dim_claims_departments",
    "storage": "Lakehouse",
    "key": "dept_id",
    "properties": [
        {"name": "dept_id", "type": "string", "key": true},
        {"name": "name", "type": "string"},
        {"name": "region", "type": "string"},
        {"name": "claim_types_handled", "type": "string"},
        {"name": "headcount", "type": "integer"},
        {"name": "avg_caseload", "type": "integer"}
    ]
}
```

### ENT-004: ClaimFormType

```json
{
    "name": "ClaimFormType",
    "description": "Type of form used during claims processing and documentation",
    "table": "dim_claim_form_types",
    "storage": "Lakehouse",
    "key": "form_type_id",
    "properties": [
        {"name": "form_type_id", "type": "string", "key": true},
        {"name": "name", "type": "string"},
        {"name": "category", "type": "string"},
        {"name": "regulatory_requirement", "type": "string"},
        {"name": "avg_completion_time_min", "type": "decimal"},
        {"name": "applies_to_claim_types", "type": "string"}
    ]
}
```

### ENT-005: CoverageType

```json
{
    "name": "CoverageType",
    "description": "Type of insurance coverage offered to policyholders",
    "table": "dim_coverage_types",
    "storage": "Lakehouse",
    "key": "coverage_id",
    "properties": [
        {"name": "coverage_id", "type": "string", "key": true},
        {"name": "name", "type": "string"},
        {"name": "line_of_business", "type": "string"},
        {"name": "limit_range", "type": "string"},
        {"name": "deductible_range", "type": "string"}
    ]
}
```

### ENT-006: ServiceProvider

```json
{
    "name": "ServiceProvider",
    "description": "External service provider supporting claims operations (repair, medical, legal)",
    "table": "dim_service_providers",
    "storage": "Lakehouse",
    "key": "provider_id",
    "properties": [
        {"name": "provider_id", "type": "string", "key": true},
        {"name": "name", "type": "string"},
        {"name": "type", "type": "string"},
        {"name": "region", "type": "string"},
        {"name": "avg_turnaround_days", "type": "decimal"}
    ]
}
```

---

## Step 4: Relationship Type Definitions

### REL-001: handles_claims_for

```json
{
    "name": "handles_claims_for",
    "description": "Adjuster handles claims on behalf of policyholders",
    "source_entity": "Adjuster",
    "target_entity": "Policyholder",
    "cardinality": "many-to-many",
    "join_path": "fact_claim_lifecycle.adjuster_id → fact_claim_lifecycle.policyholder_id"
}
```

### REL-002: belongs_to_dept

```json
{
    "name": "belongs_to_dept",
    "description": "Adjuster belongs to a claims department",
    "source_entity": "Adjuster",
    "target_entity": "ClaimsDepartment",
    "cardinality": "many-to-one",
    "join_path": "dim_adjusters.department → dim_claims_departments.name"
}
```

### REL-003: covered_by

```json
{
    "name": "covered_by",
    "description": "Policyholder is covered by one or more coverage types",
    "source_entity": "Policyholder",
    "target_entity": "CoverageType",
    "cardinality": "many-to-many",
    "join_path": "dim_policyholders.policy_type → dim_coverage_types.line_of_business"
}
```

### REL-004: requires_form

```json
{
    "name": "requires_form",
    "description": "Coverage type requires specific claim forms for processing",
    "source_entity": "CoverageType",
    "target_entity": "ClaimFormType",
    "cardinality": "one-to-many",
    "join_path": "dim_coverage_types.name → dim_claim_form_types.applies_to_claim_types"
}
```

### REL-005: served_by

```json
{
    "name": "served_by",
    "description": "Claims department is served by external service providers",
    "source_entity": "ClaimsDepartment",
    "target_entity": "ServiceProvider",
    "cardinality": "many-to-many",
    "join_path": "dim_claims_departments.region → dim_service_providers.region"
}
```

---

## Step 5: Contextualization Definitions

### CTX-001: claims_doc_events

```json
{
    "name": "claims_doc_events",
    "description": "Per-form documentation events tracking time and errors per adjuster",
    "table": "fact_claims_doc_events",
    "storage": "Eventhouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"},
        {"entity": "ClaimFormType", "column": "form_type_id"}
    ],
    "measures": ["duration_minutes", "error_count", "regulatory_flag"]
}
```

### CTX-002: claims_system_clicks

```json
{
    "name": "claims_system_clicks",
    "description": "Per-click interactions within the claims management system",
    "table": "fact_claims_system_clicks",
    "storage": "Eventhouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"}
    ],
    "measures": ["duration_ms", "idle_before_ms", "error_code"]
}
```

### CTX-003: claim_lifecycle

```json
{
    "name": "claim_lifecycle",
    "description": "End-to-end claim lifecycle milestones from FNOL to close",
    "table": "fact_claim_lifecycle",
    "storage": "Eventhouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"},
        {"entity": "Policyholder", "column": "policyholder_id"}
    ],
    "measures": ["total_doc_hours"]
}
```

### CTX-004: claim_status_changes

```json
{
    "name": "claim_status_changes",
    "description": "Status transitions across the claim lifecycle",
    "table": "fact_claim_status_changes",
    "storage": "Eventhouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"}
    ],
    "measures": ["time_in_previous_status_hours", "documentation_required"]
}
```

### CTX-005: field_inspections

```json
{
    "name": "field_inspections",
    "description": "Field inspection events including travel, inspection, and report writing time",
    "table": "fact_field_inspections",
    "storage": "Eventhouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"}
    ],
    "measures": ["travel_time_min", "inspection_time_min", "photo_count", "report_time_min"]
}
```

### CTX-006: claim_handoffs

```json
{
    "name": "claim_handoffs",
    "description": "Claim handoff events between adjusters with documentation transfer time",
    "table": "fact_claim_handoffs",
    "storage": "Eventhouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "from_adjuster_id"},
        {"entity": "Adjuster", "column": "to_adjuster_id"}
    ],
    "measures": ["doc_transfer_time_min", "reason"]
}
```

### CTX-007: fraud_alerts

```json
{
    "name": "fraud_alerts",
    "description": "Fraud alert events requiring investigation documentation",
    "table": "fact_fraud_alerts",
    "storage": "Eventhouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"}
    ],
    "measures": ["investigation_time_min", "severity", "action_taken"]
}
```

### CTX-008: verification_scans

```json
{
    "name": "verification_scans",
    "description": "Document verification scan results with discrepancy tracking",
    "table": "fact_verification_scans",
    "storage": "Eventhouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"}
    ],
    "measures": ["result", "discrepancy_flag", "document_source"]
}
```

### CTX-009: underwriting_docs

```json
{
    "name": "underwriting_docs",
    "description": "Underwriting documentation events for risk assessment",
    "table": "fact_underwriting_docs",
    "storage": "Eventhouse",
    "entity_bindings": [],
    "measures": ["risk_assessment_time_min", "form_count", "approval_status"]
}
```

### CTX-010: adjuster_wellness

```json
{
    "name": "adjuster_wellness",
    "description": "Monthly adjuster wellness and burnout risk surveys",
    "table": "fact_adjuster_wellness",
    "storage": "Lakehouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"},
        {"entity": "ClaimsDepartment", "column": "dept_id"}
    ],
    "measures": ["caseload_count", "workload_perception", "overtime_hours", "burnout_risk_score"]
}
```

### CTX-011: claim_accuracy

```json
{
    "name": "claim_accuracy",
    "description": "Claim accuracy audits measuring documentation completeness and settlement variance",
    "table": "fact_claim_accuracy",
    "storage": "Lakehouse",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"}
    ],
    "measures": ["reopened_flag", "settlement_variance_pct", "audit_finding_count", "documentation_completeness_pct"]
}
```

### CTX-012: policyholder_satisfaction

```json
{
    "name": "policyholder_satisfaction",
    "description": "Post-claim policyholder CSAT surveys",
    "table": "fact_policyholder_satisfaction",
    "storage": "Lakehouse",
    "entity_bindings": [
        {"entity": "Policyholder", "column": "policyholder_id"}
    ],
    "measures": ["csat_score", "communication_rating", "speed_rating", "complaint_flag"]
}
```

### CTX-013: live_system_clicks

```json
{
    "name": "live_system_clicks",
    "description": "Real-time claims system click stream",
    "table": "stream_claims_system_clicks",
    "storage": "KQL_DB",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"}
    ],
    "measures": ["duration_ms", "module", "action", "error_code"]
}
```

### CTX-014: live_status_changes

```json
{
    "name": "live_status_changes",
    "description": "Real-time claim status transition stream",
    "table": "stream_claim_status_changes",
    "storage": "KQL_DB",
    "entity_bindings": [
        {"entity": "Adjuster", "column": "adjuster_id"}
    ],
    "measures": ["from_status", "to_status", "trigger", "auto_vs_manual"]
}
```

---

## Step 6: Create Ontology

```python
from fabriciq import OntologyManager

ontology = OntologyManager(
    workspace_id="<YOUR_WORKSPACE_ID>",
    ontology_name="InsuranceClaimsOpsOntology"
)

# --- Entity Types ---
entity_types = [
    {
        "name": "Adjuster",
        "table": "dim_adjusters",
        "storage": "Lakehouse",
        "key": "adjuster_id",
        "properties": [
            {"name": "adjuster_id", "type": "string", "key": True},
            {"name": "name", "type": "string"},
            {"name": "role", "type": "string"},
            {"name": "department", "type": "string"},
            {"name": "region", "type": "string"},
            {"name": "license_state", "type": "string"},
            {"name": "hire_date", "type": "date"},
            {"name": "claim_authority_limit", "type": "decimal"},
        ],
    },
    {
        "name": "Policyholder",
        "table": "dim_policyholders",
        "storage": "Lakehouse",
        "key": "policyholder_id",
        "properties": [
            {"name": "policyholder_id", "type": "string", "key": True},
            {"name": "name", "type": "string"},
            {"name": "policy_type", "type": "string"},
            {"name": "effective_date", "type": "date"},
            {"name": "risk_tier", "type": "string"},
            {"name": "segment", "type": "string"},
            {"name": "state", "type": "string"},
        ],
    },
    {
        "name": "ClaimsDepartment",
        "table": "dim_claims_departments",
        "storage": "Lakehouse",
        "key": "dept_id",
        "properties": [
            {"name": "dept_id", "type": "string", "key": True},
            {"name": "name", "type": "string"},
            {"name": "region", "type": "string"},
            {"name": "claim_types_handled", "type": "string"},
            {"name": "headcount", "type": "integer"},
            {"name": "avg_caseload", "type": "integer"},
        ],
    },
    {
        "name": "ClaimFormType",
        "table": "dim_claim_form_types",
        "storage": "Lakehouse",
        "key": "form_type_id",
        "properties": [
            {"name": "form_type_id", "type": "string", "key": True},
            {"name": "name", "type": "string"},
            {"name": "category", "type": "string"},
            {"name": "regulatory_requirement", "type": "string"},
            {"name": "avg_completion_time_min", "type": "decimal"},
            {"name": "applies_to_claim_types", "type": "string"},
        ],
    },
    {
        "name": "CoverageType",
        "table": "dim_coverage_types",
        "storage": "Lakehouse",
        "key": "coverage_id",
        "properties": [
            {"name": "coverage_id", "type": "string", "key": True},
            {"name": "name", "type": "string"},
            {"name": "line_of_business", "type": "string"},
            {"name": "limit_range", "type": "string"},
            {"name": "deductible_range", "type": "string"},
        ],
    },
    {
        "name": "ServiceProvider",
        "table": "dim_service_providers",
        "storage": "Lakehouse",
        "key": "provider_id",
        "properties": [
            {"name": "provider_id", "type": "string", "key": True},
            {"name": "name", "type": "string"},
            {"name": "type", "type": "string"},
            {"name": "region", "type": "string"},
            {"name": "avg_turnaround_days", "type": "decimal"},
        ],
    },
]

for et in entity_types:
    ontology.create_entity_type(**et)
    print(f"Created entity type: {et['name']}")

# --- Relationship Types ---
relationship_types = [
    {
        "name": "handles_claims_for",
        "source_entity": "Adjuster",
        "target_entity": "Policyholder",
        "cardinality": "many-to-many",
    },
    {
        "name": "belongs_to_dept",
        "source_entity": "Adjuster",
        "target_entity": "ClaimsDepartment",
        "cardinality": "many-to-one",
    },
    {
        "name": "covered_by",
        "source_entity": "Policyholder",
        "target_entity": "CoverageType",
        "cardinality": "many-to-many",
    },
    {
        "name": "requires_form",
        "source_entity": "CoverageType",
        "target_entity": "ClaimFormType",
        "cardinality": "one-to-many",
    },
    {
        "name": "served_by",
        "source_entity": "ClaimsDepartment",
        "target_entity": "ServiceProvider",
        "cardinality": "many-to-many",
    },
]

for rt in relationship_types:
    ontology.create_relationship_type(**rt)
    print(f"Created relationship: {rt['name']}")

# --- Contextualizations ---
contextualizations = [
    {"name": "claims_doc_events", "table": "fact_claims_doc_events", "storage": "Eventhouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}, {"entity": "ClaimFormType", "column": "form_type_id"}]},
    {"name": "claims_system_clicks", "table": "fact_claims_system_clicks", "storage": "Eventhouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}]},
    {"name": "claim_lifecycle", "table": "fact_claim_lifecycle", "storage": "Eventhouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}, {"entity": "Policyholder", "column": "policyholder_id"}]},
    {"name": "claim_status_changes", "table": "fact_claim_status_changes", "storage": "Eventhouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}]},
    {"name": "field_inspections", "table": "fact_field_inspections", "storage": "Eventhouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}]},
    {"name": "claim_handoffs", "table": "fact_claim_handoffs", "storage": "Eventhouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "from_adjuster_id"}, {"entity": "Adjuster", "column": "to_adjuster_id"}]},
    {"name": "fraud_alerts", "table": "fact_fraud_alerts", "storage": "Eventhouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}]},
    {"name": "verification_scans", "table": "fact_verification_scans", "storage": "Eventhouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}]},
    {"name": "underwriting_docs", "table": "fact_underwriting_docs", "storage": "Eventhouse",
     "entity_bindings": []},
    {"name": "adjuster_wellness", "table": "fact_adjuster_wellness", "storage": "Lakehouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}, {"entity": "ClaimsDepartment", "column": "dept_id"}]},
    {"name": "claim_accuracy", "table": "fact_claim_accuracy", "storage": "Lakehouse",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}]},
    {"name": "policyholder_satisfaction", "table": "fact_policyholder_satisfaction", "storage": "Lakehouse",
     "entity_bindings": [{"entity": "Policyholder", "column": "policyholder_id"}]},
    {"name": "live_system_clicks", "table": "stream_claims_system_clicks", "storage": "KQL_DB",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}]},
    {"name": "live_status_changes", "table": "stream_claim_status_changes", "storage": "KQL_DB",
     "entity_bindings": [{"entity": "Adjuster", "column": "adjuster_id"}]},
]

for ctx in contextualizations:
    ontology.create_contextualization(**ctx)
    print(f"Created contextualization: {ctx['name']}")

print("\nOntology 'InsuranceClaimsOpsOntology' created successfully.")
```

---

## Step 7: Verify

After running the creation script, verify the ontology components:

```python
summary = ontology.get_summary()
print(f"Entity Types:        {summary['entity_type_count']}")        # Expected: 6
print(f"Relationship Types:  {summary['relationship_type_count']}")  # Expected: 5
print(f"Contextualizations:  {summary['contextualization_count']}")  # Expected: 14
```

### Expected Counts

| Component            | Count | Details                                                     |
|----------------------|-------|-------------------------------------------------------------|
| Entity Types         | 6     | Adjuster, Policyholder, ClaimsDepartment, ClaimFormType, CoverageType, ServiceProvider |
| Relationship Types   | 5     | handles_claims_for, belongs_to_dept, covered_by, requires_form, served_by |
| Contextualizations   | 14    | 9 event facts + 3 batch facts + 2 streams                  |

---

## Data Binding Summary

| Contextualization             | Storage     | Bound Entities                       | Primary Metric                     |
|-------------------------------|-------------|--------------------------------------|------------------------------------|
| claims_doc_events             | Eventhouse  | Adjuster, ClaimFormType              | duration_minutes                   |
| claims_system_clicks          | Eventhouse  | Adjuster                             | duration_ms                        |
| claim_lifecycle               | Eventhouse  | Adjuster, Policyholder               | total_doc_hours                    |
| claim_status_changes          | Eventhouse  | Adjuster                             | time_in_previous_status_hours      |
| field_inspections             | Eventhouse  | Adjuster                             | report_time_min                    |
| claim_handoffs                | Eventhouse  | Adjuster (×2)                        | doc_transfer_time_min              |
| fraud_alerts                  | Eventhouse  | Adjuster                             | investigation_time_min             |
| verification_scans            | Eventhouse  | Adjuster                             | discrepancy_flag                   |
| underwriting_docs             | Eventhouse  | —                                    | risk_assessment_time_min           |
| adjuster_wellness             | Lakehouse   | Adjuster, ClaimsDepartment           | burnout_risk_score                 |
| claim_accuracy                | Lakehouse   | Adjuster                             | documentation_completeness_pct     |
| policyholder_satisfaction     | Lakehouse   | Policyholder                         | csat_score                         |
| live_system_clicks            | KQL DB      | Adjuster                             | duration_ms                        |
| live_status_changes           | KQL DB      | Adjuster                             | trigger                            |

---

## Built-In Data Patterns

### Pattern 1: Adjuster Caseload Documentation Overload

**Question:** Which adjusters have high caseloads AND high documentation time per claim?

**Data path:**
- `fact_adjuster_wellness` → `caseload_count`, `burnout_risk_score`
- `fact_claims_doc_events` → SUM(`duration_minutes`) per adjuster
- JOIN on `adjuster_id`

**Insight:** Reveals adjusters at risk of burnout due to combined caseload pressure and documentation overhead. High documentation time per claim with high caseload indicates systemic workflow inefficiency.

---

### Pattern 2: FNOL-to-Close Documentation Cascade

**Question:** What fraction of the total claim lifecycle is spent on documentation?

**Data path:**
- `fact_claim_lifecycle` → `total_doc_hours`, DATEDIFF(`fnol_date`, `close_date`)
- `fact_claims_doc_events` → SUM(`duration_minutes`) per `claim_id`
- JOIN on `claim_id`

**Insight:** Quantifies `doc_hours / total_lifecycle_hours` to identify claim types where documentation consumes a disproportionate portion of the overall processing time.

---

### Pattern 3: Field Inspection Report Time vs. Travel

**Question:** Are field adjusters spending more time writing reports than performing inspections?

**Data path:**
- `fact_field_inspections` → `travel_time_min`, `inspection_time_min`, `report_time_min`
- GROUP BY `adjuster_id`, `location`

**Insight:** `report_time_min / (inspection_time_min + report_time_min)` reveals the report-writing burden ratio. High ratios suggest opportunities for mobile reporting tools or standardized field templates.

---

### Pattern 4: Fraud Alert Investigation Burden

**Question:** How much documentation effort do low-severity fraud alerts consume vs. high-severity ones?

**Data path:**
- `fact_fraud_alerts` → `investigation_time_min`, `severity`, `alert_type`
- GROUP BY `severity`, `alert_type`

**Insight:** If low-severity alerts consume substantial investigation time, the fraud detection thresholds may need recalibration to reduce documentation burden on adjusters for false or marginal alerts.

---

### Pattern 5: Claim Handoff Documentation Gaps

**Question:** How much time is lost in documentation transfer when claims change hands?

**Data path:**
- `fact_claim_handoffs` → `doc_transfer_time_min`, `reason`
- `fact_claim_accuracy` → `documentation_completeness_pct` for claims with handoffs
- JOIN on `claim_id`

**Insight:** Correlates handoff frequency and transfer time with downstream documentation completeness. Claims with multiple handoffs often show lower `documentation_completeness_pct`, indicating information loss during transfers.
