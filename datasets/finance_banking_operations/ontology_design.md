# Finance Banking Operations — Ontology Design

## Overview

This document defines the Fabric IQ ontology for the **Finance Banking Operations** use case. It maps the financial services data model to Fabric IQ entity types, relationship types, properties, contextualizations (events), and data bindings across **Lakehouse** (Delta tables) and **Eventhouse** (KQL tables via Real-Time Intelligence).

The core analytical focus is **documentation burden on Financial Advisors** — quantifying how much time advisors spend on compliance documentation, KYC verifications, trade compliance filings, loan processing paperwork, and regulatory exam preparation vs. actual client advisory, relationship management, and revenue-generating activities.

**Ontology Name:** `FinanceBankingOpsOntology`

---

## Concept Mapping (RDF → Fabric IQ)

| RDF Concept       | Fabric IQ Concept   | Description                                              |
|-------------------|---------------------|----------------------------------------------------------|
| Class             | Entity Type         | A category of real-world object (Advisor, Client, Branch)|
| Data Property     | Property            | An attribute of an entity (name, role, risk_profile)     |
| Object Property   | Relationship Type   | A link between two entities (advises, stationed_at)      |
| Time-Series Event | Contextualization   | An event binding entities to time (ComplianceDocEvent)   |

---

## Entity Types (Lakehouse — Delta Tables)

### 1. Advisor
**Source Table:** `dim_advisors` (Lakehouse)
**Primary Key:** `advisor_id`

| Property       | Type    | Description                                |
|----------------|---------|--------------------------------------------|
| advisor_id     | String  | Primary key (advisor identifier)           |
| name           | String  | Full name                                  |
| role           | String  | Financial Advisor, Senior Advisor, VP      |
| branch_id      | String  | Assigned branch (FK → Branch)              |
| license_type   | String  | Series 7, Series 66, CFP, CFA             |
| hire_date      | Date    | Date of hire                               |
| AUM_millions   | Float   | Assets Under Management (millions USD)     |
| certifications | String  | Professional certifications held           |

### 2. Client
**Source Table:** `dim_clients` (Lakehouse)
**Primary Key:** `client_id`

| Property             | Type    | Description                              |
|----------------------|---------|------------------------------------------|
| client_id            | String  | Primary key (client identifier)          |
| name                 | String  | Client name                              |
| account_type         | String  | Individual, Joint, Trust, Corporate      |
| risk_profile         | String  | Conservative, Moderate, Aggressive       |
| onboarding_date      | Date    | Client onboarding date                   |
| segment              | String  | Retail, HNW, UHNW, Institutional        |
| relationship_manager | String  | Assigned relationship manager            |

### 3. Branch
**Source Table:** `dim_branches` (Lakehouse)
**Primary Key:** `branch_id`

| Property          | Type    | Description                              |
|-------------------|---------|------------------------------------------|
| branch_id         | String  | Primary key (branch identifier)          |
| name              | String  | Branch name                              |
| region            | String  | Geographic region                        |
| state             | String  | State code                               |
| branch_type       | String  | Full-Service, Satellite, Virtual         |
| headcount         | Integer | Number of employees                      |
| compliance_rating | Float   | Compliance audit rating (1.0–5.0)       |

### 4. DocumentType
**Source Table:** `dim_document_types` (Lakehouse)
**Primary Key:** `doc_type_id`

| Property                  | Type    | Description                              |
|---------------------------|---------|------------------------------------------|
| doc_type_id               | String  | Primary key (document type identifier)   |
| name                      | String  | Document type name                       |
| category                  | String  | KYC, Compliance, Trade, Loan, Regulatory |
| regulatory_body           | String  | SEC, FINRA, OCC, State                   |
| required_fields           | String  | Comma-separated required fields          |
| avg_completion_time_min   | Float   | Average completion time (minutes)        |

