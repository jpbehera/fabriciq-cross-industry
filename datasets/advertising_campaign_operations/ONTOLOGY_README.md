# Advertising Campaign Operations — Ontology Guide

## Overview

The **AdvertisingDocBurdenOntology** models the Out-of-Home (OOH) advertising industry, focusing on **documentation burden on Account Executives (AEs)** — quantifying time spent on campaign orders, proof-of-performance reports, charting, contract changes, and work orders vs. actual selling activities.

```
                    ┌──────────────┐
                    │   Market     │
                    │  (10 rows)   │
                    └──────┬───────┘
                           │ located_in
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  Account    │ │  Inventory  │ │  Campaign   │
    │  Executive  │ │  Unit       │ │  (40 rows)  │
    │  (25 rows)  │ │  (60 rows)  │ └──────┬──────┘
    └──────┬──────┘ └─────────────┘        │
           │ manages                       │ placed_by
           │                        ┌──────▼──────┐
           │                        │ Advertiser  │
           │                        │  (30 rows)  │
           │                        └─────────────┘
           │
    ┌──────▼──────────────────────────────┐
    │     Fact / Event Tables             │
    │  (Campaign Orders, OMS, Charting,   │
    │   POP Reports, Contract Changes,    │
    │   Work Orders, Wellness, etc.)      │
    └─────────────────────────────────────┘
           │
    ┌──────▼──────┐
    │   Vendor    │
    │  (15 rows)  │
    └─────────────┘
```

---

## Entity Types (6 Dimension Tables → Warehouse)

Each entity type maps to a `dim_*` table in the Fabric Warehouse (`Advertising_Datawarehouse.dbo`).

| Entity Type | Source Table | Key Column | Display Column | Columns | Description |
|---|---|---|---|---|---|
| **AccountExecutive** | `dim_account_executives` | `ae_id` | `name` | 9 | AEs who manage campaigns and do documentation |
| **Advertiser** | `dim_advertisers` | `advertiser_id` | `name` | 8 | Companies that buy advertising space |
| **Campaign** | `dim_campaigns` | `campaign_id` | `name` | 10 | OOH advertising campaigns |
| **InventoryUnit** | `dim_inventory_units` | `unit_id` | `name` | 12 | Physical OOH ad units (billboards, posters, digital) |
| **Market** | `dim_markets` | `market_id` | `name` | 8 | Geographic markets (Atlanta, Chicago, etc.) |
| **Vendor** | `dim_vendors` | `vendor_id` | `name` | 7 | Production, installation, creative vendors |

### Data Binding: NonTimeSeries → Warehouse
Each entity type has a **NonTimeSeries** data binding that maps every column in the dimension table to an ontology property. The binding uses:
- **Source Type:** `LakehouseTable`
- **Item ID:** Warehouse artifact ID
- **Schema:** `dbo`

---

## Relationships (Auto-Detected from Star Schema)

Relationships are inferred from FK columns shared between fact tables and dimension tables. When a fact table contains FK columns linking two different dimension tables, those entities are related.

| Relationship | Source Entity | Target Entity | Discovered Via |
|---|---|---|---|
| `AccountExecutiveToAdvertiser` | AccountExecutive | Advertiser | Fact tables linking `ae_id` + `advertiser_id` |
| `AccountExecutiveToCampaign` | AccountExecutive | Campaign | `fact_campaign_orders` (`ae_id`, `campaign_id`) |
| `AccountExecutiveToMarket` | AccountExecutive | Market | Fact tables linking `ae_id` + `market_id` |
| `AdvertiserToCampaign` | Advertiser | Campaign | `fact_campaign_orders` (`advertiser_id`, `campaign_id`) via dim FKs |
| `CampaignToMarket` | Campaign | Market | `fact_campaign_orders` (`campaign_id`, `market_id`) |
| `CampaignToVendor` | Campaign | Vendor | `fact_work_orders` (`campaign_id`, `vendor_id`) |
| `MarketToVendor` | Market | Vendor | `fact_work_orders` (`market_id`, `vendor_id`) |

### Relationship Data Bindings
Each relationship has a data binding that specifies:
- **Binding Table:** The fact table that contains both FK columns
- **Source Key Column:** FK column for the source entity
- **Target Key Column:** FK column for the target entity

---

## Fact Tables (17 — Batch + Event + Streaming)

### Batch Fact Tables → Warehouse (Lakehouse Delta)

