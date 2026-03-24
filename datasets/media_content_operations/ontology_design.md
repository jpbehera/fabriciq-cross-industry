# Media Content Operations — Ontology Design

## Overview

This document defines the Fabric IQ ontology for the **Media Content Operations Documentation Burden** use case. It maps the media/content production data model to Fabric IQ entity types, relationship types, properties, contextualizations (events), and data bindings across **Lakehouse** (Delta tables) and **Eventhouse** (KQL tables via Real-Time Intelligence).

**Ontology Name:** `MediaContentOpsOntology`

---

## Concept Mapping (RDF → Fabric IQ)

| RDF Concept       | Fabric IQ Concept   | Description                                    |
|-------------------|---------------------|------------------------------------------------|
| Class             | Entity Type         | A category of real-world object (Producer, Show) |
| Data Property     | Property            | An attribute of an entity (name, genre, network) |
| Object Property   | Relationship Type   | A link between two entities (produces, airs_on)  |
| Time-Series Event | Contextualization   | An event binding entities to time (ContentDocEvent, DeliveryAlert) |

---

## Entity Types (Lakehouse — Delta Tables)

### 1. Producer
**Source Table:** `dim_producers` (Lakehouse)
**Primary Key:** `producer_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| producer_id        | String  | Primary key                              |
| name               | String  | Producer name                            |
| role               | String  | Executive Producer, Line Producer, etc.  |
| department         | String  | Production department                    |
| shows_assigned     | Integer | Number of shows assigned                 |
| hire_date          | String  | Hire date                                |
| specialization     | String  | Drama, Unscripted, Documentary, etc.     |
| email              | String  | Email address                            |
| location           | String  | Office / studio location                 |
| seniority_level    | String  | Junior, Mid, Senior, Lead                |
| weekly_hours       | Integer | Contracted weekly hours                  |
| certification      | String  | Industry certifications                  |

### 2. Show
**Source Table:** `dim_shows` (Lakehouse)
**Primary Key:** `show_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| show_id            | String  | Primary key                              |
| name               | String  | Show title                               |
| genre              | String  | Drama, Comedy, Reality, Documentary      |
| network            | String  | Broadcasting network                     |
| platform           | String  | Streaming / distribution platform        |
| season             | Integer | Current season number                    |
| episode_count      | Integer | Total episodes this season               |
| production_budget  | Real    | Production budget                        |
| show_type          | String  | Scripted, Unscripted, Limited Series     |
| status             | String  | In Production, Post, Delivered, Hiatus   |
| premiere_date      | String  | Premiere / launch date                   |
| content_rating     | String  | TV-PG, TV-14, TV-MA, etc.               |

### 3. Network
**Source Table:** `dim_networks` (Lakehouse)
**Primary Key:** `network_id`

| Property               | Type    | Description                          |
|------------------------|---------|--------------------------------------|
| network_id             | String  | Primary key                          |
| name                   | String  | Network name                         |
| type                   | String  | Broadcast, Cable, Streaming, Digital |
| platform_count         | Integer | Number of platforms served            |
| content_hours_per_week | Integer | Weekly content hours                 |
| region                 | String  | Geographic region                    |

