"""
Generate a Fabric Real-Time Dashboard JSON definition file.

Matches the schema format used by working Fabric dashboards (schema_version 63+).
Tiles reference queries via queryRef; queries live in a separate top-level array.

Usage:
  python generate_dashboard.py
"""

import json
import uuid

# ─── Configuration ───────────────────────────────────────────────────────────
CLUSTER_URI = "https://<YOUR_EVENTHOUSE>.z<N>.kusto.fabric.microsoft.com"
DATABASE_NAME = "medical_data_rt_store"
DATABASE_ID = "<YOUR_DATABASE_ID>"
WORKSPACE_ID = "<YOUR_WORKSPACE_ID>"
OUTPUT_FILE = "Healthcare_Nursing_Dashboard.json"

# ─── Helpers ─────────────────────────────────────────────────────────────────
def uid():
    return str(uuid.uuid4())

DS_ID = uid()   # shared data-source id

# Page IDs
PAGE_OVERVIEW = uid()
PAGE_LOCATION = uid()
PAGE_EHR = uid()
PAGE_CALLS = uid()
PAGE_BCMA = uid()
PAGE_ALERTS = uid()
PAGE_WORKLOAD = uid()

# Accumulator for queries (populated by tile() calls)
_queries = []

# ─── Visual-options presets ──────────────────────────────────────────────────
def chart_opts():
    return {
        "multipleYAxes": {
            "base": {
                "id": "-1",
                "columns": [],
                "label": "",
                "yAxisMinimumValue": None,
                "yAxisMaximumValue": None,
                "yAxisScale": "linear",
                "horizontalLines": []
            },
            "additional": [],
            "showMultiplePanels": False
        },
        "hideLegend": False,
        "legendLocation": "bottom",
        "xColumnTitle": "",
        "xColumn": None,
        "yColumns": None,
        "seriesColumns": None,
        "xAxisScale": "linear",
        "verticalLine": "",
        "crossFilterDisabled": True,
        "drillthroughDisabled": False,
        "crossFilter": [],
        "drillthrough": []
    }

def table_opts():
    return {
        "table__enableRenderLinks": True,
        "colorRulesDisabled": True,
        "crossFilterDisabled": True,
        "drillthroughDisabled": False,
        "crossFilter": [],
        "drillthrough": [],
        "table__renderLinks": [],
        "colorRules": []
    }

# ─── Tile builder ────────────────────────────────────────────────────────────
def tile(title, query_text, visual_type, page_id, x, y, w, h, opts=None):
    """Create a tile + its associated query. Returns the tile dict."""
    query_id = uid()
    # Register query in the separate queries list
    _queries.append({
        "dataSource": {
            "kind": "inline",
            "dataSourceId": DS_ID
        },
        "text": query_text,
        "id": query_id,
        "usedVariables": []
    })
    return {
        "id": uid(),
        "title": title,
        "visualType": visual_type,
        "pageId": page_id,
        "layout": {"x": x, "y": y, "width": w, "height": h},
        "queryRef": {
            "kind": "query",
            "queryId": query_id
        },
        "visualOptions": opts or chart_opts()
    }

# ─── Queries ─────────────────────────────────────────────────────────────────

Q_OVERVIEW_STATS = """streaming_events
| summarize
    TotalEvents      = count(),
    LocationPings    = countif(stream_type == "rtls_location"),
    EHRClicks        = countif(stream_type == "ehr_clickstream"),
    NurseCalls       = countif(stream_type == "nurse_call_events"),
    MedScans         = countif(stream_type == "bcma_scans"),
    ClinicalAlerts   = countif(stream_type == "clinical_alerts")"""

Q_EVENTS_BY_STREAM = """streaming_events
| summarize EventCount = count() by stream_type
| order by EventCount desc"""

Q_EVENT_TIMELINE = """streaming_events
| extend ts = todatetime(data.timestamp)
| summarize Events = count() by bin(ts, 5m), stream_type"""

Q_ZONE_DWELL = """stream_rtls_location
| summarize
    TotalDwellMinutes = round(sum(dwell_time_seconds) / 60.0, 1),
    Pings = count()
  by nurse_id, zone_type
| order by TotalDwellMinutes desc"""

