# Media Content Operations — Sample Dataset

## Overview

Sample dataset for the **Media & Entertainment — Content Production Documentation Burden** use case.
This dataset demonstrates how producers, editors, rights managers, and compliance officers in a
fictional media company ("Global Media Group") spend 30–50% of their time on documentation tasks:
metadata tagging, rights clearance, approval workflows, regulatory compliance, and delivery paperwork.

**Total:** 23 CSV files | ~2,418 rows | Compatible with the generic cross-industry notebooks (00–07)

---

## Use Case Narrative

Global Media Group produces 15 shows across scripted drama, comedy, reality, documentary,
news, sports, animation, short-form digital, and podcast formats — distributed across 6 networks
and 12 platforms (SVOD, linear, AVOD, FAST, podcast, cinema).

**Key data quality stories embedded in this dataset:**
- **SHW-005 "Future Forward"** (sci-fi): Highest production quality & audience engagement, but
  worst delivery timeliness due to VFX complexity, most rights pending, longest approval cycles
- **SHW-003 "Wilderness Challenge"** (reality): Declining on-time delivery rate, delivery
  alerts escalating to overdue status
- **SHW-012 "Viral Moments"** (short-form): Fastest turnaround but lowest metadata quality
  scores, upscaled resolution warnings in QC
- **SHW-010 "Legal Eagles"** (drama): Compliance issues requiring regulatory review
- **PRD-010 & PRD-015**: Critical burnout risk (highest admin burden)
- **Rights managers**: Highest administrative burden across all producer roles

---

## Table Inventory

### Dimensions (6 tables → Lakehouse + Warehouse)

| Table | Rows | Description |
|-------|------|-------------|
| `dim_producers` | 25 | Production staff: producers, editors, rights managers, QC, compliance |
| `dim_shows` | 15 | Shows across all genres and networks |
| `dim_networks` | 6 | Broadcast and streaming networks |
| `dim_content_task_types` | 20 | Documentation task categories |
| `dim_rights_holders` | 30 | Music, footage, talent, brand, format, sports rights holders |
| `dim_platforms` | 12 | Distribution platforms (SVOD, linear, AVOD, FAST, etc.) |

### Batch Facts (6 tables → Lakehouse + Warehouse)

| Table | Rows | Description |
|-------|------|-------------|
| `fact_content_doc_events` | 250 | Individual documentation tasks with time spent |
| `fact_rights_clearance` | 100 | Rights clearance requests and statuses |
| `fact_crew_wellness` | 25 | Producer burnout risk scores |
| `fact_content_quality` | 200 | Content quality scores per show per asset |
| `fact_client_satisfaction` | 15 | Client/network satisfaction per show |
| `fact_production_performance` | 45 | Monthly production vs documentation hours |

### Event Facts (6 tables → Eventhouse + Warehouse)

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `fact_mam_interactions` | 400 | `mam_interactions` | Media Asset Management system clicks/actions |
| `fact_metadata_entries` | 500 | `metadata_entries` | Individual metadata field entries with auto/manual split |
| `fact_approval_workflows` | 80 | `approval_workflows` | Creative, network, legal, and client approvals |
| `fact_content_handoffs` | 40 | `content_handoffs` | Role-to-role content handoffs with documentation time |
| `fact_delivery_alerts` | 60 | `delivery_alerts` | Deadline warnings, QC failures, rights issues |
| `fact_regulatory_reviews` | 50 | `regulatory_reviews` | FCC, GDPR, CCPA, accessibility compliance checks |

### Streaming (5 tables → Eventhouse only)

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `stream_mam_activity` | 100 | `mam_activity` | Real-time MAM system activity feed |
| `stream_rights_status` | 80 | `rights_status` | Live rights clearance status updates |
| `stream_delivery_tracking` | 80 | `delivery_tracking` | File transfer progress tracking |
| `stream_qc_results` | 80 | `qc_results` | Automated QC check results |
| `stream_audience_metrics` | 80 | `audience_metrics` | Real-time viewership and engagement |

---

## ID Reference

| Entity | Pattern | Example | Source Table |
|--------|---------|---------|-------------|
| Producer | PRD-NNN | PRD-001 | dim_producers |
| Show | SHW-NNN | SHW-001 | dim_shows |
| Network | NET-NNN | NET-001 | dim_networks |
| Task Type | CTT-NNN | CTT-001 | dim_content_task_types |
| Rights Holder | RH-NNN | RH-001 | dim_rights_holders |
| Platform | PLT-NNN | PLT-001 | dim_platforms |
| Asset | AST-SSSXXX | AST-001003 | Referenced in facts (SSS=show suffix) |

---

## Quick Start

1. Upload the `data/` folder to your Fabric Lakehouse Files area
2. Use `Media_Config.ipynb` (or `00_Industry_Config.ipynb`) as the config notebook
3. Run notebooks 01–07 in sequence

```
%run ./Media_Config
```

---

## Compatible Notebooks

| Notebook | Purpose |
|----------|---------|
| `Media_Config.ipynb` | Pre-filled configuration (skip auto-discovery) |
| `00_Industry_Config.ipynb` | Auto-discover tables from CSVs |
| `01_Data_Ingestion.ipynb` | Schema discovery and data profiling |
| `02_Load_Lakehouse.ipynb` | Load dims + batch facts to Lakehouse Delta |
| `03_Load_Warehouse.ipynb` | Load all tables to Warehouse SQL |
| `04_Create_Ontology.ipynb` | Create Fabric IQ ontology |
| `05_Create_Data_Agent.ipynb` | Create QA + Ops data agents |
| `06_Create_Semantic_Model.ipynb` | Power BI semantic model |
| `07_Create_Dashboards.ipynb` | KQL dashboard + Power BI report |
