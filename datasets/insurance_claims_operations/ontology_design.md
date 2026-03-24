# Insurance Claims Operations — Ontology Design

## Overview

**Ontology Name:** `InsuranceClaimsOpsOntology`

This ontology models the documentation burden within insurance claims operations — capturing how adjusters, policyholders, departments, and service providers interact across claim lifecycle events, field inspections, fraud investigations, and verification scans. It quantifies time spent on claim forms, system clicks, handoff documentation, and regulatory compliance vs. actual claims evaluation and decision-making.

The model comprises **6 entity types** (dimension tables), **12 fact tables** (9 event + 3 batch), and **5 stream tables**, providing a comprehensive view of claims documentation overhead from first notice of loss through settlement and closure.

---

## Concept Mapping

| RDF / OWL Concept        | Fabric IQ Equivalent     | Description                                              |
|--------------------------|--------------------------|----------------------------------------------------------|
| `owl:Class`              | Entity Type              | Adjuster, Policyholder, ClaimsDepartment, etc.           |
| `owl:DatatypeProperty`   | Property                 | adjuster_id, name, caseload_count, etc.                  |
| `owl:ObjectProperty`     | Relationship Type        | handles_claims_for, belongs_to_dept, etc.                |
| `rdfs:domain` / `range`  | Source / Target Entity   | Defines relationship directionality                      |
| `owl:NamedIndividual`    | Row in Lakehouse table   | A specific adjuster, policyholder, or department record  |
| Context / Reification    | Contextualization        | Event/fact tables that annotate entity relationships     |

---

## Entity Types

### ENT-001: Adjuster

| Property                 | Type     | Description                                  |
|--------------------------|----------|----------------------------------------------|
| `adjuster_id`            | string   | Primary key — unique adjuster identifier     |
| `name`                   | string   | Full name of the adjuster                    |
| `role`                   | string   | Role (field adjuster, desk adjuster, senior) |
| `department`             | string   | Department assignment                        |
| `region`                 | string   | Operating region                             |
| `license_state`          | string   | State of licensure                           |
| `hire_date`              | date     | Date of hire                                 |
| `claim_authority_limit`  | decimal  | Maximum claim settlement authority ($)       |

**Source table:** `dim_adjusters`
**Storage:** Lakehouse (`InsuranceLakehouse`)

---

### ENT-002: Policyholder

| Property            | Type     | Description                                  |
|---------------------|----------|----------------------------------------------|
| `policyholder_id`   | string   | Primary key — unique policyholder identifier |
| `name`              | string   | Full name of the policyholder                |
| `policy_type`       | string   | Type of policy (auto, home, commercial)      |
| `effective_date`    | date     | Policy effective date                        |
| `risk_tier`         | string   | Risk classification tier                     |
| `segment`           | string   | Customer segment                             |
| `state`             | string   | Policyholder state of residence              |

**Source table:** `dim_policyholders`
**Storage:** Lakehouse (`InsuranceLakehouse`)

---

### ENT-003: ClaimsDepartment

| Property                | Type     | Description                                  |
|-------------------------|----------|----------------------------------------------|
| `dept_id`               | string   | Primary key — department identifier          |
| `name`                  | string   | Department name                              |
| `region`                | string   | Region served                                |
| `claim_types_handled`   | string   | Comma-separated claim types                  |
| `headcount`             | integer  | Number of adjusters in department            |
| `avg_caseload`          | integer  | Average caseload per adjuster                |

**Source table:** `dim_claims_departments`
**Storage:** Lakehouse (`InsuranceLakehouse`)

---

### ENT-004: ClaimFormType

| Property                      | Type     | Description                                      |
|-------------------------------|----------|--------------------------------------------------|
| `form_type_id`                | string   | Primary key — form type identifier               |
| `name`                        | string   | Name of the claim form                           |
| `category`                    | string   | Form category (intake, investigation, closure)   |
| `regulatory_requirement`      | string   | Whether regulatory-mandated (yes/no/conditional) |
| `avg_completion_time_min`     | decimal  | Average time to complete (minutes)               |
| `applies_to_claim_types`      | string   | Applicable claim types                           |

