# Retail Store Operations — Ontology Design

## Overview

The **RetailStoreOpsOntology** models the documentation and administrative burden placed on
retail store managers. It captures the relationships between managers, stores, districts,
product categories, vendor partners, and report types — then contextualises those entities
with event-level facts (compliance documentation, inventory audits, scheduling, shift
handoffs, incidents, system clicks, POS transactions, associate presence) and real-time
streams (POS transactions, foot traffic, inventory scans, incidents, associate location).

The goal is to quantify how much time managers spend on paperwork, compliance reporting,
inventory counts, and administrative overhead versus customer-facing floor time, and to
surface correlations between documentation burden and store performance outcomes.

---

## Concept Mapping

| RDF / OWL Concept       | Fabric IQ Equivalent        | Description                                      |
|--------------------------|-----------------------------|--------------------------------------------------|
| `owl:Class`              | **Entity Type**             | A dimension: StoreManager, Store, District, etc.  |
| `owl:ObjectProperty`     | **Relationship Type**       | Directed edge between two entity types            |
| `owl:DatatypeProperty`   | **Property**                | Column / attribute on an entity type              |
| `rdf:type`               | **Entity Instance**         | A single row in a dimension table                 |
| _n/a_                    | **Contextualization**       | Binding an event/stream table to entity types     |
| `rdfs:label`             | **display_name**            | Human-readable name for UI display                |
| `rdfs:comment`           | **description**             | Free-text description of the concept              |

---

## Entity Types

### ENT-001 — StoreManager

| Property               | Type     | Description                                      |
|------------------------|----------|--------------------------------------------------|
| `manager_id`           | string   | **Primary key** — unique manager identifier       |
| `name`                 | string   | Full name of the store manager                    |
| `store_id`             | string   | Foreign key to the assigned store                 |
| `region`               | string   | Geographic region                                 |
| `hire_date`            | date     | Date the manager was hired                        |
| `certifications`       | string   | Comma-separated list of certifications            |
| `avg_weekly_floor_hours` | float  | Average weekly hours on the store floor           |

**Source table:** `dim_store_managers`

---

### ENT-002 — Store

| Property       | Type     | Description                                      |
|----------------|----------|--------------------------------------------------|
| `store_id`     | string   | **Primary key** — unique store identifier         |
| `name`         | string   | Store display name                                |
| `district_id`  | string   | Foreign key to district                           |
| `region`       | string   | Geographic region                                 |
| `format`       | string   | Store format (e.g., Superstore, Express, Outlet)  |
| `sq_footage`   | int      | Total square footage                              |
| `headcount`    | int      | Total number of associates                        |
| `revenue_tier` | string   | Revenue classification tier                       |

**Source table:** `dim_stores`

---

### ENT-003 — District

| Property             | Type     | Description                                      |
|----------------------|----------|--------------------------------------------------|
| `district_id`        | string   | **Primary key** — unique district identifier      |
| `name`               | string   | District display name                             |
| `region`             | string   | Geographic region                                 |
| `store_count`        | int      | Number of stores in the district                  |
| `district_manager`   | string   | Name of the district manager                      |
| `performance_rating` | string   | Current performance rating                        |

**Source table:** `dim_districts`

---

### ENT-004 — ReportType

| Property                    | Type     | Description                                      |
|-----------------------------|----------|--------------------------------------------------|
| `report_type_id`            | string   | **Primary key** — unique report type identifier   |
| `name`                      | string   | Report name (e.g., "Daily Compliance Checklist")  |
| `category`                  | string   | Report category (compliance, safety, inventory)   |
| `frequency`                 | string   | Filing frequency (daily, weekly, monthly)         |
| `avg_completion_time_min`   | float    | Average minutes to complete the report            |
| `regulatory_required`       | boolean  | Whether the report is mandated by regulation      |

**Source table:** `dim_report_types`

---

### ENT-005 — ProductCategory

| Property                     | Type     | Description                                      |
|------------------------------|----------|--------------------------------------------------|
| `category_id`                | string   | **Primary key** — unique category identifier      |
| `name`                       | string   | Category name (e.g., "Fresh Produce", "Electronics") |
| `department`                 | string   | Owning department                                 |
| `planogram_reset_frequency`  | string   | How often planogram resets occur                  |
| `shrinkage_risk_tier`        | string   | Shrinkage risk classification                     |

**Source table:** `dim_product_categories`

---

### ENT-006 — VendorPartner

