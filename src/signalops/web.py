"""Minimal operator-facing web app for SignalOps."""

from __future__ import annotations

import os
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .core import ValidationError
from .saas import SaaSStore

DB_PATH = os.environ.get("SIGNALOPS_DB", ".signalops/signalops.db")
store = SaaSStore(DB_PATH)
app = FastAPI(title="SignalOps", version="0.1.0")


class PolicyInput(BaseModel):
    channel: str
    reply_threshold: float = 6
    dm_threshold: float = 8
    call_threshold: float = 9
    dm_requires_response: bool = True


class SurfaceInput(BaseModel):
    channel: str
    title: str
    url: str
    pain: str = ""
    exact_language: str
    relevance: float = Field(ge=0, le=10)
    urgency: float = Field(ge=0, le=10)
    conversation: float = Field(ge=0, le=10)
    responded: bool = False
    who: str = ""
    external_id: str = ""


class ReviewInput(BaseModel):
    outcome: str
    investigation_minutes: float = Field(ge=0)
    manual_baseline_minutes: float | None = Field(default=None, ge=0)
    pipeline_value: float = Field(default=0, ge=0)
    notes: str = ""


def _translate(exc: Exception) -> HTTPException:
    if isinstance(exc, KeyError):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=422, detail=str(exc))
    return HTTPException(status_code=500, detail="unexpected error")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/policies")
def configure_policy(payload: PolicyInput) -> dict[str, Any]:
    try:
        policy = store.core.configure_policy(payload.model_dump())
        return {"channel": policy.channel}
    except Exception as exc:
        raise _translate(exc) from exc


@app.post("/api/signals")
def add_signal(payload: SurfaceInput) -> dict[str, Any]:
    try:
        surface, decision = store.core.process(**payload.model_dump())
        return {"external_id": surface.external_id, **decision.to_dict()}
    except Exception as exc:
        raise _translate(exc) from exc


@app.get("/api/actions")
def actions(channel: str | None = None) -> list[dict[str, Any]]:
    return store.core.rows(channel)


@app.post("/api/actions/{external_id}/review")
def review(external_id: str, payload: ReviewInput) -> dict[str, Any]:
    try:
        store.record_review(external_id=external_id, **payload.model_dump())
        return {"external_id": external_id, "recorded": True}
    except Exception as exc:
        raise _translate(exc) from exc


@app.get("/api/metrics")
def metrics() -> dict[str, Any]:
    return store.metrics().to_dict()


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return _HTML


_HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SignalOps — Evidence to Action</title>
<style>
:root{font-family:Inter,ui-sans-serif,system-ui;background:#0b1020;color:#eef2ff}body{margin:0}.wrap{max-width:1120px;margin:auto;padding:28px}.hero{padding:28px 0 18px}.eyebrow{color:#93c5fd;font-weight:700}.hero h1{font-size:clamp(36px,6vw,64px);line-height:1;margin:10px 0}.hero p{max-width:760px;color:#b9c3d9;font-size:18px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}.card{background:#121a2f;border:1px solid #26314f;border-radius:16px;padding:18px}.metric{font-size:30px;font-weight:800}.muted{color:#9ca9c7}.row{display:grid;grid-template-columns:1fr 1fr;gap:14px}input,textarea,select,button{width:100%;box-sizing:border-box;margin:6px 0;padding:11px;border-radius:9px;border:1px solid #33405f;background:#0e1629;color:#eef2ff}button{background:#e8eeff;color:#0b1020;font-weight:800;cursor:pointer}.action{border-left:4px solid #93c5fd}.pill{display:inline-block;padding:4px 8px;border-radius:999px;background:#1f2a44;color:#bfdbfe;font-size:12px}.small{font-size:12px}.good{color:#86efac}@media(max-width:720px){.row{grid-template-columns:1fr}}
</style>
</head>
<body><div class="wrap">
<section class="hero"><div class="eyebrow">SIGNALOPS</div><h1>Turn market evidence into justified GTM action.</h1><p>Observe → preserve evidence → rank intervention → enforce permission → hand off → measure outcome. The kernel stays deterministic; the human owns the decision.</p></section>
<div id="metrics" class="grid"></div>
<section class="row" style="margin-top:18px">
<div class="card"><h2>1. Configure channel</h2><input id="pchannel" placeholder="reddit"><button onclick="policy()">Save policy</button><div id="pmsg" class="small muted"></div></div>
<div class="card"><h2>2. Add evidence</h2><input id="channel" placeholder="reddit"><input id="title" placeholder="Signal title"><input id="url" placeholder="https://..."><input id="who" placeholder="Who / account"><textarea id="language" placeholder="Exact observed language"></textarea><input id="pain" placeholder="Observed pain"><div class="row"><input id="rel" type="number" min="0" max="10" value="8" placeholder="Relevance"><input id="urg" type="number" min="0" max="10" value="7" placeholder="Urgency"></div><input id="conv" type="number" min="0" max="10" value="8" placeholder="Conversation"><button onclick="signal()">Score signal</button><div id="smsg" class="small muted"></div></div>
</section>
<section style="margin-top:18px"><div class="card"><h2>3. Ranked actions</h2><div id="actions"></div></div></section>
</div>
<script>
const j=(u,o)=>fetch(u,o).then(async r=>{const x=await r.json();if(!r.ok)throw Error(x.detail||r.statusText);return x});
async function refresh(){const m=await j('/api/metrics');document.getElementById('metrics').innerHTML=[['Signals',m.signals],['Qualified actions',m.qualified_actions],['Min / useful action',m.minutes_per_useful_action??'—'],['Pipeline / operator hr',m.pipeline_per_operator_hour===null?'—':'$'+m.pipeline_per_operator_hour.toLocaleString()],['Est. minutes saved',m.estimated_minutes_saved],['Pipeline value', '$'+m.pipeline_value.toLocaleString()]].map(x=>`<div class="card"><div class="muted">${x[0]}</div><div class="metric">${x[1]}</div></div>`).join('');const a=await j('/api/actions');document.getElementById('actions').innerHTML=a.length?a.map(x=>`<div class="card action" style="margin:10px 0"><span class="pill">${x.action}</span> <b>${x.score.toFixed(2)}</b><h3>${x.title}</h3><div class="muted">“${esc(x.exact_language)}”</div><p>${x.reason}</p><details><summary>Record human outcome</summary><select id="o-${x.external_id}"><option>replied</option><option>responded</option><option>dm_sent</option><option>call_booked</option><option>converted</option><option>rejected</option><option>saved</option></select><input id="i-${x.external_id}" type="number" min="0" step="0.1" placeholder="Actual investigation minutes"><input id="b-${x.external_id}" type="number" min="0" step="0.1" placeholder="Estimated manual baseline minutes"><input id="v-${x.external_id}" type="number" min="0" step="1" placeholder="Attributed pipeline value"><button onclick="review('${x.external_id}')">Record receipt</button></details></div>`).join(''):'<p class="muted">No signals yet.</p>'}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function policy(){try{await j('/api/policies',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channel:pchannel.value})});pmsg.textContent='Policy configured.'}catch(e){pmsg.textContent=e.message}}
async function signal(){try{const x=await j('/api/signals',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({channel:channel.value,title:title.value,url:url.value,who:who.value,pain:pain.value,exact_language:language.value,relevance:+rel.value,urgency:+urg.value,conversation:+conv.value})});smsg.innerHTML=`<span class="good">${x.action} · ${x.score}</span> — ${x.reason}`;refresh()}catch(e){smsg.textContent=e.message}}
async function review(id){await j('/api/actions/'+id+'/review',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({outcome:document.getElementById('o-'+id).value,investigation_minutes:+document.getElementById('i-'+id).value,manual_baseline_minutes:document.getElementById('b-'+id).value===''?null:+document.getElementById('b-'+id).value,pipeline_value:+document.getElementById('v-'+id).value||0})});refresh()}
refresh();
</script></body></html>'''
