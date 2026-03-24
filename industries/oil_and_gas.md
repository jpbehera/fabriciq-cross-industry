# Oil & Natural Gas

> **Reducing field documentation overhead so engineers and operators focus on safe production, not paperwork compliance**

---

## The Problem

Field engineers, drilling supervisors, and HSE officers in oil & gas spend **40–60%** of their time on documentation — daily drilling reports (DDRs), permit-to-work (PTW) paperwork, HSE compliance forms, production reports, and well integrity documentation. In an industry where a single well costs $5M–$15M to drill and regulatory non-compliance carries million-dollar fines, documentation is critical but crushingly time-consuming.

| Stat | Impact |
|---|---|
| **40–60%** of field engineer time on documentation | Less time for well optimization and production decisions |
| **2–4 hours/day** on DDR completion alone | Drilling supervisor's most time-consuming daily task |
| **$200K+** average field engineer salary | 50% admin time = $100K/year per person on paperwork |
| **15–25 PTW forms** per major maintenance event | Each requires multi-party sign-off and hazard assessment |
| **$1M–$50M** regulatory fines for HSE violations | Incomplete documentation is a leading audit finding |

---

## Ontology Mapping

| Core Concept | Oil & Gas Equivalent |
|---|---|
| Worker Entity | `FieldEngineer` / `DrillingSupervisor` / `HSEOfficer` |
| Client Entity | `WellSite` / `ProductionFacility` |
| Unit Entity | `Basin` / `Field` / `Platform` |
| Task Type Entity | `ReportType` (DDR, PTW, HSE inspection, production report, well integrity) |
| Core Event | `FieldDocEvent` — daily reports, PTW processing, inspection documentation |
| System Interaction | `SCADAInteraction` — SCADA, WellView, SAP PM activities |
| Handoff Event | `TourHandoff` — crew rotation shift change, well handover |
| Burnout Measure | `FieldCrewWellness` — rotation fatigue, admin burden, isolation score |
| Quality Measure | `ReportQuality` — completeness, accuracy, timeliness, regulatory readiness |
| Satisfaction Measure | `OperatorSatisfaction` — JV partner satisfaction, regulatory audit outcomes |
| Location Tracking | `FieldLocation` — wellsite GPS, offshore platform zone tracking |
| UX Clickstream | `SCADAClickstream` — control room interactions, alarm management |
| Interruption Event | `WellControlEvent` — kick detection, shutdown, emergency response |
| Compliance Scan | `PermitScan` — PTW status, regulatory permit verification |
| Decision Alert | `ProductionAlert` — decline curve deviation, equipment failure, HSE trigger |

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_field_engineers` | engineer_id, name, role, certifications, rotation_schedule, base, years_experience | 25 |
| `dim_well_sites` | well_id, name, basin, field, operator, spud_date, status, depth_ft, production_bpd | 20 |
| `dim_facilities` | facility_id, name, type, location, capacity, operator, regulatory_jurisdiction | 8 |
| `dim_report_types` | report_type_id, name, category, frequency, avg_completion_min, regulatory_required | 18 |
| `dim_equipment` | equipment_id, name, type, well_id, install_date, last_maintenance, criticality | 40 |
| `dim_regulatory_bodies` | reg_id, name, jurisdiction, inspection_frequency, key_requirements | 6 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_daily_drilling_reports` | ddr_id, engineer_id, well_id, date, depth_start, depth_end, footage_drilled, mud_weight, doc_time_min, incidents | 200 |
| `fact_permit_to_work` | ptw_id, engineer_id, facility_id, date, work_type, hazard_level, signatories_required, signatories_obtained, doc_time_min | 120 |
| `fact_field_wellness` | survey_id, engineer_id, date, rotation_fatigue_score, admin_burden_score, isolation_score, overtime_hours | 25 |
| `fact_report_quality` | quality_id, report_id, engineer_id, date, completeness_pct, accuracy_score, timeliness_hours, regulatory_ready | 200 |
| `fact_operator_satisfaction` | survey_id, facility_id, engineer_id, date, audit_score, jv_partner_rating, regulatory_compliance_pct | 15 |
| `fact_production_performance` | perf_id, well_id, engineer_id, month, production_bpd, decline_rate, uptime_pct, doc_hours, operating_hours | 60 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_scada_interactions` | interaction_id, engineer_id, timestamp, system, screen, action, duration_ms, alarm_count | 400 |
| `fact_hse_inspections` | inspection_id, engineer_id, facility_id, timestamp, type, findings_count, critical_findings, doc_time_min | 100 |
| `fact_well_integrity_events` | integrity_id, well_id, engineer_id, timestamp, test_type, result, pressure_psi, doc_time_min | 60 |
| `fact_tour_handoffs` | handoff_id, well_id, from_engineer, to_engineer, timestamp, open_items, doc_time_min, narrative_length | 50 |
| `fact_production_alerts` | alert_id, well_id, timestamp, alert_type, severity, parameter, threshold, actual_value, action_taken | 80 |
| `fact_field_location` | ping_id, engineer_id, timestamp, lat, lon, facility_id, zone, activity_type, dwell_minutes | 500 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_scada_alarms` | SCADA / DCS | alarm_id, facility_id, timestamp, tag, alarm_type, priority, value, setpoint | Equipment alarms, process excursions |
| `stream_well_telemetry` | Wellhead sensors | reading_id, well_id, timestamp, pressure_psi, temp_f, flow_bpd, gas_rate_mcfd | Production monitoring, decline detection |
| `stream_ptw_status` | PTW management system | ptw_id, facility_id, timestamp, status, work_type, hazard_level, approvals_pending | Permit processing, work authorization |
| `stream_hse_events` | Safety systems / wearables | event_id, facility_id, timestamp, event_type, severity, zone, personnel_count | Near-misses, gas detection, emergency |
| `stream_environmental_monitoring` | Environmental sensors | reading_id, facility_id, timestamp, parameter, value, regulatory_limit, exceedance_flag | Emissions, water quality, flaring |