Q_NURSE_MOVEMENT = """stream_rtls_location
| summarize
    TotalPings       = count(),
    MovingPings      = countif(is_moving == "Yes"),
    AvgSpeed         = round(avg(speed_mph), 2),
    AvgDwellSec      = round(avg(dwell_time_seconds), 0),
    UniqueZones      = dcount(zone_name),
    AvgSignal_dBm    = round(avg(signal_strength_dbm), 0)
  by nurse_id
| extend MovingPct = round(100.0 * MovingPings / TotalPings, 1)
| project nurse_id, TotalPings, MovingPct, AvgSpeed, AvgDwellSec, UniqueZones, AvgSignal_dBm
| order by MovingPct desc"""

Q_FLOOR_ACTIVITY = """stream_rtls_location
| summarize Pings = count(), UniqueNurses = dcount(nurse_id) by floor
| order by floor asc"""

Q_EHR_MODULE = """stream_ehr_clickstream
| summarize
    Clicks        = count(),
    TotalTime_ms  = sum(duration_ms),
    AvgDuration   = round(avg(duration_ms), 0)
  by ehr_module
| extend TotalTime_sec = round(TotalTime_ms / 1000.0, 1)
| project ehr_module, Clicks, TotalTime_sec, AvgDuration
| order by TotalTime_sec desc"""

Q_INTERACTION_TYPES = """stream_ehr_clickstream
| summarize Clicks = count() by event_type
| order by Clicks desc"""

Q_IDLE_TIME = """stream_ehr_clickstream
| summarize
    TotalClicks      = count(),
    AvgIdleBefore    = round(avg(idle_seconds_before), 1),
    MaxIdleBefore    = max(idle_seconds_before),
    ErrorCount       = countif(isnotempty(error_code)),
    AvgDuration_ms   = round(avg(duration_ms), 0)
  by nurse_id
| order by AvgIdleBefore desc"""

Q_RESPONSE_PRIORITY = """stream_nurse_call_events
| summarize
    Calls           = count(),
    AvgResponse_sec = round(avg(response_time_seconds), 0),
    MaxResponse_sec = max(response_time_seconds),
    MinResponse_sec = min(response_time_seconds)
  by priority
| order by AvgResponse_sec desc"""

Q_CALL_REASONS = """stream_nurse_call_events
| summarize Calls = count() by reason
| order by Calls desc"""

Q_DOC_INTERRUPTIONS = """stream_nurse_call_events
| where interrupted_documentation == "Yes"
| summarize
    InterruptedCalls          = count(),
    AvgResumeDelay_sec        = round(avg(documentation_resume_delay_seconds), 0),
    TotalDocLost_min          = round(sum(documentation_resume_delay_seconds) / 60.0, 1),
    EscalatedCount            = countif(escalated == "Yes")
  by nurse_id
| order by TotalDocLost_min desc"""

Q_CALLS_LOCATION = """stream_nurse_call_events
| summarize
    Calls = count(),
    AvgResponse = round(avg(response_time_seconds), 0),
    Escalations = countif(escalated == "Yes")
  by unit_id, room_id
| order by Calls desc"""

Q_SCAN_RESULTS = """stream_bcma_scans
| summarize Scans = count() by scan_result
| extend Pct = round(100.0 * Scans / toscalar(stream_bcma_scans | count), 1)
| order by Scans desc"""

Q_SCAN_NURSE = """stream_bcma_scans
| summarize
    TotalScans     = count(),
    Successes      = countif(scan_result == "Success"),
    Failures       = countif(scan_result == "Failure"),
    Overrides      = countif(scan_result == "Override"),
    AvgRetries     = round(avg(retry_count), 2),
    AvgTime_ms     = round(avg(time_to_complete_ms), 0),
    AlertsTriggered = countif(isnotempty(alert_triggered) and alert_triggered != "")
  by nurse_id
| extend SuccessRate = round(100.0 * Successes / TotalScans, 1)
| project nurse_id, TotalScans, SuccessRate, Failures, Overrides, AvgRetries, AvgTime_ms, AlertsTriggered
| order by SuccessRate asc"""