### 5. Product
**Source Table:** `dim_products` (Lakehouse)
**Primary Key:** `product_id`

| Property         | Type    | Description                              |
|------------------|---------|------------------------------------------|
| product_id       | String  | Primary key (product identifier)         |
| name             | String  | Product name                             |
| category         | String  | Equity, Fixed Income, Mutual Fund, ETF   |
| risk_tier        | String  | Low, Medium, High, Speculative           |
| regulatory_class | String  | Regulatory classification                |

### 6. Regulation
**Source Table:** `dim_regulations` (Lakehouse)
**Primary Key:** `regulation_id`

| Property                      | Type    | Description                          |
|-------------------------------|---------|--------------------------------------|
| regulation_id                 | String  | Primary key (regulation identifier)  |
| name                          | String  | Regulation name                      |
| body                          | String  | Regulatory body (SEC, FINRA, OCC)    |
| effective_date                | Date    | Effective date of regulation         |
| documentation_requirements    | String  | Documentation requirements summary   |

---

## Relationship Types

| Relationship ID | Name           | Source Entity | Target Entity | Cardinality | Description                                          |
|-----------------|----------------|---------------|---------------|-------------|------------------------------------------------------|
| REL-001         | advises        | Advisor       | Client        | 1:Many      | Advisor advises one or more clients                  |
| REL-002         | stationed_at   | Advisor       | Branch        | Many:1      | Advisor is stationed at a branch                     |
| REL-003         | holds          | Client        | Product       | Many:Many   | Client holds one or more financial products          |
| REL-004         | governed_by    | DocumentType  | Regulation    | Many:1      | Document type is governed by a regulation            |
| REL-005         | complies_with  | Branch        | Regulation    | Many:Many   | Branch must comply with applicable regulations       |

**Implementation Notes:**
- `REL-001` (advises) is derived from `fact_compliance_doc_events.advisor_id` → `dim_clients.client_id` joins and `dim_clients.relationship_manager` mappings.
- `REL-003` (holds) is a dynamic relationship derived from trade and loan fact tables — a single client may hold multiple products across asset classes.
- `REL-005` (complies_with) is derived from `fact_exam_readiness` branch-to-regulation bindings — a branch may be subject to multiple regulatory examinations.
- Static relationships (`REL-002`, `REL-004`) are derived from dimension table foreign keys.

---

## Contextualizations (Events — Eventhouse KQL Tables)

Contextualizations bind entities to time-series events. These are the core of Real-Time Intelligence analytics for measuring advisor documentation burden.

### CTX-001: ComplianceDocEvent
**Source Table:** `fact_compliance_doc_events` (Eventhouse)
**Key Entity Bindings:** Advisor, Client, DocumentType

| Field            | Type     | Description                                    |
|------------------|----------|------------------------------------------------|
| event_id         | String   | Primary key (event identifier)                 |
| advisor_id       | String   | FK → Advisor entity                            |
| client_id        | String   | FK → Client entity                             |
| doc_type_id      | String   | FK → DocumentType entity                       |
| start_time       | DateTime | Document creation start time                   |
| duration_minutes | Float    | Minutes spent on compliance documentation      |
| status           | String   | Draft, Submitted, Approved, Rejected           |
| error_count      | Integer  | Number of errors flagged during completion     |
| regulatory_body  | String   | Governing regulatory body                      |

**Analytical Value:** Core compliance documentation burden per advisor, error-driven rework time, document type complexity analysis, regulatory body workload distribution.

### CTX-002: CoreBankingInteractionEvent
**Source Table:** `fact_core_banking_interactions` (Eventhouse)
**Key Entity Bindings:** Advisor

