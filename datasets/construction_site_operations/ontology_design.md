# Construction Site Operations — Ontology Design

## Overview

This document defines the Fabric IQ ontology for the **Construction Site Operations** use case. It maps the construction data model to Fabric IQ entity types, relationship types, properties, contextualizations (events), and data bindings across **Lakehouse** (Delta tables) and **Eventhouse** (KQL tables via Real-Time Intelligence).

**Ontology Name:** `ConstructionSiteOpsOntology`

The Construction Site Operations ontology models the documentation burden experienced by field supervisors across daily logs, RFIs (Requests for Information), safety inspections, change orders, and phase handoffs. By capturing both structured event data and real-time streams (safety events, equipment telemetry, weather), this ontology enables analysis of how much supervisor time is consumed by administrative work versus actual field supervision.

**Model Summary:** 6 entity types, 5 relationships, 13 contextualizations (8 event facts + 5 streams)

---

## Concept Mapping (RDF → Fabric IQ)

| RDF Concept       | Fabric IQ Concept   | Description                                              |
|-------------------|---------------------|----------------------------------------------------------|
| Class             | Entity Type         | A category of real-world object (Supervisor, Project)    |
| Data Property     | Property            | An attribute of an entity (name, role, certifications)   |
| Object Property   | Relationship Type   | A link between two entities (supervises, located_at)     |
| Time-Series Event | Contextualization   | An event binding entities to time (DailyLogEvent, RFIEvent) |

---

## Entity Types (Lakehouse — Delta Tables)

### 1. Supervisor
**Source Table:** `dim_supervisors` (Lakehouse)
**Primary Key:** `supervisor_id`

| Property         | Type    | Description                                |
|------------------|---------|--------------------------------------------|
| supervisor_id    | String  | Primary key identifier                     |
| name             | String  | Full name of the supervisor                |
| role             | String  | Site Super, Project Manager, Foreman, etc. |
| certifications   | String  | OSHA 30, PMP, LEED AP, etc.               |
| years_experience | Integer | Years of construction experience           |
| project_id       | String  | Currently assigned project (FK)            |
| hire_date        | Date    | Date of hire                               |
| department       | String  | Department or division                     |
| region           | String  | Geographic region                          |
| email            | String  | Contact email address                      |
| phone            | String  | Contact phone number                       |
| status           | String  | Active, On Leave, Terminated               |

### 2. Project
**Source Table:** `dim_projects` (Lakehouse)
**Primary Key:** `project_id`

| Property        | Type    | Description                                  |
|-----------------|---------|----------------------------------------------|
| project_id      | String  | Primary key identifier                       |
| name            | String  | Project name                                 |
| type            | String  | Commercial, Residential, Industrial, etc.    |
| value           | Float   | Total contract value                         |
| start_date      | Date    | Project start date                           |
| est_completion  | Date    | Estimated completion date                    |
| owner           | String  | Property/project owner                       |
| gc_name         | String  | General contractor name                      |
| status          | String  | Active, Complete, On Hold, Delayed           |
| contract_type   | String  | Lump Sum, GMP, Cost-Plus, Design-Build       |
| city            | String  | Project city                                 |
| state           | String  | Project state                                |

### 3. ProjectSite
**Source Table:** `dim_project_sites` (Lakehouse)
**Primary Key:** `site_id`

| Property         | Type    | Description                                |
|------------------|---------|--------------------------------------------|
| site_id          | String  | Primary key identifier                     |
| project_id       | String  | Associated project (FK)                    |
| address          | String  | Physical street address                    |
| region           | String  | Geographic region                          |
| active_trades    | Integer | Number of active trades on site            |
| total_area_sqft  | Integer | Total site area in square feet             |
| floors           | Integer | Number of floors in structure              |
| site_status      | String  | Pre-Construction, Active, Punch List, etc. |
| lat              | Float   | Latitude coordinate                        |
| lon              | Float   | Longitude coordinate                       |

