# Law Firms

> **Reducing legal documentation overhead so attorneys and paralegals focus on practicing law, not administering files**

---

## The Problem

Attorneys and paralegals spend **40–60%** of their time on documentation and administrative tasks — time entries, discovery review, court filing preparation, contract lifecycle management, and matter administration. In an industry that bills $300–$1,000+/hour, every hour of non-billable documentation time directly erodes firm profitability and attorney satisfaction.

| Stat | Impact |
|---|---|
| **40–60%** of attorney time on documentation/admin | Directly reduces billable hours and client service quality |
| **1.5–2.5 hours/day** on time entry and billing narrative | Most common complaint among associates |
| **$300–$1,000+/hour** billing rates | Non-billable documentation hours = $150K–$500K lost revenue/attorney/year |
| **30–40%** of discovery review time on documentation | Privilege logs, review memoranda, coding documentation |
| **55–65%** realization rate industry average | Documentation gaps contribute to write-downs and billing disputes |

---

## Ontology Mapping

| Core Concept | Law Firm Equivalent |
|---|---|
| Worker Entity | `Attorney` / `Paralegal` |
| Client Entity | `Client` / `Matter` |
| Unit Entity | `PracticeGroup` / `Office` |
| Task Type Entity | `LegalTaskType` (drafting, review, filing, research, client communication) |
| Core Event | `LegalDocEvent` — time entries, document drafting, filing submissions |
| System Interaction | `DMSInteraction` — Clio, iManage, Relativity, NetDocuments activities |
| Handoff Event | `MatterTransfer` — attorney transitions, practice group referrals |
| Burnout Measure | `AttorneyWellness` — billable pressure, admin burden, work-life balance |
| Quality Measure | `WorkProductQuality` — brief quality, document accuracy, filing timeliness |
| Satisfaction Measure | `ClientSatisfaction` — responsiveness, outcome, value perception |
| Location Tracking | `TimeLocation` — office, remote, court, client site, deposition |
| UX Clickstream | `DMSClickstream` — document management system navigation patterns |
| Interruption Event | `UrgentCaseEvent` — emergency motion, TRO, court order, client crisis |
| Compliance Scan | `EthicsCheck` — conflict check, privilege review, deadline tracking |
| Decision Alert | `DeadlineAlert` — statute of limitations, filing deadline, response due date |

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_attorneys` | attorney_id, name, role, practice_group, bar_admission, years_experience, billing_rate, hire_date | 30 |
| `dim_clients` | client_id, name, industry, relationship_start, billing_arrangement, annual_revenue, matter_count | 25 |
| `dim_matters` | matter_id, client_id, name, practice_area, matter_type, open_date, status, budget, lead_attorney_id | 40 |
| `dim_legal_task_types` | task_type_id, name, category, billable_flag, avg_duration_min, requires_review | 20 |
| `dim_practice_groups` | practice_group_id, name, office, attorney_count, revenue_target, specializations | 8 |
| `dim_courts` | court_id, name, jurisdiction, type, filing_requirements, efiling_system | 12 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_time_entries` | entry_id, attorney_id, matter_id, date, task_type, hours_worked, hours_billed, narrative, entry_time_min, write_down_pct | 500 |
| `fact_discovery_events` | discovery_id, attorney_id, matter_id, date, review_type, docs_reviewed, docs_coded, privilege_flags, doc_time_min | 150 |
| `fact_attorney_wellness` | survey_id, attorney_id, date, billable_pressure_score, admin_burden_score, work_life_score, overtime_hours | 30 |
| `fact_work_product_quality` | quality_id, document_id, attorney_id, date, document_type, accuracy_score, revision_count, review_time_min | 200 |
| `fact_client_satisfaction` | survey_id, client_id, matter_id, date, responsiveness_score, outcome_score, value_score, nps | 25 |
| `fact_matter_performance` | perf_id, matter_id, attorney_id, month, hours_billed, revenue, collections, realization_pct, wip_aging_days | 80 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_dms_interactions` | interaction_id, attorney_id, timestamp, system, action, document_id, duration_ms, search_terms | 500 |
| `fact_filing_events` | filing_id, matter_id, attorney_id, timestamp, court_id, filing_type, deadline_date, submitted_date, doc_time_min | 60 |
| `fact_contract_events` | contract_id, matter_id, attorney_id, timestamp, stage, counterparty, redline_count, doc_time_min, version | 80 |
| `fact_matter_transfers` | transfer_id, matter_id, from_attorney, to_attorney, timestamp, open_items, doc_time_min, reason | 20 |
| `fact_deadline_alerts` | alert_id, matter_id, attorney_id, timestamp, deadline_type, deadline_date, days_remaining, status | 100 |
| `fact_billing_events` | billing_id, matter_id, attorney_id, timestamp, invoice_amount, write_down_amount, status, dispute_flag | 60 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_dms_activity` | iManage / NetDocuments / Clio | activity_id, attorney_id, timestamp, document_id, action, matter_id, duration_sec | Document creation, editing, search patterns |
| `stream_time_tracking` | Time & billing system | entry_id, attorney_id, timestamp, matter_id, task_type, duration_min, billable_flag | Real-time time capture, billing patterns |
| `stream_court_deadlines` | Docketing / calendaring | deadline_id, matter_id, timestamp, deadline_type, due_date, days_remaining, priority | Filing deadlines, statute expirations |
| `stream_discovery_progress` | Relativity / review platform | review_id, attorney_id, timestamp, docs_reviewed, privilege_flags, coding_decisions | Review pace, privilege calls, responsiveness |
| `stream_client_communications` | Email / CRM | comm_id, attorney_id, client_id, timestamp, comm_type, response_time_min, matter_id | Responsiveness, communication volume |