### 4. ContentTaskType
**Source Table:** `dim_content_task_types` (Lakehouse)
**Primary Key:** `task_type_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| task_type_id       | String  | Primary key                              |
| name               | String  | Task type name                           |
| category           | String  | Metadata, Rights, QC, Delivery, Admin    |
| avg_duration_min   | Integer | Average task duration in minutes         |
| requires_approval  | String  | Yes/No — requires approval step          |
| regulatory_flag    | String  | Yes/No — has regulatory implications     |

### 5. RightsHolder
**Source Table:** `dim_rights_holders` (Lakehouse)
**Primary Key:** `holder_id`

| Property             | Type    | Description                            |
|----------------------|---------|----------------------------------------|
| holder_id            | String  | Primary key                            |
| name                 | String  | Rights holder name                     |
| type                 | String  | Music, Footage, Talent, Format, Brand  |
| territory            | String  | Licensed territory                     |
| content_count        | Integer | Number of content items held           |
| avg_clearance_days   | Real    | Average clearance turnaround in days   |
| contact_email        | String  | Contact email address                  |
| preferred_method     | String  | Preferred clearance method             |
| contract_status      | String  | Active, Expired, Pending               |
| response_reliability | String  | High, Medium, Low                      |

### 6. Platform
**Source Table:** `dim_platforms` (Lakehouse)
**Primary Key:** `platform_id`

| Property               | Type    | Description                          |
|------------------------|---------|--------------------------------------|
| platform_id            | String  | Primary key                          |
| name                   | String  | Platform name                        |
| type                   | String  | SVOD, AVOD, Linear, FAST, Theatrical |
| spec_requirements      | String  | Technical spec requirements          |
| delivery_format        | String  | ProRes, H.264, IMF, etc.            |
| region                 | String  | Distribution region                  |
| resolution             | String  | 4K, HD, SD                           |
| audio_format           | String  | Dolby Atmos, 5.1, Stereo            |
| subtitle_required      | String  | Yes/No                               |
| turnaround_sla_hours   | Real    | Delivery SLA in hours                |

---

## Relationship Types

| Relationship ID | Name               | Source Entity    | Target Entity    | Cardinality | Description                                     |
|-----------------|--------------------|------------------|------------------|-------------|-------------------------------------------------|
| REL-001         | produces           | Producer         | Show             | Many:Many   | Producer produces show                          |
| REL-002         | airs_on            | Show             | Network          | Many:Many   | Show airs on network                            |
| REL-003         | delivers_to        | Show             | Platform         | Many:Many   | Show delivers to distribution platform          |
| REL-004         | clears_rights_with | Show             | RightsHolder     | Many:Many   | Show clears rights with rights holder           |
| REL-005         | categorized_by     | ContentDocEvent  | ContentTaskType  | Many:1      | Content documentation event categorized by task type |

**Implementation Notes:**
- `REL-001` is derived from `fact_content_doc_events` — producers are associated with shows via documentation events.
- `REL-002` is derived from `dim_shows.network` matching `dim_networks.name`.
- `REL-003` is derived from `fact_delivery_alerts` and `fact_content_handoffs` — shows delivered to platforms.
- `REL-004` is derived from `fact_rights_clearance` — shows linked to rights holders through clearance events.
- `REL-005` is derived from `fact_content_doc_events.task_type` matching `dim_content_task_types.task_type_id`.

---

## Contextualizations (Events — Eventhouse KQL Tables)

### CTX-001: ContentDocEvent
**Source Table:** `fact_content_doc_events` (Eventhouse)
**Key Entity Bindings:** Producer, Show, ContentTaskType

| Field                      | Type     | Description                                   |
|----------------------------|----------|-----------------------------------------------|
| doc_id                     | String   | Primary key                                   |
| producer_id                | String   | FK → Producer entity                          |
| show_id                    | String   | FK → Show entity                              |
| date                       | DateTime | Documentation event date                      |
| task_type                  | String   | FK → ContentTaskType entity                   |
| asset_id                   | String   | Content asset identifier                      |
| doc_time_min               | Integer  | Documentation time in minutes                 |
| metadata_fields_completed  | Integer  | Number of metadata fields completed           |
| status                     | String   | Complete, Partial, Pending                    |

### CTX-002: MAMInteraction
**Source Table:** `mam_interactions` (Eventhouse)
**Key Entity Bindings:** Producer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| interaction_id       | String   | Primary key                                   |
| producer_id          | String   | FK → Producer entity                          |
| timestamp            | DateTime | Interaction timestamp                         |
| system               | String   | MAM system (Aspera, Dalet, Avid, etc.)        |
| module               | String   | System module accessed                        |
| action               | String   | Action performed                              |
| duration_ms          | Integer  | Duration in milliseconds                      |
| asset_id             | String   | Content asset identifier                      |

### CTX-003: MetadataEntry
**Source Table:** `metadata_entries` (Eventhouse)
**Key Entity Bindings:** Producer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| entry_id             | String   | Primary key                                   |
| producer_id          | String   | FK → Producer entity                          |
| asset_id             | String   | Content asset identifier                      |
| timestamp            | DateTime | Entry timestamp                               |
| field_name           | String   | Metadata field name                           |
| field_value          | String   | Metadata field value                          |
| auto_populated       | String   | Yes/No — auto-populated by system             |
| manual_time_sec      | Integer  | Manual entry time in seconds                  |

### CTX-004: RightsClearance
**Source Table:** `rights_clearance` (Eventhouse)
**Key Entity Bindings:** Producer, Show, RightsHolder

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| clearance_id         | String   | Primary key                                   |
| rights_manager_id    | String   | FK → Producer entity (rights manager)         |
| show_id              | String   | FK → Show entity                              |
| holder_id            | String   | FK → RightsHolder entity                      |
| date                 | DateTime | Clearance request date                        |
| rights_type          | String   | Music, Footage, Talent, Format                |
| territory            | String   | Licensed territory                            |
| status               | String   | Requested, Approved, Denied, Pending          |
| doc_time_min         | Integer  | Documentation time in minutes                 |
| cycle_days           | Integer  | Clearance cycle in days                       |

### CTX-005: ContentHandoff
**Source Table:** `content_handoffs` (Eventhouse)
**Key Entity Bindings:** Show

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| handoff_id           | String   | Primary key                                   |
| show_id              | String   | FK → Show entity                              |
| from_role            | String   | Source role in handoff                         |
| to_role              | String   | Target role in handoff                        |
| timestamp            | DateTime | Handoff timestamp                             |
| asset_count          | Integer  | Number of assets handed off                   |
| doc_time_min         | Integer  | Documentation time in minutes                 |
| notes_length         | Integer  | Length of handoff notes                       |

### CTX-006: ApprovalWorkflow
**Source Table:** `approval_workflows` (Eventhouse)
**Key Entity Bindings:** Show, Producer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| approval_id          | String   | Primary key                                   |
| show_id              | String   | FK → Show entity                              |
| producer_id          | String   | FK → Producer entity                          |
| timestamp            | DateTime | Approval event timestamp                      |
| approval_type        | String   | Content, Rights, Delivery, Regulatory         |
| status               | String   | Submitted, Approved, Rejected, Revision       |
| approver             | String   | Approver name / role                          |
| cycle_time_hours     | Real     | Approval cycle time in hours                  |

### CTX-007: RegulatoryReview
**Source Table:** `regulatory_reviews` (Eventhouse)
**Key Entity Bindings:** Producer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| review_id            | String   | Primary key                                   |
| asset_id             | String   | Content asset identifier                      |
| producer_id          | String   | FK → Producer entity                          |
| timestamp            | DateTime | Review timestamp                              |
| regulation           | String   | Regulation type (FCC, COPPA, GDPR, etc.)      |
| finding              | String   | Review finding                                |
| severity             | String   | Critical, Major, Minor                        |
| remediation_time_min | Integer  | Time to remediate in minutes                  |

### CTX-008: DeliveryAlert
**Source Table:** `delivery_alerts` (Eventhouse)
**Key Entity Bindings:** Show, Platform

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| alert_id             | String   | Primary key                                   |
| show_id              | String   | FK → Show entity                              |
| platform_id          | String   | FK → Platform entity                          |
| timestamp            | DateTime | Alert timestamp                               |
| alert_type           | String   | Deadline, Rejection, Spec Mismatch, Missing   |
| severity             | String   | Critical, Warning, Info                       |
| deadline_date        | String   | Delivery deadline date                        |
| days_to_deadline     | Integer  | Days remaining to deadline                    |

### CTX-009: MAMActivity (Real-Time Stream)
**Source Table:** `mam_activity` (Eventhouse)
**Key Entity Bindings:** Producer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| activity_id          | String   | Primary key                                   |
| producer_id          | String   | FK → Producer entity                          |
| timestamp            | DateTime | Activity timestamp                            |
| asset_id             | String   | Content asset identifier                      |
| action               | String   | Upload, Edit, Review, Export, Tag             |
| module               | String   | MAM system module                             |
| duration_sec         | Integer  | Duration in seconds                           |

### CTX-010: DeliveryTracking (Real-Time Stream)
**Source Table:** `delivery_tracking` (Eventhouse)
**Key Entity Bindings:** Show, Platform

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| delivery_id          | String   | Primary key                                   |
| show_id              | String   | FK → Show entity                              |
| platform_id          | String   | FK → Platform entity                          |
| timestamp            | DateTime | Delivery tracking timestamp                   |
| status               | String   | Queued, Transferring, Complete, Failed         |
| file_size_gb         | Real     | File size in gigabytes                        |
| transfer_pct         | Real     | Transfer completion percentage                |

### CTX-011: QCResult (Real-Time Stream)
**Source Table:** `qc_results` (Eventhouse)
**Key Entity Bindings:** (asset-level — no direct entity FK)

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| qc_id                | String   | Primary key                                   |
| asset_id             | String   | Content asset identifier                      |
| timestamp            | DateTime | QC check timestamp                            |
| check_type           | String   | Video, Audio, Subtitle, Metadata, Packaging   |
| result               | String   | Pass, Fail, Warning                           |
| error_description    | String   | Error description if failed                   |
| severity             | String   | Critical, Major, Minor                        |

### CTX-012: RightsStatus (Real-Time Stream)
**Source Table:** `rights_status` (Eventhouse)
**Key Entity Bindings:** RightsHolder

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| status_id            | String   | Primary key                                   |
| clearance_id         | String   | FK → RightsClearance                          |
| timestamp            | DateTime | Status update timestamp                       |
| rights_type          | String   | Music, Footage, Talent, Format                |
| status               | String   | Requested, Approved, Denied, Escalated        |
| holder_response      | String   | Rights holder response                        |
| territory            | String   | Licensed territory                            |

### CTX-013: AudienceMetric (Real-Time Stream)
**Source Table:** `audience_metrics` (Eventhouse)
**Key Entity Bindings:** Show, Platform

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| metric_id            | String   | Primary key                                   |
| show_id              | String   | FK → Show entity                              |
| platform_id          | String   | FK → Platform entity                          |
| timestamp            | DateTime | Metric collection timestamp                   |
| viewers              | Integer  | Concurrent / total viewers                    |
| completion_rate      | Real     | Content completion rate                       |
| engagement_score     | Real     | Engagement score                              |

---

## Data Storage Mapping

### Lakehouse (Delta Tables — Dimensional/Static Data)

| Delta Table Name            | Source CSV                      | Entity Mapping            |
|-----------------------------|---------------------------------|---------------------------|
| dim_producers               | dim_producers.csv               | Producer entity           |
| dim_shows                   | dim_shows.csv                   | Show entity               |
| dim_networks                | dim_networks.csv                | Network entity            |
| dim_content_task_types      | dim_content_task_types.csv      | ContentTaskType entity    |
| dim_rights_holders          | dim_rights_holders.csv          | RightsHolder entity       |
| dim_platforms               | dim_platforms.csv               | Platform entity           |
| fact_crew_wellness          | fact_crew_wellness.csv          | Wellness analytics        |
| fact_content_quality        | fact_content_quality.csv        | Quality analytics         |
| fact_client_satisfaction    | fact_client_satisfaction.csv    | Satisfaction analytics    |
| fact_production_performance | fact_production_performance.csv | Performance analytics     |

### Eventhouse (KQL Tables — Event/Streaming Data)

| KQL Table Name         | Source CSV                       | Contextualization |
|------------------------|----------------------------------|-------------------|
| content_doc_events     | fact_content_doc_events.csv      | CTX-001           |
| mam_interactions       | fact_mam_interactions.csv        | CTX-002           |
| metadata_entries       | fact_metadata_entries.csv        | CTX-003           |
| rights_clearance       | fact_rights_clearance.csv        | CTX-004           |
| content_handoffs       | fact_content_handoffs.csv        | CTX-005           |
| approval_workflows     | fact_approval_workflows.csv      | CTX-006           |
| regulatory_reviews     | fact_regulatory_reviews.csv      | CTX-007           |
| delivery_alerts        | fact_delivery_alerts.csv         | CTX-008           |
| mam_activity           | stream_mam_activity.csv          | CTX-009           |
| delivery_tracking      | stream_delivery_tracking.csv     | CTX-010           |
| qc_results             | stream_qc_results.csv            | CTX-011           |
| rights_status          | stream_rights_status.csv         | CTX-012           |
| audience_metrics       | stream_audience_metrics.csv      | CTX-013           |

---

## Ontology Visualization

```
                          ┌────────────────┐
                          │ContentTaskType │
                          └───────┬────────┘
                                  │ categorized_by
                                  ▼
