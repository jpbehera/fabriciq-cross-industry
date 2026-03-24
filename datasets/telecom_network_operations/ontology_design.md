# Telecom Network Operations — Ontology Design

## Overview

This document defines the Fabric IQ ontology for the **Telecom Network Operations Documentation Burden** use case. It maps the telecom data model to Fabric IQ entity types, relationship types, properties, contextualizations (events), and data bindings across **Lakehouse** (Delta tables) and **Eventhouse** (KQL tables via Real-Time Intelligence).

**Ontology Name:** `TelecomNetworkOpsOntology`

---

## Concept Mapping (RDF → Fabric IQ)

| RDF Concept       | Fabric IQ Concept   | Description                                    |
|-------------------|---------------------|------------------------------------------------|
| Class             | Entity Type         | A category of real-world object (Engineer, Equipment) |
| Data Property     | Property            | An attribute of an entity (name, role, region)  |
| Object Property   | Relationship Type   | A link between two entities (assigned_to, serves) |
| Time-Series Event | Contextualization   | An event binding entities to time (OutageEvent, SLAAlert) |

---

## Entity Types (Lakehouse — Delta Tables)

### 1. Engineer
**Source Table:** `dim_engineers` (Lakehouse)
**Primary Key:** `engineer_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| engineer_id        | String  | Primary key                              |
| first_name         | String  | First name                               |
| last_name          | String  | Last name                                |
| role               | String  | NOC Analyst, Network Engineer, Field Tech |
| tier               | String  | Tier 1, 2, 3                             |
| certifications     | String  | CCNA, CCNP, JNCIA, etc.                 |
| region             | String  | Geographic region                        |
| hire_date          | String  | Hire date                                |
| on_call_schedule   | String  | On-call rotation                         |
| specialty          | String  | Fiber, Wireless, Security, etc.          |
| email              | String  | Email address                            |
| years_experience   | Integer | Years of experience                      |

### 2. EnterpriseCustomer
**Source Table:** `dim_enterprise_customers` (Lakehouse)
**Primary Key:** `customer_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| customer_id        | String  | Primary key                              |
| name               | String  | Customer name                            |
| industry           | String  | Industry vertical                        |
| contract_value     | Real    | Annual contract value                    |
| sla_tier           | String  | Platinum, Gold, Silver, Bronze           |
| circuit_count      | Integer | Number of circuits                       |
| region             | String  | Geographic region                        |
| contract_start     | String  | Contract start date                      |
| contract_end       | String  | Contract end date                        |
| account_manager    | String  | Assigned account manager                 |

### 3. Equipment
**Source Table:** `dim_equipment` (Lakehouse)
**Primary Key:** `equipment_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| equipment_id       | String  | Primary key                              |
| name               | String  | Equipment name                           |
| vendor             | String  | Manufacturer                             |
| model              | String  | Model number                             |
| site_id            | String  | Site location (FK)                       |
| site_type          | String  | Site type                                |
| region             | String  | Geographic region                        |
| install_date       | String  | Installation date                        |
| firmware_version   | String  | Current firmware                         |
| criticality        | String  | Critical, High, Medium, Low              |
| status             | String  | Active, Degraded, Maintenance            |

### 4. NetworkSegment
**Source Table:** `dim_network_segments` (Lakehouse)
**Primary Key:** `segment_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| segment_id         | String  | Primary key                              |
| name               | String  | Segment name                             |
| type               | String  | Metro Fiber, Backbone, Access, etc.      |
| technology         | String  | Network technology                       |
| region             | String  | Geographic region                        |
| node_count         | Integer | Number of nodes                          |
| circuit_count      | Integer | Number of circuits                       |
| capacity_gbps      | Real    | Capacity in Gbps                         |
| redundancy_level   | String  | Redundancy configuration                 |

### 5. ServiceArea
**Source Table:** `dim_service_areas` (Lakehouse)
**Primary Key:** `area_id`

