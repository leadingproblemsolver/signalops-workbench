from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any, Callable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from .clay import ClayCompanySignal


_ALLOWED_HUBSPOT_COMPANY_FIELDS = frozenset({"name", "domain", "description"})
Transport = Callable[
    [str, str, Mapping[str, str], Mapping[str, Any] | None, float],
    tuple[int, Mapping[str, Any]],
]


def _normalized_value(field: str, value: object) -> str:
    text = str(value or "").strip()
    if field == "domain":
        return text.lower()
    return text


class HubSpotAPIError(RuntimeError):
    def __init__(self, status: int | None, message: str):
        self.status = status
        self.message = message
        prefix = f"HubSpot API {status}" if status is not None else "HubSpot transport"
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
        raise HubSpotAPIError(None, str(error.reason)) from error


@dataclass(frozen=True, slots=True)
class HubSpotCompanyProjection:
    """Deterministic, evidence-bounded projection into a HubSpot company mutation.

    The CRM payload intentionally contains only explicitly mapped observed fields.
    Clay enrichment outputs remain provenance/evidence and are never promoted into
    arbitrary CRM fields by inference.
    """

    source_company: str
    clay_source_id: str
    intended_properties: tuple[tuple[str, str], ...]

    @property
    def properties(self) -> dict[str, str]:
        return dict(self.intended_properties)

    @property
    def operation_key(self) -> str:
        canonical = json.dumps(
            {
                "source_company": self.source_company,
                "clay_source_id": self.clay_source_id,
                "intended_properties": self.intended_properties,
            },
            separators=(",", ":"),
            sort_keys=True,
        )
        return sha256(canonical.encode("utf-8")).hexdigest()[:24]


@dataclass(frozen=True, slots=True)
class HubSpotReconciliationReceipt:
    hubspot_object_id: str
    operation_key: str
    intended_properties: tuple[tuple[str, str], ...]
    read_back_properties: tuple[tuple[str, str], ...]
    reconciliation_diff: tuple[tuple[str, str, str], ...]

    @property
    def matched(self) -> bool:
        return not self.reconciliation_diff


@dataclass(frozen=True, slots=True)
class HubSpotWriteReceipt:
    hubspot_object_id: str
    operation_key: str
    returned_properties: tuple[tuple[str, str], ...]
    reconciliation: HubSpotReconciliationReceipt

    @property
    def matched(self) -> bool:
        return self.reconciliation.matched


class HubSpotClient:
    """Minimal HubSpot Companies API transport with explicit failure semantics.

    Authentication is bearer-token based. The client deliberately implements only
    search/read/update needed for one bounded evidence-preserving company transition;
    it does not auto-create companies or infer mutations from enrichment output.
    """

    def __init__(
        self,
        access_token: str,
        *,
        base_url: str = "https://api.hubapi.com",
        timeout: float = 15.0,
        transport: Transport | None = None,
    ) -> None:
        token = access_token.strip()
        if not token:
            raise ValueError("HubSpot access token is required")
        self.access_token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.transport = transport or _default_transport

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
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
            message = str(response.get("message") or response.get("error") or "request failed")
            raise HubSpotAPIError(status, message)
        if not isinstance(response, Mapping):
            raise HubSpotAPIError(status, "response body must be a JSON object")
        return response

    def find_company_by_domain(
        self,
        domain: str,
        *,
        properties: Sequence[str] = ("name", "domain", "description"),
    ) -> Mapping[str, Any] | None:
        normalized_domain = _normalized_value("domain", domain)
        if not normalized_domain:
            raise ValueError("company domain is required")
        response = self._request(
            "POST",
            "/crm/v3/objects/companies/search",
            {
                "filterGroups": [
                    {
                        "filters": [
                            {
                                "propertyName": "domain",
                                "operator": "EQ",
                                "value": normalized_domain,
                            }
                        ]
                    }
                ],
                "properties": list(properties),
                "limit": 2,
            },
        )
        results = response.get("results") or []
        if not isinstance(results, list):
            raise HubSpotAPIError(200, "search results must be a list")
        if len(results) > 1:
            raise HubSpotAPIError(409, f"domain {normalized_domain!r} matched multiple companies")
        return results[0] if results else None

    def get_company(
        self,
        object_id: str | int,
        *,
        properties: Sequence[str] = ("name", "domain", "description"),
    ) -> Mapping[str, Any]:
        object_id_text = quote(str(object_id).strip(), safe="")
        if not object_id_text:
            raise ValueError("HubSpot company object id is required")
        query = urlencode({"properties": ",".join(properties)})
        return self._request("GET", f"/crm/v3/objects/companies/{object_id_text}?{query}")

    def update_company(
        self,
        object_id: str | int,
        properties: Mapping[str, object],
    ) -> Mapping[str, Any]:
        intended = {
            field: _normalized_value(field, value)
            for field, value in properties.items()
        }
        if not intended:
            raise ValueError("HubSpot company update requires at least one property")
        unknown = set(intended) - _ALLOWED_HUBSPOT_COMPANY_FIELDS
        if unknown:
            raise ValueError(f"Unsupported HubSpot company fields: {sorted(unknown)}")
        object_id_text = quote(str(object_id).strip(), safe="")
        if not object_id_text:
            raise ValueError("HubSpot company object id is required")
        return self._request(
            "PATCH",
            f"/crm/v3/objects/companies/{object_id_text}",
            {"properties": intended},
        )