**Source table:** `dim_claim_form_types`
**Storage:** Lakehouse (`InsuranceLakehouse`)

---

### ENT-005: CoverageType

| Property            | Type     | Description                                  |
|---------------------|----------|----------------------------------------------|
| `coverage_id`       | string   | Primary key — coverage identifier            |
| `name`              | string   | Coverage name                                |
| `line_of_business`  | string   | Line of business (personal, commercial)      |
| `limit_range`       | string   | Coverage limit range                         |
| `deductible_range`  | string   | Deductible range                             |

**Source table:** `dim_coverage_types`
**Storage:** Lakehouse (`InsuranceLakehouse`)

---

### ENT-006: ServiceProvider

| Property                | Type     | Description                                  |
|-------------------------|----------|----------------------------------------------|
| `provider_id`           | string   | Primary key — provider identifier            |
| `name`                  | string   | Provider name                                |
| `type`                  | string   | Provider type (repair, medical, legal)       |
| `region`                | string   | Service region                               |
| `avg_turnaround_days`   | decimal  | Average service turnaround in days           |

**Source table:** `dim_service_providers`
**Storage:** Lakehouse (`InsuranceLakehouse`)

---

## Relationship Types

### REL-001: handles_claims_for

| Field       | Value                                                        |
|-------------|--------------------------------------------------------------|
| Source      | Adjuster (ENT-001)                                           |
| Target      | Policyholder (ENT-002)                                       |
| Cardinality | Many-to-Many                                                 |
| Description | Adjusters handle claims on behalf of policyholders           |
| Join Path   | `fact_claim_lifecycle.adjuster_id → fact_claim_lifecycle.policyholder_id` |

### REL-002: belongs_to_dept

| Field       | Value                                                        |
|-------------|--------------------------------------------------------------|
| Source      | Adjuster (ENT-001)                                           |
| Target      | ClaimsDepartment (ENT-003)                                   |
| Cardinality | Many-to-One                                                  |
| Description | Adjusters belong to a claims department                      |
| Join Path   | `dim_adjusters.department → dim_claims_departments.name`     |

### REL-003: covered_by

| Field       | Value                                                        |
|-------------|--------------------------------------------------------------|
| Source      | Policyholder (ENT-002)                                       |
| Target      | CoverageType (ENT-005)                                       |
| Cardinality | Many-to-Many                                                 |
| Description | Policyholders are covered by one or more coverage types      |
| Join Path   | `dim_policyholders.policy_type → dim_coverage_types.line_of_business` |

### REL-004: requires_form

| Field       | Value                                                        |
|-------------|--------------------------------------------------------------|
| Source      | CoverageType (ENT-005)                                       |
| Target      | ClaimFormType (ENT-004)                                      |
| Cardinality | One-to-Many                                                  |
| Description | Coverage types require specific claim forms for processing   |
| Join Path   | `dim_coverage_types.name → dim_claim_form_types.applies_to_claim_types` |

### REL-005: served_by

| Field       | Value                                                        |
|-------------|--------------------------------------------------------------|
| Source      | ClaimsDepartment (ENT-003)                                   |
| Target      | ServiceProvider (ENT-006)                                    |
| Cardinality | Many-to-Many                                                 |
| Description | Departments are served by external service providers         |
| Join Path   | `dim_claims_departments.region → dim_service_providers.region` |

---

## Contextualizations

### Event Fact Contextualizations (Eventhouse)

