# Oil & Gas Field Operations — Ontology Design

## Overview

**Ontology Name:** `OilGasFieldOpsOntology`

This ontology models the documentation burden experienced by field engineers
working across well sites, production facilities, and regulatory environments
in the oil & gas upstream sector. It captures the relationship between
operational activities — daily drilling reports (DDRs), HSE inspections,
permit-to-work (PTW) paperwork, well integrity testing, and tour handoffs —
and the time field engineers spend documenting those activities instead of
performing actual field operations, monitoring, and decision-making.

The ontology connects **6 entity types**, **5 relationship types**, and
**13 contextualizations** (event facts + stream tables) to provide a
comprehensive view of documentation overhead in field operations.

| Metric               | Count |
|----------------------|-------|
| Entity Types         | 6     |
| Relationship Types   | 5     |
| Contextualizations   | 13    |
| Dim Tables           | 6     |
| Fact Tables (Event)  | 8     |
| Fact Tables (Batch)  | 4     |
| Stream Tables        | 5     |

---

## Concept Mapping

| RDF / OWL Concept       | Fabric IQ Equivalent       | Description                                      |
|--------------------------|----------------------------|--------------------------------------------------|
| `owl:Class`              | Entity Type                | Field engineers, well sites, facilities, etc.     |
| `owl:ObjectProperty`     | Relationship Type          | operates, stationed_at, hosts, regulated_by, etc. |
| `owl:DatatypeProperty`   | Entity Property            | Columns from dim tables (name, certifications…)   |
| `rdf:type`               | Entity Instance            | Rows in dim tables                                |
| `owl:NamedIndividual`    | Contextualization          | Fact/stream bindings to entity pairs              |
| `rdfs:label`             | Display Name               | Human-readable labels in the UI                   |
| `rdfs:comment`           | Description                | Tooltip / metadata descriptions                   |
| `owl:Restriction`        | Relationship Cardinality   | One-to-many, many-to-many constraints             |
| `skos:Concept`           | Tag / Category             | Grouping and classification of entities           |

---

## Entity Types

### ENT-001: FieldEngineer

Represents a field engineer working rotational shifts across well sites and
production facilities, responsible for drilling, completions, production, or
HSE operations.

**Source Table:** `dim_field_engineers`

| Property            | Type     | Description                                |
|---------------------|----------|--------------------------------------------|
| `engineer_id`       | string   | Primary key — unique engineer identifier   |
| `name`              | string   | Full name of the field engineer            |
| `role`              | string   | Job role (drilling engineer, production…)  |
| `certifications`    | string   | Active certifications (IWCF, SafeGulf…)   |
| `rotation_schedule` | string   | Rotation pattern (14/14, 28/28, etc.)      |
| `base`              | string   | Home base or office location               |
| `years_experience`  | integer  | Total years of field experience            |

### ENT-002: WellSite

Represents an individual well or well pad, including its basin location,
operator, and current production status.

**Source Table:** `dim_well_sites`

| Property         | Type     | Description                                   |
|------------------|----------|-----------------------------------------------|
| `well_id`        | string   | Primary key — unique well identifier          |
| `name`           | string   | Well name or pad designation                  |
| `basin`          | string   | Geological basin (Permian, Eagle Ford…)       |
| `field`          | string   | Production field name                         |
| `operator`       | string   | Operating company                             |
| `spud_date`      | date     | Date drilling commenced                       |
| `status`         | string   | Current status (drilling, producing, SI…)     |
| `depth_ft`       | integer  | Total measured depth in feet                  |
| `production_bpd` | float    | Current production rate in barrels per day    |

### ENT-003: Facility

Represents a surface facility — gathering station, compressor station,
processing plant, tank battery, or field camp.

**Source Table:** `dim_facilities`

| Property                  | Type     | Description                              |
|---------------------------|----------|------------------------------------------|
| `facility_id`             | string   | Primary key — unique facility identifier |
| `name`                    | string   | Facility name                            |
| `type`                    | string   | Facility type (compressor, gathering…)   |
| `location`                | string   | Geographic location or GPS coordinates   |
| `capacity`                | string   | Throughput or storage capacity            |
| `operator`                | string   | Operating company                        |
| `regulatory_jurisdiction` | string   | Governing regulatory body jurisdiction   |

### ENT-004: ReportType

Represents a category of documentation or report that field engineers must
complete as part of operational or regulatory requirements.

**Source Table:** `dim_report_types`

