import unittest

from signalops.core import ValidationError
from signalops.market_return import (
    build_externalization_plan,
    record_market_outcome,
    summarize_market_return,
)


def base_kwargs():
    return {
        "route_key": "route-123",
        "contact_name": "Operator One",
        "company": "Example Logistics",
        "evidence_refs": ("clay:contact:123",),
    }


class MarketReturnTests(unittest.TestCase):
    def test_rapport_first_requires_real_personal_signal_and_starts_without_ask(self):
        with self.assertRaises(ValidationError):
            build_externalization_plan(
                **base_kwargs(),
                strategy="rapport_first",
                bounded_deliverable="A useful exception-flow observation",
            )

        plan = build_externalization_plan(
            **base_kwargs(),
            strategy="rapport_first",
            personal_signal="Published a concrete view on warehouse visibility",
            bounded_deliverable="A useful exception-flow observation",
        )

        self.assertEqual(plan.next_action, "human_review")
        self.assertEqual(plan.touches[0].purpose, "human_connection")
        self.assertEqual(plan.touches[0].ask, "")
        self.assertTrue(plan.touches[0].value_given)

    def test_useful_artifact_first_requires_artifact_before_ask(self):
        with self.assertRaises(ValidationError):
            build_externalization_plan(**base_kwargs(), strategy="useful_artifact_first")

        plan = build_externalization_plan(
            **base_kwargs(),
            strategy="useful_artifact_first",
            artifact_ref="https://example.test/operator-map",
        )

        self.assertEqual(plan.next_action, "human_review")
        self.assertEqual(plan.touches[0].purpose, "artifact_delivery")
        self.assertIn("wrong", plan.touches[0].ask)
        self.assertIn("https://example.test/operator-map", plan.touches[0].evidence_refs)

    def test_micro_pilot_requires_bounded_deliverable_and_adoption_receipt(self):
        with self.assertRaises(ValidationError):
            build_externalization_plan(
                **base_kwargs(),
                strategy="micro_pilot",
                bounded_deliverable="One-page reconstruction",
            )

        plan = build_externalization_plan(
            **base_kwargs(),
            strategy="micro_pilot",
            bounded_deliverable="One-page reconstruction from one sanitized exception",
            adoption_receipt="operator supplies a second case or explicitly reuses the output",
        )

        self.assertEqual(plan.next_action, "human_review")
        self.assertEqual(plan.touches[0].purpose, "show_finished_example")
        self.assertIn("sanitized", plan.touches[0].value_given)

    def test_reply_is_not_adoption_and_adoption_needs_evidence(self):
        plan = build_externalization_plan(
            **base_kwargs(),
            strategy="micro_pilot",
            bounded_deliverable="One-page reconstruction",
            adoption_receipt="second use",
        )

        reply = record_market_outcome(plan, outcome="human_reply")
        self.assertFalse(reply.is_adoption)
        self.assertFalse(reply.is_evidence_bearing)

        with self.assertRaises(ValidationError):
            record_market_outcome(plan, outcome="second_use")

        adoption = record_market_outcome(
            plan,
            outcome="second_use",
            evidence_ref="gmail:thread-receipt",
        )
        self.assertTrue(adoption.is_adoption)
        self.assertTrue(adoption.is_evidence_bearing)

    def test_summary_keeps_evidence_and_adoption_separate(self):
        rapport = build_externalization_plan(
            **base_kwargs(),
            strategy="rapport_first",
            personal_signal="Verified public viewpoint",
            bounded_deliverable="Useful observation",
        )
        artifact = build_externalization_plan(
            route_key="route-456",
            contact_name="Operator Two",
            company="Example Freight",
            strategy="useful_artifact_first",
            artifact_ref="https://example.test/map",
        )

        receipts = [
            record_market_outcome(rapport, outcome="human_reply"),
            record_market_outcome(
                artifact,
                outcome="correction",
                evidence_ref="reply:correction-1",
            ),
            record_market_outcome(
                artifact,
                outcome="pilot_used",
                evidence_ref="pilot:use-1",
            ),
        ]
        summary = summarize_market_return(receipts)

        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["by_strategy"]["rapport_first"]["adoption"], 0)
        self.assertEqual(
            summary["by_strategy"]["useful_artifact_first"]["evidence_bearing"], 2
        )
        self.assertEqual(summary["by_strategy"]["useful_artifact_first"]["adoption"], 1)


if __name__ == "__main__":
    unittest.main()
