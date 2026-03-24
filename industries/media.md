# Media & Entertainment

> **Reducing content production documentation burden so producers and editors focus on creating, not cataloging**

---

## The Problem

Content producers, editors, and rights managers spend **30–50%** of their time on metadata tagging, rights clearance documentation, ad copy approvals, regulatory compliance (FCC/GDPR), and content delivery paperwork. In an industry racing to fill 24/7 programming slots and multi-platform distribution, documentation bottlenecks delay air dates and inflate production costs.

| Stat | Impact |
|---|---|
| **30–50%** of producer time on documentation/admin | Less time for creative development and audience engagement |
| **60–90 metadata fields** per asset | Title, description, credits, rights, technical specs, accessibility |
| **$150K–$250K** average producer/editor salary | 40% admin time = $60K–$100K/year on documentation |
| **15–25%** of content delayed by rights clearance | Music, stock footage, talent, brand licenses — each requiring paperwork |
| **6–12 weeks** average rights clearance cycle | Documentation back-and-forth is the primary bottleneck |

---

## Ontology Mapping

| Core Concept | Media Equivalent |
|---|---|
| Worker Entity | `ContentProducer` / `Editor` / `RightsManager` |
| Client Entity | `Show` / `Campaign` / `ContentClient` |
| Unit Entity | `Network` / `Platform` / `Studio` |
| Task Type Entity | `ContentTaskType` (tagging, rights clearance, QC, delivery, compliance review) |
| Core Event | `ContentDocEvent` — metadata entry, rights processing, approval workflows |
| System Interaction | `MAMInteraction` — Avid, Frame.io, Aspera, MediaSilo activities |
| Handoff Event | `ContentHandoff` — editor to QC, QC to delivery, platform distribution |
| Burnout Measure | `CrewWellness` — production fatigue, deadline pressure, admin burden |
| Quality Measure | `ContentQuality` — metadata completeness, rights accuracy, QC pass rate |
| Satisfaction Measure | `ClientSatisfaction` — on-time delivery rate, revision frequency |
| Location Tracking | `StudioLocation` — edit suite, control room, field production location |
| UX Clickstream | `MAMClickstream` — DAM/MAM system navigation patterns |
| Interruption Event | `UrgentRevision` — last-minute edit, rights dispute, regulatory flag |
| Compliance Scan | `RegulatoryReview` — FCC flag, GDPR data check, accessibility compliance |
| Decision Alert | `DeliveryAlert` — missed deadline, rights gap, QC failure |

---

## Data Model

### Dimension Tables (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `dim_producers` | producer_id, name, role, department, shows_assigned, hire_date, specialization | 25 |
| `dim_shows` | show_id, name, genre, network, platform, season, episode_count, production_budget | 15 |
| `dim_networks` | network_id, name, type, platform_count, content_hours_per_week, region | 6 |
| `dim_content_task_types` | task_type_id, name, category, avg_duration_min, requires_approval, regulatory_flag | 20 |
| `dim_rights_holders` | holder_id, name, type, territory, content_count, avg_clearance_days | 30 |
| `dim_platforms` | platform_id, name, type, spec_requirements, delivery_format, region | 12 |

### Fact Tables — Batch (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_content_doc_events` | doc_id, producer_id, show_id, date, task_type, asset_id, doc_time_min, metadata_fields_completed, status | 250 |
| `fact_rights_clearance` | clearance_id, rights_manager_id, show_id, holder_id, date, rights_type, territory, status, doc_time_min, cycle_days | 100 |
| `fact_crew_wellness` | survey_id, producer_id, date, production_fatigue_score, admin_burden_score, deadline_pressure, overtime_hours | 25 |
| `fact_content_quality` | quality_id, asset_id, producer_id, date, metadata_completeness_pct, rights_accuracy_pct, qc_pass_rate | 200 |
| `fact_client_satisfaction` | survey_id, show_id, client_id, date, on_time_delivery_pct, revision_count, satisfaction_score | 15 |
| `fact_production_performance` | perf_id, show_id, producer_id, month, episodes_delivered, on_time_pct, doc_hours, creative_hours, budget_spent | 45 |

