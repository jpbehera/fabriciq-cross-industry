# Retail Store Operations — Sample Dataset

## Overview

A **23-CSV** sample dataset modelling the **administrative documentation burden**
faced by store managers and merchandising teams in a multi-format retail chain.
Store managers spend 30–50% of their time on inventory documentation, compliance
reporting, planogram audits, and workforce scheduling paperwork — time that could
be spent on the sales floor driving customer engagement and conversion.

This dataset is designed to work with the **generic cross-industry notebooks**
in `cross_industry_notebooks/` (notebooks 00–07) using the pre-filled
`Retail_Config.ipynb` configuration.

---

## Quick Start

1. Upload the `data/` folder to your Fabric Lakehouse under  
   `Files/retail_store_operations/data/`.
2. Import all **cross-industry notebooks** (00–07) plus `Retail_Config.ipynb`
   into a Fabric workspace.
3. Run `Retail_Config` to set artifact names, then run the notebooks in order.

---

## Table Inventory (23 Tables, 2,555 Data Rows)

### Dimensions (6 tables — 105 rows) → Lakehouse + Warehouse

| File | Rows | Description |
|------|------|-------------|
| `dim_store_managers.csv` | 25 | Store managers with store assignment, certifications, avg weekly floor hours |
| `dim_stores.csv` | 30 | Store locations with district, format, sq footage, headcount, revenue tier |
| `dim_districts.csv` | 5 | Districts across 5 regions with store counts and performance ratings |
| `dim_report_types.csv` | 18 | Report taxonomy — 18 types across Sales, Inventory, LP, Compliance, HR, Ops |
| `dim_product_categories.csv` | 15 | Product categories with department, planogram reset frequency, shrinkage risk |
| `dim_vendor_partners.csv` | 12 | Vendor partners with delivery frequency and documentation requirements |

### Batch Facts (6 tables — 505 rows) → Lakehouse + Warehouse

| File | Rows | Description |
|------|------|-------------|
| `fact_compliance_doc_events.csv` | 180 | Report filing events with duration, status, overdue tracking |
| `fact_inventory_audits.csv` | 90 | Cycle count audits with variance %, documentation time, scan counts |
| `fact_manager_wellness.csv` | 25 | Per-manager burnout metrics: admin burden, work-life balance, floor time % |
| `fact_audit_quality.csv` | 60 | Planogram compliance, inventory accuracy, safety checklist completion |
| `fact_customer_satisfaction.csv` | 30 | Per-store NPS, mystery shopper scores, wait time, staff helpfulness |
| `fact_scheduling_events.csv` | 120 | Scheduling tasks: creation, time-off, coverage gaps, overtime approvals |

### Event Facts (6 tables — 1,545 rows) → Eventhouse + Warehouse

| File | Rows | KQL Name | Description |
|------|------|----------|-------------|
| `fact_pos_transactions.csv` | 500 | `pos_transactions` | POS sales, returns, voids, price overrides |
| `fact_inventory_scans.csv` | 250 | `inventory_scans` | Barcode scans with expected vs actual qty variance |
| `fact_store_incidents.csv` | 35 | `store_incidents` | Theft, safety, complaints with documentation time |
| `fact_shift_handoffs.csv` | 60 | `shift_handoffs` | Manager shift changes with open task counts |
| `fact_retail_system_clicks.csv` | 300 | `retail_system_clicks` | POS/WFM/Inventory system clickstream |
| `fact_associate_presence.csv` | 400 | `associate_presence` | Zone-level associate tracking (floor vs back office) |

### Streaming (5 tables — 400 rows) → Eventhouse

| File | Rows | KQL Name | Description |
|------|------|----------|-------------|
| `stream_pos_transactions.csv` | 80 | `pos_transactions_rt` | Real-time transaction feed with void/return flags |
| `stream_foot_traffic.csv` | 80 | `foot_traffic` | Sensor-based customer flow by zone |
| `stream_inventory_scans.csv` | 80 | `inventory_scans_rt` | Live cycle count scans with discrepancies |
| `stream_store_incidents.csv` | 80 | `store_incidents_rt` | Real-time incident alerts with response times |
| `stream_associate_location.csv` | 80 | `associate_location` | Badge/RTLS pings — zone, movement, customer-facing flag |

---

## Data Stories & Embedded Signals

### 1. Admin Burden Burnout — Karen Weston (MGR-003)
- Store Manager, Northeast region
- **Admin burden score:** 9.2 / 10 — highest in the company
- **Work-life balance:** 2.5 / 10
- **Overtime hours:** 14 per month
- **Floor time:** 28% (vs. company goal of 50%+)
- Compliance doc duration: 30–90 minutes (company avg ≈ 10–60 min)
- System click dwell time: 2–15 seconds (longest in company)
- *Signal:* Excessive time in back office on reports → lowest store NPS