Q_MED_ALERTS = """stream_bcma_scans
| where isnotempty(alert_type) and alert_type != ""
| summarize Alerts = count() by alert_type, alert_action
| order by Alerts desc"""

Q_SEVERITY = """stream_clinical_alerts
| summarize Alerts = count() by severity
| order by Alerts desc"""

Q_CATEGORY_SEVERITY = """stream_clinical_alerts
| summarize Alerts = count() by alert_category, severity
| order by Alerts desc"""

Q_FATIGUE = """stream_clinical_alerts
| summarize
    TotalAlerts      = count(),
    Actionable       = countif(was_actionable == "Yes"),
    NonActionable    = countif(was_actionable == "No"),
    Suppressed       = countif(suppressed == "Yes"),
    AvgFatigue       = round(avg(fatigue_score), 1),
    AvgResponse_sec  = round(avg(response_time_seconds), 0),
    AvgDocDelay_sec  = round(avg(documentation_delay_seconds), 0)
  by nurse_id
| extend ActionableRate = round(100.0 * Actionable / TotalAlerts, 1)
| project nurse_id, TotalAlerts, ActionableRate, Suppressed, AvgFatigue, AvgResponse_sec, AvgDocDelay_sec
| order by AvgFatigue desc"""

Q_CRITICAL_FEED = """stream_clinical_alerts
| where severity == "Critical"
| project timestamp, nurse_id, patient_id, alert_category, alert_type, description, action_taken, response_time_seconds
| order by timestamp desc"""

Q_WORKLOAD = """let loc = stream_rtls_location | summarize LocationPings = count(), AvgDwell = round(avg(dwell_time_seconds), 0) by nurse_id;
let ehr = stream_ehr_clickstream | summarize EHRClicks = count(), AvgClickDur = round(avg(duration_ms), 0) by nurse_id;
let calls = stream_nurse_call_events | summarize NurseCalls = count(), AvgCallResponse = round(avg(response_time_seconds), 0) by nurse_id;
let scans = stream_bcma_scans | summarize MedScans = count(), ScanSuccessRate = round(100.0 * countif(scan_result == "Success") / count(), 1) by nurse_id;
let alerts = stream_clinical_alerts | summarize Alerts = count(), AvgFatigue = round(avg(fatigue_score), 1) by nurse_id;
loc
| join kind=leftouter ehr on nurse_id
| join kind=leftouter calls on nurse_id
| join kind=leftouter scans on nurse_id
| join kind=leftouter alerts on nurse_id
| project nurse_id, LocationPings, AvgDwell, EHRClicks, AvgClickDur, NurseCalls, AvgCallResponse, MedScans, ScanSuccessRate, Alerts, AvgFatigue
| order by Alerts desc, NurseCalls desc"""

