from __future__ import annotations

from datetime import UTC, datetime
import unittest

from signalops.core import ValidationError
from signalops.pql import (
    ActivationAction,
    PQLPolicy,
    PQLState,
    ProductUsageSignal,
    build_handoff,
    decide_pql,
)


NOW = datetime(2026, 8, 22, 0, 0, tzinfo=UTC)


def signal(**overrides):
    data = {
        "account_id": "acct-001",
        "observed_at": "2026-08-21T23:00:00+00:00",
        "weekly_active_users": 18,
        "previous_weekly_active_users": 12,
        "purchased_seats": 20,
        "active_seats": 18,
        "key_feature_users": 14,
        "admin_invites_7d": 4,
        "owner": "ae@example.com",
        "source": "posthog",
    }
    data.update(overrides)
    return ProductUsageSignal(**data)


class PQLActivationTests(unittest.TestCase):
    def test_strong_fresh_usage_routes_expansion(self):
        decision = decide_pql(signal(), now=NOW)
        self.assertEqual(decision.state, PQLState.EXPANSION_READY)
        self.assertEqual(decision.action, ActivationAction.ROUTE_EXPANSION)
        self.assertGreaterEqual(decision.score, 8)

    def test_missing_owner_blocks_automatic_routing(self):
        decision = decide_pql(signal(owner=""), now=NOW)
        self.assertEqual(decision.state, PQLState.REVIEW)
        self.assertEqual(decision.action, ActivationAction.HUMAN_REVIEW)

    def test_stale_evidence_never_routes_even_with_high_usage(self):
        decision = decide_pql(
            signal(observed_at="2026-08-15T00:00:00+00:00"),
            now=NOW,
        )
        self.assertEqual(decision.state, PQLState.STALE)
        self.assertEqual(decision.action, ActivationAction.MONITOR)

    def test_low_activity_remains_monitor(self):
        decision = decide_pql(
            signal(
                weekly_active_users=1,
                previous_weekly_active_users=1,
                active_seats=1,
                key_feature_users=1,
                admin_invites_7d=0,
            ),
            now=NOW,
        )
        self.assertEqual(decision.state, PQLState.MONITOR)
        self.assertEqual(decision.action, ActivationAction.MONITOR)

    def test_missing_seat_denominator_requires_review(self):
        decision = decide_pql(
            signal(purchased_seats=0, active_seats=0),
            now=NOW,
        )
        self.assertEqual(decision.state, PQLState.REVIEW)
        self.assertEqual(decision.action, ActivationAction.HUMAN_REVIEW)

    def test_future_timestamp_requires_review(self):
        decision = decide_pql(
            signal(observed_at="2026-08-22T02:00:00+00:00"),
            now=NOW,
        )
        self.assertEqual(decision.state, PQLState.REVIEW)
        self.assertEqual(decision.action, ActivationAction.HUMAN_REVIEW)

    def test_handoff_is_deterministic_and_preserves_evidence(self):
        current = signal()
        decision = decide_pql(current, now=NOW)
        one = build_handoff(current, decision)
        two = build_handoff(current, decision)
        self.assertEqual(one["handoff_id"], two["handoff_id"])
        self.assertEqual(one["account_id"], "acct-001")
        self.assertEqual(one["evidence"]["source"], "posthog")
        self.assertEqual(
            one["expected_destination_state"]["pql_state"],
            "expansion_ready",
        )

    def test_non_routable_decision_cannot_build_handoff(self):
        current = signal(weekly_active_users=1, active_seats=1, key_feature_users=1)
        decision = decide_pql(current, now=NOW)
        with self.assertRaisesRegex(ValidationError, "not routable"):
            build_handoff(current, decision)

    def test_thresholds_are_monotonic(self):
        with self.assertRaisesRegex(ValidationError, "qualification <= expansion"):
            PQLPolicy(qualification_threshold=9, expansion_threshold=8)


if __name__ == "__main__":
    unittest.main()
