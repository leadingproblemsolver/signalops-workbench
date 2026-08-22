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


def normalize_clay_jobs(payload: Sequence[Mapping[str, Any]]) -> list[ClayJob]:
    """Normalize a bounded batch while preserving input order."""
    return [ClayJob.from_mapping(item) for item in payload]


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
