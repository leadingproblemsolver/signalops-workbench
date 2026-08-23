"""Bounded SerpApi acquisition for live, source-linked SignalOps evidence.

The adapter deliberately does one thing: turn a Google Search API response into
small provenance-carrying evidence objects. It does not decide what action to take;
that remains the responsibility of the existing deterministic SignalOps policy core.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class SerpApiError(RuntimeError):
    """Raised when SerpApi cannot produce a valid structured search response."""


@dataclass(frozen=True, slots=True)
class SerpEvidence:
    query: str
    title: str
    url: str
    snippet: str
    source: str
    position: int
    date: str = ""
    search_id: str = ""

    @property
    def observed_fact(self) -> str:
        """Return only source-provided language; never mix in interpretation."""

        return self.snippet.strip() or self.title.strip()


Transport = Callable[[Request, float], bytes]


def _default_transport(request: Request, timeout: float) -> bytes:
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS endpoint
            return response.read()
    except HTTPError as exc:
        raise SerpApiError(f"SerpApi HTTP error: {exc.code}") from exc
    except URLError as exc:
        raise SerpApiError(f"SerpApi network error: {exc.reason}") from exc


class SerpApiClient:
    """Small Google Search API client with an injectable transport for tests."""

    endpoint = "https://serpapi.com/search.json"

    def __init__(
        self,
        api_key: str | None = None,
        *,
        timeout: float = 12.0,
        transport: Transport | None = None,
    ) -> None:
        self.api_key = (api_key or os.getenv("SERPAPI_API_KEY", "")).strip()
        if not self.api_key:
            raise SerpApiError("SERPAPI_API_KEY is required")
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.timeout = float(timeout)
        self.transport = transport or _default_transport

    def search_google(
        self,
        query: str,
        *,
        limit: int = 10,
        location: str | None = None,
        gl: str = "us",
        hl: str = "en",
    ) -> list[SerpEvidence]:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query is required")
        if not 1 <= limit <= 20:
            raise ValueError("limit must be within 1..20")

        params: dict[str, str | int] = {
            "engine": "google",
            "q": normalized_query,
            "api_key": self.api_key,
            "output": "json",
            "num": limit,
            "gl": gl.strip().lower() or "us",
            "hl": hl.strip().lower() or "en",
        }
        if location and location.strip():
            params["location"] = location.strip()

        request = Request(
            f"{self.endpoint}?{urlencode(params)}",
            headers={"Accept": "application/json", "User-Agent": "SignalOps-SerpApi/1.0"},
            method="GET",
        )
        raw = self.transport(request, self.timeout)

        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SerpApiError("SerpApi returned invalid JSON") from exc

        if not isinstance(payload, dict):
            raise SerpApiError("SerpApi response must be a JSON object")
        if payload.get("error"):
            raise SerpApiError(f"SerpApi error: {payload['error']}")

        metadata = payload.get("search_metadata") or {}
        search_id = str(metadata.get("id") or "") if isinstance(metadata, dict) else ""
        organic = payload.get("organic_results") or []
        if not isinstance(organic, list):
            raise SerpApiError("SerpApi organic_results must be a list")

        evidence: list[SerpEvidence] = []
        for item in organic:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            link = str(item.get("link") or "").strip()
            if not title or not link.startswith(("http://", "https://")):
                continue
            snippet = str(item.get("snippet") or "").strip()
            source = str(item.get("source") or item.get("displayed_link") or "").strip()
            date = str(item.get("date") or "").strip()
            try:
                position = int(item.get("position") or len(evidence) + 1)
            except (TypeError, ValueError):
                position = len(evidence) + 1

            evidence.append(
                SerpEvidence(
                    query=normalized_query,
                    title=title,
                    url=link,
                    snippet=snippet,
                    source=source,
                    position=position,
                    date=date,
                    search_id=search_id,
                )
            )
            if len(evidence) >= limit:
                break

        return evidence
