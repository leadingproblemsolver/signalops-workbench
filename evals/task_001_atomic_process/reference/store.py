"""Reference implementation for the atomic projection/event evaluation."""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import sqlite3
from typing import Iterator


_SCHEMA = """
CREATE TABLE IF NOT EXISTS surfaces (
    external_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    score REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL
);
"""


class Store:
    def __init__(self, path: str | Path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as connection:
            connection.executescript(_SCHEMA)

    @contextmanager
    def connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
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
        title: str,
        *,
        fail_event: bool,
    ) -> None:
        if fail_event:
            raise RuntimeError("injected event write failure")
        connection.execute(
            """
            INSERT INTO events(entity_id, event_type, payload)
            VALUES (?, 'surface_processed', ?)
            """,
            (entity_id, title),
        )

    def process(
        self,
        external_id: str,
        title: str,
        score: float,
        *,
        fail_event: bool = False,
    ) -> None:
        """Persist the current projection and append its immutable event receipt."""
        # One transaction owns both writes. Any exception rolls both back.
        with self.connection() as connection:
            connection.execute(
                """
                INSERT INTO surfaces(external_id, title, score)
                VALUES (?, ?, ?)
                ON CONFLICT(external_id) DO UPDATE SET
                    title = excluded.title,
                    score = excluded.score
                """,
                (external_id, title, score),
            )
            self._event(connection, external_id, title, fail_event=fail_event)

    def surface(self, external_id: str):
        with self.connection() as connection:
            row = connection.execute(
                "SELECT external_id, title, score FROM surfaces WHERE external_id = ?",
                (external_id,),
            ).fetchone()
        return dict(row) if row else None

    def events(self, external_id: str):
        with self.connection() as connection:
            rows = connection.execute(
                """
                SELECT entity_id, event_type, payload
                FROM events
                WHERE entity_id = ?
                ORDER BY id ASC
                """,
                (external_id,),
            ).fetchall()
        return [dict(row) for row in rows]
