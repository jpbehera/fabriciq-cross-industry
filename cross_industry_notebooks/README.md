# Cross-Industry Accelerator Notebooks

A pipeline of 8 Fabric notebooks that automate end-to-end deployment of a **Fabric IQ + Real-Time Intelligence** solution for **any industry**. Change one variable (`INDUSTRY`) and the entire pipeline adapts — data ingestion, lakehouse/warehouse loading, ontology creation, agent setup, semantic model, and dashboards.

## Supported Industries

| Key | Label | Description |
|-----|-------|-------------|
| `advertising` | Advertising | OOH campaign ops, charting, POP documentation |
| `construction` | Construction | Project tracking, safety, RFIs |
| `cpg` | CPG | Supply chain, demand planning |
| `finance` | Finance | Trading, risk, compliance |
| `healthcare` | Healthcare | Nursing documentation burden |
| `insurance` | Insurance | Claims processing, underwriting |
| `law_firms` | LawFirm | Case management, billing |
| `media` | Media | Content ops, ad delivery |
| `oil_and_gas` | OilGas | Production, pipeline monitoring |
| `retail` | Retail | Omnichannel, inventory, customer |
| `telecom` | Telecom | Network ops, customer churn |

## Pre-Filled Config Notebooks

For industries with ready-made sample datasets, **pre-filled config notebooks** are available as drop-in replacements for `00_Industry_Config`. These skip auto-discovery and hardcode all table names, KQL mappings, and expected row counts.

| Config Notebook | Industry | Tables | Rows | Dataset Folder |
|----------------|----------|--------|------|----------------|
| `Advertising_Config.ipynb` | Advertising (OOH) | 23 | 2,095 | `advertising_campaign_operations/` |
| `Construction_Config.ipynb` | Construction | 23 | — | `construction_site_operations/` |
| `Finance_Config.ipynb` | Finance (Banking) | 23 | 1,342 | `finance_banking_operations/` |
| `Healthcare_Config.ipynb` | Healthcare (Nursing) | 25 | — | `healthcare_nursing_documentation/` |
| `Insurance_Config.ipynb` | Insurance (Claims) | 23 | 1,637 | `insurance_claims_operations/` |
| `LawFirms_Config.ipynb` | Law Firms | 23 | 2,340 | `law_firm_operations/` |
| `Media_Config.ipynb` | Media (Content) | 23 | — | `media_content_operations/` |
| `OilAndGas_Config.ipynb` | Oil & Gas (Field) | 23 | 2,327 | `oil_gas_field_operations/` |
| `Retail_Config.ipynb` | Retail (Store) | 23 | 2,555 | `retail_store_operations/` |
| `Telecom_Config.ipynb` | Telecom (Network) | 23 | — | `telecom_network_operations/` |

**Usage:** Instead of running `00_Industry_Config`, run the pre-filled config (e.g., `%run ./Advertising_Config`) and proceed directly to notebook 01.

## Prerequisites

1. **Microsoft Fabric workspace** with capacity assigned (F2 or higher recommended)
2. **Fabric Lakehouse** created in the workspace
3. **Fabric Data Warehouse** created in the workspace
4. **Fabric Eventhouse** created (for real-time / event streaming tables)
5. **CSV data files** uploaded to the Lakehouse `Files/` area under a folder named `<industry>_data/`
   - e.g., `Files/healthcare_data/dim_nurses.csv`, `Files/healthcare_data/fact_documentation_events.csv`
6. **Ontology package** (`.iq` file) uploaded to Lakehouse `Files/` (for notebook 05)
7. **fabriciq_ontology_accelerator** `.whl` file uploaded to Lakehouse `Files/` (for notebook 05)

### CSV Naming Convention

The auto-discovery engine classifies tables by filename prefix:

| Prefix | Classification | Targets |
|--------|---------------|---------|
| `dim_*` | Dimension table | Lakehouse + Warehouse |
| `fact_*` | Fact table (batch or event) | Lakehouse + Warehouse + Eventhouse* |
| `stream_*` | Streaming table | Eventhouse only |

> \*Fact tables containing event keywords (`_events`, `_clickstream`, `_alerts`, `_vital`, etc.) are automatically routed to the Eventhouse as event-level tables.

## Notebook Pipeline

Run the notebooks **in order** — each builds on the previous step.

