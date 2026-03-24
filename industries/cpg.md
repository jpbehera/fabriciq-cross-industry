# Consumer Packaged Goods (CPG)

> **Reducing field sales documentation burden so reps can focus on selling and building retailer relationships, not completing visit reports**

---

## The Problem

Field sales reps and trade marketing teams spend **35–55%** of their time on store visit documentation, promotion compliance reporting, and distributor coordination paperwork instead of selling and building retailer relationships. The industry calls it "windshield time vs admin time" — reps are measured on revenue, but a third of their day goes to CRM entries, photo uploads, and compliance forms.

| Stat | Impact |
|---|---|
| **35–55%** of rep time on admin and documentation | Directly reduces selling time and account coverage |
| **8–12 forms** per store visit | Pre-call planning, visit report, photos, order entry, compliance check |
| **$180K** average fully loaded cost per field rep | Documenting instead of selling wastes ~$63K–$99K per rep/year |
| **30%** of visited stores show promo non-compliance | But reps lack time to document and escalate every gap |
| **15 visits/week** target vs 10–12 actual | Documentation overhead reduces store visit capacity by 20–30% |

---

## Ontology Mapping

| Core Concept | CPG Equivalent |
|---|---|
| Worker Entity | `FieldSalesRep` / `TradeMarketingManager` |
| Client Entity | `RetailAccount` / `Distributor` |
| Unit Entity | `SalesTerritory` / `Region` |
| Task Type Entity | `VisitReportType` (store audit, promo compliance, shelf survey, planogram check) |
| Core Event | `StoreVisitDocEvent` — visit reports, photo uploads, order entries |
| System Interaction | `CRMInteraction` — Salesforce, SAP CRM field operations |
| Handoff Event | `TerritoryTransfer` — rep territory changes, account reassignment |
| Burnout Measure | `RepWellnessSurvey` — travel fatigue, admin burden perception |
| Quality Measure | `VisitQuality` — data completeness, photo quality, compliance accuracy |
| Satisfaction Measure | `RetailerSatisfaction` — scorecard, JBP achievement |
| Location Tracking | `FieldLocation` — GPS route tracking, store dwell time |
| UX Clickstream | `CRMClickstream` — mobile app usage, form completion patterns |
| Interruption Event | `UrgentOrderChange` — retailer call, out-of-stock escalation |
| Compliance Scan | `ShelfScan` — product barcode scan, shelf tag verification |
| Decision Alert | `PromoComplianceAlert` — display not set, price not matched |

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_field_reps` | rep_id, name, territory_id, region, hire_date, quota, product_portfolio, certifications | 25 |
| `dim_retail_accounts` | account_id, name, banner, channel, tier, region, store_count, annual_volume | 40 |
| `dim_territories` | territory_id, name, region, rep_count, account_count, revenue_target | 8 |
| `dim_visit_report_types` | report_type_id, name, category, required_fields, avg_completion_min, photo_required | 15 |
| `dim_products` | product_id, name, brand, category, SKU, pack_size, shelf_life, promo_eligible | 50 |
| `dim_distributors` | distributor_id, name, region, coverage_area, product_lines, avg_fill_rate | 10 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_store_visit_events` | visit_id, rep_id, account_id, date, check_in_time, check_out_time, report_types_completed, total_doc_minutes, order_placed | 200 |
| `fact_promo_compliance` | compliance_id, rep_id, account_id, promo_id, date, display_present, price_correct, signage_correct, photo_uploaded, doc_time_min | 120 |
| `fact_rep_wellness` | survey_id, rep_id, territory_id, date, travel_fatigue_score, admin_burden_score, selling_time_pct, overtime_hours | 25 |
| `fact_visit_quality` | quality_id, visit_id, rep_id, date, data_completeness_pct, photo_quality_score, compliance_accuracy_pct | 200 |
| `fact_retailer_satisfaction` | survey_id, account_id, rep_id, date, scorecard_score, jbp_achievement_pct, service_rating | 40 |
| `fact_territory_performance` | perf_id, territory_id, rep_id, month, revenue, visits_completed, visits_target, selling_hours, admin_hours | 48 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_crm_interactions` | interaction_id, rep_id, timestamp, module, screen, action, duration_ms, form_field_count, error_code | 350 |
| `fact_shelf_scans` | scan_id, rep_id, account_id, timestamp, product_id, location, facing_count, out_of_stock_flag, photo_id | 180 |
| `fact_order_entries` | order_id, rep_id, account_id, timestamp, product_count, order_total, entry_time_min, distributor_id | 80 |
| `fact_territory_transfers` | transfer_id, from_rep_id, to_rep_id, account_id, timestamp, handoff_doc_time_min, open_tasks | 15 |
| `fact_promo_alerts` | alert_id, rep_id, account_id, timestamp, promo_id, alert_type, severity, action_taken, response_min | 50 |
| `fact_field_location` | ping_id, rep_id, timestamp, lat, lon, location_type, is_at_store, travel_speed_mph, dwell_minutes | 500 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_field_gps_tracking` | Mobile CRM / GPS | ping_id, rep_id, timestamp, lat, lon, speed_mph, is_at_store, store_id, dwell_min | Route efficiency, store dwell time |
| `stream_crm_activity` | Salesforce / SAP | activity_id, rep_id, timestamp, activity_type, account_id, duration_sec, form_completion_pct | Order entries, visit check-ins, report submissions |
| `stream_shelf_scans` | Image recognition / barcodes | scan_id, rep_id, store_id, timestamp, product_id, facing_count, oos_flag, compliance_score | Shelf compliance, out-of-stock detection |
| `stream_promo_alerts` | Trade promotion management | alert_id, promo_id, store_id, timestamp, alert_type, gap_description, funding_impact | Execution gaps, funding discrepancies |
| `stream_distributor_orders` | EDI / order management | order_id, distributor_id, timestamp, account_id, status, fill_rate, est_delivery_date | Order status, fulfillment delays |

