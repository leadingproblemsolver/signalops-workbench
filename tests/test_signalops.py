from __future__ import annotations

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest

from signalops.core import Action, Policy, Store, Surface, ValidationError, decide, stable_id
from signalops.cli import main


POLICY = {
    "channel": "reddit",
    "reply_threshold": 6,
    "dm_threshold": 8,
    "call_threshold": 9,
    "dm_requires_response": True,
}


class SignalOpsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.store = Store(self.root / "signalops.db")
        self.store.configure_policy(POLICY)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def add(self, **overrides):
        data = {
            "channel": "reddit",
            "title": "Context loss",
            "url": "https://example.com/thread#reply",
            "pain": "handoff",
            "exact_language": "We restart every shift.",
            "relevance": 9,
            "urgency": 8,
            "conversation": 9,
            "responded": False,
            "who": "SRE",
        }
        data.update(overrides)
        return self.store.process(**data)

    def test_permission_gate_blocks_private_escalation(self) -> None:
        _, decision = self.add()
        self.assertEqual(decision.action, Action.PUBLIC_REPLY)

    def test_call_requires_response_and_threshold(self) -> None:
        _, decision = self.add(
            responded=True,
            relevance=10,
            urgency=10,
            conversation=10,
        )
        self.assertEqual(decision.action, Action.CALL)

    def test_low_relevance_is_ignored_even_with_urgency(self) -> None:
        _, decision = self.add(relevance=3, urgency=10, conversation=10)
        self.assertEqual(decision.action, Action.IGNORE)

    def test_policy_thresholds_must_be_monotonic(self) -> None:
        with self.assertRaisesRegex(ValidationError, "reply <= dm <= call"):
            Policy("reddit", reply_threshold=8, dm_threshold=6, call_threshold=9)

    def test_channel_mismatch_is_rejected(self) -> None:
        surface = Surface(
            channel="linkedin",
            title="Problem",
            url="https://example.com/a",
            pain="manual work",
            exact_language="This is slow.",
            relevance=8,
            urgency=8,
            conversation=8,
        )
        with self.assertRaisesRegex(ValidationError, "does not match policy"):
            decide(surface, Policy("reddit"))

    def test_url_canonicalization_produces_stable_id(self) -> None:
        one = stable_id("Reddit", "HTTPS://EXAMPLE.COM/a#fragment", "Issue")
        two = stable_id("reddit", "https://example.com/a", "Issue")
        self.assertEqual(one, two)

    def test_upsert_is_idempotent_but_event_history_is_preserved(self) -> None:
        self.add(external_id="same")
        self.add(external_id="same", pain="updated")
        rows = self.store.rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["pain"], "updated")
        self.assertEqual(
            [event["event_type"] for event in self.store.events("same")],
            ["surface_created", "surface_updated"],
        )

    def test_events_are_immutable_at_database_level(self) -> None:
        self.add(external_id="same")
        connection = sqlite3.connect(self.store.path)
        try:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("DELETE FROM events")
        finally:
            connection.close()

    def test_record_outcome_requires_existing_surface(self) -> None:
        with self.assertRaises(KeyError):
            self.store.record_outcome("missing", "replied")
        self.add(external_id="same")
        self.store.record_outcome("same", "responded", "Asked for demo")
        self.assertEqual(self.store.events("same")[-1]["event_type"], "outcome_recorded")

    def test_rank_order_is_deterministic(self) -> None:
        self.add(external_id="low", relevance=6, urgency=6, conversation=6)
        self.add(external_id="high", relevance=10, urgency=10, conversation=10)
        self.assertEqual([row["external_id"] for row in self.store.rows()], ["high", "low"])

    def test_cli_initializes_and_exports_empty_csv(self) -> None:
        channels = self.root / "channels"
        channels.mkdir()
        (channels / "reddit.json").write_text(json.dumps(POLICY), encoding="utf-8")
        db = self.root / "cli.db"
        output = self.root / "nested" / "crm.csv"
        self.assertEqual(main(["--db", str(db), "init", "--channels", str(channels)]), 0)
        self.assertEqual(main(["--db", str(db), "export-crm", "--output", str(output)]), 0)
        self.assertIn("external_id", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