┌──────────┐   produces    ┌──────────────┐   airs_on     ┌──────────────┐
│ Producer │──────────────▶│    Show      │──────────────▶│   Network    │
└────┬─────┘               └──────┬───────┘               └──────────────┘
     │                            │
     │                   delivers_to / clears_rights_with
     │                     ┌──────┴───────┐
     │                     ▼              ▼
     │             ┌──────────────┐ ┌──────────────┐
     │             │  Platform    │ │ RightsHolder │
     │             └──────────────┘ └──────────────┘
     │
     │    ┌─────────────────┬──────────────────┬──────────────┐
     ▼    ▼                 ▼                  ▼              ▼
┌──────────────┐  ┌─────────────────┐  ┌──────────────┐  ┌───────────┐
│ContentDocEvt │  │ MAM Interaction │  │MetadataEntry │  │Regulatory │
│  (CTX-001)   │  │   (CTX-002)     │  │  (CTX-003)   │  │  Review   │
└──────────────┘  └─────────────────┘  └──────────────┘  │ (CTX-007) │
                                                          └───────────┘
         ┌──────────────┬───────────────┬───────────────┐
         ▼              ▼               ▼               ▼
  ┌──────────────┐┌───────────┐┌──────────────┐┌──────────────┐
  │   Rights     ││  Content  ││  Approval    ││  Delivery    │
  │  Clearance   ││  Handoff  ││  Workflow    ││   Alert      │
  │  (CTX-004)   ││ (CTX-005) ││  (CTX-006)  ││  (CTX-008)   │
  └──────────────┘└───────────┘└──────────────┘└──────────────┘

            ── Real-Time Streaming Layer ──

