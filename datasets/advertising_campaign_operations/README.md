# Advertising (OOH) Campaign Operations — Sample Dataset

> **Disclaimer:** All data in this directory is **entirely fictional and synthetic**. Names, email addresses, phone numbers, and company references do not represent real individuals or organizations. Phone numbers use the `555-0xxx` reserved range. Email addresses use `.example` domains per [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606). Any resemblance to real persons or entities is coincidental.



## Overview

This dataset models **Advertising (OOH) Campaign Operations Documentation Burden** — the
administrative overhead that account executives, chartists, production specialists, and
POP coordinators face managing campaign orders, contract charting, creative proofing,
work order scheduling, and proof of performance reporting across multiple active campaigns
and markets.

**Industry Context:** OOH advertising AEs and campaign operations staff spend 35–55% of
their time on campaign documentation. With average AE salaries of $120K–$180K, this
represents $48K–$72K per person per year in administrative burden.

## Dataset Statistics

| Category | Tables | Total Rows |
|----------|--------|------------|
| Dimensions | 6 | 180 |
| Batch Facts | 6 | 675 |
| Event Facts | 6 | 840 |
| Streaming | 5 | 400 |
| **Total** | **23** | **2,095** |

## Table Inventory

### Dimensions (6 tables → Lakehouse + Warehouse)

| Table | Rows | Description |
|-------|------|-------------|
| `dim_account_executives` | 25 | AEs, coordinators, chartists, production specialists, POP coordinators |
| `dim_campaigns` | 40 | Active/pending campaigns across billboard, digital, transit, street furniture |
| `dim_inventory_units` | 60 | Physical ad units (billboards, digital displays, transit shelters) across 6 markets |
| `dim_markets` | 10 | DMA markets (6 active with inventory + 4 expansion) |
| `dim_advertisers` | 30 | Client advertisers across 30 industries with agency associations |
| `dim_vendors` | 15 | Print, digital, transit, installation, and photography vendors |

### Batch Facts (6 tables → Lakehouse + Warehouse)

| Table | Rows | Description |
|-------|------|-------------|
| `fact_campaign_orders` | 200 | Campaign order processing with doc time, proof cycles, vendor assignments |
| `fact_charting_events` | 150 | Contract-to-inventory charting (manual vs auto, CCN recharting burden) |
| `fact_pop_reports` | 120 | Proof of Performance reports with photo compliance and verification time |
| `fact_ae_wellness` | 25 | Burnout/wellness metrics per AE — admin burden, quota pressure, fatigue |
| `fact_production_quality` | 150 | Charting accuracy, proof approval rates, install on-time, POP completeness |
| `fact_advertiser_satisfaction` | 30 | Client satisfaction scores — campaign accuracy, POP timeliness, renewal likelihood |

### Event Facts (6 tables → Eventhouse + Warehouse)

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `fact_oms_interactions` | 400 | `oms_interactions` | System interactions (Boostr, OMS, IMS, Workforce, Salesforce) |
| `fact_contract_changes` | 80 | `contract_changes` | CCN (Contract Change Notification) processing and revenue impact |
| `fact_proof_approvals` | 100 | `proof_approvals` | Creative proof approval cycles with reviewer and revision tracking |
| `fact_work_orders` | 120 | `work_orders` | Installation work orders with posting instructions and vendor dispatch |
| `fact_pop_alerts` | 60 | `pop_alerts` | POP compliance alerts (missing photos, wrong creative, damaged units) |
| `fact_inventory_tracking` | 80 | `inventory_tracking` | Unit status changes (onboarding, offboarding, holds, maintenance) |

### Streaming (5 tables → Eventhouse)

