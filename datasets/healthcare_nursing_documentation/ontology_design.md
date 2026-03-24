# Healthcare Nursing Documentation Burden — Ontology Design

## Overview

This document defines the Fabric IQ ontology for the **Nursing Documentation Burden** use case. It maps the healthcare data model to Fabric IQ entity types, relationship types, properties, contextualizations (events), and data bindings across **Lakehouse** (Delta tables) and **Eventhouse** (KQL tables via Real-Time Intelligence).

**Ontology Name:** `NursingDocBurdenOntology`

---

## Concept Mapping (RDF → Fabric IQ)

| RDF Concept       | Fabric IQ Concept   | Description                                    |
|-------------------|---------------------|------------------------------------------------|
| Class             | Entity Type         | A category of real-world object (Nurse, Patient)|
| Data Property     | Property            | An attribute of an entity (name, age, unit)     |
| Object Property   | Relationship Type   | A link between two entities (assigned_to, cares_for) |
| Time-Series Event | Contextualization   | An event binding entities to time (DocumentationEvent) |

---

## Entity Types (Lakehouse — Delta Tables)

### 1. Nurse
**Source Table:** `dim_nurses` (Lakehouse)
**Primary Key:** `nurse_id`

| Property             | Type    | Description                          |
|----------------------|---------|--------------------------------------|
| nurse_id             | String  | Primary key (NRS-xxx)                |
| first_name           | String  | First name                           |
| last_name            | String  | Last name                            |
| unit_id              | String  | Assigned unit (FK)                   |
| role                 | String  | RN, Charge Nurse                     |
| credentials          | String  | RN BSN, RN MSN, RN ADN              |
| years_experience     | Integer | Years of nursing experience          |
| certifications       | String  | Specialty certifications             |
| shift_preference     | String  | Day, Night, Rotating                 |

### 2. Patient
**Source Table:** `dim_patients` (Lakehouse)
**Primary Key:** `patient_id`

| Property             | Type    | Description                          |
|----------------------|---------|--------------------------------------|
| patient_id           | String  | Primary key (PAT-xxx)               |
| first_name           | String  | First name                           |
| last_name            | String  | Last name                            |
| age                  | Integer | Patient age                          |
| gender               | String  | Gender                               |
| acuity_level         | Integer | Acuity score (2-5)                   |
| primary_diagnosis_id | String  | Primary diagnosis (FK)               |
| insurance_type       | String  | Insurance category                   |

### 3. HospitalUnit
**Source Table:** `dim_hospital_units` (Lakehouse)
**Primary Key:** `unit_id`

| Property              | Type    | Description                         |
|-----------------------|---------|-------------------------------------|
| unit_id               | String  | Primary key (UNIT-xxx)              |
| unit_name             | String  | Unit name                           |
| unit_type             | String  | Med-Surg, ICU, Emergency            |
| bed_count             | Integer | Total beds                          |
| target_nurse_ratio    | String  | Nurse:patient ratio (e.g., 1:5)     |
| ehr_system            | String  | EHR system in use                   |
| avg_daily_admissions  | Integer | Average daily admissions             |
| avg_daily_discharges  | Integer | Average daily discharges             |

### 4. DocumentationType
**Source Table:** `dim_documentation_types` (Lakehouse)
**Primary Key:** `doc_type_id`

| Property              | Type    | Description                              |
|-----------------------|---------|------------------------------------------|
| doc_type_id           | String  | Primary key (DOC-xxx)                    |
| doc_type_name         | String  | E.g., Head-to-Toe Assessment, MAR Entry  |
| category              | String  | Assessment, Medication, Communication    |
| avg_time_minutes      | Integer | Average completion time                  |
| is_duplicative        | String  | Yes/No/Partial flag                      |
| duplicative_reason    | String  | Why this is considered redundant         |

### 5. Medication
**Source Table:** `dim_medications` (Lakehouse)
**Primary Key:** `medication_id`

