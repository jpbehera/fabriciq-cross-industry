# Finance (Banking & Wealth Management) — Sample Dataset

## Overview

This dataset models the **KYC/AML Documentation Burden** facing financial advisors
at a mid-size wealth management firm. Advisors spend 40–60 % of their time on
regulatory documentation, KYC/AML paperwork, and compliance filing rather than
serving clients. The data covers **Q4 2025** operations across 5 branches,
25 advisors, and 40 client accounts.

## Use Cases

| # | Use Case | Primary Tables |
|---|----------|----------------|
| 1 | KYC/AML Documentation Burden | `fact_compliance_doc_events`, `fact_kyc_verifications`, `dim_document_types` |
| 2 | Loan Processing Cycle Time | `fact_loan_processing`, `fact_case_escalations`, `dim_products` |
| 3 | Trade Compliance Documentation | `fact_trade_compliance`, `stream_trading_events`, `dim_regulations` |
| 4 | Advisor Productivity Analytics | `fact_advisor_wellness`, `fact_core_banking_interactions`, `stream_core_banking_clicks` |
| 5 | Regulatory Exam Readiness | `fact_exam_readiness`, `fact_document_quality`, `dim_regulations` |

## Key Personas (embedded data stories)

| Advisor | Role | Story |
|---------|------|-------|
| **ADV-003** (Jennifer Walsh) | Financial Advisor | Extreme compliance burden — longest doc times, highest error rates, lowest NPS |
| **ADV-009** (Raj Patel) | Wealth Manager | Most efficient — fastest doc completion, highest AUM ($180M+), best client satisfaction |
| **ADV-015** (Marcus Green) | Compliance Analyst | Alert fatigue — receives 30 % of all regulatory alerts, slowest response times |

## Table Inventory (23 tables, ~1,342 rows)

### Dimensions (6 tables — 117 rows)

| Table | Rows | Description |
|-------|------|-------------|
| `dim_advisors` | 25 | Financial advisors, loan officers, compliance analysts |
| `dim_clients` | 40 | Client accounts with risk profiles and segments |
| `dim_branches` | 5 | Branch locations across 5 US regions |
| `dim_document_types` | 20 | KYC/AML, lending, trading, and internal document types |
| `dim_products` | 15 | Loan, investment, and deposit products |
| `dim_regulations` | 12 | Federal and state regulations (BSA, PATRIOT, Reg BI, etc.) |

### Batch Facts (6 tables — 335 rows) → Lakehouse + Warehouse

| Table | Rows | Description |
|-------|------|-------------|
| `fact_compliance_doc_events` | 150 | Compliance documentation sessions with duration and error counts |
| `fact_loan_processing` | 45 | Loan pipeline stages, durations, and rejection reasons |
| `fact_advisor_wellness` | 25 | Monthly wellness survey — workload, overtime, burnout risk |
| `fact_document_quality` | 60 | Document error rates, rejection rates, audit findings |
| `fact_client_satisfaction` | 40 | Client NPS, responsiveness, onboarding experience |
| `fact_exam_readiness` | 15 | Regulatory exam preparation status per branch |

### Event Facts (6 tables — 490 rows) → Eventhouse + Warehouse

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `fact_kyc_verifications` | 80 | `kyc_verifications` | Identity/address/income verification events |
| `fact_trade_compliance` | 60 | `trade_compliance` | Pre- and post-trade documentation time |
| `fact_core_banking_interactions` | 200 | `core_banking_interactions` | System module clicks, idle time, errors |
| `fact_case_escalations` | 30 | `case_escalations` | Loan/compliance case escalations with delays |
| `fact_regulatory_alerts` | 45 | `regulatory_alerts` | AML/fraud/sanctions alerts and response times |
| `fact_branch_presence` | 75 | `branch_presence` | Daily arrival/departure, remote and meeting hours |

### Streaming Tables (5 tables — 400 rows) → Eventhouse only

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `stream_trading_events` | 80 | `trading_events` | Real-time trade execution and filing status |
| `stream_core_banking_clicks` | 80 | `core_banking_clicks` | Clickstream from core banking UI |
| `stream_client_interactions` | 80 | `client_interactions` | Phone/email/video client touchpoints |
| `stream_compliance_alerts` | 80 | `compliance_alerts` | Real-time AML/fraud alert stream |
| `stream_branch_presence` | 80 | `branch_presence_rt` | Badge/VPN presence pings |

## Foreign Key Relationships

```
dim_advisors.advisor_id  ──→  fact_compliance_doc_events.advisor_id
                          ──→  fact_loan_processing.officer_id
                          ──→  fact_advisor_wellness.advisor_id
                          ──→  fact_document_quality.advisor_id
                          ──→  fact_client_satisfaction.advisor_id
                          ──→  fact_kyc_verifications.advisor_id
                          ──→  fact_trade_compliance.advisor_id
                          ──→  fact_core_banking_interactions.advisor_id
                          ──→  fact_case_escalations.advisor_id
                          ──→  fact_regulatory_alerts.advisor_id
                          ──→  fact_branch_presence.advisor_id

dim_clients.client_id    ──→  fact_compliance_doc_events.client_id
                          ──→  fact_loan_processing.client_id
                          ──→  fact_client_satisfaction.client_id
                          ──→  fact_kyc_verifications.client_id
                          ──→  fact_trade_compliance.client_id
                          ──→  fact_case_escalations.client_id
                          ──→  fact_regulatory_alerts.client_id

dim_branches.branch_id   ──→  dim_advisors.branch_id
                          ──→  fact_advisor_wellness.branch_id
                          ──→  fact_exam_readiness.branch_id
                          ──→  fact_branch_presence.branch_id

dim_document_types.doc_type_id ──→  fact_compliance_doc_events.doc_type_id
                                ──→  fact_document_quality.doc_type_id

dim_regulations.regulation_id  ──→  fact_exam_readiness.regulation_id
```

## Usage

1. Upload the `data/` folder to your Fabric Lakehouse Files area
2. Open `Finance_Config.ipynb` in the `cross_industry_notebooks/` folder
3. Update `EVENTHOUSE_CLUSTER_URI` and `EVENTHOUSE_DATABASE` with your values
4. Run the generic notebooks (`01` through `07`) which import this config via `%run ./Finance_Config`

## Data Period

All dates fall within **Q4 2025** (October–December 2025).
Streaming timestamps are concentrated around **December 15, 2025** starting at 09:30 UTC.