| Property           | Type    | Description                              |
|--------------------|---------|------------------------------------------|
| area_id            | String  | Primary key                              |
| name               | String  | Service area name                        |
| region             | String  | Geographic region                        |
| customer_count     | Integer | Number of customers served               |
| technology         | String  | Primary technology                       |
| capacity_gbps      | Real    | Total capacity                           |
| last_upgrade       | String  | Last upgrade date                        |
| pop_count          | Integer | Points of presence                       |
| fiber_miles        | Real    | Fiber miles deployed                     |

### 6. TicketType
**Source Table:** `dim_ticket_types` (Lakehouse)
**Primary Key:** `ticket_type_id`

| Property               | Type    | Description                          |
|------------------------|---------|--------------------------------------|
| ticket_type_id         | String  | Primary key                          |
| name                   | String  | Ticket type name                     |
| category               | String  | Outage, Degradation, Maintenance     |
| priority_levels        | String  | Available priority levels            |
| avg_resolution_min     | Integer | Average resolution time              |
| sla_target_hours       | Real    | SLA target in hours                  |
| documentation_template | String  | Required documentation template      |
| requires_rca           | String  | Yes/No — requires root cause analysis |

---

## Relationship Types

| Relationship ID | Name               | Source Entity       | Target Entity       | Cardinality | Description                                    |
|-----------------|--------------------|---------------------|---------------------|-------------|------------------------------------------------|
| REL-001         | operates_in        | Engineer            | ServiceArea         | Many:Many   | Engineer operates in service area              |
| REL-002         | manages            | Engineer            | NetworkSegment      | Many:Many   | Engineer manages network segment               |
| REL-003         | serves             | ServiceArea         | EnterpriseCustomer  | Many:Many   | Service area serves enterprise customer        |
| REL-004         | hosts              | NetworkSegment      | Equipment           | 1:Many      | Network segment hosts equipment                |
| REL-005         | monitors           | Engineer            | Equipment           | Many:Many   | Engineer monitors equipment                    |

**Implementation Notes:**
- `REL-001` and `REL-002` are primarily derived from `fact_trouble_tickets` and `fact_field_dispatches` — engineers are dynamically associated with areas and segments based on ticket assignments.
- `REL-003` is derived from `dim_enterprise_customers.region` matching `dim_service_areas.region`.
- `REL-004` is from `dim_equipment.site_id` linking to network segment infrastructure.

---

## Contextualizations (Events — Eventhouse KQL Tables)

### CTX-001: TroubleTicket
**Source Table:** `fact_trouble_tickets` (Eventhouse)
**Key Entity Bindings:** Engineer, TicketType, NetworkSegment, Equipment

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| ticket_id            | String   | Primary key                                   |
| engineer_id          | String   | FK → Engineer entity                          |
| area_id              | String   | FK → ServiceArea entity                       |
| ticket_date          | DateTime | Ticket creation date                          |
| ticket_type_id       | String   | FK → TicketType entity                        |
| priority             | String   | P1–P4                                         |
| open_time            | DateTime | Ticket open timestamp                         |
| close_time           | DateTime | Ticket close timestamp                        |
| doc_time_min         | Integer  | Documentation time in minutes                 |
| resolution_code      | String   | Resolution classification                     |
| escalation_count     | Integer  | Number of escalations                         |
| segment_id           | String   | FK → NetworkSegment entity                    |
| equipment_id         | String   | FK → Equipment entity                         |
| customers_affected   | Integer  | Number of affected customers                  |
| notes                | String   | Ticket notes                                  |

### CTX-002: NMSInteraction
**Source Table:** `nms_interactions` (Eventhouse)
**Key Entity Bindings:** Engineer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| interaction_id       | String   | Primary key                                   |
| engineer_id          | String   | FK → Engineer entity                          |
| timestamp            | DateTime | Interaction timestamp                         |
| system               | String   | NMS system (SolarWinds, NetBrain, etc.)       |
| action               | String   | Action performed                              |
| alarm_id             | String   | Associated alarm                              |
| duration_ms          | Integer  | Duration in milliseconds                      |
| correlation_group    | String   | Alarm correlation group                       |
| notes                | String   | Interaction notes                             |