| Property             | Type     | Description                                 |
|----------------------|----------|---------------------------------------------|
| `report_type_id`     | string   | Primary key — unique report type identifier |
| `name`               | string   | Report name (DDR, TRIR, JSA…)               |
| `category`           | string   | Category (drilling, HSE, production…)       |
| `frequency`          | string   | Required frequency (daily, per-job, etc.)   |
| `avg_completion_min` | integer  | Average time to complete in minutes         |
| `regulatory_required`| boolean  | Whether mandated by regulation              |

### ENT-005: Equipment

Represents a piece of field equipment installed at a well site, including
BOP stacks, ESP pumps, christmas trees, and other critical components.

**Source Table:** `dim_equipment`

| Property           | Type     | Description                                |
|--------------------|----------|--------------------------------------------|
| `equipment_id`     | string   | Primary key — unique equipment identifier  |
| `name`             | string   | Equipment name or designation              |
| `type`             | string   | Equipment type (BOP, ESP, separator…)      |
| `well_id`          | string   | FK — well site where installed             |
| `install_date`     | date     | Installation date                          |
| `last_maintenance` | date     | Date of most recent maintenance            |
| `criticality`      | string   | Criticality level (high, medium, low)      |

### ENT-006: RegulatoryBody

Represents a regulatory authority that governs field operations, inspections,
and reporting requirements.

**Source Table:** `dim_regulatory_bodies`

| Property               | Type     | Description                                  |
|------------------------|----------|----------------------------------------------|
| `reg_id`               | string   | Primary key — unique regulatory body ID      |
| `name`                 | string   | Regulatory body name (BSEE, TRRC, EPA…)     |
| `jurisdiction`         | string   | Jurisdiction scope (federal, state, basin…)  |
| `inspection_frequency` | string   | Required inspection frequency                |
| `key_requirements`     | string   | Primary compliance requirements              |

---

## Relationship Types

### REL-001: operates

| Field        | Value                                                  |
|--------------|--------------------------------------------------------|
| Source       | FieldEngineer (ENT-001)                                |
| Target       | WellSite (ENT-002)                                     |
| Cardinality  | Many-to-Many                                           |
| Description  | Field engineer operates or is assigned to a well site  |
| Join Key     | `engineer_id` via fact tables                          |

### REL-002: stationed_at

| Field        | Value                                                  |
|--------------|--------------------------------------------------------|
| Source       | FieldEngineer (ENT-001)                                |
| Target       | Facility (ENT-003)                                     |
| Cardinality  | Many-to-Many                                           |
| Description  | Field engineer is stationed at or works from a facility|
| Join Key     | `engineer_id` ↔ `facility_id` via fact tables          |

### REL-003: hosts

| Field        | Value                                                  |
|--------------|--------------------------------------------------------|
| Source       | WellSite (ENT-002)                                     |
| Target       | Equipment (ENT-005)                                    |
| Cardinality  | One-to-Many                                            |
| Description  | Well site hosts installed equipment                    |
| Join Key     | `well_id`                                              |

### REL-004: regulated_by

| Field        | Value                                                  |
|--------------|--------------------------------------------------------|
| Source       | Facility (ENT-003)                                     |
| Target       | RegulatoryBody (ENT-006)                               |
| Cardinality  | Many-to-Many                                           |
| Description  | Facility is governed by a regulatory authority         |
| Join Key     | `regulatory_jurisdiction` ↔ `jurisdiction`             |

### REL-005: requires_report

| Field        | Value                                                  |
|--------------|--------------------------------------------------------|
| Source       | WellSite (ENT-002)                                     |
| Target       | ReportType (ENT-004)                                   |
| Cardinality  | Many-to-Many                                           |
| Description  | Well site operations require specific report types     |
| Join Key     | Inferred from fact table `report_type` references      |

---

## Contextualizations

Contextualizations bind fact and stream data to entity pairs, creating the
analytical layer for documentation burden analysis.

### Event Contextualizations (Eventhouse)

| ID       | Name                        | Source Entity    | Target Entity   | Fact Table                  | Key Metric               |
|----------|-----------------------------|------------------|-----------------|-----------------------------|--------------------------|
| CTX-001  | Daily Drilling Reports      | FieldEngineer    | WellSite        | fact_daily_drilling_reports  | doc_time_min             |
| CTX-002  | SCADA Interactions          | FieldEngineer    | WellSite        | fact_scada_interactions      | duration_ms              |
| CTX-003  | HSE Inspections             | FieldEngineer    | Facility        | fact_hse_inspections         | doc_time_min             |
| CTX-004  | Permit-to-Work              | FieldEngineer    | Facility        | fact_permit_to_work          | doc_time_min             |
| CTX-005  | Well Integrity Events       | FieldEngineer    | WellSite        | fact_well_integrity_events   | doc_time_min             |
| CTX-006  | Tour Handoffs               | FieldEngineer    | WellSite        | fact_tour_handoffs           | doc_time_min             |
| CTX-007  | Production Alerts           | WellSite         | Equipment       | fact_production_alerts       | severity                 |
| CTX-008  | Field Location Tracking     | FieldEngineer    | Facility        | fact_field_location          | dwell_minutes            |

