import copy
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from scripts.ingest_llm_packet import (
    canonicalize_fingerprint_fields,
    compute_fingerprint,
    create_event,
    find_similar_event,
    merge_event,
    render_article_history_section,
    compute_sustainability_index,
)


BASE_FIELDS = {
    "cluster": "ai_capex",
    "event_type": "investment_update",
    "primary_entities": ["Hyperscalers", "Microsoft"],
    "geography": ["global", "united_states"],
    "instruments": ["data_centers", "infrastructure"],
    "mechanism": "ai_capex_expansion",
}


def test_canonical_source_is_ignored_by_fingerprint():
    fields_a = canonicalize_fingerprint_fields(
        {**BASE_FIELDS, "canonical_source": "newmark.com"}
    )
    fields_b = canonicalize_fingerprint_fields(
        {**BASE_FIELDS, "canonical_source": "reuters.com"}
    )

    assert compute_fingerprint(fields_a) == compute_fingerprint(fields_b)


def test_merging_updates_tracks_sources_and_history():
    canonical_initial = canonicalize_fingerprint_fields(
        {**BASE_FIELDS, "canonical_source": "newmark.com"}
    )
    fingerprint = compute_fingerprint(canonical_initial)
    payload_initial = {
        "cluster": BASE_FIELDS["cluster"],
        "event_type": BASE_FIELDS["event_type"],
        "title": "Hyperscalers Expand AI Capex Amid $7 Trillion Buildout",
        "phase": "watch",
        "bullish_score": 65,
        "bearish_score": 55,
        "score": 55,
        "confidence": "medium",
        "indicators": {"capex_2024_b": 210},
        "tripwires": ["capex_guidance_cuts"],
        "rationale": ["Hyperscaler spend remains elevated"],
        "sources": ["https://example.com/initial"],
    }
    event = create_event(canonical_initial, fingerprint, payload_initial, "2025-09-24")

    second_fields = canonicalize_fingerprint_fields(
        {**BASE_FIELDS, "canonical_source": "reuters.com"}
    )
    fingerprint_second = compute_fingerprint(second_fields)
    assert fingerprint_second == fingerprint

    payload_second = copy.deepcopy(payload_initial)
    payload_second.update(
        {
            "title": "Hyperscalers Signal AI Capex Discipline",
            "score": 58,
            "bullish_score": 60,
            "bearish_score": 46,
            "sources": ["https://reuters.com/technology/example"],
        }
    )

    merge_event(event, payload_second, second_fields, fingerprint_second, "2025-09-25")

    assert event["canonical_source"] == "https://reuters.com"
    assert {"https://reuters.com", "https://newmark.com"}.issubset(set(event["sources"]))

    assert len(event["history"]) == 2
    assert event["history"][-1] == {"date": "2025-09-25", "score": event["score"]}

    assert len(event["article_history"]) == 2
    latest_article = event["article_history"][-1]
    assert latest_article["source"] == "https://reuters.com"
    assert latest_article["score"] == event["score"]
    assert "https://reuters.com/technology/example" in latest_article["sources"]
    expected_nsi = compute_sustainability_index(payload_second["bullish_score"], payload_second["bearish_score"])
    assert event["sustainability_index"] == expected_nsi


def test_find_similar_event_detects_near_match():
    canonical_initial = canonicalize_fingerprint_fields(
        {**BASE_FIELDS, "canonical_source": "newmark.com"}
    )
    fingerprint = compute_fingerprint(canonical_initial)
    payload_initial = {
        "cluster": BASE_FIELDS["cluster"],
        "event_type": BASE_FIELDS["event_type"],
        "title": "Hyperscalers Expand AI Capex Amid $7 Trillion Buildout",
        "phase": "watch",
        "bullish_score": 65,
        "bearish_score": 55,
        "score": 55,
        "confidence": "medium",
        "indicators": {},
        "tripwires": [],
        "rationale": [],
        "sources": [],
    }
    event = create_event(canonical_initial, fingerprint, payload_initial, "2025-09-24")
    events_by_fp = {fingerprint: event}

    new_fields = canonicalize_fingerprint_fields(
        {
            "cluster": "ai_capex",
            "event_type": "investment_update",
            "primary_entities": ["Hyperscalers", "Microsoft"],
            "geography": ["global", "united_states", "canada"],
            "instruments": ["data_centers", "infrastructure", "power"],
            "mechanism": "ai_capex_expansion",
            "canonical_source": "reuters.com",
        }
    )

    match = find_similar_event(
        new_fields,
        events_by_fp,
        title="Hyperscalers Signal AI Capex Discipline",
    )

    assert match is not None
    matched_event, score = match
    assert matched_event is event
    assert score >= 0.7


def test_article_history_renders_newest_first():
    html = render_article_history_section(
        {
            "article_history": [
                {
                    "date": "2025-09-24",
                    "title": "Initial outlook",
                    "sources": ["https://example.com/original"],
                    "score": 55,
                },
                {
                    "date": "2025-09-25",
                    "title": "Follow-up assessment",
                    "sources": ["https://example.com/update"],
                    "score": 58,
                },
            ]
        }
    )

    assert "Update history" in html

    tbody = html.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
    assert tbody.count("<tr>") == 2

    first_row = tbody.split("</tr>", 1)[0]

    assert "25 September 2025" in first_row
    assert "Follow-up assessment" in first_row
