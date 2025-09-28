# AI Sustainability Monitor

Static reporting stack that tracks whether the current AI investment boom is on sustainable footing. The site ingests structured
JSON packets, rebuilds the sustainability index, refreshes cluster briefings, and updates hard-metric dashboards so every change
is deterministic and auditable.

## Repository layout

| Path | Purpose |
| --- | --- |
| `index.html` | Homepage with the sustainability index hero, cluster health table, latest briefings, and hard-metrics dashboard. |
| `methodology.html` | Public reference explaining scoring weights, decay logic, and data provenance mirrored in this README. |
| `glossary.html` | Definitions for index states, confidence bands, tiers, and ingestion fields (with update provenance). |
| `posts/` | Generated HTML briefings for daily summaries and per-cluster events. Regenerated on every ingest run. |
| `data/events.json` | Canonical registry of every tracked event with fingerprints, history, rationale, indicators, and sources. |
| `data/leaderboard.json` | Sustainability snapshot: overall state, cluster NSI values, thresholds, top-pressures list, and hard metrics. |
| `data/latest_briefings.json` | Lightweight feed powering the “Latest briefings” homepage cards. |
| `data/briefings_archive.json` | Full archive index used by `posts/index.html` for infinite scrolling of every published briefing. |
| `data/llm/` | Drop zone for raw Deep Research packets (`YYYY-MM-DD[(-HHMM)].packet.json`); the newest file per day is ingested. |
| `assets/` | Site styles, favicons, and JavaScript that power navigation, latest-briefing cards, and confirmation links. |
| `scripts/` | Python utilities that validate packets, dedupe events, compute NSI scores, and regenerate JSON + HTML outputs. |

## Daily research pipeline

Every publication cycle is repeatable and machine-verifiable.

### 1. Deep research prompt

* Analysts run the "AI Sustainability Monitor" Deep Research brief focused on six structural clusters (capex, power, semis,
  unit economics, demand, policy/geopolitics).
* The prompt requires Amsterdam time, explicit ISO `as_of` dates, and consistent fingerprints so the registry can track events
  over time.
* Each update includes both bullish and bearish qualitative scores plus quantitative indicators and primary sources.

### 2. Structured packet format

The agent responds with deterministic JSON. Required top-level keys are `as_of`, `overall`, `thresholds`, `clusters`,
`hard_metrics_summary`, `events_update`, and `post`, with optional `briefings` for additional write-ups.

Each `events_update` entry contains fingerprint fields, bullish and bearish scores, phase (`watch`, `elevated`, `critical`),
confidence, indicators, tripwires, rationale, sources, and an HTML `brief` fragment. Clusters mirror the higher-level view.
Hard metrics supply unit data (ratios, utilisation, spreads) that anchor the narrative.

A trimmed example:

```json
{
  "as_of": "2025-09-28",
  "overall": {
    "bullish_score_overall": 58,
    "bearish_score_overall": 56.3,
    "sustainability_index": 50.9,
    "state": "watch"
  },
  "thresholds": {"X": 50, "Y": 40, "Z": 30},
  "clusters": [
    {
      "id": "AI_CAPEX",
      "name": "AI Capex and Capacity",
      "bullish_score": 65,
      "bearish_score": 55,
      "phase": "elevated",
      "confidence": "medium",
      "rationale": ["Hyperscalers spent ~$210B on AI data-center capex in 2024"],
      "indicators": {"latest_capex_guidance_usd_b": 210},
      "sources": ["https://newmark.com/2025-us-data-center-market-outlook"]
    }
  ],
  "hard_metrics_summary": {
    "ccr": {
      "value": 0.25,
      "tier": "x",
      "note": "Estimated using OpenAI revenue versus depreciation+interest and opex for installed AI capacity"
    }
  },
  "events_update": [
    {
      "uid": "AI_CAPEX__hyperscalers-ai-capex-boom__2025-09-28",
      "fingerprint_fields": {"cluster": "AI_CAPEX", "event_type": "investment_update"},
      "title": "Hyperscalers Expand AI Capex Amid $7 Trillion Buildout",
      "phase": "elevated",
      "bullish_score": 65,
      "bearish_score": 55,
      "brief": {"slug": "hyperscalers-ai-capex-boom", "title": "Hyperscalers Expand AI Capex Amid $7 Trillion Buildout"}
    }
  ],
  "post": {
    "slug": "nsi-daily-brief-2025-09-28",
    "title": "AI Sustainability Monitor Daily Brief — Watch State",
    "format": "html",
    "content": "<h2>Daily Brief</h2><p>…</p>"
  }
}
```