```
00_Industry_Config          ← Set industry & configure all artifact names
       │
01_Data_Ingestion           ← Discover schemas, profile data, detect quality issues
       │
02_Load_Lakehouse           ← Load dim + fact → Lakehouse Delta; events → Eventhouse
       │
03_Load_Warehouse           ← Load all tables → Warehouse with auto-generated DDL
       │
04_Create_Semantic_Model    ← Auto-generate Power BI semantic model from Lakehouse or Warehouse
       │
05_Create_Ontology          ← Create Fabric IQ Ontology from .iq package or RDF/OWL
       │
06_Create_Data_Agent        ← Create QA Agent + Ops Agent linked to ontology
       │
07_Create_Dashboards        ← Real-time KQL dashboard + Power BI report
```

## Step-by-Step Guide

### Step 0 — Configure Industry

Open **`00_Industry_Config.ipynb`** and set:

```python
INDUSTRY = "healthcare"  # Change to your target industry key
```

Optionally update:
- `EVENTHOUSE_CLUSTER_URI` — your Eventhouse cluster endpoint (e.g., `https://<name>.<region>.kusto.fabric.microsoft.com`)
- `EVENTHOUSE_DATABASE` — your Eventhouse database name
- `CSV_BASE_PATH` — if your CSV files are in a non-default location

Run all cells. The notebook will:
- Auto-name all Fabric artifacts (Lakehouse, Warehouse, Eventhouse, Ontology, Agents, Semantic Model)
- Scan the CSV folder and classify all tables
- Display a discovery summary

### Step 1 — Data Ingestion & Validation

Open **`01_Data_Ingestion.ipynb`** and run all cells.

This notebook:
- Reads every CSV file and infers schemas
- Profiles each column (nulls, distinct values, numeric ranges)
- Flags quality issues (>50% nulls = HIGH severity, >20% = MEDIUM)
- Generates a full **data catalog** with column-level details
- Produces a **load plan** showing which tables go where

> **No data is moved in this step** — it's read-only discovery and validation.

### Step 2 — Load Lakehouse + Eventhouse

Open **`02_Load_Lakehouse.ipynb`**, **attach your Lakehouse**, and run all cells.

This notebook:
- Loads all `dim_*` tables → Lakehouse as Delta tables
- Loads all `fact_*` (batch) tables → Lakehouse as Delta tables
- Loads all `fact_*` (event) + `stream_*` tables → Eventhouse KQL tables
- Generates a load summary with row counts and success/failure status

> If `EVENTHOUSE_CLUSTER_URI` is not set, Eventhouse loading is skipped gracefully.

### Step 3 — Load Warehouse

Open **`03_Load_Warehouse.ipynb`** and run all cells.

This notebook:
- Reads each CSV and infers the Spark schema
- Auto-generates `CREATE TABLE IF NOT EXISTS` DDL (Spark types → SQL Server types)
- Loads data via the `synapsesql()` connector
- Supports all table types: dimensions, batch facts, event facts, streaming

**Type mapping used:**

| Spark Type | SQL Type |
|-----------|----------|
| StringType | NVARCHAR(4000) |
| IntegerType | INT |
| LongType | BIGINT |
| FloatType / DoubleType | FLOAT |
| BooleanType | BIT |
| DateType | DATE |
| TimestampType | DATETIME2 |
| DecimalType(p,s) | DECIMAL(p,s) |

### Step 4 — Create Semantic Model

Open **`04_Create_Semantic_Model.ipynb`** and run all cells.

This notebook:
- Reads all table schemas from CSVs
- Builds a TMSL (Tabular Model Scripting Language) definition
- Auto-detects star-schema relationships (FK `_id` columns → dim PK columns)
- Auto-generates DAX measures (`SUM`, `AVERAGE`) for numeric fact columns
- Creates the semantic model from Lakehouse or Warehouse (configurable via `SEMANTIC_MODEL_SOURCE`)
- Creates the semantic model in Fabric via REST API

### Step 5 — Create Ontology

Open **`05_Create_Ontology.ipynb`** and run all cells.

Two modes are supported:

| Mode | Set `ONTOLOGY_MODE` to | Input |
|------|----------------------|-------|
| **Package** (default) | `"package"` | `.iq` ontology package file |
| **RDF/OWL** | `"rdf"` | `.rdf`/`.owl` file path or URL |

