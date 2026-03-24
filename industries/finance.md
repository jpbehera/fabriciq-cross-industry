# Finance (Banking & Wealth Management)

> **Reducing the KYC/AML documentation burden so advisors can focus on clients, not compliance paperwork**

---

## The Problem

Financial advisors, loan officers, and compliance analysts spend **40–60%** of their time on regulatory documentation, KYC/AML paperwork, and internal reporting instead of client advisory and deal execution. A single client onboarding can require **15–25 forms** spanning KYC, AML, suitability, and account opening — many with overlapping fields across regulators (SEC, FINRA, OCC, state banking authorities).

| Stat | Impact |
|---|---|
| **40–60%** of advisor time consumed by compliance documentation | Less time for client relationships and revenue generation |
| **$25,000–$50,000** average cost per regulatory finding | Documentation gaps during exams are the #1 source of findings |
| **15–25 forms** per client onboarding | Duplicative fields across KYC, AML, suitability questionnaires |
| **72-hour** average KYC turnaround | Clients abandon onboarding when paperwork takes too long |
| **$3.6B** annual global KYC compliance spend (industry) | Rising regulatory requirements compound annually |

---

## Ontology Mapping

| Core Concept | Finance Equivalent |
|---|---|
| Worker Entity | `FinancialAdvisor` / `LoanOfficer` / `ComplianceAnalyst` |
| Client Entity | `Client` / `Account` |
| Unit Entity | `Branch` / `BusinessUnit` |
| Task Type Entity | `DocumentationType` (KYC forms, SARs, loan apps, trade confirmations) |
| Core Event | `ComplianceDocEvent` — filing time, form type, regulatory body |
| System Interaction | `CoreBankingInteraction` — clicks in Fiserv, FIS, Temenos |
| Handoff Event | `CaseEscalation` — loan handoff between underwriting stages |
| Burnout Measure | `AdvisorWellnessSurvey` — workload perception, overtime |
| Quality Measure | `DocumentAccuracy` — error rate, rejection rate, audit findings |
| Satisfaction Measure | `ClientNPS` — net promoter score, complaint rate |
| Location Tracking | `BranchPresence` — in-office vs remote, meeting room usage |
| UX Clickstream | `CoreBankingClickstream` — navigation patterns, error screens |
| Interruption Event | `UrgentClientRequest` — unscheduled calls, escalations |
| Compliance Scan | `KYCVerificationScan` — identity checks, document verification |
| Decision Alert | `RegulatoryAlert` — AML flag, SAR trigger, limit breach |

---