| Field           | Type     | Description                                     |
|-----------------|----------|-------------------------------------------------|
| interaction_id  | String   | Primary key (interaction identifier)            |
| advisor_id      | String   | FK → Advisor entity                             |
| timestamp       | DateTime | Interaction timestamp                           |
| system_module   | String   | Core banking module accessed                    |
| action          | String   | Create, Update, Search, Export, Submit           |
| click_count     | Integer  | Number of clicks in this interaction            |
| idle_seconds    | Integer  | Idle / wait time (system latency)               |
| error_code      | String   | Error code (null if none)                       |

**Analytical Value:** Core banking system friction analysis, non-productive navigation time, module usage patterns, system latency burden on advisors.

### CTX-003: KYCVerificationEvent
**Source Table:** `fact_kyc_verifications` (Eventhouse)
**Key Entity Bindings:** Advisor, Client

| Field                 | Type     | Description                                |
|-----------------------|----------|--------------------------------------------|
| kyc_id                | String   | Primary key (KYC verification identifier)  |
| advisor_id            | String   | FK → Advisor entity                        |
| client_id             | String   | FK → Client entity                         |
| timestamp             | DateTime | Verification timestamp                     |
| verification_type     | String   | Identity, Address, Income, Source-of-Funds |
| source                | String   | Manual, Automated, ThirdParty              |
| result                | String   | Pass, Fail, Pending, Escalated             |
| time_to_complete_min  | Float    | Minutes to complete verification           |

**Analytical Value:** KYC documentation cascade — time per verification type, manual vs. automated verification efficiency, failure-driven rework burden.

### CTX-004: LoanProcessingEvent
**Source Table:** `fact_loan_processing` (Eventhouse)
**Key Entity Bindings:** Advisor, Client

| Field               | Type     | Description                                  |
|---------------------|----------|----------------------------------------------|
| loan_id             | String   | Primary key (loan identifier)                |
| officer_id          | String   | FK → Advisor entity (loan officer)           |
| client_id           | String   | FK → Client entity                           |
| stage               | String   | Application, Underwriting, Approval, Closing |
| start_date          | DateTime | Stage start date                             |
| stage_duration_days | Float    | Days spent in this stage                     |
| doc_count           | Integer  | Number of documents required for stage       |
| rejection_reason    | String   | Rejection reason (null if none)              |

**Analytical Value:** Loan processing documentation bottleneck — stage-level doc requirements, rejection-driven rework, pipeline velocity vs. documentation load.

### CTX-005: TradeComplianceEvent
**Source Table:** `fact_trade_compliance` (Eventhouse)
**Key Entity Bindings:** Advisor, Client

| Field                    | Type     | Description                              |
|--------------------------|----------|------------------------------------------|
| trade_id                 | String   | Primary key (trade identifier)           |
| advisor_id               | String   | FK → Advisor entity                      |
| client_id                | String   | FK → Client entity                       |
| timestamp                | DateTime | Trade timestamp                          |
| trade_type               | String   | Buy, Sell, Transfer, Rebalance           |
| pre_trade_doc_time_min   | Float    | Minutes on pre-trade documentation       |
| post_trade_doc_time_min  | Float    | Minutes on post-trade documentation      |

**Analytical Value:** Trade documentation overhead — pre vs. post-trade documentation split, trade type complexity, total documentation cost per trade.

### CTX-006: CaseEscalationEvent
**Source Table:** `fact_case_escalations` (Eventhouse)
**Key Entity Bindings:** Advisor, Client

| Field             | Type     | Description                                  |
|-------------------|----------|----------------------------------------------|
| escalation_id     | String   | Primary key (escalation identifier)          |
| advisor_id        | String   | FK → Advisor entity                          |
| client_id         | String   | FK → Client entity                           |
| from_stage        | String   | Stage escalated from                         |
| to_stage          | String   | Stage escalated to                           |
| timestamp         | DateTime | Escalation timestamp                         |
| reason            | String   | Escalation reason                            |
| doc_delay_minutes | Float    | Documentation delay triggering escalation    |

**Analytical Value:** Escalation patterns driven by documentation delays, stage transition friction, documentation-related case bottlenecks.

