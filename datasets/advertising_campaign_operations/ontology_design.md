# Advertising Campaign Operations — Ontology Design

## Overview

This document defines the Fabric IQ ontology for the **Advertising Campaign Operations** use case. It maps the out-of-home (OOH) advertising data model to Fabric IQ entity types, relationship types, properties, contextualizations (events), and data bindings across **Lakehouse** (Delta tables) and **Eventhouse** (KQL tables via Real-Time Intelligence).

The core analytical focus is **documentation burden on Account Executives (AEs)** — quantifying how much time AEs spend on campaign orders, proof-of-performance (POP) reports, charting, contract change notices (CCNs), and work orders vs. actual client relationship management and selling activities.

**Ontology Name:** `AdvertisingCampaignOpsOntology`

---

## Concept Mapping (RDF → Fabric IQ)

| RDF Concept       | Fabric IQ Concept   | Description                                          |
|-------------------|---------------------|------------------------------------------------------|
| Class             | Entity Type         | A category of real-world object (AE, Campaign, Unit) |
| Data Property     | Property            | An attribute of an entity (name, budget, market)     |
| Object Property   | Relationship Type   | A link between two entities (manages, placed_by)     |
| Time-Series Event | Contextualization   | An event binding entities to time (CampaignOrder)    |

---

## Entity Types (Lakehouse — Delta Tables)

### 1. AccountExecutive
**Source Table:** `dim_account_executives` (Lakehouse)
**Primary Key:** `ae_id`

| Property          | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| ae_id             | String  | Primary key (AE identifier)              |
| name              | String  | Full name                                |
| role              | String  | AE, Senior AE, Sales Manager             |
| market_id         | String  | Assigned market (FK → Market)            |
| team              | String  | Sales team name                          |
| quota_target      | Float   | Annual revenue quota target              |
| hire_date         | Date    | Date of hire                             |
| specialization    | String  | Digital, Traditional, Hybrid             |
| active_campaigns  | Integer | Count of currently active campaigns      |

### 2. Campaign
**Source Table:** `dim_campaigns` (Lakehouse)
**Primary Key:** `campaign_id`

| Property          | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| campaign_id       | String  | Primary key (campaign identifier)        |
| name              | String  | Campaign name                            |
| advertiser_id     | String  | FK → Advertiser entity                   |
| market_id         | String  | FK → Market entity                       |
| start_date        | Date    | Campaign start date                      |
| end_date          | Date    | Campaign end date                        |
| budget            | Float   | Total campaign budget                    |
| media_type        | String  | Bulletin, Poster, Digital, Transit       |
| contract_value    | Float   | Signed contract value                    |
| status            | String  | Active, Completed, Pending, Cancelled    |

### 3. InventoryUnit
**Source Table:** `dim_inventory_units` (Lakehouse)
**Primary Key:** `unit_id`

| Property          | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| unit_id           | String  | Primary key (unit identifier)            |
| name              | String  | Unit display name / location label       |
| type              | String  | Bulletin, Poster, Digital, Transit       |
| market_id         | String  | FK → Market entity                       |
| address           | String  | Physical address                         |
| lat               | Float   | Latitude                                 |
| lng               | Float   | Longitude                                |
| faces             | Integer | Number of advertising faces              |
| illuminated       | String  | Yes/No                                   |
| digital           | String  | Yes/No — digital unit flag               |
| size              | String  | Dimensions (e.g., 14x48, 10.5x22)       |
| monthly_rate      | Float   | Standard monthly rate card               |

### 4. Market
**Source Table:** `dim_markets` (Lakehouse)
**Primary Key:** `market_id`

| Property            | Type    | Description                            |
|---------------------|---------|----------------------------------------|
| market_id           | String  | Primary key (market identifier)        |
| name                | String  | Market name (e.g., Atlanta, Chicago)   |
| region              | String  | Geographic region (Southeast, Midwest) |
| dma_rank            | Integer | DMA ranking                            |
| population          | Integer | Market population                      |
| total_units         | Integer | Total OOH inventory units in market    |
| digital_pct         | Float   | Percentage of digital units            |
| avg_occupancy_rate  | Float   | Average inventory occupancy rate       |

