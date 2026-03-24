# Advertising (Out-of-Home / OOH)

> **Reducing campaign operations documentation burden so account executives and chartists focus on selling and optimizing, not paperwork**

---

## The Problem

Account executives (AEs), sales coordinators, chartists, production specialists, and proof-of-performance teams spend **35–55%** of their time on campaign documentation — contract charting, order management, creative proof approvals, work order scheduling, photography coordination, and proof of performance (POP) reporting. In an industry where inventory is perishable (unsold ad space = zero revenue) and clients demand verified performance, documentation bottlenecks delay campaign launches, slow contract changes, and inflate operational costs.

| Stat | Impact |
|---|---|
| **35–55%** of AE/coordinator time on campaign admin | Directly reduces time available for prospecting, upselling, and client strategy |
| **8–15 handoffs** per campaign lifecycle | Proposal → contract → charting → production → installation → POP, each generating documentation |
| **$120K–$180K** average AE salary | 40% admin time = $48K–$72K/year per person on documentation |
| **30–45%** of contract changes require manual re-charting | CCNs (Contract Change Notifications) cascade through charting, scheduling, and production |
| **3–5 hours/week** per AE on Proof of Performance documentation | Proving to advertisers their ads were actually displayed correctly |
| **15–25%** of production orders delayed by proof approval cycles | Creative proofing back-and-forth between AE, client, and vendor |

---

## Industry Context — Inspired by Real OOH Business Processes

This data model is inspired by standard OOH advertising business processes at Level 4 (L4) granularity, covering end-to-end campaign operations:

| L3 Process | L4 Activities | Key Documentation Burden |
|---|---|---|
| **Digital Direct Ad (DDA) Server** | End-to-End DDA Campaign Management | Proposal creation, OMS contract, creative publishing, pacing/monitoring, post-buy reporting |
| **Production** | Order Management | Art/copy approval, proofing with customer, vendor print scheduling, job close-out |
| **Campaign Fulfillment** | Hold Management | In-market vs out-of-market hold validation, charting adjustments |
| **Campaign Fulfillment** | Contract Charting | Mapping contracts to physical units — individual vs grouped, manual vs automatic charting |
| **Campaign Fulfillment** | CCN Charting | Contract Change Notification processing, re-charting, short-term hold release |
| **Campaign Fulfillment** | Work Order / Digital Scheduling | Work order creation, posting instructions, installation execution, outcome documentation |
| **Campaign Fulfillment** | Inventory Onboarding / Offboarding | Adding/removing advertising units, checklist completion, system entry |
| **Photography** | Manage Photography | Photo shoot scheduling, QC review, customer photo approval, re-shoots |
| **Proof of Performance** | Manage POP | Reporting requirements, dashboard monitoring, proactive remediation, stakeholder communication |

---

## Ontology Mapping

