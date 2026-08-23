from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Mapping

from .clay import ClayCompanySignal


_ALLOWED_HUBSPOT_COMPANY_FIELDS = frozenset({"name", "domain", "description"})


def _normalized_value(field: str, value: object) -> str:
    text = str(value or "").strip()
    if field == "domain":
        return text.lower()
    return text


@dataclass(frozen=True, slots=True)
class HubSpotCompanyProjection:
    """Deterministic, evidence-bounded projection into a HubSpot company mutation.

    The CRM payload intentionally contains only explicitly mapped observed fields.
    Clay enrichment outputs remain provenance/evidence and are never promoted into
    arbitrary CRM fields by inference.
    """

    source_company: str
    clay_source_id: str
    intended_properties: tuple[tuple[str, str], ...]

    @property
    def properties(self) -> dict[str, str]:
        return dict(self.intended_properties)

    @property
    def operation_key(self) -> str:
        canonical = json.dumps(
            {
                "source_company": self.source_company,
                "clay_source_id": self.clay_source_id,
                "intended_properties": self.intended_properties,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        return sha256(canonical.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True, slots=True)
class HubSpotReconciliationReceipt:
    hubspot_object_id: str
    operation_key: str
    intended_properties: tuple[tuple[str, str], ...]
    read_back_properties: tuple[tuple[str, str], ...]
    reconciliation_diff: tuple[tuple[str, str, str], ...]

    @property
    def matched(self) -> bool:
        return not self.reconciliation_diff


def project_hubspot_company(
    signal: ClayCompanySignal,
    *,
    include_description: bool = False,
) -> HubSpotCompanyProjection:
    """Create the smallest safe CRM projection from an observed Clay company.

    Identity fields are observed directly from Clay. Description is opt-in because
    some CRM portals treat it as operator-managed narrative. Enrichment values such
    as tech stack, open jobs, or recent news are deliberately not projected here.
    """

    intended: dict[str, str] = {"name": signal.company}
    if signal.domain:
        intended["domain"] = signal.domain
    if include_description and signal.description:
        intended["description"] = signal.description

    unknown = set(intended) - _ALLOWED_HUBSPOT_COMPANY_FIELDS
    if unknown:
        raise ValueError(f"Unsupported HubSpot company fields: {sorted(unknown)}")

    normalized = tuple(
        sorted((field, _normalized_value(field, value)) for field, value in intended.items())
    )
    return HubSpotCompanyProjection(
        source_company=signal.company,
        clay_source_id=signal.provenance_id,
        intended_properties=normalized,
    )


def reconcile_hubspot_company(
    projection: HubSpotCompanyProjection,
    *,
    hubspot_object_id: str | int,
    read_back_properties: Mapping[str, object],
) -> HubSpotReconciliationReceipt:
    """Compare the intended mutation with a fresh HubSpot read-back.

    Extra CRM fields are ignored. Missing or changed projected fields are explicit
    mismatches. This prevents a successful HTTP mutation from being mistaken for a
    verified state transition.
    """

    expected = projection.properties
    observed = {
        field: _normalized_value(field, read_back_properties.get(field, ""))
        for field in expected
    }

    diff: list[tuple[str, str, str]] = []
    for field, expected_value in expected.items():
        actual_value = observed[field]
        if actual_value != expected_value:
            diff.append((field, expected_value, actual_value))

    return HubSpotReconciliationReceipt(
        hubspot_object_id=str(hubspot_object_id),
        operation_key=projection.operation_key,
        intended_properties=projection.intended_properties,
        read_back_properties=tuple(sorted(observed.items())),
        reconciliation_diff=tuple(diff),
    )