### Fact Tables — Events (6)

| Table | Key Columns | Rows (sample) |
|---|---|---|
| `fact_mam_interactions` | interaction_id, producer_id, timestamp, system, module, action, duration_ms, asset_id | 400 |
| `fact_metadata_entries` | entry_id, producer_id, asset_id, timestamp, field_name, field_value, auto_populated, manual_time_sec | 500 |
| `fact_approval_workflows` | approval_id, show_id, producer_id, timestamp, approval_type, status, approver, cycle_time_hours | 80 |
| `fact_content_handoffs` | handoff_id, show_id, from_role, to_role, timestamp, asset_count, doc_time_min, notes_length | 40 |
| `fact_delivery_alerts` | alert_id, show_id, platform_id, timestamp, alert_type, severity, deadline_date, days_to_deadline | 60 |
| `fact_regulatory_reviews` | review_id, asset_id, producer_id, timestamp, regulation, finding, severity, remediation_time_min | 50 |

---

## Real-Time Streams (5)

| Stream | Source System | Key Columns | Signal |
|---|---|---|---|
| `stream_mam_activity` | Avid / Frame.io / DAM | activity_id, producer_id, timestamp, asset_id, action, module, duration_sec | Edit progress, metadata entry, review cycles |
| `stream_rights_status` | Rights management system | status_id, clearance_id, timestamp, rights_type, status, holder_response, territory | Clearance progress, expiration warnings |
| `stream_delivery_tracking` | Distribution / Aspera | delivery_id, show_id, platform_id, timestamp, status, file_size_gb, transfer_pct | Content delivery progress and failures |
| `stream_qc_results` | QC automation | qc_id, asset_id, timestamp, check_type, result, error_description, severity | Technical quality, compliance flags |
| `stream_audience_metrics` | Analytics platform | metric_id, show_id, platform_id, timestamp, viewers, completion_rate, engagement_score | Real-time audience response |

---

## Use Cases — Detailed

### UC-1: Metadata Tagging & Cataloging Burden

**Problem:** Every media asset (episode, clip, promo, interstitial) requires 60–90 metadata fields — title, description, credits, technical specs, language, accessibility data, content ratings, keywords, rights windows, and platform-specific fields. Content libraries have millions of assets, and metadata quality directly impacts discovery, monetization, and regulatory compliance. Producers report that metadata entry consumes 3–5 hours per episode.

**What the Platform Measures:**
- Metadata entry time per asset type (episode, clip, promo, etc.)
- Fields manually entered vs auto-populated (automation opportunity)
- Metadata completeness rate by show and platform
- Re-work rate: metadata corrections after initial entry
- Discovery impact: correlation between metadata quality and content performance

**Ontology Traversal:**
> _"Show me producers whose metadata entry time per episode exceeds 4 hours, and flag which fields are most frequently left incomplete"_
>
> `ContentProducer → works_on → Show` → `ContentDocEvent (metadata, duration > 240 min)` → `ContentQuality (metadata_completeness_pct)`