| Core Concept | Advertising (OOH) Equivalent |
|---|---|
| Worker Entity | `AccountExecutive` / `SalesCoordinator` / `Chartist` |
| Client Entity | `Campaign` / `Advertiser` |
| Unit Entity | `Market` / `InventoryUnit` (billboard, digital display, transit, street furniture) |
| Task Type Entity | `CampaignTaskType` (charting, proofing, POP, creative approval, installation) |
| Core Event | `CampaignDocEvent` — contract processing, charting, order management, POP filing |
| System Interaction | `OMSInteraction` — Boostr, OMS, IMS, Workforce systems |
| Handoff Event | `CampaignHandoff` — AE to chartist, chartist to production, production to operations |
| Burnout Measure | `AEWellness` — admin burden, quota pressure, after-hours documentation |
| Quality Measure | `ProductionQuality` — charting accuracy, proof approval rate, POP completeness |
| Satisfaction Measure | `AdvertiserSatisfaction` — campaign accuracy, POP delivery timeliness, renewal rate |
| Location Tracking | `FieldLocation` — site visits, photo shoots, installation verification |
| UX Clickstream | `OMSClickstream` — Boostr/OMS navigation patterns, module usage |
| Interruption Event | `UrgentCampaignEvent` — last-minute creative change, hold conflict, installation failure |
| Compliance Scan | `POPVerification` — proof of performance photo review, impression verification |
| Decision Alert | `CampaignAlert` — missed install date, charting conflict, pacing underdelivery |

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_account_executives` | ae_id, name, role, market_id, team, quota_target, hire_date, specialization, active_campaigns | 25 |
| `dim_campaigns` | campaign_id, name, advertiser_id, market_id, start_date, end_date, budget, media_type, contract_value, status | 40 |
| `dim_inventory_units` | unit_id, name, type, market_id, address, lat, lng, faces, illuminated, digital, size, monthly_rate | 60 |
| `dim_markets` | market_id, name, region, dma_rank, population, total_units, digital_pct, avg_occupancy_rate | 10 |
| `dim_advertisers` | advertiser_id, name, industry, annual_spend, campaigns_ytd, tenure_years, agency_name, contact | 30 |
| `dim_vendors` | vendor_id, name, type, region, specialization, avg_turnaround_days, quality_rating | 15 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_campaign_orders` | order_id, campaign_id, ae_id, date, order_type, units_booked, doc_time_min, proof_cycles, status, production_vendor_id | 200 |
| `fact_charting_events` | charting_id, campaign_id, chartist_id, date, charting_type, units_charted, manual_charts, auto_charts, doc_time_min, ccn_flag | 150 |
| `fact_pop_reports` | pop_id, campaign_id, ae_id, date, units_verified, photos_required, photos_submitted, compliance_pct, doc_time_min | 120 |
| `fact_ae_wellness` | survey_id, ae_id, date, admin_burden_score, quota_pressure_score, overtime_hours, after_hours_doc_min, fatigue_score, work_life_balance | 25 |
| `fact_production_quality` | quality_id, order_id, ae_id, date, charting_accuracy_pct, proof_approval_rate, install_on_time_pct, pop_completeness_pct | 150 |
| `fact_advertiser_satisfaction` | survey_id, advertiser_id, campaign_id, date, campaign_accuracy_score, pop_timeliness_score, communication_score, renewal_likelihood | 30 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_oms_interactions` | interaction_id, ae_id, timestamp, system, module, action, duration_ms, campaign_id | 400 |
| `fact_contract_changes` | ccn_id, campaign_id, ae_id, timestamp, change_type, units_affected, revenue_impact, doc_time_min, approval_status | 80 |
| `fact_proof_approvals` | approval_id, order_id, ae_id, timestamp, proof_type, status, reviewer, cycle_time_hours, revision_count | 100 |
| `fact_work_orders` | wo_id, campaign_id, unit_id, timestamp, wo_type, posting_instructions, vendor_id, install_status, doc_time_min | 120 |
| `fact_pop_alerts` | alert_id, campaign_id, unit_id, timestamp, alert_type, severity, description, photos_missing, resolution_status | 60 |
| `fact_inventory_tracking` | tracking_id, unit_id, timestamp, event_type, market_id, previous_status, new_status, reason, doc_time_min | 80 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_campaign_pacing` | Ad server / DDA platform | pacing_id, campaign_id, timestamp, impressions_delivered, impressions_target, spend_pct, pacing_status | Campaign delivery pacing, under/over-delivery alerts |
| `stream_creative_status` | OMS / Boostr | status_id, order_id, campaign_id, timestamp, creative_status, proof_stage, days_pending, blocker_type | Creative proof workflow bottlenecks |
| `stream_installation_events` | Workforce / IMS | event_id, wo_id, unit_id, timestamp, event_type, crew_id, status, photo_uploaded, gps_lat, gps_lng | Field installation progress, completion verification |
| `stream_digital_impressions` | DDA ad server | impression_id, campaign_id, unit_id, timestamp, impressions_count, dwell_time_sec, audience_segment | Digital OOH real-time impression data |
| `stream_inventory_availability` | IMS / Charting system | avail_id, unit_id, market_id, timestamp, availability_status, hold_type, campaign_id, days_available | Inventory occupancy changes, hold conflicts |

---

## Use Cases — Detailed

### UC-1: Campaign Order Documentation Burden

