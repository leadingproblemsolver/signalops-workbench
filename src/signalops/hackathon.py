"""Judge-facing SignalOps × SerpApi opportunity discovery surface."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .core import Store, ValidationError
from .serp_ai import AIAssessmentError, OpportunityAssessor
from .serpapi import SerpApiClient, SerpApiError


DB_PATH = os.getenv("SIGNALOPS_DB", "data/signalops.db")
store = Store(Path(DB_PATH))
app = FastAPI(title="SignalOps × SerpApi", version="0.1.0")


class DiscoverIn(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    goal: str = Field(
        default="Find current, externally verifiable opportunities where a technical operator can create useful value.",
        min_length=5,
        max_length=1000,
    )
    limit: int = Field(default=8, ge=1, le=20)
    location: str = Field(default="", max_length=160)


class OutcomeIn(BaseModel):
    outcome: str = Field(min_length=2, max_length=64)
    notes: str = Field(default="", max_length=1000)


def _ensure_serp_policy() -> None:
    try:
        store.policy("serpapi")
    except KeyError:
        store.configure_policy(
            {
                "channel": "serpapi",
                "reply_threshold": 6.0,
                "dm_threshold": 8.0,
                "call_threshold": 9.0,
                "dm_requires_response": True,
            }
        )


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "serpapi_configured": bool(os.getenv("SERPAPI_API_KEY")),
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
    }


@app.post("/api/discover")
def discover(body: DiscoverIn) -> dict[str, Any]:
    try:
        search_rows = SerpApiClient().search_google(
            body.query,
            limit=body.limit,
            location=body.location or None,
        )
        assessments = OpportunityAssessor().assess(search_rows, goal=body.goal)
    except (SerpApiError, AIAssessmentError, ValueError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    _ensure_serp_policy()
    output: list[dict[str, Any]] = []
    for evidence, assessment in zip(search_rows, assessments, strict=True):
        surface, decision = store.process(
            channel="serpapi",
            title=evidence.title,
            url=evidence.url,
            pain=assessment.inference,
            exact_language=evidence.observed_fact,
            relevance=assessment.relevance,
            urgency=assessment.urgency,
            conversation=assessment.conversation,
            responded=False,
            who=assessment.who or evidence.source,
        )
        output.append(
            {
                "external_id": surface.external_id,
                "search_id": evidence.search_id,
                "position": evidence.position,
                "date": evidence.date,
                "source": evidence.source,
                "title": surface.title,
                "url": surface.url,
                "observed_fact": surface.exact_language,
                "inference": surface.pain,
                "who": surface.who,
                "decision": decision.to_dict(),
            }
        )

    return {
        "query": body.query,
        "goal": body.goal,
        "serpapi_results": len(search_rows),
        "decisions": output,
        "invariant": "SerpApi supplies evidence; AI proposes interpretation/scores; deterministic SignalOps policy authorizes the next action.",
    }


@app.post("/api/outcomes/{external_id}")
def record_outcome(external_id: str, body: OutcomeIn) -> dict[str, Any]:
    """Append a durable outcome receipt without mutating the original evidence event."""

    try:
        store.record_outcome(external_id, body.outcome, body.notes)
    except (ValidationError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    events = store.events(external_id)
    receipt = events[-1]
    return {
        "status": "recorded",
        "receipt": {
            "event_id": receipt["id"],
            "event_type": receipt["event_type"],
            "occurred_at": receipt["occurred_at"],
            "outcome": receipt["payload"]["outcome"],
            "notes": receipt["payload"].get("notes", ""),
        },
        "invariant": "Outcome receipts are appended to immutable event history; observed evidence remains unchanged.",
    }


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SignalOps × SerpApi</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui,sans-serif;color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#080b10;color:#f7f9fc}main{width:min(1120px,94vw);margin:auto;padding:48px 0 70px}.tag{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#8ea1b8}h1{font-size:clamp(40px,6vw,72px);line-height:1;margin:12px 0 16px;max-width:900px}.lead{font-size:18px;line-height:1.55;color:#aeb9c8;max-width:800px}.panel,.card{border:1px solid #253044;background:#101620;border-radius:18px}.panel{padding:20px;margin:28px 0}.grid{display:grid;grid-template-columns:2fr 1fr;gap:12px}label{font-size:12px;color:#9aa9bc}input,textarea,select,button{width:100%;margin-top:6px;border:1px solid #2b3850;border-radius:10px;background:#090e16;color:#f7f9fc;padding:12px}.full{grid-column:1/-1}button{background:#eef5ff;color:#08101a;font-weight:800;cursor:pointer}.secondary{background:#162033;color:#dce8f8}.results{display:grid;gap:14px}.card{padding:18px}.row{display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}.pill{font-size:12px;padding:5px 8px;border-radius:999px;background:#1c2940}.fact{padding:12px;margin:12px 0;background:#0a1019;border-left:3px solid #72a7ff}.inference{color:#c7d2e2}.muted{color:#8998aa;font-size:13px}.receipt-tools{margin-top:14px;display:grid;grid-template-columns:1fr 2fr;gap:8px}.receipt{margin-top:8px;color:#8fd6ad;font-size:12px}a{color:#8ec1ff}@media(max-width:720px){.grid,.receipt-tools{grid-template-columns:1fr}}
</style></head><body><main>
<div class="tag">DevNetwork 2026 · SerpApi Best AI Use Case</div>
<h1>Live web evidence → justified external action.</h1>
<p class="lead">SerpApi retrieves structured, real-time evidence. AI interprets only what the evidence supports. SignalOps keeps fact separate from inference, deterministically gates the next action, and preserves outcome receipts without rewriting the source evidence.</p>
<section class="panel"><form id="f" class="grid">
<label class="full">Live search query<input name="query" value="AI agent production reliability hiring OR looking for help" required></label>
<label class="full">Decision goal<textarea name="goal">Find current, externally verifiable opportunities where a technical operator can create useful value.</textarea></label>
<label>Results<input name="limit" type="number" min="1" max="20" value="8"></label><label>Location (optional)<input name="location" placeholder="San Francisco, California, United States"></label>
<div class="full"><button>Discover and resolve</button></div></form><p id="status" class="muted"></p></section>
<section id="results" class="results"></section>
</main><script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function recordOutcome(id){const select=document.getElementById(`outcome-${id}`);const target=document.getElementById(`receipt-${id}`);target.textContent='Recording immutable outcome receipt…';const r=await fetch(`/api/outcomes/${encodeURIComponent(id)}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({outcome:select.value,notes:'Recorded from judge-facing SignalOps × SerpApi demo.'})});const d=await r.json();if(!r.ok){target.textContent='Receipt error: '+(d.detail||'unknown');return}target.textContent=`Receipt #${d.receipt.event_id} · ${d.receipt.outcome} · ${d.receipt.occurred_at}`;}
document.getElementById('f').addEventListener('submit',async e=>{e.preventDefault();const fd=new FormData(e.currentTarget);const body=Object.fromEntries(fd.entries());body.limit=Number(body.limit);const status=document.getElementById('status');status.textContent='Querying SerpApi and evaluating evidence…';const r=await fetch('/api/discover',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const d=await r.json();if(!r.ok){status.textContent='Error: '+(d.detail||'unknown');return}status.textContent=`${d.serpapi_results} live results · ${d.invariant}`;document.getElementById('results').innerHTML=d.decisions.map(x=>`<article class="card"><div class="row"><strong>${esc(x.title)}</strong><span class="pill">${esc(x.decision.action)} · ${esc(x.decision.score)}</span></div><div class="fact"><b>Observed evidence</b><br>${esc(x.observed_fact)}</div><div class="inference"><b>AI inference</b><br>${esc(x.inference||'No supported inference.')}</div><p class="muted">${esc(x.decision.reason)} · source ${esc(x.source||'web')} ${esc(x.date||'')}</p><a href="${esc(x.url)}" target="_blank" rel="noreferrer">Inspect source ↗</a><div class="receipt-tools"><select id="outcome-${esc(x.external_id)}"><option value="saved">saved</option><option value="replied">replied</option><option value="responded">responded</option><option value="converted">converted</option><option value="rejected">rejected</option></select><button class="secondary" onclick="recordOutcome('${esc(x.external_id)}')">Record outcome receipt</button></div><div id="receipt-${esc(x.external_id)}" class="receipt"></div></article>`).join('')});
</script></body></html>"""