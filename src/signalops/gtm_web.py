"""Minimal employer-proof GTM integration surface.

Run with:
    uvicorn signalops.gtm_web:app --reload

Clay can call POST /integrations/clay/events through an HTTP/webhook action. The route
persists a deterministic receipt and always stops at human review; it never sends outreach
or mutates a CRM.
"""

from __future__ import annotations

from html import escape
import os
from pathlib import Path
import secrets
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .core import ValidationError
from .gtm_ingress import ClayIngressEvent, ReceiptStore, build_clay_ingress_receipt


RECEIPT_PATH = Path(
    os.getenv("SIGNALOPS_GTM_RECEIPTS", "data/gtm_ingress_receipts.jsonl")
)
store = ReceiptStore(RECEIPT_PATH)
app = FastAPI(title="SignalOps GTM Integration Proof", version="2026-08-28.v1")


class AccountIn(BaseModel):
    name: str = Field(min_length=1, max_length=240)
    domain: str = Field(min_length=1, max_length=240)


class ContactIn(BaseModel):
    title: str = Field(min_length=1, max_length=240)
    source_id: str = Field(min_length=1, max_length=512)


class SignalIn(BaseModel):
    type: str = Field(min_length=1, max_length=32)
    value: str = Field(min_length=1, max_length=6000)
    source_ref: str = Field(min_length=1, max_length=2000)


class ClayIngressIn(BaseModel):
    account: AccountIn
    contact: ContactIn
    signals: list[SignalIn] = Field(min_length=1, max_length=50)
    fit_reasons: list[str] = Field(default_factory=list, max_length=20)


def _authorize(provided: str | None) -> None:
    expected = os.getenv("SIGNALOPS_CLAY_WEBHOOK_TOKEN", "").strip()
    if expected and (not provided or not secrets.compare_digest(expected, provided)):
        raise HTTPException(status_code=401, detail="invalid webhook token")


def _safe_receipts() -> list[dict[str, Any]]:
    try:
        return store.receipts()
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "surface": "gtm-integration-proof"}


@app.post("/integrations/clay/events")
def clay_event(
    body: ClayIngressIn,
    x_signalops_webhook_token: str | None = Header(default=None),
) -> dict[str, Any]:
    _authorize(x_signalops_webhook_token)
    try:
        event = ClayIngressEvent.from_mapping(body.model_dump())
        receipt = build_clay_ingress_receipt(event)
        persisted = store.append(receipt)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "recorded" if persisted else "duplicate",
        "persisted": persisted,
        "receipt": receipt.to_dict(),
    }