---

## Use Cases — Detailed

### UC-1: Daily Drilling Report (DDR) Documentation Burden

**Problem:** DDRs are the single most important document on a drilling operation — they record every aspect of the 24-hour drilling cycle: depth drilled, mud properties, bit records, BHA configuration, formation tops, problems encountered, and time breakdowns. Drilling supervisors spend 2–4 hours per day completing these reports, often during rest periods between 12-hour tours. Incomplete or inaccurate DDRs lead to costly well control decisions and drilling optimization failures.

**What the Platform Measures:**
- DDR completion time per day, per well, per drilling phase
- Documentation time as percentage of tour (12-hour shift)
- DDR completeness score (sections populated, attachments, time logs)
- Rest-period documentation (hours spent on DDR during off-tour time)
- Correlation between DDR quality and drilling non-productive time (NPT)

**Ontology Traversal:**
> _"Show me drilling supervisors on the Permian Basin wells whose DDR completion time exceeds 3 hours, correlated with well NPT events"_
>
> `DrillingSupervisor → assigned_to → WellSite (basin = Permian)` → `FieldDocEvent (DDR, duration > 180 min)` → `ProductionPerformance (NPT hours)`

**Sample SQL Query — DDR Burden Analysis:**
```sql
SELECT e.name AS engineer,
       w.name AS well,
       w.basin,
       COUNT(*) AS total_ddrs,
       AVG(d.doc_time_min) AS avg_ddr_minutes,
       SUM(d.doc_time_min) / 60.0 AS total_ddr_hours,
       AVG(d.footage_drilled) AS avg_footage_per_day,
       SUM(d.incidents) AS total_incidents,
       pp.uptime_pct
FROM fact_daily_drilling_reports d
JOIN dim_field_engineers e ON d.engineer_id = e.engineer_id
JOIN dim_well_sites w ON d.well_id = w.well_id
LEFT JOIN fact_production_performance pp ON d.well_id = pp.well_id
GROUP BY e.name, w.name, w.basin, pp.uptime_pct
ORDER BY avg_ddr_minutes DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| DDR completion time | > 180 minutes | > 240 minutes |
| Rest-period documentation hours | > 1 hour/day | > 2 hours/day |
| DDR completeness score | < 85% | < 70% |
| Missing DDR | 1 missed day | > 1 consecutive day |

---

### UC-2: Permit-to-Work (PTW) Documentation Overhead

**Problem:** PTW is the safety control system for hazardous work — hot work, confined space entry, working at heights, electrical isolation, excavation. Each permit requires hazard identification, risk assessment, isolation verification, multi-party sign-off (originator, area authority, performing authority), and close-out documentation. Major turnarounds/shutdowns can generate 50–200 PTW per day, overwhelming the documentation system.

**What the Platform Measures:**
- PTW processing time (creation to full authorization)
- Documentation time per PTW by work type and hazard level
- Signatory bottlenecks: which approvers cause delays
- PTW backlog during turnaround/maintenance events
- Correlation between PTW documentation delays and work start delays

**Sample KQL Query — Real-Time PTW Tracking:**
```kql
stream_ptw_status
| where timestamp > ago(24h)
| summarize
    TotalPTW = count(),
    PendingApproval = countif(status == "pending_approval"),
    ActivePermits = countif(status == "active"),
    AvgApprovalsPending = avg(approvals_pending),
    HighHazard = countif(hazard_level == "high")
  by facility_id, work_type
