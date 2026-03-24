# Law Firm Operations — Sample Dataset

## Overview

A **23-CSV** sample dataset modelling the **documentation burden** faced by attorneys
and paralegals in a mid-to-large law firm. Attorneys typically spend 40–60 % of
their time on non-billable documentation—time entries, discovery review, court
filings, contract lifecycle tracking, and matter administration. At billing
rates of $300–$1,000+/hr, every unnecessary documentation minute represents
direct revenue loss.

This dataset is designed to work with the **generic cross-industry notebooks**
in `cross_industry_notebooks/` (notebooks 00–07) using the pre-filled
`LawFirms_Config.ipynb` configuration.

---

## Quick Start

1. Upload the `data/` folder to your Fabric Lakehouse under  
   `Files/law_firm_operations/data/`.
2. Import all **cross-industry notebooks** (00–07) plus `LawFirms_Config.ipynb`
   into a Fabric workspace.
3. Run `LawFirms_Config` to set artifact names, then run the notebooks in order.

---

## Table Inventory (23 Tables, 2,340 Data Rows)

### Dimensions (6 tables — 135 rows) → Lakehouse + Warehouse

| File | Rows | Description |
|------|------|-------------|
| `dim_attorneys.csv` | 30 | Attorneys with role, practice group, billing rate, bar number |
| `dim_clients.csv` | 25 | Client organizations with industry, billing arrangement, revenue |
| `dim_matters.csv` | 40 | Legal matters with practice area, type, budget, status |
| `dim_legal_task_types.csv` | 20 | Task taxonomy (14 billable, 6 non-billable) with avg duration |
| `dim_practice_groups.csv` | 8 | Practice groups with headquarters office |
| `dim_courts.csv` | 12 | Federal, state, bankruptcy, and administrative courts |

### Batch Facts (6 tables — 985 rows) → Lakehouse + Warehouse

| File | Rows | Description |
|------|------|-------------|
| `fact_time_entries.csv` | 500 | Billable hour time entries with narrative, entry time, write-down % |
| `fact_discovery_events.csv` | 150 | E-discovery review events with docs reviewed, privilege flags |
| `fact_attorney_wellness.csv` | 30 | Burnout & wellness metrics per attorney |
| `fact_work_product_quality.csv` | 200 | Document accuracy, revision counts, review cycles |
| `fact_client_satisfaction.csv` | 25 | Per-client satisfaction scores and NPS |
| `fact_matter_performance.csv` | 80 | Monthly financial performance per matter |

### Event Facts (6 tables — 820 rows) → Eventhouse + Warehouse

| File | Rows | KQL Name | Description |
|------|------|----------|-------------|
| `fact_dms_interactions.csv` | 500 | `dms_interactions` | Document management system interactions (5 DMS platforms) |
| `fact_filing_events.csv` | 60 | `filing_events` | Court filing events with deadline tracking |
| `fact_contract_events.csv` | 80 | `contract_events` | Contract lifecycle stages with redline counts |
| `fact_matter_transfers.csv` | 20 | `matter_transfers` | Attorney-to-attorney matter handoffs |
| `fact_deadline_alerts.csv` | 100 | `deadline_alerts` | Filing deadlines, statutes of limitations, discovery cutoffs |
| `fact_billing_events.csv` | 60 | `billing_events` | Invoice events with write-downs and dispute flags |

### Streaming (5 tables — 400 rows) → Eventhouse

| File | Rows | KQL Name | Description |
|------|------|----------|-------------|
| `stream_dms_activity.csv` | 80 | `dms_activity` | Real-time document management activity |
| `stream_time_tracking.csv` | 80 | `time_tracking` | Real-time time capture with billable flags |
| `stream_court_deadlines.csv` | 80 | `court_deadlines` | Upcoming court deadlines with priority scoring |
| `stream_discovery_progress.csv` | 80 | `discovery_progress` | Live discovery review pace and privilege calls |
| `stream_client_communications.csv` | 80 | `client_communications` | Client email/phone/video interactions |

---

## Data Stories & Embedded Signals

### 1. Attorney Burnout — Emily Richardson (ATT-003)
- Senior Associate, Corporate/M&A practice
- **Admin burden:** 9.5 / 10 — highest in the firm
- **Work-life balance:** 2.0 / 10
- **Overtime hours:** 24 per month
- Time entry duration: 18–45 minutes (firm avg ≈ 8–15 min)
- *Signal:* Excessive documentation time is a burnout driver