### CTX-007: RegulatoryAlertEvent
**Source Table:** `fact_regulatory_alerts` (Eventhouse)
**Key Entity Bindings:** Advisor, Client

| Field             | Type     | Description                                  |
|-------------------|----------|----------------------------------------------|
| alert_id          | String   | Primary key (alert identifier)               |
| advisor_id        | String   | FK → Advisor entity                          |
| client_id         | String   | FK → Client entity                           |
| timestamp         | DateTime | Alert timestamp                              |
| alert_type        | String   | SuitabilityFlag, ComplianceGap, AMLAlert     |
| severity          | String   | Low, Medium, High, Critical                  |
| action_taken      | String   | Acknowledge, Investigate, Escalate, Dismiss  |
| response_time_min | Float    | Minutes to respond to alert                  |

**Analytical Value:** Regulatory alert response burden, severity-weighted response time, alert fatigue analysis across advisors.

### CTX-008: BranchPresenceEvent
**Source Table:** `fact_branch_presence` (Eventhouse)
**Key Entity Bindings:** Advisor, Branch

| Field           | Type     | Description                                    |
|-----------------|----------|------------------------------------------------|
| presence_id     | String   | Primary key (presence record identifier)       |
| advisor_id      | String   | FK → Advisor entity                            |
| branch_id       | String   | FK → Branch entity                             |
| date            | DateTime | Presence date                                  |
| arrival_time    | DateTime | Arrival time at branch                         |
| departure_time  | DateTime | Departure time from branch                     |
| remote_hours    | Float    | Hours worked remotely                          |
| meeting_hours   | Float    | Hours spent in client/internal meetings        |

**Analytical Value:** Advisor time allocation — branch presence vs. remote work, meeting time vs. documentation time, work pattern analysis for burden distribution.

---

## Batch Fact Contextualizations (Lakehouse — Periodic Aggregates)

### CTX-B01: AdvisorWellnessEvent
**Source Table:** `fact_advisor_wellness` (Lakehouse — batch/survey)
**Key Entity Bindings:** Advisor, Branch

| Field                    | Type   | Description                                  |
|--------------------------|--------|----------------------------------------------|
| survey_id                | String | Primary key (survey identifier)              |
| advisor_id               | String | FK → Advisor entity                          |
| branch_id                | String | FK → Branch entity                           |
| date                     | Date   | Survey date                                  |
| workload_score           | Integer| Self-reported workload score (1–10)          |
| overtime_hours           | Float  | Overtime hours in reporting period            |
| burnout_risk             | String | Low, Medium, High                            |
| admin_burden_perception  | String | Self-reported admin burden level              |

### CTX-B02: DocumentQualityEvent
**Source Table:** `fact_document_quality` (Lakehouse — batch)
**Key Entity Bindings:** DocumentType, Advisor

| Field              | Type   | Description                                    |
|--------------------|--------|------------------------------------------------|
| quality_id         | String | Primary key (quality record identifier)        |
| doc_type_id        | String | FK → DocumentType entity                       |
| advisor_id         | String | FK → Advisor entity                            |
| date               | Date   | Quality assessment date                        |
| error_rate         | Float  | Document error rate                            |
| rejection_rate     | Float  | Document rejection rate                        |
| audit_finding_count| Integer| Number of audit findings                       |
| completeness_score | Float  | Document completeness score (0–100)            |

### CTX-B03: ClientSatisfactionEvent
**Source Table:** `fact_client_satisfaction` (Lakehouse — batch/survey)
**Key Entity Bindings:** Client, Advisor

| Field                  | Type   | Description                                   |
|------------------------|--------|-----------------------------------------------|
| survey_id              | String | Primary key (survey identifier)               |
| client_id              | String | FK → Client entity                            |
| advisor_id             | String | FK → Advisor entity                           |
| date                   | Date   | Survey date                                   |
| nps_score              | Integer| Net Promoter Score                            |
| responsiveness_rating  | Float  | Advisor responsiveness rating                 |
| onboarding_experience  | Float  | Onboarding experience rating                  |
| complaint_flag         | String | Yes/No — formal complaint filed               |

