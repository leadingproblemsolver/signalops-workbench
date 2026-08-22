"""Bounded Clay -> SignalOps normalization.

This module deliberately consumes operator-supplied/authorized Clay results rather than
scraping or sending outreach. Clay owns discovery/enrichment; SignalOps owns provenance,
decision policy, human override and outcome memory.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping, Sequence

from .core import Surface, ValidationError


@dataclass(frozen=True, slots=True)
class ClayJob:
    company: str
    title: str
    url: str
    description: str
    location: str = ""
    employment_type: str = ""
    posted_at: str = ""

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ClayJob":
        company = str(data.get("company_name") or data.get("company") or "").strip()
        title = str(data.get("title") or "").strip()
        url = str(data.get("url") or data.get("application_url") or "").strip()
        description = str(data.get("description") or "").strip()
        if not company or not title or not url or not description:
            raise ValidationError("Clay job requires company, title, url, and description")
        return cls(
            company=company,
            title=title,
            url=url,
            description=description,
            location=str(data.get("location") or "").strip(),
            employment_type=str(data.get("employment_type") or "").strip(),
            posted_at=str(data.get("posted_at") or "").strip(),
        )

    @property
    def provenance_id(self) -> str:
        payload = f"clay|job|{self.company}|{self.title}|{self.url}"
        return sha256(payload.encode("utf-8")).hexdigest()[:24]

    def to_surface(
        self,
        *,
        relevance: float,
        urgency: float,
        conversation: float,
        decision_context: str,
    ) -> Surface:
        """Convert a Clay job into a SignalOps evidence surface.

        The source description is preserved verbatim in exact_language. decision_context is
        explicitly interpretation and therefore lives in pain rather than exact_language.
        """
        return Surface(
            channel="clay",
            title=f"{self.company} — {self.title}",
            url=self.url,
            who=self.company,
            pain=decision_context,
            exact_language=self.description,
            relevance=relevance,
            urgency=urgency,
            conversation=conversation,
            external_id=self.provenance_id,
        )


@dataclass(frozen=True, slots=True)
class ClayCompanySignal:
    """A bounded company-level Clay enrichment receipt.

    Only completed enrichment values are carried forward. In-progress/error states remain
    explicit in enrichment_states so SignalOps never turns missing enrichment into a fact.
    """

    company: str
    domain: str
    url: str
    description: str
    size: str = ""
    country: str = ""
    industry: str = ""
    tech_stack: str = ""
    open_jobs: str = ""
    recent_news: str = ""
    enrichment_states: tuple[tuple[str, str], ...] = ()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ClayCompanySignal":
        company = str(data.get("name") or data.get("company") or "").strip()
        domain = str(data.get("domain") or "").strip()
        url = str(data.get("url") or "").strip()
        description = str(data.get("description") or "").strip()
        if not company or not url or not description:
            raise ValidationError("Clay company requires name, url, and description")

        values, states = _company_enrichments(data.get("enrichments"))
        return cls(
            company=company,
            domain=domain,
            url=url,
            description=description,
            size=str(data.get("size") or "").strip(),
            country=str(data.get("country") or "").strip(),
            industry=str(data.get("industry") or "").strip(),
            tech_stack=values.get("Tech Stack", ""),
            open_jobs=values.get("Open Jobs", ""),
            recent_news=values.get("Recent News", ""),
            enrichment_states=tuple(sorted(states.items())),
        )

    @property
    def provenance_id(self) -> str:
        identity = self.domain or self.url
        return sha256(f"clay|company|{identity}".encode("utf-8")).hexdigest()[:24]

    def evidence_text(self) -> str:
        parts = [self.description]
        if self.tech_stack:
            parts.append(f"Tech Stack: {self.tech_stack}")
        if self.open_jobs:
            parts.append(f"Open Jobs: {self.open_jobs}")
        if self.recent_news:
            parts.append(f"Recent News: {self.recent_news}")
        return "\n\n".join(parts)

    def to_surface(
        self,
        *,
        relevance: float,
        urgency: float,
        conversation: float,
        decision_context: str,
    ) -> Surface:
        return Surface(
            channel="clay",
            title=f"{self.company} — company signal",
            url=self.url,
            who=self.company,
            pain=decision_context,
            exact_language=self.evidence_text(),
            relevance=relevance,
            urgency=urgency,
            conversation=conversation,
            external_id=self.provenance_id,
        )


def _company_enrichments(raw: Any) -> tuple[dict[str, str], dict[str, str]]:
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
        name = str(item.get("name") or "").strip()
        state = str(item.get("state") or "unknown").strip().lower()
        if not name:
            continue
        states[name] = state
        value = item.get("value")
        if state == "completed" and value not in (None, ""):
            values[name] = str(value).strip()
    return values, states


def normalize_clay_jobs(payload: Sequence[Mapping[str, Any]]) -> list[ClayJob]:
    """Normalize a bounded batch while preserving input order."""
    return [ClayJob.from_mapping(item) for item in payload]


def normalize_clay_companies(payload: Sequence[Mapping[str, Any]]) -> list[ClayCompanySignal]:
    """Normalize company search/enrichment results while preserving input order."""
    return [ClayCompanySignal.from_mapping(item) for item in payload]


def incremental_enrichment_decision(
    *,
    missing_decision_fields: Sequence[str],
    enrichment_cost: float,
    expected_decision_value: float,
) -> dict[str, Any]:
    """Make the 'buy another enrichment?' boundary explicit.

    This is intentionally deterministic and conservative. A new enrichment is justified only
    when a decision-critical field is missing and expected decision value strictly exceeds cost.
    The values are operator estimates, not learned economics.
    """
    if enrichment_cost < 0 or expected_decision_value < 0:
        raise ValidationError("enrichment cost/value must be non-negative")
    missing = [str(field).strip() for field in missing_decision_fields if str(field).strip()]
    should_enrich = bool(missing) and expected_decision_value > enrichment_cost
    return {
        "should_enrich": should_enrich,
        "missing_decision_fields": missing,
        "enrichment_cost": float(enrichment_cost),
        "expected_decision_value": float(expected_decision_value),
        "reason": (
            "Decision-critical evidence is missing and expected value exceeds cost."
            if should_enrich
            else "Do not buy more enrichment before a decision-critical evidence gap earns it."
        ),
    }
