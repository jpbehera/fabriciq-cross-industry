# Telecom Network Operations — Sample Dataset

## Overview

This dataset supports the **Telecom Network Operations Documentation Burden** demo for
Microsoft Fabric Real-Time Intelligence, Fabric IQ, Foundry IQ, and Work IQ.

**Problem:** Network engineers and field technicians spend **35–55%** of their time on
documentation — trouble tickets, dispatch reports, root-cause analysis (RCA) documents,
regulatory filings, and SLA compliance reporting — instead of resolving network issues.

**23 CSV files · ~2,705 rows · 4 table categories**

---

## Dataset Structure

### Dimensions (6 tables · 150 rows)

| Table | Rows | Key | Description |
|-------|-----:|-----|-------------|
| `dim_engineers` | 30 | `engineer_id` | NOC analysts, network engineers, field technicians, security analysts, planning engineers |
| `dim_service_areas` | 15 | `area_id` | Geographic service regions with customer counts and network density |
| `dim_network_segments` | 12 | `segment_id` | Network segments (metro fiber, backbone, access, enterprise, data center, transport) |
| `dim_ticket_types` | 18 | `type_id` | Ticket categories with SLA targets and priority rules |
| `dim_enterprise_customers` | 25 | `customer_id` | Enterprise/business customers with SLA tiers (Platinum/Gold/Silver/Bronze) |
| `dim_equipment` | 50 | `equipment_id` | Routers, switches, optical gear, firewalls, servers, microwave radios |

### Batch Facts (6 tables · 865 rows) → Lakehouse + Warehouse

| Table | Rows | Key | Description |
|-------|-----:|-----|-------------|
| `fact_trouble_tickets` | 300 | `ticket_id` | 4 weeks of tickets (Feb 23 – Mar 22, 2026), multi-priority, documentation times |
| `fact_field_dispatches` | 150 | `dispatch_id` | Field technician dispatches with travel, work, and documentation durations |
| `fact_technician_wellness` | 30 | `engineer_id` | Burnout indicators, documentation fatigue scores, overtime hours |
| `fact_ticket_quality` | 300 | `ticket_id` | Documentation quality scores per ticket (completeness, accuracy, clarity) |
| `fact_customer_satisfaction` | 25 | `customer_id` | NPS, CSAT, resolution satisfaction, documentation clarity ratings |
| `fact_network_performance` | 60 | `record_id` | Monthly KPIs per segment (5 months × 12 segments) — MTTR, availability, SLA compliance |

### Event Facts (6 tables · 1,260 rows) → Eventhouse + Warehouse

| Table | Rows | Key | Description |
|-------|-----:|-----|-------------|
| `fact_nms_interactions` | 500 | `interaction_id` | Engineer interactions with 8 NMS systems (Mar 1–12, 2026) |
| `fact_outage_events` | 40 | `outage_id` | Network outages by severity, root cause, affected customers, and restoration time |
| `fact_rca_documents` | 40 | `rca_id` | Root-cause analysis documents with authoring time, page count, and review status |
| `fact_ticket_escalations` | 80 | `escalation_id` | Escalation chains (Tier 1 → 2 → 3 → Management) with handling durations |
| `fact_sla_alerts` | 100 | `alert_id` | SLA breach/warning events across 5 metric types, CUST-010 and CUST-003 most affected |
| `fact_field_location` | 500 | `ping_id` | GPS pings for 8 field technicians across 6 days with activity type and site visits |

### Streaming (5 tables · 430 rows) → Eventhouse

| Table | Rows | Key | Description |
|-------|-----:|-----|-------------|
| `stream_network_alarms` | 100 | `alarm_id` | Alarm storm pattern — 30+ alarm types, rapid-fire timestamps, progressive clearing |
| `stream_ticket_activity` | 100 | `activity_id` | Real-time ticket lifecycle: create → assign → escalate → resolve → close |
| `stream_field_dispatch` | 70 | `dispatch_id` | Live dispatch tracking: Dispatched → En Route → Arrived → Working → Complete |
| `stream_performance_metrics` | 100 | `metric_id` | Equipment telemetry with threshold exceedances (CPU, optical, BER, temperature) |
| `stream_customer_impact` | 60 | `impact_id` | Customer service impact events with restoration timeline |