# ─── Build tiles per page ────────────────────────────────────────────────────
tiles = [
    # ── Page 1: Overview ──────────────────────────────────────────────────
    tile("Event Volume Summary",      Q_OVERVIEW_STATS,   "multistat",  PAGE_OVERVIEW, 0, 0,  12, 6),
    tile("Events by Stream Type",     Q_EVENTS_BY_STREAM, "pie",        PAGE_OVERVIEW, 0, 6,  12, 8),
    tile("Event Timeline (5m bins)",  Q_EVENT_TIMELINE,   "timechart",  PAGE_OVERVIEW, 0, 14, 12, 8),

    # ── Page 2: Nurse Location ────────────────────────────────────────────
    tile("Nurse Dwell Time by Zone",  Q_ZONE_DWELL,       "bar",        PAGE_LOCATION, 0, 0,  12, 8),
    tile("Nurse Movement Activity",   Q_NURSE_MOVEMENT,   "table",      PAGE_LOCATION, 0, 8,  12, 8, table_opts()),
    tile("Floor Activity",            Q_FLOOR_ACTIVITY,   "column",     PAGE_LOCATION, 0, 16, 12, 8),

    # ── Page 3: EHR Workflow ──────────────────────────────────────────────
    tile("EHR Module Usage",          Q_EHR_MODULE,       "bar",        PAGE_EHR, 0, 0,  12, 8),
    tile("EHR Interaction Types",     Q_INTERACTION_TYPES, "pie",       PAGE_EHR, 0, 8,  12, 8),
    tile("Idle Time by Nurse",        Q_IDLE_TIME,        "table",      PAGE_EHR, 0, 16, 12, 8, table_opts()),

    # ── Page 4: Nurse Calls ───────────────────────────────────────────────
    tile("Response Time by Priority", Q_RESPONSE_PRIORITY, "bar",       PAGE_CALLS, 0, 0,  12, 8),
    tile("Call Reasons",              Q_CALL_REASONS,     "pie",        PAGE_CALLS, 0, 8,  12, 8),
    tile("Documentation Interruptions", Q_DOC_INTERRUPTIONS, "table",   PAGE_CALLS, 0, 16, 12, 8, table_opts()),
    tile("Calls by Unit & Room",      Q_CALLS_LOCATION,   "table",     PAGE_CALLS, 0, 24, 12, 8, table_opts()),

    # ── Page 5: Medication Safety ─────────────────────────────────────────
    tile("Scan Results Distribution", Q_SCAN_RESULTS,     "pie",        PAGE_BCMA, 0, 0,  12, 8),
    tile("Scan Performance by Nurse", Q_SCAN_NURSE,       "table",      PAGE_BCMA, 0, 8,  12, 8, table_opts()),
    tile("Medication Alert Actions",  Q_MED_ALERTS,       "bar",        PAGE_BCMA, 0, 16, 12, 8),

    # ── Page 6: Clinical Alerts ───────────────────────────────────────────
    tile("Alert Severity",            Q_SEVERITY,         "pie",        PAGE_ALERTS, 0, 0,  12, 8),
    tile("Alerts by Category & Severity", Q_CATEGORY_SEVERITY, "bar",   PAGE_ALERTS, 0, 8,  12, 8),
    tile("Alert Fatigue by Nurse",    Q_FATIGUE,          "table",      PAGE_ALERTS, 0, 16, 12, 8, table_opts()),
    tile("Critical Alerts Feed",      Q_CRITICAL_FEED,    "table",      PAGE_ALERTS, 0, 24, 12, 8, table_opts()),

    # ── Page 7: Nurse Workload ────────────────────────────────────────────
    tile("Nurse Workload Composite",  Q_WORKLOAD,         "table",      PAGE_WORKLOAD, 0, 0, 12, 16, table_opts()),
]

# ─── Assemble dashboard ─────────────────────────────────────────────────────
dashboard = {
    "schema_version": 63,
    "title": "Healthcare Nursing Operations",
    "dataSources": [
        {
            "kind": "kusto-trident",
            "scopeId": "kusto-trident",
            "clusterUri": CLUSTER_URI,
            "database": DATABASE_ID,
            "name": DATABASE_NAME,
            "id": DS_ID,
            "workspace": WORKSPACE_ID
        }
    ],
    "pages": [
        {"id": PAGE_OVERVIEW,  "name": "Overview"},
        {"id": PAGE_LOCATION,  "name": "Nurse Location"},
        {"id": PAGE_EHR,       "name": "EHR Workflow"},
        {"id": PAGE_CALLS,     "name": "Nurse Calls"},
        {"id": PAGE_BCMA,      "name": "Medication Safety"},
        {"id": PAGE_ALERTS,    "name": "Clinical Alerts"},
        {"id": PAGE_WORKLOAD,  "name": "Nurse Workload"},
    ],
    "parameters": [],
    "baseQueries": [],
    "queries": _queries,
    "tiles": tiles
}

# ─── Write output ────────────────────────────────────────────────────────────
with open(OUTPUT_FILE, "w") as f:
    json.dump(dashboard, f, indent=2)

print(f"✅ Dashboard JSON written to: {OUTPUT_FILE}")
print(f"   Title : {dashboard['title']}")
print(f"   Pages : {len(dashboard['pages'])}")
print(f"   Tiles : {len(dashboard['tiles'])}")
print()
print("To import into Fabric:")
print("  1. Create a new Real-Time Dashboard in your workspace")
print("  2. Switch to Edit mode")
print("  3. Go to Manage tab → 'Replace with file'")
print(f"  4. Select '{OUTPUT_FILE}'")
print("  5. Save the dashboard")
