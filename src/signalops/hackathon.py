"""Judge-facing SignalOps × SerpApi opportunity discovery surface."""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import os
from pathlib import Path
from time import perf_counter
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .core import Store, ValidationError
from .serp_ai import AIAssessmentError, OpportunityAssessor
from .serpapi import SerpApiClient, SerpApiError


DB_PATH = os.getenv("SIGNALOPS_DB", "data/signalops.db")
store = Store(Path(DB_PATH))
app = FastAPI(title="SignalOps × SerpApi", version="0.2.0")


class DiscoverIn(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    goal: str = Field(
        default="Find current, externally verifiable opportunities where a technical operator can create useful value.",
        min_length=5,
        max_length=1000,
    )
    limit: int = Field(default=5, ge=1, le=20)
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


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "signalops-serpapi",
        "version": app.version,
        "serpapi_configured": bool(os.getenv("SERPAPI_API_KEY")),
        "ai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "store_backend": "sqlite",
        "persistence_scope": "configured path; Cloud Run /tmp is ephemeral",
    }


@app.post("/api/discover")
def discover(body: DiscoverIn) -> dict[str, Any]:
    started = perf_counter()
    run_id = f"run_{uuid4().hex[:12]}"
    created_at = _utc_now()

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
        decision_payload = decision.to_dict()
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
                "scores": {
                    "relevance": assessment.relevance,
                    "urgency": assessment.urgency,
                    "conversation": assessment.conversation,
                },
                "decision": decision_payload,
            }
        )

    output.sort(
        key=lambda item: (
            -float(item["decision"].get("score") or 0),
            int(item["position"] or 999),
        )
    )
    for rank, row in enumerate(output, start=1):
        row["rank"] = rank

    action_counts = Counter(str(row["decision"].get("action") or "unknown") for row in output)
    search_ids = sorted({row["search_id"] for row in output if row["search_id"]})
    top_score = max(
        (float(row["decision"].get("score") or 0) for row in output),
        default=0.0,
    )

    return {
        "run_id": run_id,
        "created_at": created_at,
        "elapsed_ms": round((perf_counter() - started) * 1000),
        "engine": "google",
        "query": body.query,
        "goal": body.goal,
        "serpapi_results": len(search_rows),
        "serpapi_search_ids": search_ids,
        "top_score": top_score,
        "action_counts": dict(sorted(action_counts.items())),
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
:root{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color-scheme:dark;--bg:#070a10;--panel:#0f1622;--panel2:#121c2b;--line:#27354a;--text:#f7f9fc;--muted:#9aa9bc;--blue:#8ec1ff;--green:#8fd6ad;--amber:#ffd58a;--danger:#ff9d9d}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top right,#12223a 0,#080b10 35%,#070a10 100%);color:var(--text)}
main{width:min(1180px,94vw);margin:auto;padding:36px 0 72px}.topline{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.tag{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#91a8c6}.live{font-size:12px;color:var(--green);border:1px solid #28523c;border-radius:999px;padding:6px 10px;background:#0b1b13}
h1{font-size:clamp(42px,6vw,76px);line-height:.98;margin:16px 0;max-width:980px;letter-spacing:-.035em}.lead{font-size:18px;line-height:1.55;color:#b4c1d2;max-width:900px}
.pipeline{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 0}.pipeline span{font-size:12px;color:#c8d5e6;border:1px solid var(--line);background:#0b111b;padding:7px 10px;border-radius:999px}.arrow{color:#61748e!important;border:0!important;background:transparent!important;padding-inline:0!important}
.panel,.card,.summary{border:1px solid var(--line);background:linear-gradient(180deg,#111927,#0d141f);border-radius:18px;box-shadow:0 12px 40px rgba(0,0,0,.22)}
.panel{padding:22px;margin:28px 0 18px}.grid{display:grid;grid-template-columns:2fr 1fr;gap:12px}label{font-size:12px;color:#9fb0c4}input,textarea,select,button{width:100%;margin-top:6px;border:1px solid #30415a;border-radius:10px;background:#090e16;color:var(--text);padding:12px;font:inherit}textarea{min-height:76px;resize:vertical}.full{grid-column:1/-1}button{background:#eef5ff;color:#08101a;font-weight:800;cursor:pointer;transition:.15s transform,.15s opacity}button:hover{transform:translateY(-1px)}button:disabled{opacity:.55;cursor:wait}.secondary{background:#162033;color:#dce8f8}.ghost{background:#0b111b;color:#c5d7eb}
.presets{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 2px}.preset{width:auto;margin:0;padding:8px 10px;font-size:12px;background:#111c2c;color:#cbd8e9}
.status{min-height:20px}.summary{display:none;padding:15px 18px;margin:0 0 16px}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.metric{padding:10px 12px;border:1px solid #27354a;border-radius:12px;background:#0b111b}.metric b{display:block;font-size:20px}.metric span{font-size:11px;color:var(--muted)}
.toolbar{display:none;justify-content:space-between;gap:10px;align-items:center;margin:12px 0}.toolbar .right{display:flex;gap:8px}.toolbar button{width:auto;margin:0;padding:9px 12px}
.results{display:grid;gap:14px}.card{padding:20px}.row{display:flex;gap:10px;align-items:center;justify-content:space-between;flex-wrap:wrap}.title-wrap{display:flex;gap:10px;align-items:center;min-width:0}.rank{width:28px;height:28px;border-radius:50%;display:grid;place-items:center;background:#1b2c44;color:#b9d5f6;font-weight:800;font-size:12px}.title{font-size:17px}.pill{font-size:12px;padding:6px 9px;border-radius:999px;background:#1c2940;white-space:nowrap}.action{background:#162b21;color:#a9e4bf;border:1px solid #28523c}.meta{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 2px}.meta span{font-size:11px;color:#9bb0c8;border:1px solid #26364c;background:#0a1019;border-radius:999px;padding:5px 8px}
.evidence-grid{display:grid;grid-template-columns:1.15fr 1fr;gap:12px;margin:12px 0}.box{border:1px solid #26364c;border-radius:12px;padding:13px;background:#0a1019}.box h3{font-size:11px;letter-spacing:.08em;text-transform:uppercase;margin:0 0 7px;color:#9bb0c8}.fact{border-left:3px solid #72a7ff}.inference{border-left:3px solid #9e85ff;color:#c7d2e2}.policy{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0}.policy-card{border:1px solid #28452f;background:#0a1710;border-radius:12px;padding:12px}.policy-card b{display:block;color:#a9e4bf}.reason{color:#b9c7d7;font-size:13px;line-height:1.45}
.scores{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.score{border:1px solid #29384e;border-radius:10px;padding:9px;background:#0a1019}.score b{font-size:16px}.score span{display:block;color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:.06em}
.card-footer{display:flex;justify-content:space-between;gap:10px;align-items:center;flex-wrap:wrap}.source{color:var(--blue);text-decoration:none}.receipt-tools{margin-top:14px;display:grid;grid-template-columns:1fr 1.6fr 1fr;gap:8px}.receipt{margin-top:8px;color:var(--green);font-size:12px}.empty{padding:26px;text-align:center;color:var(--muted);border:1px dashed #30415a;border-radius:14px}
a{color:var(--blue)}@media(max-width:760px){.grid,.evidence-grid,.policy,.receipt-tools,.summary-grid{grid-template-columns:1fr}.toolbar{align-items:flex-start;flex-direction:column}.toolbar .right{width:100%}.toolbar button{flex:1}}
</style></head><body><main>
<div class="topline"><div class="tag">SignalOps × SerpApi · Live market interpretation layer</div><div class="live">● public Cloud Run judge surface</div></div>
<h1>Turn live market evidence into an inspectable action queue.</h1>
<p class="lead">SerpApi retrieves structured real-time evidence. AI contributes a bounded interpretation. SignalOps keeps source fact separate from inference, applies deterministic permission policy, ranks the result, and preserves what happened next.</p>
<div class="pipeline"><span>Live evidence</span><span class="arrow">→</span><span>AI inference</span><span class="arrow">→</span><span>Policy authority</span><span class="arrow">→</span><span>Durable outcome</span></div>

<section class="panel"><form id="f" class="grid">
<label class="full">Live search query<input id="query" name="query" value="AI agent production reliability hiring OR looking for help" required></label>
<div class="full"><div class="presets">
<button type="button" class="preset" data-query="AI agent production reliability hiring OR looking for help" data-goal="Find current, externally verifiable opportunities where a technical operator can create useful value.">Reliability demand</button>
<button type="button" class="preset" data-query="AI infrastructure hiring platform engineer OR reliability engineer" data-goal="Find current hiring or expansion signals that imply active infrastructure, reliability, or AI-platform investment.">Hiring triggers</button>
<button type="button" class="preset" data-query="AI startup funding launch partnership enterprise deployment" data-goal="Find current company-change signals that may indicate a new commercial or technical intervention window.">Company changes</button>
</div></div>
<label class="full">Decision goal<textarea id="goal" name="goal">Find current, externally verifiable opportunities where a technical operator can create useful value.</textarea></label>
<label>Results<input name="limit" type="number" min="1" max="20" value="5"></label><label>Location (optional)<input name="location" placeholder="San Francisco, California, United States"></label>
<div class="full"><button id="discover">Discover, interpret & rank</button></div></form><p id="status" class="status muted"></p></section>

<section id="summary" class="summary"><div class="summary-grid">
<div class="metric"><b id="m-results">0</b><span>live results</span></div>
<div class="metric"><b id="m-top">0</b><span>top policy score</span></div>
<div class="metric"><b id="m-actions">0</b><span>action states</span></div>
<div class="metric"><b id="m-time">0 ms</b><span>end-to-end</span></div>
</div><p id="run-meta" class="muted"></p></section>

<div id="toolbar" class="toolbar"><strong>Ranked decision queue</strong><div class="right"><button id="export-json" class="ghost" type="button">Export evidence pack</button></div></div>
<section id="results" class="results"><div class="empty">Run a live query to produce a ranked, source-linked decision queue.</div></section>
</main><script>
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let latest=null;
const short=s=>{const t=String(s||'');return t.length>18?t.slice(0,18)+'…':t};
document.querySelectorAll('.preset').forEach(btn=>btn.addEventListener('click',()=>{document.getElementById('query').value=btn.dataset.query;document.getElementById('goal').value=btn.dataset.goal;}));
async function recordOutcome(id){const select=document.getElementById(`outcome-${id}`);const notes=document.getElementById(`notes-${id}`);const target=document.getElementById(`receipt-${id}`);target.textContent='Recording append-only outcome receipt…';try{const r=await fetch(`/api/outcomes/${encodeURIComponent(id)}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({outcome:select.value,notes:notes.value})});const d=await r.json();if(!r.ok){target.textContent='Receipt error: '+(d.detail||'unknown');return}target.textContent=`Receipt #${d.receipt.event_id} · ${d.receipt.outcome} · ${d.receipt.occurred_at}`;}catch(err){target.textContent='Receipt error: '+err;}}
function render(d){latest=d;document.getElementById('summary').style.display='block';document.getElementById('toolbar').style.display='flex';document.getElementById('m-results').textContent=d.serpapi_results;document.getElementById('m-top').textContent=d.top_score;document.getElementById('m-actions').textContent=Object.keys(d.action_counts||{}).length;document.getElementById('m-time').textContent=`${d.elapsed_ms} ms`;document.getElementById('run-meta').textContent=`${d.run_id} · SerpApi engine ${d.engine} · search ID ${short((d.serpapi_search_ids||[])[0])} · ${d.created_at}`;
const rows=d.decisions||[];if(!rows.length){document.getElementById('results').innerHTML='<div class="empty">No valid evidence rows were returned. No action was inferred.</div>';return}
document.getElementById('results').innerHTML=rows.map(x=>`<article class="card">
<div class="row"><div class="title-wrap"><span class="rank">${esc(x.rank)}</span><strong class="title">${esc(x.title)}</strong></div><span class="pill action">${esc(x.decision.action)} · ${esc(x.decision.score)}</span></div>
<div class="meta"><span>source: ${esc(x.source||'web')}</span><span>search position: ${esc(x.position)}</span>${x.date?`<span>${esc(x.date)}</span>`:''}<span>SerpApi: ${esc(short(x.search_id))}</span><span>stable ID: ${esc(short(x.external_id))}</span></div>
<div class="evidence-grid"><div class="box fact"><h3>Observed evidence</h3>${esc(x.observed_fact)}</div><div class="box inference"><h3>AI inference</h3>${esc(x.inference||'No supported inference.')}</div></div>
<div class="policy"><div class="policy-card"><b>Policy decision: ${esc(x.decision.action)}</b><div class="reason">${esc(x.decision.reason)}</div></div><div class="scores"><div class="score"><b>${esc(x.scores.relevance)}</b><span>relevance</span></div><div class="score"><b>${esc(x.scores.urgency)}</b><span>urgency</span></div><div class="score"><b>${esc(x.scores.conversation)}</b><span>conversation</span></div></div></div>
<div class="card-footer"><a class="source" href="${esc(x.url)}" target="_blank" rel="noreferrer">Inspect source ↗</a><span class="muted">AI interprets; deterministic policy authorizes.</span></div>
<div class="receipt-tools"><select id="outcome-${esc(x.external_id)}"><option value="saved">saved</option><option value="replied">replied</option><option value="responded">responded</option><option value="converted">converted</option><option value="rejected">rejected</option></select><input id="notes-${esc(x.external_id)}" placeholder="Optional observed outcome note"><button class="secondary" onclick="recordOutcome('${esc(x.external_id)}')">Record outcome receipt</button></div><div id="receipt-${esc(x.external_id)}" class="receipt"></div>
</article>`).join('');}
document.getElementById('export-json').addEventListener('click',()=>{if(!latest)return;const blob=new Blob([JSON.stringify(latest,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`signalops-${latest.run_id}.json`;a.click();URL.revokeObjectURL(url);});
document.getElementById('f').addEventListener('submit',async e=>{e.preventDefault();const btn=document.getElementById('discover');const fd=new FormData(e.currentTarget);const body=Object.fromEntries(fd.entries());body.limit=Number(body.limit);const status=document.getElementById('status');btn.disabled=true;status.textContent='Querying SerpApi → evaluating evidence → applying deterministic policy…';try{const r=await fetch('/api/discover',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});const d=await r.json();if(!r.ok){status.textContent='Error: '+(d.detail||'unknown');return}status.textContent=`${d.serpapi_results} live results ranked · ${d.invariant}`;render(d);}catch(err){status.textContent='Network error: '+err;}finally{btn.disabled=false;}});
</script></body></html>"""