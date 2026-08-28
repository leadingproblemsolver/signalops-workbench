"""Minimal employer-proof GTM integration surface.

Run with:
    uvicorn signalops.gtm_web:app --reload

Clay can call POST /integrations/clay/events through an HTTP/webhook action. The route
persists a deterministic receipt and always stops at human review; it never sends outreach
or mutates a CRM.
"""

from __future__ import annotations

import os
from pathlib import Path
import secrets
from typing import Any

from fastapi import FastAPI, Header, HTTPException
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
    try:
        return store.receipts()
    except ValidationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