| Table | Rows | Key Metrics | FKs |
|---|---|---|---|
| `fact_advertiser_satisfaction` | 30 | Satisfaction scores, NPS | `advertiser_id` |
| `fact_ae_wellness` | 25 | Burnout, stress, overtime | `ae_id` |
| `fact_campaign_orders` | 200 | Order volume, doc time, proof cycles | `campaign_id`, `ae_id` |
| `fact_inventory_tracking` | 80 | Unit status, availability | `unit_id`, `market_id` |
| `fact_pop_reports` | 60 | POP compliance, doc time | `campaign_id`, `ae_id` |
| `fact_production_quality` | 40 | Quality scores, defects | `vendor_id`, `campaign_id` |
| `fact_work_orders` | 120 | Work order volume, turnaround | `campaign_id`, `vendor_id` |

### Event Fact Tables → Eventhouse (KQL)

| Table | Rows | Timestamp | Key Metrics |
|---|---|---|---|
| `fact_charting_events` | 150 | `date` | Manual vs auto charting, doc time |
| `fact_contract_changes` | 80 | `timestamp` | CCN impact, revenue changes |
| `fact_oms_interactions` | 400 | `timestamp` | OMS system usage, duration |
| `fact_pop_alerts` | 60 | `timestamp` | Alert type, severity |
| `fact_proof_approvals` | 80 | `timestamp` | Approval cycles, delays |

### Streaming Tables → Eventhouse (KQL)

| Table | Rows | Timestamp | Real-Time Metrics |
|---|---|---|---|
| `stream_campaign_pacing` | 80 | `timestamp` | Impression delivery vs target |
| `stream_creative_status` | 80 | `timestamp` | Creative approval pipeline |
| `stream_digital_impressions` | 80 | `timestamp` | Digital unit impression counts |
| `stream_installation_events` | 80 | `timestamp` | Field installation progress |
| `stream_inventory_availability` | 80 | `timestamp` | Real-time unit availability |

---

## Fabric Artifacts

| Artifact | Name | Type |
|---|---|---|
| Lakehouse | `Advertising_Data_Bronze` | Delta tables (CSVs → Spark) |
| Warehouse | `Advertising_Datawarehouse` | SQL tables (pyodbc) |
| Eventhouse | `advertising_rt_store` | KQL tables (REST API) |
| KQL Database | `advertising_rt_store` | Same name as Eventhouse |
| Eventstream | `advertising_events` | Custom Endpoint → KQL |
| Semantic Model | `Advertising_DocBurden_Model` | DirectQuery → Warehouse |
| Ontology | `AdvertisingDocBurdenOntology` | Fabric IQ ontology |

---

## Documentation Burden Metrics

The ontology enables analysis of these key documentation burden KPIs:

| Metric | Source | Formula |
|---|---|---|
| **Avg Doc Time per Order** | `fact_campaign_orders` | `AVG(doc_time_min)` |
| **Proof Cycle Overhead** | `fact_campaign_orders` | `AVG(proof_cycles)` per order |
| **Manual Charting Ratio** | `fact_charting_events` | `SUM(manual_charts) / SUM(units_charted)` |
| **OMS Time per AE** | `fact_oms_interactions` | `SUM(duration_ms) / 1000 / 60` per AE |
| **CCN Recharting Rate** | `fact_charting_events` | `COUNT(ccn_flag='Yes') / COUNT(*)` |
| **AE Burnout Risk** | `fact_ae_wellness` | Composite of stress, overtime, satisfaction |
| **POP Compliance Rate** | `fact_pop_reports` | `AVG(compliance_pct)` |
| **Vendor Quality Score** | `fact_production_quality` | `AVG(quality_rating)` by vendor |

---

## How the Ontology Was Created

The ontology is created programmatically via the **Fabric REST API** (same approach as the Healthcare Nursing use case):

1. **Parse CSV schemas** — reads all `dim_*`, `fact_*`, `stream_*` tables from the Lakehouse
2. **Build Entity Types** — maps `dim_*` tables to ontology entities with properties
3. **Auto-detect Relationships** — finds FK columns shared between fact tables to infer entity-entity relationships
4. **Discover KQL Tables** — queries Eventhouse to find TimeSeries data sources
5. **Two-phase REST API creation:**
   - Phase 1: Create ontology structure (entity types + relationship types)
   - Phase 2: Update with data bindings (NonTimeSeries + TimeSeries + Relationship)

No `.iq` package file or `fabriciq_ontology_accelerator` wheel is required.