### 4. InspectionType
**Source Table:** `dim_inspection_types` (Lakehouse)
**Primary Key:** `inspection_type_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| inspection_type_id | String  | Primary key identifier                   |
| name               | String  | Inspection name (e.g., Fire Stopping)    |
| category           | String  | Safety, Structural, MEP, Environmental   |
| required_frequency | String  | Daily, Weekly, Per-Phase, As-Needed      |
| avg_duration_min   | Integer | Average inspection duration in minutes   |
| checklist_items    | Integer | Number of items on the inspection form   |

### 5. Subcontractor
**Source Table:** `dim_subcontractors` (Lakehouse)
**Primary Key:** `subcontractor_id`

| Property            | Type    | Description                             |
|---------------------|---------|-----------------------------------------|
| subcontractor_id    | String  | Primary key identifier                  |
| name                | String  | Company name                            |
| trade               | String  | Electrical, Plumbing, HVAC, Steel, etc. |
| license_no          | String  | State license number                    |
| safety_rating       | Float   | Safety performance rating (EMR)         |
| projects_completed  | Integer | Total projects completed                |

### 6. TradePhase
**Source Table:** `dim_trade_phases` (Lakehouse)
**Primary Key:** `phase_id`

| Property      | Type    | Description                                  |
|---------------|---------|----------------------------------------------|
| phase_id      | String  | Primary key identifier                       |
| name          | String  | Phase name (e.g., Rough-In, Framing)         |
| project_id    | String  | Associated project (FK)                      |
| sequence      | Integer | Phase order within the project schedule      |
| planned_start | Date    | Planned start date                           |
| planned_end   | Date    | Planned end date                             |
| budget        | Float   | Allocated budget for this phase              |

---

## Relationship Types

| Relationship ID | Name         | Source Entity | Target Entity | Cardinality | Description                                      |
|-----------------|--------------|---------------|---------------|-------------|--------------------------------------------------|
| REL-001         | supervises   | Supervisor    | Project       | Many:Many   | Supervisor oversees one or more projects         |
| REL-002         | located_at   | Project       | ProjectSite   | 1:Many      | Project has one or more physical sites           |
| REL-003         | works_on     | Subcontractor | Project       | Many:Many   | Subcontractor is contracted to a project         |
| REL-004         | belongs_to   | TradePhase    | Project       | Many:1      | Trade phase is part of a project schedule        |
| REL-005         | assigned_to  | Supervisor    | ProjectSite   | Many:Many   | Supervisor is assigned to oversee a site         |

**Implementation Notes:**
- `REL-001` (supervises) is derived from the `project_id` foreign key in `dim_supervisors` and from fact table references where supervisors log activity across multiple projects.
- `REL-002` (located_at) is derived from the `project_id` foreign key in `dim_project_sites`.
- `REL-003` (works_on) is derived from `fact_subcontractor_satisfaction` and phase handoff data linking subcontractors to projects.
- `REL-004` (belongs_to) is derived from the `project_id` foreign key in `dim_trade_phases`.
- `REL-005` (assigned_to) is a dynamic relationship derived from `fact_site_location` pings and daily log entries tying supervisors to specific sites.

---

## Contextualizations (Events — Eventhouse KQL Tables)

Contextualizations bind entities to time-series events. These are the core of Real-Time Intelligence analytics for construction documentation burden.

### CTX-001: DailyLogEvent
**Source Table:** `fact_daily_logs` (Eventhouse)
**Key Entity Bindings:** Supervisor, Project

| Field            | Type     | Description                                       |
|------------------|----------|---------------------------------------------------|
| log_id           | String   | Primary key                                       |
| supervisor_id    | String   | FK → Supervisor entity                            |
| project_id       | String   | FK → Project entity                               |
| date             | DateTime | Log date                                          |
| weather          | String   | Weather conditions (Clear, Rain, Snow, etc.)      |
| crew_count       | Integer  | Number of crew members on site                    |
| work_summary     | String   | Free-text description of daily work performed     |
| doc_time_min     | Integer  | Minutes spent creating this daily log             |
| photos_attached  | Integer  | Number of photos attached to the log              |
| safety_incidents | Integer  | Number of safety incidents reported that day      |

**Analytical Value:** Core documentation burden metric. Tracks time supervisors spend on daily logs vs. field supervision. Enables weather-impact and crew-size correlation analysis.

### CTX-002: PMInteractionEvent
**Source Table:** `fact_pm_interactions` (Eventhouse)
**Key Entity Bindings:** Supervisor

| Field          | Type     | Description                                         |
|----------------|----------|-----------------------------------------------------|
| interaction_id | String   | Primary key                                         |
| supervisor_id  | String   | FK → Supervisor entity                              |
| timestamp      | DateTime | Interaction timestamp                               |
| system         | String   | Software system (Procore, PlanGrid, BIM 360, etc.)  |
| module         | String   | System module accessed                              |
| action         | String   | Action performed (Create, Update, Review, Approve)  |
| duration_ms    | Integer  | Interaction duration in milliseconds                |
| document_type  | String   | Document type being worked on                       |

**Analytical Value:** Project management software friction analysis. Identifies time sinks across different PM tools and modules. Quantifies system-switching overhead.

### CTX-003: RFIEvent
**Source Table:** `fact_rfi_events` (Eventhouse)
**Key Entity Bindings:** Supervisor, Project

| Field              | Type     | Description                                     |
|--------------------|----------|-------------------------------------------------|
| rfi_id             | String   | Primary key                                     |
| supervisor_id      | String   | FK → Supervisor entity                          |
| project_id         | String   | FK → Project entity                             |
| timestamp          | DateTime | RFI submission timestamp                        |
| question           | String   | RFI question text                               |
| status             | String   | Open, Responded, Closed, Overdue                |
| response_time_hours| Float    | Hours until response received                   |
| doc_time_min       | Integer  | Minutes spent preparing this RFI                |
| trade              | String   | Trade discipline the RFI pertains to            |

**Analytical Value:** RFI documentation cascade analysis. Tracks how RFI preparation time compounds with response delays. Identifies trades and project types with highest RFI burden.

### CTX-004: SafetyInspectionEvent
**Source Table:** `fact_safety_inspections` (Eventhouse)
**Key Entity Bindings:** Supervisor, ProjectSite

| Field             | Type     | Description                                      |
|-------------------|----------|--------------------------------------------------|
| inspection_id     | String   | Primary key                                      |
| supervisor_id     | String   | FK → Supervisor entity                           |
| site_id           | String   | FK → ProjectSite entity                          |
| date              | DateTime | Inspection date                                  |
| type              | String   | Inspection type (matches InspectionType entity)   |
| findings_count    | Integer  | Total findings documented                        |
| critical_count    | Integer  | Critical findings requiring immediate action     |
| doc_time_min      | Integer  | Minutes spent documenting the inspection         |
| corrective_actions| Integer  | Number of corrective actions issued              |

**Analytical Value:** Safety inspection burden quantification. Correlates findings complexity with documentation time. Tracks critical-vs-routine inspection ratio and its impact on supervisor workload.

### CTX-005: ChangeOrderEvent
**Source Table:** `fact_change_orders` (Eventhouse)
**Key Entity Bindings:** Supervisor, Project

| Field               | Type     | Description                                    |
|---------------------|----------|------------------------------------------------|
| change_order_id     | String   | Primary key                                    |
| project_id          | String   | FK → Project entity                            |
| supervisor_id       | String   | FK → Supervisor entity                         |
| timestamp           | DateTime | Change order submission timestamp              |
| description         | String   | Description of the change                      |
| cost_impact         | Float    | Dollar impact of the change order              |
| schedule_impact_days| Integer  | Schedule impact in days                        |
| doc_time_min        | Integer  | Minutes spent preparing the change order       |

**Analytical Value:** Change order documentation cost correlation. Analyzes whether higher-value change orders require proportionally more documentation time. Identifies schedule impact patterns.

### CTX-006: PhaseHandoffEvent
**Source Table:** `fact_phase_handoffs` (Eventhouse)
**Key Entity Bindings:** Project

| Field            | Type     | Description                                       |
|------------------|----------|---------------------------------------------------|
| handoff_id       | String   | Primary key                                       |
| project_id       | String   | FK → Project entity                               |
| from_trade       | String   | Trade handing off work                            |
| to_trade         | String   | Trade receiving work                              |
| timestamp        | DateTime | Handoff timestamp                                 |
| punch_list_items | Integer  | Number of punch list items at handoff             |
| doc_time_min     | Integer  | Minutes spent on handoff documentation            |
| approved         | String   | Yes/No — whether handoff was approved             |

**Analytical Value:** Trade coordination documentation burden. Measures handoff documentation time and punch list complexity. Identifies trade transitions that generate the most administrative overhead.

### CTX-007: SafetyAlertEvent
**Source Table:** `fact_safety_alerts` (Eventhouse)
**Key Entity Bindings:** Supervisor, ProjectSite

| Field            | Type     | Description                                       |
|------------------|----------|---------------------------------------------------|
| alert_id         | String   | Primary key                                       |
| site_id          | String   | FK → ProjectSite entity                           |
| supervisor_id    | String   | FK → Supervisor entity                            |
| timestamp        | DateTime | Alert timestamp                                   |
| alert_type       | String   | Fall Hazard, Confined Space, Electrical, etc.     |
| severity         | String   | Low, Medium, High, Critical                       |
| description      | String   | Alert description                                 |
| immediate_action | String   | Action taken (Stop Work, Evacuate, Barricade)     |
| osha_reportable  | String   | Yes/No — OSHA reportable incident                 |

**Analytical Value:** Safety alert pattern recognition. Tracks alert severity distribution, OSHA reportables frequency, and the documentation overhead triggered by each alert type.

### CTX-008: SiteLocationPing
**Source Table:** `fact_site_location` (Eventhouse)
**Key Entity Bindings:** Supervisor, ProjectSite

| Field          | Type     | Description                                        |
|----------------|----------|----------------------------------------------------|
| ping_id        | String   | Primary key                                        |
| supervisor_id  | String   | FK → Supervisor entity                             |
| timestamp      | DateTime | Location ping timestamp                            |
| site_id        | String   | FK → ProjectSite entity                            |
| zone           | String   | Site zone (Office Trailer, Active Floor, Staging)  |
| floor          | Integer  | Floor number                                       |
| activity_type  | String   | Supervision, Documentation, Meeting, Travel        |
| dwell_minutes  | Float    | Minutes spent in this zone                         |

**Analytical Value:** Field-vs-desk time ratio. Quantifies how much time supervisors spend in the office trailer (documentation) versus active floors (supervision). Enables zone-level productivity analysis.

### CTX-009: SupervisorWellnessEvent
**Source Table:** `fact_supervisor_wellness` (Lakehouse — Batch)
**Key Entity Bindings:** Supervisor

| Field              | Type     | Description                                    |
|--------------------|----------|------------------------------------------------|
| survey_id          | String   | Primary key                                    |
| supervisor_id      | String   | FK → Supervisor entity                         |
| date               | Date     | Survey date                                    |
| overtime_hours     | Float    | Overtime hours in period                       |
| admin_burden_score | Integer  | Self-reported admin burden (1-10)              |
| fatigue_score      | Integer  | Self-reported fatigue level (1-10)             |
| work_life_balance  | Integer  | Work-life balance rating (1-10)                |

**Analytical Value:** Supervisor burnout indicators. Correlates documentation burden metrics with self-reported wellness scores and overtime patterns.

### CTX-010: InspectionQualityEvent
**Source Table:** `fact_inspection_quality` (Lakehouse — Batch)
**Key Entity Bindings:** Supervisor

| Field                    | Type     | Description                              |
|--------------------------|----------|------------------------------------------|
| quality_id               | String   | Primary key                              |
| inspection_id            | String   | FK → inspection reference                |
| supervisor_id            | String   | FK → Supervisor entity                   |
| date                     | Date     | Quality assessment date                  |
| completeness_pct         | Float    | Percentage of checklist completed        |
| photo_coverage_pct       | Float    | Photo documentation coverage percentage  |
| defect_identification_rate| Float   | Rate of defect identification            |

**Analytical Value:** Documentation quality-vs-quantity tradeoff. Determines whether time pressure degrades inspection thoroughness and photo coverage.

### CTX-011: SubcontractorSatisfactionEvent
**Source Table:** `fact_subcontractor_satisfaction` (Lakehouse — Batch)
**Key Entity Bindings:** Subcontractor, Project

| Field                | Type     | Description                                    |
|----------------------|----------|------------------------------------------------|
| survey_id            | String   | Primary key                                    |
| subcontractor_id     | String   | FK → Subcontractor entity                      |
| project_id           | String   | FK → Project entity                            |
| date                 | Date     | Survey date                                    |
| coordination_score   | Integer  | Coordination rating (1-10)                     |
| payment_timeliness   | Integer  | Payment timeliness rating (1-10)               |
| communication_rating | Integer  | Communication rating (1-10)                    |

**Analytical Value:** Subcontractor relationship health. Correlates coordination scores with RFI volume and handoff documentation quality.

### CTX-012: ProjectPerformanceEvent
**Source Table:** `fact_project_performance` (Lakehouse — Batch)
**Key Entity Bindings:** Project, Supervisor

| Field                | Type     | Description                                    |
|----------------------|----------|------------------------------------------------|
| perf_id              | String   | Primary key                                    |
| project_id           | String   | FK → Project entity                            |
| supervisor_id        | String   | FK → Supervisor entity                         |
| month                | Date     | Performance month                              |
| budget_spent         | Float    | Budget spent to date                           |
| budget_remaining     | Float    | Remaining budget                               |
| schedule_variance_days| Integer | Days ahead or behind schedule                  |
| rfi_count            | Integer  | RFIs generated this month                      |
| change_order_count   | Integer  | Change orders this month                       |

**Analytical Value:** Project-level documentation cost analysis. Correlates RFI and change order volumes with budget and schedule variance.

### CTX-013: StreamingEvents (5 Real-Time Streams)

#### CTX-013a: SafetyEventStream
**Source Table:** `stream_safety_events` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** ProjectSite

| Field        | Type     | Description                                         |
|--------------|----------|-----------------------------------------------------|
| event_id     | String   | Primary key                                         |
| site_id      | String   | FK → ProjectSite entity                             |
| timestamp    | DateTime | Event timestamp                                     |
| event_type   | String   | Near Miss, Injury, Property Damage, Environmental   |
| zone         | String   | Site zone where event occurred                      |
| severity     | String   | Low, Medium, High, Critical                         |
| worker_count | Integer  | Number of workers in affected zone                  |

#### CTX-013b: EquipmentTelemetryStream
**Source Table:** `stream_equipment_telemetry` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** ProjectSite

| Field            | Type     | Description                                      |
|------------------|----------|--------------------------------------------------|
| telemetry_id     | String   | Primary key                                      |
| equipment_id     | String   | Equipment identifier                             |
| site_id          | String   | FK → ProjectSite entity                          |
| timestamp        | DateTime | Telemetry reading timestamp                      |
| utilization_pct  | Float    | Equipment utilization percentage                 |
| fuel_level       | Float    | Fuel level percentage                            |
| maintenance_flag | String   | Yes/No — maintenance alert triggered             |

#### CTX-013c: RFIStatusStream
**Source Table:** `stream_rfi_status` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Project

| Field        | Type     | Description                                         |
|--------------|----------|-----------------------------------------------------|
| rfi_id       | String   | RFI reference identifier                            |
| project_id   | String   | FK → Project entity                                 |
| timestamp    | DateTime | Status update timestamp                             |
| status       | String   | Submitted, Under Review, Responded, Closed          |
| assigned_to  | String   | Person assigned to respond                          |
| days_open    | Integer  | Number of days the RFI has been open                |
| priority     | String   | Low, Medium, High, Critical                         |

#### CTX-013d: WeatherConditionsStream
**Source Table:** `stream_weather_conditions` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** ProjectSite

| Field          | Type     | Description                                       |
|----------------|----------|---------------------------------------------------|
| reading_id     | String   | Primary key                                       |
| site_id        | String   | FK → ProjectSite entity                           |
| timestamp      | DateTime | Weather reading timestamp                         |
| temp_f         | Float    | Temperature in Fahrenheit                         |
| wind_mph       | Float    | Wind speed in miles per hour                      |
| precip_in      | Float    | Precipitation in inches                           |
| lightning_flag | String   | Yes/No — lightning detected in vicinity           |

#### CTX-013e: DailyLogActivityStream
**Source Table:** `stream_daily_log_activity` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Supervisor, Project

| Field          | Type     | Description                                       |
|----------------|----------|---------------------------------------------------|
| log_id         | String   | Log entry reference                               |
| supervisor_id  | String   | FK → Supervisor entity                            |
| timestamp      | DateTime | Activity timestamp                                |
| project_id     | String   | FK → Project entity                               |
| section        | String   | Log section (Weather, Crew, Work, Safety, Photos) |
| entry_type     | String   | Text, Photo, Voice-to-Text, Template              |
| photo_count    | Integer  | Photos attached in this entry                     |

---

## Data Storage Mapping

### Lakehouse (Delta Tables — Dimensional/Static Data)

| Delta Table Name               | Source CSV                          | Entity / Purpose           |
|--------------------------------|-------------------------------------|----------------------------|
| dim_supervisors                | dim_supervisors.csv                 | Supervisor entity          |
| dim_projects                   | dim_projects.csv                    | Project entity             |
| dim_project_sites              | dim_project_sites.csv               | ProjectSite entity         |
| dim_inspection_types           | dim_inspection_types.csv            | InspectionType entity      |
| dim_subcontractors             | dim_subcontractors.csv              | Subcontractor entity       |
| dim_trade_phases               | dim_trade_phases.csv                | TradePhase entity          |
| fact_supervisor_wellness       | fact_supervisor_wellness.csv        | Batch wellness analytics   |
| fact_inspection_quality        | fact_inspection_quality.csv         | Batch quality analytics    |
| fact_subcontractor_satisfaction| fact_subcontractor_satisfaction.csv | Batch satisfaction surveys |
| fact_project_performance       | fact_project_performance.csv        | Batch performance metrics  |

### Eventhouse (KQL Tables — Event/Streaming Data)

| KQL Table Name              | Source CSV                          | Contextualization  |
|-----------------------------|-------------------------------------|--------------------|
| daily_logs                  | fact_daily_logs.csv                 | CTX-001            |
| pm_interactions             | fact_pm_interactions.csv            | CTX-002            |
| rfi_events                  | fact_rfi_events.csv                 | CTX-003            |
| safety_inspections          | fact_safety_inspections.csv         | CTX-004            |
| change_orders               | fact_change_orders.csv              | CTX-005            |
| phase_handoffs              | fact_phase_handoffs.csv             | CTX-006            |
| safety_alerts               | fact_safety_alerts.csv              | CTX-007            |
| site_location               | fact_site_location.csv              | CTX-008            |
| stream_safety_events        | stream_safety_events.csv            | CTX-013a           |
| stream_equipment_telemetry  | stream_equipment_telemetry.csv      | CTX-013b           |
| stream_rfi_status           | stream_rfi_status.csv               | CTX-013c           |
| stream_weather_conditions   | stream_weather_conditions.csv       | CTX-013d           |
| stream_daily_log_activity   | stream_daily_log_activity.csv       | CTX-013e           |

---

## Ontology Visualization

```
                        ┌───────────────────┐
                        │   Subcontractor   │
                        └────────┬──────────┘
                                 │ works_on (REL-003)
                                 ▼