| ID       | Name                         | Fact Table                    | Entities Involved                          | Key Metrics                                          |
|----------|------------------------------|-------------------------------|--------------------------------------------|------------------------------------------------------|
| CTX-001  | claims_doc_events            | fact_claims_doc_events        | Adjuster, ClaimFormType                    | duration_minutes, error_count, regulatory_flag       |
| CTX-002  | claims_system_clicks         | fact_claims_system_clicks     | Adjuster                                   | duration_ms, idle_before_ms, error_code              |
| CTX-003  | claim_lifecycle              | fact_claim_lifecycle          | Adjuster, Policyholder                     | total_doc_hours, fnol→close duration                 |
| CTX-004  | claim_status_changes         | fact_claim_status_changes     | Adjuster                                   | time_in_previous_status_hours, documentation_required |
| CTX-005  | field_inspections            | fact_field_inspections        | Adjuster                                   | travel_time_min, inspection_time_min, report_time_min |
| CTX-006  | claim_handoffs               | fact_claim_handoffs           | Adjuster (from), Adjuster (to)             | doc_transfer_time_min, reason                        |
| CTX-007  | fraud_alerts                 | fact_fraud_alerts             | Adjuster                                   | investigation_time_min, severity, action_taken        |
| CTX-008  | verification_scans           | fact_verification_scans       | Adjuster                                   | result, discrepancy_flag, document_source            |
| CTX-009  | underwriting_docs            | fact_underwriting_docs        | (Underwriter via underwriter_id)           | risk_assessment_time_min, form_count, approval_status |

### Batch Fact Contextualizations (Lakehouse)

| ID       | Name                         | Fact Table                        | Entities Involved                  | Key Metrics                                              |
|----------|------------------------------|-----------------------------------|------------------------------------|----------------------------------------------------------|
| CTX-010  | adjuster_wellness            | fact_adjuster_wellness            | Adjuster, ClaimsDepartment         | caseload_count, burnout_risk_score, overtime_hours        |
| CTX-011  | claim_accuracy               | fact_claim_accuracy               | Adjuster                           | reopened_flag, settlement_variance_pct, documentation_completeness_pct |
| CTX-012  | policyholder_satisfaction    | fact_policyholder_satisfaction    | Policyholder                       | csat_score, communication_rating, speed_rating           |

### Stream Contextualizations (Eventhouse)

| ID       | Name                         | Stream Table                      | Entities Involved       | Key Metrics                                    |
|----------|------------------------------|-----------------------------------|-------------------------|------------------------------------------------|
| CTX-013  | live_system_clicks           | stream_claims_system_clicks       | Adjuster                | duration_ms, module, action, error_code        |
| CTX-014  | live_status_changes          | stream_claim_status_changes       | Adjuster                | from_status, to_status, trigger, auto_vs_manual |
| CTX-015  | live_customer_contacts       | stream_customer_contacts          | Policyholder            | channel, sentiment, wait_time_sec              |
| CTX-016  | live_field_location          | stream_field_adjuster_location    | Adjuster                | lat, lon, is_at_inspection, dwell_time_min     |
| CTX-017  | live_fraud_alerts            | stream_fraud_alerts               | (claim-level)           | risk_score, pattern_type, related_claims_count |

---

## Data Storage Mapping

| Storage Layer   | Resource Name           | Tables Stored                                                                                                  |
|-----------------|-------------------------|----------------------------------------------------------------------------------------------------------------|
| **Lakehouse**   | InsuranceLakehouse      | dim_adjusters, dim_policyholders, dim_claims_departments, dim_claim_form_types, dim_coverage_types, dim_service_providers, fact_adjuster_wellness, fact_claim_accuracy, fact_policyholder_satisfaction |
| **Eventhouse**  | InsuranceEventhouse     | fact_claims_doc_events, fact_claims_system_clicks, fact_claim_lifecycle, fact_claim_status_changes, fact_field_inspections, fact_claim_handoffs, fact_fraud_alerts, fact_verification_scans, fact_underwriting_docs |
| **KQL DB**      | InsuranceKQLDB          | stream_claims_system_clicks, stream_claim_status_changes, stream_customer_contacts, stream_field_adjuster_location, stream_fraud_alerts |

