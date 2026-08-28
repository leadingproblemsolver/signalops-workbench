#!/usr/bin/env python3
"""Execute one explicitly approved HubSpot company update and verify read-back.

Dry-run is the default. A live PATCH cannot occur unless --approve-write is present.
The runner never creates a company and never promotes arbitrary Clay enrichments into CRM fields.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from signalops.clay import ClayCompanySignal
from signalops.crm import (
    HubSpotAPIError,
    HubSpotClient,
    project_hubspot_company,
    write_and_reconcile_company,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preview or execute one bounded Clay -> HubSpot company update."
    )
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--source-url", required=True)
    parser.add_argument("--observed-description", required=True)
    parser.add_argument("--expected-object-id")
    parser.add_argument(
        "--include-description",
        action="store_true",
        help="Include the observed source description in the HubSpot mutation.",
    )
    parser.add_argument(
        "--approve-write",
        action="store_true",
        help="Explicitly authorize exactly one PATCH followed by one verification GET.",
    )
    parser.add_argument("--receipt-out", type=Path)
    return parser


def _emit(payload: dict[str, Any], path: Path | None) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    print(rendered)
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")


def main() -> int:
    args = _parser().parse_args()
    token = os.getenv("HUBSPOT_ACCESS_TOKEN", "").strip()
    if not token:
        raise SystemExit("HUBSPOT_ACCESS_TOKEN is required; keep it outside the repository")

    signal = ClayCompanySignal.from_mapping(
        {
            "name": args.company_name,
            "domain": args.domain,
            "url": args.source_url,
            "description": args.observed_description,
            "enrichments": [],
        }
    )
    projection = project_hubspot_company(
        signal,
        include_description=args.include_description,
    )
    client = HubSpotClient(token)

    try:
        existing = client.find_company_by_domain(signal.domain)
    except HubSpotAPIError as exc:
        _emit(
            {
                "status": "hubspot_read_failed",
                "executed": False,
                "http_status": exc.status,
                "message": exc.message,
            },
            args.receipt_out,
        )
        return 2

    if existing is None:
        _emit(
            {
                "status": "company_not_found",
                "executed": False,
                "domain": signal.domain.lower(),
                "reason": "runner refuses to create CRM companies",
            },
            args.receipt_out,
        )
        return 3

    object_id = str(existing.get("id") or "").strip()
    if not object_id:
        raise SystemExit("HubSpot search result omitted object id")
    if args.expected_object_id and object_id != str(args.expected_object_id).strip():
        _emit(
            {
                "status": "identity_mismatch",
                "executed": False,
                "expected_object_id": str(args.expected_object_id),
                "observed_object_id": object_id,
            },
            args.receipt_out,
        )
        return 4

    current = existing.get("properties") or {}
    if not isinstance(current, dict):
        raise SystemExit("HubSpot search result properties must be an object")

    intended = projection.properties
    changes: dict[str, dict[str, str]] = {}
    for field, proposed in intended.items():
        observed = str(current.get(field) or "").strip()
        if field == "domain":
            observed = observed.lower()
        if observed != proposed:
            changes[field] = {"current": observed, "proposed": proposed}

    plan = {
        "status": "approval_required" if changes else "no_change",
        "executed": False,
        "hubspot_object_id": object_id,
        "operation_key": projection.operation_key,
        "source_company": projection.source_company,
        "clay_source_id": projection.clay_source_id,
        "changes": changes,
        "authorization_required": True,
        "mutation_limit": "exactly one company PATCH, then one verification GET",
    }

    if not args.approve_write:
        _emit(plan, args.receipt_out)
        return 0

    if not changes:
        _emit(plan, args.receipt_out)
        return 0

    try:
        receipt = write_and_reconcile_company(
            client,
            hubspot_object_id=object_id,
            projection=projection,
        )
    except HubSpotAPIError as exc:
        _emit(
            {
                **plan,
                "status": "hubspot_write_failed",
                "http_status": exc.status,
                "message": exc.message,
            },
            args.receipt_out,
        )
        return 5

    payload = {
        **plan,
        "status": "verified" if receipt.matched else "reconciliation_mismatch",
        "executed": True,
        "authorization": "explicit_cli_flag",
        "returned_properties": dict(receipt.returned_properties),
        "read_back_properties": dict(receipt.reconciliation.read_back_properties),
        "reconciliation_diff": [
            {"field": field, "expected": expected, "actual": actual}
            for field, expected, actual in receipt.reconciliation.reconciliation_diff
        ],
    }
    _emit(payload, args.receipt_out)
    return 0 if receipt.matched else 6


if __name__ == "__main__":
    raise SystemExit(main())