| Property                       | Type     | Description                                      |
|--------------------------------|----------|--------------------------------------------------|
| `vendor_id`                    | string   | **Primary key** — unique vendor identifier        |
| `name`                         | string   | Vendor / partner company name                     |
| `category`                     | string   | Product category supplied                         |
| `delivery_frequency`           | string   | Delivery cadence (daily, biweekly, weekly)        |
| `documentation_requirements`   | string   | Required receiving documentation                  |

**Source table:** `dim_vendor_partners`

---

## Relationship Types

| ID      | Name                 | Source Entity    | Target Entity    | Cardinality | Description                                                 |
|---------|----------------------|------------------|------------------|-------------|-------------------------------------------------------------|
| REL-001 | `manages`            | StoreManager     | Store            | N : 1       | A manager is assigned to manage a store                     |
| REL-002 | `belongs_to_district`| Store            | District         | N : 1       | A store belongs to a geographic district                    |
| REL-003 | `stocks`             | Store            | ProductCategory  | N : M       | A store stocks products across multiple categories          |
| REL-004 | `partners_with`      | Store            | VendorPartner    | N : M       | A store receives deliveries from vendor partners            |
| REL-005 | `requires_report`    | Store            | ReportType       | N : M       | A store must file specific report types on schedule         |

### Join Keys

| Relationship          | Join Column(s)                                      |
|-----------------------|------------------------------------------------------|
| `manages`             | `dim_store_managers.store_id` → `dim_stores.store_id`|
| `belongs_to_district` | `dim_stores.district_id` → `dim_districts.district_id`|
| `stocks`              | Bridged via `fact_inventory_audits.category_id`       |
| `partners_with`       | Bridged via vendor delivery/receiving records         |
| `requires_report`     | Bridged via `fact_compliance_doc_events.report_type_id`|

---

## Contextualizations

Contextualizations bind event and stream tables to entity types so the ontology engine
can navigate from an entity to its time-series data and vice-versa.

### Event Contextualizations (Eventhouse — KQL DB)

| ID       | Fact / Stream Table              | Entity Bindings                          | Description                                                     |
|----------|----------------------------------|------------------------------------------|-----------------------------------------------------------------|
| CTX-001  | `fact_compliance_doc_events`     | StoreManager, Store, ReportType          | Compliance report filing events — duration, status, overdue flag |
| CTX-002  | `fact_retail_system_clicks`      | StoreManager                             | Clickstream in retail admin systems (POS, WFM, inventory)        |
| CTX-003  | `fact_inventory_audits`          | Store, StoreManager, ProductCategory     | Inventory count/audit events with variance and doc time          |
| CTX-004  | `fact_inventory_scans`           | Store                                    | Individual product scan events during inventory counts           |
| CTX-005  | `fact_scheduling_events`         | StoreManager, Store                      | Scheduling tasks — shift planning, coverage gap resolution       |
| CTX-006  | `fact_shift_handoffs`            | Store, StoreManager (from), StoreManager (to) | End-of-shift handoff documentation between managers         |
| CTX-007  | `fact_store_incidents`           | Store, StoreManager                      | Safety / security incident reports and documentation time        |
| CTX-008  | `fact_associate_presence`        | Store                                    | Zone-level associate presence and dwell tracking                 |
| CTX-009  | `fact_pos_transactions`          | Store                                    | Point-of-sale transaction events                                 |

### Batch Contextualizations (Lakehouse)

| ID       | Fact Table                       | Entity Bindings                          | Description                                                     |
|----------|----------------------------------|------------------------------------------|-----------------------------------------------------------------|
| CTX-010  | `fact_manager_wellness`          | StoreManager, Store                      | Monthly manager wellness — admin burden score, overtime, floor % |
| CTX-011  | `fact_audit_quality`             | Store, ProductCategory                   | Audit quality scores — planogram compliance, inventory accuracy  |
| CTX-012  | `fact_customer_satisfaction`     | Store                                    | Customer satisfaction surveys — NPS, mystery shopper, wait time  |

### Stream Contextualizations (Eventhouse — Real-Time)

| ID       | Stream Table                     | Entity Bindings                          | Description                                                     |
|----------|----------------------------------|------------------------------------------|-----------------------------------------------------------------|
| CTX-013  | `stream_pos_transactions`        | Store                                    | Real-time POS transaction feed                                   |
| CTX-014  | `stream_foot_traffic`            | Store                                    | Real-time foot traffic sensor data by zone                       |
| CTX-015  | `stream_inventory_scans`         | Store                                    | Real-time inventory scan events with discrepancy detection       |
| CTX-016  | `stream_store_incidents`         | Store                                    | Real-time incident reporting stream                              |
| CTX-017  | `stream_associate_location`      | Store                                    | Real-time associate location pings by zone                       |

