# Retail

> **Reducing store manager administrative burden so they can be on the floor driving sales, not in the back office doing paperwork**

---

## The Problem

Store managers and merchandising teams spend **30–50%** of their time on inventory documentation, compliance reporting, planogram audits, and workforce scheduling paperwork instead of customer engagement and sales floor optimization. The average store manager completes **12–18 different report types** weekly — from daily sales recaps to shrinkage reports to OSHA checklists.

| Stat | Impact |
|---|---|
| **30–50%** of manager time consumed by admin tasks | Every hour off the floor costs measurable sales revenue |
| **12–18 reports** per manager per week | Daily sales, inventory, safety, scheduling, LP, compliance |
| **$10,000–$15,000** estimated lost revenue per manager-week in back office | Manager floor presence directly correlates with conversion rate |
| **35%** of store managers cite admin burden as #1 frustration | Drives turnover in a role that's already difficult to fill |
| **2–3 hours/week** on scheduling alone | Time-off requests, coverage gaps, labor compliance |

---

## Ontology Mapping

| Core Concept | Retail Equivalent |
|---|---|
| Worker Entity | `StoreManager` / `MerchandisingAssociate` |
| Client Entity | `Customer` / `StoreLocation` |
| Unit Entity | `Region` / `District` / `Store` |
| Task Type Entity | `ReportType` (inventory count, planogram audit, safety checklist, shrinkage report) |
| Core Event | `ComplianceDocEvent` — report filing, audit completion |
| System Interaction | `POSSystemInteraction` — register operations, returns processing |
| Handoff Event | `ShiftHandoff` — store manager shift change, task delegation |
| Burnout Measure | `ManagerWellnessSurvey` — workload, work-life balance |
| Quality Measure | `AuditAccuracy` — planogram compliance, inventory accuracy |
| Satisfaction Measure | `CustomerSatisfaction` — NPS, mystery shopper scores |
| Location Tracking | `StoreZonePresence` — sales floor vs back office vs register |
| UX Clickstream | `RetailSystemClickstream` — POS, WFM, inventory system usage |
| Interruption Event | `StoreIncident` — theft alert, customer complaint, vendor arrival |
| Compliance Scan | `InventoryScan` — barcode scans, cycle count verification |
| Decision Alert | `ShrinkageAlert` — loss prevention trigger, out-of-stock alert |

---

## Fabric Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         CentralData Workspace                              │
│                                                                            │
│  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │  Retail_Data_     │  │ Retail_            │  │ retail_rt_store        │  │
│  │  Bronze           │  │ Datawarehouse      │  │ (Eventhouse)           │  │
│  │  (Lakehouse)      │  │                    │  │                        │  │
│  │  • 6 dim tables   │  │ • Star schema      │  │ • 5 KQL streaming      │  │
│  │  • 12 fact tables │  │ • DirectQuery → PBI│  │   tables               │  │
│  └──────────────────┘  └───────────────────┘  └────────────────────────┘  │
│                                                                            │
│  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │  RetailDocBurden  │  │ RetailQA           │  │ RetailDocBurden         │  │
│  │  Ontology         │  │ (Data Agent)       │  │ (Operations Agent)      │  │
│  └──────────────────┘  └───────────────────┘  └────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_store_managers` | manager_id, name, store_id, region, hire_date, certifications, avg_weekly_floor_hours | 25 |
| `dim_stores` | store_id, name, district, region, format, sq_footage, headcount, revenue_tier | 30 |
| `dim_districts` | district_id, name, region, store_count, district_manager, performance_rating | 5 |
| `dim_report_types` | report_type_id, name, category, frequency, avg_completion_time_min, regulatory_required | 18 |
| `dim_product_categories` | category_id, name, department, planogram_reset_frequency, shrinkage_risk_tier | 15 |
| `dim_vendor_partners` | vendor_id, name, category, delivery_frequency, documentation_requirements | 12 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_compliance_doc_events` | event_id, manager_id, store_id, report_type_id, start_time, duration_minutes, status, overdue_flag | 180 |
| `fact_inventory_audits` | audit_id, store_id, manager_id, category_id, date, unit_count, variance_pct, doc_time_min, scan_count | 90 |
| `fact_manager_wellness` | survey_id, manager_id, store_id, date, admin_burden_score, work_life_balance, overtime_hours, floor_time_pct | 25 |
| `fact_audit_quality` | quality_id, store_id, audit_type, date, planogram_compliance_pct, inventory_accuracy_pct, safety_checklist_complete | 60 |
| `fact_customer_satisfaction` | survey_id, store_id, date, nps_score, mystery_shopper_score, wait_time_rating, staff_helpfulness | 30 |
| `fact_scheduling_events` | event_id, manager_id, store_id, date, task_type, duration_minutes, coverage_gaps_filled, overtime_approved | 120 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_pos_transactions` | txn_id, store_id, register_id, timestamp, type, total, items, associate_id, return_flag | 500 |
| `fact_inventory_scans` | scan_id, store_id, associate_id, timestamp, product_id, location, expected_qty, actual_qty, variance | 250 |
| `fact_store_incidents` | incident_id, store_id, manager_id, timestamp, type, severity, documentation_time_min, resolution | 35 |
| `fact_shift_handoffs` | handoff_id, store_id, from_manager_id, to_manager_id, timestamp, open_tasks_count, notes_length | 60 |
| `fact_retail_system_clicks` | click_id, manager_id, timestamp, system, module, action, duration_ms, error_code | 300 |
| `fact_associate_presence` | presence_id, associate_id, store_id, timestamp, zone, dwell_time_min, is_customer_facing | 400 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_pos_transactions` | POS system | txn_id, store_id, timestamp, type, total, items, return_flag, void_flag | Transaction velocity, returns, voids |
| `stream_foot_traffic` | Store sensors/cameras | sensor_id, store_id, timestamp, zone, enter_count, exit_count, dwell_seconds | Customer flow, conversion opportunity |
| `stream_inventory_scans` | Handheld scanners | scan_id, store_id, associate_id, timestamp, product_id, qty, expected_qty, discrepancy | Cycle count progress and discrepancies |
| `stream_store_incidents` | Incident management | incident_id, store_id, timestamp, type, severity, response_time_sec, is_resolved | Theft, safety, customer complaints |
| `stream_associate_location` | Badge / RTLS system | ping_id, associate_id, store_id, timestamp, zone, is_moving, is_customer_facing | Floor presence vs back office time |