### Batch Contextualizations (Lakehouse)

| ID       | Name                        | Source Entity    | Target Entity   | Fact Table                   | Key Metric               |
|----------|-----------------------------|------------------|-----------------|-----------------------------|--------------------------|
| CTX-009  | Field Wellness Surveys      | FieldEngineer    | —               | fact_field_wellness           | admin_burden_score       |
| CTX-010  | Report Quality Metrics      | FieldEngineer    | ReportType      | fact_report_quality           | completeness_pct         |
| CTX-011  | Operator Satisfaction       | FieldEngineer    | Facility        | fact_operator_satisfaction    | audit_score              |
| CTX-012  | Production Performance      | FieldEngineer    | WellSite        | fact_production_performance   | doc_hours                |

### Stream Contextualizations (Eventhouse — Real-Time)

| ID       | Name                        | Source Entity    | Target Entity    | Stream Table                       | Key Metric           |
|----------|-----------------------------|------------------|------------------|------------------------------------|----------------------|
| CTX-013  | Well Telemetry              | WellSite         | Equipment        | stream_well_telemetry              | pressure_psi         |
| CTX-014  | SCADA Alarms                | Facility         | Equipment        | stream_scada_alarms                | priority             |
| CTX-015  | HSE Events                  | Facility         | RegulatoryBody   | stream_hse_events                  | severity             |
| CTX-016  | PTW Status Updates          | Facility         | FieldEngineer    | stream_ptw_status                  | approvals_pending    |
| CTX-017  | Environmental Monitoring    | Facility         | RegulatoryBody   | stream_environmental_monitoring    | exceedance_flag      |

---

## Data Storage Mapping

```
┌─────────────────────────────────────────────────────────────────┐
│                    FABRIC LAKEHOUSE                              │
│                  (OilGasLakehouse)                               │
│                                                                 │
│  Dimension Tables (Delta)          Batch Fact Tables (Delta)    │
│  ┌─────────────────────┐          ┌──────────────────────────┐  │
│  │ dim_field_engineers  │          │ fact_field_wellness       │  │
│  │ dim_well_sites       │          │ fact_report_quality       │  │
│  │ dim_facilities       │          │ fact_operator_satisfaction│  │
│  │ dim_report_types     │          │ fact_production_performance│ │
│  │ dim_equipment        │          └──────────────────────────┘  │
│  │ dim_regulatory_bodies│                                       │
│  └─────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   FABRIC EVENTHOUSE                              │
│                 (OilGasEventhouse)                               │
│                                                                 │
│  Event Fact Tables (KQL)           Stream Tables (KQL)          │
│  ┌──────────────────────────┐     ┌────────────────────────────┐│
│  │ fact_daily_drilling_rpts │     │ stream_well_telemetry      ││
│  │ fact_scada_interactions  │     │ stream_scada_alarms        ││
│  │ fact_hse_inspections     │     │ stream_hse_events          ││
│  │ fact_permit_to_work      │     │ stream_ptw_status          ││
│  │ fact_well_integrity_evts │     │ stream_environmental_mon   ││
│  │ fact_tour_handoffs       │     └────────────────────────────┘│
│  │ fact_production_alerts   │                                   │
│  │ fact_field_location      │                                   │
│  └──────────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Ontology Visualization

```
                        ┌──────────────┐
                        │  Regulatory  │
                        │    Body      │
                        │  (ENT-006)   │
                        └──────┬───────┘
                               │
                          regulated_by
                          (REL-004)
                               │
┌──────────────┐    stationed_at    ┌──────────────┐
│    Field     │───(REL-002)───────>│   Facility   │
│   Engineer   │                    │  (ENT-003)   │
│  (ENT-001)   │                    └──────────────┘
└──────┬───────┘                           │
       │                                   │
    operates                          [CTX-003] HSE Inspections
    (REL-001)                         [CTX-004] Permit-to-Work
       │                              [CTX-008] Field Location
       v                              [CTX-011] Operator Satisfaction
┌──────────────┐    requires_report   ┌──────────────┐
│   Well Site  │───(REL-005)────────>│  Report Type  │
│  (ENT-002)   │                     │  (ENT-004)    │
└──────┬───────┘                     └───────────────┘
       │
     hosts
    (REL-003)
       │
       v
┌──────────────┐
│  Equipment   │
│  (ENT-005)   │
└──────────────┘