---

## Use Cases — Detailed

### UC-1: Billable vs Non-Billable Documentation Time

**Problem:** The fundamental economics of a law firm are built on billable hours. Yet attorneys spend 1.5–2.5 hours daily on time entry narratives, billing reconciliation, and administrative documentation that is not billable. The "documentation tax" on each billable hour means that a target of 2,000 billable hours actually requires 2,800–3,200 total working hours. This drives burnout, attrition, and revenue leakage.

**What the Platform Measures:**
- Billable-to-total-hours ratio by attorney, practice group, and seniority level
- Time entry documentation burden (minutes spent writing time narratives per day)
- Time entry lag (hours/days between work and time entry — impacts accuracy and collections)
- Write-down correlation: late time entries × write-down percentage
- Non-billable administrative overhead by category

**Ontology Traversal:**
> _"Show me associates in Litigation whose time entry documentation exceeds 2 hours/day, and correlate with their realization rates and wellness scores"_
>
> `Attorney (role=associate) → member_of → PracticeGroup (Litigation)` → `TimeEntry (entry_time > 120 min/day)` → `MatterPerformance (realization_pct)` + `AttorneyWellness (admin_burden_score)`

**Sample SQL Query — Billable Efficiency Analysis:**
```sql
SELECT a.name AS attorney,
       a.role,
       pg.name AS practice_group,
       a.billing_rate,
       SUM(te.hours_worked) AS total_hours,
       SUM(te.hours_billed) AS billable_hours,
       ROUND(SUM(te.hours_billed) * 100.0 / NULLIF(SUM(te.hours_worked), 0), 1) AS billable_pct,
       AVG(te.entry_time_min) AS avg_time_entry_min,
       SUM(te.entry_time_min) / 60.0 AS total_entry_doc_hours,
       AVG(te.write_down_pct) AS avg_write_down_pct,
       aw.admin_burden_score
FROM fact_time_entries te
JOIN dim_attorneys a ON te.attorney_id = a.attorney_id
JOIN dim_practice_groups pg ON a.practice_group = pg.practice_group_id
LEFT JOIN fact_attorney_wellness aw ON a.attorney_id = aw.attorney_id
GROUP BY a.name, a.role, pg.name, a.billing_rate, aw.admin_burden_score
ORDER BY billable_pct ASC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Billable hours percentage | < 65% | < 50% |
| Time entry lag | > 48 hours | > 1 week |
| Daily time entry documentation | > 2 hours | > 3 hours |
| Write-down rate | > 10% | > 20% |

---

### UC-2: Discovery Review Documentation Burden

**Problem:** E-discovery is among the most labor-intensive legal activities. Associates and contract attorneys review thousands to millions of documents, making privilege determinations, coding relevance, and documenting review decisions. The privilege log alone — required for every document withheld on privilege grounds — can take hundreds of hours to prepare. Documentation overhead in discovery directly impacts litigation costs and client satisfaction.

**What the Platform Measures:**
- Documents reviewed per hour and associated documentation time
- Privilege log documentation time per privilege call
- Review coding consistency and quality scores
- Discovery documentation cost per GB reviewed
- TAR (Technology Assisted Review) vs manual review documentation efficiency

**Sample KQL Query — Real-Time Discovery Progress:**
```kql
stream_discovery_progress
| where timestamp > ago(24h)
| summarize
    TotalReviewed = sum(docs_reviewed),
    PrivilegeFlags = sum(privilege_flags),
    CodingDecisions = sum(coding_decisions),
    ReviewHours = count() * 0.25  // 15-min review intervals
  by attorney_id
| extend DocsPerHour = TotalReviewed / ReviewHours
| order by DocsPerHour asc
```

---

### UC-3: Court Filing Cycle Time

**Problem:** Court filings require meticulous documentation — the brief itself, exhibits, certificates of service, proposed orders, and e-filing system compliance. Each jurisdiction has unique formatting and procedural requirements. Filing errors cause rejections, missed deadlines, and potential malpractice exposure. Attorneys report that filing documentation consumes 5–10 hours per major brief, with a significant portion spent on procedural compliance rather than substantive legal work.

**What the Platform Measures:**
- Filing preparation time by court, filing type, and complexity
- Filing rejection rate and re-submission documentation time
- Deadline performance: submissions relative to due date
- Cross-jurisdictional filing documentation overhead
- Substantive-to-procedural documentation time ratio

**Sample SQL Query — Filing Efficiency:**
```sql
SELECT a.name AS attorney,
       c.name AS court,
       c.jurisdiction,
       fe.filing_type,
       COUNT(fe.filing_id) AS total_filings,
       AVG(fe.doc_time_min) AS avg_filing_doc_min,
       AVG(DATEDIFF(day, fe.submitted_date, fe.deadline_date)) AS avg_days_before_deadline,
       SUM(CASE WHEN fe.submitted_date > fe.deadline_date THEN 1 ELSE 0 END) AS late_filings,
       SUM(fe.doc_time_min) / 60.0 AS total_filing_doc_hours