## Fabric Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         CentralData Workspace                              │
│                                                                            │
│  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │  Finance_Data_    │  │ Finance_           │  │ finance_rt_store      │  │
│  │  Bronze           │  │ Datawarehouse      │  │ (Eventhouse)          │  │
│  │  (Lakehouse)      │  │                    │  │                       │  │
│  │  • 6 dim tables   │  │ • Star schema      │  │ • 5 KQL streaming     │  │
│  │  • 12 fact tables │  │ • DirectQuery → PBI│  │   tables              │  │
│  └──────────────────┘  └───────────────────┘  └────────────────────────┘  │
│                                                                            │
│  ┌──────────────────┐  ┌───────────────────┐  ┌────────────────────────┐  │
│  │  FinanceDocBurden │  │ FinanceQA          │  │ FinanceDocBurden       │  │
│  │  Ontology         │  │ (Data Agent)       │  │ (Operations Agent)     │  │
│  └──────────────────┘  └───────────────────┘  └────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_advisors` | advisor_id, name, role, branch_id, license_type, hire_date, AUM, certifications | 25 |
| `dim_clients` | client_id, name, account_type, risk_profile, onboarding_date, segment, relationship_manager | 40 |
| `dim_branches` | branch_id, name, region, state, branch_type, headcount, compliance_rating | 5 |
| `dim_document_types` | doc_type_id, name, category, regulatory_body, required_fields, avg_completion_time_min | 20 |
| `dim_products` | product_id, name, category (loan/investment/deposit), risk_tier, regulatory_class | 15 |
| `dim_regulations` | regulation_id, name, body (SEC/FINRA/OCC), effective_date, documentation_requirements | 12 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_compliance_doc_events` | event_id, advisor_id, client_id, doc_type_id, start_time, duration_minutes, status, error_count, regulatory_body | 150 |
| `fact_loan_processing` | loan_id, officer_id, client_id, stage, start_date, stage_duration_days, doc_count, rejection_reason | 45 |
| `fact_advisor_wellness` | survey_id, advisor_id, branch_id, date, workload_score, overtime_hours, burnout_risk, admin_burden_perception | 25 |
| `fact_document_quality` | quality_id, doc_type_id, advisor_id, date, error_rate, rejection_rate, audit_finding_count, completeness_score | 60 |
| `fact_client_satisfaction` | survey_id, client_id, advisor_id, date, nps_score, responsiveness_rating, onboarding_experience, complaint_flag | 40 |
| `fact_exam_readiness` | exam_id, branch_id, regulation_id, date, doc_completion_pct, gap_count, days_to_exam, prep_hours_spent | 15 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_kyc_verifications` | kyc_id, advisor_id, client_id, timestamp, verification_type, source, result, time_to_complete_min | 80 |
| `fact_trade_compliance` | trade_id, advisor_id, client_id, timestamp, trade_type, pre_trade_doc_time_min, post_trade_doc_time_min | 60 |
| `fact_core_banking_interactions` | interaction_id, advisor_id, timestamp, system_module, action, click_count, idle_seconds, error_code | 200 |
| `fact_case_escalations` | escalation_id, advisor_id, client_id, from_stage, to_stage, timestamp, reason, doc_delay_minutes | 30 |
| `fact_regulatory_alerts` | alert_id, advisor_id, client_id, timestamp, alert_type, severity, action_taken, response_time_min | 45 |
| `fact_branch_presence` | presence_id, advisor_id, branch_id, date, arrival_time, departure_time, remote_hours, meeting_hours | 75 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_trading_events` | Trading platform | trade_id, advisor_id, client_id, timestamp, instrument, action, pre_trade_check, post_trade_filing_status | Trade execution + compliance filing gap |
| `stream_core_banking_clicks` | Core banking system | click_id, advisor_id, timestamp, module, screen, action, duration_ms, idle_before_ms, error_code | UI friction and navigation dead-ends |
| `stream_client_interactions` | CRM / phone system | interaction_id, advisor_id, client_id, timestamp, channel, duration_sec, topic, outcome | Client-facing time vs admin time ratio |
| `stream_compliance_alerts` | AML/fraud detection | alert_id, advisor_id, client_id, timestamp, alert_type, risk_score, suppressed, action_taken | Alert fatigue and response patterns |
| `stream_branch_presence` | Badge / VPN system | ping_id, advisor_id, branch_id, timestamp, location_type, zone, is_in_meeting | Office presence patterns, remote work trends |

---

## Use Cases — Detailed

### UC-1: KYC/AML Documentation Burden

**Problem:** A single client onboarding requires completing KYC forms (CIP, CDD, EDD), AML questionnaires, suitability assessments, and account opening documents — each with overlapping fields. Advisors re-enter the same client information 4–6 times across different forms.

**What the Platform Measures:**
- Time per KYC form type (CIP vs CDD vs EDD vs SAR)
- Field duplication rate across forms (% of fields that repeat)
- KYC completion time by advisor experience level
- Rejection rate by form type (incomplete submissions)
- Advisor overtime driven by compliance deadlines

**Ontology Traversal:**
> _"Show me the total KYC documentation time for all advisors in the Manhattan branch handling high-net-worth clients with enhanced due diligence requirements"_
>
> `FinancialAdvisor → assigned_to → Branch (Manhattan)` → `manages → Client (HNW segment)` → `ComplianceDocEvent (doc_type = EDD)`