| Property             | Type    | Description                          |
|----------------------|---------|--------------------------------------|
| medication_id        | String  | Primary key (MED-xxx)                |
| medication_name      | String  | Generic drug name                    |
| drug_class           | String  | Pharmacological class                |
| route                | String  | Administration route                 |
| high_alert           | String  | Yes/No - high-alert medication flag  |

### 6. Diagnosis
**Source Table:** `dim_diagnoses` (Lakehouse)
**Primary Key:** `diagnosis_id`

| Property               | Type    | Description                        |
|------------------------|---------|------------------------------------|
| diagnosis_id           | String  | Primary key (DX-xxx)               |
| diagnosis_name         | String  | Clinical diagnosis name            |
| icd10_code             | String  | ICD-10 classification code         |
| typical_los_days       | Integer | Typical length of stay             |
| acuity_level           | Integer | Severity indicator                 |
| avg_daily_doc_events   | Integer | Average documentation events/day   |

---

## Relationship Types

| Relationship ID         | Name               | Source Entity      | Target Entity       | Cardinality | Description                                  |
|-------------------------|--------------------|--------------------|---------------------|-------------|----------------------------------------------|
| REL-001                 | assigned_to        | Nurse              | HospitalUnit        | Many:1      | Nurse is assigned to a unit                  |
| REL-002                 | admitted_to        | Patient            | HospitalUnit        | Many:1      | Patient is admitted to a unit                |
| REL-003                 | has_diagnosis      | Patient            | Diagnosis           | Many:Many   | Patient has one or more diagnoses            |
| REL-004                 | cares_for          | Nurse              | Patient             | Many:Many   | Nurse provides care for patient (per shift)  |
| REL-005                 | prescribes_for     | Medication         | Diagnosis           | Many:Many   | Medication commonly used for diagnosis       |

**Implementation Notes:**
- `REL-004` (cares_for) is a dynamic relationship derived from `fact_shifts` and `fact_patient_encounters` — nurse-patient assignment changes each shift.
- Static relationships (`REL-001`, `REL-002`, `REL-003`, `REL-005`) are derived from dimension table foreign keys.

---

## Contextualizations (Events — Eventhouse KQL Tables)

Contextualizations bind entities to time-series events. These are the core of Real-Time Intelligence analytics.

### CTX-001: DocumentationEvent
**Source Table:** `fact_documentation_events` (Eventhouse)
**Key Entity Bindings:** Nurse, Patient, DocumentationType

| Field                | Type     | Description                                     |
|----------------------|----------|-------------------------------------------------|
| event_id             | String   | Primary key (EVT-xxxx)                          |
| nurse_id             | String   | FK → Nurse entity                               |
| patient_id           | String   | FK → Patient entity                             |
| doc_type_id          | String   | FK → DocumentationType entity                   |
| shift_id             | String   | Reference to shift                              |
| timestamp            | DateTime | Event timestamp                                 |
| duration_minutes     | Integer  | Time spent on this documentation                |
| documentation_method | String   | Manual Entry, Barcode Scan, Copy-Forward, etc.  |
| is_duplicate_entry   | String   | Yes/No — flag for redundant documentation       |
| was_after_shift      | String   | Yes/No — after scheduled shift end              |
| ehr_screen_name      | String   | EHR screen used                                 |
| note_length_chars    | Integer  | Length of documentation text                     |
| interruption_count   | Integer  | Number of interruptions during documentation    |

**Analytical Value:** Core event stream. Enables documentation burden analysis, duplicate detection, after-shift charting patterns, and interruption impact.

### CTX-002: MedicationAdministration
**Source Table:** `fact_medication_administration` (Eventhouse)
**Key Entity Bindings:** Nurse, Patient, Medication

| Field                | Type     | Description                                     |
|----------------------|----------|-------------------------------------------------|
| admin_id             | String   | Primary key (ADM-xxx)                           |
| nurse_id             | String   | FK → Nurse entity                               |
| patient_id           | String   | FK → Patient entity                             |
| medication_id        | String   | FK → Medication entity                          |
| timestamp            | DateTime | Administration timestamp                        |
| scheduled_time       | DateTime | When med was scheduled                          |
| dose                 | String   | Dose administered                               |
| barcode_scanned      | String   | Yes/No                                          |
| time_to_document_min | Integer  | Time to complete MAR entry                      |

