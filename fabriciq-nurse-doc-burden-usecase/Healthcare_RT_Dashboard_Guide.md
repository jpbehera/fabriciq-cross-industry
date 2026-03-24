# Healthcare Real-Time Dashboard — Setup Guide

## Overview

This guide walks you through creating a **Fabric Real-Time Dashboard** with 21 tiles across 6 sections, powered by the KQL queries in `Healthcare_RT_Dashboard_Queries.kql`.

**Data Source:** Eventhouse `medical_data_rt_store`  
**Cluster URI:** `https://<YOUR_EVENTHOUSE>.z<N>.kusto.fabric.microsoft.com`  
**Tables:** `streaming_events`, `stream_rtls_location`, `stream_ehr_clickstream`, `stream_nurse_call_events`, `stream_bcma_scans`, `stream_clinical_alerts`

---

## Step 1 — Create the Dashboard

1. In **Microsoft Fabric**, go to your workspace
2. Click **+ New** → **Real-Time Dashboard**
3. Name it: `Healthcare Nursing Operations`
4. Click **Create**

---

## Step 2 — Connect the Data Source

1. In the dashboard, click **+ Add data source** (or the ⚙ icon → Data Sources)
2. Select **Kusto Query Language (KQL)**
3. Choose **OneLake data hub** → `medical_data_rt_store`
4. Or paste the cluster URI manually: `https://<YOUR_EVENTHOUSE>.z<N>.kusto.fabric.microsoft.com`
5. Select database: `medical_data_rt_store`
6. Click **Add**

---

## Step 3 — Build the Dashboard Pages

### Recommended Layout: 6 Sections

Create tiles in order. For each tile, click **+ Add tile**, select the data source, paste the query, choose the visual type, and configure the tile.

---

### Section 1: Overview (Tiles 1–3)

| Tile | Title | Visual | Query Ref |
|------|-------|--------|-----------|
| 1 | **Event Volume** | Multi-stat card | TILE 1 — display all 6 metrics as big numbers |
| 2 | **Events by Stream** | Donut chart | TILE 2 — `stream_type` as Category, `EventCount` as Value |
| 3 | **Event Timeline** | Time chart | TILE 3 — X: `ts`, Y: `Events`, Series: `stream_type` |

**Tile 1 configuration:** After pasting the query, choose "Stat" visual. Add 6 value columns: TotalEvents, LocationPings, EHRClicks, NurseCalls, MedScans, ClinicalAlerts.

---

### Section 2: Nurse Location & Movement (Tiles 4–6)

| Tile | Title | Visual | Query Ref |
|------|-------|--------|-----------|
| 4 | **Time by Zone Type** | Stacked bar | TILE 4 — X: `nurse_id`, Y: `TotalDwellMinutes`, Series: `zone_type` |
| 5 | **Nurse Movement** | Table | TILE 5 — columns: nurse_id, TotalPings, MovingPct, AvgSpeed, AvgDwellSec, UniqueZones |
| 6 | **Floor Activity** | Bar chart | TILE 6 — X: `floor`, Y: `Pings` |

---

### Section 3: EHR Workflow (Tiles 7–9)

| Tile | Title | Visual | Query Ref |
|------|-------|--------|-----------|
| 7 | **EHR Module Usage** | Horizontal bar | TILE 7 — Y: `ehr_module`, X: `TotalTime_sec` |
| 8 | **Interaction Types** | Pie chart | TILE 8 — Category: `event_type`, Value: `Clicks` |
| 9 | **Idle Time by Nurse** | Table | TILE 9 — all columns |

---

### Section 4: Nurse Call Response (Tiles 10–13)

| Tile | Title | Visual | Query Ref |
|------|-------|--------|-----------|
| 10 | **Response by Priority** | Bar chart | TILE 10 — X: `priority`, Y: `AvgResponse_sec`, Color: `priority` |
| 11 | **Call Reasons** | Pie chart | TILE 11 — Category: `reason`, Value: `Calls` |
| 12 | **Doc Interruptions** | Table | TILE 12 — all columns |
| 13 | **Calls by Location** | Table | TILE 13 — sortable table |

**Key insight:** Watch for high `TotalDocLost_min` values — these nurses are losing significant documentation time to call interruptions.

---

### Section 5: Medication Safety — BCMA (Tiles 14–16)

| Tile | Title | Visual | Query Ref |
|------|-------|--------|-----------|
| 14 | **Scan Results** | Donut chart | TILE 14 — Category: `scan_result`, Value: `Scans` |
| 15 | **Scan by Nurse** | Table | TILE 15 — Highlight low `SuccessRate` rows |
| 16 | **Med Alert Actions** | Stacked bar | TILE 16 — X: `alert_type`, Y: `Alerts`, Series: `alert_action` |

