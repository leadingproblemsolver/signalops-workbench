from __future__ import annotations

import json
import unittest

from signalops.serpapi import SerpApiClient, SerpApiError


class SerpApiClientTests(unittest.TestCase):
    def test_normalizes_structured_organic_results(self) -> None:
        payload = {
            "search_metadata": {"id": "search-123", "status": "Success"},
            "organic_results": [
                {
                    "position": 1,
                    "title": "Founder looking for an AI workflow engineer",
                    "link": "https://example.com/post/1",
                    "displayed_link": "example.com",
                    "date": "2 hours ago",
                    "snippet": "We need help hardening an existing agent workflow this week.",
                },
                {
                    "position": 2,
                    "title": "Second result",
                    "link": "https://example.com/post/2",
                    "snippet": "Another source-provided snippet.",
                },
            ],
        }

        def transport(_request, _timeout):
            return json.dumps(payload).encode("utf-8")

        client = SerpApiClient("test-key", transport=transport)
        rows = client.search_google("AI agent workflow hiring", limit=2)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].search_id, "search-123")
        self.assertEqual(rows[0].position, 1)
        self.assertEqual(rows[0].source, "example.com")
        self.assertEqual(
            rows[0].observed_fact,
            "We need help hardening an existing agent workflow this week.",
        )

    def test_title_is_fallback_observed_fact_when_snippet_missing(self) -> None:
        payload = {
            "organic_results": [
                {"position": 1, "title": "Only title", "link": "https://example.com/x"}
            ]
        }

        client = SerpApiClient(
            "test-key", transport=lambda _request, _timeout: json.dumps(payload).encode()
        )
        [row] = client.search_google("query", limit=1)
        self.assertEqual(row.observed_fact, "Only title")

    def test_api_error_is_not_silently_treated_as_empty_results(self) -> None:
        payload = {"error": "Invalid API key"}
        client = SerpApiClient(
            "test-key", transport=lambda _request, _timeout: json.dumps(payload).encode()
        )
        with self.assertRaisesRegex(SerpApiError, "Invalid API key"):
            client.search_google("query")

    def test_requires_key_and_bounded_limit(self) -> None:
        with self.assertRaisesRegex(SerpApiError, "SERPAPI_API_KEY"):
            SerpApiClient("")

        client = SerpApiClient("test-key", transport=lambda _request, _timeout: b"{}")
        with self.assertRaisesRegex(ValueError, "1..20"):
            client.search_google("query", limit=21)


if __name__ == "__main__":
    unittest.main()
