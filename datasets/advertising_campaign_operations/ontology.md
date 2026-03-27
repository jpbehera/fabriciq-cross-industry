# Advertising Campaign Operations — Ontology

## Overview

This document defines the **AdvertisingDocBurdenOntology** for the Advertising Campaign Operations use case. It maps the Out-of-Home (OOH) advertising data model to Fabric IQ entity types, relationship types, contextualizations (events), and data bindings across **Lakehouse**, **Warehouse**, and **Eventhouse**.

The core analytical focus is **documentation burden on Account Executives (AEs)** — quantifying time spent on campaign orders, proof-of-performance (POP) reports, charting, contract change notices (CCNs), and work orders vs. actual selling activities.

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
```

---

## Fabric Artifacts

| Artifact | Name | Type |
|---|---|---|
| Lakehouse | `Advertising_Data_Bronze` | Delta tables (CSVs → Spark) |
| Warehouse | `Advertising_Datawarehouse` | SQL tables (pyodbc, schema `dbo`) |
| Eventhouse | `advertising_rt_store` | KQL tables (REST API) |
| KQL Database | `advertising_rt_store` | Same name as Eventhouse |
| Eventstream | `advertising_events` | Custom Endpoint → KQL |
| Semantic Model | `Advertising_DocBurden_Model` | DirectQuery → Warehouse |
| Ontology | `AdvertisingDocBurdenOntology` | Fabric IQ ontology |

---

## Entity Types (6 Dimension Tables)

Each entity type maps to a `dim_*` table in the Warehouse (`dbo` schema) with a **NonTimeSeries** data binding.

### 1. AccountExecutive
**Source Table:** `dim_account_executives` | **Key:** `ae_id` | **Display:** `name`

| Property | Type | Description |
|---|---|---|
| ae_id | String | Primary key |
| name | String | Full name |
| role | String | AE, Senior AE, Sales Manager |
| market_id | String | FK → Market |
| team | String | Sales team |
| quota_target | Float | Annual revenue quota |
| hire_date | Date | Date of hire |
| specialization | String | Digital, Traditional, Hybrid |
| active_campaigns | Integer | Currently active campaigns |

### 2. Campaign
**Source Table:** `dim_campaigns` | **Key:** `campaign_id` | **Display:** `name`

| Property | Type | Description |
|---|---|---|
| campaign_id | String | Primary key |
| name | String | Campaign name |
| advertiser_id | String | FK → Advertiser |
| market_id | String | FK → Market |
| start_date | Date | Start date |
| end_date | Date | End date |
| budget | Float | Total budget |
| media_type | String | Bulletin, Poster, Digital, Transit |
| contract_value | Float | Signed contract value |
| status | String | Active, Completed, Pending, Cancelled |

### 3. InventoryUnit
**Source Table:** `dim_inventory_units` | **Key:** `unit_id` | **Display:** `name`

| Property | Type | Description |
|---|---|---|
| unit_id | String | Primary key |
| name | String | Location label |
| type | String | Bulletin, Poster, Digital, Transit |
| market_id | String | FK → Market |
| address | String | Physical address |
| lat | Float | Latitude |
| lng | Float | Longitude |
| faces | Integer | Number of advertising faces |
| illuminated | String | Yes/No |
| digital | String | Yes/No |
| size | String | Dimensions (e.g., 14x48) |
| monthly_rate | Float | Standard monthly rate |

### 4. Market
**Source Table:** `dim_markets` | **Key:** `market_id` | **Display:** `name`

| Property | Type | Description |
|---|---|---|
| market_id | String | Primary key |
| name | String | Market name (Atlanta, Chicago, etc.) |
| region | String | Geographic region |
| dma_rank | Integer | DMA ranking |
| population | Integer | Market population |
| total_units | Integer | Total OOH units |
| digital_pct | Float | Percentage digital units |
| avg_occupancy_rate | Float | Average occupancy rate |

### 5. Advertiser
**Source Table:** `dim_advertisers` | **Key:** `advertiser_id` | **Display:** `name`

| Property | Type | Description |
|---|---|---|
| advertiser_id | String | Primary key |
| name | String | Company name |
| industry | String | Industry vertical |
| annual_spend | Float | Annual OOH spend |
| campaigns_ytd | Integer | Campaigns year-to-date |
| tenure_years | Integer | Years as client |
| agency_name | String | Media agency |
| contact | String | Primary contact |

### 6. Vendor
**Source Table:** `dim_vendors` | **Key:** `vendor_id` | **Display:** `name`

| Property | Type | Description |
|---|---|---|
| vendor_id | String | Primary key |
| name | String | Vendor company name |
| type | String | Production, Installation, Creative |
| region | String | Service region |
| specialization | String | Vinyl, Digital, Transit, Wallscape |
| avg_turnaround_days | Float | Average turnaround |
| quality_rating | Float | Quality score (1.0–5.0) |

---

## Relationship Types

| Relationship | Source → Target | Cardinality | Description | Binding Table |
|---|---|---|---|---|
| `manages_campaign` | AccountExecutive → Campaign | 1:Many | AE manages campaigns | `fact_campaign_orders` |
| `belongs_to_market` | Campaign → Market | Many:1 | Campaign runs in a market | `dim_campaigns` |
| `placed_by` | Campaign → Advertiser | Many:1 | Campaign placed by advertiser | `dim_campaigns` |
| `located_in` | InventoryUnit → Market | Many:1 | Unit located in a market | `dim_inventory_units` |
| `fulfilled_by` | Campaign → Vendor | Many:Many | Campaign fulfilled by vendors | `fact_work_orders` |

**Auto-detected relationships** (from star schema FK analysis):

| Relationship | Source → Target | Discovered Via |
|---|---|---|
| `AccountExecutiveToAdvertiser` | AccountExecutive → Advertiser | Fact tables linking `ae_id` + `advertiser_id` |
| `AccountExecutiveToMarket` | AccountExecutive → Market | Fact tables linking `ae_id` + `market_id` |
| `CampaignToVendor` | Campaign → Vendor | `fact_work_orders` (`campaign_id`, `vendor_id`) |
| `MarketToVendor` | Market → Vendor | `fact_work_orders` (`market_id`, `vendor_id`) |

---

## Contextualizations (Event Fact Tables → Eventhouse)

### Event Facts (9 tables)

| # | Contextualization | Source Table | Timestamp | Entity Bindings | Key Metrics |
|---|---|---|---|---|---|
| CTX-001 | CampaignOrderEvent | `campaign_orders` | `date` | Campaign, AE, Vendor | `doc_time_min`, `proof_cycles`, `units_booked` |
| CTX-002 | OMSInteractionEvent | `oms_interactions` | `timestamp` | AE, Campaign | `duration_ms`, `action`, `module` |
| CTX-003 | ChartingEvent | `charting_events` | `date` | Campaign | `manual_charts`, `auto_charts`, `doc_time_min`, `ccn_flag` |
| CTX-004 | POPReportEvent | `pop_reports` | `date` | Campaign, AE | `compliance_pct`, `doc_time_min`, `photos_submitted` |
| CTX-005 | ContractChangeEvent | `contract_changes` | `timestamp` | Campaign, AE | `change_type`, `revenue_impact`, `doc_time_min` |
| CTX-006 | WorkOrderEvent | `work_orders` | `timestamp` | Campaign, Unit, Vendor | `wo_type`, `install_status`, `doc_time_min` |
| CTX-007 | ProofApprovalEvent | `proof_approvals` | `timestamp` | AE | `cycle_time_hours`, `revision_count`, `status` |
| CTX-008 | POPAlertEvent | `pop_alerts` | `timestamp` | Campaign, Unit | `alert_type`, `severity`, `photos_missing` |
| CTX-009 | InventoryTrackingEvent | `inventory_tracking` | `timestamp` | Unit, Market | `event_type`, `doc_time_min` |

### Real-Time Streams (5 tables)

| # | Contextualization | Source Table | Timestamp | Entity Bindings | Key Metrics |
|---|---|---|---|---|---|
| CTX-010 | CampaignPacingStream | `campaign_pacing` | `timestamp` | Campaign | `impressions_delivered`, `pacing_status` |
| CTX-011 | CreativeStatusStream | `creative_status` | `timestamp` | Campaign | `creative_status`, `days_pending`, `blocker_type` |
| CTX-012 | DigitalImpressionsStream | `digital_impressions` | `timestamp` | Campaign, Unit | `impressions_count`, `dwell_time_sec` |
| CTX-013 | InstallationEventStream | `installation_events` | `timestamp` | Unit | `event_type`, `status`, `photo_uploaded` |
| CTX-014 | InventoryAvailabilityStream | `inventory_availability` | `timestamp` | Unit, Market, Campaign | `availability_status`, `days_available` |

### Batch Facts (3 tables → Lakehouse)

| # | Contextualization | Source Table | Entity Bindings | Key Metrics |
|---|---|---|---|---|
| CTX-B01 | AEWellnessEvent | `fact_ae_wellness` | AE | `admin_burden_score`, `overtime_hours`, `fatigue_score` |
| CTX-B02 | ProductionQualityEvent | `fact_production_quality` | AE | `charting_accuracy_pct`, `proof_approval_rate` |
| CTX-B03 | AdvertiserSatisfactionEvent | `fact_advertiser_satisfaction` | Advertiser, Campaign | `communication_score`, `renewal_likelihood` |

---

## Data Storage Summary

| Binding Target | Tables | Store | Source Type |
|---|---|---|---|
| Entity dimensions | 6 | Warehouse | `LakehouseTable` (dbo schema) |
| Batch facts | 3 | Lakehouse | Delta tables |
| Event facts | 9 | Eventhouse | KQL tables |
| Real-time streams | 5 | Eventhouse | KQL tables |
| **Total** | **23** | | |

---

## Documentation Burden Patterns

### Pattern 1: AE Overload Detection
AEs with `active_campaigns > 8` AND `doc_time_min > 60/day` across campaign orders + POP reports + contract changes. Identifies AEs spending more time on paperwork than selling.

### Pattern 2: POP Documentation Cascade
A single contract change (CCN) triggers recharting (`ccn_flag=Yes`) → re-verification (POP) → new POP alerts. Sum `doc_time_min` across all stages within 72 hours to quantify ripple effect.

### Pattern 3: Proof Cycle Delays
Proof approvals with `cycle_time_hours > 48` AND `revision_count >= 3` correlating with creative status blockers. Often the single largest hidden documentation cost.

### Pattern 4: Contract Change Burden
Unit-swap changes require recharting + new work orders + updated POP + new proofs — 3× more documention per unit than date changes.

### Pattern 5: Digital vs. Traditional Doc Time
Digital campaigns require less installation documentation but more pacing/impression reporting. Quantifies the trade-off as operators shift to digital inventory.

---

## KQL Query Examples

```kql
// POP documentation burden per AE
pop_reports
| summarize total_doc_min = sum(doc_time_min), reports = count(),
            avg_compliance = avg(compliance_pct)
  by ae_id