---

## Data Storage Mapping

| Storage Layer  | Asset               | Tables / Streams                                                                                         |
|----------------|----------------------|----------------------------------------------------------------------------------------------------------|
| **Lakehouse**  | RetailLakehouse      | `dim_store_managers`, `dim_stores`, `dim_districts`, `dim_report_types`, `dim_product_categories`, `dim_vendor_partners`, `fact_manager_wellness`, `fact_audit_quality`, `fact_customer_satisfaction` |
| **Eventhouse** | RetailEventhouse     | `fact_compliance_doc_events`, `fact_retail_system_clicks`, `fact_inventory_audits`, `fact_inventory_scans`, `fact_scheduling_events`, `fact_shift_handoffs`, `fact_store_incidents`, `fact_associate_presence`, `fact_pos_transactions` |
| **KQL DB**     | RetailKQLDB          | `stream_pos_transactions`, `stream_foot_traffic`, `stream_inventory_scans`, `stream_store_incidents`, `stream_associate_location` |

---

## Ontology Visualization

```
                          ┌──────────────┐
                          │   District   │
                          │  ENT-003     │
                          └──────┬───────┘
                                 │
                        belongs_to_district
                           (REL-002)
                                 │
┌──────────────┐        ┌───────┴────────┐        ┌──────────────────┐
│ StoreManager │───────▶│     Store      │───────▶│  ProductCategory │
│  ENT-001     │manages │   ENT-002      │ stocks │    ENT-005       │
└──────────────┘(REL-001)└───────┬────────┘(REL-003)└──────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    │                         │
              partners_with            requires_report
                (REL-004)                (REL-005)
                    │                         │
           ┌────────┴───────┐        ┌────────┴───────┐
           │ VendorPartner  │        │   ReportType   │
           │   ENT-006      │        │   ENT-004      │
           └────────────────┘        └────────────────┘

  ─── Contextualizations (event / stream bindings) ───

  StoreManager ◄── CTX-001 (compliance_doc_events)
  StoreManager ◄── CTX-002 (retail_system_clicks)
  StoreManager ◄── CTX-005 (scheduling_events)
  StoreManager ◄── CTX-006 (shift_handoffs)
  StoreManager ◄── CTX-007 (store_incidents)
  StoreManager ◄── CTX-010 (manager_wellness)

  Store ◄── CTX-001 .. CTX-017   (all event & stream tables)
  ProductCategory ◄── CTX-003 (inventory_audits), CTX-011 (audit_quality)
  ReportType ◄── CTX-001 (compliance_doc_events)
```

---

## Key Analytical Queries

### 1. Compliance Documentation Time vs. Floor Time

> _How much time does each manager spend on compliance documentation versus
> customer-facing floor time, and which report types consume the most hours?_

- **Entities:** StoreManager, ReportType
- **Contextualizations:** CTX-001 (`fact_compliance_doc_events`), CTX-010 (`fact_manager_wellness`)
- **Pattern:** Aggregate `duration_minutes` from compliance events per manager per week,
  compare against `floor_time_pct` from wellness surveys. Rank report types by total
  administrative burden.

### 2. Inventory Audit Accuracy by Category

> _Which product categories have the worst inventory accuracy, and do stores that
> spend more documentation time on audits achieve better variance results?_

- **Entities:** Store, ProductCategory
- **Contextualizations:** CTX-003 (`fact_inventory_audits`), CTX-011 (`fact_audit_quality`)
- **Pattern:** Correlate `doc_time_min` and `scan_count` with `variance_pct` per
  category. Overlay `planogram_compliance_pct` and `inventory_accuracy_pct` from
  quality audits to find categories where extra effort yields measurable improvement.

### 3. Shift Handoff Documentation Burden

> _How does shift handoff documentation overhead vary by store format, and do
> stores with longer handoff notes have fewer open-task carryover?_

- **Entities:** StoreManager, Store
- **Contextualizations:** CTX-006 (`fact_shift_handoffs`), CTX-005 (`fact_scheduling_events`)
- **Pattern:** Measure `notes_length` and `open_tasks_count` per handoff. Group by
  `store.format` to compare Express vs. Superstore handoff burden. Correlate with
  scheduling `coverage_gaps_filled` to assess whether thorough handoffs reduce
  downstream scheduling rework.

