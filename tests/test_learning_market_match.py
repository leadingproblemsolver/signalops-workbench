import json
from datetime import date
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from learning_market_match import (  # noqa: E402
    parse_issue_body,
    rank_matches,
    run_from_event,
    validate_learner,
)


ISSUE_BODY = """### Learner status

Current student

### Age

20

### Current learning

Probability and Statistics; Electric Circuits

### Capabilities you can already exercise

basic circuit analysis, probability/statistics, Python data analysis

### Access / equipment

Laptop, breadboard, basic sensors; no Arduino UNO Q

### Location

Qatar

### Hours available this week

6

### Evidence you want

External evaluation
"""


class LearningMarketEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((ROOT / "data" / "learning_market_opportunities.json").read_text(encoding="utf-8"))

    def test_issue_form_parses_into_real_learner_state(self):
        fields = parse_issue_body(ISSUE_BODY)
        learner = validate_learner(fields)
        self.assertTrue(learner["is_student"])
        self.assertEqual(learner["age_number"], 20)
        self.assertEqual(learner["hours_number"], 6.0)
        self.assertIn("Electric Circuits", learner["current_learning"])

    def test_probability_and_circuits_routes_to_current_volthacks_action(self):
        learner = validate_learner(parse_issue_body(ISSUE_BODY))
        ranked, rejected = rank_matches(learner, self.registry, as_of=date(2026, 9, 9))
        self.assertTrue(ranked)
        self.assertEqual(ranked[0]["opportunity"]["id"], "volthacks-2026")
        rejection = {row["id"]: row["reason"] for row in rejected}
        self.assertIn("arduino-uno-q-2026", rejection)
        self.assertIn("requires existing access", rejection["arduino-uno-q-2026"])

    def test_complete_event_returns_external_action_and_receipt_contract(self):
        code, markdown = run_from_event(
            {"issue": {"body": ISSUE_BODY, "number": 999}},
            self.registry,
            as_of=date(2026, 9, 9),
        )
        self.assertEqual(code, 0)
        self.assertIn("Learning → Market Evidence — ACTIONABLE", markdown)
        self.assertIn("VoltHacks 2026", markdown)
        self.assertIn("Join VoltHacks on Devpost now", markdown)
        self.assertIn("reply to this issue with the external receipt", markdown)
        self.assertIn("lme_", markdown)

    def test_expired_registry_fails_closed_with_retry_instructions(self):
        code, markdown = run_from_event(
            {"issue": {"body": ISSUE_BODY, "number": 999}},
            self.registry,
            as_of=date(2026, 11, 16),
        )
        self.assertEqual(code, 3)
        self.assertIn("NO ELIGIBLE CURRENT ACTION", markdown)
        self.assertIn("expired", markdown)
        self.assertIn("Edit this issue", markdown)

    def test_missing_capability_is_bounded_input_failure(self):
        body = ISSUE_BODY.replace(
            "basic circuit analysis, probability/statistics, Python data analysis",
            "_No response_",
        )
        code, markdown = run_from_event(
            {"issue": {"body": body}},
            self.registry,
            as_of=date(2026, 9, 9),
        )
        self.assertEqual(code, 2)
        self.assertIn("INPUT FAILURE", markdown)
        self.assertIn("capability", markdown.lower())
        self.assertIn("Edit the issue", markdown)


if __name__ == "__main__":
    unittest.main()