**Analytical Value:** Medication safety analysis, barcode compliance, documentation time per medication administration.

### CTX-003: VitalSignsRecording
**Source Table:** `fact_vital_signs` (Eventhouse)
**Key Entity Bindings:** Nurse, Patient

| Field                  | Type     | Description                                   |
|------------------------|----------|-----------------------------------------------|
| vital_id               | String   | Primary key (VS-xxx)                          |
| nurse_id               | String   | FK → Nurse entity                             |
| patient_id             | String   | FK → Patient entity                           |
| timestamp              | DateTime | Recording timestamp                           |
| systolic_bp            | Integer  | Systolic blood pressure                       |
| diastolic_bp           | Integer  | Diastolic blood pressure                      |
| heart_rate             | Integer  | Heart rate                                    |
| temperature_f          | Float    | Temperature in Fahrenheit                     |
| spo2_pct               | Integer  | Oxygen saturation percentage                  |
| respiratory_rate       | Integer  | Respiratory rate                              |
| pain_score             | Integer  | Pain scale 0-10                               |
| documentation_time_sec | Integer  | Time to document vital signs                  |

**Analytical Value:** Vital sign trends, documentation time analysis, frequency patterns by unit/acuity.

### CTX-004: AssessmentEvent
**Source Table:** `fact_assessments` (Eventhouse)
**Key Entity Bindings:** Nurse, Patient

| Field                | Type     | Description                                     |
|----------------------|----------|-------------------------------------------------|
| assessment_id        | String   | Primary key (ASM-xxx)                           |
| nurse_id             | String   | FK → Nurse entity                               |
| patient_id           | String   | FK → Patient entity                             |
| assessment_type      | String   | Head-to-Toe, Focused Reassessment               |
| timestamp            | DateTime | Assessment timestamp                            |
| duration_minutes     | Integer  | Time to complete assessment + documentation     |
| acuity_score         | Integer  | Patient acuity at assessment                    |
| fall_risk_score      | Integer  | Morse Fall Scale score                          |
| braden_score         | Integer  | Braden Scale for pressure injury risk           |
| pain_score           | Integer  | Pain score at assessment                        |

**Analytical Value:** Assessment frequency and duration by unit/acuity, correlation between patient complexity and documentation time.

### CTX-005: EHRInteraction
**Source Table:** `fact_ehr_interactions` (Eventhouse)
**Key Entity Bindings:** Nurse

| Field                | Type     | Description                                     |
|----------------------|----------|-------------------------------------------------|
| interaction_id       | String   | Primary key (INT-xxx)                           |
| nurse_id             | String   | FK → Nurse entity                               |
| timestamp            | DateTime | Interaction timestamp                           |
| action_type          | String   | Login, Documentation, Navigation, Search, etc.  |
| ehr_module           | String   | System module accessed                          |
| screen_name          | String   | Specific screen                                 |
| duration_seconds     | Integer  | Time on action                                  |
| click_count          | Integer  | Mouse clicks                                    |
| keystrokes           | Integer  | Keyboard entries                                |
| is_productive        | String   | Yes/No/Partial                                  |
| frustration_indicator| String   | Yes/No                                          |

**Analytical Value:** EHR usability metrics, friction analysis, non-productive time quantification, system navigation inefficiency detection.

### CTX-006: HandoffReport
**Source Table:** `fact_handoff_reports` (Eventhouse)
**Key Entity Bindings:** Nurse (outgoing), Nurse (incoming), Patient

| Field                         | Type     | Description                              |
|-------------------------------|----------|------------------------------------------|
| handoff_id                    | String   | Primary key (HO-xxx)                     |
| outgoing_nurse_id             | String   | FK → Nurse entity (sender)               |
| incoming_nurse_id             | String   | FK → Nurse entity (receiver)             |
| patient_id                    | String   | FK → Patient entity                      |
| timestamp                     | DateTime | Handoff timestamp                        |
| handoff_method                | String   | Verbal + Written, Verbal Only            |
| duration_minutes              | Integer  | Time for handoff                         |
| pending_tasks_count           | Integer  | Outstanding tasks communicated           |
| was_bedside                   | String   | Yes/No — bedside handoff                 |

