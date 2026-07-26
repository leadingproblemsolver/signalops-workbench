"""Deterministic policy engine and durable workflow state for SignalOps."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterator, Mapping
from urllib.parse import urlparse, urlunparse


class ValidationError(ValueError):
    """Raised when a policy or evidence surface violates the public contract."""


class Action(StrEnum):
    IGNORE = "ignore"
    SAVE = "save"
    PUBLIC_REPLY = "public_reply"
    DM = "dm"
    CALL = "call"


@dataclass(frozen=True, slots=True)
class Policy:
    channel: str
    reply_threshold: float = 6.0
    dm_threshold: float = 8.0
    call_threshold: float = 9.0
    dm_requires_response: bool = True

    def __post_init__(self) -> None:
        channel = self.channel.strip().lower()
        if not channel:
            raise ValidationError("policy.channel is required")
        object.__setattr__(self, "channel", channel)

        thresholds = (
            self.reply_threshold,
            self.dm_threshold,
            self.call_threshold,
        )
        if not all(isinstance(value, (int, float)) for value in thresholds):
            raise ValidationError("policy thresholds must be numeric")
        if not all(0 <= float(value) <= 10 for value in thresholds):
            raise ValidationError("policy thresholds must be within 0..10")
        if not self.reply_threshold <= self.dm_threshold <= self.call_threshold:
            raise ValidationError(
                "policy thresholds must satisfy reply <= dm <= call"
            )

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "Policy":
        try:
            return cls(
                channel=str(data["channel"]),
                reply_threshold=float(data.get("reply_threshold", 6)),
                dm_threshold=float(data.get("dm_threshold", 8)),
                call_threshold=float(data.get("call_threshold", 9)),
                dm_requires_response=bool(data.get("dm_requires_response", True)),
            )
        except KeyError as exc:
            raise ValidationError(f"missing policy field: {exc.args[0]}") from exc


@dataclass(frozen=True, slots=True)
class Surface:
    channel: str
    title: str
    url: str
    pain: str
    exact_language: str
    relevance: float
    urgency: float
    conversation: float
    external_id: str = ""
    responded: bool = False
    who: str = ""

    def __post_init__(self) -> None:
        normalized_channel = self.channel.strip().lower()
        normalized_url = canonical_url(self.url)
        normalized_title = self.title.strip()
        normalized_language = self.exact_language.strip()

        if not normalized_channel:
            raise ValidationError("surface.channel is required")
        if not normalized_title:
            raise ValidationError("surface.title is required")
        if not normalized_language:
            raise ValidationError("surface.exact_language is required")

        for name in ("relevance", "urgency", "conversation"):
            value = getattr(self, name)
            if not isinstance(value, (int, float)) or not 0 <= float(value) <= 10:
                raise ValidationError(f"surface.{name} must be within 0..10")

        object.__setattr__(self, "channel", normalized_channel)
        object.__setattr__(self, "url", normalized_url)
        object.__setattr__(self, "title", normalized_title)
        object.__setattr__(self, "exact_language", normalized_language)
        object.__setattr__(self, "pain", self.pain.strip())
        object.__setattr__(self, "who", self.who.strip())
        object.__setattr__(
            self,
            "external_id",
            self.external_id.strip()
            or stable_id(normalized_channel, normalized_url, normalized_title),
        )


@dataclass(frozen=True, slots=True)
class Decision:
    action: Action
    score: float
    reason: str
    trace: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action.value,
            "score": self.score,
            "reason": self.reason,
            "trace": list(self.trace),
        }


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def canonical_url(value: str) -> str:
    """Return a stable HTTP(S) URL representation suitable for deduplication."""

    raw = value.strip()
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError("surface.url must be an absolute http(s) URL")
    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        fragment="",
    )
    return urlunparse(normalized)


def stable_id(channel: str, url: str, title: str) -> str:
    canonical = f"{channel.strip().lower()}|{canonical_url(url)}|{title.strip()}"
    return sha256(canonical.encode("utf-8")).hexdigest()[:24]


def decide(surface: Surface, policy: Policy) -> Decision:
    """Evaluate a surface deterministically under a channel policy."""

    if surface.channel != policy.channel:
        raise ValidationError(
            f"surface channel {surface.channel!r} does not match policy "
            f"channel {policy.channel!r}"
        )

    score = round(
        0.50 * surface.relevance
        + 0.30 * surface.conversation
        + 0.20 * surface.urgency,
        2,
    )
    trace = (
        f"score={score}",
        "formula=.50 relevance + .30 conversation + .20 urgency",
        f"reply_threshold={policy.reply_threshold}",
        f"dm_threshold={policy.dm_threshold}",
        f"call_threshold={policy.call_threshold}",
        f"responded={surface.responded}",
    )

    if surface.relevance < 4:
        return Decision(
            Action.IGNORE,
            score,
            "Relevance is below the useful-problem threshold.",
            trace,
        )
    if score >= policy.call_threshold and surface.responded:
        return Decision(
            Action.CALL,
            score,
            "Call threshold and prior-response permission are satisfied.",
            trace,
        )
    if score >= policy.dm_threshold and policy.dm_requires_response and not surface.responded:
        return Decision(
            Action.PUBLIC_REPLY,
            score,
            "Private escalation is blocked until a public response exists.",
            trace,
        )
    if score >= policy.dm_threshold:
        return Decision(
            Action.DM,
            score,
            "DM threshold and permission requirements are satisfied.",
            trace,
        )
    if score >= policy.reply_threshold:
        return Decision(
            Action.PUBLIC_REPLY,
            score,
            "Public-reply threshold is satisfied.",
            trace,
        )
    return Decision(
        Action.SAVE,
        score,
        "Preserve the evidence; no contact threshold is satisfied.",
        trace,
    )


_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS policies (
    channel TEXT PRIMARY KEY,
    data_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS surfaces (
    external_id TEXT PRIMARY KEY,
    channel TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    who TEXT NOT NULL,
    pain TEXT NOT NULL,
    exact_language TEXT NOT NULL,
    relevance REAL NOT NULL CHECK(relevance BETWEEN 0 AND 10),
    urgency REAL NOT NULL CHECK(urgency BETWEEN 0 AND 10),
    conversation REAL NOT NULL CHECK(conversation BETWEEN 0 AND 10),
    responded INTEGER NOT NULL CHECK(responded IN (0, 1)),
    action TEXT NOT NULL,
    score REAL NOT NULL CHECK(score BETWEEN 0 AND 10),
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS surfaces_channel_score_idx
ON surfaces(channel, score DESC, updated_at DESC);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    occurred_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS events_entity_idx
ON events(entity_id, id);

CREATE TRIGGER IF NOT EXISTS events_are_immutable_update
BEFORE UPDATE ON events
BEGIN
    SELECT RAISE(ABORT, 'events are immutable');
END;

CREATE TRIGGER IF NOT EXISTS events_are_immutable_delete
BEFORE DELETE ON events
BEGIN
    SELECT RAISE(ABORT, 'events are immutable');
END;
"""