def project_hubspot_company(
    signal: ClayCompanySignal,
    *,
    include_description: bool = False,
) -> HubSpotCompanyProjection:
    """Create the smallest safe CRM projection from an observed Clay company.

    Identity fields are observed directly from Clay. Description is opt-in because
    some CRM portals treat it as operator-managed narrative. Enrichment values such
    as tech stack, open jobs, or recent news are deliberately not projected here.
    """

    intended: dict[str, str] = {"name": signal.company}
    if signal.domain:
        intended["domain"] = signal.domain
    if include_description and signal.description:
        intended["description"] = signal.description

    unknown = set(intended) - _ALLOWED_HUBSPOT_COMPANY_FIELDS
    if unknown:
        raise ValueError(f"Unsupported HubSpot company fields: {sorted(unknown)}")

    normalized = tuple(
        sorted((field, _normalized_value(field, value)) for field, value in intended.items())
    )
    return HubSpotCompanyProjection(
        source_company=signal.company,
        clay_source_id=signal.provenance_id,
        intended_properties=normalized,
    )


def reconcile_hubspot_company(
    projection: HubSpotCompanyProjection,
    *,
    hubspot_object_id: str | int,
    read_back_properties: Mapping[str, object],
) -> HubSpotReconciliationReceipt:
    """Compare the intended mutation with a fresh HubSpot read-back.

    Extra CRM fields are ignored. Missing or changed projected fields are explicit
    mismatches. This prevents a successful HTTP mutation from being mistaken for a
    verified state transition.
    """

    expected = projection.properties
    observed = {
        field: _normalized_value(field, read_back_properties.get(field, ""))
        for field in expected
    }

    diff: list[tuple[str, str, str]] = []
    for field, expected_value in expected.items():
        actual_value = observed[field]
        if actual_value != expected_value:
            diff.append((field, expected_value, actual_value))

    return HubSpotReconciliationReceipt(
        hubspot_object_id=str(hubspot_object_id),
        operation_key=projection.operation_key,
        intended_properties=projection.intended_properties,
        read_back_properties=tuple(sorted(observed.items())),
        reconciliation_diff=tuple(diff),
    )


def write_and_reconcile_company(
    client: HubSpotClient,
    *,
    hubspot_object_id: str | int,
    projection: HubSpotCompanyProjection,
) -> HubSpotWriteReceipt:
    """Execute exactly one bounded update, then verify it with a fresh read-back."""

    update_response = client.update_company(hubspot_object_id, projection.properties)
    returned = update_response.get("properties") or {}
    if not isinstance(returned, Mapping):
        raise HubSpotAPIError(200, "update response properties must be an object")

    read_response = client.get_company(
        hubspot_object_id,
        properties=tuple(projection.properties),
    )
    read_back = read_response.get("properties") or {}
    if not isinstance(read_back, Mapping):
        raise HubSpotAPIError(200, "read-back properties must be an object")

    reconciliation = reconcile_hubspot_company(
        projection,
        hubspot_object_id=hubspot_object_id,
        read_back_properties=read_back,
    )
    returned_properties = tuple(
        sorted(
            (
                field,
                _normalized_value(field, returned.get(field, "")),
            )
            for field in projection.properties
        )
    )
    return HubSpotWriteReceipt(
        hubspot_object_id=str(hubspot_object_id),
        operation_key=projection.operation_key,
        returned_properties=returned_properties,
        reconciliation=reconciliation,
    )