**Sample SQL Query — Metadata Burden Analysis:**
```sql
SELECT p.name AS producer,
       s.name AS show,
       s.genre,
       COUNT(cd.doc_id) AS total_episodes_documented,
       AVG(cd.doc_time_min) AS avg_metadata_minutes,
       AVG(cd.metadata_fields_completed) AS avg_fields_completed,
       AVG(cq.metadata_completeness_pct) AS avg_completeness,
       pp.creative_hours,
       pp.doc_hours,
       ROUND(pp.creative_hours * 100.0 / (pp.creative_hours + pp.doc_hours), 1) AS creative_pct
FROM fact_content_doc_events cd
JOIN dim_producers p ON cd.producer_id = p.producer_id
JOIN dim_shows s ON cd.show_id = s.show_id
LEFT JOIN fact_content_quality cq ON cd.asset_id = cq.asset_id
LEFT JOIN fact_production_performance pp ON cd.show_id = pp.show_id AND cd.producer_id = pp.producer_id
WHERE cd.task_type = 'metadata_entry'
GROUP BY p.name, s.name, s.genre, pp.creative_hours, pp.doc_hours
ORDER BY avg_metadata_minutes DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Metadata entry time per episode | > 4 hours | > 6 hours |
| Metadata completeness rate | < 90% | < 75% |
| Auto-population rate | < 40% | < 20% |
| Creative-to-admin time ratio | < 55% creative | < 40% creative |

---

### UC-2: Rights Clearance Documentation

**Problem:** Rights clearance is the most documentation-intensive process in media — every piece of music, stock footage, talent likeness, brand placement, and archive clip requires verification of rights ownership, territory, window, and usage terms. A single episode can have 50–200 rights elements. Clearance involves sending requests, tracking responses, negotiating terms, documenting agreements, and maintaining audit trails — often across multiple territories and platforms.

**What the Platform Measures:**
- Rights clearance cycle time (request → response → agreement → filing)
- Documentation time per clearance by rights type (music, footage, talent, brand)
- Clearance bottleneck identification (holder response delays vs internal doc delays)
- Uncleared rights inventory: content held up by pending clearances
- Revenue at risk: content with partial clearance across territories

**Sample KQL Query — Real-Time Rights Pipeline:**
```kql
stream_rights_status
| where timestamp > ago(7d)
| summarize
    TotalClearances = count(),
    Pending = countif(status == "pending"),
    Approved = countif(status == "approved"),
    Denied = countif(status == "denied"),
    Expiring = countif(status == "expiring_soon")
  by rights_type, territory
| where Pending > 5 or Expiring > 0
| order by Pending desc
```

---

### UC-3: Ad Copy & Creative Approval Cycles

**Problem:** Advertising-supported content requires ad copy approval workflows involving legal review, standards & practices, client approval, and network clearance. Each ad placement requires documentation of creative specifications, compliance review, revision history, and final approval. During upfronts and peak advertising periods, approval documentation can bottleneck ad revenue realization.

**What the Platform Measures:**
- Approval cycle time by stage (creative, legal, S&P, client, network)
- Documentation overhead per approval type
- Revision count and documentation time per revision cycle
- Approval bottleneck identification: which stage causes the most delay
- Revenue impact: delayed approvals × ad rate

**Sample SQL Query — Approval Workflow Analysis:**
```sql
SELECT s.name AS show,
       aw.approval_type,
       COUNT(aw.approval_id) AS total_approvals,
       AVG(aw.cycle_time_hours) AS avg_cycle_hours,
       SUM(CASE WHEN aw.status = 'rejected' THEN 1 ELSE 0 END) AS rejections,
       SUM(CASE WHEN aw.status = 'pending' THEN 1 ELSE 0 END) AS pending,
       p.name AS producer,
       pp.on_time_pct
FROM fact_approval_workflows aw
JOIN dim_shows s ON aw.show_id = s.show_id
JOIN dim_producers p ON aw.producer_id = p.producer_id
LEFT JOIN fact_production_performance pp ON s.show_id = pp.show_id
GROUP BY s.name, aw.approval_type, p.name, pp.on_time_pct
ORDER BY avg_cycle_hours DESC;
```

---

### UC-4: Regulatory Compliance Documentation (FCC/GDPR)

**Problem:** Media companies must comply with FCC content regulations (broadcast), GDPR/CCPA data requirements (digital), accessibility standards (closed captioning, audio description), and regional content regulations. Each compliance area generates documentation requirements — content rating justifications, data processing records, accessibility certifications, and regulatory filing paperwork. Non-compliance carries fines and license revocation risk.

**What the Platform Measures:**
- Regulatory documentation hours per show by regulation type
- Compliance review cycle time (initial review → findings → remediation → sign-off)
- Accessibility documentation burden: captioning, audio description, language tracks
- Compliance finding remediation time
- Regulatory risk score: non-compliant assets × regulatory severity

**Sample KQL Query — QC & Compliance Monitoring:**
```kql
stream_qc_results
| where timestamp > ago(24h)
| summarize
    TotalChecks = count(),
    Failures = countif(result == "fail"),
    ComplianceFlags = countif(check_type has "compliance" or check_type has "regulatory"),
    CriticalErrors = countif(severity == "critical")
  by asset_id, check_type