┌───────────┐┌──────────┐┌───────────┐┌──────────┐┌──────────┐
│   MAM     ││ Delivery ││    QC     ││  Rights  ││ Audience │
│ Activity  ││ Tracking ││  Results  ││  Status  ││ Metrics  │
│ (CTX-009) ││(CTX-010) ││ (CTX-011) ││(CTX-012) ││(CTX-013) │
└───────────┘└──────────┘└───────────┘└──────────┘└──────────┘
```

---

## Key Analytical Queries Enabled by This Ontology

### 1. Documentation Burden per Producer
```kql
content_doc_events
| summarize total_doc_min = sum(doc_time_min),
            task_count = count()
  by producer_id
| order by total_doc_min desc
```

### 2. Rights Clearance Cycle Time by Holder Reliability
```kql
rights_clearance
| join kind=inner dim_rights_holders on $left.holder_id == $right.holder_id
| summarize avg_cycle_days = avg(cycle_days),
            avg_doc_time = avg(doc_time_min)
  by response_reliability
| order by avg_cycle_days desc
```

### 3. Delivery Rejection Rate by Platform
```kql
delivery_alerts
| where alert_type == "Rejection"
| summarize rejection_count = count()
  by platform_id
| order by rejection_count desc
```

### 4. Metadata Entry: Manual vs Auto-Populated
```kql
metadata_entries
| summarize total_manual_sec = sum(manual_time_sec),
            auto_count = countif(auto_populated == "Yes"),
            manual_count = countif(auto_populated == "No")
  by producer_id
| extend auto_pct = round(100.0 * auto_count / (auto_count + manual_count), 1)
| order by total_manual_sec desc
```

### 5. Production Performance: Doc Hours vs Creative Hours
```sql
SELECT
    p.name AS show_name,
    pp.doc_hours,
    pp.creative_hours,
    ROUND(pp.doc_hours * 100.0 / (pp.doc_hours + pp.creative_hours), 1) AS doc_burden_pct
FROM fact_production_performance pp
JOIN dim_shows p ON pp.show_id = p.show_id
ORDER BY doc_burden_pct DESC
```
