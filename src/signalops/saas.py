"""Thin SaaS measurement layer around the deterministic SignalOps kernel.

The core policy engine remains authoritative for ranking and permission decisions.
This module adds only operator review receipts and economic instrumentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .core import Store, ValidationError, utc_now


_SAAS_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS action_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    external_id TEXT NOT NULL,
    outcome TEXT NOT NULL,
    investigation_minutes REAL NOT NULL CHECK(investigation_minutes >= 0),
    manual_baseline_minutes REAL CHECK(manual_baseline_minutes >= 0),
    pipeline_value REAL NOT NULL DEFAULT 0 CHECK(pipeline_value >= 0),
    notes TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(external_id) REFERENCES surfaces(external_id)
);

CREATE INDEX IF NOT EXISTS action_reviews_external_id_idx
ON action_reviews(external_id, id DESC);
"""


@dataclass(frozen=True, slots=True)
class EconomicMetrics:
    signals: int
    qualified_actions: int
    reviewed_actions: int
    useful_actions: int
    investigation_minutes: float
    estimated_manual_minutes: float
    estimated_minutes_saved: float
    pipeline_value: float
    minutes_per_useful_action: float | None
    pipeline_per_operator_hour: float | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "signals": self.signals,
            "qualified_actions": self.qualified_actions,
            "reviewed_actions": self.reviewed_actions,
            "useful_actions": self.useful_actions,
            "investigation_minutes": self.investigation_minutes,
            "estimated_manual_minutes": self.estimated_manual_minutes,
            "estimated_minutes_saved": self.estimated_minutes_saved,
            "pipeline_value": self.pipeline_value,
            "minutes_per_useful_action": self.minutes_per_useful_action,
            "pipeline_per_operator_hour": self.pipeline_per_operator_hour,
            "evidence_boundary": {
                "observed": [
                    "signals",
                    "qualified_actions",
                    "reviewed_actions",
                    "useful_actions",
                    "investigation_minutes",
                    "pipeline_value",
                ],
                "operator_estimated": [
                    "estimated_manual_minutes",
                    "estimated_minutes_saved",
                ],
            },
        }


class SaaSStore:
    """Compose the core store with review receipts and ROI calculations."""

    USEFUL_OUTCOMES = {"responded", "call_booked", "converted"}

    def __init__(self, path: str):
        self.core = Store(path)
        with self.core.connection() as connection:
            connection.executescript(_SAAS_SCHEMA)

    def record_review(
        self,
        external_id: str,
        outcome: str,
        investigation_minutes: float,
        manual_baseline_minutes: float | None = None,
        pipeline_value: float = 0,
        notes: str = "",
    ) -> None:
        entity_id = external_id.strip()
        normalized_outcome = outcome.strip().lower()
        if not entity_id:
            raise ValidationError("external_id is required")
        if normalized_outcome not in {
            "ignored",
            "saved",
            "replied",
            "responded",
            "dm_sent",
            "call_booked",
            "converted",
            "rejected",
        }:
            raise ValidationError("unsupported outcome")
        if investigation_minutes < 0:
            raise ValidationError("investigation_minutes must be >= 0")
        if manual_baseline_minutes is not None and manual_baseline_minutes < 0:
            raise ValidationError("manual_baseline_minutes must be >= 0")
        if pipeline_value < 0:
            raise ValidationError("pipeline_value must be >= 0")

        with self.core.connection() as connection:
            exists = connection.execute(
                "SELECT 1 FROM surfaces WHERE external_id = ?", (entity_id,)
            ).fetchone()
            if exists is None:
                raise KeyError(f"unknown surface: {entity_id}")
            connection.execute(
                """
                INSERT INTO action_reviews(
                    external_id, outcome, investigation_minutes,
                    manual_baseline_minutes, pipeline_value, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity_id,
                    normalized_outcome,
                    float(investigation_minutes),
                    None if manual_baseline_minutes is None else float(manual_baseline_minutes),
                    float(pipeline_value),
                    notes.strip(),
                    utc_now(),
                ),
            )

        # Keep the immutable core history as the canonical outcome timeline.
        self.core.record_outcome(entity_id, normalized_outcome, notes)

    def reviews(self) -> list[dict[str, Any]]:
        with self.core.connection() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM action_reviews ORDER BY id DESC"
                )
            ]

    def metrics(self) -> EconomicMetrics:
        rows = self.core.rows()
        reviews = self.reviews()
        signals = len(rows)
        qualified_actions = sum(
            row["action"] not in {"ignore", "save"} for row in rows
        )
        useful_actions = sum(
            review["outcome"] in self.USEFUL_OUTCOMES for review in reviews
        )
        investigation_minutes = round(
            sum(float(review["investigation_minutes"]) for review in reviews), 2
        )
        estimated_manual_minutes = round(
            sum(
                float(review["manual_baseline_minutes"])
                for review in reviews
                if review["manual_baseline_minutes"] is not None
            ),
            2,
        )
        estimated_minutes_saved = round(
            max(0.0, estimated_manual_minutes - investigation_minutes), 2
        )
        pipeline_value = round(
            sum(float(review["pipeline_value"]) for review in reviews), 2
        )
        minutes_per_useful_action = (
            round(investigation_minutes / useful_actions, 2)
            if useful_actions
            else None
        )
        operator_hours = investigation_minutes / 60
        pipeline_per_operator_hour = (
            round(pipeline_value / operator_hours, 2)
            if operator_hours > 0
            else None
        )
        return EconomicMetrics(
            signals=signals,
            qualified_actions=qualified_actions,
            reviewed_actions=len(reviews),
            useful_actions=useful_actions,
            investigation_minutes=investigation_minutes,
            estimated_manual_minutes=estimated_manual_minutes,
            estimated_minutes_saved=estimated_minutes_saved,
            pipeline_value=pipeline_value,
            minutes_per_useful_action=minutes_per_useful_action,
            pipeline_per_operator_hour=pipeline_per_operator_hour,
        )