**Sample KQL Query — Real-Time KYC Pipeline:**
```kql
stream_core_banking_clicks
| where module == "KYC" and timestamp > ago(1h)
| summarize
    TotalClicks = count(),
    AvgIdleSeconds = avg(idle_before_ms) / 1000,
    ErrorCount = countif(error_code != "")
  by advisor_id, screen
| order by ErrorCount desc
```

**Sample SQL Query — KYC Burden by Advisor:**
```sql
SELECT a.name, a.branch_id,
       d.name AS doc_type,
       COUNT(*) AS filings,
       AVG(c.duration_minutes) AS avg_min_per_filing,
       SUM(c.duration_minutes) AS total_doc_minutes
FROM fact_compliance_doc_events c
JOIN dim_advisors a ON c.advisor_id = a.advisor_id
JOIN dim_document_types d ON c.doc_type_id = d.doc_type_id
WHERE d.category = 'KYC/AML'
GROUP BY a.name, a.branch_id, d.name
ORDER BY total_doc_minutes DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| KYC completion time (per client) | > 4 hours | > 8 hours |
| Form rejection rate | > 10% | > 20% |
| Advisor overtime (weekly) | > 5 hours | > 10 hours |
| EDD backlog (pending > 48h) | > 3 clients | > 8 clients |

---

### UC-2: Loan Processing Cycle Time

**Problem:** Loan officers navigate a multi-stage pipeline (application → underwriting → approval → closing) where each stage requires separate documentation. Officers often wait on internal paperwork (appraisals, income verification, title search) while documenting status updates and communicating timelines to borrowers.

**What the Platform Measures:**
- Documentation time per loan stage (application, underwriting, approval, closing)
- Wait time vs active documentation time at each stage
- Handoff documentation overhead between underwriting stages
- Status update communication burden (emails, calls, portal updates)
- Loan abandonment correlated with documentation delays

**Ontology Traversal:**
> _"Which loan officers have the longest documentation time in the underwriting stage for mortgage products in the Southeast region?"_
>
> `LoanOfficer → assigned_to → Branch (Southeast)` → `processes → Loan (product = mortgage)` → `fact_loan_processing (stage = underwriting)`

**Sample SQL Query — Stage Bottleneck Detection:**
```sql
SELECT p.stage,
       AVG(p.stage_duration_days) AS avg_days,
       AVG(p.doc_count) AS avg_docs_per_stage,
       COUNT(CASE WHEN p.rejection_reason IS NOT NULL THEN 1 END) AS rejections,
       COUNT(*) AS total_loans
FROM fact_loan_processing p
GROUP BY p.stage
ORDER BY avg_days DESC;
```

**Data Agent Example Questions:**
- _"What's the average time from application to closing for auto loans vs mortgages?"_
- _"Which underwriters have the highest documentation turnaround time?"_
- _"Show me loan abandonment rates by stage and officer"_

---

### UC-3: Trade Compliance Documentation

**Problem:** Every trade requires pre-trade compliance checks (suitability, best execution, concentration limits) and post-trade documentation (confirmations, regulatory filings, books & records). The gap between trade execution and filing completion is a compliance risk.

**What the Platform Measures:**
- Pre-trade documentation time (suitability review, compliance approval)
- Post-trade filing time (trade confirmation, regulatory submission)
- Execution-to-filing gap (time between trade and completed documentation)
- Compliance exception rate (trades flagged for documentation deficiency)
- Trade type burden analysis (equities vs fixed income vs alternatives)

**Sample KQL Query — Real-Time Trade Filing Gap:**
```kql
stream_trading_events
| where timestamp > ago(24h)
| where post_trade_filing_status != "complete"
| summarize
    UnfiledTrades = count(),
    AvgGapMinutes = avg(datetime_diff('minute', now(), timestamp))
  by advisor_id, instrument
