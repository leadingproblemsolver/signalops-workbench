from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from signalops.saas import SaaSStore


class SaaSMetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = SaaSStore(str(Path(self.temp.name) / "signalops.db"))
        self.store.core.configure_policy({"channel": "reddit"})
        self.surface, _ = self.store.core.process(
            channel="reddit",
            title="Hiring signal",
            url="https://example.com/thread",
            pain="manual account research",
            exact_language="We spend hours qualifying these accounts.",
            relevance=9,
            urgency=8,
            conversation=9,
            who="VP Sales",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_metrics_keep_observed_and_estimated_values_separate(self) -> None:
        self.store.record_review(
            self.surface.external_id,
            outcome="call_booked",
            investigation_minutes=4,
            manual_baseline_minutes=20,
            pipeline_value=5000,
        )
        metrics = self.store.metrics().to_dict()
        self.assertEqual(metrics["signals"], 1)
        self.assertEqual(metrics["qualified_actions"], 1)
        self.assertEqual(metrics["useful_actions"], 1)
        self.assertEqual(metrics["investigation_minutes"], 4)
        self.assertEqual(metrics["estimated_manual_minutes"], 20)
        self.assertEqual(metrics["estimated_minutes_saved"], 16)
        self.assertEqual(metrics["minutes_per_useful_action"], 4)
        self.assertEqual(metrics["pipeline_per_operator_hour"], 75000)
        self.assertIn("estimated_minutes_saved", metrics["evidence_boundary"]["operator_estimated"])

    def test_unknown_surface_cannot_receive_economic_receipt(self) -> None:
        with self.assertRaises(KeyError):
            self.store.record_review(
                "missing",
                outcome="responded",
                investigation_minutes=1,
            )


if __name__ == "__main__":
    unittest.main()
