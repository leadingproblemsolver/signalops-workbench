from __future__ import annotations

import unittest

from signalops.clay import ClayCompanySignal
from signalops.crm import (
    HubSpotAPIError,
    HubSpotClient,
    project_hubspot_company,
    write_and_reconcile_company,
)


class FakeTransport:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, method, url, headers, payload, timeout):
        self.calls.append(
            {
                "method": method,
                "url": url,
                "headers": dict(headers),
                "payload": payload,
                "timeout": timeout,
            }
        )
        return self.responses.pop(0)


class HubSpotClientTests(unittest.TestCase):
    def signal(self) -> ClayCompanySignal:
        return ClayCompanySignal.from_mapping(
            {
                "name": "Example AI",
                "domain": "Example.AI",
                "url": "https://www.linkedin.com/company/example-ai",
                "description": "Observed company description",
                "enrichments": [
                    {"name": "Tech Stack", "state": "completed", "value": "AWS"},
                ],
            }
        )

    def test_domain_search_uses_bearer_auth_and_normalized_exact_filter(self) -> None:
        transport = FakeTransport(
            [
                (
                    200,
                    {
                        "total": 1,
                        "results": [
                            {"id": "123", "properties": {"name": "Example AI", "domain": "example.ai"}}
                        ],
                    },
                )
            ]
        )
        client = HubSpotClient("secret-token", transport=transport)

        result = client.find_company_by_domain(" EXAMPLE.AI ")

        self.assertEqual(result["id"], "123")
        call = transport.calls[0]
        self.assertEqual(call["method"], "POST")
        self.assertTrue(call["url"].endswith("/crm/v3/objects/companies/search"))
        self.assertEqual(call["headers"]["Authorization"], "Bearer secret-token")
        self.assertEqual(
            call["payload"]["filterGroups"][0]["filters"][0],
            {"propertyName": "domain", "operator": "EQ", "value": "example.ai"},
        )
        self.assertEqual(call["payload"]["limit"], 2)

    def test_domain_search_refuses_ambiguous_company_identity(self) -> None:
        transport = FakeTransport(
            [(200, {"results": [{"id": "1"}, {"id": "2"}]})]
        )
        client = HubSpotClient("secret-token", transport=transport)

        with self.assertRaisesRegex(HubSpotAPIError, "matched multiple companies"):
            client.find_company_by_domain("example.ai")

    def test_write_then_read_back_is_exactly_one_mutation_and_one_verification_read(self) -> None:
        projection = project_hubspot_company(self.signal())
        transport = FakeTransport(
            [
                (
                    200,
                    {
                        "id": "123",
                        "properties": {"name": "Example AI", "domain": "example.ai"},
                    },
                ),
                (
                    200,
                    {
                        "id": "123",
                        "properties": {"name": "Example AI", "domain": "EXAMPLE.AI"},
                    },
                ),
            ]
        )
        client = HubSpotClient("secret-token", transport=transport)

        receipt = write_and_reconcile_company(
            client,
            hubspot_object_id="123",
            projection=projection,
        )

        self.assertTrue(receipt.matched)
        self.assertEqual(receipt.operation_key, projection.operation_key)
        self.assertEqual([call["method"] for call in transport.calls], ["PATCH", "GET"])
        self.assertEqual(
            transport.calls[0]["payload"],
            {"properties": {"domain": "example.ai", "name": "Example AI"}},
        )
        self.assertIn("properties=domain%2Cname", transport.calls[1]["url"])

    def test_update_cannot_promote_arbitrary_enrichment_field(self) -> None:
        client = HubSpotClient("secret-token", transport=FakeTransport([]))

        with self.assertRaisesRegex(ValueError, "Unsupported HubSpot company fields"):
            client.update_company("123", {"tech_stack": "AWS"})

    def test_api_authorization_failure_stays_explicit(self) -> None:
        transport = FakeTransport([(401, {"message": "missing required scope"})])
        client = HubSpotClient("secret-token", transport=transport)

        with self.assertRaises(HubSpotAPIError) as caught:
            client.get_company("123")

        self.assertEqual(caught.exception.status, 401)
        self.assertIn("missing required scope", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