**Alert:** Nurses with SuccessRate below 85% may need barcode scanner inspection or re-training.

---

### Section 6: Clinical Alert Fatigue (Tiles 17–20)

| Tile | Title | Visual | Query Ref |
|------|-------|--------|-----------|
| 17 | **Alert Severity** | Donut chart | TILE 17 — Category: `severity`, Value: `Alerts` |
| 18 | **Category × Severity** | Stacked bar | TILE 18 — X: `alert_category`, Y: `Alerts`, Series: `severity` |
| 19 | **Fatigue Scores** | Table | TILE 19 — Highlight high `AvgFatigue` and low `ActionableRate` |
| 20 | **Critical Alert Feed** | Table | TILE 20 — Live feed of critical alerts |

**Key insight:** If `ActionableRate` is below 50%, alert tuning is needed to reduce fatigue.

---

### Section 7: Composite View (Tile 21)

| Tile | Title | Visual | Query Ref |
|------|-------|--------|-----------|
| 21 | **Nurse Workload** | Table | TILE 21 — Cross-table composite. Use conditional formatting: Red for AvgFatigue > 3, Yellow for ScanSuccessRate < 90 |

---

## Step 4 — Configure Auto-Refresh

1. Click the **⚙ gear** icon in the dashboard toolbar
2. Under **Auto refresh**, set the interval:
   - **Minimum:** 30 seconds (for real-time monitoring)
   - **Recommended:** 1 minute (for general use)
3. Click **Apply**

---

## Step 5 — Add Parameters (Optional)

Add a **nurse_id** parameter for filtering:

1. Click **+ Add parameter** → **Single select**
2. Name: `NurseFilter`
3. Data type: String
4. Default: All
5. Source query:
   ```kql
   stream_rtls_location | distinct nurse_id | order by nurse_id asc
   ```
6. In each tile's query, add a filter line (if parameter is set):
   ```kql
   | where nurse_id == NurseFilter or isempty(NurseFilter)
   ```

---

## Step 6 — Pin & Share

1. Click **Save** in the dashboard
2. To share: Click **Share** → add workspace members
3. To pin to a Power BI dashboard: use **Pin tile** on individual tiles

---

## Quick Reference: Query → Visual Type Mapping

| Query | Recommended Visual | Size |
|-------|-------------------|------|
| Tile 1 (Event Volume) | Multi-stat | 4×1 |
| Tile 2 (Events by Stream) | Donut | 2×2 |
| Tile 3 (Event Timeline) | Time chart | 4×2 |
| Tile 4 (Zone Dwell) | Stacked bar | 3×2 |
| Tile 5 (Nurse Movement) | Table | 3×2 |
| Tile 6 (Floor Activity) | Bar | 2×2 |
| Tile 7 (EHR Module) | Horizontal bar | 3×2 |
| Tile 8 (Interaction Types) | Pie | 2×2 |
| Tile 9 (Idle Analysis) | Table | 3×2 |
| Tile 10 (Response by Priority) | Bar | 3×2 |
| Tile 11 (Call Reasons) | Pie | 2×2 |
| Tile 12 (Doc Interruptions) | Table | 3×2 |
| Tile 13 (Calls by Location) | Table | 3×2 |
| Tile 14 (Scan Results) | Donut | 2×2 |
| Tile 15 (Scan by Nurse) | Table | 3×2 |
| Tile 16 (Med Alerts) | Stacked bar | 3×2 |
| Tile 17 (Severity) | Donut | 2×2 |
| Tile 18 (Category × Severity) | Stacked bar | 3×2 |
| Tile 19 (Fatigue Scores) | Table | 3×2 |
| Tile 20 (Critical Feed) | Table | 4×2 |
| Tile 21 (Workload Composite) | Table | 6×2 |

---

## Current Data Snapshot (Validated)

| Table | Rows | Sample Insight |
|-------|------|----------------|
| `stream_rtls_location` | 95 | NRS-002 avg 513s dwell per zone |
| `stream_ehr_clickstream` | 135 | Documentation module = 59 clicks, highest |
| `stream_nurse_call_events` | 35 | Routine calls avg 99s response |
| `stream_bcma_scans` | 57 | 85.7% overall success rate |
| `stream_clinical_alerts` | 38 | NRS-002 highest fatigue score (3.3) |

Data refreshes each time the simulator runs (360 events per run).
