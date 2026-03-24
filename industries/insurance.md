# Insurance

> **Reducing claims documentation burden so adjusters can focus on investigation and settlement, not paperwork**

---

## The Problem

Claims adjusters spend **50–70%** of their time on documentation: filling forms, requesting records, writing assessments, and responding to regulatory inquiries — instead of investigating and settling claims. A single auto claim can require **8–15 distinct documents** (FNOL, police report, damage estimate, rental authorization, settlement letter, subrogation demand), each in a different system with different approval workflows.

| Stat | Impact |
|---|---|
| **50–70%** of adjuster time on documentation | Less capacity for investigation and fair settlement |
| **8–15 forms** per auto claim lifecycle | Duplicate data entry across FNOL, estimate, settlement workflows |
| **22 days** average auto claim cycle time | Documentation bottlenecks add 5–8 days |
| **18%** of claims reopened due to documentation gaps | Incomplete initial documentation creates downstream rework |
| **$45,000** average cost per adjuster for turnover replacement | Documentation burden is the #2 cited reason for adjuster attrition |

---

## Ontology Mapping

| Core Concept | Insurance Equivalent |
|---|---|
| Worker Entity | `ClaimsAdjuster` / `Underwriter` |
| Client Entity | `Policyholder` / `Claimant` |
| Unit Entity | `ClaimsDepartment` / `Region` |
| Task Type Entity | `ClaimFormType` (FNOL, reserve estimate, settlement letter, subrogation) |
| Core Event | `ClaimsDocEvent` — form completion, assessment writing |
| System Interaction | `ClaimsSystemInteraction` — Guidewire, Duck Creek clicks |
| Handoff Event | `ClaimHandoff` — transfer between adjusters, escalation to SIU |
| Burnout Measure | `AdjusterWellnessSurvey` — caseload stress, overtime |
| Quality Measure | `ClaimAccuracy` — reopened claims, settlement accuracy |
| Satisfaction Measure | `PolicyholderSatisfaction` — CSAT, complaint rate |
| Location Tracking | `FieldInspectionLocation` — field vs office, travel time |
| UX Clickstream | `ClaimsSystemClickstream` — Guidewire usage patterns |
| Interruption Event | `UrgentClaim` — catastrophe event, litigation notice |
| Compliance Scan | `VerificationScan` — document authenticity, coverage verification |
| Decision Alert | `FraudAlert` — SIU flag, suspicious pattern, red flag indicator |

---

## Fabric Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         CentralData Workspace                              │
│                                                                            │
│  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │  Insurance_Data_  │  │ Insurance_         │  │ insurance_rt_store    │  │
│  │  Bronze           │  │ Datawarehouse      │  │ (Eventhouse)          │  │
│  │  (Lakehouse)      │  │                    │  │                       │  │
│  │  • 6 dim tables   │  │ • Star schema      │  │ • 5 KQL streaming     │  │
│  │  • 12 fact tables │  │ • DirectQuery → PBI│  │   tables              │  │
│  └──────────────────┘  └───────────────────┘  └────────────────────────┘  │
│                                                                            │
│  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │  InsuranceDoc     │  │ InsuranceQA        │  │ InsuranceDocBurden     │  │
│  │  BurdenOntology   │  │ (Data Agent)       │  │ (Operations Agent)     │  │
│  └──────────────────┘  └───────────────────┘  └────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_adjusters` | adjuster_id, name, role, department, region, license_state, hire_date, claim_authority_limit | 30 |
| `dim_policyholders` | policyholder_id, name, policy_type, effective_date, risk_tier, segment, state | 50 |
| `dim_claims_departments` | dept_id, name, region, claim_types_handled, headcount, avg_caseload | 5 |
| `dim_claim_form_types` | form_type_id, name, category, regulatory_requirement, avg_completion_time_min, applies_to_claim_types | 22 |
| `dim_coverage_types` | coverage_id, name, line_of_business, limit_range, deductible_range | 15 |
| `dim_service_providers` | provider_id, name, type (body_shop/medical/legal), region, avg_turnaround_days | 20 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_claims_doc_events` | event_id, adjuster_id, claim_id, form_type_id, start_time, duration_minutes, status, error_count, regulatory_flag | 200 |
| `fact_claim_lifecycle` | claim_id, policyholder_id, adjuster_id, fnol_date, assignment_date, reserve_date, settlement_date, close_date, total_doc_hours | 60 |
| `fact_adjuster_wellness` | survey_id, adjuster_id, dept_id, date, caseload_count, workload_perception, overtime_hours, burnout_risk_score | 30 |
| `fact_claim_accuracy` | accuracy_id, claim_id, adjuster_id, date, reopened_flag, settlement_variance_pct, audit_finding_count, documentation_completeness_pct | 60 |
| `fact_policyholder_satisfaction` | survey_id, policyholder_id, claim_id, date, csat_score, communication_rating, speed_rating, complaint_flag | 50 |
| `fact_underwriting_docs` | doc_id, underwriter_id, policy_id, date, doc_type, risk_assessment_time_min, form_count, approval_status | 40 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_claim_status_changes` | change_id, claim_id, adjuster_id, timestamp, from_status, to_status, documentation_required, time_in_previous_status_hours | 180 |
| `fact_claims_system_clicks` | click_id, adjuster_id, timestamp, module, screen, action, duration_ms, idle_before_ms, error_code | 300 |
| `fact_field_inspections` | inspection_id, adjuster_id, claim_id, timestamp, location, travel_time_min, inspection_time_min, photo_count, report_time_min | 45 |
| `fact_claim_handoffs` | handoff_id, claim_id, from_adjuster_id, to_adjuster_id, timestamp, reason, doc_transfer_time_min | 25 |
| `fact_fraud_alerts` | alert_id, adjuster_id, claim_id, timestamp, alert_type, severity, action_taken, investigation_time_min | 35 |
| `fact_verification_scans` | scan_id, adjuster_id, claim_id, timestamp, scan_type, document_source, result, discrepancy_flag | 70 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_claim_status_changes` | Claims management system | claim_id, adjuster_id, timestamp, from_status, to_status, trigger, auto_vs_manual | Stage transitions and bottleneck detection |
| `stream_field_adjuster_location` | Mobile GPS / badge | ping_id, adjuster_id, timestamp, lat, lon, location_type, is_at_inspection, dwell_time_min | Field inspection routing and travel efficiency |
| `stream_claims_system_clicks` | Guidewire / Duck Creek | click_id, adjuster_id, timestamp, module, screen, action, duration_ms, error_code | UI friction, form abandonment, error patterns |
| `stream_fraud_alerts` | SIU analytics engine | alert_id, claim_id, timestamp, alert_type, risk_score, pattern_type, related_claims_count | Fraud pattern flags and ring detection |
| `stream_customer_contacts` | Call center / self-service portal | contact_id, policyholder_id, claim_id, timestamp, channel, topic, sentiment, wait_time_sec | Inbound inquiry volume and complaint spikes |