### CTX-B04: ExamReadinessEvent
**Source Table:** `fact_exam_readiness` (Lakehouse — batch)
**Key Entity Bindings:** Branch, Regulation

| Field              | Type   | Description                                    |
|--------------------|--------|------------------------------------------------|
| exam_id            | String | Primary key (exam readiness identifier)        |
| branch_id          | String | FK → Branch entity                             |
| regulation_id      | String | FK → Regulation entity                         |
| date               | Date   | Assessment date                                |
| doc_completion_pct | Float  | Documentation completion percentage            |
| gap_count          | Integer| Number of documentation gaps                   |
| days_to_exam       | Integer| Days until regulatory exam                     |
| prep_hours_spent   | Float  | Hours spent on exam preparation                |

---

## Real-Time Stream Contextualizations (Eventhouse — Streaming)

### CTX-S01: CoreBankingClickStream
**Source Table:** `stream_core_banking_clicks` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Advisor

| Field          | Type     | Description                                     |
|----------------|----------|-------------------------------------------------|
| click_id       | String   | Primary key (click event identifier)            |
| advisor_id     | String   | FK → Advisor entity                             |
| timestamp      | DateTime | Click timestamp                                 |
| module         | String   | Core banking module                             |
| screen         | String   | Screen / page within module                     |
| action         | String   | Click action performed                          |
| duration_ms    | Integer  | Duration of action (milliseconds)               |
| idle_before_ms | Integer  | Idle time before click (milliseconds)           |
| error_code     | String   | Error code (null if none)                       |

### CTX-S02: ClientInteractionStream
**Source Table:** `stream_client_interactions` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Advisor, Client

| Field          | Type     | Description                                     |
|----------------|----------|-------------------------------------------------|
| interaction_id | String   | Primary key (interaction event identifier)      |
| advisor_id     | String   | FK → Advisor entity                             |
| client_id      | String   | FK → Client entity                              |
| timestamp      | DateTime | Interaction timestamp                           |
| channel        | String   | InPerson, Phone, Video, Email, Chat             |
| duration_sec   | Integer  | Interaction duration (seconds)                  |
| topic          | String   | Interaction topic                               |
| outcome        | String   | Resolved, FollowUp, Escalated                  |

### CTX-S03: ComplianceAlertStream
**Source Table:** `stream_compliance_alerts` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Advisor, Client

| Field        | Type     | Description                                       |
|--------------|----------|---------------------------------------------------|
| alert_id     | String   | Primary key (alert event identifier)              |
| advisor_id   | String   | FK → Advisor entity                               |
| client_id    | String   | FK → Client entity                                |
| timestamp    | DateTime | Alert timestamp                                   |
| alert_type   | String   | SuitabilityFlag, AMLAlert, ComplianceGap          |
| risk_score   | Float    | Risk score associated with alert                  |
| suppressed   | String   | Yes/No — alert suppressed by rules engine         |
| action_taken | String   | Acknowledge, Investigate, Escalate, Dismiss       |

### CTX-S04: TradingEventStream
**Source Table:** `stream_trading_events` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Advisor, Client

| Field                      | Type     | Description                               |
|----------------------------|----------|-------------------------------------------|
| trade_id                   | String   | Primary key (trade event identifier)      |
| advisor_id                 | String   | FK → Advisor entity                       |
| client_id                  | String   | FK → Client entity                        |
| timestamp                  | DateTime | Trade event timestamp                     |
| instrument                 | String   | Financial instrument traded               |
| action                     | String   | Buy, Sell, Transfer, Rebalance            |
| pre_trade_check            | String   | Pass, Fail, Waived                        |
| post_trade_filing_status   | String   | Pending, Filed, Overdue                   |

