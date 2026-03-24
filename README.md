# FabricIQ Cross-Industry Accelerator

An end-to-end accelerator for deploying **Microsoft Fabric Real-Time Intelligence** solutions across 10 industries. It automates the full pipeline — from data ingestion through Lakehouse, Warehouse, Semantic Model, Ontology, Data Agents, and Dashboards — using a single set of parameterized notebooks.

Every industry addresses a real operational challenge where frontline workers spend **30–70% of their time on documentation**. The accelerator surfaces burden metrics through automated pipelines, ontologies, AI agents, and both batch (Power BI) and real-time (KQL) dashboards.

---

## Repository Structure

```
fabriciq-cross-industry/
├── cross_industry_notebooks/   # Core pipeline notebooks + industry configs
├── datasets/                   # Sample data, ontology designs, and guides for 10 industries
├── industries/                 # Industry problem statements and architecture specs
├── fabriciq-nurse-doc-burden-usecase/  # Deep-dive healthcare demo with simulator
└── .gitignore
```

---

## `cross_industry_notebooks/`

**19 files** — A universal notebook pipeline that deploys a complete Fabric IQ solution for any supported industry. Change one `INDUSTRY` variable and the entire pipeline adapts.

### Core Pipeline (8 Notebooks)

| # | Notebook | Purpose |
|---|----------|---------|
| 00 | `00_Industry_Config.ipynb` | Sets industry name, artifact names, CSV paths, and Eventhouse cluster URI |
| 01 | `01_Data_Ingestion.ipynb` | Auto-discovers CSV schemas, profiles columns, detects quality issues |
| 02 | `02_Load_Lakehouse.ipynb` | Loads `dim_*` → Lakehouse Delta; `fact_*` (batch) → Lakehouse; `fact_*` (events) & `stream_*` → Eventhouse KQL |
| 03 | `03_Load_Warehouse.ipynb` | Auto-generates DDL, loads all tables to Warehouse with Spark→SQL type mapping |
| 04 | `04_Create_Semantic_Model.ipynb` | Builds TMSL definition, auto-detects star-schema relationships, generates DAX measures |
| 05 | `05_Create_Ontology.ipynb` | Creates Fabric IQ ontology from `.iq` package or RDF/OWL; auto-resolves data source IDs |
| 06 | `06_Create_Data_Agent.ipynb` | Creates QA Agent (ad-hoc questions) + Ops Agent (event monitoring) |
| 07 | `07_Create_Dashboards.ipynb` | Creates real-time KQL dashboard + Power BI report |

### Pre-Filled Industry Configs (10 Notebooks)

Each config notebook is pre-populated with table names, row counts, and CSV paths for its industry:

| Config Notebook | Industry | Tables |
|----------------|----------|--------|
| `Advertising_Config.ipynb` | Out-of-Home Advertising | 23 |
| `Construction_Config.ipynb` | Construction Site Operations | 23 |
| `Finance_Config.ipynb` | Banking / Wealth Management | 23 |
| `Healthcare_Config.ipynb` | Nursing Documentation | 25 |
| `Insurance_Config.ipynb` | Insurance Claims Processing | 23 |
| `LawFirms_Config.ipynb` | Legal Documentation | 23 |
| `Media_Config.ipynb` | Media & Content Production | 23 |
| `OilAndGas_Config.ipynb` | Oil & Gas Field Operations | 23 |
| `Retail_Config.ipynb` | Retail Store Operations | 23 |
| `Telecom_Config.ipynb` | Telecom Network Operations | 23 |

Also includes a `README.md` with prerequisites and step-by-step walkthrough.

---

## `datasets/`

**10 industry directories**, each containing sample CSV data, an ontology design document, and an ontology package guide.

### Industries

| Directory | Industry |
|-----------|----------|
| `advertising_campaign_operations/` | Out-of-Home Advertising |
| `construction_site_operations/` | Construction |
| `finance_banking_operations/` | Banking / Wealth Management |
| `healthcare_nursing_documentation/` | Healthcare Nursing |
| `insurance_claims_operations/` | Insurance Claims |
| `law_firm_operations/` | Law Firms |
| `media_content_operations/` | Media & Entertainment |
| `oil_gas_field_operations/` | Oil & Natural Gas |
| `retail_store_operations/` | Retail |
| `telecom_network_operations/` | Telecommunications |

### Contents per Industry

Each directory follows this structure:

```
<industry>/
├── README.md                  # Overview, problem statement, table inventory, use cases, personas
├── ontology_design.md         # Entity types, properties, relationships, contextualizations, KQL/SQL queries
├── ontology_package_guide.md  # Step-by-step guide to create .iq ontology package with Python code
└── data/
    ├── dim_*.csv              # Dimension tables (6 per industry)
    ├── fact_*.csv             # Fact tables — batch + event (varies per industry)
    └── stream_*.csv           # Streaming-only tables (5 per industry)
```

### CSV Naming Convention

| Prefix | Type | Destination |
|--------|------|-------------|
| `dim_*` | Dimension | Lakehouse + Warehouse |
| `fact_*` (batch) | Batch fact | Lakehouse + Warehouse |
| `fact_*` (event) | Event fact | Eventhouse + Warehouse |
| `stream_*` | Streaming-only | Eventhouse |

Each industry has **23–25 CSV files** with sample data ready for ingestion.

---

## `industries/`

**10 markdown files** — Industry-specific problem statements with statistics, ontology mappings, and Fabric architecture diagrams.