FROM fact_filing_events fe
JOIN dim_attorneys a ON fe.attorney_id = a.attorney_id
JOIN dim_courts c ON fe.court_id = c.court_id
GROUP BY a.name, c.name, c.jurisdiction, fe.filing_type
ORDER BY avg_filing_doc_min DESC;
```

---

### UC-4: Contract Lifecycle Documentation

**Problem:** Transactional attorneys spend enormous time on contract documentation — drafting, redlining, version tracking, negotiation correspondence, signature management, and post-execution administration. A single M&A deal can generate 100–500 documents with 5–20 redline cycles each. Version control and document comparison consume hours of non-billable time.

**What the Platform Measures:**
- Contract documentation time by stage (draft, negotiate, redline, sign, admin)
- Redline cycles per contract and documentation overhead per cycle
- Version control time: searching, comparing, organizing contract versions
- Post-execution admin burden: filing, indexing, obligation tracking
- Contract turnaround time: documentation bottleneck vs substantive negotiation

**Sample KQL Query — Real-Time Document Activity:**
```kql
stream_dms_activity
| where timestamp > ago(8h)
| summarize
    TotalActions = count(),
    Creates = countif(action == "create"),
    Edits = countif(action == "edit"),
    Searches = countif(action == "search"),
    TotalMinutes = sum(duration_sec) / 60.0
  by attorney_id, matter_id
| extend SearchPct = round(Searches * 100.0 / TotalActions, 1)
| where SearchPct > 30  // Flag attorneys spending too much time searching
| order by SearchPct desc
```

---

### UC-5: Matter Profitability & Documentation Cost

**Problem:** Law firms struggle to understand the true profitability of individual matters because non-billable documentation time is invisible in standard billing reports. A matter may show 500 billable hours, but the attorneys actually spent 700 total hours — with 200 hours on non-billable documentation (time entry, billing reconciliation, internal memos, document management). This hidden cost can make profitable-looking matters actually unprofitable.

**What the Platform Measures:**
- True cost per matter: billable hours + non-billable documentation hours × blended rate
- Documentation cost as percentage of matter revenue
- Practice group profitability including documentation overhead
- Client profitability after documentation cost allocation
- Documentation efficiency trend: cost trajectory as matter matures

**Sample SQL Query — Matter Profitability Analysis:**
```sql
SELECT m.name AS matter,
       c.name AS client,
       pg.name AS practice_group,
       mp.revenue,
       mp.collections,
       mp.realization_pct,
       SUM(te.hours_billed) AS billable_hours,
       SUM(te.hours_worked) - SUM(te.hours_billed) AS non_billable_hours,
       SUM(te.entry_time_min) / 60.0 AS time_entry_doc_hours,
       mp.revenue - (SUM(te.hours_worked) * a.billing_rate) AS true_margin,
       ROUND(mp.collections * 100.0 / NULLIF(mp.revenue, 0), 1) AS collection_rate
FROM fact_matter_performance mp
JOIN dim_matters m ON mp.matter_id = m.matter_id
JOIN dim_clients c ON m.client_id = c.client_id
JOIN dim_attorneys a ON mp.attorney_id = a.attorney_id
JOIN dim_practice_groups pg ON a.practice_group = pg.practice_group_id
JOIN fact_time_entries te ON m.matter_id = te.matter_id AND a.attorney_id = te.attorney_id
GROUP BY m.name, c.name, pg.name, mp.revenue, mp.collections, mp.realization_pct, a.billing_rate
ORDER BY true_margin ASC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Matter realization rate | < 85% | < 70% |
| Non-billable documentation ratio | > 25% | > 40% |
| WIP aging | > 60 days | > 120 days |
| Collection rate | < 90% | < 75% |

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (revenue, realization, utilization), practice group scorecard | _"How is the firm performing?"_ |
| **Documentation Burden** | Time entry overhead, billable %, admin time by role | _"How much attorney time is lost to documentation?"_ |
| **Matter Profitability** | Revenue vs true cost, documentation margin impact, client profitability | _"Which matters are truly profitable?"_ |
| **Filing & Deadlines** | Deadline compliance, filing cycle time, malpractice risk indicators | _"Are we meeting all deadlines?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **DMS Activity** | `stream_dms_activity` | Document creation, edits, search patterns |
| **Time Capture** | `stream_time_tracking` | Real-time entries, billable patterns, lag alerts |
| **Deadline Tracker** | `stream_court_deadlines` | Upcoming deadlines, statute expirations, priority |
| **Discovery Progress** | `stream_discovery_progress` | Review pace, privilege calls, completion projection |
| **Client Response** | `stream_client_communications` | Response times, communication volume, engagement |