| where Failures > 0 or CriticalErrors > 0
| order by CriticalErrors desc
```

---

### UC-5: Content Delivery & Distribution Documentation

**Problem:** Multi-platform distribution (broadcast, streaming, SVOD, AVOD, international) requires content to be prepared, documented, and delivered in platform-specific formats with corresponding metadata, rights verification, and technical specifications. Each platform has unique requirements, creating a multiplication effect on documentation burden as content is distributed across more platforms.

**What the Platform Measures:**
- Delivery documentation time per platform
- Platform-specific metadata adaptation effort
- Delivery rejection rate and re-delivery documentation overhead
- Multi-platform documentation multiplication factor
- Time from content completion to all-platform delivery

**Sample SQL Query — Delivery Performance:**
```sql
SELECT s.name AS show,
       pl.name AS platform,
       COUNT(cd.doc_id) AS episodes_delivered,
       AVG(cd.doc_time_min) AS avg_delivery_doc_min,
       cq.qc_pass_rate,
       cs.on_time_delivery_pct,
       cs.revision_count AS avg_revisions,
       pp.on_time_pct AS production_on_time
FROM fact_content_doc_events cd
JOIN dim_shows s ON cd.show_id = s.show_id
JOIN dim_platforms pl ON cd.asset_id IS NOT NULL
LEFT JOIN fact_content_quality cq ON cd.asset_id = cq.asset_id
LEFT JOIN fact_client_satisfaction cs ON s.show_id = cs.show_id
LEFT JOIN fact_production_performance pp ON s.show_id = pp.show_id
WHERE cd.task_type = 'delivery'
GROUP BY s.name, pl.name, cq.qc_pass_rate, cs.on_time_delivery_pct, cs.revision_count, pp.on_time_pct
ORDER BY avg_delivery_doc_min DESC;
```

**Operations Agent Alert Thresholds:**

| Metric | Warning | Critical |
|---|---|---|
| Content delivery to deadline | < 5 days | < 2 days |
| QC failure rate | > 10% | > 25% |
| Uncleared rights (days to air) | < 14 days | < 7 days |
| Platform-specific metadata gaps | > 5 fields | > 15 fields |

---

## Power BI Report Pages

| Page | Key Visuals | Business Question |
|---|---|---|
| **Executive Summary** | KPIs (content delivered, on-time %, rights cleared), show pipeline | _"How is our content pipeline performing?"_ |
| **Documentation Burden** | Metadata time, creative-to-admin ratio, producer workload heatmap | _"How much creative time is lost to documentation?"_ |
| **Rights Pipeline** | Clearance status by type/territory, cycle time, risk inventory | _"What content is at risk from rights gaps?"_ |
| **Delivery Performance** | Platform delivery status, rejection rates, multi-platform efficiency | _"Are we delivering on time across all platforms?"_ |

## Real-Time Dashboard Pages

| Page | KQL Source | Live Signal |
|---|---|---|
| **MAM Activity** | `stream_mam_activity` | Editor sessions, metadata updates, review actions |
| **Rights Tracker** | `stream_rights_status` | Clearance progress, expirations, approvals |
| **Delivery Pipeline** | `stream_delivery_tracking` | Transfer status, completion %, platform readiness |
| **QC Monitor** | `stream_qc_results` | Quality failures, compliance flags, critical issues |
| **Audience Response** | `stream_audience_metrics` | Viewer counts, engagement, completion rates |