---

## Use Cases — Detailed

### UC-1: Store Manager Administrative Burden

**Problem:** Store managers are hired and evaluated on sales performance, but they spend a third to half their time on reports, audits, and compliance documentation. There's strong anecdotal evidence that stores where managers spend more time on the floor perform better — but no data to quantify the relationship.

**What the Platform Measures:**
- Manager time split: floor presence vs back office vs register vs meetings (weekly)
- Report completion time by type (daily sales recap, inventory count, safety checklist, etc.)
- Correlation: manager floor hours vs store conversion rate and revenue
- Administrative task clustering: which reports could be batched or eliminated
- Manager overtime driven by documentation catch-up

**Ontology Traversal:**
> _"Show me store managers who spend less than 40% of their time on the floor, and compare their stores' NPS scores to managers with 60%+ floor time"_
>
> `StoreManager → assigned_to → Store` → `ManagerWellnessSurvey (floor_time_pct)` + `CustomerSatisfaction (nps_score)`

**Sample SQL Query — Floor Time vs Revenue:**
```sql
SELECT m.name AS manager,
       s.name AS store,
       w.floor_time_pct,
       w.admin_burden_score,
       w.overtime_hours,
       cs.nps_score,
       cs.mystery_shopper_score
FROM fact_manager_wellness w
JOIN dim_store_managers m ON w.manager_id = m.manager_id
JOIN dim_stores s ON w.store_id = s.store_id
LEFT JOIN fact_customer_satisfaction cs ON w.store_id = cs.store_id AND w.date = cs.date
ORDER BY w.floor_time_pct ASC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Manager floor time (weekly) | < 50% | < 35% |
| Admin overtime (weekly) | > 4 hours | > 8 hours |
| Report overdue count | > 2 reports | > 5 reports |
| Admin burden survey score | > 7/10 | > 9/10 |

---

### UC-2: Inventory Documentation Efficiency

**Problem:** Cycle counts are a constant documentation burden. Managers and associates scan products, reconcile discrepancies, document adjustments, and file variance reports. Some stores take 3x longer than others on identical categories — but without per-store documentation metrics, there's no way to identify and spread best practices.

**What the Platform Measures:**
- Cycle count completion time by store, category, and associate
- Scan frequency and accuracy (expected vs actual variance)
- Documentation time per inventory adjustment (writing the reason for variance)
- Receiving documentation burden (checking POs, documenting shorts, vendor credits)
- Shrinkage report time and correlation with actual shrinkage rates

**Sample KQL Query — Real-Time Cycle Count Progress:**
```kql
stream_inventory_scans
| where timestamp > ago(8h)
| summarize
    TotalScans = count(),
    Discrepancies = countif(abs(qty - expected_qty) > 0),
    DiscrepancyRate = round(100.0 * countif(abs(qty - expected_qty) > 0) / count(), 1)
  by store_id, associate_id
| order by DiscrepancyRate desc
```

**Data Agent Example Questions:**
- _"Which stores have the highest cycle count documentation time per category?"_
- _"Show me the discrepancy rate trend for Store 12 over the last month"_
- _"Are stores with faster inventory counts seeing worse shrinkage numbers?"_

---

### UC-3: Planogram Compliance Monitoring

**Problem:** Planogram resets (seasonal changes, promotional displays, category reflows) require detailed compliance documentation: before photos, reset verification, compliance scores, and exception notes. District managers need visibility into which stores complete resets on time vs which fall behind — but compliance tracking is fragmented across emails, shared drives, and ad-hoc reports.

**What the Platform Measures:**
- Planogram reset completion rate by store, district, and category
- Time-to-compliance: days from reset request to verified completion
- Documentation overhead per reset (photos, forms, verification scans)
- Non-compliance reasons and patterns (staffing, fixture issues, product availability)
- District-level reset velocity rankings

**Sample SQL Query — Reset Compliance Dashboard:**
```sql
SELECT d.name AS district,
       s.name AS store,
       pc.name AS category,
       aq.planogram_compliance_pct,
       aq.date AS audit_date,
       DATEDIFF(day, reset_request_date, aq.date) AS days_to_compliance,
       CASE
         WHEN aq.planogram_compliance_pct >= 95 THEN 'COMPLIANT'
         WHEN aq.planogram_compliance_pct >= 80 THEN 'PARTIAL'
         ELSE 'NON-COMPLIANT'
       END AS status