### CTX-003: OutageEvent
**Source Table:** `outage_events` (Eventhouse)
**Key Entity Bindings:** NetworkSegment, Equipment, ServiceArea

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| outage_id            | String   | Primary key                                   |
| segment_id           | String   | FK → NetworkSegment entity                    |
| timestamp            | DateTime | Outage start timestamp                        |
| severity             | String   | Major, Minor, Critical                        |
| customers_affected   | Integer  | Impacted customer count                       |
| root_cause           | String   | Root cause classification                     |
| duration_min         | Integer  | Outage duration                               |
| doc_time_min         | Integer  | Documentation time                            |
| area_id              | String   | FK → ServiceArea entity                       |
| equipment_id         | String   | FK → Equipment entity                         |
| restoration_method   | String   | How service was restored                      |
| post_mortem_required | String   | Yes/No                                        |

### CTX-004: RCADocument
**Source Table:** `rca_documents` (Eventhouse)
**Key Entity Bindings:** Engineer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| rca_id               | String   | Primary key                                   |
| outage_id            | String   | FK → OutageEvent                              |
| engineer_id          | String   | FK → Engineer entity                          |
| timestamp            | DateTime | RCA creation timestamp                        |
| root_cause_category  | String   | Root cause category                           |
| contributing_factors | String   | Contributing factors                          |
| corrective_actions   | String   | Corrective actions taken                      |
| doc_time_min         | Integer  | Time to write RCA document                    |
| preventive_measures  | String   | Preventive measures                           |
| review_status        | String   | Draft, Under Review, Approved                 |
| pages_written        | Integer  | Number of pages                               |

### CTX-005: TicketEscalation
**Source Table:** `ticket_escalations` (Eventhouse)
**Key Entity Bindings:** Engineer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| escalation_id        | String   | Primary key                                   |
| ticket_id            | String   | FK → TroubleTicket                            |
| from_tier            | String   | Source tier                                    |
| to_tier              | String   | Target tier                                    |
| timestamp            | DateTime | Escalation timestamp                          |
| reason               | String   | Escalation reason                             |
| doc_time_min         | Integer  | Documentation time for escalation             |
| open_items           | Integer  | Open items at escalation                      |
| engineer_from        | String   | FK → Engineer entity (source)                 |
| engineer_to          | String   | FK → Engineer entity (target)                 |

### CTX-006: SLAAlert
**Source Table:** `sla_alerts` (Eventhouse)
**Key Entity Bindings:** EnterpriseCustomer, ServiceArea

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| alert_id             | String   | Primary key                                   |
| customer_id          | String   | FK → EnterpriseCustomer entity                |
| ticket_id            | String   | FK → TroubleTicket                            |
| timestamp            | DateTime | Alert timestamp                               |
| sla_metric           | String   | SLA metric type                               |
| threshold            | Real     | SLA threshold value                           |
| actual_value         | Real     | Actual measured value                         |
| breach_flag          | String   | Yes/No                                        |
| area_id              | String   | FK → ServiceArea entity                       |
| severity             | String   | Warning, Critical                             |
| notification_sent    | String   | Yes/No                                        |
| response_within_sla  | String   | Yes/No                                        |

### CTX-007: FieldLocation
**Source Table:** `field_location` (Eventhouse)
**Key Entity Bindings:** Engineer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| ping_id              | String   | Primary key                                   |
| technician_id        | String   | FK → Engineer entity                          |
| timestamp            | DateTime | Location ping timestamp                       |
| lat                  | Real     | Latitude                                      |
| lon                  | Real     | Longitude                                     |
| site_id              | String   | Site identifier                               |
| site_type            | String   | CO, Cell Tower, Data Center, etc.             |
| activity_type        | String   | Travel, Installation, Documentation           |
| dwell_minutes        | Real     | Time at location in minutes                   |

