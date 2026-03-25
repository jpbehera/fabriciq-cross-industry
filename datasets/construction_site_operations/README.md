# Construction Site Operations — Sample Dataset

> **Disclaimer:** All data in this directory is **entirely fictional and synthetic**. Names, email addresses, phone numbers, and company references do not represent real individuals or organizations. Phone numbers use the `555-0xxx` reserved range. Email addresses use `.example` domains per [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606). Any resemblance to real persons or entities is coincidental.



## Overview

This dataset models **Construction Site Documentation Burden** — the administrative overhead
that superintendents, project managers, and safety directors face managing daily logs,
safety inspections, RFIs, change orders, and subcontractor coordination across multiple
active construction projects.

**Industry Context:** Construction superintendents spend 30-50% of their time on
documentation and administrative tasks. With average superintendent salaries of $150K-$200K,
this represents $60-80K per person per year in administrative burden.

## Dataset Statistics

| Category | Tables | Total Rows |
|----------|--------|------------|
| Dimensions | 6 | 124 |
| Batch Facts | 6 | 603 |
| Event Facts | 6 | 1,105 |
| Streaming | 5 | 420 |
| **Total** | **23** | **2,252** |

## Table Inventory

### Dimensions (6 tables → Lakehouse + Warehouse)

| Table | Rows | Description |
|-------|------|-------------|
| `dim_supervisors` | 25 | Superintendents, PMs, safety directors across 12 projects |
| `dim_projects` | 12 | Active projects ($28M renovation to $320M healthcare) |
| `dim_project_sites` | 12 | Physical site details with lat/lon, floors, active trades |
| `dim_inspection_types` | 20 | Safety, quality, environmental, and progress inspections |
| `dim_subcontractors` | 30 | Trade subcontractors (30 distinct trades) |
| `dim_trade_phases` | 25 | Construction phase definitions across projects |

### Batch Facts (6 tables → Lakehouse + Warehouse)

| Table | Rows | Description |
|-------|------|-------------|
| `fact_daily_logs` | 200 | Daily field reports with doc time, photos, safety incidents |
| `fact_safety_inspections` | 150 | Inspection records with findings, critical counts, corrective actions |
| `fact_supervisor_wellness` | 25 | Burnout/wellness metrics per supervisor |
| `fact_inspection_quality` | 150 | Completeness scores, photo coverage, defect identification rates |
| `fact_subcontractor_satisfaction` | 30 | Coordination, payment, and communication ratings |
| `fact_project_performance` | 48 | Monthly budget/schedule metrics (12 projects × 4 months) |

### Event Facts (6 tables → Eventhouse + Warehouse)

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `fact_pm_interactions` | 400 | `pm_interactions` | PM software interactions (Procore, PlanGrid, Bluebeam, Autodesk Build) |
| `fact_rfi_events` | 80 | `rfi_events` | Request for Information lifecycle events |
| `fact_change_orders` | 40 | `change_orders` | Change order documentation with cost/schedule impact |
| `fact_phase_handoffs` | 25 | `phase_handoffs` | Trade-to-trade handoff documentation |
| `fact_safety_alerts` | 60 | `safety_alerts` | Real-time safety alerts with severity and OSHA reporting |
| `fact_site_location` | 500 | `site_location` | Supervisor location pings with zone, floor, dwell time |

### Streaming (5 tables → Eventhouse)

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `stream_daily_log_activity` | 100 | `daily_log_activity` | Real-time daily log entries being created |
| `stream_safety_events` | 80 | `safety_events` | Live safety events (PPE violations, near misses, incidents) |
| `stream_rfi_status` | 80 | `rfi_status` | RFI status changes across all projects |
| `stream_weather_conditions` | 80 | `weather_conditions` | Hourly weather readings per site |
| `stream_equipment_telemetry` | 80 | `equipment_telemetry` | Equipment utilization, fuel, maintenance flags |

## Key Data Stories

### 1. Documentation Burden Hotspots
- **SUP-019** (Data Center PM): Highest admin burden score (9.5/10), 22 hrs overtime, work-life balance 2.0/10 — **critical burnout risk**
- **SUP-017** (Hospitality Asst Super): Lowest doc times but also lowest quality (76-79%) — **experience gap signal**
- **SUP-001** (Senior Superintendent): High doc times (85-112 min/day) but high quality — **experienced but overburdened**

### 2. Project Complexity Correlation
- **PRJ-002** (Riverfront Medical, $320M): Highest crew counts, most complex MEP documentation
- **PRJ-009** (Prairie Wind Data Center, $250M): Highest cost change orders ($425K cooling, $380K generator)
- **PRJ-011** (Heritage Lofts, $28M renovation): Low crew but detailed historic preservation requirements

### 3. Safety Performance
- ~85% of daily logs report zero safety incidents, ~12% report one, ~3% report two
- 3 OSHA-reportable incidents in safety alerts (struck-by, fall protection, equipment damage)
- Site location data shows supervisors spending 30-40% of dwell time in Office Trailer (documentation)

### 4. RFI & Change Order Patterns
- RFI response times range 4-72 hours; several Critical priority items open 10+ days
- Change order costs peak at infrastructure ($320K) and data center ($425K) projects
- Phase handoffs: 2 of 25 not approved (HVAC→Fire Protection, Steel→HVAC)

## Usage

### With Generic Notebooks
1. Upload `data/` folder to your Fabric Lakehouse Files area under `construction_site_operations/data/`
2. Import `Construction_Config.ipynb` to your Fabric workspace
3. Run notebooks 01-07 using `%run ./Construction_Config` for configuration

### File Naming Convention
- `dim_*` — Dimension tables (loaded to Lakehouse Delta + Warehouse SQL)
- `fact_*` — Fact tables (batch → Lakehouse + Warehouse; event → Eventhouse + Warehouse)
- `stream_*` — Streaming tables (loaded to Eventhouse KQL only)

## Foreign Key Relationships

```
dim_supervisors.supervisor_id → fact_daily_logs, fact_safety_inspections,
                                 fact_supervisor_wellness, fact_inspection_quality,
                                 fact_pm_interactions, fact_site_location,
                                 fact_safety_alerts, stream_daily_log_activity

dim_projects.project_id      → fact_daily_logs, fact_pm_interactions,
                                 fact_rfi_events, fact_change_orders,
                                 fact_project_performance, stream_daily_log_activity,
                                 stream_rfi_status

dim_project_sites.site_id    → fact_safety_inspections, fact_site_location,
                                 fact_safety_alerts, stream_safety_events,
                                 stream_weather_conditions, stream_equipment_telemetry

dim_inspection_types.type_id → fact_safety_inspections

dim_subcontractors.sub_id    → fact_subcontractor_satisfaction, stream_rfi_status

dim_trade_phases.phase_id    → fact_phase_handoffs
```

## Date Ranges
- **Batch facts:** November 2025 – March 2026
- **Event facts:** February 24 – March 14, 2026
- **Streaming:** March 9, 2026 (single day snapshot)
