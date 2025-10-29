The scheduled task for the AI Infra Health Check is configured as follows:
# Name
```
TASKS: Run AI Infra Health Check
```
# Instructions
```
Search for AI infrastructure and compute‑financing announcements and updates in the last 3 days worldwide, and reevaluate previously tracked announcements using the AI Infra Health Check rubric below. Maintain a persistent Watchlist in this thread, updating each item’s status, score, and last_verified on every run. Treat this as an evidence‑based research brief: always read and cite primary sources first (press releases, SEC/EDGAR filings including 8‑K, 10‑Q, 10‑K, S‑1/F‑1, prospectuses, IR decks, utility or planning filings, regulator dockets). If a news article cites another outlet, click through to the earliest primary source before scoring. If details are uncertain or conflicting, mark them as uncertain and explain why.

Scope to scan each run
- Foundation models and AI platforms: OpenAI, Anthropic, Google, Meta, Microsoft, xAI, Cohere, Stability, Mistral, etc.
- Compute suppliers and integrators: Nvidia, AMD, Intel, Super Micro, HPE, Dell, Foxconn, Pegatron, Quanta, Inventec, Wiwynn, Broadcom.
- Hyperscalers and clouds: Azure, AWS, Google Cloud, Oracle Cloud, CoreWeave, Lambda, OCI.
- Data center and power ecosystem: Equinix, Digital Realty, Switch, QTS, CyrusOne, NextEra, Exelon, EDF, Engie, RWE, Ørsted, Iberdrola, national grid operators, ISO/RTOs, major PPAs, colocation builds, permits, interconnect queues.
- Key geographies: US, EU, UK, Middle East, India, Southeast Asia.

Rubric and weights (score 0‑100)
1) Economic substance 25 – cash flow reality, counterparties, capacity actually built or delivered; evidence includes site permits, interconnect, delivery photos, or utility filings.
2) Financing independence 20 – degree of vendor financing or circularity; supplier equity, loans, rebates, or warrants reduce this. Disclose any supplier‑investor‑customer overlaps.
3) Accounting clarity 15 – explicit treatment under ASC 606/IFRS 15 for consideration payable to a customer; net vs gross; warranty or warrant fair‑value disclosures; segment impacts.
4) Contract binding and phasing 15 – LOI vs definitive, milestones, termination clauses, penalties, and delivery schedules with dates and quantities (GW, MW, racks, accelerators).
5) Third‑party demand and utilization 15 – independent demand signals, utilization rates, attach of services, bookings, backlog, and customer diversity.
6) Concentration risk 5 – revenue or dependency on a single counterparty or site.
7) Policy, permitting, and grid risk 5 – regulatory, environmental, community, or grid constraints.

Automatic adjustments and red flags
- Supplier becomes investor or lender to the buyer → minus 5‑20 depending on size, terms, and vesting.
- Warrants or credits tied to purchases → reduce recognized revenue in scoring unless clearly separate and at fair value; note expected accounting treatment.
- Announcements without site, grid, or delivery specifics after 90 days → decay score by 5 each run until clarified.
- Slippages vs prior milestones → subtract 5 per missed milestone window and log in Diff.

Deliverables each run (post all sections clearly)
A) Executive snapshot – 5 bullet summary with overall traffic‑light status (Green ≥80, Yellow 60‑79, Orange 40‑59, Red <40) plus top risks and momentum.
B) New announcements (last 3 days) – for each item: who, what, where, size (GW/MW, racks, accelerator counts), term, financing terms, accounting notes, risks, score 0‑100, confidence 0‑100, and citations with primary sources first.
C) Reevaluation of Watchlist – rescore existing items, note milestone hits or slips, update last_verified, and show change in score with reason.
D) Scorecards – compact table listing entity, category, size, start date, next milestone, score, confidence, status.
E) Diff since last run – adds, removals, upgrades/downgrades, missed vs hit milestones.
F) Key dates – upcoming filings, earnings, regulator hearings, construction or interconnect milestones.
G) Sources – link and cite every primary source used; include secondary only if it adds new facts.
H) Machine‑readable JSON block at the end with the exact key name ai_infra_health_check, fields: run_timestamp_utc, new_items[], reevaluated_items[], watchlist[], red_flags[], key_dates[]. Use ISO 8601 dates and SI units. Keep it strictly valid JSON.

Scoring discipline and style
- Be cautious, neutral, and explicit about uncertainty. Never infer numbers that are not in sources. Prefer ranges if sources differ.
- When a company guides to revenue tied to a partner that also invested or issued warrants, flag potential circularity and note how ASC 606 would treat consideration payable to a customer.
- Always include unit conversions and definitions for GW, MW, rack counts, and accelerator counts where used.
- Keep language concise and analytical. Use bullet points, short sentences, and numeric specifics. Avoid hype.
```