### CTX-008: NetworkAlarm (Real-Time Stream)
**Source Table:** `network_alarms` (Eventhouse)
**Key Entity Bindings:** Equipment

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| alarm_id             | String   | Primary key                                   |
| equipment_id         | String   | FK → Equipment entity                         |
| timestamp            | DateTime | Alarm timestamp                               |
| alarm_type           | String   | Alarm classification                          |
| severity             | String   | Critical, Major, Minor, Warning               |
| site_id              | String   | Site identifier                               |
| cleared_flag         | String   | Yes/No                                        |

### CTX-009: TicketActivity (Real-Time Stream)
**Source Table:** `ticket_activity` (Eventhouse)
**Key Entity Bindings:** Engineer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| activity_id          | String   | Primary key                                   |
| ticket_id            | String   | FK → TroubleTicket                            |
| engineer_id          | String   | FK → Engineer entity                          |
| timestamp            | DateTime | Activity timestamp                            |
| action               | String   | Create, Assign, Escalate, Resolve, Close      |
| status               | String   | Current ticket status                         |
| priority             | String   | Priority level                                |
| sla_remaining_min    | Integer  | SLA time remaining                            |

### CTX-010: FieldDispatch (Real-Time Stream)
**Source Table:** `field_dispatch` (Eventhouse)
**Key Entity Bindings:** Engineer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| dispatch_id          | String   | Primary key                                   |
| technician_id        | String   | FK → Engineer entity                          |
| timestamp            | DateTime | Dispatch timestamp                            |
| ticket_id            | String   | FK → TroubleTicket                            |
| status               | String   | Dispatched, EnRoute, Arrived, Working, Complete |
| location             | String   | Dispatch location                             |
| eta_min              | Integer  | Estimated time of arrival in minutes          |

### CTX-011: PerformanceMetric (Real-Time Stream)
**Source Table:** `performance_metrics` (Eventhouse)
**Key Entity Bindings:** Equipment

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| metric_id            | String   | Primary key                                   |
| equipment_id         | String   | FK → Equipment entity                         |
| timestamp            | DateTime | Metric collection timestamp                   |
| metric_type          | String   | CPU%, Optical Power, BER, Temperature         |
| value                | Real     | Measured value                                |
| threshold            | Real     | Threshold value                               |
| interface_id         | String   | Interface identifier                          |

### CTX-012: CustomerImpact (Real-Time Stream)
**Source Table:** `customer_impact` (Eventhouse)
**Key Entity Bindings:** EnterpriseCustomer

| Field                | Type     | Description                                   |
|----------------------|----------|-----------------------------------------------|
| impact_id            | String   | Primary key                                   |
| customer_id          | String   | FK → EnterpriseCustomer entity                |
| timestamp            | DateTime | Impact timestamp                              |
| service_affected     | String   | Service impacted                              |
| impact_type          | String   | Outage, Degradation, Latency                  |
| est_restore_time     | String   | Estimated restoration time                    |

---

## Data Storage Mapping

### Lakehouse (Delta Tables — Dimensional/Static Data)

| Delta Table Name            | Source CSV                      | Entity Mapping            |
|-----------------------------|---------------------------------|---------------------------|
| dim_engineers               | dim_engineers.csv               | Engineer entity           |
| dim_enterprise_customers    | dim_enterprise_customers.csv    | EnterpriseCustomer entity |
| dim_equipment               | dim_equipment.csv               | Equipment entity          |
| dim_network_segments        | dim_network_segments.csv        | NetworkSegment entity     |
| dim_service_areas           | dim_service_areas.csv           | ServiceArea entity        |
| dim_ticket_types            | dim_ticket_types.csv            | TicketType entity         |
| fact_technician_wellness    | fact_technician_wellness.csv    | Wellness analytics        |
| fact_ticket_quality         | fact_ticket_quality.csv         | Quality analytics         |
| fact_customer_satisfaction  | fact_customer_satisfaction.csv  | Satisfaction analytics    |
| fact_network_performance    | fact_network_performance.csv    | Performance analytics     |
| fact_field_dispatches       | fact_field_dispatches.csv       | Dispatch analytics        |
| fact_trouble_tickets        | fact_trouble_tickets.csv        | Ticket analytics          |

### Eventhouse (KQL Tables — Event/Streaming Data)

