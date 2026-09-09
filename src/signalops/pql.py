"""Deterministic product-usage to PQL/expansion decision layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from typing import Any

from .core import ValidationError


class PQLState(StrEnum):
    MONITOR = "monitor"
    PQL = "pql"
    EXPANSION_READY = "expansion_ready"
    REVIEW = "review"
    STALE = "stale"


class ActivationAction(StrEnum):
    MONITOR = "monitor"
    HUMAN_REVIEW = "human_review"
    ROUTE_PQL = "route_pql"
    ROUTE_EXPANSION = "route_expansion"


@dataclass(frozen=True, slots=True)
class PQLPolicy:
    qualification_threshold: float = 6.0
    expansion_threshold: float = 8.0
    min_weekly_active_users: int = 3
    max_age_hours: int = 72
    owner_required_for_routing: bool = True

    def __post_init__(self) -> None:
        if not 0 <= self.qualification_threshold <= self.expansion_threshold <= 10:
            raise ValidationError(
                "PQL thresholds must satisfy 0 <= qualification <= expansion <= 10"
            )
        if self.min_weekly_active_users < 1:
            raise ValidationError("min_weekly_active_users must be >= 1")
        if self.max_age_hours < 1:
            raise ValidationError("max_age_hours must be >= 1")


@dataclass(frozen=True, slots=True)
class ProductUsageSignal:
    account_id: str
    observed_at: str
    weekly_active_users: int
    previous_weekly_active_users: int
    purchased_seats: int
    active_seats: int
    key_feature_users: int
    admin_invites_7d: int
    owner: str = ""
    source: str = "product"

    def __post_init__(self) -> None:
        account_id = self.account_id.strip()
        owner = self.owner.strip()
        source = self.source.strip().lower()
        if not account_id:
            raise ValidationError("account_id is required")
        if not source:
            raise ValidationError("source is required")

        numeric_fields = (
            "weekly_active_users",
            "previous_weekly_active_users",
            "purchased_seats",
            "active_seats",
            "key_feature_users",
            "admin_invites_7d",
        )
        for name in numeric_fields:
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValidationError(f"{name} must be a non-negative integer")

        timestamp = _parse_timestamp(self.observed_at)
        object.__setattr__(self, "account_id", account_id)
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "observed_at", timestamp.isoformat())


@dataclass(frozen=True, slots=True)
class PQLDecision:
    state: PQLState
    action: ActivationAction
    score: float
    reasons: tuple[str, ...]
    trace: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "action": self.action.value,
            "score": self.score,
            "reasons": list(self.reasons),
            "trace": list(self.trace),
        }


def _parse_timestamp(value: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise ValidationError("observed_at must be an ISO-8601 timestamp") from exc
    if timestamp.tzinfo is None:
        raise ValidationError("observed_at must include a timezone")
    return timestamp.astimezone(UTC)


def _clamp(value: float, lower: float = 0.0, upper: float = 10.0) -> float:
    return max(lower, min(upper, value))


def _component_scores(signal: ProductUsageSignal) -> dict[str, float]:
    if signal.purchased_seats > 0:
        adoption = _clamp(10 * signal.active_seats / signal.purchased_seats)
    else:
        adoption = 0.0

    depth = _clamp(10 * signal.key_feature_users / max(signal.weekly_active_users, 1))

    if signal.previous_weekly_active_users == 0:
        growth = 10.0 if signal.weekly_active_users > 0 else 0.0
    else:
        growth_rate = (
            signal.weekly_active_users - signal.previous_weekly_active_users
        ) / signal.previous_weekly_active_users
        # Stable usage scores 5; +50% growth reaches 10; -50% reaches 0.
        growth = _clamp(5 + (10 * growth_rate))

    invite_pressure = _clamp(2 * signal.admin_invites_7d)

    return {
        "adoption": round(adoption, 2),
        "depth": round(depth, 2),
        "growth": round(growth, 2),
        "invite_pressure": round(invite_pressure, 2),
    }


def decide_pql(
    signal: ProductUsageSignal,
    policy: PQLPolicy | None = None,
    *,
    now: datetime | None = None,
) -> PQLDecision:
    """Turn product-usage evidence into an explainable PQL/expansion action."""

    policy = policy or PQLPolicy()
    now = (now or datetime.now(UTC)).astimezone(UTC)
    observed_at = _parse_timestamp(signal.observed_at)
    age_hours = (now - observed_at).total_seconds() / 3600

    components = _component_scores(signal)
    score = round(
        0.35 * components["adoption"]
        + 0.25 * components["depth"]
        + 0.25 * components["growth"]
        + 0.15 * components["invite_pressure"],
        2,
    )

    trace = (
        f"score={score}",
        "formula=.35 adoption + .25 depth + .25 growth + .15 invite_pressure",
        f"adoption={components['adoption']}",
        f"depth={components['depth']}",
        f"growth={components['growth']}",
        f"invite_pressure={components['invite_pressure']}",
        f"age_hours={round(age_hours, 2)}",
        f"qualification_threshold={policy.qualification_threshold}",
        f"expansion_threshold={policy.expansion_threshold}",
        f"owner_present={bool(signal.owner)}",
    )

    if age_hours < 0:
        return PQLDecision(
            PQLState.REVIEW,
            ActivationAction.HUMAN_REVIEW,
            score,
            ("Evidence timestamp is in the future; routing is blocked.",),
            trace,
        )

    if age_hours > policy.max_age_hours:
        return PQLDecision(
            PQLState.STALE,
            ActivationAction.MONITOR,
            score,
            ("Evidence is stale; refresh usage before routing.",),
            trace,
        )

    if signal.purchased_seats == 0:
        return PQLDecision(
            PQLState.REVIEW,
            ActivationAction.HUMAN_REVIEW,
            score,
            ("Seat denominator is unavailable; automatic commercial routing is blocked.",),
            trace,
        )

    if signal.weekly_active_users < policy.min_weekly_active_users:
        return PQLDecision(
            PQLState.MONITOR,
            ActivationAction.MONITOR,
            score,
            (
                f"Weekly active users are below the minimum of "
                f"{policy.min_weekly_active_users}.",
            ),
            trace,
        )

    if score >= policy.expansion_threshold:
        if policy.owner_required_for_routing and not signal.owner:
            return PQLDecision(
                PQLState.REVIEW,
                ActivationAction.HUMAN_REVIEW,
                score,
                ("Expansion signal is strong but no accountable owner is assigned.",),
                trace,
            )
        return PQLDecision(
            PQLState.EXPANSION_READY,
            ActivationAction.ROUTE_EXPANSION,
            score,
            (
                "Expansion threshold is satisfied.",
                "Fresh product evidence and routing authority requirements are satisfied.",
            ),
            trace,
        )

    if score >= policy.qualification_threshold:
        if policy.owner_required_for_routing and not signal.owner:
            return PQLDecision(
                PQLState.REVIEW,
                ActivationAction.HUMAN_REVIEW,
                score,
                ("PQL threshold is satisfied but no accountable owner is assigned.",),
                trace,
            )
        return PQLDecision(
            PQLState.PQL,
            ActivationAction.ROUTE_PQL,
            score,
            ("PQL threshold is satisfied.",),
            trace,
        )

    return PQLDecision(
        PQLState.MONITOR,
        ActivationAction.MONITOR,
        score,
        ("Usage evidence does not yet satisfy the PQL threshold.",),
        trace,
    )


def build_handoff(
    signal: ProductUsageSignal,
    decision: PQLDecision,
) -> dict[str, Any]:
    """Build an idempotent, evidence-preserving handoff for a CRM/action layer."""

    if decision.action not in {
        ActivationAction.ROUTE_PQL,
        ActivationAction.ROUTE_EXPANSION,
    }:
        raise ValidationError("decision is not routable")
    if not signal.owner:
        raise ValidationError("routable handoff requires an owner")

    idempotency_basis = "|".join(
        (
            signal.account_id,
            signal.observed_at,
            decision.state.value,
            signal.owner,
        )
    )
    handoff_id = sha256(idempotency_basis.encode("utf-8")).hexdigest()[:24]

    return {
        "handoff_id": handoff_id,
        "idempotency_key": handoff_id,
        "account_id": signal.account_id,
        "owner": signal.owner,
        "state": decision.state.value,
        "action": decision.action.value,
        "score": decision.score,
        "reasons": list(decision.reasons),
        "evidence": asdict(signal),
        "expected_destination_state": {
            "pql_state": decision.state.value,
            "pql_score": decision.score,
            "pql_reason": "; ".join(decision.reasons),
        },
    }
