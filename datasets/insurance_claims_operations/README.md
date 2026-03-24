# Insurance (Claims Operations) — Sample Dataset

## Overview

This dataset models the **Claims Adjuster Documentation Burden** at a mid-size
property & casualty insurer. Claims adjusters spend 50–70% of their time on
documentation: filling FNOL forms, requesting records, writing damage assessments,
and responding to regulatory inquiries — instead of investigating and settling claims.
The data covers **Q4 2025** operations across 5 departments, 30 adjusters, and
50 policyholders.

## Use Cases

| # | Use Case | Primary Tables |
|---|----------|----------------|
| 1 | Claims Documentation Burden Analysis | `fact_claims_doc_events`, `fact_claim_lifecycle`, `dim_claim_form_types` |
| 2 | FNOL Optimization | `fact_claim_lifecycle`, `stream_claim_status_changes`, `dim_policyholders` |
| 3 | Catastrophe (CAT) Event Response | `stream_claim_status_changes`, `stream_field_adjuster_location`, `fact_adjuster_wellness` |
| 4 | Fraud Investigation Documentation | `fact_fraud_alerts`, `stream_fraud_alerts`, `fact_claim_accuracy` |
| 5 | Underwriting Documentation Efficiency | `fact_underwriting_docs`, `dim_coverage_types`, `dim_claim_form_types` |

## Key Personas (embedded data stories)

| Adjuster | Role | Story |
|----------|------|-------|
| **ADJ-003** (Lisa Martinez) | Claims Adjuster | Extreme doc burden — longest form times, highest error rates, caseload of 48, 18 hrs overtime, lowest CSAT |
| **ADJ-012** (Brian Nguyen) | Senior Claims Adjuster | Most efficient — fastest doc completion, fewest errors, best CSAT and settlement accuracy |
| **ADJ-022** (Karen Phillips) | SIU Investigator | Fraud specialist overload — handles 30% of fraud alerts, longest investigation times, high burnout |

## Table Inventory (23 tables, ~1,637 rows)

### Dimensions (6 tables — 142 rows)

| Table | Rows | Description |
|-------|------|-------------|
| `dim_adjusters` | 30 | Claims adjusters, field adjusters, underwriters, SIU investigators |
| `dim_policyholders` | 50 | Policyholder accounts with policy types and risk tiers |
| `dim_claims_departments` | 5 | Claims departments across 5 US regions |
| `dim_claim_form_types` | 22 | FNOL, estimates, settlement letters, SIU forms, etc. |
| `dim_coverage_types` | 15 | Auto, property, commercial, specialty coverage lines |
| `dim_service_providers` | 20 | Body shops, medical providers, legal firms, appraisers |

### Batch Facts (6 tables — 440 rows) → Lakehouse + Warehouse

| Table | Rows | Description |
|-------|------|-------------|
| `fact_claims_doc_events` | 200 | Form completion sessions with duration and error counts |
| `fact_claim_lifecycle` | 60 | Full claim pipeline: FNOL → assignment → reserve → settlement → close |
| `fact_adjuster_wellness` | 30 | Monthly wellness survey — caseload, overtime, burnout risk |
| `fact_claim_accuracy` | 60 | Reopened claims, settlement variance, documentation completeness |
| `fact_policyholder_satisfaction` | 50 | CSAT, communication rating, speed rating, complaint flags |
| `fact_underwriting_docs` | 40 | Risk assessment forms, loss run analyses, approval status |

### Event Facts (6 tables — 655 rows) → Eventhouse + Warehouse

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `fact_claim_status_changes` | 180 | `claim_status_changes` | Claim stage transitions with documentation requirements |
| `fact_claims_system_clicks` | 300 | `claims_system_clicks` | Guidewire/Duck Creek UI interactions |
| `fact_field_inspections` | 45 | `field_inspections` | Field visits with travel, inspection, and report times |
| `fact_claim_handoffs` | 25 | `claim_handoffs` | Adjuster-to-adjuster claim transfers |
| `fact_fraud_alerts` | 35 | `fraud_alerts` | SIU fraud flags with investigation time |
| `fact_verification_scans` | 70 | `verification_scans` | Coverage and document verification events |

### Streaming Tables (5 tables — 400 rows) → Eventhouse only

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `stream_claim_status_changes` | 80 | `claim_status_changes_rt` | Real-time claim stage transitions |
| `stream_field_adjuster_location` | 80 | `field_adjuster_location` | GPS pings for field adjusters |
| `stream_claims_system_clicks` | 80 | `claims_system_clicks_rt` | Real-time Guidewire clickstream |
| `stream_fraud_alerts` | 80 | `fraud_alerts_rt` | Real-time SIU fraud pattern flags |
| `stream_customer_contacts` | 80 | `customer_contacts` | Call center / portal inbound contacts |

## Foreign Key Relationships

```
dim_adjusters.adjuster_id  ──→  fact_claims_doc_events.adjuster_id
                            ──→  fact_claim_lifecycle.adjuster_id
                            ──→  fact_adjuster_wellness.adjuster_id
                            ──→  fact_claim_accuracy.adjuster_id
                            ──→  fact_claim_status_changes.adjuster_id
                            ──→  fact_claims_system_clicks.adjuster_id
                            ──→  fact_field_inspections.adjuster_id
                            ──→  fact_claim_handoffs.from_adjuster_id / to_adjuster_id
                            ──→  fact_fraud_alerts.adjuster_id
                            ──→  fact_verification_scans.adjuster_id

dim_policyholders.policyholder_id ──→  fact_claim_lifecycle.policyholder_id
                                   ──→  fact_policyholder_satisfaction.policyholder_id

dim_claims_departments.dept_id    ──→  dim_adjusters.department
                                   ──→  fact_adjuster_wellness.dept_id

dim_claim_form_types.form_type_id ──→  fact_claims_doc_events.form_type_id

claim_id (across tables)          ──→  fact_claims_doc_events.claim_id
                                   ──→  fact_claim_lifecycle.claim_id
                                   ──→  fact_claim_accuracy.claim_id
                                   ──→  fact_claim_status_changes.claim_id
                                   ──→  fact_field_inspections.claim_id
                                   ──→  fact_claim_handoffs.claim_id
                                   ──→  fact_fraud_alerts.claim_id
                                   ──→  fact_verification_scans.claim_id
```

## Usage

1. Upload the `data/` folder to your Fabric Lakehouse Files area
2. Open `Insurance_Config.ipynb` in the `cross_industry_notebooks/` folder
3. Update `EVENTHOUSE_CLUSTER_URI` and `EVENTHOUSE_DATABASE` with your values
4. Run the generic notebooks (`01` through `07`) which import this config via `%run ./Insurance_Config`

## Data Period

All dates fall within **Q4 2025** (October–December 2025).
Streaming timestamps are concentrated around **December 15, 2025** starting at 09:00 UTC.
