# Notebook Instrumentation Guide

This guide shows how to add `Pipeline_Logger` tracking to notebooks 03-07. Notebooks 00-02 are already instrumented and serve as reference examples.

## Pattern Overview

Each notebook needs 3 additions:

1. **Start cell** — After `%run 00_Industry_Config`, add pipeline step start tracking
2. **Record logging** — Throughout the notebook, log record counts as tables are loaded
3. **Completion cell** — At the end, mark the step complete with summary stats

---

## Template for Each Notebook

### 1. Start Cell (insert after `%run 00_Industry_Config`)

```python
# ════════════════════════════════════════════════════════════════════════
# START PIPELINE STEP TRACKING
# ════════════════════════════════════════════════════════════════════════

try:
    pipeline_step_start("<notebook_name>", "<description>")
except NameError:
    pass
```

### 2. Record Logging (insert where tables are loaded)

```python
try:
    log_records_loaded("<notebook_name>", table_name, row_count, target="<Lakehouse|Warehouse|Eventhouse>")
except NameError:
    pass
```

### 3. Completion Cell (insert at the very end)

```python
# ════════════════════════════════════════════════════════════════════════
# COMPLETE PIPELINE STEP
# ════════════════════════════════════════════════════════════════════════

try:
    # Log any artifacts created
    log_artifact_created("<notebook_name>", "<artifact_type>", "<artifact_name>", "<artifact_id>")
    
    # Mark step complete with summary
    pipeline_step_complete("<notebook_name>", "<summary_message>")
except NameError:
    pass
```

---

## Notebook-Specific Instructions

### 03_Load_Warehouse.ipynb

**Start tracking:**
```python
pipeline_step_start("03_Load_Warehouse", "Load all tables → Warehouse SQL (auto DDL)")
```

**Record logging:** In the warehouse load loop (after each table insert), add:
```python
log_records_loaded("03_Load_Warehouse", table_name, row_count, target="Warehouse")
```

**Completion:**
```python
log_artifact_created("03_Load_Warehouse", "Warehouse", WAREHOUSE_NAME, warehouse_id)
total_rows = sum(r[2] for r in results if len(r) > 2)
pipeline_step_complete("03_Load_Warehouse", f"Loaded {len(results)} tables with {total_rows:,} rows")
```

---

### 04_Create_Semantic_Model.ipynb

**Start tracking:**
```python
pipeline_step_start("04_Create_Semantic_Model", "Create Power BI semantic model with measures & relationships")
```

**Record logging:** (No table loads, but track model metadata)
```python
log_pipeline_event("MODEL_CREATED", SEMANTIC_MODEL_NAME, 
    f"{len(bim_tables)} tables, {all_measures_count} measures, {len(relationships)} relationships")
```

**Completion:**
```python
log_artifact_created("04_Create_Semantic_Model", "SemanticModel", SEMANTIC_MODEL_NAME, sm_id)
pipeline_step_complete("04_Create_Semantic_Model", f"{len(bim_tables)} tables, {all_measures_count} measures")
```

---

### 05_Create_Ontology.ipynb

**Start tracking:**
```python
pipeline_step_start("05_Create_Ontology", "Create Fabric IQ ontology with data bindings")
```

**Completion:**
```python
log_artifact_created("05_Create_Ontology", "Ontology", ONTOLOGY_NAME, ontology_item_id)
log_artifact_created("05_Create_Ontology", "Lakehouse", LAKEHOUSE_NAME, binding_lakehouse_item_id)
if EVENTHOUSE_CLUSTER_URI:
    log_artifact_created("05_Create_Ontology", "Eventhouse", EVENTHOUSE_NAME, binding_eventhouse_item_id)
pipeline_step_complete("05_Create_Ontology", "Ontology created with data bindings")
```

---

### 06_Create_Data_Agent.ipynb

**Start tracking:**
```python
pipeline_step_start("06_Create_Data_Agent", "Deploy QA and Ops agents with industry prompts")
```

**Completion:**
```python
log_artifact_created("06_Create_Data_Agent", "DataAgent", DATA_AGENT_NAME, qa_agent_id)
log_artifact_created("06_Create_Data_Agent", "DataAgent", OPS_AGENT_NAME, ops_agent_id)
pipeline_step_complete("06_Create_Data_Agent", "QA Agent + Ops Agent created")
```

---

### 07_Create_Dashboards.ipynb

**Start tracking:**
```python
pipeline_step_start("07_Create_Dashboards", "Create KQL real-time dashboard + Power BI report")
```

**Completion:**
```python
if EVENTHOUSE_CLUSTER_URI:
    log_artifact_created("07_Create_Dashboards", "KQLDashboard", RT_DASHBOARD_NAME, rt_dashboard_id)
log_artifact_created("07_Create_Dashboards", "Report", REPORT_NAME, report_id)
pipeline_step_complete("07_Create_Dashboards", f"{len(pages)} KQL pages, {len(sections)} report pages")
```

---

## How to Add the Cells

Use the `edit_notebook_file` tool or edit in VS Code:

1. Get cell IDs: `copilot_getNotebookSummary(notebook_path)`
2. Insert start cell after the cell containing `%run 00_Industry_Config`
3. Add record logging where appropriate (look for existing `print()` statements showing row counts)
4. Insert completion cell at the very end (after the last cell)

### Example using edit_notebook_file:

```python
edit_notebook_file(
    filePath="/path/to/03_Load_Warehouse.ipynb",
    cellId="#VSC-<id_of_cell_after_config>",
    editType="insert",
    language="python",
    newCode='''# ════════════════════════════════════════════════════════════════════════
# START PIPELINE STEP TRACKING
# ════════════════════════════════════════════════════════════════════════

try:
    pipeline_step_start("03_Load_Warehouse", "Load all tables → Warehouse SQL (auto DDL)")
except NameError:
    pass'''
)
```

---

## Testing

After instrumenting:

1. Run `00_Industry_Config.ipynb` manually
2. Run the instrumented notebook
3. Verify output includes:
   - `▶ STEP: <notebook_name>` at the start
   - `✅ <notebook_name> completed in <time>` at the end
4. Run `print_pipeline_summary()` to see the full report

---

## Validation

Run the Fabric Data Pipeline (`CrossIndustry_Pipeline.json`) and verify:

1. Audit tables are created in Lakehouse:
   - `dbo.pipeline_runs`
   - `dbo.pipeline_events`
   - `dbo.pipeline_artifacts`
   - `dbo.pipeline_errors`

2. Query the run:
   ```sql
   SELECT * FROM dbo.pipeline_runs ORDER BY start_time DESC LIMIT 1;
   SELECT * FROM dbo.pipeline_events WHERE run_id = '<run_id>' ORDER BY timestamp;
   SELECT * FROM dbo.pipeline_artifacts WHERE run_id = '<run_id>';
   ```

3. Verify record counts match expected table sizes
4. Check that all artifacts are logged with IDs

---

## Reference: Fully Instrumented Notebooks

- **00_Industry_Config.ipynb** — Logs Lakehouse creation, table discovery
- **01_Data_Ingestion.ipynb** — Logs data profiling results
- **02_Load_Lakehouse.ipynb** — Logs record counts per table to Lakehouse/Eventhouse

Use these as templates for the remaining notebooks.