FROM fact_audit_quality aq
JOIN dim_stores s ON aq.store_id = s.store_id
JOIN dim_districts d ON s.district = d.district_id
JOIN dim_product_categories pc ON aq.category_id = pc.category_id
WHERE aq.audit_type = 'Planogram'
ORDER BY aq.planogram_compliance_pct ASC;
```

---

### UC-4: Workforce Scheduling Overhead

**Problem:** Scheduling is a hidden documentation burden. Managers spend 2–3 hours per week creating schedules, handling time-off requests, filling coverage gaps, tracking overtime compliance, and documenting labor law adherence (break times, minor work restrictions, maximum hour limits). Scheduling platforms help, but the manager still spends significant time in the "admin wrapper" around the tool.

**What the Platform Measures:**
- Total scheduling documentation time per manager per week
- Time-off request processing time (request → approval → schedule update)
- Coverage gap resolution time (identifying gap → finding coverage → confirming)
- Overtime approval documentation burden
- Labor compliance documentation (break tracking, minor restrictions, max hours)

**Sample SQL Query — Scheduling Burden by Store:**
```sql
SELECT m.name AS manager,
       s.name AS store,
       COUNT(*) AS scheduling_events,
       SUM(se.duration_minutes) AS total_scheduling_minutes,
       SUM(CASE WHEN se.task_type = 'Coverage Gap' THEN se.duration_minutes ELSE 0 END) AS gap_fill_minutes,
       SUM(CASE WHEN se.task_type = 'Overtime Approval' THEN se.duration_minutes ELSE 0 END) AS overtime_doc_minutes,
       AVG(se.coverage_gaps_filled) AS avg_gaps_per_week
FROM fact_scheduling_events se
JOIN dim_store_managers m ON se.manager_id = m.manager_id
JOIN dim_stores s ON se.store_id = s.store_id
GROUP BY m.name, s.name
ORDER BY total_scheduling_minutes DESC;
```

**Data Agent Example Questions:**
- _"Which stores spend the most time on scheduling documentation?"_
- _"How much time do managers spend on overtime approvals vs actual scheduling?"_
- _"Is there a correlation between scheduling time and associate satisfaction?"_

---

### UC-5: Loss Prevention Documentation

**Problem:** Every theft, safety incident, or customer complaint requires documentation: incident reports, camera review logs, police reports, and follow-up notes. LP documentation is time-sensitive (reports must be filed within hours for prosecution) but competes with all other manager responsibilities. Heavy LP documentation burden may deter timely reporting — creating a data gap that makes shrinkage harder to combat.

**What the Platform Measures:**
- Incident report completion time by incident type and severity
- Time from incident occurrence to report filing (reporting delay)
- Camera review documentation time per incident
- Follow-up documentation burden (police, insurance, corporate reporting)
- Correlation between reporting timeliness and successful prosecution/recovery

**Sample KQL Query — Real-Time Incident Monitoring:**
```kql
stream_store_incidents
| where timestamp > ago(24h) and severity in ("high", "critical")
| summarize
    IncidentCount = count(),
    AvgResponseSec = avg(response_time_sec),
    UnresolvedCount = countif(is_resolved == false)
  by store_id, type
| order by UnresolvedCount desc
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Incident report delay | > 2 hours | > 6 hours |
| Unresolved high-severity incidents | > 1 per store | > 3 per store |
| LP documentation backlog (week) | > 3 incidents | > 8 incidents |
| Shrinkage rate (rolling 4-week) | > 1.5% of revenue | > 2.5% of revenue |

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (store performance, NPS, manager floor time), district heat map | _"How are our stores performing?"_ |
| **Manager Workload** | Admin vs floor time split, report completion rates, overtime trends | _"Where is admin burden consuming floor time?"_ |
| **Inventory & Compliance** | Cycle count accuracy, planogram compliance, shrinkage trend | _"Are our inventory processes efficient?"_ |
| **Customer & Associate** | NPS trend, mystery shopper scores, associate scheduling satisfaction | _"How is the admin burden affecting customers?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **Sales Floor** | `stream_pos_transactions` | Transaction velocity, returns, void alerts |
| **Foot Traffic** | `stream_foot_traffic` | Customer flow, zone dwell, conversion |
| **Inventory** | `stream_inventory_scans` | Cycle count progress, discrepancies |
| **Incidents** | `stream_store_incidents` | Active incidents, response time, resolution |
| **Staff Presence** | `stream_associate_location` | Zone distribution, floor coverage percentage |