| where PendingApproval > 3
| order by PendingApproval desc
```

---

### UC-3: HSE Compliance Documentation

**Problem:** Oil & gas operations face stringent HSE regulations from BSEE, EPA, OSHA, state agencies, and environmental bodies. Compliance requires continuous documentation of safety inspections, environmental monitoring, incident investigations, training records, and emergency drill logs. HSE officers report that 60–70% of their time is documentation — writing findings, uploading evidence, maintaining audit-ready records.

**What the Platform Measures:**
- HSE documentation hours per week by category
- Inspection documentation time vs field observation time
- Audit readiness score: percentage of records current and complete
- Corrective action documentation cycle time
- Regulatory citation risk: overdue inspections × severity

**Sample SQL Query — HSE Documentation Burden:**
```sql
SELECT e.name AS hse_officer,
       f.name AS facility,
       COUNT(i.inspection_id) AS total_inspections,
       AVG(i.doc_time_min) AS avg_doc_minutes,
       SUM(i.findings_count) AS total_findings,
       SUM(i.critical_findings) AS critical_findings,
       SUM(i.doc_time_min) / 60.0 AS total_doc_hours,
       os.regulatory_compliance_pct
FROM fact_hse_inspections i
JOIN dim_field_engineers e ON i.engineer_id = e.engineer_id
JOIN dim_facilities f ON i.facility_id = f.facility_id
LEFT JOIN fact_operator_satisfaction os ON f.facility_id = os.facility_id
GROUP BY e.name, f.name, os.regulatory_compliance_pct
ORDER BY total_doc_hours DESC;
```

---

### UC-4: Production Reporting Documentation

**Problem:** Production engineers must compile daily, weekly, and monthly production reports from SCADA data, well test results, allocation calculations, and decline curve analysis. The reports feed royalty calculations, JV partner statements, regulatory filings, and reservoir management decisions. Manual compilation from multiple systems creates a documentation burden of 10–15 hours per week per production engineer.

**What the Platform Measures:**
- Production report compilation time by report type (daily, weekly, monthly)
- Time spent on data reconciliation across systems (SCADA vs accounting vs allocation)
- Report accuracy: variance between initial report and final corrected values
- Automation opportunity: percentage of report data available via API vs manual entry
- Production engineer admin-to-analysis time ratio

**Sample KQL Query — Well Telemetry Anomaly Detection:**
```kql
stream_well_telemetry
| where timestamp > ago(1h)
| summarize
    AvgPressure = avg(pressure_psi),
    AvgFlow = avg(flow_bpd),
    MaxTemp = max(temp_f),
    Readings = count()
  by well_id, bin(timestamp, 10m)
| where AvgFlow < 50 or AvgPressure > 5000 or MaxTemp > 300
| order by timestamp desc
```

---

### UC-5: Well Integrity Management Documentation

**Problem:** Well integrity management requires comprehensive documentation of well barrier status, pressure testing, annular monitoring, cement evaluations, and corrosion inspections throughout the well lifecycle. A single well can have hundreds of integrity-related documents spanning decades. Regulatory agencies require operators to demonstrate barrier status at any point in time — making documentation completeness a license-to-operate issue.

**What the Platform Measures:**
- Well integrity documentation completeness per well
- Integrity test documentation cycle time (test → report → review → filing)
- Barrier diagram currency: percentage of wells with current barrier diagrams
- Overdue integrity inspections/tests
- Documentation cost per well per year

**Sample SQL Query — Well Integrity Documentation:**
```sql
SELECT w.name AS well,
       w.basin,
       w.status,
       COUNT(wi.integrity_id) AS total_integrity_events,
       AVG(wi.doc_time_min) AS avg_doc_minutes,
       SUM(wi.doc_time_min) / 60.0 AS total_doc_hours,
       MAX(wi.timestamp) AS last_integrity_test,
       DATEDIFF(day, MAX(wi.timestamp), GETDATE()) AS days_since_last_test,
       rq.completeness_pct AS avg_report_completeness
FROM fact_well_integrity_events wi
JOIN dim_well_sites w ON wi.well_id = w.well_id
LEFT JOIN fact_report_quality rq ON wi.engineer_id = rq.engineer_id
GROUP BY w.name, w.basin, w.status, rq.completeness_pct
ORDER BY days_since_last_test DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Well integrity test overdue | > 30 days | > 90 days |
| Barrier diagram currency | < 90% wells current | < 75% wells current |
| Integrity report completeness | < 85% | < 70% |
| SCADA alarm documentation backlog | > 10 unresolved | > 25 unresolved |

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (production, uptime, HSE incidents), basin map | _"How are our operations performing?"_ |
| **Documentation Burden** | DDR time, PTW processing, HSE doc hours, admin ratio | _"How much field time is lost to documentation?"_ |
| **HSE Compliance** | Inspection rate, findings trend, corrective actions, audit readiness | _"Are we regulatory-ready?"_ |
| **Production Analytics** | Decline curves, well performance, documentation cost per BOE | _"What's our documentation cost per barrel?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **SCADA Alarms** | `stream_scada_alarms` | Equipment alarms, process excursions |
| **Well Telemetry** | `stream_well_telemetry` | Pressure, flow, temperature monitoring |
| **Permit Status** | `stream_ptw_status` | Active PTW, pending approvals, expirations |
| **HSE Events** | `stream_hse_events` | Near-misses, gas detections, emergency alerts |
| **Environmental** | `stream_environmental_monitoring` | Emissions, exceedances, flare monitoring |