### 2. Revenue Leakage — Maria Gonzalez (ATT-009)
- Partner, Litigation practice
- **Write-downs:** 8–30 % (firm avg ≈ 2–8 %)
- **Billable pressure:** 9.5 / 10
- **Work product accuracy:** 72–88 % (firm avg ≈ 88–98 %)
- Matter realization rates: 55–75 % (vs. firm avg 80–95 %)
- *Signal:* Under-documented or poorly documented work → client disputes → write-downs

### 3. Non-Billable Task Analysis
- 6 of 20 legal task types are non-billable: Time Entry, Billing Review,
  Conflict Check, Matter Admin, Pro Bono, CLE/Training
- These tasks consume significant attorney hours with zero revenue generation
- *Signal:* Automate or reduce non-billable documentation to recover billable capacity

### 4. DMS Fragmentation
- 5 separate DMS platforms in use: iManage, NetDocuments, Clio, Relativity, Westlaw
- ATT-003 has longest average DMS interaction durations
- *Signal:* Context-switching between platforms increases documentation time

---

## Foreign Key Relationships

```
dim_attorneys.attorney_id ────→ fact_time_entries.attorney_id
                               fact_discovery_events.attorney_id
                               fact_attorney_wellness.attorney_id
                               fact_work_product_quality.attorney_id
                               fact_dms_interactions.attorney_id
                               fact_filing_events.attorney_id
                               fact_contract_events.attorney_id
                               fact_billing_events.attorney_id
                               stream_dms_activity.attorney_id
                               stream_time_tracking.attorney_id
                               stream_discovery_progress.attorney_id

dim_clients.client_id ────────→ fact_client_satisfaction.client_id
                               fact_billing_events.client_id
                               stream_client_communications.client_id

dim_matters.matter_id ────────→ fact_time_entries.matter_id
                               fact_discovery_events.matter_id
                               fact_work_product_quality.matter_id
                               fact_matter_performance.matter_id
                               fact_filing_events.matter_id
                               fact_contract_events.matter_id
                               fact_matter_transfers.matter_id
                               fact_deadline_alerts.matter_id
                               stream_court_deadlines.matter_id

dim_legal_task_types.task_type_id → fact_time_entries.task_type_id

dim_practice_groups.group_id ──→ dim_attorneys.practice_group_id

dim_courts.court_id ──────────→ fact_filing_events.court_id
                               fact_deadline_alerts.court_id
                               stream_court_deadlines.court_id
```

---

## Fabric Artifact Mapping

| Artifact | Name | Tables |
|----------|------|--------|
| Lakehouse | `LawFirmLakehouse` | 12 (6 dim + 6 batch facts) |
| Warehouse | `LawFirm_Datawarehouse` | 18 (6 dim + 6 batch + 6 event facts) |
| Eventhouse | `lawfirm_rt_store` | 11 (6 event facts + 5 streams) |
| Ontology | `LawFirmOpsOntology` | 6 entity types, 5 relationships, 6 contextualizations |
| Data Agent | `LawFirmQA` | Natural-language queries |
| Ops Agent | `LawFirmDocBurden` | Documentation burden analysis |
| Semantic Model | `Law_Firm_Ops_Model` | Power BI reporting |

---

## File Listing

```
datasets/law_firm_operations/
├── README.md                          ← this file
└── data/
    ├── dim_attorneys.csv               (30 rows)
    ├── dim_clients.csv                 (25 rows)
    ├── dim_matters.csv                 (40 rows)
    ├── dim_legal_task_types.csv        (20 rows)
    ├── dim_practice_groups.csv          (8 rows)
    ├── dim_courts.csv                  (12 rows)
    ├── fact_time_entries.csv          (500 rows)
    ├── fact_discovery_events.csv      (150 rows)
    ├── fact_attorney_wellness.csv      (30 rows)
    ├── fact_work_product_quality.csv  (200 rows)
    ├── fact_client_satisfaction.csv    (25 rows)
    ├── fact_matter_performance.csv     (80 rows)
    ├── fact_dms_interactions.csv      (500 rows)
    ├── fact_filing_events.csv          (60 rows)
    ├── fact_contract_events.csv        (80 rows)
    ├── fact_matter_transfers.csv       (20 rows)
    ├── fact_deadline_alerts.csv       (100 rows)
    ├── fact_billing_events.csv         (60 rows)
    ├── stream_dms_activity.csv         (80 rows)
    ├── stream_time_tracking.csv        (80 rows)
    ├── stream_court_deadlines.csv      (80 rows)
    ├── stream_discovery_progress.csv   (80 rows)
    └── stream_client_communications.csv(80 rows)
```
