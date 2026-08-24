from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Mapping

from signalops.clay import ClayCompanySignal
from signalops.crm import HubSpotClient, project_hubspot_company, write_and_reconcile_company


CONFIRMATION = "I_APPROVE_ONE_HUBSPOT_COMPANY_UPDATE"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or execute one evidence-preserving Clay -> HubSpot company transition."
    )
    parser.add_argument("--company-json", type=Path, required=True, help="one raw Clay company object")
    parser.add_argument("--expected-object-id", required=True, help="HubSpot object id explicitly selected for the proof")
    parser.add_argument("--include-description", action="store_true", help="include observed Clay description in the intended CRM projection")
    parser.add_argument("--confirmation", default="", help=f"exactly {CONFIRMATION!r} to permit the PATCH")
    parser.add_argument("--output", type=Path, required=True, help="write the dry-run/live receipt here")
    return parser.parse_args()


def load_company(path: Path) -> ClayCompanySignal:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("company JSON must contain exactly one object")
    return ClayCompanySignal.from_mapping(raw)


def normalized_subset(properties: Mapping[str, Any], keys: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for key in keys:
        value = str(properties.get(key) or "").strip()
        result[key] = value.lower() if key == "domain" else value
    return result


def main() -> int:
    args = parse_args()
    signal = load_company(args.company_json)
    projection = project_hubspot_company(signal, include_description=args.include_description)
    intended = projection.properties

    dry_run = {
        "mode": "DRY_RUN",
        "source_company": signal.company,
        "clay_source_id": projection.clay_source_id,
        "operation_key": projection.operation_key,
        "expected_hubspot_object_id": str(args.expected_object_id),
        "intended_properties": intended,
        "write_permitted": False,
        "claim_boundary": "No HubSpot mutation has occurred.",
    }

    if args.confirmation != CONFIRMATION:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(dry_run, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(dry_run, indent=2, sort_keys=True))
        return 0

    token = os.environ.get("HUBSPOT_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError("HUBSPOT_ACCESS_TOKEN is required only for an approved live write")
    if not signal.domain:
        raise RuntimeError("approved live proof requires an observed Clay company domain")

    client = HubSpotClient(token)
    found = client.find_company_by_domain(signal.domain, properties=tuple(intended))
    if found is None:
        raise RuntimeError("exact Clay domain does not resolve to an existing HubSpot company; auto-create is forbidden")

    found_id = str(found.get("id") or "").strip()
    if found_id != str(args.expected_object_id).strip():
        raise RuntimeError(
            f"resolved HubSpot company id {found_id!r} does not match explicitly approved id {args.expected_object_id!r}"
        )

    before_raw = found.get("properties") or {}
    if not isinstance(before_raw, Mapping):
        raise RuntimeError("HubSpot search result properties must be an object")
    before = normalized_subset(before_raw, list(intended))
    changed_fields = sorted(
        field for field, intended_value in intended.items() if before.get(field, "") != intended_value
    )
    if not changed_fields:
        raise RuntimeError(
            "approved write would be a no-op; refusing to manufacture a state-transition receipt"
        )

    write_receipt = write_and_reconcile_company(
        client,
        hubspot_object_id=found_id,
        projection=projection,
    )
    receipt = {
        "mode": "LIVE_WRITE_READ_BACK",
        "source_company": signal.company,
        "clay_source_id": projection.clay_source_id,
        "operation_key": projection.operation_key,
        "hubspot_object_id": found_id,
        "before_properties": before,
        "intended_properties": intended,
        "changed_fields": changed_fields,
        "returned_properties": dict(write_receipt.returned_properties),
        "read_back_properties": dict(write_receipt.reconciliation.read_back_properties),
        "reconciliation_diff": [list(item) for item in write_receipt.reconciliation.reconciliation_diff],
        "matched": write_receipt.matched,
        "write_count": 1,
        "read_back_count": 1,
        "duplicate_objects_created": 0,
        "claim_boundary": (
            "This receipt proves one bounded company mutation and immediate read-back only; "
            "it does not prove production sync, adoption, pipeline, or revenue."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0 if write_receipt.matched else 2


if __name__ == "__main__":
    raise SystemExit(main())