┌──────────────┐  supervises  ┌───────────────┐  located_at  ┌───────────────┐
│  Supervisor  │────────────▶ │    Project    │────────────▶ │  ProjectSite  │
└──────┬───────┘  (REL-001)   └───────┬───────┘  (REL-002)   └───────────────┘
       │                              │                              ▲
       │  assigned_to (REL-005)       │ belongs_to (REL-004)         │
       └──────────────────────────────┼──────────────────────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │  TradePhase   │
                              └───────────────┘

       ── Event Fact Layer (Eventhouse) ──

┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│ Daily Log  │ │    PM      │ │    RFI     │ │  Safety    │
│  Event     │ │ Interaction│ │   Event    │ │ Inspection │
│ (CTX-001)  │ │ (CTX-002)  │ │ (CTX-003)  │ │ (CTX-004)  │
└────────────┘ └────────────┘ └────────────┘ └────────────┘

┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│  Change    │ │   Phase    │ │  Safety    │ │   Site     │
│   Order    │ │  Handoff   │ │   Alert    │ │ Location   │
│ (CTX-005)  │ │ (CTX-006)  │ │ (CTX-007)  │ │ (CTX-008)  │
└────────────┘ └────────────┘ └────────────┘ └────────────┘

       ── Real-Time Streaming Layer ──

┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│  Safety    │ │ Equipment  │ │    RFI     │ │  Weather   │ │ Daily Log  │
│  Events    │ │ Telemetry  │ │   Status   │ │ Conditions │ │ Activity   │
│ (CTX-013a) │ │ (CTX-013b) │ │ (CTX-013c) │ │ (CTX-013d) │ │ (CTX-013e) │
└────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘

       ── Batch Analytical Layer (Lakehouse) ──

┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│ Supervisor │ │ Inspection │ │   Subcon   │ │  Project   │
│  Wellness  │ │  Quality   │ │Satisfaction│ │Performance │
│ (CTX-009)  │ │ (CTX-010)  │ │ (CTX-011)  │ │ (CTX-012)  │
└────────────┘ └────────────┘ └────────────┘ └────────────┘
```

---

## Key Analytical Queries Enabled by This Ontology

### 1. Daily Log Documentation Burden per Supervisor
```kql
daily_logs
| where date between (datetime(2026-01-01) .. datetime(2026-03-23))
| summarize total_log_minutes = sum(doc_time_min),
            log_count = count(),
            avg_doc_time = avg(doc_time_min),
            total_photos = sum(photos_attached),
            total_incidents = sum(safety_incidents)
  by supervisor_id
| order by total_log_minutes desc
```

### 2. RFI Response Time and Documentation Cascade
```kql
rfi_events
| where status != "Closed"
| summarize avg_response_hours = avg(response_time_hours),
            avg_doc_time = avg(doc_time_min),
            open_rfis = countif(status == "Open"),
            overdue_rfis = countif(status == "Overdue"),
            total_doc_minutes = sum(doc_time_min)
  by project_id, trade
