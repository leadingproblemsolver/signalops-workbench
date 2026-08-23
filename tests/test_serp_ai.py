from __future__ import annotations

import json
import unittest

from signalops.serp_ai import AIAssessmentError, OpportunityAssessor
from signalops.serpapi import SerpEvidence


class OpportunityAssessorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.evidence = [
            SerpEvidence(
                query="agent reliability",
                title="Looking for help with an existing agent",
                url="https://example.com/post",
                snippet="Our production agent is failing on retries and we need help this week.",
                source="example.com",
                position=1,
                date="1 hour ago",
                search_id="s1",
            )
        ]

    def test_assessment_is_structured_and_bounded(self) -> None:
        model_output = [
            {
                "index": 0,
                "inference": "This may indicate an active reliability intervention opportunity.",
                "relevance": 9,
                "urgency": 8,
                "conversation": 8.5,
                "who": "example.com",
            }
        ]
        response = {"output_text": json.dumps(model_output)}

        assessor = OpportunityAssessor(
            "test-openai-key",
            transport=lambda _request, _timeout: json.dumps(response).encode("utf-8"),
        )
        [assessment] = assessor.assess(self.evidence, goal="Find active reliability work")

        self.assertEqual(assessment.index, 0)
        self.assertEqual(assessment.relevance, 9.0)
        self.assertEqual(assessment.urgency, 8.0)
        self.assertEqual(assessment.conversation, 8.5)
        self.assertIn("active reliability", assessment.inference)

    def test_rejects_out_of_range_model_scores(self) -> None:
        response = {
            "output_text": json.dumps(
                [
                    {
                        "index": 0,
                        "inference": "unsupported",
                        "relevance": 11,
                        "urgency": 5,
                        "conversation": 5,
                        "who": "",
                    }
                ]
            )
        }
        assessor = OpportunityAssessor(
            "test-openai-key",
            transport=lambda _request, _timeout: json.dumps(response).encode("utf-8"),
        )
        with self.assertRaisesRegex(AIAssessmentError, "relevance"):
            assessor.assess(self.evidence, goal="Find active reliability work")


if __name__ == "__main__":
    unittest.main()
