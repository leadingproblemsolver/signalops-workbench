"""Evidence-bounded Clay -> SignalOps ingress contract.

This module accepts a small, explicit payload that Clay can send through an HTTP/webhook
step. It preserves evidence classes, creates a deterministic receipt, suppresses duplicate
writes, and hard-stops before external outreach or CRM mutation.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from .core import ValidationError


_ALLOWED_SIGNAL_TYPES = frozenset({"fact", "inference", "unknown", "no_signal"})


def _clean(value: object) -> str:
    return str(value or "").strip()


def _normalize_domain(value: object) -> str:
    domain = _clean(value).lower()
    for prefix in ("https://", "http://"):
        if domain.startswith(prefix):
            domain = domain[len(prefix) :]
    domain = domain.split("/", 1)[0]
    if domain.startswith("www."):
        domain = domain[4:]
    return domain


def _clean_sequence(raw: object) -> tuple[str, ...]:
    if isinstance(raw, str):
        values: Sequence[object] = (raw,)
    elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        values = raw
    else:
        values = ()
    return tuple(value for item in values if (value := _clean(item)))


@dataclass(frozen=True, slots=True)
class EvidenceSignal:
    signal_type: str
    value: str
    source_ref: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "EvidenceSignal":
        signal_type = _clean(data.get("type")).lower()
        value = _clean(data.get("value"))
        source_ref = _clean(data.get("source_ref"))
        if signal_type not in _ALLOWED_SIGNAL_TYPES:
            raise ValidationError(
                f"signal type must be one of {sorted(_ALLOWED_SIGNAL_TYPES)}"
            )
        if not value or not source_ref:
            raise ValidationError("each signal requires value and source_ref")
        return cls(signal_type=signal_type, value=value, source_ref=source_ref)


@dataclass(frozen=True, slots=True)
class ClayIngressEvent:
    account_name: str
    account_domain: str
    contact_title: str
    contact_source_id: str
    signals: tuple[EvidenceSignal, ...]
    fit_reasons: tuple[str, ...]

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "ClayIngressEvent":
        account = data.get("account")
        contact = data.get("contact")
        raw_signals = data.get("signals")
        if not isinstance(account, Mapping):
            raise ValidationError("Clay ingress requires account object")
        if not isinstance(contact, Mapping):
            raise ValidationError("Clay ingress requires contact object")
        if not isinstance(raw_signals, Sequence) or isinstance(
            raw_signals, (str, bytes, bytearray)
        ):
            raise ValidationError("Clay ingress requires signals array")

        event = cls(
            account_name=_clean(account.get("name")),
            account_domain=_normalize_domain(account.get("domain")),
            contact_title=_clean(contact.get("title")),
            contact_source_id=_clean(contact.get("source_id")),
            signals=tuple(
                EvidenceSignal.from_mapping(item)
                for item in raw_signals
                if isinstance(item, Mapping)
            ),
            fit_reasons=_clean_sequence(data.get("fit_reasons")),
        )
        if not event.account_name or not event.account_domain:
            raise ValidationError("account name and domain are required")
        if not event.contact_title or not event.contact_source_id:
            raise ValidationError("contact title and stable source_id are required")
        if len(event.signals) != len(raw_signals):
            raise ValidationError("every signals item must be an object")
        if not event.signals:
            raise ValidationError("at least one evidence signal is required")
        return event


@dataclass(frozen=True, slots=True)
class ClayIngressReceipt:
    schema_version: str
    receipt_id: str
    source: str
    account_name: str
    account_domain: str
    contact_title: str
    contact_source_id: str
    evidence_counts: tuple[tuple[str, int], ...]
    fit_reasons: tuple[str, ...]
    personalization_state: str
    next_action: str
    send_actions_executed: bool
    crm_mutation_executed: bool

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence_counts"] = dict(self.evidence_counts)
        return data


def build_clay_ingress_receipt(event: ClayIngressEvent) -> ClayIngressReceipt:
    """Resolve one Clay event into a deterministic, non-executing GTM receipt."""

    counts = {kind: 0 for kind in sorted(_ALLOWED_SIGNAL_TYPES)}
    for signal in event.signals:
        counts[signal.signal_type] += 1

    if counts["no_signal"]:
        personalization_state = "explicit_no_signal"
    elif counts["fact"] and event.fit_reasons:
        personalization_state = "eligible"
    else:
        personalization_state = "insufficient_evidence"

    canonical = json.dumps(
        {
            "account_domain": event.account_domain,
            "contact_source_id": event.contact_source_id,
            "signals": [asdict(signal) for signal in event.signals],
            "fit_reasons": event.fit_reasons,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    receipt_id = sha256(canonical.encode("utf-8")).hexdigest()[:24]

    return ClayIngressReceipt(
        schema_version="2026-08-28.v1",
        receipt_id=receipt_id,
        source="clay",
        account_name=event.account_name,
        account_domain=event.account_domain,
        contact_title=event.contact_title,
        contact_source_id=event.contact_source_id,
        evidence_counts=tuple(sorted(counts.items())),
        fit_reasons=event.fit_reasons,
        personalization_state=personalization_state,
        next_action="human_review",
        send_actions_executed=False,
        crm_mutation_executed=False,
    )


class ReceiptStore:
    """Small append-only JSONL receipt store with deterministic duplicate suppression."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def receipts(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        rows: list[dict[str, Any]] = []
        for line_number, raw in enumerate(
            self.path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            if not raw.strip():
                continue
            try:
                value = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValidationError(
                    f"receipt store is corrupt at line {line_number}"
                ) from exc
            if not isinstance(value, dict):
                raise ValidationError(
                    f"receipt store line {line_number} must be a JSON object"
                )
            rows.append(value)
        return rows

    def append(self, receipt: ClayIngressReceipt) -> bool:
        """Append exactly once. Return False when the deterministic receipt already exists."""

        if any(
            row.get("receipt_id") == receipt.receipt_id for row in self.receipts()
        ):
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(receipt.to_dict(), sort_keys=True) + "\n")
        return True