**Problem:** Every campaign lifecycle involves 8–15 documentation handoffs: proposal creation, OMS contract entry, manager approval, charting assignment, production order, creative proofing, vendor scheduling, work order creation, installation confirmation, and POP reporting. AEs and sales coordinators are the connective tissue across all handoffs, spending 3–4 hours per campaign on documentation alone. When an AE manages 15–25 active campaigns, this admin time crowds out prospecting and client strategy.

**What the Platform Measures:**
- Campaign documentation time (proposal through go-live)
- Documentation time per handoff stage (charting, production, installation, POP)
- AE after-hours documentation (contract/order work done after 6 PM)
- Campaigns delayed by documentation bottlenecks
- Correlation between campaign complexity (multi-market, mixed media) and admin burden

**Ontology Traversal:**
> _"Show me AEs whose average campaign setup documentation exceeds 4 hours, broken down by media type and market"_
>
> `AccountExecutive → manages → Campaign` → `CampaignDocEvent (doc_time > 240 min)` → `Market` + `InventoryUnit.type`

**Sample SQL Query — Campaign Documentation Burden:**
```sql
SELECT ae.name AS account_executive,
       m.name AS market,
       c.media_type,
       COUNT(co.order_id) AS total_orders,
       AVG(co.doc_time_min) AS avg_doc_minutes,
       SUM(CASE WHEN co.doc_time_min > 60 THEN 1 ELSE 0 END) AS orders_over_60min,
       AVG(co.proof_cycles) AS avg_proof_cycles,
       SUM(co.doc_time_min) / 60.0 AS total_doc_hours
FROM fact_campaign_orders co
JOIN dim_account_executives ae ON co.ae_id = ae.ae_id
JOIN dim_campaigns c ON co.campaign_id = c.campaign_id
JOIN dim_markets m ON c.market_id = m.market_id
GROUP BY ae.name, m.name, c.media_type
ORDER BY avg_doc_minutes DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Campaign setup doc time | > 4 hours | > 6 hours |
| After-hours documentation | > 1 hour/day | > 2 hours/day |
| Proof approval cycles | > 3 rounds | > 5 rounds |
| Campaign go-live delay | > 3 days | > 7 days |

---

### UC-2: Contract Charting & CCN Processing

**Problem:** Charting is the process of mapping a signed contract to physical inventory — assigning specific billboard faces, digital display slots, and transit units to a campaign. For individual units, some charting can be automated, but grouped inventory (packages, network buys, rotary programs) requires manual charting by a specialist. Contract Change Notifications (CCNs) — which occur on 30–45% of contracts — cascade through the charting system, requiring release of previously charted units, re-charting, and schedule adjustments. A single CCN can take 30–90 minutes of documentation.

**What the Platform Measures:**
- Charting time per contract (manual vs automatic)
- CCN frequency and documentation burden per campaign
- Re-charting time when CCNs arrive late in the fulfillment cycle
- Charting conflicts (double-booked units, hold collisions)
- Chartist workload distribution and backlogs

**Sample KQL Query — Real-Time Charting Bottlenecks:**
```kql
stream_inventory_availability
| where timestamp > ago(24h)
| summarize
    TotalChanges = count(),
    HoldConflicts = countif(hold_type == "conflict"),
    NewHolds = countif(availability_status == "held"),
    Released = countif(availability_status == "available")
  by market_id
| where HoldConflicts > 0
| order by HoldConflicts desc
```

**Sample SQL Query — CCN Burden Analysis:**
```sql
SELECT ae.name AS account_executive,
       c.name AS campaign,
       COUNT(cc.ccn_id) AS total_ccns,
       AVG(cc.doc_time_min) AS avg_ccn_doc_minutes,
       SUM(cc.doc_time_min) / 60.0 AS total_ccn_doc_hours,
       SUM(cc.units_affected) AS total_units_recharted,
       SUM(cc.revenue_impact) AS total_revenue_impact
FROM fact_contract_changes cc
JOIN dim_account_executives ae ON cc.ae_id = ae.ae_id
JOIN dim_campaigns c ON cc.campaign_id = c.campaign_id
GROUP BY ae.name, c.name
ORDER BY total_ccn_doc_hours DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Manual charting backlog | > 10 contracts | > 25 contracts |
| CCN processing time | > 60 minutes | > 120 minutes |
| Charting conflicts in a market | > 3/week | > 8/week |
| CCN rate on active contracts | > 35% | > 50% |

