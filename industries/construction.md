# Construction

> **Reducing site documentation overhead so superintendents and project managers focus on building, not paperwork**

---

## The Problem

Construction superintendents and project managers spend **30–50%** of their time on daily logs, safety inspections, RFI management, change order documentation, and subcontractor coordination paperwork. In an industry where projects run $10M–$500M+, documentation delays cascade into schedule slippage, cost overruns, and dispute liability.

| Stat | Impact |
|---|---|
| **30–50%** of superintendent time on documentation | Directly reduces quality oversight and crew coordination |
| **12–18 daily reports** across safety, progress, weather, equipment, materials | Most completed after hours — unpaid administrative work |
| **$150K–$200K** average superintendent salary | 40% admin time = $60K–$80K/year per person on documentation |
| **35%** of change orders involve documentation disputes | Rework, claims, and disputes trace back to poor documentation |
| **4.7 hours/week** average time on RFI management | For a single superintendent overseeing one project |

---

## Ontology Mapping

| Core Concept | Construction Equivalent |
|---|---|
| Worker Entity | `SiteSupervisor` / `ProjectManager` |
| Client Entity | `Project` / `GeneralContractor` |
| Unit Entity | `ProjectSite` / `Region` |
| Task Type Entity | `InspectionType` (safety, quality, progress, environmental, equipment) |
| Core Event | `SiteDocEvent` — daily logs, inspection reports, photo documentation |
| System Interaction | `PMSystemInteraction` — Procore, PlanGrid, Bluebeam activities |
| Handoff Event | `PhaseHandoff` — trade transitions, milestone handovers |
| Burnout Measure | `SupervisorWellness` — overtime hours, admin burden perception |
| Quality Measure | `InspectionQuality` — completeness, photo coverage, defect identification |
| Satisfaction Measure | `SubcontractorSatisfaction` — coordination efficiency, payment processing |
| Location Tracking | `SiteLocation` — zone tracking, floor/area time logs |
| UX Clickstream | `PMClickstream` — Procore/PlanGrid mobile app usage patterns |
| Interruption Event | `UrgentSiteEvent` — safety stop, weather hold, material shortage |
| Compliance Scan | `PermitScan` — permit status, inspection sign-off verification |
| Decision Alert | `SafetyAlert` — near-miss, violation, OSHA trigger |

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_supervisors` | supervisor_id, name, role, certifications, years_experience, project_id, hire_date | 25 |
| `dim_projects` | project_id, name, type, value, start_date, est_completion, owner, gc_name | 12 |
| `dim_project_sites` | site_id, project_id, address, region, active_trades, total_area_sqft, floors | 12 |
| `dim_inspection_types` | inspection_type_id, name, category, required_frequency, avg_duration_min, checklist_items | 20 |
| `dim_subcontractors` | subcontractor_id, name, trade, license_no, safety_rating, projects_completed | 30 |
| `dim_trade_phases` | phase_id, name, project_id, sequence, planned_start, planned_end, budget | 25 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_daily_logs` | log_id, supervisor_id, project_id, date, weather, crew_count, work_summary, doc_time_min, photos_attached, safety_incidents | 200 |
| `fact_safety_inspections` | inspection_id, supervisor_id, site_id, date, type, findings_count, critical_count, doc_time_min, corrective_actions | 150 |
| `fact_supervisor_wellness` | survey_id, supervisor_id, date, overtime_hours, admin_burden_score, fatigue_score, work_life_balance | 25 |
| `fact_inspection_quality` | quality_id, inspection_id, supervisor_id, date, completeness_pct, photo_coverage_pct, defect_identification_rate | 150 |
| `fact_subcontractor_satisfaction` | survey_id, subcontractor_id, project_id, date, coordination_score, payment_timeliness, communication_rating | 30 |
| `fact_project_performance` | perf_id, project_id, supervisor_id, month, budget_spent, budget_remaining, schedule_variance_days, rfi_count, change_order_count | 48 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_pm_interactions` | interaction_id, supervisor_id, timestamp, system, module, action, duration_ms, document_type | 400 |
| `fact_rfi_events` | rfi_id, supervisor_id, project_id, timestamp, question, status, response_time_hours, doc_time_min, trade | 80 |
| `fact_change_orders` | change_order_id, project_id, supervisor_id, timestamp, description, cost_impact, schedule_impact_days, doc_time_min | 40 |
| `fact_phase_handoffs` | handoff_id, project_id, from_trade, to_trade, timestamp, punch_list_items, doc_time_min, approved | 25 |
| `fact_safety_alerts` | alert_id, site_id, supervisor_id, timestamp, alert_type, severity, description, immediate_action, osha_reportable | 60 |
| `fact_site_location` | ping_id, supervisor_id, timestamp, site_id, zone, floor, activity_type, dwell_minutes | 500 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_daily_log_activity` | Procore / PlanGrid | log_id, supervisor_id, timestamp, project_id, section, entry_type, photo_count | Log entries, documentation pace |
| `stream_safety_events` | IoT sensors / wearables | event_id, site_id, timestamp, event_type, zone, severity, worker_count | Near-misses, stop-work triggers |
| `stream_rfi_status` | PM software | rfi_id, project_id, timestamp, status, assigned_to, days_open, priority | RFI bottlenecks, response delays |
| `stream_weather_conditions` | Weather APIs / site stations | reading_id, site_id, timestamp, temp_f, wind_mph, precip_in, lightning_flag | Schedule impact, safety holds |
| `stream_equipment_telemetry` | Equipment IoT | telemetry_id, equipment_id, site_id, timestamp, utilization_pct, fuel_level, maintenance_flag | Equipment availability, maintenance needs |

