"""Live acceptance receipt for the SignalOps × SerpApi hackathon path.

Run only with real SERPAPI_API_KEY and OPENAI_API_KEY credentials. The generated
receipt intentionally excludes credentials and preserves only source-linked evidence,
deterministic decisions, deduplication behavior, and immutable outcome state.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path

from signalops.core import Store
from signalops.serp_ai import OpportunityAssessor
from signalops.serpapi import SerpApiClient


def ensure_policy(store: Store) -> None:
    try:
        store.policy("serpapi")
    except KeyError:
        store.configure_policy(
            {
                "channel": "serpapi",
                "reply_threshold": 6.0,
                "dm_threshold": 8.0,
                "call_threshold": 9.0,
                "dm_requires_response": True,
            }
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="AI agent production reliability hiring OR looking for help",
    )
    parser.add_argument(
        "--goal",
        default=(
            "Find current, externally verifiable opportunities where a technical "
            "operator can create useful value."
        ),
    )
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--location", default="")
    parser.add_argument(
        "--output",
        default="artifacts/live/serpapi_hackathon_receipt.json",
    )
    args = parser.parse_args()

    db_path = Path(os.getenv("SIGNALOPS_DB", "data/hackathon-live.db"))
    store = Store(db_path)
    ensure_policy(store)

    evidence = SerpApiClient().search_google(
        args.query,
        limit=args.limit,
        location=args.location or None,
    )
    if not evidence:
        raise SystemExit("FAIL: SerpApi returned zero usable organic results")

    assessments = OpportunityAssessor().assess(evidence, goal=args.goal)
    if len(assessments) != len(evidence):
        raise SystemExit("FAIL: AI assessment count does not match evidence count")

    decisions: list[dict[str, object]] = []
    first_payload: dict[str, object] | None = None
    first_id = ""
    for source, assessment in zip(evidence, assessments, strict=True):
        payload = {
            "channel": "serpapi",
            "title": source.title,
            "url": source.url,
            "pain": assessment.inference,
            "exact_language": source.observed_fact,
            "relevance": assessment.relevance,
            "urgency": assessment.urgency,
            "conversation": assessment.conversation,
            "responded": False,
            "who": assessment.who or source.source,
        }
        surface, decision = store.process(**payload)
        if first_payload is None:
            first_payload = payload
            first_id = surface.external_id
        decisions.append(
            {
                "external_id": surface.external_id,
                "search_id": source.search_id,
                "position": source.position,
                "date": source.date,
                "source": source.source,
                "title": surface.title,
                "url": surface.url,
                "observed_fact": surface.exact_language,
                "inference": surface.pain,
                "who": surface.who,
                "decision": decision.to_dict(),
            }
        )

    assert first_payload is not None
    duplicate_surface, _ = store.process(**first_payload)
    stable_id_reused = duplicate_surface.external_id == first_id
    if not stable_id_reused:
        raise SystemExit("FAIL: repeated evidence did not preserve stable external ID")

    store.record_outcome(
        first_id,
        "saved",
        "Live hackathon acceptance receipt: source inspected and durable state verified.",
    )
    events = store.events(first_id)
    latest = events[-1]
    if latest["event_type"] != "outcome_recorded":
        raise SystemExit("FAIL: outcome receipt was not appended")

    receipt = {
        "receipt_version": 1,
        "captured_at": datetime.now(UTC).isoformat(),
        "query": args.query,
        "goal": args.goal,
        "serpapi_results": len(evidence),
        "serpapi_search_ids": sorted({row.search_id for row in evidence if row.search_id}),
        "model": os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        "decisions": decisions,
        "stable_id_reused_on_repeat": stable_id_reused,
        "first_entity_event_types": [event["event_type"] for event in events],
        "outcome_receipt": {
            "event_id": latest["id"],
            "occurred_at": latest["occurred_at"],
            "outcome": latest["payload"]["outcome"],
        },
        "claim_boundary": (
            "This receipt proves one live source-linked acquisition/assessment/policy/state "
            "run only. It does not prove user demand, revenue, conversion, or hackathon placement."
        ),
    }

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    print(f"PASS: wrote sanitized live receipt to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