---

## Use Cases — Detailed

### UC-1: Store Visit Documentation Overhead

**Problem:** Every store visit follows a documentation lifecycle: pre-call planning (review history, check promo calendar) → check-in → execute tasks (audit shelf, check promo, take orders) → document findings (photos, forms, notes) → check-out. Reps report that documentation consumes 35–45% of their in-store time, reducing actual selling and relationship-building time.

**What the Platform Measures:**
- Total in-store time decomposed: selling vs documentation vs travel
- Documentation time per visit by report type (audit, promo, order, compliance)
- Pre-call planning overhead (CRM time before visit)
- Post-visit report completion time (after check-out)
- Visit capacity impact: actual visits/week vs target, with doc time as the bottleneck

**Ontology Traversal:**
> _"Show me field reps in the Northeast territory whose documentation time per visit exceeds 30 minutes, and compare their visit count to reps with under 20 minutes"_
>
> `FieldSalesRep → assigned_to → Territory (Northeast)` → `StoreVisitDocEvent (duration > 30 min)` + `TerritoryPerformance (visits_completed)`

**Sample SQL Query — Visit Documentation Burden:**
```sql
SELECT r.name AS rep,
       t.name AS territory,
       COUNT(*) AS total_visits,
       AVG(v.total_doc_minutes) AS avg_doc_min_per_visit,
       SUM(v.total_doc_minutes) / 60.0 AS total_doc_hours,
       tp.selling_hours,
       tp.admin_hours,
       ROUND(tp.selling_hours * 100.0 / (tp.selling_hours + tp.admin_hours), 1) AS selling_pct
FROM fact_store_visit_events v
JOIN dim_field_reps r ON v.rep_id = r.rep_id
JOIN dim_territories t ON r.territory_id = t.territory_id
LEFT JOIN fact_territory_performance tp ON r.rep_id = tp.rep_id
GROUP BY r.name, t.name, tp.selling_hours, tp.admin_hours
ORDER BY avg_doc_min_per_visit DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Avg doc time per visit | > 30 minutes | > 45 minutes |
| Weekly visit count vs target | < 80% of target | < 60% of target |
| Post-visit report delay | > 2 hours | > 24 hours |
| Selling time percentage | < 55% | < 40% |

---

### UC-2: Promotion Compliance Tracking

**Problem:** CPG companies invest billions in trade promotions, but 30–40% of promotions are executed improperly at the store level (display not set up, price not correct, signage missing). Reps are supposed to audit compliance at every visit, but documentation burden means they often spot-check or skip stores — leaving millions in trade spend unverified.

**What the Platform Measures:**
- Promo compliance rate by account, banner, and rep
- Documentation time per promo audit (photo upload, form fill, exception note)
- Undocumented promotions: gap between active promos and audit records
- Compliance issue types: display, price, signage, placement
- Trade spend at risk: dollar value of non-compliant promotions

**Sample KQL Query — Real-Time Promo Gap Detection:**
```kql
stream_promo_alerts
| where timestamp > ago(24h)
| summarize
    GapCount = count(),
    TotalFundingImpact = sum(funding_impact),
    Types = make_set(alert_type)
  by store_id, promo_id
