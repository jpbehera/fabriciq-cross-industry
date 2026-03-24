# Oil & Gas Field Operations — Sample Dataset

> **Reducing field documentation overhead so engineers and operators focus on safe production, not paperwork compliance**

## Overview

This dataset contains **2,327 rows** across **23 CSV files** representing a realistic oil & gas field operations environment. It is designed for the FabricIQ cross-industry accelerator and demonstrates documentation burden analysis for field engineers, drilling supervisors, and HSE officers.

## Table Inventory

### Dimension Tables (6) → Lakehouse + Warehouse

| File | Rows | Description |
|---|---|---|
| `dim_field_engineers.csv` | 25 | Engineers, supervisors, HSE officers with roles, certifications, rotation schedules |
| `dim_well_sites.csv` | 20 | Wells across Permian, Eagle Ford, Bakken, DJ Basin, Marcellus, Gulf of Mexico |
| `dim_facilities.csv` | 8 | Offshore platforms, processing plants, gas plants, compressor stations |
| `dim_report_types.csv` | 18 | DDR, PTW, HSE inspection, production report, well integrity, environmental |
| `dim_equipment.csv` | 40 | BOPs, mud pumps, separators, compressors, ESPs, SCADA RTUs |
| `dim_regulatory_bodies.csv` | 6 | BSEE, Texas RRC, EPA, OSHA, North Dakota DMR, Colorado COGCC |

### Batch Fact Tables (6) → Lakehouse + Warehouse

| File | Rows | Description |
|---|---|---|
| `fact_daily_drilling_reports.csv` | 200 | DDR records with depth, footage, mud weight, doc time, incidents |
| `fact_permit_to_work.csv` | 120 | PTW forms: work type, hazard level, signatory tracking, doc time |
| `fact_field_wellness.csv` | 25 | Rotation fatigue, admin burden, isolation scores, overtime hours |
| `fact_report_quality.csv` | 200 | Completeness, accuracy, timeliness, regulatory readiness per report |
| `fact_operator_satisfaction.csv` | 15 | Audit scores, JV partner ratings, regulatory compliance percentages |
| `fact_production_performance.csv` | 60 | Monthly production, decline rate, uptime, doc hours per well |

### Event Fact Tables (6) → Eventhouse + Warehouse

| File | Rows | Description |
|---|---|---|
| `fact_scada_interactions.csv` | 400 | Control room clicks: WellView, OSIsoft PI, alarm acknowledgements |
| `fact_hse_inspections.csv` | 100 | Inspections with findings, critical findings count, doc time |
| `fact_well_integrity_events.csv` | 60 | Pressure tests, casing inspections, cement bond logs, results |
| `fact_tour_handoffs.csv` | 50 | Crew rotation handoffs with open items, doc time, narrative length |
| `fact_production_alerts.csv` | 80 | Decline deviations, pressure anomalies, ESP trips, equipment failures |
| `fact_field_location.csv` | 500 | GPS pings: engineer location, zone, activity type, dwell time |

### Streaming Tables (5) → Eventhouse

| File | Rows | Description |
|---|---|---|
| `stream_scada_alarms.csv` | 80 | Real-time equipment alarms, process excursions, priorities |
| `stream_well_telemetry.csv` | 80 | Wellhead pressure, temperature, flow rate, gas rate readings |
| `stream_ptw_status.csv` | 80 | Permit status changes, pending approvals, hazard levels |
| `stream_hse_events.csv` | 80 | Near-misses, gas detections, fire alarms, spills |
| `stream_environmental_monitoring.csv` | 80 | Emissions (SO2, NOx, H2S, VOC), water quality, flare efficiency |

## Data Story Personas

| Engineer ID | Name | Role | Story |
|---|---|---|---|
| **ENG-003** | Mike Rawlings | Drilling Supervisor | Extreme DDR burden — 200–280 min/day on documentation, high fatigue scores (7.5–9.5), poor report quality. Spends rest periods on paperwork. |
| **ENG-012** | Priya Venkatesh | Production Engineer | Most efficient — 60–100 min DDR time, lowest admin burden (2.0–3.5), highest report quality (92–100% completeness). Digital-first approach. |
| **ENG-018** | Carlos Rivera | HSE Officer | Inspection documentation overload — 5–15 findings per inspection, 80–150 min doc time, high admin burden (7.5–9.5). Perpetual backlog. |

## Key Relationships (Foreign Keys)

```
dim_field_engineers.engineer_id  →  fact_daily_drilling_reports.engineer_id
dim_field_engineers.engineer_id  →  fact_permit_to_work.engineer_id
dim_field_engineers.engineer_id  →  fact_field_wellness.engineer_id
dim_field_engineers.engineer_id  →  fact_report_quality.engineer_id
dim_field_engineers.engineer_id  →  fact_scada_interactions.engineer_id
dim_field_engineers.engineer_id  →  fact_hse_inspections.engineer_id
dim_field_engineers.engineer_id  →  fact_well_integrity_events.engineer_id
dim_field_engineers.engineer_id  →  fact_tour_handoffs.from_engineer / to_engineer
dim_field_engineers.engineer_id  →  fact_field_location.engineer_id
dim_well_sites.well_id           →  fact_daily_drilling_reports.well_id
dim_well_sites.well_id           →  fact_production_performance.well_id
dim_well_sites.well_id           →  fact_well_integrity_events.well_id
dim_well_sites.well_id           →  fact_tour_handoffs.well_id
dim_well_sites.well_id           →  fact_production_alerts.well_id
dim_well_sites.well_id           →  stream_well_telemetry.well_id
dim_facilities.facility_id       →  fact_permit_to_work.facility_id
dim_facilities.facility_id       →  fact_hse_inspections.facility_id
dim_facilities.facility_id       →  fact_operator_satisfaction.facility_id
dim_facilities.facility_id       →  fact_field_location.facility_id
dim_facilities.facility_id       →  stream_scada_alarms.facility_id
dim_facilities.facility_id       →  stream_ptw_status.facility_id
dim_facilities.facility_id       →  stream_hse_events.facility_id
dim_facilities.facility_id       →  stream_environmental_monitoring.facility_id
dim_equipment.well_id            →  dim_well_sites.well_id
```

## Usage

1. Upload the `data/` folder to your Fabric Lakehouse Files area
2. Use `OilAndGas_Config.ipynb` (or `00_Industry_Config`) to configure table mappings
3. Run notebooks `01` through `07` to load dimensions, facts, events, and streams
4. Build Power BI reports and real-time dashboards from the loaded data

## Config Notebook

Use [`cross_industry_notebooks/OilAndGas_Config.ipynb`](../cross_industry_notebooks/OilAndGas_Config.ipynb) as a drop-in replacement for `00_Industry_Config`. All table names, KQL mappings, and row counts are pre-filled.
