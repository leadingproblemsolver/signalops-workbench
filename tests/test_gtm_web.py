from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from signalops import gtm_web
from signalops.gtm_ingress import ReceiptStore


class GTMWebTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.original_store = gtm_web.store
        gtm_web.store = ReceiptStore(Path(self.directory.name) / "receipts.jsonl")

    def tearDown(self) -> None:
        gtm_web.store = self.original_store
        self.directory.cleanup()

    def body(self) -> gtm_web.ClayIngressIn:
        return gtm_web.ClayIngressIn(
            account=gtm_web.AccountIn(name="Example Logistics", domain="example.com"),
            contact=gtm_web.ContactIn(
                title="Digital Transformation Director",
                source_id="clay:contact:42",
            ),
            signals=[
                gtm_web.SignalIn(
                    type="fact",
                    value="Public systems-integration signal",
                    source_ref="https://example.com/source",
                )
            ],
            fit_reasons=["role owns systems integration"],
        )

    def test_endpoint_records_once_then_reports_duplicate(self) -> None:
        first = gtm_web.clay_event(self.body(), None)
        second = gtm_web.clay_event(self.body(), None)

        self.assertEqual(first["status"], "recorded")
        self.assertTrue(first["persisted"])
        self.assertEqual(first["receipt"]["next_action"], "human_review")
        self.assertFalse(first["receipt"]["send_actions_executed"])
        self.assertFalse(first["receipt"]["crm_mutation_executed"])
        self.assertEqual(second["status"], "duplicate")
        self.assertFalse(second["persisted"])

    def test_dashboard_is_sanitized_and_employer_readable(self) -> None:
        gtm_web.clay_event(self.body(), None)
        html = gtm_web.gtm_dashboard()

        self.assertIn("Clay research", html)
        self.assertIn("Example Logistics", html)
        self.assertIn("Digital Transformation Director", html)
        self.assertIn("human_review", html)
        self.assertNotIn("clay:contact:42", html)


if __name__ == "__main__":
    unittest.main()
