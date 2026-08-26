from __future__ import annotations

from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch

from signalops.core import Store, ValidationError
from signalops.externalization import (
    ExternalizationReceipt,
    commercial_entrypoint_from_env,
    externalization_metrics,
    record_externalization,
)


class ExternalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name) / "signalops.db")
        self.store.configure_policy({"channel": "reddit"})
        self.store.process(
            channel="reddit",
            title="Founder has weak post-launch GTM",
            url="https://example.com/thread",
            pain="manual prioritization",
            exact_language="I shipped but do not know who to target next.",
            relevance=9,
            urgency=8,
            conversation=9,
            who="Founder",
        )
        self.external_id = self.store.rows()[0]["external_id"]

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_commercial_receipt_preserves_attribution(self) -> None:
        receipt = ExternalizationReceipt(
            external_id=self.external_id,
            outcome="paid",
            mode="commercial",
            artifact="signalops-workbench",
            artifact_version="d18d841",
            surface="whop",
            experiment_id="exp-001",
            target="Founder",
            operator_minutes=12,
            value_amount=49,
            value_currency="usd",
            receipt_url="https://example.com/receipt/1",
            payment_ref="pay_123",
        )
        record_externalization(self.store, receipt)
        payload = self.store.events(self.external_id)[-1]["payload"]
        self.assertEqual(payload["mode"], "commercial")
        self.assertEqual(payload["value_currency"], "USD")
        self.assertEqual(payload["payment_ref"], "pay_123")

    def test_impact_receipt_requires_measurement(self) -> None:
        with self.assertRaisesRegex(ValidationError, "metric_name"):
            ExternalizationReceipt(
                external_id=self.external_id,
                outcome="improved",
                mode="impact",
                observed_value=4,
            )

    def test_impact_delta_and_metrics(self) -> None:
        record_externalization(
            self.store,
            ExternalizationReceipt(
                external_id=self.external_id,
                outcome="improved",
                mode="impact",
                artifact="signalops-workbench",
                surface="direct-user",
                operator_minutes=8,
                metric_name="minutes_to_justified_action",
                baseline_value=20,
                observed_value=8,
                receipt_url="https://example.com/proof/impact",
            ),
        )
        metrics = externalization_metrics(self.store)
        self.assertEqual(metrics["receipts"], 1)
        self.assertEqual(metrics["external_consequences"], 1)
        self.assertEqual(metrics["impact_measurements"], 1)
        self.assertEqual(metrics["minutes_per_external_consequence"], 8.0)
        self.assertEqual(self.store.events(self.external_id)[-1]["payload"]["impact_delta"], -12)

    def test_unknown_surface_is_rejected(self) -> None:
        with self.assertRaises(KeyError):
            record_externalization(
                self.store,
                ExternalizationReceipt(external_id="missing", outcome="responded"),
            )

    def test_negative_operator_time_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValidationError, "operator_minutes"):
            ExternalizationReceipt(
                external_id=self.external_id,
                outcome="responded",
                operator_minutes=-1,
            )

    def test_commercial_env_reports_configuration_without_secret(self) -> None:
        with patch.dict(
            os.environ,
            {
                "SIGNALOPS_CHECKOUT_URL": "https://whop.com/example",
                "WHOP_API_KEY": "secret-value",
            },
            clear=False,
        ):
            config = commercial_entrypoint_from_env()
        self.assertEqual(config["checkout_url"], "https://whop.com/example")
        self.assertTrue(config["whop_api_key_configured"])
        self.assertNotIn("secret-value", str(config))


if __name__ == "__main__":
    unittest.main()