| order by total_doc_minutes desc
```

### 3. Safety Inspection Documentation Burden by Site
```kql
safety_inspections
| summarize total_inspections = count(),
            total_doc_minutes = sum(doc_time_min),
            total_findings = sum(findings_count),
            critical_findings = sum(critical_count),
            avg_doc_per_inspection = avg(doc_time_min)
  by site_id, type
| order by total_doc_minutes desc
```

### 4. Change Order Cost-Documentation Correlation
```kql
change_orders
| summarize total_cost_impact = sum(cost_impact),
            total_schedule_days = sum(schedule_impact_days),
            total_doc_minutes = sum(doc_time_min),
            change_order_count = count(),
            avg_doc_per_co = avg(doc_time_min)
  by project_id
| extend doc_cost_ratio = total_doc_minutes / total_cost_impact
| order by total_doc_minutes desc
```

### 5. Supervisor Field-vs-Desk Time Analysis
```kql
site_location
| where timestamp between (datetime(2026-03-01) .. datetime(2026-03-23))
| summarize field_minutes = sumif(dwell_minutes, activity_type == "Supervision"),
            doc_minutes = sumif(dwell_minutes, activity_type == "Documentation"),
            meeting_minutes = sumif(dwell_minutes, activity_type == "Meeting"),
            travel_minutes = sumif(dwell_minutes, activity_type == "Travel")
  by supervisor_id
| extend field_pct = round(100.0 * field_minutes / (field_minutes + doc_minutes + meeting_minutes + travel_minutes), 1)
| order by field_pct asc
```

### 6. Weather-Driven Documentation Delays (SQL — Cross-Source)
```sql
-- Lakehouse SQL: Correlate weather with daily log documentation time
SELECT dl.project_id, dl.date, dl.weather,
       AVG(dl.doc_time_min) as avg_doc_time,
       AVG(dl.crew_count) as avg_crew,
       COUNT(*) as log_count,
       pp.schedule_variance_days
FROM fact_daily_logs dl
LEFT JOIN fact_project_performance pp
  ON dl.project_id = pp.project_id
  AND DATE_TRUNC('month', dl.date) = pp.month
WHERE dl.weather IN ('Rain', 'Snow', 'High Wind')
GROUP BY dl.project_id, dl.date, dl.weather, pp.schedule_variance_days
ORDER BY avg_doc_time DESC
```