**Analytical Value:** Handoff quality, duration patterns, information transfer completeness.

### CTX-007: RTLSLocationPing
**Source Table:** `rtls_location` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Nurse, HospitalUnit

| Field                         | Type     | Description                              |
|-------------------------------|----------|------------------------------------------|
| ping_id                       | String   | Primary key (LOC-xxxx)                   |
| nurse_id                      | String   | FK → Nurse entity                        |
| unit_id                       | String   | FK → HospitalUnit entity                 |
| timestamp                     | DateTime | Ping timestamp (~30 s cadence)           |
| zone_type                     | String   | Staff Area, Patient Room, Medication Room, Hallway, Treatment Area |
| zone_name                     | String   | Human-readable zone (e.g., Room 401)     |
| floor                         | Integer  | Building floor                           |
| room_id                       | String   | Room identifier                          |
| x_coord / y_coord             | Real     | BLE beacon coordinates                   |
| beacon_id                     | String   | Beacon hardware ID                       |
| signal_strength_dbm           | Integer  | RSSI signal strength                     |
| speed_mph                     | Real     | Estimated walking speed                  |
| is_moving                     | String   | Yes/No                                   |
| dwell_time_seconds            | Integer  | Cumulative seconds in current zone       |

**Analytical Value:** Bedside-vs-desk time ratio, walking distance, zone transition frequency, correlation of nursing station dwell time with documentation burden.

### CTX-008: EHRClickstream
**Source Table:** `ehr_clickstream` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Nurse

| Field                         | Type     | Description                              |
|-------------------------------|----------|------------------------------------------|
| click_id                      | String   | Primary key (CLK-xxxx)                   |
| nurse_id                      | String   | FK → Nurse entity                        |
| shift_id                      | String   | FK → Shift lookup                        |
| timestamp                     | DateTime | Sub-second precision                     |
| event_type                    | String   | Login, MouseClick, Keystroke, ScrollEvent, IdleStart, IdleEnd, PageLoad, BarcodeScan, AlertPopup, ErrorPopup, AutoPopulate, SystemEvent |
| target_element                | String   | UI element identifier                    |
| screen_name                   | String   | Current EHR screen                       |
| ehr_module                    | String   | Module (Documentation, Vitals, MAR, Orders, etc.) |
| action_context                | String   | Why the click happened                   |
| duration_ms                   | Integer  | Interaction duration in milliseconds     |
| idle_seconds_before           | Integer  | Seconds idle before this event           |
| error_code                    | String   | System error code if applicable          |
| session_id                    | String   | EHR login session                        |

**Analytical Value:** Clicks-per-task, idle-to-active ratio, documentation interruption frequency, error/retry friction, module time distribution, SmartPhrase adoption rate.

### CTX-009: NurseCallEvent
**Source Table:** `nurse_call_events` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Nurse, Patient, HospitalUnit

| Field                         | Type     | Description                              |
|-------------------------------|----------|------------------------------------------|
| call_id                       | String   | Primary key (CALL-xxx)                   |
| patient_id                    | String   | FK → Patient entity                      |
| nurse_id                      | String   | FK → Nurse entity (responder)            |
| unit_id                       | String   | FK → HospitalUnit entity                 |
| room_id                       | String   | Room identifier                          |
| timestamp                     | DateTime | Call initiation time                     |
| call_type                     | String   | CallButton, BedAlarm, FallAlert, VentAlarm, MonitorAlarm, InfusionAlarm, TraumaAlert |
| priority                      | String   | Routine, Urgent, Critical, Emergency     |
| source_device                 | String   | Bedside Console, Bed Sensor, Motion Sensor, Ventilator, Cardiac Monitor, IV Pump, ED System |
| reason                        | String   | Reason for call                          |
| response_time_seconds         | Integer  | Time to respond                          |
| resolution                    | String   | Addressed, Code Called                   |
| interrupted_documentation     | String   | Yes/No — was the nurse documenting?      |
| documentation_resume_delay_seconds | Integer | Seconds until documentation resumed  |
| escalated                     | String   | Yes/No                                   |
| escalated_to                  | String   | Nurse ID if escalated                    |