---

## Use Cases — Detailed

### UC-1: Daily Log Documentation Burden

**Problem:** Daily logs are the backbone of construction project documentation — they record weather, crew counts, work performed, material deliveries, equipment usage, safety observations, and site photos. Superintendents typically complete these after hours, adding 1–2 hours of unpaid admin time per day. Incomplete daily logs expose firms to claims and disputes.

**What the Platform Measures:**
- Daily log completion time (per entry, per log)
- After-hours documentation (time spent after 5 PM on logs)
- Log completeness score (sections filled, photos attached, safety noted)
- Correlation between incomplete logs and project disputes
- Documentation time trend as project complexity increases

**Ontology Traversal:**
> _"Show me supervisors whose daily log completion time exceeds 90 minutes, broken down by project type and phase"_
>
> `SiteSupervisor → manages → Project` → `SiteDocEvent (daily_log, duration > 90 min)` → `TradePhase (current phase)`

**Sample SQL Query — Daily Log Burden:**
```sql
SELECT s.name AS supervisor,
       p.name AS project,
       p.type AS project_type,
       COUNT(*) AS total_logs,
       AVG(dl.doc_time_min) AS avg_doc_minutes,
       SUM(CASE WHEN dl.doc_time_min > 90 THEN 1 ELSE 0 END) AS logs_over_90min,
       AVG(dl.photos_attached) AS avg_photos,
       SUM(dl.safety_incidents) AS total_incidents
FROM fact_daily_logs dl
JOIN dim_supervisors s ON dl.supervisor_id = s.supervisor_id
JOIN dim_projects p ON dl.project_id = p.project_id
GROUP BY s.name, p.name, p.type
ORDER BY avg_doc_minutes DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Daily log completion time | > 90 minutes | > 120 minutes |
| After-hours documentation | > 1 hour/day | > 2 hours/day |
| Log completeness score | < 80% | < 60% |
| Missing daily log | 1 day | > 2 consecutive days |

---

### UC-2: Safety Inspection Documentation Overhead

**Problem:** Safety inspections are required daily/weekly depending on type (toolbox talks, confined space, scaffolding, electrical, fall protection). Each inspection generates a checklist, findings, corrective actions, and photographs. When documentation burden causes inspectors to rush or skip inspections, safety risk increases — but the burden is invisible in most project dashboards.

**What the Platform Measures:**
- Inspection documentation time by type and complexity
- Inspection completion rate vs required frequency
- Finding-to-corrective-action cycle time (documentation component)
- Safety inspection backlog per site
- Correlation between inspection documentation shortcuts and incident rates

**Sample KQL Query — Real-Time Safety Monitoring:**
```kql
stream_safety_events
| where timestamp > ago(24h)
| summarize
    TotalEvents = count(),
    CriticalEvents = countif(severity == "critical"),
    NearMisses = countif(event_type == "near_miss"),
    StopWork = countif(event_type == "stop_work")
  by site_id, zone
| where CriticalEvents > 0 or StopWork > 0
| order by CriticalEvents desc
```

---

### UC-3: RFI & Change Order Documentation

**Problem:** RFIs (Requests for Information) and change orders are among the most documentation-intensive activities on a construction project. Each RFI requires detailed written questions, reference drawings, photo documentation, and tracking through multiple parties. Change orders compound this with cost estimates, schedule impact analyses, and approval chains. A typical commercial project generates 200–800 RFIs and 50–200 change orders.

**What the Platform Measures:**
- RFI documentation time (drafting, tracking, closing)
- Change order documentation time (estimating, writing, processing)
- RFI response cycle time (architecture/engineering delays vs documentation delays)
- Superintendent time spent on RFI/CO management per week
- Claims exposure: open RFIs + unprocessed change orders

**Sample SQL Query — RFI Burden Analysis:**
```sql
SELECT s.name AS supervisor,
       p.name AS project,
       COUNT(r.rfi_id) AS total_rfis,
       AVG(r.response_time_hours) AS avg_response_hours,
       AVG(r.doc_time_min) AS avg_doc_minutes_per_rfi,
       SUM(r.doc_time_min) / 60.0 AS total_rfi_doc_hours,
       COUNT(co.change_order_id) AS total_change_orders,
       SUM(co.cost_impact) AS total_co_cost_impact,
       SUM(co.doc_time_min) / 60.0 AS total_co_doc_hours
