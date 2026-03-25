# Healthcare Nursing Documentation Burden — Demo Dataset

> **Disclaimer:** All data in this directory is **entirely fictional and synthetic**. Names, email addresses, phone numbers, and company references do not represent real individuals or organizations. Phone numbers use the `555-0xxx` reserved range. Email addresses use `.example` domains per [RFC 2606](https://www.rfc-editor.org/rfc/rfc2606). Any resemblance to real persons or entities is coincidental.



## Problem Statement

> Nurses complete patient care but face hours of duplicative documentation, feeling more like data clerks than caregivers. Documentation burden strongly correlates with clinician burnout in studies, directly harming patient care quality and satisfaction. Industry surveys reveal widespread unproductive charting practices tied to nurse well-being and retention risks.

---

## Cross-Industry Reusability

This demo follows a **universal documentation-burden pattern** that applies across industries:

| Layer | Healthcare (This Demo) | Legal | Insurance | Education |
|---|---|---|---|---|
| **Worker** | Nurse | Attorney | Claims Adjuster | Teacher |
| **Core Task** | Patient Care | Client Representation | Claim Processing | Student Instruction |
| **Documentation** | EHR Charting | Case Notes / Filings | Claim Forms / Notes | Grading / IEPs |
| **System** | EHR (Epic, Cerner) | Case Mgmt Software | Claims Platform | SIS / LMS |
| **Burden Signal** | Chart time vs care time | Billable vs admin hours | Processing time | Prep vs teaching time |
| **Quality Impact** | Patient satisfaction (HCAHPS) | Case outcomes | Claim accuracy | Student outcomes |
| **Burnout Signal** | Maslach Burnout Inventory | Attrition rate | Error rate | Teacher turnover |

The ontology, data model, and analytics patterns can be adapted to any of these industries by renaming entities and adjusting domain-specific fields.

---

## Nursing Workflow — Complete Guide

### What Does a Nurse Actually Do in a 12-Hour Shift?

A typical bedside nurse (RN) works a **12-hour shift** (e.g., 7:00 AM – 7:30 PM) and is responsible for **4–6 patients** on a Medical-Surgical unit, **1–2 patients** in the ICU, or a **variable number** in the Emergency Department. Here is the detailed workflow:

---

### Phase 1: Pre-Shift Preparation (6:30 – 7:00 AM)

| Activity | Documentation Required | Time |
|---|---|---|
| Review patient charts in EHR | None (reading) | 15–30 min |
| Receive **SBAR handoff** from outgoing nurse | Handoff report acknowledgment | 3–5 min per patient |

**SBAR** = Situation, Background, Assessment, Recommendation — the standardized handoff format.

---

### Phase 2: Start of Shift — Initial Assessments (7:00 – 8:30 AM)

| Activity | Documentation Required | Time per Patient |
|---|---|---|
| **Head-to-toe assessment** (neuro, cardiac, respiratory, GI, skin, musculoskeletal, psychosocial) | Comprehensive assessment flowsheet | 15–25 min |
| **Vital signs** (BP, HR, Temp, SpO2, RR, Pain) | Vital signs flowsheet | 3–5 min |
| **Safety assessment** (fall risk — Morse scale, Braden skin risk) | Risk assessment forms | 5–8 min |
| **Review & acknowledge physician orders** | Order acknowledgment in EHR | 2–3 min per order |
| **Verify IV lines, drains, catheters** | Line/drain assessment form | 3–5 min |
| **Review medication schedule** | MAR review (no entry yet) | 2–3 min |

**Total Phase 2 documentation: ~35–50 min per patient × 4–6 patients = 2.5–5 hours**

---

### Phase 3: Morning Medication Pass & Rounds (8:00 – 10:00 AM)

| Activity | Documentation Required | Time per Patient |
|---|---|---|
| **Medication administration** (scan patient, scan med, administer, document) | MAR entry per medication | 3–5 min per med |
| **Insulin/blood sugar management** | Blood glucose flowsheet + MAR | 5–8 min |
| **IV medication/drip management** | IV flowsheet entries | 3–5 min |
| **Physician rounding** (report to attending/team) | Update orders, care plan revisions | 5–10 min |
| **Patient education** (explain meds, procedures, self-care) | Education documentation form | 5–10 min |

A patient on 8+ medications means **24–40 minutes just for med documentation** per patient.

---

### Phase 4: Mid-Morning Care & Ongoing Monitoring (10:00 AM – 12:00 PM)

| Activity | Documentation Required | Time |
|---|---|---|
| **Repeat vital signs** (q4h or q2h depending on acuity) | Vital signs flowsheet | 3–5 min per patient |
| **Wound care / dressing changes** | Wound assessment form, measurements, photos | 10–15 min per wound |
| **Intake & Output (I&O)** tracking | I&O flowsheet | 2–3 min per entry |
| **Progress notes** (SOAP or narrative) | Progress note in EHR | 10–15 min per patient |
| **Respond to patient call lights** | Intervention documentation | 2–5 min per event |
| **Coordinate with ancillary services** (PT, OT, social work, dietary) | Interdisciplinary note updates | 5–10 min |

---

### Phase 5: Afternoon Care (12:00 – 4:00 PM)

| Activity | Documentation Required | Time |
|---|---|---|
| **Noon medication pass** | MAR entries | 3–5 min per med per patient |
| **Reassessments** (focused, not full head-to-toe) | Focused assessment flowsheet | 8–12 min per patient |
| **New admission** (if bed opens) | Full admission assessment, history, medication reconciliation | 45–90 min |
| **Discharge** (if patient leaving) | Discharge instructions, med reconciliation, education, follow-up | 30–60 min |
| **Procedure documentation** (catheter insertion, NG tube, etc.) | Procedure note | 10–15 min each |
| **Lab/test result review & notification** | Acknowledgment, notification note | 3–5 min |

---

### Phase 6: Late Afternoon Wrap-Up (4:00 – 6:00 PM)

| Activity | Documentation Required | Time |
|---|---|---|
| **Evening vital signs** | Vital signs flowsheet | 3–5 min per patient |
| **Evening medication pass** | MAR entries | 3–5 min per med per patient |
| **Update care plans** for next shift | Care plan addendum/revision | 5–10 min per patient |
| **Complete overdue documentation** ("catch-up charting") | Various | 30–60 min |
| **Prepare SBAR handoff report** | Handoff documentation | 3–5 min per patient |

---

### Phase 7: End of Shift (6:00 – 7:30 PM)

| Activity | Documentation Required | Time |
|---|---|---|
| **Give SBAR handoff** to incoming nurse | Handoff report | 3–5 min per patient |
| **Final chart review** (ensure all documentation is complete) | Chart completion audit | 15–30 min |
| **Late charting** (anything missed during shift) | Various | 0–30 min |

---

### Documentation Burden Summary

| Documentation Type | Avg Time/Entry | Frequency/Shift (4 patients) | Total Time |
|---|---|---|---|
| Initial head-to-toe assessment | 20 min | 4–6 | 80–120 min |
| Vital signs documentation | 4 min | 16–24 (q4h × 4–6 pts) | 64–96 min |
| Medication administration (MAR) | 4 min | 20–40 meds total | 80–160 min |
| Progress notes (SOAP) | 12 min | 4–8 | 48–96 min |
| Care plan updates | 8 min | 4–6 | 32–48 min |
| Flowsheet entries (I&O, lines, drains) | 3 min | 16–24 | 48–72 min |
| Order acknowledgment | 3 min | 8–15 | 24–45 min |
| Handoff report (SBAR) | 4 min | 4–6 (end of shift) | 16–24 min |
| Patient education | 7 min | 4–8 | 28–56 min |
| Risk assessments (fall, skin) | 6 min | 4–6 | 24–36 min |
| Admission/discharge documentation | 45 min | 0–2 | 0–90 min |
| **TOTAL** | | | **444–843 min (7.4–14 hrs)** |

> **Key Insight**: Documentation can consume **60–100%+ of a 12-hour shift**, forcing nurses to chart during patient care, skip breaks, or chart after shift (unpaid overtime). The typical nurse spends **4–6 hours per shift on documentation** with significant overtime charting.

---

### Key Documentation Systems & Forms

| System/Form | Purpose | Charting Frequency |
|---|---|---|
| **EHR** (Epic, Cerner, Meditech) | Central electronic health record | Continuous |
| **MAR** (Medication Administration Record) | Tracks every medication given | Per medication event |
| **Flowsheets** | Vital signs, I&O, pain, assessments | Every 2–4 hours |
| **SOAP Notes** | Subjective, Objective, Assessment, Plan narrative | 1–2 per patient per shift |
| **Care Plans** | Nursing diagnoses, goals, interventions | Updated each shift |
| **SBAR Reports** | Standardized handoff communication | Start/end of each shift |
| **Risk Assessments** | Morse Fall Scale, Braden Scale, pain scales | Admission + each shift |
| **Procedure Notes** | Document any procedure performed | Per procedure |
| **Discharge Instructions** | Patient going-home education | At discharge |
| **Incident Reports** | Falls, medication errors, adverse events | Per incident |

---

### Burnout Indicators in Nursing

| Indicator | Measurement | Data Source |
|---|---|---|
| Emotional Exhaustion | Maslach Burnout Inventory (MBI) score 0–54 | Survey |
| Depersonalization | MBI score 0–30 | Survey |
| Personal Accomplishment | MBI score 0–48 (lower = worse) | Survey |
| Overtime hours | Hours charted after shift end | EHR login data |
| Missed breaks | Break documentation gaps | Shift records |
| Sick days | Unplanned absences | HR records |
| Turnover intent | Self-reported intent to leave | Survey |
| Documentation after-hours | EHR activity after shift clock-out | EHR audit logs |

---

### Patient Satisfaction Metrics (HCAHPS)

| Domain | Question Theme | Link to Documentation |
|---|---|---|
| Communication with Nurses | "How often did nurses listen carefully?" | Less face time = lower scores |
| Responsiveness of Staff | "How quickly did you get help?" | Documentation delays response |
| Pain Management | "Was your pain well controlled?" | Delayed documentation = delayed care |
| Communication about Medicines | "Were side effects explained?" | Rushed education documentation |
| Discharge Information | "Did you get written discharge info?" | Incomplete discharge docs |
| Overall Rating | "Rate this hospital 0–10" | Composite of all interactions |

---

## Data Model Overview

### Dimensional Tables (Lakehouse — Delta Tables)

| Table | Description | Key Fields |
|---|---|---|
| `dim_nurses` | Nurse profiles and credentials | nurse_id, name, unit, role, years_experience, certification |
| `dim_patients` | Patient demographics | patient_id, age, gender, acuity_level, primary_diagnosis |
| `dim_hospital_units` | Hospital unit information | unit_id, unit_name, unit_type, bed_count, nurse_patient_ratio |
| `dim_documentation_types` | Documentation categories | doc_type_id, name, category, avg_time_minutes, is_required |
| `dim_medications` | Medication reference | medication_id, name, drug_class, route, schedule_type |
| `dim_diagnoses` | Diagnosis reference | diagnosis_id, icd10_code, name, category, typical_los_days |

### Event/Fact Tables (Eventhouse — KQL Tables for Real-Time Intelligence)

| Table | Description | Key Fields |
|---|---|---|
| `fact_documentation_events` | **Core table** — every charting action | event_id, nurse_id, patient_id, doc_type, timestamp, duration_min, documentation_method |
| `fact_ehr_interactions` | EHR system usage telemetry | interaction_id, nurse_id, action_type, screen_name, timestamp, duration_seconds |
| `fact_medication_administration` | MAR entries | admin_id, nurse_id, patient_id, medication_id, timestamp, status |
| `fact_vital_signs` | Vital sign recordings | record_id, nurse_id, patient_id, timestamp, bp, hr, temp, spo2, rr, pain |
| `fact_assessments` | Clinical assessments | assessment_id, nurse_id, patient_id, assessment_type, timestamp, findings |
| `fact_handoff_reports` | Shift handoff records | handoff_id, outgoing_nurse_id, incoming_nurse_id, patient_id, timestamp |

### Analytics/Derived Tables

| Table | Description | Key Fields |
|---|---|---|
| `fact_shifts` | Shift schedule and actuals | shift_id, nurse_id, date, scheduled_start/end, actual_start/end, overtime_min |
| `fact_patient_encounters` | Patient stay records | encounter_id, patient_id, unit_id, admit_date, discharge_date, los_days |
| `fact_burnout_surveys` | Burnout assessment scores | survey_id, nurse_id, date, emotional_exhaustion, depersonalization, accomplishment |
| `fact_patient_satisfaction` | HCAHPS-style scores | satisfaction_id, patient_id, unit_id, nurse_communication, responsiveness, overall_rating |
| `fact_documentation_quality` | Documentation audit results | audit_id, nurse_id, patient_id, completeness_pct, timeliness_score, accuracy_score |

---

## Files in This Dataset

```
datasets/healthcare_nursing_documentation/
├── README.md                              ← You are here
├── ontology_design.md                     ← Fabric IQ ontology mapping
├── data/
│   ├── dim_nurses.csv
│   ├── dim_patients.csv
│   ├── dim_hospital_units.csv
│   ├── dim_documentation_types.csv
│   ├── dim_medications.csv
│   ├── dim_diagnoses.csv
│   ├── fact_shifts.csv
│   ├── fact_patient_encounters.csv
│   ├── fact_documentation_events.csv
│   ├── fact_medication_administration.csv
│   ├── fact_vital_signs.csv
│   ├── fact_assessments.csv
│   ├── fact_care_plans.csv
│   ├── fact_ehr_interactions.csv
│   ├── fact_handoff_reports.csv
│   ├── fact_burnout_surveys.csv
│   ├── fact_patient_satisfaction.csv
│   └── fact_documentation_quality.csv
```

## Key Analytical Questions This Dataset Answers

1. **How much time do nurses spend documenting vs. providing direct care?**
2. **Which documentation types consume the most time and are most duplicative?**
3. **Is there a correlation between documentation burden and nurse burnout scores?**
4. **Do units with higher documentation burden have lower patient satisfaction?**
5. **How much overtime is driven by after-shift charting?**
6. **Which EHR workflows cause the most friction (clicks, screen time)?**
7. **Can AI-assisted documentation reduce charting time without sacrificing quality?**
8. **What is the financial impact of documentation-driven nurse turnover?**

## Fabric Components Mapping

| Component | Role in Demo |
|---|---|
| **Fabric Real-Time Intelligence (Eventhouse)** | Stream documentation events, EHR interactions, vital signs in real-time |
| **Fabric IQ (Ontology)** | Define Nurse, Patient, Unit entities and their relationships; contextualize events |
| **Foundry IQ / AI Agents** | Natural language querying: "Show me nurses with highest charting overtime this week" |
| **Work IQ** | Workflow automation to flag burnout risk, auto-generate handoff summaries |
| **Power BI** | Dashboards for documentation burden analysis, burnout correlation, patient satisfaction |