### 5. Advertiser
**Source Table:** `dim_advertisers` (Lakehouse)
**Primary Key:** `advertiser_id`

| Property          | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| advertiser_id     | String  | Primary key (advertiser identifier)      |
| name              | String  | Company / advertiser name                |
| industry          | String  | Advertiser industry vertical             |
| annual_spend      | Float   | Annual OOH advertising spend             |
| campaigns_ytd     | Integer | Number of campaigns year-to-date         |
| tenure_years      | Integer | Years as a client                        |
| agency_name       | String  | Media agency name (if applicable)        |
| contact           | String  | Primary contact person                   |

### 6. Vendor
**Source Table:** `dim_vendors` (Lakehouse)
**Primary Key:** `vendor_id`

| Property              | Type    | Description                          |
|-----------------------|---------|--------------------------------------|
| vendor_id             | String  | Primary key (vendor identifier)      |
| name                  | String  | Vendor company name                  |
| type                  | String  | Production, Installation, Creative   |
| region                | String  | Service region                       |
| specialization        | String  | Vinyl, Digital, Transit, Wallscape   |
| avg_turnaround_days   | Float   | Average production turnaround        |
| quality_rating        | Float   | Quality score (1.0–5.0)             |

---

## Relationship Types

| Relationship ID | Name              | Source Entity      | Target Entity | Cardinality | Description                                       |
|-----------------|-------------------|--------------------|---------------|-------------|---------------------------------------------------|
| REL-001         | manages_campaign  | AccountExecutive   | Campaign      | 1:Many      | AE manages one or more campaigns                  |
| REL-002         | belongs_to_market | Campaign           | Market        | Many:1      | Campaign runs in a specific market                |
| REL-003         | placed_by         | Campaign           | Advertiser    | Many:1      | Campaign is placed by an advertiser               |
| REL-004         | located_in        | InventoryUnit      | Market        | Many:1      | Inventory unit is physically located in a market  |
| REL-005         | fulfilled_by      | Campaign           | Vendor        | Many:Many   | Campaign production/installation fulfilled by vendor(s) |

**Implementation Notes:**
- `REL-001` (manages_campaign) is derived from `fact_campaign_orders.ae_id` → `dim_campaigns.campaign_id` joins.
- `REL-005` (fulfilled_by) is a dynamic relationship derived from `fact_work_orders` and `fact_campaign_orders` vendor assignments — a single campaign may use multiple vendors across its lifecycle.
- Static relationships (`REL-002`, `REL-003`, `REL-004`) are derived from dimension table foreign keys.

---

## Contextualizations (Events — Eventhouse KQL Tables)

Contextualizations bind entities to time-series events. These are the core of Real-Time Intelligence analytics for measuring AE documentation burden.

### CTX-001: CampaignOrderEvent
**Source Table:** `fact_campaign_orders` (Eventhouse)
**Key Entity Bindings:** Campaign, AccountExecutive, Vendor

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| order_id              | String   | Primary key (order identifier)                   |
| campaign_id           | String   | FK → Campaign entity                             |
| ae_id                 | String   | FK → AccountExecutive entity                     |
| date                  | DateTime | Order date                                       |
| order_type            | String   | New, Renewal, Extension, Revision                |
| units_booked          | Integer  | Number of OOH units in this order                |
| doc_time_min          | Float    | Minutes spent on order documentation             |
| proof_cycles          | Integer  | Number of proof approval cycles                  |
| status                | String   | Submitted, Approved, In-Production, Completed    |
| production_vendor_id  | String   | FK → Vendor entity                               |

**Analytical Value:** Order documentation burden per AE, proof cycle impact on admin time, order volume vs. documentation load correlation.