class Store:
    """SQLite projection plus immutable event history."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.executescript(_SCHEMA)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA busy_timeout = 5000")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _event(
        connection: sqlite3.Connection,
        entity_id: str,
        event_type: str,
        payload: Mapping[str, Any],
    ) -> None:
        connection.execute(
            """
            INSERT INTO events(entity_id, event_type, payload_json, occurred_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                entity_id,
                event_type,
                json.dumps(payload, ensure_ascii=False, sort_keys=True),
                utc_now(),
            ),
        )

    def configure_policy(self, data: Mapping[str, Any]) -> Policy:
        policy = Policy.from_mapping(data)
        timestamp = utc_now()
        payload = asdict(policy)
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO policies(channel, data_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(channel) DO UPDATE SET
                    data_json = excluded.data_json,
                    updated_at = excluded.updated_at
                """,
                (policy.channel, json.dumps(payload, sort_keys=True), timestamp),
            )
            self._event(connection, policy.channel, "policy_configured", payload)
        return policy

    def policy(self, channel: str) -> Policy:
        normalized = channel.strip().lower()
        with self.connection() as connection:
            row = connection.execute(
                "SELECT data_json FROM policies WHERE channel = ?",
                (normalized,),
            ).fetchone()
        if row is None:
            raise KeyError(f"channel policy not configured: {normalized}")
        return Policy.from_mapping(json.loads(row["data_json"]))

    def process(self, **data: Any) -> tuple[Surface, Decision]:
        surface = Surface(**data)
        decision = decide(surface, self.policy(surface.channel))
        timestamp = utc_now()

        with self.connection() as connection:
            previous = connection.execute(
                "SELECT external_id FROM surfaces WHERE external_id = ?",
                (surface.external_id,),
            ).fetchone()
            connection.execute(
                """
                INSERT INTO surfaces(
                    external_id, channel, title, url, who, pain, exact_language,
                    relevance, urgency, conversation, responded, action, score,
                    reason, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(external_id) DO UPDATE SET
                    channel = excluded.channel,
                    title = excluded.title,
                    url = excluded.url,
                    who = excluded.who,
                    pain = excluded.pain,
                    exact_language = excluded.exact_language,
                    relevance = excluded.relevance,
                    urgency = excluded.urgency,
                    conversation = excluded.conversation,
                    responded = excluded.responded,
                    action = excluded.action,
                    score = excluded.score,
                    reason = excluded.reason,
                    updated_at = excluded.updated_at
                """,
                (
                    surface.external_id,
                    surface.channel,
                    surface.title,
                    surface.url,
                    surface.who,
                    surface.pain,
                    surface.exact_language,
                    surface.relevance,
                    surface.urgency,
                    surface.conversation,
                    int(surface.responded),
                    decision.action.value,
                    decision.score,
                    decision.reason,
                    timestamp,
                    timestamp,
                ),
            )
            self._event(
                connection,
                surface.external_id,
                "surface_updated" if previous else "surface_created",
                {
                    "surface": asdict(surface),
                    "decision": decision.to_dict(),
                },
            )
        return surface, decision

    def record_outcome(
        self,
        external_id: str,
        outcome: str,
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
        with self.connection() as connection:
            row = connection.execute(
                "SELECT external_id FROM surfaces WHERE external_id = ?",
                (entity_id,),
            ).fetchone()
            if row is None:
                raise KeyError(f"unknown surface: {entity_id}")
            self._event(
                connection,
                entity_id,
                "outcome_recorded",
                {"outcome": normalized_outcome, "notes": notes.strip()},
            )

    def rows(self, channel: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM surfaces"
        args: tuple[Any, ...] = ()
        if channel:
            query += " WHERE channel = ?"
            args = (channel.strip().lower(),)
        query += " ORDER BY score DESC, updated_at DESC, external_id ASC"
        with self.connection() as connection:
            return [dict(row) for row in connection.execute(query, args)]

    def events(self, entity_id: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM events"
        args: tuple[Any, ...] = ()
        if entity_id:
            query += " WHERE entity_id = ?"
            args = (entity_id,)
        query += " ORDER BY id ASC"
        with self.connection() as connection:
            rows = connection.execute(query, args).fetchall()
        return [
            {
                **dict(row),
                "payload": json.loads(row["payload_json"]),
            }
            for row in rows
        ]