@app.get("/gtm/receipts")
def receipts(
    x_signalops_webhook_token: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    _authorize(x_signalops_webhook_token)
    return _safe_receipts()


@app.get("/gtm", response_class=HTMLResponse)
def gtm_dashboard() -> str:
    """Public, sanitized proof lens over persisted Clay ingress receipts."""

    rows = _safe_receipts()
    accounts = {str(row.get("account_domain") or "") for row in rows if row.get("account_domain")}
    contacts = {str(row.get("contact_source_id") or "") for row in rows if row.get("contact_source_id")}
    eligible = sum(row.get("personalization_state") == "eligible" for row in rows)
    no_signal = sum(row.get("personalization_state") == "explicit_no_signal" for row in rows)
    human_review = sum(row.get("next_action") == "human_review" for row in rows)
    sends = sum(bool(row.get("send_actions_executed")) for row in rows)
    crm_writes = sum(bool(row.get("crm_mutation_executed")) for row in rows)

    cards = [
        ("Ingress receipts", len(rows)),
        ("Accounts", len(accounts)),
        ("Contacts", len(contacts)),
        ("Personalization eligible", eligible),
        ("Explicit no-signal", no_signal),
        ("Human-review gated", human_review),
        ("Autonomous sends", sends),
        ("CRM mutations from ingress", crm_writes),
    ]
    card_html = "".join(
        f'<div class="metric"><span>{escape(label)}</span><strong>{value}</strong></div>'
        for label, value in cards
    )

    table_rows = []
    for row in reversed(rows[-25:]):
        counts = row.get("evidence_counts") or {}
        if not isinstance(counts, dict):
            counts = {}
        evidence = ", ".join(
            f"{escape(str(kind))}:{int(value)}"
            for kind, value in sorted(counts.items())
            if value
        ) or "—"
        reasons = row.get("fit_reasons") or []
        if not isinstance(reasons, list):
            reasons = list(reasons) if isinstance(reasons, tuple) else []
        table_rows.append(
            "<tr>"
            f"<td>{escape(str(row.get('account_name') or '—'))}</td>"
            f"<td>{escape(str(row.get('contact_title') or '—'))}</td>"
            f"<td>{escape(evidence)}</td>"
            f"<td>{escape(str(row.get('personalization_state') or '—'))}</td>"
            f"<td>{escape('; '.join(str(reason) for reason in reasons) or '—')}</td>"
            f"<td>{escape(str(row.get('next_action') or '—'))}</td>"
            "</tr>"
        )
    table_html = "".join(table_rows) or (
        '<tr><td colspan="6" class="empty">No live ingress receipt yet. '
        'The integration is implemented and CI-tested; send one authorized Clay row to create the first external receipt.</td></tr>'
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>SignalOps × Clay — GTM Integration Proof</title>
<style>
:root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: #080b10; color: #f7f9fc; }}
main {{ width: min(1220px,94vw); margin: 0 auto; padding: 48px 0 80px; }}
.eyebrow {{ color:#8fa0b5; font-size:12px; letter-spacing:.15em; text-transform:uppercase; }}
h1 {{ font-size:clamp(38px,6vw,72px); line-height:1; margin:12px 0 18px; max-width:950px; }}
.lead {{ color:#b3bfcc; font-size:18px; line-height:1.6; max-width:820px; }}
.flow {{ margin:30px 0; padding:18px 20px; background:#101620; border:1px solid #263142; border-radius:14px; overflow:auto; color:#d7e1ed; font-family:ui-monospace,SFMono-Regular,monospace; }}
.metrics {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:28px 0; }}
.metric {{ padding:16px; border:1px solid #263142; background:#101620; border-radius:14px; }}
.metric span {{ display:block; color:#91a0b3; font-size:12px; }}
.metric strong {{ display:block; font-size:28px; margin-top:6px; }}
.panel {{ margin-top:20px; padding:22px; border:1px solid #263142; background:#0e141d; border-radius:16px; }}
.badges {{ display:flex; flex-wrap:wrap; gap:8px; margin:14px 0 0; }}
.badge {{ border:1px solid #324258; padding:6px 9px; border-radius:999px; color:#c6d4e4; font-size:12px; }}
table {{ width:100%; border-collapse:collapse; margin-top:12px; font-size:13px; }}
th,td {{ text-align:left; vertical-align:top; padding:11px 10px; border-bottom:1px solid #222d3b; }}
th {{ color:#8fa0b5; font-weight:600; }}
.empty {{ color:#8fa0b5; padding:24px 10px; }}
.boundary {{ color:#b8c4d2; line-height:1.6; }}
code {{ color:#dbe9ff; }}
</style>
</head>
<body>
<main>
<div class="eyebrow">SignalOps / technical GTM execution proof</div>
<h1>Clay research → evidence-bounded GTM action.</h1>
<p class="lead">This surface shows what actually crossed the integration boundary. Facts, inference and explicit no-signal states remain separate; duplicate events collapse to one receipt; every record stops at human review before CRM mutation or outreach.</p>
<div class="flow">Clay → POST /integrations/clay/events → evidence class → deterministic receipt → duplicate suppression → human_review → future HubSpot / delivery → outcome</div>
<div class="metrics">{card_html}</div>
<section class="panel">
<h2>Execution boundary</h2>
<div class="badges">
<span class="badge">fact ≠ inference</span>
<span class="badge">no_signal is preserved</span>
<span class="badge">stable receipt IDs</span>
<span class="badge">duplicate suppression</span>
<span class="badge">human review required</span>
<span class="badge">autonomous send disabled</span>
</div>
</section>
<section class="panel">
<h2>Sanitized ingress receipts</h2>
<table>
<thead><tr><th>Account</th><th>Role</th><th>Evidence</th><th>Personalization</th><th>Fit reason</th><th>Next action</th></tr></thead>
<tbody>{table_html}</tbody>
</table>
</section>
<section class="panel boundary">
<h2>Claim boundary</h2>
<p><strong>Implemented and test-verified:</strong> HTTP ingress, evidence-state preservation, deterministic identity, duplicate suppression, receipt persistence, and human-review gating.</p>
<p><strong>Requires external receipt before claiming:</strong> live deployed Clay call, authorized HubSpot write-back, outreach execution, recipient response, pilot use, repeat use, pipeline or revenue.</p>
</section>
</main>
</body>
</html>"""