**Analytical Value:** Documentation interruption rate, response time vs. documentation delay, call frequency by unit type, escalation patterns, alarm fatigue correlation.

### CTX-010: BCMAScanEvent
**Source Table:** `bcma_scans` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Nurse, Patient, Medication

| Field                         | Type     | Description                              |
|-------------------------------|----------|------------------------------------------|
| scan_id                       | String   | Primary key (SCAN-xxx)                   |
| nurse_id                      | String   | FK → Nurse entity                        |
| patient_id                    | String   | FK → Patient entity                      |
| medication_id                 | String   | FK → Medication entity                   |
| unit_id                       | String   | FK → HospitalUnit entity                 |
| timestamp                     | DateTime | Scan timestamp (sub-second)              |
| scan_step                     | Integer  | 1 = Patient band, 2 = Med barcode       |
| scan_type                     | String   | PatientWristband, MedicationBarcode      |
| scan_result                   | String   | Success, Failure, Override               |
| barcode_value                 | String   | Scanned barcode string                   |
| retry_count                   | Integer  | Number of retries before this attempt    |
| override_reason               | String   | Reason for override (if applicable)      |
| time_to_complete_ms           | Integer  | Time for this scan action                |
| alert_triggered               | String   | Yes/No                                   |
| alert_type                    | String   | DrugInteraction, HighDoseAlert, AllergyWarning, TimingAlert |
| alert_action                  | String   | Acknowledged, Overridden                 |
| ehr_session_id                | String   | EHR session for clickstream correlation  |

**Analytical Value:** Scan failure rate, override frequency, time-per-medication-admin workflow, barcode error patterns, alert-during-scan fatigue.

### CTX-011: ClinicalAlert
**Source Table:** `clinical_alerts` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Nurse, Patient

| Field                         | Type     | Description                              |
|-------------------------------|----------|------------------------------------------|
| alert_id                      | String   | Primary key (ALT-xxx)                    |
| nurse_id                      | String   | FK → Nurse entity                        |
| patient_id                    | String   | FK → Patient entity                      |
| unit_id                       | String   | FK → HospitalUnit entity                 |
| timestamp                     | DateTime | Alert fired time                         |
| alert_source                  | String   | EHR-CDS (Clinical Decision Support)      |
| alert_type                    | String   | DrugInteraction, CriticalLab, FallRisk, SepsisScreen, AllergyWarning, DuplicateOrder, TraumaAlert, VentilatorBundle, InfusionAlert |
| alert_category                | String   | Medication Safety, Lab Results, Patient Safety, Sepsis, Care Bundle, Order Safety |
| severity                      | String   | Info, Warning, Critical                  |
| description                   | String   | Human-readable alert message             |
| suppressed                    | String   | Yes/No — was it auto-suppressed?         |
| was_actionable                | String   | Yes/No — did it require real action?     |
| action_taken                  | String   | Acknowledged, Dismissed, Overridden, Escalated, Auto-Suppressed |
| response_time_seconds         | Integer  | Time to respond                          |
| interrupted_task              | String   | What task the nurse was doing             |
| documentation_delay_seconds   | Integer  | Documentation time lost to this alert    |
| related_order_id              | String   | Associated order if applicable           |
| fatigue_score                 | Integer  | 1 (most actionable) to 5 (noise)        |

**Analytical Value:** Alert fatigue quantification, actionable-vs-noise ratio, documentation delay per alert, severity distribution, override risk analysis, suppression effectiveness.

---

## Data Storage Mapping

### Lakehouse (Delta Tables — Dimensional/Static Data)