### CTX-002: OMSInteractionEvent
**Source Table:** `fact_oms_interactions` (Eventhouse)
**Key Entity Bindings:** AccountExecutive, Campaign

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| interaction_id        | String   | Primary key (interaction identifier)             |
| ae_id                 | String   | FK → AccountExecutive entity                     |
| timestamp             | DateTime | Interaction timestamp                            |
| system                | String   | OMS platform (e.g., Salesforce, VistarOMS)       |
| module                | String   | Module accessed (Orders, Inventory, Reporting)   |
| action                | String   | Create, Update, Search, Export, Upload            |
| duration_ms           | Integer  | Time spent on this interaction (milliseconds)    |
| campaign_id           | String   | FK → Campaign entity (if applicable)             |

**Analytical Value:** OMS system friction analysis, non-productive navigation time, module usage patterns, system-switching overhead.

### CTX-003: ChartingEvent
**Source Table:** `fact_charting_events` (Eventhouse)
**Key Entity Bindings:** Campaign, AccountExecutive

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| charting_id           | String   | Primary key (charting identifier)                |
| campaign_id           | String   | FK → Campaign entity                             |
| chartist_id           | String   | Chartist / AE who performed charting             |
| date                  | DateTime | Charting date                                    |
| charting_type         | String   | Initial, Revision, Recharting                    |
| units_charted         | Integer  | Number of units charted                          |
| manual_charts         | Integer  | Units charted manually                           |
| auto_charts           | Integer  | Units charted via automated tools                |
| doc_time_min          | Float    | Time spent on charting documentation             |
| ccn_flag              | String   | Yes/No — triggered by a contract change          |

**Analytical Value:** Manual vs. automated charting ratio, CCN-driven recharting burden, charting accuracy and rework patterns.

### CTX-004: POPReportEvent
**Source Table:** `fact_pop_reports` (Eventhouse)
**Key Entity Bindings:** Campaign, AccountExecutive

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| pop_id                | String   | Primary key (POP report identifier)              |
| campaign_id           | String   | FK → Campaign entity                             |
| ae_id                 | String   | FK → AccountExecutive entity                     |
| date                  | DateTime | POP report date                                  |
| units_verified        | Integer  | Number of units verified for POP                 |
| photos_required       | Integer  | Photos required for proof                        |
| photos_submitted      | Integer  | Photos actually submitted                        |
| compliance_pct        | Float    | POP compliance percentage                        |
| doc_time_min          | Float    | Time spent on POP documentation                  |

**Analytical Value:** POP documentation cascade — time per unit verified, photo compliance gaps, campaign-level POP burden aggregation.

### CTX-005: ContractChangeEvent
**Source Table:** `fact_contract_changes` (Eventhouse)
**Key Entity Bindings:** Campaign, AccountExecutive

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| ccn_id                | String   | Primary key (contract change notice ID)          |
| campaign_id           | String   | FK → Campaign entity                             |
| ae_id                 | String   | FK → AccountExecutive entity                     |
| timestamp             | DateTime | Change timestamp                                 |
| change_type           | String   | UnitSwap, DateChange, BudgetRevision, Creative   |
| units_affected        | Integer  | Number of units impacted by change               |
| revenue_impact        | Float    | Revenue impact of the change                     |
| doc_time_min          | Float    | Minutes spent documenting the change             |
| approval_status       | String   | Pending, Approved, Rejected                      |

**Analytical Value:** CCN documentation burden — change frequency per campaign, ripple effect on recharting and POP, revenue-at-risk correlation.