---

## Key Relationships

```
dim_engineers.engineer_id  ←→  fact_trouble_tickets.engineer_id
                           ←→  fact_field_dispatches.technician_id
                           ←→  fact_technician_wellness.engineer_id
                           ←→  fact_nms_interactions.engineer_id
                           ←→  fact_field_location.technician_id

dim_equipment.equipment_id ←→  fact_outage_events.equipment_id
                           ←→  stream_network_alarms.equipment_id
                           ←→  stream_performance_metrics.equipment_id

dim_enterprise_customers.customer_id ←→  fact_customer_satisfaction.customer_id
                                     ←→  fact_sla_alerts.customer_id
                                     ←→  stream_customer_impact.customer_id

dim_network_segments.segment_id ←→  fact_network_performance.segment_id

dim_ticket_types.type_id        ←→  fact_trouble_tickets.type_id

fact_trouble_tickets.ticket_id  ←→  fact_ticket_quality.ticket_id
                                ←→  fact_ticket_escalations.ticket_id
                                ←→  stream_ticket_activity.ticket_id
                                ←→  stream_field_dispatch.ticket_id
```

---

## Embedded Data Quality Stories

- **SEG-004 / SEG-009**: Consistently underperforming network segments (lower availability, higher MTTR)
- **CUST-010 / CUST-003**: Most SLA breaches, lowest satisfaction scores
- **EQ-007 / EQ-002**: CPU utilization exceeding thresholds in streaming metrics
- **EQ-040**: Degraded fiber (optical power and BER exceeded)
- **Documentation burden**: RCA docs take 30–240 minutes; ticket documentation averages 15–45 min
- **Field location**: Documentation dwell times of 10–32 min per site visit

---

## Usage with Generic Notebooks

### Quick Start

1. Upload the `data/` folder to your Fabric Lakehouse at:
   ```
   Files/telecom_network_operations/data/
   ```

2. In the `cross_industry_notebooks/` folder, run:
   ```
   %run ./Telecom_Config
   ```
   This loads all table names, paths, and artifact names.

3. Execute notebooks in order: `01_Data_Ingestion` → `02_Load_Lakehouse` → `03_Load_Warehouse` → `04_Create_Ontology` → `05_Create_Data_Agent` → `06_Create_Semantic_Model` → `07_Create_Dashboards`

### Data Destination Mapping

| Table Category | Lakehouse (Delta) | Warehouse (SQL) | Eventhouse (KQL) |
|---------------|:-:|:-:|:-:|
| `dim_*` dimensions | ✓ | ✓ | — |
| `fact_*` batch facts | ✓ | ✓ | — |
| `fact_*` event facts | — | ✓ | ✓ |
| `stream_*` streaming | — | — | ✓ |

### KQL Table Names

Event facts and streams use shortened names in Eventhouse:

| CSV Table Name | KQL Table Name |
|---------------|---------------|
| `fact_nms_interactions` | `nms_interactions` |
| `fact_outage_events` | `outage_events` |
| `fact_rca_documents` | `rca_documents` |
| `fact_ticket_escalations` | `ticket_escalations` |
| `fact_sla_alerts` | `sla_alerts` |
| `fact_field_location` | `field_location` |
| `stream_network_alarms` | `network_alarms` |
| `stream_ticket_activity` | `ticket_activity` |
| `stream_field_dispatch` | `field_dispatch` |
| `stream_performance_metrics` | `performance_metrics` |
| `stream_customer_impact` | `customer_impact` |

---

## Time Ranges

| Table | Date Range |
|-------|-----------|
| Trouble tickets / dispatches | Feb 23 – Mar 22, 2026 |
| NMS interactions | Mar 1–12, 2026 |
| Outage / RCA events | Mar 1–22, 2026 |
| Network performance | Nov 2025 – Mar 2026 (5 months) |
| Field location | Mar 1–6, 2026 |
| Streaming tables | Mar 10, 2026 (real-time window) |