| where AvgGapMinutes > 60
| order by UnfiledTrades desc
```

---

### UC-4: Advisor Productivity Analytics

**Problem:** Revenue per advisor varies dramatically, but firms lack visibility into whether low-producing advisors spend more time on documentation. The hypothesis: top producers have found documentation shortcuts or have better support staff, while mid-tier advisors drown in paperwork.

**What the Platform Measures:**
- Documentation hours vs client-facing hours per advisor per week
- Revenue per hour of client-facing time (true productivity metric)
- Admin support utilization (which advisors delegate documentation effectively)
- Documentation pattern clusters (identify advisor archetypes)
- Core banking system friction per advisor (click count, error rate)

**Sample SQL Query — Productivity Correlation:**
```sql
SELECT a.name, a.AUM,
       SUM(CASE WHEN d.category IN ('KYC/AML','Internal') THEN c.duration_minutes ELSE 0 END) AS admin_doc_min,
       SUM(CASE WHEN d.category = 'Client-Facing' THEN c.duration_minutes ELSE 0 END) AS client_doc_min,
       cs.nps_score AS avg_client_nps
FROM dim_advisors a
JOIN fact_compliance_doc_events c ON a.advisor_id = c.advisor_id
JOIN dim_document_types d ON c.doc_type_id = d.doc_type_id
LEFT JOIN (SELECT advisor_id, AVG(nps_score) AS nps_score FROM fact_client_satisfaction GROUP BY advisor_id) cs
  ON a.advisor_id = cs.advisor_id
GROUP BY a.name, a.AUM, cs.nps_score
ORDER BY a.AUM DESC;
```

**Data Agent Example Questions:**
- _"Which top-10 advisors by AUM spend the least time on compliance documentation?"_
- _"Is there a correlation between documentation hours and NPS scores?"_
- _"Show me the admin-to-client time ratio by branch"_

---

### UC-5: Regulatory Exam Readiness

**Problem:** When regulators announce an exam, branches scramble to verify documentation completeness. Exam preparation itself becomes a massive documentation burden — pulling files, filling gaps, running self-assessments — on top of normal workload.

**What the Platform Measures:**
- Documentation completeness score by regulation and branch
- Gap count and gap severity (missing vs incomplete vs outdated)
- Exam prep hours per branch (distinct documentation category)
- Days-to-exam vs documentation readiness trend
- Historical exam findings vs current gap patterns (predictive)

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Doc completeness score (branch) | < 90% | < 80% |
| Gap count (per regulation) | > 5 gaps | > 15 gaps |
| Days to exam with gaps | < 30 days + gaps | < 14 days + gaps |
| Prep hours exceeding budget | > 120% of planned | > 200% of planned |

**Sample SQL Query — Exam Readiness Dashboard:**
```sql
SELECT b.name AS branch,
       r.name AS regulation,
       e.doc_completion_pct,
       e.gap_count,
       e.days_to_exam,
       e.prep_hours_spent,
       CASE
         WHEN e.doc_completion_pct < 80 AND e.days_to_exam < 14 THEN 'CRITICAL'
         WHEN e.doc_completion_pct < 90 AND e.days_to_exam < 30 THEN 'WARNING'
         ELSE 'ON TRACK'
       END AS readiness_status
FROM fact_exam_readiness e
JOIN dim_branches b ON e.branch_id = b.branch_id
JOIN dim_regulations r ON e.regulation_id = r.regulation_id
ORDER BY e.days_to_exam ASC;
```

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (avg KYC time, loan cycle time, NPS), advisor burden heat map | _"How are we performing across branches?"_ |
| **Compliance & Documentation** | Doc time by type, form rejection rates, duplicative field analysis | _"Where is the paperwork burden highest?"_ |
| **Loan Pipeline** | Stage funnel, bottleneck detection, abandonment rate | _"Where do loans stall due to documentation?"_ |
| **Advisor Wellness** | Burnout risk scores, overtime trends, admin-to-client ratio | _"Which advisors are at risk?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **Trading Floor** | `stream_trading_events` | Unfiled trades, filing gap countdown |
| **Core Banking Usage** | `stream_core_banking_clicks` | Live click patterns, error hotspots |
| **Client Interactions** | `stream_client_interactions` | Activity heatmap, channel breakdown |
| **Compliance Alerts** | `stream_compliance_alerts` | Active alerts, suppression rate |
| **Branch Presence** | `stream_branch_presence` | Real-time advisor location distribution |