### CTX-006: WorkOrderEvent
**Source Table:** `fact_work_orders` (Eventhouse)
**Key Entity Bindings:** Campaign, InventoryUnit, Vendor

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| wo_id                 | String   | Primary key (work order identifier)              |
| campaign_id           | String   | FK → Campaign entity                             |
| unit_id               | String   | FK → InventoryUnit entity                        |
| timestamp             | DateTime | Work order timestamp                             |
| wo_type               | String   | Install, Takedown, Repair, Refresh               |
| posting_instructions  | String   | Posting / installation instructions              |
| vendor_id             | String   | FK → Vendor entity                               |
| install_status        | String   | Scheduled, In-Progress, Completed, Failed        |
| doc_time_min          | Float    | Time spent documenting the work order            |

**Analytical Value:** Work order volume per campaign, vendor fulfillment tracking, installation documentation overhead.

### CTX-007: ProofApprovalEvent
**Source Table:** `fact_proof_approvals` (Eventhouse)
**Key Entity Bindings:** AccountExecutive

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| approval_id           | String   | Primary key (approval identifier)                |
| order_id              | String   | FK → CampaignOrderEvent                          |
| ae_id                 | String   | FK → AccountExecutive entity                     |
| timestamp             | DateTime | Approval event timestamp                         |
| proof_type            | String   | Creative, Posting, POP                           |
| status                | String   | Approved, Revision-Requested, Rejected           |
| reviewer              | String   | Reviewer name / role                             |
| cycle_time_hours      | Float    | Hours from submission to decision                |
| revision_count        | Integer  | Number of revisions on this proof                |

**Analytical Value:** Proof cycle bottleneck analysis, revision frequency by proof type, AE time sunk in approval workflows.

### CTX-008: POPAlertEvent
**Source Table:** `fact_pop_alerts` (Eventhouse)
**Key Entity Bindings:** Campaign, InventoryUnit

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| alert_id              | String   | Primary key (alert identifier)                   |
| campaign_id           | String   | FK → Campaign entity                             |
| unit_id               | String   | FK → InventoryUnit entity                        |
| timestamp             | DateTime | Alert timestamp                                  |
| alert_type            | String   | MissingPhoto, ComplianceGap, LatePOP, DamagedUnit|
| severity              | String   | Low, Medium, High, Critical                      |
| description           | String   | Human-readable alert description                 |
| photos_missing        | Integer  | Number of photos missing                         |
| resolution_status     | String   | Open, Acknowledged, Resolved                     |

**Analytical Value:** POP alert cascade — missing photo follow-up burden, compliance gap resolution time, alert fatigue for high-volume campaigns.

### CTX-009: InventoryTrackingEvent
**Source Table:** `fact_inventory_tracking` (Eventhouse)
**Key Entity Bindings:** InventoryUnit, Market

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| tracking_id           | String   | Primary key (tracking event identifier)          |
| unit_id               | String   | FK → InventoryUnit entity                        |
| timestamp             | DateTime | Event timestamp                                  |
| event_type            | String   | StatusChange, Hold, Release, Maintenance         |
| market_id             | String   | FK → Market entity                               |
| previous_status       | String   | Previous availability status                     |
| new_status            | String   | New availability status                          |
| reason                | String   | Reason for status change                         |
| doc_time_min          | Float    | Time spent documenting the change                |

**Analytical Value:** Inventory churn documentation overhead, status change frequency per market, hold/release patterns affecting campaign planning time.

### CTX-010: CampaignPacingStream
**Source Table:** `stream_campaign_pacing` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Campaign

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| pacing_id             | String   | Primary key (pacing event identifier)            |
| campaign_id           | String   | FK → Campaign entity                             |
| timestamp             | DateTime | Pacing check timestamp                           |
| impressions_delivered  | Integer | Impressions delivered to date                    |
| impressions_target    | Integer  | Target impressions                               |
| spend_pct             | Float    | Percentage of budget spent                       |
| pacing_status         | String   | On-Track, Under-Pacing, Over-Pacing             |

**Analytical Value:** Real-time campaign performance monitoring, pacing alerts triggering AE intervention and documentation.