## Machine-readable packet specification

The scheduled task must emit a machine-readable JSON block that fully conforms to the AI Sustainability Monitor packet contract. Use the following structure and field requirements when constructing the payload so downstream validators accept it without modification.

### Top-level envelope

```json
{
  "as_of": "YYYY-MM-DD",
  "methodology_note": "string",
  "thresholds": {"watch": number, "elevated": number, "critical": number},
  "overall": {
    "bullish_score_overall": number,
    "bearish_score_overall": number,
    "sustainability_index": number,
    "state": "watch" | "elevated" | "critical",
    "override_applied": boolean,
    "persistence_flag": boolean
  },
  "clusters": [Cluster, ...],
  "events_update": [EventUpdate, ...],
  "hard_metrics_summary": {MetricId: MetricSummary, ...},
  "post": Post,
  "briefings": [Briefing, ...],
  "ai_infra_health_check": HealthCheck
}
```

* Populate every key exactly as shown. Arrays (`clusters`, `events_update`, `briefings`) must exist even when empty.
* Dates (`as_of`, any `last_verified`, or `run_timestamp_utc`) use ISO 8601 format. Encode JSON as UTF-8 with no trailing commas and terminate the block with a newline.

### Cluster object

```json
{
  "id": "AI_CAPEX",
  "name": "AI Capex and Capacity",
  "bullish_score": number,
  "bearish_score": number,
  "phase": "watch" | "elevated" | "critical",
  "confidence": "high" | "medium" | "low",
  "rationale": ["string", ...],
  "indicators": {"metric_name": number | string, ...},
  "sources": ["plain URL or citation text", ...]
}
```

Use the canonical cluster `id` values (`AI_CAPEX`, `POWER_GRID`, `SEMI_SUPPLY`, `UNIT_ECONOMICS`, `ENTERPRISE_DEMAND`, `POLICY_GEOPOLITICS`). Provide at least one rationale entry and one source per cluster.

### Event update object

```json
{
  "uid": "ai_capex__meta-hyperion-spv-financing__2025-10-17",
  "fingerprint_fields": {
    "cluster": "AI_CAPEX",
    "event_type": "project_financing",
    "entity": "Meta Hyperion"
  },
  "title": "Concise event title",
  "phase": "watch" | "elevated" | "critical",
  "confidence": "high" | "medium" | "low",
  "bullish_score": number,
  "bearish_score": number,
  "score": number,
  "rationale": "One-sentence justification",
  "indicators": {"name": number | string, ...},
  "sources": ["URL or plain citation", ...],
  "brief": {
    "slug": "kebab-case-slug",
    "title": "Brief headline",
    "format": "html" | "md",
    "content": "Sanitised HTML fragment"
  }
}
```

Always include `fingerprint_fields.cluster` and at least one `sources` entry. `brief.content` must remain third-person and free of helper tokens.

### Hard metrics summary

```json
{
  "ccr": {"value": number, "tier": "watch", "note": "string"},
  "psr": {"value": number, "tier": "critical", "note": "string"},
  "uei": {"utilization_pct": number, "tier": "watch", "note": "string"}
}
```

Match tiers to `watch`, `elevated`, or `critical` and explain each data point with a concise note.

### Post object

```json
{
  "slug": "nsi-daily-brief-2025-10-29",
  "title": "AI Sustainability Monitor Daily Brief ...",
  "format": "html" | "md" | "markdown",
  "content": "<h2>Daily Brief</h2><p>Third-person HTML narrative ...</p>"
}
```

The `content` field must use sanitised HTML without inline scripts or Markdown link syntax.

### AI infrastructure health check payload

```json
{
  "run_timestamp_utc": "2025-10-29T08:06:15Z",
  "new_items": [ { /* object matching data/templates/ai_infra_health_check.template.json */ } ],
  "reevaluated_items": [ { "status": "Active", ... } ],
  "watchlist": [ { "name": "Item", "category": "Type", "score": number, "status": "Active", "last_verified": "YYYY-MM-DD" } ],
  "red_flags": [ ... ],
  "key_dates": [ { "date": "YYYY-MM-DD", "event": "Milestone", "source": "Citation", "notes": "Optional" } ]
}
```

Keep every array present, even when empty, and mirror the schema defined in `data/templates/ai_infra_health_check.template.json`. Use SI units and cite primary sources first.