FROM fact_rfi_events r
JOIN dim_supervisors s ON r.supervisor_id = s.supervisor_id
JOIN dim_projects p ON r.project_id = p.project_id
LEFT JOIN fact_change_orders co ON r.project_id = co.project_id AND r.supervisor_id = co.supervisor_id
GROUP BY s.name, p.name
ORDER BY total_rfi_doc_hours DESC;
```

---

### UC-4: Subcontractor Coordination Documentation

**Problem:** General contractors and superintendents manage 15–40 subcontractors per project. Coordination involves schedule alignment, scope clarification, deficiency notices, backcharge documentation, and completion certificates. Each interaction generates paperwork, and poor documentation leads to payment disputes, rework, and schedule conflicts.

**What the Platform Measures:**
- Documentation time per subcontractor interaction type
- Deficiency notice cycle time (identification → documentation → resolution → close-out)
- Backcharge documentation burden per trade
- Phase handoff documentation completeness
- Subcontractor dispute rate correlated with documentation quality

**Sample KQL Query — Phase Handoff Tracking:**
```kql
stream_rfi_status
| where timestamp > ago(7d)
| summarize
    OpenRFIs = countif(status == "open"),
    AvgDaysOpen = avg(days_open),
    OverdueRFIs = countif(days_open > 14),
    CriticalRFIs = countif(priority == "critical")
  by project_id, assigned_to
| where OverdueRFIs > 0
| order by OverdueRFIs desc
```

---

### UC-5: Punch List & Project Closeout

**Problem:** Project closeout is the most documentation-intensive phase of construction. Punch lists, as-built drawings, O&M manuals, warranties, lien releases, final inspections, and certificate of occupancy — each requires extensive documentation and multi-party sign-off. Closeout documentation burden routinely delays project completion by 2–8 weeks and ties up superintendent capacity.

**What the Platform Measures:**
- Punch list item count and documentation time per item
- Closeout documentation checklist completion rate
- Time from substantial completion to final closeout (documentation bottleneck)
- Superintendent hours dedicated to closeout documentation vs new project ramp
- Outstanding documentation items by trade/subcontractor

**Sample SQL Query — Closeout Burden:**
```sql
SELECT p.name AS project,
       p.value AS project_value,
       ph.name AS phase,
       COUNT(h.handoff_id) AS handoff_events,
       SUM(h.punch_list_items) AS total_punch_items,
       AVG(h.doc_time_min) AS avg_handoff_doc_min,
       SUM(h.doc_time_min) / 60.0 AS total_handoff_doc_hours,
       SUM(CASE WHEN h.approved = 0 THEN 1 ELSE 0 END) AS unapproved_handoffs
FROM fact_phase_handoffs h
JOIN dim_projects p ON h.project_id = p.project_id
JOIN dim_trade_phases ph ON h.project_id = ph.project_id
GROUP BY p.name, p.value, ph.name
ORDER BY total_punch_items DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Closeout documentation backlog | > 20 items | > 50 items |
| Days from substantial completion | > 30 days | > 60 days |
| Unapproved phase handoffs | > 3 | > 8 |
| Outstanding subcontractor docs | > 5 trades | > 10 trades |

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (projects, budget, schedule variance), project map | _"How are our projects performing?"_ |
| **Documentation Burden** | Doc time per log/inspection, admin hours trend, after-hours work | _"How much time are supervisors losing to paperwork?"_ |
| **Safety Compliance** | Inspection completion rate, findings trend, corrective action cycle | _"Are we meeting safety documentation requirements?"_ |
| **RFI & Change Orders** | RFI volume, response times, CO cost impact, documentation hours | _"Are documentation delays causing project delays?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **Daily Log Activity** | `stream_daily_log_activity` | Log entries, photo uploads, completion status |
| **Safety Monitoring** | `stream_safety_events` | Incidents, near-misses, stop-work events |
| **RFI Tracker** | `stream_rfi_status` | Open RFIs, response times, bottlenecks |
| **Weather Impact** | `stream_weather_conditions` | Weather holds, schedule adjustments |
| **Equipment Status** | `stream_equipment_telemetry` | Equipment utilization, maintenance alerts |