---

## Ontology Visualization

```
                    ┌──────────────────────┐
                    │   ClaimsDepartment   │
                    │      (ENT-003)       │
                    └──────────┬───────────┘
                               │
                    belongs_to_dept (REL-002)
                               │
                               ▼
┌───────────────┐   handles_claims_for   ┌──────────────────┐   covered_by    ┌────────────────┐
│   Adjuster    │──────(REL-001)────────▶│  Policyholder    │───(REL-003)───▶│  CoverageType  │
│  (ENT-001)    │                        │    (ENT-002)     │                │   (ENT-005)    │
└───────┬───────┘                        └──────────────────┘                └───────┬────────┘
        │                                                                            │
        │  ┌─ CTX-001: claims_doc_events                              requires_form (REL-004)
        │  ├─ CTX-002: claims_system_clicks                                          │
        │  ├─ CTX-003: claim_lifecycle                                               ▼
        │  ├─ CTX-004: claim_status_changes                          ┌────────────────────┐
        │  ├─ CTX-005: field_inspections                             │  ClaimFormType     │
        │  ├─ CTX-006: claim_handoffs                                │    (ENT-004)       │
        │  ├─ CTX-007: fraud_alerts                                  └────────────────────┘
        │  ├─ CTX-008: verification_scans
        │  └─ CTX-010: adjuster_wellness                  served_by (REL-005)
        │                                    ┌──────────────────┐──────────────▶┌──────────────────┐
        │                                    │ ClaimsDepartment │               │ ServiceProvider  │
        │                                    │    (ENT-003)     │               │   (ENT-006)      │
        └────────────────────────────────────┘                  │               └──────────────────┘
                                                                │
                                              CTX-012: policyholder_satisfaction
                                              CTX-015: live_customer_contacts
```

---

## Key Analytical Queries

### 1. Claims Documentation Time per Adjuster

> How much time does each adjuster spend on claim documentation vs. regulatory forms?

- **Entities:** Adjuster, ClaimFormType
- **Contextualization:** CTX-001 (claims_doc_events)
- **Metrics:** SUM(duration_minutes) grouped by adjuster and regulatory_flag
- **Insight:** Identifies adjusters spending disproportionate time on regulatory documentation

### 2. Claim Lifecycle Documentation Cascade

> What is the total documentation overhead from FNOL to close for each claim?

- **Entities:** Adjuster, Policyholder
- **Contextualization:** CTX-003 (claim_lifecycle)
- **Metrics:** total_doc_hours, DATEDIFF(fnol_date, close_date)
- **Insight:** Reveals claims where documentation consumes a large fraction of total lifecycle

### 3. Field Inspection Report Burden

> How much time do field adjusters spend writing reports vs. performing inspections?

- **Entities:** Adjuster
- **Contextualization:** CTX-005 (field_inspections)
- **Metrics:** report_time_min / (inspection_time_min + report_time_min)
- **Insight:** Quantifies the report-writing burden relative to actual inspection work

### 4. Fraud Investigation Documentation Overhead

> What is the documentation overhead of fraud investigations by alert severity?

- **Entities:** Adjuster
- **Contextualization:** CTX-007 (fraud_alerts)
- **Metrics:** investigation_time_min grouped by severity and alert_type
- **Insight:** Reveals whether low-severity alerts consume disproportionate documentation effort

### 5. Claim Handoff Documentation Gaps

> How much time is lost to documentation transfers during claim handoffs?

- **Entities:** Adjuster (from), Adjuster (to)
- **Contextualization:** CTX-006 (claim_handoffs)
- **Metrics:** doc_transfer_time_min, frequency of handoffs by reason
- **Insight:** Identifies handoff bottlenecks where documentation transfer adds delay to claims processing
