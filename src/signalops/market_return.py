"""Human-first externalization contracts for evidence-bounded market return.

Clay may discover and enrich people, but it does not get to invent rapport, authorize
outreach, or promote a reply into adoption. This module turns a reviewed distribution
route into one of three explicit strategies whose first principle is value before ask.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from typing import Mapping, Sequence

from .core import ValidationError


STRATEGIES = ("rapport_first", "useful_artifact_first", "micro_pilot")
ADOPTION_OUTCOMES = ("pilot_used", "second_use", "purchase")
EVIDENCE_BEARING_OUTCOMES = (
    "evidence_reply",
    "correction",
    "referral",
    "pilot_started",
    *ADOPTION_OUTCOMES,
)
OUTCOMES = (
    "no_response",
    "human_reply",
    *EVIDENCE_BEARING_OUTCOMES,
    "explicit_rejection",
)


def _clean(value: object) -> str:
    return str(value or "").strip()


def _as_tuple(values: Sequence[str] | str | None) -> tuple[str, ...]:
    if values is None:
        return ()
    if isinstance(values, str):
        values = (values,)
    return tuple(str(value).strip() for value in values if str(value).strip())


@dataclass(frozen=True, slots=True)
class ExternalizationTouch:
    """One planned human touch. It is never a send instruction."""

    order: int
    purpose: str
    value_given: str
    ask: str
    evidence_refs: tuple[str, ...] = ()

    @property
    def asks_for_work(self) -> bool:
        return bool(self.ask)


@dataclass(frozen=True, slots=True)
class ExternalizationPlan:
    """Reviewable plan for one route and one market-return strategy."""

    route_key: str
    strategy: str
    contact_name: str
    company: str
    personal_signal: str
    artifact_ref: str
    bounded_deliverable: str
    adoption_receipt: str
    touches: tuple[ExternalizationTouch, ...]
    next_action: str = "human_review"

    @property
    def plan_key(self) -> str:
        canonical = json.dumps(
            {
                "route_key": self.route_key,
                "strategy": self.strategy,
                "contact_name": self.contact_name,
                "company": self.company,
                "touches": [asdict(touch) for touch in self.touches],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return sha256(canonical.encode("utf-8")).hexdigest()[:24]

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["plan_key"] = self.plan_key
        return data


@dataclass(frozen=True, slots=True)
class MarketOutcomeReceipt:
    """External evidence receipt. A reply is not silently upgraded into adoption."""

    plan_key: str
    route_key: str
    strategy: str
    outcome: str
    evidence_ref: str
    notes: str = ""

    @property
    def is_adoption(self) -> bool:
        return self.outcome in ADOPTION_OUTCOMES

    @property
    def is_evidence_bearing(self) -> bool:
        return self.outcome in EVIDENCE_BEARING_OUTCOMES


def build_externalization_plan(
    *,
    route_key: str,
    strategy: str,
    contact_name: str,
    company: str,
    evidence_refs: Sequence[str] | str | None = None,
    personal_signal: str = "",
    artifact_ref: str = "",
    bounded_deliverable: str = "",
    adoption_receipt: str = "",
) -> ExternalizationPlan:
    """Build a value-before-ask plan with strategy-specific evidence gates."""

    route_key = _clean(route_key)
    strategy = _clean(strategy)
    contact_name = _clean(contact_name)
    company = _clean(company)
    personal_signal = _clean(personal_signal)
    artifact_ref = _clean(artifact_ref)
    bounded_deliverable = _clean(bounded_deliverable)
    adoption_receipt = _clean(adoption_receipt)
    refs = _as_tuple(evidence_refs)

    if not route_key or not contact_name or not company:
        raise ValidationError("route_key, contact_name, and company are required")
    if strategy not in STRATEGIES:
        raise ValidationError(f"strategy must be one of {', '.join(STRATEGIES)}")

    if strategy == "rapport_first":
        if not personal_signal:
            raise ValidationError("rapport_first requires a verified personal signal")
        if not bounded_deliverable:
            raise ValidationError("rapport_first requires a later bounded contribution")
        touches = (
            ExternalizationTouch(
                order=1,
                purpose="human_connection",
                value_given="Specific, sincere response to the verified public signal",
                ask="",
                evidence_refs=refs,
            ),
            ExternalizationTouch(
                order=2,
                purpose="useful_contribution",
                value_given=bounded_deliverable,
                ask="One low-effort reaction or correction only if the contribution is relevant",
                evidence_refs=refs,
            ),
            ExternalizationTouch(
                order=3,
                purpose="bounded_invitation",
                value_given="Apply the contribution to one real or sanitized workflow",
                ask="Opt in to one bounded test; no meeting required",
                evidence_refs=refs,
            ),
        )
    elif strategy == "useful_artifact_first":
        if not artifact_ref:
            raise ValidationError("useful_artifact_first requires an artifact_ref")
        touches = (
            ExternalizationTouch(
                order=1,
                purpose="artifact_delivery",
                value_given="Send the already-built, company-relevant artifact",
                ask="Point to the one part that is wrong, irrelevant, or incomplete",
                evidence_refs=(*refs, artifact_ref),
            ),
            ExternalizationTouch(
                order=2,
                purpose="artifact_revision",
                value_given="Return a corrected version that incorporates their feedback",
                ask="Optional: name one real case where the corrected model should be tested",
                evidence_refs=(*refs, artifact_ref),
            ),
            ExternalizationTouch(
                order=3,
                purpose="bounded_application",
                value_given="Apply the corrected artifact to one real or sanitized case",
                ask="Confirm, correct, reject, or reuse the output",
                evidence_refs=(*refs, artifact_ref),
            ),
        )
    else:
        if not bounded_deliverable or not adoption_receipt:
            raise ValidationError(
                "micro_pilot requires a bounded_deliverable and explicit adoption_receipt"
            )
        touches = (
            ExternalizationTouch(
                order=1,
                purpose="show_finished_example",
                value_given=bounded_deliverable,
                ask="Choose one tiny input or sanitized case only if useful",
                evidence_refs=refs,
            ),
            ExternalizationTouch(
                order=2,
                purpose="deliver_pilot_output",
                value_given="Return the promised bounded output with evidence boundaries visible",
                ask="Mark it useful, partial, wrong, or not relevant",
                evidence_refs=refs,
            ),
            ExternalizationTouch(
                order=3,
                purpose="test_repeat_use",
                value_given="Apply the same workflow to a second case without expanding scope",
                ask=f"Repeat only if the adoption receipt can be observed: {adoption_receipt}",
                evidence_refs=refs,
            ),
        )

    if touches[0].asks_for_work and not touches[0].value_given:
        raise ValidationError("first touch may not ask for work before giving value")

    return ExternalizationPlan(
        route_key=route_key,
        strategy=strategy,
        contact_name=contact_name,
        company=company,
        personal_signal=personal_signal,
        artifact_ref=artifact_ref,
        bounded_deliverable=bounded_deliverable,
        adoption_receipt=adoption_receipt,
        touches=touches,
    )


def record_market_outcome(
    plan: ExternalizationPlan,
    *,
    outcome: str,
    evidence_ref: str = "",
    notes: str = "",
) -> MarketOutcomeReceipt:
    """Record one external outcome without converting weak signals into adoption."""

    outcome = _clean(outcome)
    evidence_ref = _clean(evidence_ref)
    if outcome not in OUTCOMES:
        raise ValidationError(f"outcome must be one of {', '.join(OUTCOMES)}")
    if outcome in EVIDENCE_BEARING_OUTCOMES and not evidence_ref:
        raise ValidationError(f"{outcome} requires an evidence_ref")

    return MarketOutcomeReceipt(
        plan_key=plan.plan_key,
        route_key=plan.route_key,
        strategy=plan.strategy,
        outcome=outcome,
        evidence_ref=evidence_ref,
        notes=_clean(notes),
    )


def summarize_market_return(
    receipts: Sequence[MarketOutcomeReceipt],
) -> dict[str, Mapping[str, int] | int]:
    """Return strategy counts. Human replies remain distinct from adoption receipts."""

    by_strategy: dict[str, dict[str, int]] = {
        strategy: {"total": 0, "evidence_bearing": 0, "adoption": 0}
        for strategy in STRATEGIES
    }
    for receipt in receipts:
        metrics = by_strategy[receipt.strategy]
        metrics["total"] += 1
        if receipt.is_evidence_bearing:
            metrics["evidence_bearing"] += 1
        if receipt.is_adoption:
            metrics["adoption"] += 1
    return {"total": len(receipts), "by_strategy": by_strategy}