### CTX-S05: BranchPresenceStream
**Source Table:** `stream_branch_presence` (Eventhouse — Real-Time Stream)
**Key Entity Bindings:** Advisor, Branch

| Field         | Type     | Description                                      |
|---------------|----------|--------------------------------------------------|
| ping_id       | String   | Primary key (presence ping identifier)           |
| advisor_id    | String   | FK → Advisor entity                              |
| branch_id     | String   | FK → Branch entity                               |
| timestamp     | DateTime | Presence ping timestamp                          |
| location_type | String   | InBranch, Remote, ClientSite, Traveling          |
| zone          | String   | Zone within branch (Desk, ConferenceRoom, Lobby) |
| is_in_meeting | String   | Yes/No — currently in meeting                    |

---

## Data Storage Mapping

### Lakehouse (Delta Tables — Dimensional/Static Data)

| Delta Table Name         | Source CSV                       | Entity / Mapping          |
|--------------------------|----------------------------------|---------------------------|
| dim_advisors             | dim_advisors.csv                 | Advisor entity            |
| dim_clients              | dim_clients.csv                  | Client entity             |
| dim_branches             | dim_branches.csv                 | Branch entity             |
| dim_document_types       | dim_document_types.csv           | DocumentType entity       |
| dim_products             | dim_products.csv                 | Product entity            |
| dim_regulations          | dim_regulations.csv              | Regulation entity         |
| fact_advisor_wellness    | fact_advisor_wellness.csv        | CTX-B01 (batch)           |
| fact_document_quality    | fact_document_quality.csv        | CTX-B02 (batch)           |
| fact_client_satisfaction | fact_client_satisfaction.csv     | CTX-B03 (batch)           |
| fact_exam_readiness      | fact_exam_readiness.csv          | CTX-B04 (batch)           |

### Eventhouse (KQL Tables — Event/Streaming Data)

| KQL Table Name              | Source CSV                           | Contextualization |
|-----------------------------|--------------------------------------|-------------------|
| compliance_doc_events       | fact_compliance_doc_events.csv       | CTX-001           |
| core_banking_interactions   | fact_core_banking_interactions.csv   | CTX-002           |
| kyc_verifications           | fact_kyc_verifications.csv           | CTX-003           |
| loan_processing             | fact_loan_processing.csv             | CTX-004           |
| trade_compliance            | fact_trade_compliance.csv            | CTX-005           |
| case_escalations            | fact_case_escalations.csv            | CTX-006           |
| regulatory_alerts           | fact_regulatory_alerts.csv           | CTX-007           |
| branch_presence             | fact_branch_presence.csv             | CTX-008           |
| core_banking_clicks         | stream_core_banking_clicks.csv       | CTX-S01           |
| client_interactions         | stream_client_interactions.csv       | CTX-S02           |
| compliance_alerts           | stream_compliance_alerts.csv         | CTX-S03           |
| trading_events              | stream_trading_events.csv            | CTX-S04           |
| branch_presence_stream      | stream_branch_presence.csv           | CTX-S05           |

---

## Ontology Visualization