### 4. Incident Documentation vs. Response Time

> _Do stores with faster incident documentation also have better resolution
> outcomes, and how does documentation time impact manager floor availability?_

- **Entities:** Store, StoreManager
- **Contextualizations:** CTX-007 (`fact_store_incidents`), CTX-016 (`stream_store_incidents`), CTX-010 (`fact_manager_wellness`)
- **Pattern:** Compare `documentation_time_min` against `resolution` quality ratings.
  Use real-time `response_time_sec` from stream to assess whether documentation
  burden delays incident response. Cross-reference with `floor_time_pct` erosion.

### 5. Store Performance vs. Administrative Overhead

> _Is there a correlation between total administrative overhead (compliance +
> scheduling + audits) and customer satisfaction or revenue performance?_

- **Entities:** Store, District
- **Contextualizations:** CTX-001, CTX-003, CTX-005, CTX-012 (`fact_customer_satisfaction`)
- **Pattern:** Aggregate total admin hours per store (compliance doc + inventory audit
  + scheduling event durations). Correlate with `nps_score`, `mystery_shopper_score`,
  and `revenue_tier`. Identify the tipping point where admin burden degrades customer
  experience — the "documentation debt" threshold.

---

## Appendix — Column Quick Reference

| Table                          | Columns                                                                                                  |
|--------------------------------|----------------------------------------------------------------------------------------------------------|
| `dim_store_managers`           | manager_id, name, store_id, region, hire_date, certifications, avg_weekly_floor_hours                    |
| `dim_stores`                   | store_id, name, district_id, region, format, sq_footage, headcount, revenue_tier                         |
| `dim_districts`                | district_id, name, region, store_count, district_manager, performance_rating                             |
| `dim_report_types`             | report_type_id, name, category, frequency, avg_completion_time_min, regulatory_required                  |
| `dim_product_categories`       | category_id, name, department, planogram_reset_frequency, shrinkage_risk_tier                            |
| `dim_vendor_partners`          | vendor_id, name, category, delivery_frequency, documentation_requirements                                |
| `fact_compliance_doc_events`   | event_id, manager_id, store_id, report_type_id, start_time, duration_minutes, status, overdue_flag       |
| `fact_retail_system_clicks`    | click_id, manager_id, timestamp, system, module, action, duration_ms, error_code                         |
| `fact_inventory_audits`        | audit_id, store_id, manager_id, category_id, date, unit_count, variance_pct, doc_time_min, scan_count    |
| `fact_inventory_scans`         | scan_id, store_id, associate_id, timestamp, product_id, location, expected_qty, actual_qty, variance     |
| `fact_scheduling_events`       | event_id, manager_id, store_id, date, task_type, duration_minutes, coverage_gaps_filled, overtime_approved|
| `fact_shift_handoffs`          | handoff_id, store_id, from_manager_id, to_manager_id, timestamp, open_tasks_count, notes_length          |
| `fact_store_incidents`         | incident_id, store_id, manager_id, timestamp, type, severity, documentation_time_min, resolution         |
| `fact_associate_presence`      | presence_id, associate_id, store_id, timestamp, zone, dwell_time_min, is_customer_facing                 |
| `fact_pos_transactions`        | txn_id, store_id, register_id, timestamp, type, total, items, associate_id, return_flag                  |
| `fact_manager_wellness`        | survey_id, manager_id, store_id, date, admin_burden_score, work_life_balance, overtime_hours, floor_time_pct |
| `fact_audit_quality`           | quality_id, store_id, audit_type, category_id, date, planogram_compliance_pct, inventory_accuracy_pct, safety_checklist_complete |
| `fact_customer_satisfaction`   | survey_id, store_id, date, nps_score, mystery_shopper_score, wait_time_rating, staff_helpfulness         |
| `stream_pos_transactions`      | txn_id, store_id, timestamp, type, total, items, return_flag, void_flag                                  |
| `stream_foot_traffic`          | sensor_id, store_id, timestamp, zone, enter_count, exit_count, dwell_seconds                             |
| `stream_inventory_scans`       | scan_id, store_id, associate_id, timestamp, product_id, qty, expected_qty, discrepancy                   |
| `stream_store_incidents`       | incident_id, store_id, timestamp, type, severity, response_time_sec, is_resolved                         |
| `stream_associate_location`    | ping_id, associate_id, store_id, timestamp, zone, is_moving, is_customer_facing                          |