| order by total_doc_min desc

// Proof cycle time & revision overhead
proof_approvals
| summarize avg_cycle_hrs = avg(cycle_time_hours),
            revisions = sum(revision_count),
            reject_rate = countif(status == "Rejected") * 1.0 / count()
  by ae_id, proof_type

// Manual vs automated charting ratio
charting_events
| summarize manual_pct = round(sum(manual_charts) * 100.0 / sum(units_charted), 1),
            ccn_driven = countif(ccn_flag == "Yes"),
            total_doc_min = sum(doc_time_min)
  by campaign_id
| order by total_doc_min desc
```

---

## How the Ontology Was Created

The ontology is created programmatically by notebook `05_Create_Ontology.ipynb` via the **Fabric REST API**:

1. **Parse CSV schemas** from the Lakehouse (`dim_*`, `fact_*`, `stream_*` tables)
2. **Build Entity Types** with properties from dimension table columns
3. **Auto-detect Relationships** from FK columns shared across fact tables
4. **Discover KQL Tables** from Eventhouse for TimeSeries bindings
5. **Two-phase REST API creation:**
   - Phase 1: `POST /ontologies` with structure (entity types + relationship types)
   - Phase 2: `POST /ontologies/{id}/updateDefinition` with all data bindings

No `.iq` package or external tools required — same approach as the Healthcare Nursing use case.