---

### UC-3: Proof of Performance (POP) Documentation

**Problem:** Proof of Performance is a contractual obligation — OOH companies must prove to advertisers that their ads were displayed correctly, on the right units, for the contracted duration. This requires photography of each posting, impression verification for digital units, compliance reporting, and client-facing POP packages. A single campaign POP cycle can involve coordinating photographers across multiple markets, reviewing hundreds of photos, compiling reports, and addressing discrepancies. POP teams report spending 60–70% of their time on documentation rather than exception management.

**What the Platform Measures:**
- POP documentation time per campaign (photo collection, report compilation, client delivery)
- Photo completeness rate (photos submitted vs photos required)
- POP compliance percentage (units verified vs units contracted)
- Photographer coordination overhead (scheduling, assignment, re-shoots)
- Time from campaign end to POP delivery (client-facing SLA)

**Ontology Traversal:**
> _"Show me campaigns where POP compliance is below 90% and identify which markets have the most missing photos"_
>
> `Campaign → verifiedBy → POPReport` → `InventoryUnit (photos_missing > 0)` → `Market`

**Sample SQL Query — POP Compliance Analysis:**
```sql
SELECT c.name AS campaign,
       a.name AS advertiser,
       m.name AS market,
       pr.units_verified,
       pr.photos_required,
       pr.photos_submitted,
       pr.compliance_pct,
       pr.doc_time_min,
       (pr.photos_required - pr.photos_submitted) AS photos_gap
FROM fact_pop_reports pr
JOIN dim_campaigns c ON pr.campaign_id = c.campaign_id
JOIN dim_advertisers a ON c.advertiser_id = a.advertiser_id
JOIN dim_markets m ON c.market_id = m.market_id
WHERE pr.compliance_pct < 90
ORDER BY photos_gap DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| POP compliance rate | < 90% | < 75% |
| Photos missing per market | > 10 | > 25 |
| POP delivery SLA (days after end) | > 10 days | > 21 days |
| Re-shoot requests | > 5/campaign | > 15/campaign |

---

### UC-4: Production Order & Creative Proof Management

**Problem:** Production order management involves receiving artwork/copy from clients, validating print specifications ("pre-flight"), obtaining customer proof approval, placing orders with printing vendors, scheduling production, confirming vendor delivery, and closing out job orders. The proof approval cycle alone typically generates 3–5 rounds of back-and-forth between AE, client, and production specialist. Each round requires documentation — proof PDFs, revision notes, approval timestamps, and vendor communication. When approvals stall, installation dates slip, inventory sits empty, and revenue is lost.

**What the Platform Measures:**
- Proof approval cycle time (submission to approval) per round
- Total proof cycles per campaign (rounds of revision)
- Production order close-out documentation time
- Vendor turnaround time (order placed to delivery confirmation)
- Revenue impact of delayed production (empty units due to creative delays)

**Sample KQL Query — Real-Time Creative Bottlenecks:**
```kql
stream_creative_status
| where timestamp > ago(48h)
| where creative_status == "pending_approval" or creative_status == "revision_requested"
| summarize
    PendingProofs = countif(creative_status == "pending_approval"),
    RevisionRequests = countif(creative_status == "revision_requested"),
    AvgDaysPending = avg(days_pending)
  by campaign_id, proof_stage
| where AvgDaysPending > 3
| order by AvgDaysPending desc
```

**Sample SQL Query — Proof Cycle Burden:**
```sql
SELECT ae.name AS account_executive,
       c.name AS campaign,
       COUNT(pa.approval_id) AS total_proof_events,
       MAX(pa.revision_count) AS max_revisions,
       AVG(pa.cycle_time_hours) AS avg_cycle_hours,
       SUM(CASE WHEN pa.status = 'rejected' THEN 1 ELSE 0 END) AS rejections,
       SUM(CASE WHEN pa.cycle_time_hours > 48 THEN 1 ELSE 0 END) AS proofs_over_48h