### CTX-011: CreativeStatusStream
**Source Table:** `stream_creative_status` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Campaign

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| status_id             | String   | Primary key (status event identifier)            |
| order_id              | String   | FK → CampaignOrderEvent                          |
| campaign_id           | String   | FK → Campaign entity                             |
| timestamp             | DateTime | Status change timestamp                          |
| creative_status       | String   | Pending, InReview, Approved, Rejected, Resend    |
| proof_stage           | String   | Initial, Revision1, Revision2, Final             |
| days_pending          | Integer  | Days in current status                           |
| blocker_type          | String   | ClientFeedback, InternalReview, Production, None |

**Analytical Value:** Creative pipeline bottleneck detection, proof stage aging, blocker type distribution driving AE follow-up burden.

### CTX-012: DigitalImpressionsStream
**Source Table:** `stream_digital_impressions` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Campaign, InventoryUnit

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| impression_id         | String   | Primary key (impression event identifier)        |
| campaign_id           | String   | FK → Campaign entity                             |
| unit_id               | String   | FK → InventoryUnit entity                        |
| timestamp             | DateTime | Impression timestamp                             |
| impressions_count     | Integer  | Number of impressions in this interval           |
| dwell_time_sec        | Float    | Average dwell time (seconds)                     |
| audience_segment      | String   | Audience segment classification                  |

**Analytical Value:** Digital campaign performance verification, dwell time analytics, audience delivery for POP reporting automation.

### CTX-013: InstallationEventStream
**Source Table:** `stream_installation_events` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** InventoryUnit

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| event_id              | String   | Primary key (installation event identifier)      |
| wo_id                 | String   | FK → WorkOrderEvent                              |
| unit_id               | String   | FK → InventoryUnit entity                        |
| timestamp             | DateTime | Event timestamp                                  |
| event_type            | String   | Dispatch, Arrival, InProgress, Complete, Failed   |
| crew_id               | String   | Installation crew identifier                     |
| status                | String   | Current installation status                      |
| photo_uploaded        | String   | Yes/No — photo evidence uploaded                 |
| gps_lat               | Float    | GPS latitude of crew                             |
| gps_lng               | Float    | GPS longitude of crew                            |

**Analytical Value:** Real-time installation tracking, photo compliance for POP automation, GPS verification of crew at correct unit location.

### CTX-014: InventoryAvailabilityStream
**Source Table:** `stream_inventory_availability` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** InventoryUnit, Market

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| avail_id              | String   | Primary key (availability event identifier)      |
| unit_id               | String   | FK → InventoryUnit entity                        |
| market_id             | String   | FK → Market entity                               |
| timestamp             | DateTime | Availability check timestamp                     |
| availability_status   | String   | Available, Booked, OnHold, Maintenance           |
| hold_type             | String   | ClientHold, InternalHold, None                   |
| campaign_id           | String   | FK → Campaign entity (if booked)                 |
| days_available        | Integer  | Consecutive days in current status               |

**Analytical Value:** Real-time inventory availability for AE selling time, hold management documentation, market-level occupancy monitoring.

---

## Batch Fact Contextualizations (Lakehouse — Periodic Aggregates)

### CTX-B01: AEWellnessEvent
**Source Table:** `fact_ae_wellness` (Lakehouse — batch/survey)
**Key Entity Bindings:** AccountExecutive

| Field                 | Type     | Description                                      |
|-----------------------|----------|--------------------------------------------------|
| survey_id             | String   | Primary key (survey identifier)                  |
| ae_id                 | String   | FK → AccountExecutive entity                     |
| date                  | Date     | Survey date                                      |
| admin_burden_score    | Integer  | Self-reported admin burden (1–10)                |
| quota_pressure_score  | Integer  | Quota pressure score (1–10)                      |
| overtime_hours        | Float    | Overtime hours in reporting period               |
| after_hours_doc_min   | Float    | Documentation minutes outside business hours     |
| fatigue_score         | Integer  | Fatigue score (1–10)                             |
| work_life_balance     | Integer  | Work-life balance rating (1–10)                  |