Contextualizations on FieldEngineer → WellSite:
  [CTX-001] Daily Drilling Reports
  [CTX-002] SCADA Interactions
  [CTX-005] Well Integrity Events
  [CTX-006] Tour Handoffs
  [CTX-012] Production Performance

Contextualizations on WellSite → Equipment:
  [CTX-007] Production Alerts
  [CTX-013] Well Telemetry

Stream Contextualizations:
  [CTX-014] SCADA Alarms (Facility → Equipment)
  [CTX-015] HSE Events (Facility → RegulatoryBody)
  [CTX-016] PTW Status (Facility → FieldEngineer)
  [CTX-017] Environmental Monitoring (Facility → RegulatoryBody)
```

---

## Key Analytical Queries

### 1. DDR Documentation Time per Engineer

**Question:** How much time does each field engineer spend completing daily
drilling reports vs. footage actually drilled?

```
Target Entities: FieldEngineer, WellSite
Contextualization: CTX-001 (Daily Drilling Reports)
Key Metrics: doc_time_min, footage_drilled
Aggregation: SUM(doc_time_min) / SUM(footage_drilled) per engineer
Pattern: Engineers with high doc-time-per-foot ratios indicate
         excessive documentation burden relative to productive drilling.
```

### 2. HSE Inspection Documentation Burden

**Question:** How does HSE inspection documentation time correlate with the
number of findings, and which engineers spend disproportionate time on
post-inspection paperwork?

```
Target Entities: FieldEngineer, Facility
Contextualization: CTX-003 (HSE Inspections)
Key Metrics: doc_time_min, findings_count, critical_findings
Aggregation: AVG(doc_time_min) / AVG(findings_count) per engineer
Pattern: High doc-time per finding suggests overly complex forms or
         engineers compensating for poor mobile tools with manual entry.
```

### 3. Permit-to-Work Paperwork Overhead

**Question:** How much time do field engineers spend on permit-to-work
documentation across different hazard levels, and what is the signatory
completion rate?

```
Target Entities: FieldEngineer, Facility
Contextualization: CTX-004 (Permit-to-Work)
Key Metrics: doc_time_min, hazard_level, signatories_required, signatories_obtained
Aggregation: AVG(doc_time_min) GROUP BY hazard_level
Pattern: Escalating doc time with hazard level is expected, but
         disproportionate jumps may indicate redundant approval chains.
```

### 4. Well Integrity Test Documentation

**Question:** How long does it take to document well integrity tests, and do
failed tests result in significantly more documentation overhead?

```
Target Entities: FieldEngineer, WellSite
Contextualization: CTX-005 (Well Integrity Events)
Key Metrics: doc_time_min, result, pressure_psi, test_type
Aggregation: AVG(doc_time_min) GROUP BY result (pass/fail)
Pattern: Failed integrity tests should naturally require more
         documentation, but if the ratio exceeds 3x, it may indicate
         redundant incident reporting workflows.
```

### 5. Tour Handoff Knowledge Transfer Time

**Question:** How long do tour handoffs take, and does the number of open items
correlate with documentation time and narrative length?

```
Target Entities: FieldEngineer (from), FieldEngineer (to), WellSite
Contextualization: CTX-006 (Tour Handoffs)
Key Metrics: doc_time_min, open_items, narrative_length
Aggregation: AVG(doc_time_min) vs AVG(open_items) per well
Pattern: Wells with consistently high open-item counts during handoffs
         may indicate systemic documentation debt or deferred reporting.
```

---

## Appendix: Documentation Burden KPIs

| KPI                               | Formula                                                  | Target     |
|------------------------------------|----------------------------------------------------------|------------|
| DDR Documentation Rate             | SUM(doc_time_min) / COUNT(ddr_id) per engineer           | < 45 min   |
| HSE Doc Overhead Ratio             | SUM(doc_time_min) / SUM(findings_count) per facility     | < 15 min   |
| PTW Approval Efficiency            | AVG(signatories_obtained / signatories_required)          | > 95%      |
| Integrity Test Doc Ratio (fail)    | AVG(doc_time_min WHERE result='fail') / AVG(overall)     | < 3.0x     |
| Tour Handoff Efficiency            | AVG(doc_time_min) / AVG(open_items) per well             | < 5 min    |
| Admin Burden Score (Wellness)      | AVG(admin_burden_score) per rotation schedule            | < 6 / 10   |
| Regulatory Readiness               | AVG(regulatory_ready) across all reports                 | > 90%      |
| Field Time vs Doc Time             | SUM(dwell_minutes) / SUM(doc_time_min) per engineer      | > 3.0      |