| Delta Table Name            | Source CSV                    | Entity Mapping         |
|-----------------------------|-------------------------------|------------------------|
| dim_nurses                  | dim_nurses.csv                | Nurse entity           |
| dim_patients                | dim_patients.csv              | Patient entity         |
| dim_hospital_units          | dim_hospital_units.csv        | HospitalUnit entity    |
| dim_documentation_types     | dim_documentation_types.csv   | DocumentationType entity|
| dim_medications             | dim_medications.csv           | Medication entity      |
| dim_diagnoses               | dim_diagnoses.csv             | Diagnosis entity       |
| fact_shifts                 | fact_shifts.csv               | Shift lookup           |
| fact_patient_encounters     | fact_patient_encounters.csv   | Encounter lookup       |
| fact_care_plans             | fact_care_plans.csv           | Care plan lookup       |
| fact_burnout_surveys        | fact_burnout_surveys.csv      | Burnout analytics      |
| fact_patient_satisfaction   | fact_patient_satisfaction.csv | Satisfaction analytics |
| fact_documentation_quality  | fact_documentation_quality.csv| Quality analytics      |

### Eventhouse (KQL Tables — Event/Streaming Data)

| KQL Table Name                | Source CSV                        | Contextualization |
|-------------------------------|-----------------------------------|-------------------|
| documentation_events          | fact_documentation_events.csv     | CTX-001           |
| medication_administration     | fact_medication_administration.csv| CTX-002           |
| vital_signs                   | fact_vital_signs.csv              | CTX-003           |
| assessments                   | fact_assessments.csv              | CTX-004           |
| ehr_interactions              | fact_ehr_interactions.csv         | CTX-005           |
| handoff_reports               | fact_handoff_reports.csv          | CTX-006           |
| rtls_location                 | stream_rtls_location.csv          | CTX-007           |
| ehr_clickstream               | stream_ehr_clickstream.csv        | CTX-008           |
| nurse_call_events             | stream_nurse_call_events.csv      | CTX-009           |
| bcma_scans                    | stream_bcma_scans.csv             | CTX-010           |
| clinical_alerts               | stream_clinical_alerts.csv        | CTX-011           |

---

## Ontology Visualization

```
                           ┌──────────────┐
                           │  Diagnosis   │
                           └──────┬───────┘
                                  │ has_diagnosis
                                  ▼
┌──────────┐  assigned_to  ┌──────────────┐  admitted_to  ┌──────────────┐
│   Nurse  │──────────────▶│ HospitalUnit │◀─────────────│   Patient    │
└────┬─────┘               └──────────────┘               └──────┬───────┘
     │                                                           │
     │  cares_for                                                │
     └───────────────────────────┬───────────────────────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                   ▼
    ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐
    │ Documentation   │  │  Medication  │  │ Documentation  │
    │    Event        │  │ Admin Event  │  │    Type        │
    │   (CTX-001)     │  │  (CTX-002)   │  │   (entity)     │
    └─────────────────┘  └──────────────┘  └────────────────┘
              │
     ┌────────┼─────────┬──────────────┐
     ▼        ▼         ▼              ▼
┌─────────┐┌────────┐┌──────────┐┌──────────┐
│VitalSign││Assess- ││  EHR     ││ Handoff  │
│Recording││ment    ││Interact. ││ Report   │
│(CTX-003)││(CTX-004)│(CTX-005) ││(CTX-006) │
└─────────┘└────────┘└──────────┘└──────────┘

         ── Real-Time Streaming Layer ──

┌───────────┐┌──────────┐┌───────────┐┌──────────┐┌──────────┐
│   RTLS    ││Clickstrm ││Nurse Call ││  BCMA    ││ Clinical │
│ Location  ││  (EHR)   ││  Events   ││  Scans   ││  Alerts  │
│ (CTX-007) ││(CTX-008) ││ (CTX-009) ││(CTX-010) ││(CTX-011) │
└───────────┘└──────────┘└───────────┘└──────────┘└──────────┘
```

---

## Key Analytical Queries Enabled by This Ontology