| KQL Table Name         | Source CSV                     | Contextualization |
|------------------------|--------------------------------|-------------------|
| nms_interactions       | fact_nms_interactions.csv      | CTX-002           |
| outage_events          | fact_outage_events.csv         | CTX-003           |
| rca_documents          | fact_rca_documents.csv         | CTX-004           |
| ticket_escalations     | fact_ticket_escalations.csv    | CTX-005           |
| sla_alerts             | fact_sla_alerts.csv            | CTX-006           |
| field_location         | fact_field_location.csv        | CTX-007           |
| network_alarms         | stream_network_alarms.csv      | CTX-008           |
| ticket_activity        | stream_ticket_activity.csv     | CTX-009           |
| field_dispatch         | stream_field_dispatch.csv      | CTX-010           |
| performance_metrics    | stream_performance_metrics.csv | CTX-011           |
| customer_impact        | stream_customer_impact.csv     | CTX-012           |

---

## Ontology Visualization

```
                           ┌──────────────┐
                           │  TicketType  │
                           └──────┬───────┘
                                  │ categorizes
                                  ▼
┌──────────┐  operates_in  ┌──────────────┐   serves    ┌──────────────────┐
│ Engineer │──────────────▶│ ServiceArea  │────────────▶│EnterpriseCustomer│
└────┬─────┘               └──────────────┘             └──────────────────┘
     │                                                           │
     │  manages / monitors                                       │
     ▼                                                           │
┌──────────────┐   hosts    ┌──────────────┐                     │
│NetworkSegment│───────────▶│  Equipment   │                     │
└──────────────┘            └──────────────┘                     │
                                                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                   ▼
    ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐
    │ TroubleTicket   │  │ OutageEvent  │  │  SLA Alert     │
    │   (CTX-001)     │  │  (CTX-003)   │  │  (CTX-006)     │
    └─────────────────┘  └──────────────┘  └────────────────┘
              │
     ┌────────┼─────────┬──────────────┐
     ▼        ▼         ▼              ▼
┌─────────┐┌────────┐┌──────────┐┌──────────┐
│  NMS    ││  RCA   ││ Ticket   ││  Field   │
│Interact.││Document││Escalation││ Location │
│(CTX-002)││(CTX-004)│(CTX-005) ││(CTX-007) │
└─────────┘└────────┘└──────────┘└──────────┘

         ── Real-Time Streaming Layer ──

┌───────────┐┌──────────┐┌───────────┐┌──────────┐┌──────────┐
│  Network  ││ Ticket   ││   Field   ││Performnce││ Customer │
│  Alarms   ││ Activity ││ Dispatch  ││ Metrics  ││  Impact  │
│ (CTX-008) ││(CTX-009) ││ (CTX-010) ││(CTX-011) ││(CTX-012) │
└───────────┘└──────────┘└───────────┘└──────────┘└──────────┘
```

---

## Key Analytical Queries Enabled by This Ontology

### 1. Documentation Burden per Engineer
```kql
fact_trouble_tickets
| summarize total_doc_min = sum(doc_time_min),
            ticket_count = count()
  by engineer_id
| order by total_doc_min desc
```

### 2. RCA Documentation Time vs Outage Severity
```kql
rca_documents
| join kind=inner outage_events on outage_id
| summarize avg_doc_time = avg(doc_time_min),
            avg_pages = avg(pages_written)
  by severity
| order by avg_doc_time desc
```

### 3. SLA Breach Correlation with Documentation Delays
```kql
sla_alerts
| where breach_flag == "Yes"
| summarize breach_count = count(),
            avg_response_time = avg(actual_value)
  by customer_id
| order by breach_count desc
```

### 4. Field Technician Time Allocation
```kql
field_location
| summarize total_dwell_min = sum(dwell_minutes),
            site_visits = count()
  by technician_id, activity_type
| order by technician_id, total_dwell_min desc
```

### 5. Equipment Alarm Frequency and Network Health
```kql
network_alarms
| where cleared_flag == "No"
| summarize open_alarms = count()
  by equipment_id, alarm_type, severity
| order by open_alarms desc
```
