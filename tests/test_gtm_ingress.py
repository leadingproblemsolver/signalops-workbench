from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from signalops.core import ValidationError
from signalops.gtm_ingress import (
    ClayIngressEvent,
    ReceiptStore,
    build_clay_ingress_receipt,
)


class ClayIngressTests(unittest.TestCase):
    def payload(self):
        return {
            "account": {"name": "Example Logistics", "domain": "HTTPS://WWW.Example.com/path"},
            "contact": {"title": "Digital Transformation Director", "source_id": "clay:contact:42"},
            "signals": [
                {
                    "type": "fact",
                    "value": "Public profile describes ERP/WMS/CRM integration leadership",
                    "source_ref": "https://example.com/public-source",
                }
            ],
            "fit_reasons": ["role owns systems integration"],
        }

    def test_verified_fact_plus_explicit_fit_reason_can_be_personalization_eligible(self) -> None:
        event = ClayIngressEvent.from_mapping(self.payload())
        receipt = build_clay_ingress_receipt(event)

        self.assertEqual(receipt.account_domain, "example.com")
        self.assertEqual(receipt.personalization_state, "eligible")
        self.assertEqual(receipt.next_action, "human_review")
        self.assertFalse(receipt.send_actions_executed)
        self.assertFalse(receipt.crm_mutation_executed)
        self.assertEqual(dict(receipt.evidence_counts)["fact"], 1)

    def test_explicit_no_signal_blocks_personalization_even_when_fit_reason_exists(self) -> None:
        payload = self.payload()
        payload["signals"].append(
            {
                "type": "no_signal",
                "value": "no strong signal",
                "source_ref": "clay:enrichment:human-signal",
            }
        )
        receipt = build_clay_ingress_receipt(ClayIngressEvent.from_mapping(payload))

        self.assertEqual(receipt.personalization_state, "explicit_no_signal")
        self.assertEqual(receipt.next_action, "human_review")

    def test_inference_without_verified_fact_is_not_promoted_to_personalization(self) -> None:
        payload = self.payload()
        payload["signals"] = [
            {
                "type": "inference",
                "value": "May have handoff complexity",
                "source_ref": "operator:hypothesis:1",
            }
        ]
        receipt = build_clay_ingress_receipt(ClayIngressEvent.from_mapping(payload))

        self.assertEqual(receipt.personalization_state, "insufficient_evidence")
        self.assertEqual(dict(receipt.evidence_counts)["inference"], 1)

    def test_receipt_id_is_stable_for_same_normalized_payload(self) -> None:
        first = build_clay_ingress_receipt(ClayIngressEvent.from_mapping(self.payload()))
        second_payload = self.payload()
        second_payload["account"]["domain"] = "example.com"
        second = build_clay_ingress_receipt(ClayIngressEvent.from_mapping(second_payload))

        self.assertEqual(first.receipt_id, second.receipt_id)

    def test_receipt_store_appends_once_and_reports_duplicate(self) -> None:
        receipt = build_clay_ingress_receipt(ClayIngressEvent.from_mapping(self.payload()))
        with tempfile.TemporaryDirectory() as directory:
            store = ReceiptStore(Path(directory) / "receipts.jsonl")

            self.assertTrue(store.append(receipt))
            self.assertFalse(store.append(receipt))
            rows = store.receipts()

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["receipt_id"], receipt.receipt_id)
        self.assertFalse(rows[0]["send_actions_executed"])
        self.assertFalse(rows[0]["crm_mutation_executed"])

    def test_unknown_signal_type_is_rejected_instead_of_reinterpreted(self) -> None:
        payload = self.payload()
        payload["signals"][0]["type"] = "probably_fact"

        with self.assertRaisesRegex(ValidationError, "signal type"):
            ClayIngressEvent.from_mapping(payload)


if __name__ == "__main__":
    unittest.main()
