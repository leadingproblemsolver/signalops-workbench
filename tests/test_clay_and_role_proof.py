from __future__ import annotations

import unittest

from signalops.clay import ClayJob, incremental_enrichment_decision
from signalops.core import ValidationError
from signalops.role_proof import compile_proof_gaps, extract_requirements


class ClayAdapterTests(unittest.TestCase):
    def test_clay_job_preserves_description_as_exact_language(self) -> None:
        raw = {
            "company_name": "Example AI",
            "title": "Deployed Engineer",
            "url": "https://example.com/jobs/1",
            "description": "Build production agents with explicit failure handling.",
            "location": "Remote",
        }
        job = ClayJob.from_mapping(raw)
        surface = job.to_surface(
            relevance=10,
            urgency=8,
            conversation=7,
            decision_context="Role-to-proof mapping",
        )
        self.assertEqual(surface.channel, "clay")
        self.assertEqual(surface.exact_language, raw["description"])
        self.assertEqual(surface.pain, "Role-to-proof mapping")
        self.assertTrue(surface.external_id)

    def test_clay_job_requires_source_description(self) -> None:
        with self.assertRaises(ValidationError):
            ClayJob.from_mapping({"company_name": "A", "title": "B", "url": "https://example.com"})

    def test_more_enrichment_requires_decision_critical_gap_and_positive_value(self) -> None:
        yes = incremental_enrichment_decision(
            missing_decision_fields=["current_outbound_stack"],
            enrichment_cost=1,
            expected_decision_value=4,
        )
        no = incremental_enrichment_decision(
            missing_decision_fields=[],
            enrichment_cost=1,
            expected_decision_value=100,
        )
        self.assertTrue(yes["should_enrich"])
        self.assertFalse(no["should_enrich"])


class RoleProofTests(unittest.TestCase):
    def test_extracts_langchain_like_requirements(self) -> None:
        description = """
        Strong Python, JavaScript and systems fundamentals. Build multi-step workflows with
        orchestration and failure handling. Work directly with customers during POCs and
        technical evaluations. Experience with LLM evaluation, observability, guardrails,
        AWS and containers is useful.
        """
        found = extract_requirements(description)
        self.assertIn("python", found)
        self.assertIn("agent_workflows", found)
        self.assertIn("failure_handling", found)
        self.assertIn("customer_poc", found)
        self.assertIn("evaluation", found)
        self.assertIn("observability", found)

    def test_existing_evidence_is_not_represented_as_missing(self) -> None:
        gaps = compile_proof_gaps(
            "Python with failure handling and observability in production.",
            {
                "python": ["signalops-workbench deterministic Python core"],
                "failure_handling": ["permission and validation tests"],
            },
        )
        by_name = {gap.requirement: gap for gap in gaps}
        self.assertEqual(by_name["python"].state, "evidenced")
        self.assertEqual(by_name["failure_handling"].state, "evidenced")
        self.assertEqual(by_name["observability"].state, "missing_proof")


if __name__ == "__main__":
    unittest.main()
