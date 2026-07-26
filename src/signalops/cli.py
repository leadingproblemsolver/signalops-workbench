"""Command-line interface for the SignalOps workbench."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys
from typing import Sequence

from .core import Store, ValidationError


def _emit(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def _policy_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise ValidationError(f"channel policy directory not found: {directory}")
    files = sorted(directory.glob("*.json"))
    if not files:
        raise ValidationError(f"no channel policy JSON files found in {directory}")
    return files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="signalops",
        description="Turn public evidence into permission-safe ranked next actions.",
    )
    parser.add_argument("--db", default=".signalops/signalops.db")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Load channel policy JSON files")
    init.add_argument("--channels", required=True, type=Path)

    add = commands.add_parser("add-surface", help="Score and persist one evidence surface")
    for name in ("channel", "title", "url", "pain", "exact-language"):
        add.add_argument(f"--{name}", required=True)
    add.add_argument("--external-id", default="")
    add.add_argument("--who", default="")
    add.add_argument("--relevance", type=float, required=True)
    add.add_argument("--urgency", type=float, required=True)
    add.add_argument("--conversation", type=float, required=True)
    add.add_argument("--responded", action="store_true")

    next_actions = commands.add_parser("next-actions", help="List ranked actions")
    next_actions.add_argument("--channel")

    handoff = commands.add_parser("handoff", help="Write a restartable Markdown handoff")
    handoff.add_argument("--channel", required=True)
    handoff.add_argument("--output", required=True, type=Path)

    export = commands.add_parser("export-crm", help="Export the current projection to CSV")
    export.add_argument("--output", required=True, type=Path)

    outcome = commands.add_parser("record-outcome", help="Append an outcome event")
    outcome.add_argument("--external-id", required=True)
    outcome.add_argument("--outcome", required=True)
    outcome.add_argument("--notes", default="")

    events = commands.add_parser("events", help="Read immutable event history")
    events.add_argument("--external-id")

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    store = Store(args.db)

    try:
        if args.command == "init":
            policies = []
            for file_path in _policy_files(args.channels):
                payload = json.loads(file_path.read_text(encoding="utf-8"))
                policies.append(store.configure_policy(payload).channel)
            _emit({"configured_channels": policies})

        elif args.command == "add-surface":
            surface, decision = store.process(
                external_id=args.external_id,
                channel=args.channel,
                title=args.title,
                url=args.url,
                who=args.who,
                pain=args.pain,
                exact_language=args.exact_language,
                relevance=args.relevance,
                urgency=args.urgency,
                conversation=args.conversation,
                responded=args.responded,
            )
            _emit({"external_id": surface.external_id, **decision.to_dict()})

        elif args.command == "next-actions":
            _emit(store.rows(args.channel))

        elif args.command == "handoff":
            rows = store.rows(args.channel)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            lines = [
                "# SignalOps handoff",
                "",
                f"Channel: `{args.channel.strip().lower()}`",
                "",
                "## Ranked permission-safe actions",
                "",
            ]
            if rows:
                lines.extend(
                    f"- **{row['action']}** ({row['score']:.2f}) — "
                    f"[{row['title']}]({row['url']}): “{row['exact_language']}”"
                    for row in rows
                )
            else:
                lines.append("No evidence surfaces are currently queued.")
            lines.extend(
                [
                    "",
                    "## Continuation point",
                    "",
                    "Execute the highest-ranked permission-safe action, then record "
                    "the observed outcome with `signalops record-outcome`.",
                    "",
                ]
            )
            args.output.write_text("\n".join(lines), encoding="utf-8")
            _emit({"output": str(args.output), "items": len(rows)})

        elif args.command == "export-crm":
            rows = store.rows()
            args.output.parent.mkdir(parents=True, exist_ok=True)
            fieldnames = list(rows[0]) if rows else [
                "external_id",
                "channel",
                "title",
                "url",
                "who",
                "pain",
                "exact_language",
                "relevance",
                "urgency",
                "conversation",
                "responded",
                "action",
                "score",
                "reason",
                "created_at",
                "updated_at",
            ]
            with args.output.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            _emit({"output": str(args.output), "items": len(rows)})

        elif args.command == "record-outcome":
            store.record_outcome(args.external_id, args.outcome, args.notes)
            _emit({"external_id": args.external_id, "outcome": args.outcome})

        elif args.command == "events":
            _emit(store.events(args.external_id))

        return 0
    except (ValidationError, KeyError, json.JSONDecodeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
