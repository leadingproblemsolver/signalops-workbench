"""External consequence receipts for commercial and impact experiments.

This module deliberately sits on top of the existing immutable SignalOps event store.
It does not add a second database or rebuild payment / analytics providers. The goal is
to make real external state changes attributable before automating more distribution.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from typing import Any
from urllib.parse import urlparse

from .core import Store, ValidationError, utc_now


MODES = frozenset({"proof", "commercial", "impact"})
EXTERNAL_CONSEQUENCE_OUTCOMES = frozenset(
    {
        "responded",
        "call_booked",
        "converted",
        "paid",
        "used",
        "adopted",
        "improved",
        "referred",
    }
)


def _absolute_http_url(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        return ""
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError(f"{field_name} must be an absolute http(s) URL")
    return normalized


@dataclass(frozen=True, slots=True)
class ExternalizationReceipt:
    """One attributable external state transition.

    `mode` separates the evidence question, not the storage mechanism:
    - proof: observer/reviewer consequence without economic or impact attribution;
    - commercial: demand, payment, pipeline, or buyer consequence;
    - impact: measurable user/workflow quality consequence.
    """

    external_id: str
    outcome: str
    mode: str = "proof"
    artifact: str = ""
    artifact_version: str = ""
    surface: str = ""
    experiment_id: str = ""
    target: str = ""
    operator_minutes: float | None = None
    value_amount: float | None = None
    value_currency: str = ""
    metric_name: str = ""
    baseline_value: float | None = None
    observed_value: float | None = None
    receipt_url: str = ""
    payment_ref: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        external_id = self.external_id.strip()
        outcome = self.outcome.strip().lower()
        mode = self.mode.strip().lower()
        if not external_id:
            raise ValidationError("external_id is required")
        if not outcome:
            raise ValidationError("outcome is required")
        if mode not in MODES:
            raise ValidationError(f"mode must be one of: {', '.join(sorted(MODES))}")
        if self.operator_minutes is not None and self.operator_minutes < 0:
            raise ValidationError("operator_minutes must be >= 0")
        if self.value_amount is not None and self.value_amount < 0:
            raise ValidationError("value_amount must be >= 0")

        currency = self.value_currency.strip().upper()
        if self.value_amount is not None and not currency:
            raise ValidationError("value_currency is required when value_amount is set")
        if currency and not (3 <= len(currency) <= 8 and currency.isalnum()):
            raise ValidationError("value_currency must be a short alphanumeric currency code")

        metric_name = self.metric_name.strip()
        if mode == "impact" and not metric_name:
            raise ValidationError("metric_name is required for impact receipts")
        if mode == "impact" and self.observed_value is None:
            raise ValidationError("observed_value is required for impact receipts")

        object.__setattr__(self, "external_id", external_id)
        object.__setattr__(self, "outcome", outcome)
        object.__setattr__(self, "mode", mode)
        object.__setattr__(self, "artifact", self.artifact.strip())
        object.__setattr__(self, "artifact_version", self.artifact_version.strip())
        object.__setattr__(self, "surface", self.surface.strip())
        object.__setattr__(self, "experiment_id", self.experiment_id.strip())
        object.__setattr__(self, "target", self.target.strip())
        object.__setattr__(self, "value_currency", currency)
        object.__setattr__(self, "metric_name", metric_name)
        object.__setattr__(self, "receipt_url", _absolute_http_url(self.receipt_url, "receipt_url"))
        object.__setattr__(self, "payment_ref", self.payment_ref.strip())
        object.__setattr__(self, "notes", self.notes.strip())

    @property
    def impact_delta(self) -> float | None:
        if self.baseline_value is None or self.observed_value is None:
            return None
        return self.observed_value - self.baseline_value

    def to_payload(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["impact_delta"] = self.impact_delta
        return payload


def record_externalization(store: Store, receipt: ExternalizationReceipt) -> None:
    """Append one immutable externalization receipt for an existing surface."""

    with store.connection() as connection:
        row = connection.execute(
            "SELECT external_id FROM surfaces WHERE external_id = ?",
            (receipt.external_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"unknown surface: {receipt.external_id}")
        connection.execute(
            """
            INSERT INTO events(entity_id, event_type, payload_json, occurred_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                receipt.external_id,
                "externalization_receipt",
                json.dumps(receipt.to_payload(), ensure_ascii=False, sort_keys=True),
                utc_now(),
            ),
        )


def externalization_metrics(store: Store) -> dict[str, Any]:
    """Aggregate only directly recorded receipts; never infer revenue or impact."""

    receipts = [
        event["payload"]
        for event in store.events()
        if event["event_type"] == "externalization_receipt"
    ]
    by_mode: dict[str, int] = {}
    outcomes: dict[str, int] = {}
    value_by_currency: dict[str, float] = {}
    operator_minutes = 0.0
    operator_minutes_observed = 0
    consequence_count = 0
    impact_measurements = 0
    receipt_urls = 0

    for payload in receipts:
        mode = str(payload.get("mode", "proof"))
        outcome = str(payload.get("outcome", ""))
        by_mode[mode] = by_mode.get(mode, 0) + 1
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        if outcome in EXTERNAL_CONSEQUENCE_OUTCOMES:
            consequence_count += 1

        minutes = payload.get("operator_minutes")
        if minutes is not None:
            operator_minutes += float(minutes)
            operator_minutes_observed += 1

        amount = payload.get("value_amount")
        currency = str(payload.get("value_currency", ""))
        if amount is not None and currency:
            value_by_currency[currency] = round(
                value_by_currency.get(currency, 0.0) + float(amount), 2
            )

        if mode == "impact" and payload.get("metric_name") and payload.get("observed_value") is not None:
            impact_measurements += 1
        if payload.get("receipt_url"):
            receipt_urls += 1

    minutes_per_consequence = None
    if consequence_count and operator_minutes_observed:
        minutes_per_consequence = round(operator_minutes / consequence_count, 2)

    return {
        "receipts": len(receipts),
        "external_consequences": consequence_count,
        "by_mode": by_mode,
        "outcomes": outcomes,
        "operator_minutes_recorded": round(operator_minutes, 2),
        "minutes_per_external_consequence": minutes_per_consequence,
        "attributed_value_by_currency": value_by_currency,
        "impact_measurements": impact_measurements,
        "receipts_with_url": receipt_urls,
    }


def commercial_entrypoint_from_env() -> dict[str, Any]:
    """Expose commercial wiring status without ever exposing provider secrets."""

    checkout_url = _absolute_http_url(
        os.getenv("SIGNALOPS_CHECKOUT_URL", ""),
        "SIGNALOPS_CHECKOUT_URL",
    )
    return {
        "checkout_url": checkout_url,
        "whop_api_key_configured": bool(os.getenv("WHOP_API_KEY", "").strip()),
    }