---

## Use Cases — Detailed

### UC-1: Claims Documentation Burden Analysis

**Problem:** Adjusters handle a mix of claim types (auto, property, liability, workers' comp) — each with different documentation requirements. There's no visibility into which claim categories carry the highest per-adjuster paperwork burden, or whether documentation time scales linearly with claim severity.

**What the Platform Measures:**
- Documentation minutes per claim by claim type and severity
- Form count per claim lifecycle (FNOL → reserve → estimate → settlement → close)
- Adjuster time split: investigation vs documentation vs communication
- Documentation burden variance between adjusters on similar claims
- Overtime hours driven by documentation catch-up after claim surges

**Ontology Traversal:**
> _"Show me the average documentation time per auto liability claim for adjusters in the Southeast region compared to Northeast"_
>
> `ClaimsAdjuster → assigned_to → ClaimsDepartment (Southeast)` → `handles → Claim (type = auto liability)` → `ClaimsDocEvent` contextualizations

**Sample SQL Query — Documentation Burden by Claim Type:**
```sql
SELECT ct.name AS claim_type,
       COUNT(DISTINCT cl.claim_id) AS total_claims,
       AVG(cl.total_doc_hours) AS avg_doc_hours,
       AVG(DATEDIFF(day, cl.fnol_date, cl.close_date)) AS avg_cycle_days,
       SUM(cl.total_doc_hours) / COUNT(DISTINCT cl.adjuster_id) AS doc_hours_per_adjuster
FROM fact_claim_lifecycle cl
JOIN dim_coverage_types ct ON cl.coverage_type_id = ct.coverage_id
GROUP BY ct.name
ORDER BY avg_doc_hours DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Doc hours per claim (auto) | > 4 hours | > 8 hours |
| Doc hours per claim (property) | > 6 hours | > 12 hours |
| Adjuster overtime (weekly) | > 5 hours | > 10 hours |
| Documentation completeness | < 90% | < 80% |

---

### UC-2: First Notice of Loss (FNOL) Optimization

**Problem:** The critical window between FNOL receipt and first adjuster contact directly impacts customer satisfaction and claim cost (delayed contact → inflated repair costs, rental extensions, attorney involvement). Much of the delay is hidden documentation: assigning the claim, verifying coverage, opening the file in the system, and completing initial notes.

**What the Platform Measures:**
- FNOL-to-contact time (total elapsed) decomposed into: system processing, documentation, and actual investigation
- Coverage verification time by policy complexity
- Initial documentation time (opening notes, reserve setting, assignment)
- Channel-specific FNOL handling time (phone vs digital vs agent-reported)
- Correlation between FNOL speed and eventual claim cost

**Sample KQL Query — Real-Time FNOL Pipeline:**
```kql
stream_claim_status_changes
| where to_status == "Assigned" and timestamp > ago(4h)
| extend fnol_to_assign_min = datetime_diff('minute', timestamp, fnol_timestamp)
| summarize
    AvgAssignmentMinutes = avg(fnol_to_assign_min),
    PendingFNOLs = countif(to_status == "FNOL_Received"),
    AssignedCount = count()
  by bin(timestamp, 15m)
| render timechart
```

**Data Agent Example Questions:**
- _"What's the average FNOL-to-contact time for auto claims this week?"_
- _"Which adjusters have the fastest initial documentation turnaround?"_
- _"Show me FNOL bottleneck claims — assigned but no contact after 24 hours"_

---

### UC-3: Catastrophe (CAT) Event Response

**Problem:** During catastrophe events (hurricanes, wildfires, hailstorms), claim volume spikes 10–50x. Adjusters are overwhelmed, and documentation often gets deferred — leading to backlogs that persist for months. CAT response is a multiplier on the documentation burden problem.

**What the Platform Measures:**
- Real-time claim volume by CAT event, region, and claim type
- Per-adjuster caseload during CAT surge vs normal baseline
- Documentation backlog (claims with incomplete documentation > 48 hours)
- Field inspection queue and travel time during CAT events
- Temporary adjuster utilization (how quickly deployed, documentation ramp-up time)

**Sample KQL Query — CAT Surge Monitoring:**
```kql
stream_claim_status_changes
| where timestamp > ago(24h)
| summarize ClaimCount = count() by bin(timestamp, 1h), region
| extend IsSpike = ClaimCount > 3 * avg(ClaimCount)
| where IsSpike
| order by ClaimCount desc
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Claims per adjuster per day | > 15 (3x normal) | > 25 (5x normal) |
| Documentation backlog (> 48h) | > 10 claims | > 25 claims |
| Field inspection queue | > 8 pending | > 20 pending |
| Customer wait time (call center) | > 15 min | > 30 min |

---

### UC-4: Fraud Investigation Documentation

**Problem:** When SIU (Special Investigations Unit) flags a claim for fraud, the adjuster must complete additional documentation: investigation notes, evidence tracking, witness statements, and SIU referral forms. This documentation overhead often delays the settlement of legitimate claims by the same adjuster.

**What the Platform Measures:**
- SIU referral documentation time (hours per fraud investigation)
- Impact on non-fraud claims (settlement delay for other claims on adjuster's desk)
- Fraud alert-to-resolution cycle time
- False positive rate and documentation waste (unfounded investigations)
- SIU documentation overlap with regular claim documentation

**Sample SQL Query — Fraud Documentation Impact:**
```sql
SELECT a.name AS adjuster,
       COUNT(DISTINCT fa.alert_id) AS fraud_referrals,
       AVG(fa.investigation_time_min) AS avg_investigation_min,
       AVG(cl.total_doc_hours) AS avg_claim_doc_hours,
       -- Settlement delay for non-fraud claims
       AVG(CASE WHEN cl.claim_id NOT IN (SELECT claim_id FROM fact_fraud_alerts)
           THEN DATEDIFF(day, cl.reserve_date, cl.settlement_date)
       END) AS avg_non_fraud_settlement_days
FROM dim_adjusters a
JOIN fact_fraud_alerts fa ON a.adjuster_id = fa.adjuster_id
JOIN fact_claim_lifecycle cl ON a.adjuster_id = cl.adjuster_id
GROUP BY a.name
HAVING COUNT(DISTINCT fa.alert_id) > 0
ORDER BY fraud_referrals DESC;
```

---

### UC-5: Underwriting Documentation Efficiency

**Problem:** Underwriters spend significant time completing risk assessment forms, loss-run analyses, and pricing documentation — much of which duplicates information already in the submission. Complex commercial policies can require 20+ pages of underwriting documentation.

**What the Platform Measures:**
- Underwriting documentation time by policy type and complexity tier
- Risk assessment form completion time vs actual risk analysis time
- Duplicative fields between submission and underwriting documentation
- Quote-to-bind cycle time decomposed into documentation vs decision time
- Underwriting accuracy: correlation between documentation thoroughness and loss ratio

**Data Agent Example Questions:**
- _"Which commercial lines have the highest underwriting documentation burden?"_
- _"Show me the quote-to-bind time trend for workers' comp policies"_
- _"Are underwriters with lower documentation time seeing worse loss ratios?"_

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (avg claim cycle time, CSAT, doc hours/claim), regional heat map | _"How is claims operations performing?"_ |
| **Documentation Burden** | Doc time by claim type, form completion rates, adjuster burden ranking | _"Where is the paperwork heaviest?"_ |
| **Claim Pipeline** | Funnel by status, bottleneck stages, FNOL-to-contact trend | _"Where do claims get stuck?"_ |
| **Adjuster Wellness** | Caseload vs burnout scores, overtime trends, attrition risk | _"Which adjusters need workload relief?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **Claim Volume** | `stream_claim_status_changes` | New claims, status transitions, backlog |
| **Field Operations** | `stream_field_adjuster_location` | Adjuster locations, inspection queue |
| **System Usage** | `stream_claims_system_clicks` | Guidewire friction, form completion time |
| **Fraud Watch** | `stream_fraud_alerts` | Active flags, ring detection, SIU queue |
| **Customer Pulse** | `stream_customer_contacts` | Call volume, sentiment, complaint spikes |