### 1. Documentation Burden per Nurse per Shift
```kql
documentation_events
| where timestamp between (datetime(2026-02-23) .. datetime(2026-02-24))
| summarize total_doc_minutes = sum(duration_minutes),
            doc_count = count(),
            after_shift_count = countif(was_after_shift == "Yes"),
            duplicate_count = countif(is_duplicate_entry == "Yes")
  by nurse_id
| order by total_doc_minutes desc
```

### 2. Duplicate Documentation Waste
```kql
documentation_events
| where is_duplicate_entry == "Yes"
| summarize wasted_minutes = sum(duration_minutes),
            duplicate_events = count()
  by nurse_id, doc_type_id
| order by wasted_minutes desc
```

### 3. EHR Friction Analysis
```kql
ehr_interactions
| where is_productive == "No" or frustration_indicator == "Yes"
| summarize friction_seconds = sum(duration_seconds),
            friction_events = count(),
            total_extra_clicks = sum(click_count)
  by nurse_id, action_type
| order by friction_seconds desc
```

### 4. Burnout Correlation with Documentation Burden
```sql
-- Lakehouse SQL: Join burnout surveys with documentation event aggregates
SELECT b.nurse_id, b.emotional_exhaustion_score, b.burnout_risk_level,
       b.overtime_hours_last_2weeks, b.documentation_satisfaction,
       d.total_doc_minutes, d.after_shift_minutes
FROM fact_burnout_surveys b
JOIN (
    SELECT nurse_id,
           SUM(duration_minutes) as total_doc_minutes,
           SUM(CASE WHEN was_after_shift = 'Yes' THEN duration_minutes ELSE 0 END) as after_shift_minutes
    FROM fact_documentation_events
    GROUP BY nurse_id
) d ON b.nurse_id = d.nurse_id
ORDER BY b.emotional_exhaustion_score DESC
```

### 5. Patient Satisfaction vs. Documentation Burden by Unit
```sql
-- Lakehouse SQL: Compare unit-level patient satisfaction with documentation time
SELECT u.unit_name,
       AVG(s.overall_hospital_rating) as avg_satisfaction,
       AVG(s.nurse_communication_score) as avg_nurse_comm,
       AVG(d.doc_minutes_per_shift) as avg_doc_burden
FROM dim_hospital_units u
JOIN fact_patient_satisfaction s ON u.unit_id = s.unit_id
JOIN (
    SELECT unit_id, shift_id,
           SUM(duration_minutes) as doc_minutes_per_shift
    FROM fact_documentation_events
    GROUP BY unit_id, shift_id
) d ON u.unit_id = d.unit_id
GROUP BY u.unit_name
```

### 6. Bedside-vs-Desk Time Ratio (RTLS Streaming)
```kql
rtls_location
| summarize bedside_seconds = sumif(dwell_time_seconds, zone_type == "Patient Room"),
            desk_seconds = sumif(dwell_time_seconds, zone_type == "Staff Area"),
            hallway_seconds = sumif(dwell_time_seconds, zone_type == "Hallway")
  by nurse_id, bin(timestamp, 1h)
| extend bedside_pct = round(100.0 * bedside_seconds / (bedside_seconds + desk_seconds + hallway_seconds), 1)
| order by timestamp asc, nurse_id
```

### 7. Documentation Interruption Rate from Nurse Calls
```kql
nurse_call_events
| where interrupted_documentation == "Yes"
| summarize interruption_count = count(),
            avg_resume_delay = avg(documentation_resume_delay_seconds),
            max_resume_delay = max(documentation_resume_delay_seconds)
  by nurse_id, call_type
| order by interruption_count desc
```

### 8. EHR Clickstream Friction — Idle Gaps & Error Popups
```kql
ehr_clickstream
| where event_type in ("IdleStart", "ErrorPopup", "AlertPopup")
| summarize friction_events = count(),
            total_idle_before_sec = sum(idle_seconds_before)
  by nurse_id, ehr_module, bin(timestamp, 1h)
| order by friction_events desc
```