FROM fact_proof_approvals pa
JOIN dim_account_executives ae ON pa.ae_id = ae.ae_id
JOIN fact_campaign_orders co ON pa.order_id = co.order_id
JOIN dim_campaigns c ON co.campaign_id = c.campaign_id
GROUP BY ae.name, c.name
ORDER BY max_revisions DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Proof approval cycle time | > 48 hours | > 96 hours |
| Proof revision rounds | > 3 | > 5 |
| Pending proofs (AE queue) | > 5 | > 12 |
| Empty units due to creative delay | > 3 units | > 8 units |

---

### UC-5: Work Order / Installation & Inventory Management

**Problem:** Work orders are the bridge between sold campaigns and physical execution. Each work order requires posting instructions, crew scheduling, material delivery coordination, installation execution, and outcome documentation (including GPS-verified photos). For a company managing thousands of units across multiple markets, the work order volume can reach hundreds per week. Inventory onboarding (new locations) and offboarding (removed locations) add further documentation burden — each requiring checklists, system entry, validation, and multi-party approval. When work order documentation falls behind, installation quality drops and POP failures cascade downstream.

**What the Platform Measures:**
- Work order documentation time (creation through completion)
- Installation completion rate (on-time, verified with photos)
- Inventory onboarding/offboarding cycle time
- Posting instruction accuracy (correct creative on correct unit)
- Field crew utilization vs documentation time

**Ontology Traversal:**
> _"Show me markets where work order completion rate is below 90% and correlate with POP failures"_
>
> `Market → contains → InventoryUnit` → `WorkOrder (install_status != 'completed')` → `POPAlert (photos_missing > 0)`

**Sample SQL Query — Work Order Performance:**
```sql
SELECT m.name AS market,
       COUNT(wo.wo_id) AS total_work_orders,
       SUM(CASE WHEN wo.install_status = 'completed' THEN 1 ELSE 0 END) AS completed,
       SUM(CASE WHEN wo.install_status = 'failed' THEN 1 ELSE 0 END) AS failed,
       AVG(wo.doc_time_min) AS avg_doc_minutes,
       ROUND(100.0 * SUM(CASE WHEN wo.install_status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 1) AS completion_pct
FROM fact_work_orders wo
JOIN dim_inventory_units u ON wo.unit_id = u.unit_id
JOIN dim_markets m ON u.market_id = m.market_id
GROUP BY m.name
ORDER BY completion_pct ASC;
```

**Sample KQL Query — Real-Time Installation Tracking:**
```kql
stream_installation_events
| where timestamp > ago(24h)
| summarize
    TotalEvents = count(),
    Completed = countif(status == "completed"),
    InProgress = countif(status == "in_progress"),
    Failed = countif(status == "failed"),
    PhotosUploaded = countif(photo_uploaded == true)
  by unit_id, crew_id
| where Failed > 0
| order by Failed desc
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Work order completion rate | < 90% | < 80% |
| Installation without photo verification | > 5/week | > 15/week |
| Inventory onboarding cycle time | > 10 days | > 21 days |
| Posting instruction errors | > 3/week | > 8/week |

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (revenue, occupancy, campaigns active), market map | _"How is our inventory performing across markets?"_ |
| **Documentation Burden** | Doc time per campaign stage, admin hours trend, after-hours work by AE | _"How much time are AEs and chartists losing to paperwork?"_ |
| **Campaign Operations** | Charting backlog, CCN rate, proof cycles, go-live delays | _"Where are the bottlenecks in campaign fulfillment?"_ |
| **Proof of Performance** | POP compliance rate, photo gaps by market, POP delivery SLA | _"Are we proving campaign delivery to advertisers on time?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **Campaign Pacing** | `stream_campaign_pacing` | Delivery pacing, under/over-delivery, spend tracking |
| **Creative Status** | `stream_creative_status` | Proof approvals, revision bottlenecks, pending creatives |
| **Installation Tracker** | `stream_installation_events` | Work order execution, crew status, photo uploads |
| **Digital Impressions** | `stream_digital_impressions` | Real-time impression counts, audience data, dwell times |
| **Inventory Status** | `stream_inventory_availability` | Unit availability, hold conflicts, occupancy changes |
