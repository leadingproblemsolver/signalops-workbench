from __future__ import annotations

import pytest

from signalops.clay import ClayCompanySignal
from signalops.core import ValidationError
from signalops.distribution import (
    ClayContactSignal,
    RepoArtifactManifest,
    normalize_clay_contacts,
    route_artifact_to_clay_target,
)


def _artifact() -> RepoArtifactManifest:
    return RepoArtifactManifest.from_mapping(
        {
            "repo": "leadingproblemsolver/signalops-workbench",
            "artifact_id": "signalops-logistics-exception-router",
            "artifact_url": "https://github.com/leadingproblemsolver/signalops-workbench",
            "system": "SignalOps",
            "wedge": "logistics exception-to-action control layer",
            "target_roles": ["Head of Operations", "Control Tower Lead"],
            "pain_signals": ["fragmented exception evidence", "unclear ownership"],
            "proof_refs": ["PR #7", "PR #9", "20-signal public corpus receipt"],
            "desired_consequence": "operator-reviewed exception reconstruction",
        }
    )


def _company() -> ClayCompanySignal:
    return ClayCompanySignal.from_mapping(
        {
            "name": "HubSpot",
            "domain": "hubs.ly",
            "url": "https://www.linkedin.com/company/hubspot",
            "description": "Customer platform company.",
            "size": "5,001-10,000 employees",
            "country": "US",
            "industry": "Software Development",
            "enrichments": [],
        }
    )


def test_contact_normalization_preserves_completed_negative_enrichment() -> None:
    [contact] = normalize_clay_contacts(
        [
            {
                "name": "Valentyn P.",
                "latest_experience_company": "HubSpot",
                "latest_experience_title": "Product Engineer, Customer Agent AI",
                "url": "https://www.linkedin.com/in/vpodk/",
                "domain": "hubspot.com",
                "enrichments": [
                    {
                        "name": "Find Thought Leadership",
                        "state": "completed",
                        "value": "No relevant thought leadership items were found.",
                    }
                ],
            }
        ]
    )

    assert contact.thought_leadership == "No relevant thought leadership items were found."
    assert ("Find Thought Leadership", "completed") in contact.enrichment_states


def test_contact_normalization_does_not_promote_null_completed_value() -> None:
    contact = ClayContactSignal.from_mapping(
        {
            "name": "Niuscha Ansari Persaray",
            "latest_experience_company": "HubSpot",
            "latest_experience_title": "Lead Solution Engineer",
            "url": "https://www.linkedin.com/in/niuschaansari/",
            "domain": "hubspot.com",
            "enrichments": [
                {"name": "Find Thought Leadership", "state": "completed", "value": None}
            ],
        }
    )

    assert contact.thought_leadership == ""
    assert ("Find Thought Leadership", "completed") in contact.enrichment_states


def test_route_preserves_search_vs_observed_company_identity() -> None:
    contact = ClayContactSignal.from_mapping(
        {
            "name": "Gourav Khanijoe",
            "latest_experience_company": "HubSpot",
            "latest_experience_title": "Staff Engineering (Technical) Leader",
            "url": "https://www.linkedin.com/in/gourav-khanijoe/",
            "domain": "hubspot.com",
            "enrichments": [
                {
                    "name": "Find Thought Leadership",
                    "state": "completed",
                    "value": "Public technical interview and resilient distributed database talk found.",
                }
            ],
        }
    )

    route = route_artifact_to_clay_target(
        _artifact(),
        _company(),
        contact,
        search_identifier="hubspot.com",
        fit_reasons=["Explicit operator review: technical ownership matches the artifact observer class."],
    )

    assert route.account_search_identifier == "hubspot.com"
    assert route.account_observed_domain == "hubs.ly"
    assert route.identity_discrepancy is True
    assert route.next_action == "human_review"
    assert route.personalization_evidence
    assert route.route_key == route_artifact_to_clay_target(
        _artifact(),
        _company(),
        contact,
        search_identifier="hubspot.com",
        fit_reasons=["Explicit operator review: technical ownership matches the artifact observer class."],
    ).route_key


def test_route_requires_explicit_fit_reason() -> None:
    contact = ClayContactSignal.from_mapping(
        {
            "name": "Gourav Khanijoe",
            "latest_experience_company": "HubSpot",
            "latest_experience_title": "Staff Engineering (Technical) Leader",
            "url": "https://www.linkedin.com/in/gourav-khanijoe/",
            "domain": "hubspot.com",
            "enrichments": [],
        }
    )

    with pytest.raises(ValidationError):
        route_artifact_to_clay_target(
            _artifact(),
            _company(),
            contact,
            search_identifier="hubspot.com",
            fit_reasons=[],
        )