### 3. Deterministic ingest

Running `python scripts/ingest_llm_packet.py`:

1. Selects the newest packet per `as_of` date and validates required keys.
2. Normalises URLs, clamps derived NSI scores, and canonicalises fingerprints.
3. Merges updates into `data/events.json`, preserving score history, sources, indicators, and tripwires.
4. Applies score decay (three points per day after seven days for watch/elevated/critical phases).
5. Writes/refreshes per-event briefings, latest-briefing feed, and archive index.
6. Builds the sustainability snapshot (`data/leaderboard.json`) including overall NSI, sorted cluster scores, top-pressure list,
   thresholds, methodology note, and formatted hard metrics.
7. Emits the daily post (`posts/<slug>.html`) using the shared template.

The process is idempotent: ingesting the same packet twice yields byte-identical JSON and HTML outputs.

## Data lifecycle & reuse

* **Event registry (`data/events.json`):** Canonical source for every tracked development with fingerprints, score histories,
  and article provenance.
* **Sustainability snapshot (`data/leaderboard.json`):** Contains the latest overall NSI, cluster rankings, threshold guidance,
  top-pressures list, and formatted hard metrics consumed by the homepage.
* **Latest feed (`data/latest_briefings.json`):** Powers the homepage cards and can syndicate recent briefings elsewhere.
* **Archive (`data/briefings_archive.json`):** Full publication history used by `posts/index.html` and external dashboards.
* **Posts (`posts/*.html`):** Daily brief plus individual cluster briefs rendered with consistent chrome and metadata chips.

All JSON is UTF-8 encoded, newline-terminated, and safe for downstream automation.

## Working locally

The project is pure static HTML/CSS/JS.

1. Install Python 3.9+ (standard library only).
2. Start a simple web server from the repo root:

   ```bash
   python -m http.server 8000
   ```

3. Visit `http://localhost:8000/index.html` to explore the sustainability dashboard and briefings.

## Updating data manually

1. Save the latest Deep Research response as `data/llm/YYYY-MM-DD.packet.json` (append `-HHMM` for multiple intraday packets).
2. (Optional) Run `python scripts/check_and_fix_packet.py <path> -o data/llm/<date>.packet.json` to auto-correct minor schema
   issues using the bundled validator.
3. Execute the ingest script:

   ```bash
   python scripts/ingest_llm_packet.py
   ```

4. Commit regenerated JSON files and posts.

`scripts/ci_acceptance_checks.py` can be wired into CI/pre-commit to ensure packets include mandatory keys, mirror their briefs,
use third-person tone, and keep HTML sanitised.

## Extending the monitor

* Enhance the front-end by editing the static HTML/CSS or extending `assets/js/main.js` (navigation + confirmations) and
  `assets/js/latest.js` (latest-briefing cards).
* Add new derived metrics or alternative weightings by building on `scripts/ingest_llm_packet.py`; favour deterministic
  transforms so audit trails remain intact.
* Fork the registry (`data/*.json`) to seed your own analytics dashboards or alerting systems.

For background on scoring heuristics, decay, and provenance updates, read `methodology.html` and `glossary.html` alongside this
operator’s guide.