### 9. Alert Fatigue Score Distribution
```kql
clinical_alerts
| summarize alerts_total = count(),
            actionable = countif(was_actionable == "Yes"),
            suppressed = countif(suppressed == "Yes"),
            avg_fatigue = avg(fatigue_score),
            doc_delay_min = sum(documentation_delay_seconds) / 60.0
  by nurse_id
| extend actionable_pct = round(100.0 * actionable / alerts_total, 1)
| order by avg_fatigue desc
```

### 10. BCMA Scan Failure & Override Patterns
```kql
bcma_scans
| where scan_result != "Success"
| summarize failures = countif(scan_result == "Failure"),
            overrides = countif(scan_result == "Override"),
            avg_retries = avg(retry_count)
  by nurse_id, unit_id
| order by overrides desc
```

---

## Cross-Industry Reusability Pattern

The ontology follows a **Worker → Task → Documentation → System → Burden → Quality → Satisfaction** pattern:

| Ontology Concept      | Healthcare             | Legal            | Insurance          | Education          |
|-----------------------|------------------------|------------------|--------------------|--------------------|
| Worker Entity         | Nurse                  | Attorney         | Claims Adjuster    | Teacher            |
| Client Entity         | Patient                | Client           | Policyholder       | Student            |
| Unit Entity           | Hospital Unit          | Practice Group   | Claims Department  | School/Department  |
| Task Type Entity      | Documentation Type     | Filing Type      | Claim Form Type    | Report Type        |
| Core Event            | DocumentationEvent     | FilingEvent      | ClaimsEvent        | GradingEvent       |
| System Interaction    | EHRInteraction         | CaseSystemEvent  | ClaimsSystemEvent  | LMSInteraction     |
| Handoff Event         | HandoffReport          | CaseTransfer     | ClaimHandoff       | StudentHandoff     |
| Burnout Measure       | BurnoutSurvey          | BurnoutSurvey    | BurnoutSurvey      | BurnoutSurvey      |
| Quality Measure       | DocumentationQuality   | FilingQuality    | ClaimAccuracy      | GradingQuality     |
| Satisfaction Measure  | PatientSatisfaction    | ClientSatisfaction| PolicyholderSatisfaction | StudentSatisfaction |
| Location Tracking     | RTLSLocationPing       | BadgeSwipe        | FieldLocation         | CampusTracking      |
| UX Clickstream        | EHRClickstream         | CaseClickstream   | ClaimsClickstream     | LMSClickstream      |
| Interruption Event    | NurseCallEvent         | ClientCall        | UrgentClaim           | StudentIncident     |
| Compliance Scan       | BCMAScanEvent          | DocumentScan      | VerificationScan      | AttendanceScan      |
| Decision Alert        | ClinicalAlert          | ComplianceAlert   | FraudAlert            | GradingAlert        |

To adapt this ontology to another industry:
1. Rename entity types and properties to match industry terminology
2. Adjust the documentation types to reflect industry-specific forms
3. Modify system interaction events for the relevant software (EHR → Case Management → Claims System → LMS)
4. Keep the same relationship and contextualization patterns

---

## Implementation Steps

### Step 1: Upload Data to Fabric
1. Upload all CSV files to Lakehouse Files
2. Create Delta tables from dimension CSVs
3. Ingest event CSVs into Eventhouse KQL tables
4. Configure Real-Time Intelligence Eventstreams for the 5 streaming CSVs (`stream_*.csv`)

### Step 2: Create Ontology Package
1. Use the `fabriciq_ontology_accelerator` to define entity types, relationships, and contextualizations
2. Package into a `.iq` file following the accelerator format
3. See [ontology_package_guide.md](./ontology_package_guide.md) for detailed mapping

### Step 3: Generate Ontology
1. Run `Generate_Ontology_Data.ipynb` with the healthcare package
2. Run `Create_Ontology_from_Package.ipynb` to create the ontology item

### Step 4: Build Real-Time Intelligence Dashboards
1. Create KQL querysets for documentation burden analysis
2. Build Real-Time dashboards with the queries above
3. Connect Fabric IQ for natural language exploration