### 2. Floor Presence Champion — David Park (MGR-009)
- Store Manager, Southwest region
- **Admin burden score:** 3.0 / 10 — lowest in the company
- **Work-life balance:** 8.5 / 10
- **Overtime hours:** 1 per month
- **Floor time:** 68% (highest in company)
- Compliance doc duration: 5–20 minutes (fastest completer)
- Store NPS: 75–90 (highest in chain)
- *Signal:* More floor time → better customer satisfaction → higher conversion

### 3. Incident Documentation Burden — Rachel Torres (MGR-015)
- Store Manager handling disproportionate incident volume
- **Admin burden score:** 7.5 / 10
- **Work-life balance:** 4.0 / 10
- Incident documentation time: 30–75 minutes per incident
- 25% of all incidents route to MGR-015
- *Signal:* High-incident stores need dedicated LP support to relieve manager burden

### 4. High-Shrinkage Categories
- Fresh Produce, Dairy & Frozen, Meat & Seafood, Consumer Electronics, Toys & Games
  are flagged as "high" shrinkage risk
- These categories show larger negative variance in inventory audits (-0.5% to -8.0%)
- *Signal:* More frequent, more time-consuming cycle counts → higher documentation load

---

## Foreign Key Relationships

```
dim_store_managers.manager_id ──→ fact_compliance_doc_events.manager_id
                                  fact_inventory_audits.manager_id
                                  fact_manager_wellness.manager_id
                                  fact_scheduling_events.manager_id
                                  fact_store_incidents.manager_id
                                  fact_shift_handoffs.from_manager_id
                                  fact_shift_handoffs.to_manager_id
                                  fact_retail_system_clicks.manager_id

dim_stores.store_id ─────────────→ dim_store_managers.store_id
                                  fact_compliance_doc_events.store_id
                                  fact_inventory_audits.store_id
                                  fact_manager_wellness.store_id
                                  fact_customer_satisfaction.store_id
                                  fact_scheduling_events.store_id
                                  fact_pos_transactions.store_id
                                  fact_inventory_scans.store_id
                                  fact_store_incidents.store_id
                                  fact_shift_handoffs.store_id
                                  fact_associate_presence.store_id
                                  stream_pos_transactions.store_id
                                  stream_foot_traffic.store_id
                                  stream_inventory_scans.store_id
                                  stream_store_incidents.store_id
                                  stream_associate_location.store_id

dim_districts.district_id ───────→ dim_stores.district_id

dim_report_types.report_type_id ─→ fact_compliance_doc_events.report_type_id

dim_product_categories.category_id → fact_inventory_audits.category_id
                                     fact_audit_quality.category_id
```

---

## Fabric Artifact Mapping

| Artifact | Name | Tables |
|----------|------|--------|
| Lakehouse | `RetailLakehouse` | 12 (6 dim + 6 batch facts) |
| Warehouse | `Retail_Datawarehouse` | 18 (6 dim + 6 batch + 6 event facts) |
| Eventhouse | `retail_rt_store` | 11 (6 event facts + 5 streams) |
| Ontology | `RetailOpsOntology` | 6 entity types, 5 relationships, 6 contextualizations |
| Data Agent | `RetailQA` | Natural-language queries |
| Ops Agent | `RetailDocBurden` | Documentation burden analysis |
| Semantic Model | `Retail_Ops_Model` | Power BI reporting |

---

## File Listing

```
datasets/retail_store_operations/
├── README.md                              ← this file
└── data/
    ├── dim_store_managers.csv              (25 rows)
    ├── dim_stores.csv                      (30 rows)
    ├── dim_districts.csv                    (5 rows)
    ├── dim_report_types.csv               (18 rows)
    ├── dim_product_categories.csv         (15 rows)
    ├── dim_vendor_partners.csv            (12 rows)
    ├── fact_compliance_doc_events.csv    (180 rows)
    ├── fact_inventory_audits.csv          (90 rows)
    ├── fact_manager_wellness.csv          (25 rows)
    ├── fact_audit_quality.csv             (60 rows)
    ├── fact_customer_satisfaction.csv      (30 rows)
    ├── fact_scheduling_events.csv        (120 rows)
    ├── fact_pos_transactions.csv         (500 rows)
    ├── fact_inventory_scans.csv          (250 rows)
    ├── fact_store_incidents.csv           (35 rows)
    ├── fact_shift_handoffs.csv            (60 rows)
    ├── fact_retail_system_clicks.csv     (300 rows)
    ├── fact_associate_presence.csv       (400 rows)
    ├── stream_pos_transactions.csv        (80 rows)
    ├── stream_foot_traffic.csv            (80 rows)
    ├── stream_inventory_scans.csv         (80 rows)
    ├── stream_store_incidents.csv         (80 rows)
    └── stream_associate_location.csv      (80 rows)
```
