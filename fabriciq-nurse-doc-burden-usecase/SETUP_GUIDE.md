# Healthcare Nursing Documentation Burden — Fabric Setup Guide

End-to-end instructions for deploying the complete Healthcare Nursing Documentation Burden demo in Microsoft Fabric. Follow the steps in order — each phase builds on the previous one.

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Fabric Workspace** | A workspace with Fabric capacity (F2+) enabled |
| **Fabric IQ Accelerator** | Download the latest [release wheel](https://github.com/microsoft/fabriciq-accelerator/releases) (`fabriciq_ontology_accelerator-*.whl`) |
| **Ontology Package** | `healthcare_nursing_ontology_package.iq` (from the `samples/` directory or custom-built — see `ontology_package_guide.md`) |
| **Python (local)** | Python 3.9+ for the streaming simulator (only needed for Step 4) |
| **Azure CLI / Browser Auth** | For `create_dashboard_api.py` (only needed for Step 8b) |

---

## Fabric Artifacts You Will Create

| Artifact | Type | Name (suggested) |
|---|---|---|
| Lakehouse | Lakehouse | `HealthcareLakehouse` |
| Eventhouse | Eventhouse + KQL Database | `medical_data_rt_store` |
| Eventstream | Eventstream | `medical_data_stream` |
| Warehouse | Data Warehouse | `Hospital_Datawarehouse` |
| Semantic Model | Semantic Model | `Healthcare_Documentation_Model` |
| Ontology | Fabric IQ Ontology | `NursingDocBurdenOntology` |
| Data Agent | Fabric IQ Data Agent | `NursingDocAgent` |
| Real-Time Dashboard | KQL Dashboard | `Healthcare Nursing Operations` |
| Power BI Report | Power BI Report | `Healthcare Documentation Burden Report` |

---

## Connection Details — Where to Plug In Your Values

Several notebooks and scripts require Fabric artifact connection details. Here is a master reference of every placeholder and where it is used:

| Placeholder | Where to Find It | Used In |
|---|---|---|
| `<YOUR_EVENTHOUSE_CLUSTER_URI>` | Eventhouse → Overview → URI (e.g., `https://xyz.z5.kusto.fabric.microsoft.com`) | `Healthcare_Generate_Ontology_Data.ipynb` (Cell 3), `Healthcare_Create_Ontology_from_Package.ipynb` (Cell 2), `generate_dashboard.py` |
| `<YOUR_DATABASE_ID>` | Eventhouse → KQL Database → Properties → ID | `generate_dashboard.py` |
| `<YOUR_WORKSPACE_ID>` | Workspace → Settings → Workspace ID | `generate_dashboard.py`, Python dashboard scripts |
| Lakehouse name | The display name of the Lakehouse you created | `Healthcare_Create_Ontology_from_Package.ipynb` (Cell 2, `binding_lakehouse_name`) |
| Eventhouse name | The display name of the Eventhouse you created | `Healthcare_Create_Ontology_from_Package.ipynb` (Cell 2, `binding_eventhouse_name`) |
| Eventhouse database name | The KQL database name inside your Eventhouse | `Healthcare_Generate_Ontology_Data.ipynb` (Cell 3), `Healthcare_Create_Ontology_from_Package.ipynb` (Cell 2) |
| `EVENT_HUB_CONNECTION_STRING` | Eventstream → Custom Endpoint source → Keys → Connection string | `simulator/.env` |
| `EVENT_HUB_NAME` | Eventstream → Custom Endpoint source → Keys → Event Hub name | `simulator/.env` |

---

## Step-by-Step Setup

### Step 1 — Create Fabric Workspace Items

In your Fabric workspace, create the following items:

1. **Lakehouse** → `HealthcareLakehouse`
2. **Eventhouse** → `medical_data_rt_store` (this also creates a KQL database with the same name)
3. **Eventstream** → `medical_data_stream`
4. **Data Warehouse** → `Hospital_Datawarehouse`

> **Tip:** Note down the Eventhouse cluster URI from the Eventhouse overview page — you'll need it in multiple steps.

---

### Step 2 — Upload Data Files

Upload the CSV files and the accelerator package to the Lakehouse:

1. Open `HealthcareLakehouse` → **Files**
2. Create a folder: `healthcare_data/`
3. Upload all 23 CSV files from `datasets/healthcare_nursing_documentation/data/` into `healthcare_data/`
4. Upload the `fabriciq_ontology_accelerator-*.whl` package to the Lakehouse **Files** root
5. Upload `healthcare_nursing_ontology_package.iq` to the Lakehouse **Files** root

Your Lakehouse Files should now look like:
```
Files/
├── fabriciq_ontology_accelerator-0.1.0-py3-none-any.whl
├── healthcare_nursing_ontology_package.iq
└── healthcare_data/
    ├── dim_nurses.csv
    ├── dim_patients.csv
    ├── ... (23 CSV files total)
    └── stream_clinical_alerts.csv
```

---

### Step 3 — Ingest Data into Lakehouse & Eventhouse

**Notebook:** `notebooks/Healthcare_Generate_Ontology_Data.ipynb`

This notebook loads all 23 CSVs into two storage layers:

| Storage | Tables | Count |
|---|---|---|
| **Lakehouse (Delta)** | 6 dimension + 6 fact tables | 12 tables, 254 rows |
| **Eventhouse (KQL)** | 6 event + 5 streaming tables | 11 tables, 642 rows |

**Configuration required (Cell 3):**

```python
eventhouse_cluster_uri = "<YOUR_EVENTHOUSE_CLUSTER_URI>"   # Eventhouse overview → URI
eventhouse_database     = "medical_data_rt_store"          # KQL database name
```

**Run:** Open the notebook in Fabric, attach `HealthcareLakehouse`, fill in the two variables above, and run all cells.

---

### Step 4 — Set Up Real-Time Streaming (Eventstream + Simulator)

This step configures the Eventstream to receive live data from the streaming simulator and route it to the Eventhouse and Lakehouse simultaneously.

**Notebook (instructions):** `notebooks/Configure_Eventstream_Routing.ipynb`

#### 4a. Configure Eventstream in Fabric

1. Open `medical_data_stream` in Fabric
2. **Add source:** Custom Endpoint → name it `nursing_realtime_source`
3. **Add destination 1:** Eventhouse → `medical_data_rt_store` → table `streaming_events` (JSON)
4. **Add destination 2:** Lakehouse → `Hospital_Data_Bronze` → table `raw_streaming_events` (JSON)
5. Click **Activate** on each destination
6. Copy the **Event Hub connection string** and **Event Hub name** from the Custom Endpoint → Keys

#### 4b. Run the Simulator (local machine)

```bash
cd datasets/healthcare_nursing_documentation/simulator

# Install dependencies
pip install -r requirements.txt

# Create .env from template and fill in your credentials
cp .env.example .env
# Edit .env — paste the connection string and Event Hub name from Step 4a

# Run the simulator
python stream_simulator.py
# Optional: python stream_simulator.py --interval 0.3 --loops 5
```

The simulator replays the 5 streaming CSVs (`stream_rtls_location`, `stream_ehr_clickstream`, `stream_nurse_call_events`, `stream_bcma_scans`, `stream_clinical_alerts`) as live events into the Eventstream.

**`.env` file format:**
```
EVENT_HUB_CONNECTION_STRING=Endpoint=sb://<namespace>.servicebus.windows.net/;SharedAccessKeyName=<key_name>;SharedAccessKey=<key>;EntityPath=<entity>
EVENT_HUB_NAME=<your_event_hub_name>
```

---

### Step 5 — Load the Data Warehouse

**Notebook:** `notebooks/Load_Warehouse_Tables.ipynb`

This notebook reads the 18 healthcare CSVs from the Lakehouse and creates corresponding tables in the Fabric Data Warehouse with proper SQL types.

**Configuration required (Cell 1):**

```python
WAREHOUSE_NAME = "Hospital_Datawarehouse"    # Your warehouse name
SCHEMA_NAME    = "dbo"                       # Target schema
CSV_BASE_PATH  = "Files/healthcare_data"     # Path in attached Lakehouse
```

**Run:** Attach `HealthcareLakehouse` as the default Lakehouse, verify the warehouse name matches what you created in Step 1, and run all cells.

**Result:** 18 tables created in `Hospital_Datawarehouse` (6 dimension + 12 fact tables).

---

### Step 6 — Create the Semantic Model

Create a Power BI Semantic Model over the warehouse tables to enable reporting:

1. Open `Hospital_Datawarehouse` in Fabric
2. Click **New semantic model** (or **Reporting → New semantic model**)
3. Name it: `Healthcare_Documentation_Model`
4. Select all 18 tables (6 dim + 12 fact)
5. Click **Create**

#### Configure Relationships

Open the semantic model in the web modeling view and create these relationships:

| From Table | Column | To Table | Column | Cardinality |
|---|---|---|---|---|
| `fact_documentation_events` | `nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |
| `fact_documentation_events` | `patient_id` | `dim_patients` | `patient_id` | Many-to-One |
| `fact_documentation_events` | `doc_type_id` | `dim_documentation_types` | `doc_type_id` | Many-to-One |
| `fact_medication_administration` | `nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |
| `fact_medication_administration` | `patient_id` | `dim_patients` | `patient_id` | Many-to-One |
| `fact_medication_administration` | `medication_id` | `dim_medications` | `medication_id` | Many-to-One |
| `fact_vital_signs` | `nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |
| `fact_vital_signs` | `patient_id` | `dim_patients` | `patient_id` | Many-to-One |
| `fact_assessments` | `nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |
| `fact_assessments` | `patient_id` | `dim_patients` | `patient_id` | Many-to-One |
| `fact_shifts` | `nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |
| `fact_patient_encounters` | `patient_id` | `dim_patients` | `patient_id` | Many-to-One |
| `fact_patient_encounters` | `unit_id` | `dim_hospital_units` | `unit_id` | Many-to-One |
| `fact_burnout_surveys` | `nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |
| `fact_patient_satisfaction` | `patient_id` | `dim_patients` | `patient_id` | Many-to-One |
| `fact_patient_satisfaction` | `unit_id` | `dim_hospital_units` | `unit_id` | Many-to-One |
| `fact_documentation_quality` | `nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |
| `fact_documentation_quality` | `patient_id` | `dim_patients` | `patient_id` | Many-to-One |
| `fact_handoff_reports` | `outgoing_nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |
| `fact_ehr_interactions` | `nurse_id` | `dim_nurses` | `nurse_id` | Many-to-One |

#### Add Key Measures (DAX)

```dax
Total Documentation Time = SUM(fact_documentation_events[duration_min])

Avg Charting Time Per Shift = DIVIDE(
    [Total Documentation Time],
    DISTINCTCOUNT(fact_shifts[shift_id])
)

Documentation Burden % = DIVIDE(
    [Total Documentation Time],
    SUM(fact_shifts[actual_duration_min])
)

Burnout Risk Score = AVERAGE(fact_burnout_surveys[emotional_exhaustion])

Patient Satisfaction Avg = AVERAGE(fact_patient_satisfaction[overall_rating])
```

---

### Step 7 — Create the Fabric IQ Ontology

The ontology maps your data to entity types, relationships, and contextualizations (events) that the Data Agent uses to answer natural language questions.

**Option A — From Package (recommended):**
**Notebook:** `notebooks/Healthcare_Create_Ontology_from_Package.ipynb`

**Configuration required (Cell 2):**

```python
binding_lakehouse_name           = "HealthcareLakehouse"          # Your Lakehouse display name
binding_eventhouse_name          = "medical_data_rt_store"        # Your Eventhouse display name
binding_eventhouse_cluster_uri   = "<YOUR_EVENTHOUSE_CLUSTER_URI>"
binding_eventhouse_database_name = "medical_data_rt_store"        # KQL database name
```

> The notebook auto-resolves the Lakehouse ID and Eventhouse ID from the workspace — you only need to provide display names and the cluster URI.

**Run:** Attach `HealthcareLakehouse`, fill in the binding configuration, and run all cells.

**Option B — From RDF definition:**
**Notebook:** `notebooks/Healthcare_Create_Ontology_from_RDF.ipynb`

This notebook defines the full ontology inline using RDF/OWL (6 entity types, 5 relationships, 11 contextualizations). Use this if you want to customize the ontology structure before creating it.

**Ontology Structure:**

| Component | Count | Examples |
|---|---|---|
| Entity Types | 6 | Nurse, Patient, HospitalUnit, DocumentationType, Medication, Diagnosis |
| Relationship Types | 5 | assigned_to, admitted_to, has_diagnosis, cares_for, prescribes_for |
| Contextualizations | 6–11 | DocumentationEvent, MedicationAdministration, VitalSignsRecording, EHRInteraction, etc. |

> See `ontology_design.md` for the complete ontology mapping with all properties, data types, and bindings.

---

### Step 8 — Create the Data Agent

The Data Agent allows natural language querying against the ontology.

1. In your Fabric workspace, click **+ New** → **Data Agent**
2. Name it: `NursingDocAgent`
3. Under **Data source**, select the ontology: `NursingDocBurdenOntology`
4. Click **Create**

**Test queries:**
- *"Which nurses had the most overtime this month?"*
- *"Show me documentation burden by unit"*
- *"What is the correlation between charting time and burnout scores?"*
- *"List patients in ICU with the most medication administration events"*

> For more details, see the [Fabric IQ Data Agent tutorial](https://learn.microsoft.com/en-us/fabric/iq/ontology/tutorial-4-create-data-agent).

---

### Step 9 — Create the Real-Time Dashboard

The Real-Time Dashboard displays live streaming data from the Eventhouse with 21 KQL tiles across 7 pages.

**Option A — Import the pre-built dashboard JSON:**

1. Run `generate_dashboard.py` to regenerate the JSON with your connection details:
   ```bash
   cd datasets/healthcare_nursing_documentation/notebooks

   # Edit the variables at the top of the script first:
   #   CLUSTER_URI  = "<YOUR_EVENTHOUSE_CLUSTER_URI>"
   #   DATABASE_ID  = "<YOUR_DATABASE_ID>"
   #   WORKSPACE_ID = "<YOUR_WORKSPACE_ID>"
   python generate_dashboard.py
   ```
   This produces `Healthcare_Nursing_Dashboard.json`.

2. Use `create_dashboard_api.py` to push it to Fabric via API:
   ```bash
   pip install azure-identity requests
   python create_dashboard_api.py
   ```
   This authenticates via browser, finds your workspace, and creates the dashboard.

**Option B — Build manually:**

Follow the step-by-step instructions in `Healthcare_RT_Dashboard_Guide.md`. The guide covers:
- Connecting the Eventhouse data source
- Creating all 21 tiles across 7 sections (Overview, Location, EHR, Calls, BCMA, Alerts, Workload)
- Configuring visuals and auto-refresh

**KQL Queries:** All 21 queries are available in `Healthcare_RT_Dashboard_Queries.kql` for reference.

**Dashboard Sections:**

| Section | Tiles | Focus Area |
|---|---|---|
| Overview | 3 | Event volume, stream breakdown, timeline |
| Nurse Location | 3 | Zone time, movement patterns, floor activity |
| EHR Clickstream | 3 | Screen usage, click patterns, navigation flow |
| Nurse Calls | 3 | Call volume, response times, escalations |
| BCMA / Medication | 3 | Scan rates, override tracking, verification |
| Clinical Alerts | 3 | Alert types, severity distribution, response times |
| Workload | 3 | Nurse workload balance, documentation vs care time |

---

### Step 10 — Create the Power BI Report

Build a Power BI report on top of the semantic model created in Step 6:

1. Open `Healthcare_Documentation_Model` semantic model
2. Click **Create report** (or open Power BI Desktop → connect to the semantic model)
3. Build the following report pages:

**Suggested Report Pages:**

| Page | Visuals | Key Metrics |
|---|---|---|
| **Documentation Burden Overview** | Card visuals, clustered bar chart, line chart | Total charting time, avg per shift, burden %, by doc type |
| **Nurse-Level Analysis** | Matrix, scatter plot | Charting time by nurse, overtime vs burnout score |
| **Unit Comparison** | Stacked bar chart, KPI cards | Documentation burden and patient satisfaction by unit |
| **Burnout Correlation** | Scatter plot with trendline, heatmap | Emotional exhaustion vs charting hours, by experience level |
| **Patient Impact** | Combo chart, table | Satisfaction scores vs documentation burden, by unit |
| **Medication & Care** | Bar chart, timeline | Medication administration patterns, vital sign recording frequency |

**Key visual combinations:**
- **Scatter plot:** `fact_burnout_surveys.emotional_exhaustion` (Y) vs. documentation hours (X), sized by `years_experience`
- **Clustered bar chart:** Documentation time by `dim_documentation_types.name`, colored by `category`
- **Line chart:** Overtime trend from `fact_shifts` over time
- **Matrix:** Nurse × documentation type, values = total minutes

---

## Pipeline Summary

```
┌──────────────────────────────────────────────────────────────────────┐
│                    End-to-End Setup Pipeline                        │
├──────────────┬───────────────────────────────────────────────────────┤
│ Step 1       │ Create workspace items (Lakehouse, Eventhouse, etc.) │
│ Step 2       │ Upload CSVs + .whl + .iq to Lakehouse Files          │
│ Step 3       │ Healthcare_Generate_Ontology_Data.ipynb              │
│              │  → 12 Lakehouse Delta tables + 11 Eventhouse KQL     │
│ Step 4       │ Configure Eventstream + run stream_simulator.py      │
│              │  → Live streaming data into Eventhouse & Lakehouse   │
│ Step 5       │ Load_Warehouse_Tables.ipynb                          │
│              │  → 18 tables in Hospital_Datawarehouse               │
│ Step 6       │ Create Semantic Model over Warehouse tables          │
│              │  → Relationships + DAX measures                      │
│ Step 7       │ Healthcare_Create_Ontology_from_Package.ipynb        │
│              │  → NursingDocBurdenOntology in Fabric IQ             │
│ Step 8       │ Create Data Agent on the Ontology                    │
│              │  → Natural language querying                         │
│ Step 9       │ generate_dashboard.py + create_dashboard_api.py      │
│              │  → Real-Time KQL Dashboard (21 tiles, 7 pages)       │
│ Step 10      │ Create Power BI report on Semantic Model             │
│              │  → Interactive documentation burden analytics        │
└──────────────┴───────────────────────────────────────────────────────┘
```

---

## File Reference

| File | Purpose | Used In Step |
|---|---|---|
| `data/*.csv` (23 files) | Source data — dimensions, facts, streaming events | 2, 3 |
| `notebooks/Healthcare_Generate_Ontology_Data.ipynb` | Loads CSVs into Lakehouse (Delta) and Eventhouse (KQL) | 3 |
| `notebooks/Configure_Eventstream_Routing.ipynb` | Instructions for Eventstream → Eventhouse + Lakehouse routing | 4 |
| `simulator/stream_simulator.py` | Sends live streaming events to Fabric Eventstream | 4 |
| `simulator/.env.example` | Template for Event Hub credentials | 4 |
| `simulator/requirements.txt` | Python dependencies for the simulator | 4 |
| `notebooks/Load_Warehouse_Tables.ipynb` | Creates and loads all 18 warehouse tables with SQL types | 5 |
| `notebooks/Healthcare_Create_Ontology_from_Package.ipynb` | Creates ontology from `.iq` package with bindings | 7 |
| `notebooks/Healthcare_Create_Ontology_from_RDF.ipynb` | Creates ontology from inline RDF/OWL definition | 7 (alt) |
| `notebooks/Healthcare_Generate_Ontology_Data.ipynb` | Also used to pre-populate data before ontology creation | 7 (prereq) |
| `notebooks/generate_dashboard.py` | Generates the Real-Time Dashboard JSON definition | 9 |
| `notebooks/create_dashboard_api.py` | Pushes dashboard JSON to Fabric via REST API | 9 |
| `notebooks/Healthcare_Nursing_Dashboard.json` | Pre-built dashboard definition (needs your IDs) | 9 |
| `notebooks/Healthcare_RT_Dashboard_Guide.md` | Manual dashboard creation instructions | 9 (alt) |
| `notebooks/Healthcare_RT_Dashboard_Queries.kql` | All 21 KQL queries used in the dashboard | 9 (ref) |
| `ontology_design.md` | Full ontology design — entity types, relationships, bindings | 7 (ref) |
| `ontology_package_guide.md` | Guide for building custom `.iq` ontology packages | 7 (ref) |

---

## Troubleshooting

| Issue | Resolution |
|---|---|
| **Eventhouse ingestion fails** | Verify the cluster URI is correct (copy from Eventhouse → Overview). Ensure the KQL database exists. |
| **Simulator connection refused** | Check `.env` has the full connection string with `Endpoint=sb://...`. Ensure the Eventstream Custom Endpoint is active. |
| **Warehouse table creation fails** | Ensure the warehouse exists and the notebook's default Lakehouse has the CSVs. Check warehouse name matches `WAREHOUSE_NAME`. |
| **Ontology creation 400 error** | Verify the Lakehouse and Eventhouse names match exactly (case-sensitive). Ensure the `.iq` file and `.whl` are uploaded. |
| **Dashboard data source error** | The cluster URI, database ID, and workspace ID in `generate_dashboard.py` must match your Eventhouse. |
| **No streaming data in dashboard** | Run the simulator (Step 4b) first. Verify Eventstream destinations are activated. Check with KQL: `streaming_events \| count`. |
| **Semantic model missing relationships** | Relationships must be created manually after model creation (Step 6). Ensure column names match between fact and dim tables. |