| where GapCount > 0
| order by TotalFundingImpact desc
```

**Data Agent Example Questions:**
- _"What's our overall promo compliance rate this quarter by banner?"_
- _"Which promos have the highest documentation burden per audit?"_
- _"Show me the correlation between promo compliance and incremental revenue lift"_

---

### UC-3: Sales Territory Productivity

**Problem:** Territory revenue varies, but it's unclear whether low-performing territories suffer from documentation burden (reps spending too much time on admin), poor route planning (too much windshield time), or account mix (high-maintenance accounts that consume admin time without proportional revenue).

**What the Platform Measures:**
- Revenue per selling hour (true field productivity metric)
- Admin-to-selling time ratio by territory
- Account documentation intensity (doc minutes per $1K revenue per account)
- Route efficiency: driving time vs in-store time
- Territory documentation burden ranking with revenue overlay

**Sample SQL Query — Territory Productivity Analysis:**
```sql
SELECT t.name AS territory,
       r.name AS rep,
       tp.revenue,
       tp.selling_hours,
       tp.admin_hours,
       ROUND(tp.revenue / NULLIF(tp.selling_hours, 0), 2) AS revenue_per_selling_hour,
       ROUND(tp.admin_hours * 100.0 / (tp.selling_hours + tp.admin_hours), 1) AS admin_pct,
       tp.visits_completed,
       tp.visits_target,
       ROUND(tp.visits_completed * 100.0 / NULLIF(tp.visits_target, 0), 1) AS visit_attainment_pct
FROM fact_territory_performance tp
JOIN dim_field_reps r ON tp.rep_id = r.rep_id
JOIN dim_territories t ON tp.territory_id = t.territory_id
ORDER BY revenue_per_selling_hour DESC;
```

---

### UC-4: Distributor Coordination Burden

**Problem:** In indirect distribution channels, reps spend significant time on paperwork related to distributor orders, disputes, deduction management, and fill-rate tracking. This "channel documentation overhead" is invisible in most CRM reports but can consume 15–25% of a rep's admin time.

**What the Platform Measures:**
- Documentation time per distributor interaction type (order, dispute, deduction, fill-rate report)
- Distributor dispute resolution cycle time (documentation component)
- Deduction management documentation burden per territory
- Fill-rate tracking overhead: manual reconciliation time
- Channel documentation cost: documentation hours × rep cost per hour

**Sample KQL Query — Distributor Order Status:**
```kql
stream_distributor_orders
| where timestamp > ago(7d)
| summarize
    TotalOrders = count(),
    AvgFillRate = avg(fill_rate),
    DelayedOrders = countif(status == "delayed"),
    PendingOrders = countif(status == "pending")
  by distributor_id, account_id
| order by DelayedOrders desc
```

---

### UC-5: Perfect Store Execution

**Problem:** "Perfect Store" programs define execution standards (availability, visibility, pricing, shelving) for key accounts. Auditing perfect store compliance is one of the most documentation-intensive field activities: reps must score multiple KPIs, photograph shelf conditions, document exceptions, and upload standardized reports. When reps fall behind on perfect store audits, the program loses its effectiveness.

**What the Platform Measures:**
- Perfect store audit completion rate by territory and account tier
- Time per perfect store audit (scoring + photos + documentation)
- KPI scores: availability, visibility, pricing, shelving — trended over time
- Audit backlog: accounts overdue for a perfect store visit
- Correlation between perfect store scores and account revenue growth

**Sample SQL Query — Perfect Store Compliance:**
```sql
SELECT ra.name AS account,
       ra.banner,
       ra.tier,
       AVG(vq.compliance_accuracy_pct) AS avg_perfect_store_score,
       COUNT(v.visit_id) AS audit_visits,
       AVG(v.total_doc_minutes) AS avg_audit_doc_min,
       MAX(v.date) AS last_audit_date,
       DATEDIFF(day, MAX(v.date), GETDATE()) AS days_since_last_audit
FROM fact_store_visit_events v
JOIN fact_visit_quality vq ON v.visit_id = vq.visit_id
JOIN dim_retail_accounts ra ON v.account_id = ra.account_id
WHERE v.report_types_completed LIKE '%PerfectStore%'
GROUP BY ra.name, ra.banner, ra.tier
ORDER BY days_since_last_audit DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Perfect store audit overdue | > 14 days | > 30 days |
| Perfect store score (Tier 1 accounts) | < 85% | < 70% |
| Audit documentation time | > 45 min | > 60 min |
| Audit backlog per territory | > 5 accounts | > 12 accounts |

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (visits vs target, revenue, promo compliance), territory map | _"How are our field teams performing?"_ |
| **Documentation Burden** | Doc time per visit, selling time %, admin time trend | _"How much time are reps losing to paperwork?"_ |
| **Promo Compliance** | Compliance by promo, banner, territory; trade spend at risk | _"Are our promotions executing correctly?"_ |
| **Territory Productivity** | Revenue per selling hour, visit attainment, route efficiency | _"Which territories are under-performing and why?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **Field Activity** | `stream_field_gps_tracking` | Rep locations, store dwell, route map |
| **CRM Activity** | `stream_crm_activity` | Visit check-ins, order entries, form completions |
| **Shelf Compliance** | `stream_shelf_scans` | Product availability, facing counts, OOS alerts |
| **Promo Execution** | `stream_promo_alerts` | Compliance gaps, funding impact, resolution |
| **Distribution** | `stream_distributor_orders` | Order status, fill rates, delivery tracking |
