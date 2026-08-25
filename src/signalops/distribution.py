"""Evidence-bounded routing from repository artifacts to Clay-resolved market targets.

Clay remains the discovery/enrichment layer. SignalOps owns identity preservation,
explicit fit reasoning, deterministic route receipts, human authorization, and outcome memory.
This module deliberately does not send outreach or mutate a CRM.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from .clay import ClayCompanySignal
from .core import ValidationError


def _clean(value: object) -> str:
    return str(value or "").strip()


def _as_tuple(raw: object) -> tuple[str, ...]:
    if isinstance(raw, str):
        values = (raw,)
    elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        values = tuple(str(item) for item in raw)
    else:
        values = ()
    return tuple(value.strip() for value in values if value.strip())


def _normalized_domain(value: str) -> str:
    domain = value.strip().lower()
    for prefix in ("https://", "http://"):
        if domain.startswith(prefix):
            domain = domain[len(prefix) :]
    domain = domain.split("/", 1)[0]
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def _enrichments(raw: object) -> tuple[dict[str, str], dict[str, str]]:
    values: dict[str, str] = {}
    states: dict[str, str] = {}
    if isinstance(raw, Mapping):
        items = raw.values()
    elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        items = raw
    else:
        items = ()

    for item in items:
        if not isinstance(item, Mapping):
            continue
        name = _clean(item.get("name"))
        if not name:
            continue
        state = _clean(item.get("state") or "unknown").lower()
        states[name] = state
        value = item.get("value")
        if state == "completed" and value not in (None, ""):
            values[name] = _clean(value)
    return values, states


@dataclass(frozen=True, slots=True)
class RepoArtifactManifest:
    """Small contract any repo can emit before market routing."""

    repo: str
    artifact_id: str
    artifact_url: str
    system: str
    wedge: str
    target_roles: tuple[str, ...]
    pain_signals: tuple[str, ...]
    proof_refs: tuple[str, ...]
    desired_consequence: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RepoArtifactManifest":
        manifest = cls(
            repo=_clean(data.get("repo")),
            artifact_id=_clean(data.get("artifact_id")),
            artifact_url=_clean(data.get("artifact_url")),
            system=_clean(data.get("system")),
            wedge=_clean(data.get("wedge")),
            target_roles=_as_tuple(data.get("target_roles")),
            pain_signals=_as_tuple(data.get("pain_signals")),
            proof_refs=_as_tuple(data.get("proof_refs")),
            desired_consequence=_clean(data.get("desired_consequence")),
        )
        if not all(
            (
                manifest.repo,
                manifest.artifact_id,
                manifest.artifact_url,
                manifest.system,
                manifest.wedge,
                manifest.target_roles,
                manifest.proof_refs,
                manifest.desired_consequence,
            )
        ):
            raise ValidationError(
                "artifact manifest requires repo, artifact_id, artifact_url, system, wedge, "
                "target_roles, proof_refs, and desired_consequence"
            )
        return manifest

    @property
    def artifact_key(self) -> str:
        canonical = json.dumps(
            {
                "repo": self.repo,
                "artifact_id": self.artifact_id,
                "artifact_url": self.artifact_url,
                "system": self.system,
                "wedge": self.wedge,
                "proof_refs": self.proof_refs,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        return sha256(canonical.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True, slots=True)
class ClayContactSignal:
    """Bounded contact-level Clay result with asynchronous enrichment state preserved."""

    name: str
    title: str
    company: str
    company_domain: str
    profile_url: str
    thought_leadership: str = ""
    enrichment_states: tuple[tuple[str, str], ...] = ()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ClayContactSignal":
        values, states = _enrichments(data.get("enrichments"))
        signal = cls(
            name=_clean(data.get("name")),
            title=_clean(data.get("latest_experience_title") or data.get("title")),
            company=_clean(data.get("latest_experience_company") or data.get("company")),
            company_domain=_clean(data.get("domain") or data.get("company_domain")),
            profile_url=_clean(data.get("url") or data.get("profile_url")),
            thought_leadership=values.get("Find Thought Leadership", ""),
            enrichment_states=tuple(sorted(states.items())),
        )
        if not signal.name or not signal.title or not signal.company or not signal.profile_url:
            raise ValidationError("Clay contact requires name, title, company, and profile URL")
        return signal

    @property
    def provenance_id(self) -> str:
        identity = self.profile_url or f"{self.name}|{self.company_domain}"
        return sha256(f"clay|contact|{identity}".encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True, slots=True)
class DistributionRouteReceipt:
    """Deterministic receipt proving why an artifact was routed to a market observer."""

    artifact_key: str
    artifact_id: str
    account_name: str
    account_search_identifier: str
    account_observed_domain: str
    account_source_id: str
    contact_name: str
    contact_title: str
    contact_source_id: str
    fit_reasons: tuple[str, ...]
    personalization_evidence: tuple[str, ...]
    identity_discrepancy: bool
    next_action: str = "human_review"

    @property
    def route_key(self) -> str:
        canonical = json.dumps(
            {
                "artifact_key": self.artifact_key,
                "account_source_id": self.account_source_id,
                "contact_source_id": self.contact_source_id,
                "fit_reasons": self.fit_reasons,
                "next_action": self.next_action,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        return sha256(canonical.encode("utf-8")).hexdigest()[:24]

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["route_key"] = self.route_key
        return data


def normalize_clay_contacts(payload: Sequence[Mapping[str, Any]]) -> list[ClayContactSignal]:
    """Normalize contact discovery/enrichment results without inventing missing values."""
    return [ClayContactSignal.from_mapping(item) for item in payload]


def route_artifact_to_clay_target(
    artifact: RepoArtifactManifest,
    company: ClayCompanySignal,
    contact: ClayContactSignal,
    *,
    search_identifier: str,
    fit_reasons: Sequence[str],
) -> DistributionRouteReceipt:
    """Create one reviewable market route; never authorize sending or CRM mutation.

    Fit reasons must be supplied explicitly by the operator or an upstream bounded decision
    process. Clay evidence may support personalization, but enrichment never silently becomes
    a fit claim. Search identity and observed Clay identity are preserved independently so
    discrepancies remain inspectable instead of being overwritten.
    """

    reasons = _as_tuple(fit_reasons)
    if not reasons:
        raise ValidationError("at least one explicit fit reason is required before routing")
    search_domain = _normalized_domain(search_identifier)
    if not search_domain:
        raise ValidationError("search_identifier is required")

    observed_domain = _normalized_domain(company.domain)
    personalization = (contact.thought_leadership,) if contact.thought_leadership else ()

    return DistributionRouteReceipt(
        artifact_key=artifact.artifact_key,
        artifact_id=artifact.artifact_id,
        account_name=company.company,
        account_search_identifier=search_domain,
        account_observed_domain=observed_domain,
        account_source_id=company.provenance_id,
        contact_name=contact.name,
        contact_title=contact.title,
        contact_source_id=contact.provenance_id,
        fit_reasons=reasons,
        personalization_evidence=personalization,
        identity_discrepancy=bool(observed_domain and observed_domain != search_domain),
    )