### CTX-B02: ProductionQualityEvent
**Source Table:** `fact_production_quality` (Lakehouse — batch)
**Key Entity Bindings:** AccountExecutive

| Field                   | Type   | Description                                    |
|-------------------------|--------|------------------------------------------------|
| quality_id              | String | Primary key (quality record identifier)        |
| order_id                | String | FK → CampaignOrderEvent                        |
| ae_id                   | String | FK → AccountExecutive entity                   |
| date                    | Date   | Quality assessment date                        |
| charting_accuracy_pct   | Float  | Charting accuracy percentage                   |
| proof_approval_rate     | Float  | First-pass proof approval rate                 |
| install_on_time_pct     | Float  | Installation on-time percentage                |
| pop_completeness_pct    | Float  | POP completeness percentage                    |

### CTX-B03: AdvertiserSatisfactionEvent
**Source Table:** `fact_advertiser_satisfaction` (Lakehouse — batch/survey)
**Key Entity Bindings:** Advertiser, Campaign

| Field                    | Type   | Description                                   |
|--------------------------|--------|-----------------------------------------------|
| survey_id                | String | Primary key (survey identifier)               |
| advertiser_id            | String | FK → Advertiser entity                        |
| campaign_id              | String | FK → Campaign entity                          |
| date                     | Date   | Survey date                                   |
| campaign_accuracy_score  | Float  | Campaign execution accuracy rating            |
| pop_timeliness_score     | Float  | POP report delivery timeliness rating         |
| communication_score      | Float  | AE communication quality rating               |
| renewal_likelihood       | Float  | Likelihood of campaign renewal (0–1)          |

---

## Data Storage Mapping

### Lakehouse (Delta Tables — Dimensional/Static Data)

| Delta Table Name            | Source CSV                         | Entity / Mapping             |
|-----------------------------|------------------------------------|------------------------------|
| dim_account_executives      | dim_account_executives.csv         | AccountExecutive entity      |
| dim_campaigns               | dim_campaigns.csv                  | Campaign entity              |
| dim_inventory_units         | dim_inventory_units.csv            | InventoryUnit entity         |
| dim_markets                 | dim_markets.csv                    | Market entity                |
| dim_advertisers             | dim_advertisers.csv                | Advertiser entity            |
| dim_vendors                 | dim_vendors.csv                    | Vendor entity                |
| fact_ae_wellness            | fact_ae_wellness.csv               | CTX-B01 (batch)              |
| fact_production_quality     | fact_production_quality.csv        | CTX-B02 (batch)              |
| fact_advertiser_satisfaction| fact_advertiser_satisfaction.csv    | CTX-B03 (batch)              |

### Eventhouse (KQL Tables — Event/Streaming Data)

| KQL Table Name              | Source CSV                         | Contextualization |
|-----------------------------|------------------------------------|-------------------|
| campaign_orders             | fact_campaign_orders.csv           | CTX-001           |
| oms_interactions            | fact_oms_interactions.csv          | CTX-002           |
| charting_events             | fact_charting_events.csv           | CTX-003           |
| pop_reports                 | fact_pop_reports.csv               | CTX-004           |
| contract_changes            | fact_contract_changes.csv          | CTX-005           |
| work_orders                 | fact_work_orders.csv               | CTX-006           |
| proof_approvals             | fact_proof_approvals.csv           | CTX-007           |
| pop_alerts                  | fact_pop_alerts.csv                | CTX-008           |
| inventory_tracking          | fact_inventory_tracking.csv        | CTX-009           |
| campaign_pacing             | stream_campaign_pacing.csv         | CTX-010           |
| creative_status             | stream_creative_status.csv         | CTX-011           |
| digital_impressions         | stream_digital_impressions.csv     | CTX-012           |
| installation_events         | stream_installation_events.csv     | CTX-013           |
| inventory_availability      | stream_inventory_availability.csv  | CTX-014           |

---

## Ontology Visualization