```
                         ┌────────────┐
                         │ Regulation │
                         └──────▲─────┘
                 governed_by ┌──┘  └──┐ complies_with
                             │        │
                    ┌────────┴──┐  ┌──┴───────┐
                    │ Document  │  │  Branch   │
                    │   Type    │  └─────▲─────┘
                    └───────────┘        │ stationed_at
                                         │
┌────────────┐  advises  ┌─────────┐     │
│   Client   │◀──────────│ Advisor │─────┘
└──────┬─────┘           └─────────┘
       │ holds
       ▼
┌────────────┐
│  Product   │
└────────────┘

         ── Event Fact Contextualizations (Eventhouse) ──

┌────────────┐┌───────────┐┌───────────┐┌───────────┐
│ Compliance ││Core Banking││   KYC     ││   Loan    │
│Doc Events  ││Interactions││Verif.     ││Processing │
│ (CTX-001)  ││ (CTX-002)  ││ (CTX-003) ││ (CTX-004) │
└────────────┘└───────────┘└───────────┘└───────────┘
┌────────────┐┌───────────┐┌───────────┐┌───────────┐
│   Trade    ││   Case    ││Regulatory ││  Branch   │
│ Compliance ││Escalations││  Alerts   ││ Presence  │
│ (CTX-005)  ││ (CTX-006) ││ (CTX-007) ││ (CTX-008) │
└────────────┘└───────────┘└───────────┘└───────────┘

         ── Batch Fact Contextualizations (Lakehouse) ──

┌────────────┐┌───────────┐┌───────────┐┌───────────┐
│  Advisor   ││ Document  ││  Client   ││   Exam    │
│ Wellness   ││  Quality  ││Satisfaction│ Readiness │
│ (CTX-B01)  ││ (CTX-B02) ││ (CTX-B03) ││ (CTX-B04) │
└────────────┘└───────────┘└───────────┘└───────────┘

         ── Real-Time Streaming Layer ──

┌────────────┐┌───────────┐┌───────────┐┌───────────┐┌───────────┐
│Core Banking││  Client   ││Compliance ││  Trading  ││  Branch   │
│  Clicks    ││Interactions││  Alerts   ││  Events   ││ Presence  │
│ (CTX-S01)  ││ (CTX-S02) ││ (CTX-S03) ││ (CTX-S04) ││ (CTX-S05) │
└────────────┘└───────────┘└───────────┘└───────────┘└───────────┘
```

---

## Key Analytical Queries Enabled by This Ontology

### 1. Compliance Documentation Time per Advisor
```kql
compliance_doc_events
| where start_time between (datetime(2026-01-01) .. datetime(2026-03-23))
| summarize total_doc_min = sum(duration_minutes),
            docs_completed = count(),
            avg_errors = avg(error_count),
            rejection_rate = countif(status == "Rejected") * 1.0 / count()
  by advisor_id
| order by total_doc_min desc
```

### 2. KYC Verification Burden Analysis
```kql
kyc_verifications
| summarize total_kyc_min = sum(time_to_complete_min),
            verifications = count(),
            fail_rate = countif(result == "Fail") * 1.0 / count(),
            manual_pct = countif(source == "Manual") * 100.0 / count()
  by advisor_id, verification_type
| order by total_kyc_min desc
```

### 3. Trade Documentation Overhead (Pre vs. Post)
```kql
trade_compliance
| summarize total_pre_trade_min = sum(pre_trade_doc_time_min),
            total_post_trade_min = sum(post_trade_doc_time_min),
            total_trade_doc_min = sum(pre_trade_doc_time_min + post_trade_doc_time_min),
            trade_count = count()
  by advisor_id, trade_type
| extend pre_trade_pct = round(total_pre_trade_min * 100.0 / total_trade_doc_min, 1)
| order by total_trade_doc_min desc
```

### 4. Loan Processing Document Bottlenecks
```kql
loan_processing
| summarize avg_stage_days = avg(stage_duration_days),
            avg_doc_count = avg(doc_count),
            rejection_count = countif(isnotempty(rejection_reason)),
            loans_in_stage = count()
  by stage
| order by avg_stage_days desc
```

### 5. Exam Readiness Documentation Gaps
```kql
// Cross-reference Lakehouse batch data via materialized view
fact_exam_readiness
| where days_to_exam <= 30
| summarize avg_completion_pct = avg(doc_completion_pct),
            total_gaps = sum(gap_count),
            avg_prep_hours = avg(prep_hours_spent)
  by branch_id, regulation_id
| where avg_completion_pct < 90
| order by days_to_exam asc, total_gaps desc
```