| File | Industry | Documentation Burden |
|------|----------|---------------------|
| `advertising.md` | Out-of-Home Advertising | 35–55% of AE time on documentation |
| `construction.md` | Construction | 30–50% on daily logs, RFIs, change orders |
| `cpg.md` | Consumer Packaged Goods | 35–55% on store visit docs, compliance |
| `finance.md` | Banking / Wealth | 40–60% on KYC/AML paperwork |
| `insurance.md` | Insurance Claims | 50–70% on forms; 8–15 docs per claim |
| `law_firms.md` | Legal | 40–60%; $150K–$500K lost revenue per attorney/year |
| `media.md` | Media & Entertainment | 30–50% on metadata, rights clearance |
| `oil_and_gas.md` | Oil & Natural Gas | 40–60% on DDRs, permit-to-work paperwork |
| `retail.md` | Retail | 30–50% admin burden; 12–18 reports/week |
| `telecom.md` | Telecommunications | 35–55% on tickets, RCAs, compliance |

Each document includes:
- **The Problem** — Time spent, cost impact, document volume statistics
- **Ontology Mapping** — Core concepts (Worker, Client, Unit, Task Type, Event, System, Handoff, Burnout, Quality, Satisfaction, etc.)
- **Fabric Architecture** — Diagram showing Lakehouse → Warehouse, Eventhouse (real-time), Semantic Model, Ontology, and Agents

---

## `fabriciq-nurse-doc-burden-usecase/`

**18 files** — A production-ready, deep-dive healthcare demo focused on nursing documentation burden. Includes notebooks, dashboards, a streaming simulator, and deployment utilities.

### Notebooks

| Notebook | Purpose |
|----------|---------|
| `Healthcare_Create_Ontology_from_Package.ipynb` | Creates ontology from `.iq` package, binds to Lakehouse/Eventhouse |
| `Healthcare_Create_Ontology_from_RDF.ipynb` | Alternative: creates ontology from RDF/OWL |
| `Healthcare_Generate_Ontology_Data.ipynb` | Generates sample event data, injects into Eventhouse |
| `Load_Warehouse_Tables.ipynb` | Loads healthcare data to Warehouse |
| `Configure_Eventstream_Routing.ipynb` | Configures Eventstream routing for real-time data |

### Dashboard & Queries

| File | Description |
|------|-------------|
| `Healthcare_Nursing_Dashboard.json` | Power BI dashboard definition |
| `Healthcare_RT_Dashboard_Queries.kql` | KQL queries for real-time dashboard (6 sections, 21 tiles) |
| `Healthcare_RT_Dashboard_Guide.md` | Step-by-step guide to build the real-time KQL dashboard |

### Setup & Documentation

| File | Description |
|------|-------------|
| `SETUP_GUIDE.md` | Complete deployment guide with prerequisites and step-by-step instructions |

### Python Utilities

| Script | Purpose |
|--------|---------|
| `generate_dashboard.py` | Creates/updates Power BI real-time dashboard via Fabric REST API |
| `create_dashboard_api.py` | API helpers for dashboard creation |
| `fix_dashboard.py` | Repairs/updates existing dashboard |
| `check_dashboard.py` | Verifies dashboard exists and is valid |
| `compare_dashboards.py` | Compares two dashboard definitions |
| `recreate_dashboard.py` | Deletes and recreates dashboard |
| `inspect_working.py` | Debugging/inspection utilities |
| `search_entity.py` | Searches for entities in ontology |

### Simulator

The `simulator/` folder contains a local Python script that generates streaming healthcare events and posts them to Event Hub:

- `stream_simulator.py` — Generates realistic nursing workflow events
- `.env.example` — Template for Event Hub connection strings
- `requirements.txt` — Python dependencies

---

## Getting Started

### Prerequisites

- **Microsoft Fabric workspace** with a Fabric capacity (F2+) or trial
- **Lakehouse**, **Warehouse**, and **Eventhouse** created in the workspace
- Python 3.10+ (for utilities and simulator)

### Quick Start (Any Industry)

1. Open the **config notebook** for your industry (e.g., `cross_industry_notebooks/Retail_Config.ipynb`)
2. Update workspace-specific values (Lakehouse name, Warehouse name, Eventhouse URI)
3. Run notebooks **01 through 07** in order
4. Explore your data through the created Semantic Model, Ontology, Data Agents, and Dashboards

### Healthcare Deep-Dive

Follow the [SETUP_GUIDE.md](fabriciq-nurse-doc-burden-usecase/SETUP_GUIDE.md) in the `fabriciq-nurse-doc-burden-usecase/` folder for a complete walkthrough including real-time streaming with the simulator.

---

## Architecture

```
CSV Data Files (datasets/)
        │
        ▼
┌─────────────────────┐
│  01 Data Ingestion   │  ← Auto-discover schemas, profile columns
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐  ┌───────────┐
│Lakehouse│  │ Eventhouse │  ← dim/fact → Lakehouse; events/streams → Eventhouse
└────┬───┘  └─────┬─────┘
     │            │
     ▼            │
┌──────────┐      │
│ Warehouse │ ◄───┘  ← All tables consolidated
└─────┬────┘
      │
      ▼
┌──────────────┐
│Semantic Model │  ← Star-schema, DAX measures, auto-detected relationships
└──────┬───────┘
       │
       ▼
┌──────────┐
│ Ontology  │  ← Entity types, relationships, contextualizations
└──────┬───┘
       │
  ┌────┴────┐
  ▼         ▼
┌──────┐  ┌───────────┐
│Agents│  │ Dashboards │  ← QA Agent + Ops Agent; KQL + Power BI
└──────┘  └───────────┘
```

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