| Table | Rows | KQL Name | Description |
|-------|------|----------|-------------|
| `stream_campaign_pacing` | 80 | `campaign_pacing` | Digital campaign delivery pacing and under/over-delivery alerts |
| `stream_creative_status` | 80 | `creative_status` | Creative proof workflow status and blocker tracking |
| `stream_installation_events` | 80 | `installation_events` | Field installation progress with crew dispatch and GPS |
| `stream_digital_impressions` | 80 | `digital_impressions` | Real-time digital OOH impression counts by audience segment |
| `stream_inventory_availability` | 80 | `inventory_availability` | Inventory occupancy changes, hold conflicts, availability windows |

## Key Data Stories

### 1. Documentation Burden Hotspots
- **AE-001 (Marcus Webb)**: Senior AE with 22 active campaigns, $2.8M quota — highest campaign doc times (55–135 min), admin burden 9.2/10, fatigue 8.8
- **AE-010 (Maria Gonzalez)**: 23 active campaigns, $2.7M quota — POP completeness issues (68–85%), admin burden 9.5/10, fatigue 9.2 — **critical burnout risk**
- **AE-016 (Nicole Davis)**: Chartist with highest manual charting burden (35–90 min doc time), overwhelmed by CCN recharting

### 2. Charting & CCN Cascade
- ~25% of charting events are CCN recharting, requiring release + rechart + schedule adjustment
- Manual charting dominates non-initial charting events — automation gap for grouped inventory
- Charting conflicts correlate with high-occupancy markets (MKT-001 New York, MKT-003 Los Angeles)

### 3. POP & Photography Burden
- AE-022/AE-023 (POP Coordinators): Dedicated to proof of performance photography and verification
- Average POP report requires verification of 2–14 units with 1–3 photos each
- Missing photo alerts (~8% of POP alerts) create re-shoot cascades

### 4. Production & Proof Approval Cycles
- Proof cycles average 1–5 rounds; orders exceeding 3 rounds correlate with digital and transit media
- Creative status stream shows blocking types: client_review, art_revision, spec_mismatch dominant
- AE-001 and AE-010 show lower proof approval rates due to volume overload

### 5. System Usage Patterns
- OMS interaction data spans 5 systems: Boostr (proposals/pipeline), OMS (orders/scheduling), IMS (inventory), Workforce (installations), Salesforce (leads/accounts)
- AE-001/AE-010 spend 2–3x more time in systems than average AEs
- Chartists (AE-016 to AE-019) concentrated in OMS charting module

## Usage

### With Generic Notebooks
1. Upload `data/` folder to your Fabric Lakehouse Files area under `advertising_campaign_operations/data/`
2. Import `Advertising_Config.ipynb` to your Fabric workspace
3. Run notebooks 01–07 using `%run ./Advertising_Config` for configuration

### File Naming Convention
- `dim_*` — Dimension tables (loaded to Lakehouse Delta + Warehouse SQL)
- `fact_*` — Fact tables (batch → Lakehouse + Warehouse; event → Eventhouse + Warehouse)
- `stream_*` — Streaming tables (loaded to Eventhouse KQL only)

## Foreign Key Relationships

```
dim_account_executives.ae_id → fact_campaign_orders, fact_charting_events (as chartist_id),
                                fact_pop_reports, fact_ae_wellness,
                                fact_production_quality, fact_oms_interactions,
                                fact_contract_changes, fact_proof_approvals

dim_campaigns.campaign_id    → fact_campaign_orders, fact_charting_events,
                                fact_pop_reports, fact_contract_changes,
                                fact_work_orders, fact_pop_alerts,
                                stream_campaign_pacing, stream_creative_status,
                                stream_digital_impressions

dim_inventory_units.unit_id  → fact_work_orders, fact_pop_alerts,
                                fact_inventory_tracking,
                                stream_installation_events,
                                stream_digital_impressions,
                                stream_inventory_availability

dim_markets.market_id        → dim_account_executives, dim_campaigns,
                                dim_inventory_units, fact_inventory_tracking,
                                stream_inventory_availability

dim_advertisers.advertiser_id → dim_campaigns, fact_advertiser_satisfaction

dim_vendors.vendor_id        → fact_campaign_orders, fact_work_orders
```
