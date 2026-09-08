from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from signalops import hackathon
from signalops.core import Policy, Surface, decide
from signalops.serp_ai import OpportunityAssessment
from signalops.serpapi import SerpEvidence


class _FakeSerpClient:
    def search_google(self, query, *, limit, location=None):
        return [
            SerpEvidence(
                query=query,
                title="Lower-scoring signal",
                url="https://example.com/low",
                snippet="Observed low signal",
                source="Example",
                position=1,
                search_id="search-live-123",
            ),
            SerpEvidence(
                query=query,
                title="Higher-scoring signal",
                url="https://example.com/high",
                snippet="Observed high signal",
                source="Example",
                position=2,
                search_id="search-live-123",
            ),
        ]


class _FakeAssessor:
    def assess(self, evidence, *, goal):
        return [
            OpportunityAssessment(
                index=0,
                inference="Lower-value interpretation",
                relevance=4,
                urgency=3,
                conversation=4,
                who="Example",
            ),
            OpportunityAssessment(
                index=1,
                inference="Higher-value interpretation",
                relevance=9,
                urgency=8,
                conversation=9,
                who="Example",
            ),
        ]


class _FakeStore:
    def __init__(self):
        self._policy = None

    def policy(self, channel):
        if self._policy is None:
            raise KeyError(channel)
        return self._policy

    def configure_policy(self, data):
        self._policy = Policy.from_mapping(data)
        return self._policy

    def process(self, **data):
        surface = Surface(**data)
        return surface, decide(surface, self._policy)


class HackathonSurfaceTests(unittest.TestCase):
    def test_discover_returns_ranked_provenance_pack(self):
        fake_store = _FakeStore()
        with (
            patch.object(hackathon, "SerpApiClient", return_value=_FakeSerpClient()),
            patch.object(hackathon, "OpportunityAssessor", return_value=_FakeAssessor()),
            patch.object(hackathon, "store", fake_store),
        ):
            result = hackathon.discover(
                hackathon.DiscoverIn(
                    query="agent reliability",
                    goal="Find current useful signals",
                    limit=2,
                )
            )

        self.assertTrue(result["run_id"].startswith("run_"))
        self.assertEqual(result["engine"], "google")
        self.assertEqual(result["serpapi_search_ids"], ["search-live-123"])
        self.assertEqual(result["serpapi_results"], 2)
        self.assertGreaterEqual(result["elapsed_ms"], 0)
        self.assertEqual(result["decisions"][0]["title"], "Higher-scoring signal")
        self.assertEqual(result["decisions"][0]["rank"], 1)
        self.assertEqual(result["decisions"][1]["rank"], 2)
        self.assertEqual(
            result["decisions"][0]["scores"],
            {"relevance": 9, "urgency": 8, "conversation": 9},
        )
        self.assertEqual(result["top_score"], result["decisions"][0]["decision"]["score"])
        self.assertEqual(sum(result["action_counts"].values()), 2)

    def test_health_exposes_configuration_without_secrets(self):
        with patch.dict(
            os.environ,
            {"SERPAPI_API_KEY": "secret-a", "OPENAI_API_KEY": "secret-b"},
            clear=False,
        ):
            result = hackathon.health()

        self.assertTrue(result["serpapi_configured"])
        self.assertTrue(result["ai_configured"])
        self.assertNotIn("secret-a", str(result))
        self.assertNotIn("secret-b", str(result))
        self.assertEqual(result["store_backend"], "sqlite")

    def test_index_surfaces_judge_visible_authority_boundary(self):
        html = hackathon.index()
        for text in (
            "Observed evidence",
            "AI inference",
            "Policy decision",
            "Record outcome receipt",
            "Export evidence pack",
            "SerpApi",
        ):
            self.assertIn(text, html)


if __name__ == "__main__":
    unittest.main()