```
                          ┌──────────────┐
                          │  Advertiser  │
                          └──────┬───────┘
                                 │ placed_by
                                 ▼
┌────────────────┐ manages  ┌──────────┐  belongs_to  ┌──────────┐
│ Account        │─────────▶│ Campaign │─────────────▶│  Market  │
│ Executive      │          └────┬─────┘              └─────▲────┘
└────────────────┘               │                          │
                                 │ fulfilled_by        located_in
                                 ▼                          │
                          ┌──────────┐              ┌───────┴──────┐
                          │  Vendor  │              │ Inventory    │
                          └──────────┘              │    Unit      │
                                                    └──────────────┘

         ── Event Fact Contextualizations (Eventhouse) ──

┌────────────┐┌───────────┐┌───────────┐┌───────────┐┌───────────┐
│ Campaign   ││   OMS     ││ Charting  ││   POP     ││ Contract  │
│  Orders    ││Interaction││  Events   ││  Reports  ││  Changes  │
│ (CTX-001)  ││ (CTX-002) ││ (CTX-003) ││ (CTX-004) ││ (CTX-005) │
└────────────┘└───────────┘└───────────┘└───────────┘└───────────┘
┌────────────┐┌───────────┐┌───────────┐┌───────────┐
│   Work     ││  Proof    ││   POP     ││ Inventory │
│  Orders    ││ Approvals ││  Alerts   ││ Tracking  │
│ (CTX-006)  ││ (CTX-007) ││ (CTX-008) ││ (CTX-009) │
└────────────┘└───────────┘└───────────┘└───────────┘

         ── Real-Time Streaming Layer ──

┌────────────┐┌───────────┐┌───────────┐┌───────────┐┌───────────┐
│ Campaign   ││ Creative  ││ Digital   ││Installation││ Inventory │
│  Pacing    ││  Status   ││Impressions││  Events   ││Availability│
│ (CTX-010)  ││ (CTX-011) ││ (CTX-012) ││ (CTX-013) ││ (CTX-014) │
└────────────┘└───────────┘└───────────┘└───────────┘└───────────┘
```

---

## Key Analytical Queries Enabled by This Ontology

### 1. POP Documentation Burden per AE
```kql
pop_reports
| where date between (datetime(2026-01-01) .. datetime(2026-03-23))
| summarize total_pop_doc_min = sum(doc_time_min),
            reports_filed = count(),
            avg_compliance = avg(compliance_pct),
            total_photos_gap = sum(photos_required - photos_submitted)
  by ae_id
| order by total_pop_doc_min desc
```

### 2. Proof Cycle Time & Revision Overhead
```kql
proof_approvals
| summarize avg_cycle_hours = avg(cycle_time_hours),
            total_revisions = sum(revision_count),
            rejection_rate = countif(status == "Rejected") * 1.0 / count()
  by ae_id, proof_type
| order by avg_cycle_hours desc
```

### 3. Charting Accuracy — Manual vs. Automated
```kql
charting_events
| summarize total_manual = sum(manual_charts),
            total_auto = sum(auto_charts),
            manual_pct = round(sum(manual_charts) * 100.0 / sum(units_charted), 1),
            ccn_driven = countif(ccn_flag == "Yes"),
            total_chart_doc_min = sum(doc_time_min)
  by campaign_id
| order by total_chart_doc_min desc
```

### 4. Campaign Order Documentation Load
```kql
campaign_orders
| summarize orders_count = count(),
            total_units = sum(units_booked),
            total_doc_min = sum(doc_time_min),
            avg_proof_cycles = avg(proof_cycles)
  by ae_id, order_type
| order by total_doc_min desc
```

### 5. Inventory Tracking Documentation Overhead
```kql
inventory_tracking
| summarize status_changes = count(),
            total_doc_min = sum(doc_time_min),
            avg_doc_per_change = round(avg(doc_time_min), 1)
  by market_id, event_type
| order by total_doc_min desc
```
