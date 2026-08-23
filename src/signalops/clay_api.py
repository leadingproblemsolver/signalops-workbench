from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


Transport = Callable[
    [str, str, Mapping[str, str], Mapping[str, Any] | None, float],
    tuple[int, Mapping[str, Any]],
]


class ClayAPIError(RuntimeError):
    def __init__(self, status: int | None, message: str, *, body: Mapping[str, Any] | None = None):
        self.status = status
        self.message = message
        self.body = dict(body or {})
        prefix = f"Clay API {status}" if status is not None else "Clay transport"
        super().__init__(f"{prefix}: {message}")


def _default_transport(
    method: str,
    url: str,
    headers: Mapping[str, str],
    payload: Mapping[str, Any] | None,
    timeout: float,
) -> tuple[int, Mapping[str, Any]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=dict(headers), method=method)
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
            decoded: Mapping[str, Any] = json.loads(raw) if raw else {}
            return int(response.status), decoded
    except HTTPError as error:
        raw = error.read()
        try:
            decoded = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            decoded = {"message": raw.decode("utf-8", errors="replace")}
        return int(error.code), decoded
    except URLError as error:
        raise ClayAPIError(None, str(error.reason)) from error


@dataclass(frozen=True, slots=True)
class ClayRoutineStartReceipt:
    routine_id: str
    routine_run_id: str
    raw_response: Mapping[str, Any]


class ClayAPIClient:
    """Minimal server-side Clay Public API boundary.

    The client intentionally returns raw Clay result payloads. SignalOps must not
    invent enrichment fields before a live routine's exact output schema has been
    observed and a deterministic adapter is added for that specific routine.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.clay.com/public/v0",
        timeout: float = 30.0,
        transport: Transport | None = None,
    ) -> None:
        key = api_key.strip()
        if not key:
            raise ValueError("Clay Public API key is required")
        self.api_key = key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport or _default_transport

    @property
    def headers(self) -> dict[str, str]:
        return {
            "clay-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        payload: Mapping[str, Any] | None = None,
    ) -> Mapping[str, Any]:
        status, response = self.transport(
            method,
            f"{self.base_url}{path}",
            self.headers,
            payload,
            self.timeout,
        )
        if not 200 <= status < 300:
            message = str(
                response.get("message")
                or (response.get("error") or {}).get("message")
                if isinstance(response.get("error"), Mapping)
                else response.get("error")
                or "request failed"
            )
            raise ClayAPIError(status, message, body=response)
        if not isinstance(response, Mapping):
            raise ClayAPIError(status, "response body must be a JSON object")
        return response

    def me(self) -> Mapping[str, Any]:
        """Return the authenticated Clay user/workspace receipt."""
        return self._request("GET", "/me")

    def start_routine(
        self,
        routine_id: str,
        *,
        items: list[Mapping[str, Any]],
    ) -> ClayRoutineStartReceipt:
        """Start one Clay routine for 1-100 caller-defined input items.

        No routine ID or input schema is guessed here; both come from a routine
        explicitly enabled for API access in the user's Clay workspace.
        """

        rid = routine_id.strip()
        if not rid:
            raise ValueError("Clay routine_id is required")
        if not 1 <= len(items) <= 100:
            raise ValueError("Clay inline routine runs require 1-100 items")
        normalized_items: list[dict[str, Any]] = []
        for index, item in enumerate(items):
            item_id = str(item.get("id") or "").strip()
            inputs = item.get("inputs")
            if not item_id:
                raise ValueError(f"Clay routine item {index} requires stable id")
            if not isinstance(inputs, Mapping):
                raise ValueError(f"Clay routine item {index} requires inputs object")
            normalized_items.append({"id": item_id, "inputs": dict(inputs)})

        encoded_routine = quote(rid, safe=":")
        response = self._request(
            "POST",
            f"/routines/{encoded_routine}/run",
            {"items": normalized_items},
        )
        # Clay's generated/API surfaces have exposed both snake_case and camelCase
        # run-id spellings in examples. Accept either, but never synthesize one.
        run_id = str(
            response.get("routine_run_id")
            or response.get("routineRunId")
            or ""
        ).strip()
        if not run_id:
            raise ClayAPIError(200, "routine start response omitted run id", body=response)
        return ClayRoutineStartReceipt(rid, run_id, response)

    def get_routine_results(self, routine_run_id: str) -> Mapping[str, Any]:
        """Return Clay's raw routine result envelope for explicit downstream parsing."""
        run_id = quote(str(routine_run_id).strip(), safe="")
        if not run_id:
            raise ValueError("Clay routine_run_id is required")
        return self._request("GET", f"/routines/run/{run_id}/results")
