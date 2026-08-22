from __future__ import annotations

import unittest

from signalops.clay import (
    ClayCompanySignal,
    ClayJob,
    incremental_enrichment_decision,
    normalize_clay_companies,
)
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

    def test_company_enrichment_preserves_completed_values_and_states(self) -> None:
        raw = {
            "name": "Example AI",
            "domain": "example.ai",
            "url": "https://linkedin.com/company/example-ai",
            "description": "AI infrastructure for engineering teams.",
            "size": "11-50 employees",
            "enrichments": [
                {"name": "Tech Stack", "state": "completed", "value": "HubSpot, Slack, AWS"},
                {"name": "Open Jobs", "state": "completed", "value": "No results found."},
                {"name": "Recent News", "state": "in-progress", "value": "Running Enrichment..."},
            ],
        }
        signal = ClayCompanySignal.from_mapping(raw)
        self.assertEqual(signal.tech_stack, "HubSpot, Slack, AWS")
        self.assertEqual(signal.open_jobs, "No results found.")
        self.assertEqual(signal.recent_news, "")
        self.assertIn(("Recent News", "in-progress"), signal.enrichment_states)
        self.assertNotIn("Running Enrichment", signal.evidence_text())

    def test_company_surface_separates_observed_evidence_from_operator_context(self) -> None:
        signal = ClayCompanySignal.from_mapping(
            {
                "name": "Example AI",
                "domain": "example.ai",
                "url": "https://linkedin.com/company/example-ai",
                "description": "Builds AI systems for engineering teams.",
                "enrichments": {
                    "1": {"name": "Tech Stack", "state": "completed", "value": "HubSpot, Slack"}
                },
            }
        )
        surface = signal.to_surface(
            relevance=9,
            urgency=6,
            conversation=8,
            decision_context="Potential ReworkTrace design-partner fit; operator inference only.",
        )
        self.assertEqual(surface.channel, "clay")
        self.assertIn("Builds AI systems", surface.exact_language)
        self.assertIn("Tech Stack: HubSpot, Slack", surface.exact_language)
        self.assertEqual(surface.pain, "Potential ReworkTrace design-partner fit; operator inference only.")
        self.assertTrue(surface.external_id)

    def test_normalize_company_batch_preserves_order(self) -> None:
        rows = [
            {"name": "A", "url": "https://a.example", "description": "A desc"},
            {"name": "B", "url": "https://b.example", "description": "B desc"},
        ]
        self.assertEqual([item.company for item in normalize_clay_companies(rows)], ["A", "B"])

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
