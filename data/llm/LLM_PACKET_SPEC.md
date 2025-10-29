# AI Sustainability Monitor Packet Specification

This specification describes the JSON structure required for successful ingestion by the AI Sustainability Monitor pipeline. LLM agents should follow this contract exactly. Keys are case-sensitive and arrays must be present even when empty.

## Top-level structure

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
  "briefings": [Briefing, ...],        // optional – auto-built from events when omitted
  "ai_infra_health_check": HealthCheck // optional but recommended when running the infra add-on
}
```

* `as_of` – ISO date of analysis (required).
* `methodology_note` – brief explanation of scoring approach.
* `thresholds` – numeric guardrails that map to the watch/elevated/critical banner.
* `overall` – aggregate view for the NSI hero (all fields required).
* `clusters` – ordered list of the six structural clusters summarising bullish/bearish posture.
* `events_update` – delta-style updates to the canonical event registry.
* `hard_metrics_summary` – dictionary keyed by metric code (`ccr`, `psr`, `uei`, `mg`, `fh`, etc.).
* `post` – HTML or Markdown payload for the daily briefing.
* `ai_infra_health_check` – structured supplement for infra-specific research (mirrors the template in `data/templates/ai_infra_health_check.template.json`).

## Cluster object

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

Each cluster entry must reference the canonical `id` values (`AI_CAPEX`, `POWER_GRID`, `SEMI_SUPPLY`, `UNIT_ECONOMICS`, `ENTERPRISE_DEMAND`, `POLICY_GEOPOLITICS`). Provide at least one rationale sentence and one source per cluster.

## Event update object

```json
{
  "uid": "ai_capex__meta-hyperion-spv-financing__2025-10-17", // optional; auto-generated if omitted
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
  "score": number,                       // 0–100 scale for infra tracker crosswalk
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

* Always include `fingerprint_fields.cluster` to keep history deterministic.
* `sources` should be raw URLs or plain-text citations (avoid Markdown link syntax).
* `brief` content must be third-person and free of helper tokens.

## Hard metric summary

Each key corresponds to a dashboard metric. Values differ by metric type.

```json
{
  "ccr": {"value": number, "tier": "watch", "note": "string"},
  "psr": {"value": number, "tier": "critical", "note": "string"},
  "uei": {"utilization_pct": number, "tier": "watch", "note": "string"}
}
```

* `tier` should map to `watch`, `elevated`, or `critical`.
* Notes provide a concise explanation of the data point.

## Post object

```json
{
  "slug": "nsi-daily-brief-2025-10-29",
  "title": "AI Sustainability Monitor Daily Brief — …",
  "format": "html" | "md" | "markdown",
  "content": "<h2>Daily Brief</h2><p>Third-person HTML narrative …</p>"
}
```

The `content` field must use sanitised HTML (no inline scripts, `style` attributes, or Markdown links).

## AI infrastructure health check

The optional `ai_infra_health_check` payload follows `data/templates/ai_infra_health_check.template.json`. Every entry requires explicit `status`, `score`, `confidence`, and verification timestamps. Arrays (`new_items`, `reevaluated_items`, `watchlist`, `red_flags`, `key_dates`) must be present even if empty.

```json
{
  "run_timestamp_utc": "2025-10-29T08:06:15Z",
  "new_items": [ { /* see template */ } ],
  "reevaluated_items": [ { "status": "Active", ... } ],
  "watchlist": [ { "name": "Item", "category": "Type", "score": number, "status": "Active", "last_verified": "YYYY-MM-DD" } ],
  "red_flags": [ ... ],
  "key_dates": [ { "date": "YYYY-MM-DD", "event": "Milestone", "source": "Citation", "notes": "Optional" } ]
}
```

## Formatting rules

* Encode JSON in UTF-8 and terminate the file with a newline.
* Use numeric literals (no words such as “fifty”) and avoid trailing commas.
* Provide explicit arrays even when empty (e.g., `"secondary_sources": []`).
* Use third-person, analytical tone throughout.
* Normalise whitespace; prefer standard ASCII punctuation except where units demand special characters (e.g., non-breaking space `\u00a0` for readability is acceptable).

Adhering to this contract ensures packets pass `scripts/validate_and_fix_llm_packet.py` and can be ingested without manual edits.
