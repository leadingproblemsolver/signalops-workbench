from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path

from signalops.pql import ProductUsageSignal, build_handoff, decide_pql


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate account usage signals into PQL/expansion actions."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument(
        "--now",
        required=True,
        help="ISO-8601 evaluation time, e.g. 2026-08-22T00:00:00+00:00",
    )
    return parser.parse_args()


def parse_now(value: str) -> datetime:
    current = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if current.tzinfo is None:
        raise ValueError("--now must include a timezone")
    return current.astimezone(UTC)


def main() -> int:
    args = parse_args()
    now = parse_now(args.now)
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    results = []

    for item in payload:
        signal = ProductUsageSignal(**item)
        decision = decide_pql(signal, now=now)
        result = {
            "account_id": signal.account_id,
            "decision": decision.to_dict(),
        }
        if decision.action.value.startswith("route_"):
            result["handoff"] = build_handoff(signal, decision)
        results.append(result)

    print(json.dumps(results, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