The notebook will:
- Install the `fabriciq_ontology_accelerator` wheel package
- Auto-resolve Lakehouse, Eventhouse, and Semantic Model item IDs from the workspace
- Generate the ontology definition with data bindings
- Create the ontology item in Fabric
- Display entity types, relationship types, and bindings

### Step 6 — Create Data Agents

Open **`06_Create_Data_Agent.ipynb`** and run all cells.

Creates two agents:

| Agent | Name Variable | Purpose |
|-------|--------------|---------|
| **QA Agent** | `DATA_AGENT_NAME` | Answers ad-hoc data questions via ontology |
| **Ops Agent** | `OPS_AGENT_NAME` | Monitors events, surfaces alerts and anomalies |

Both agents are linked to the ontology created in Step 5 and backed by the semantic model from Step 4.

### Step 7 — Create Dashboards

Open **`07_Create_Dashboards.ipynb`** and run all cells.

Creates two dashboard types:

**Real-Time KQL Dashboard** (requires Eventhouse):
- Auto-generates KQL queries from event/streaming table schemas
- Creates tiles: time-series charts, category breakdowns, KPI trends, live event feeds
- Pages grouped by source table, 30-second auto-refresh

**Power BI Report** (requires Semantic Model from Step 4):
- Executive Summary page with key metrics
- Per-fact-table detail pages with tables, line charts, bar charts

> Even if automated creation fails, the notebook outputs all KQL queries for manual dashboard creation.

## Configuration Reference

All configuration variables are set in `00_Industry_Config.ipynb` and inherited by every downstream notebook via `%run ./00_Industry_Config`.

| Variable | Description | Example |
|----------|-------------|---------|
| `INDUSTRY` | Industry key | `"healthcare"` |
| `INDUSTRY_LABEL` | Display label (auto-derived) | `"Healthcare"` |
| `CSV_BASE_PATH` | Path to CSV files in Lakehouse | `/lakehouse/default/Files/healthcare_data` |
| `LAKEHOUSE_NAME` | Lakehouse name | `Healthcare_Data_Bronze` |
| `WAREHOUSE_NAME` | Warehouse name | `Healthcare_Datawarehouse` |
| `EVENTHOUSE_NAME` | Eventhouse name | `healthcare_rt_store` |
| `EVENTHOUSE_CLUSTER_URI` | Eventhouse endpoint | `https://...kusto.fabric.microsoft.com` |
| `EVENTHOUSE_DATABASE` | Eventhouse DB name | *(your DB name)* |
| `ONTOLOGY_NAME` | Ontology item name | `HealthcareDocBurdenOntology` |
| `DATA_AGENT_NAME` | QA Agent name | `HealthcareQA` |
| `OPS_AGENT_NAME` | Ops Agent name | `HealthcareDocBurden` |
| `SEMANTIC_MODEL_NAME` | Power BI model name | `Healthcare_DocBurden_Model` |

## Auto-Discovered Table Lists

These lists are populated by `discover_data_sources()` in the config notebook:

| Variable | Contents |
|----------|----------|
| `DIM_TABLES` | All `dim_*` CSV files |
| `FACT_TABLES_BATCH` | `fact_*` CSVs classified as batch |
| `FACT_TABLES_EVENT` | `fact_*` CSVs classified as event-level |
| `STREAM_TABLES` | All `stream_*` CSV files |
| `LAKEHOUSE_TABLES` | `DIM_TABLES + FACT_TABLES_BATCH` |
| `WAREHOUSE_TABLES` | `DIM_TABLES + FACT_TABLES_BATCH + FACT_TABLES_EVENT` |
| `EVENTHOUSE_TABLES` | `FACT_TABLES_EVENT + STREAM_TABLES` |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ERROR: Path not found` | Upload CSVs to `Files/<industry>_data/` in your Lakehouse |
| Eventhouse cells skipped | Set `EVENTHOUSE_CLUSTER_URI` and `EVENTHOUSE_DATABASE` in notebook 00 |
| Ontology creation fails | Ensure `.whl` and `.iq` files are uploaded to Lakehouse `Files/` |
| Warehouse DDL errors | Check that the Warehouse exists and the notebook has connectivity |
| Semantic model API error | Import the TMSL JSON manually via Power BI Desktop as a fallback |
| Agent creation 403 | Verify workspace permissions (Contributor or higher) |
| No tables discovered | Check CSV naming: files must start with `dim_`, `fact_`, or `stream_` |
