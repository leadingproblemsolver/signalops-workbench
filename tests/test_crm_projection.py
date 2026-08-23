from __future__ import annotations

import unittest

from signalops.clay import ClayCompanySignal
from signalops.crm import project_hubspot_company, reconcile_hubspot_company


class HubSpotProjectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.signal = ClayCompanySignal.from_mapping(
            {
                "name": "Example AI",
                "domain": "Example.AI",
                "url": "https://linkedin.com/company/example-ai",
                "description": "AI infrastructure for engineering teams.",
                "enrichments": [
                    {
                        "name": "Tech Stack",
                        "state": "completed",
                        "value": "HubSpot, Slack, AWS",
                    },
                    {
                        "name": "Recent News",
                        "state": "in-progress",
                        "value": "Running Enrichment...",
                    },
                ],
            }
        )

    def test_projection_only_promotes_explicit_observed_identity_fields(self) -> None:
        projection = project_hubspot_company(self.signal)

        self.assertEqual(
            projection.properties,
            {"domain": "example.ai", "name": "Example AI"},
        )
        self.assertNotIn("Tech Stack", projection.properties)
        self.assertNotIn("Recent News", projection.properties)
        self.assertNotIn("Running Enrichment", repr(projection.intended_properties))
        self.assertEqual(projection.clay_source_id, self.signal.provenance_id)

    def test_description_is_opt_in_not_silently_promoted(self) -> None:
        default_projection = project_hubspot_company(self.signal)
        explicit_projection = project_hubspot_company(
            self.signal, include_description=True
        )

        self.assertNotIn("description", default_projection.properties)
        self.assertEqual(
            explicit_projection.properties["description"],
            "AI infrastructure for engineering teams.",
        )

    def test_operation_key_is_stable_for_same_source_and_intended_state(self) -> None:
        first = project_hubspot_company(self.signal)
        second = project_hubspot_company(self.signal)

        self.assertEqual(first.operation_key, second.operation_key)
        self.assertEqual(len(first.operation_key), 24)

    def test_reconciliation_matches_fresh_read_back(self) -> None:
        projection = project_hubspot_company(self.signal)
        receipt = reconcile_hubspot_company(
            projection,
            hubspot_object_id=12345,
            read_back_properties={
                "name": "Example AI",
                "domain": "EXAMPLE.AI",
                "hs_lastmodifieddate": "ignored-extra-field",
            },
        )

        self.assertTrue(receipt.matched)
        self.assertEqual(receipt.hubspot_object_id, "12345")
        self.assertEqual(receipt.reconciliation_diff, ())
        self.assertEqual(receipt.operation_key, projection.operation_key)

    def test_reconciliation_exposes_missing_or_changed_projected_state(self) -> None:
        projection = project_hubspot_company(self.signal)
        receipt = reconcile_hubspot_company(
            projection,
            hubspot_object_id="12345",
            read_back_properties={"name": "Example AI"},
        )

        self.assertFalse(receipt.matched)
        self.assertEqual(
            receipt.reconciliation_diff,
            (("domain", "example.ai", ""),),
        )

    def test_extra_read_back_fields_cannot_create_false_mismatch(self) -> None:
        projection = project_hubspot_company(self.signal)
        receipt = reconcile_hubspot_company(
            projection,
            hubspot_object_id="12345",
            read_back_properties={
                "name": "Example AI",
                "domain": "example.ai",
                "createdate": "2026-08-23T00:00:00Z",
                "hubspot_owner_id": "999",
            },
        )

        self.assertTrue(receipt.matched)
        self.assertEqual(
            dict(receipt.read_back_properties),
            {"domain": "example.ai", "name": "Example AI"},
        )


if __name__ == "__main__":
    unittest.main()
