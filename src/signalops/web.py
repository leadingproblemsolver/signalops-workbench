"""Minimal web surface for the SignalOps decision layer.

This intentionally keeps collection and external execution out of scope. Users submit
observed evidence, SignalOps applies the existing deterministic policy engine, and the
web layer exposes a decision queue plus outcome capture.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field, HttpUrl

from .core import Store, ValidationError


DB_PATH = os.getenv("SIGNALOPS_DB", "data/signalops.db")
store = Store(Path(DB_PATH))
app = FastAPI(title="SignalOps", version="0.1.0")


class SignalIn(BaseModel):
    channel: str = Field(min_length=1, max_length=64)
    title: str = Field(min_length=1, max_length=240)
    url: HttpUrl
    observed_fact: str = Field(min_length=1, max_length=6000)
    inference: str = Field(default="", max_length=3000)
    who: str = Field(default="", max_length=240)
    relevance: float = Field(ge=0, le=10)
    urgency: float = Field(ge=0, le=10)
    conversation: float = Field(ge=0, le=10)
    responded: bool = False


class OutcomeIn(BaseModel):
    outcome: str
    notes: str = Field(default="", max_length=3000)


def _ensure_default_policy(channel: str) -> None:
    """Create a conservative policy for a new channel on first use."""

    normalized = channel.strip().lower()
    try:
        store.policy(normalized)
    except KeyError:
        store.configure_policy(
            {
                "channel": normalized,
                "reply_threshold": 6.0,
                "dm_threshold": 8.0,
                "call_threshold": 9.0,
                "dm_requires_response": True,
            }
        )


def _economics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts: dict[str, int] = {}
    for row in rows:
        action = str(row["action"])
        action_counts[action] = action_counts.get(action, 0) + 1

    actionable = sum(
        count
        for action, count in action_counts.items()
        if action not in {"ignore", "save"}
    )
    total = len(rows)
    promotion_rate = round((actionable / total) * 100, 1) if total else 0.0

    outcome_counts: dict[str, int] = {}
    for event in store.events():
        if event["event_type"] != "outcome_recorded":
            continue
        outcome = str(event["payload"]["outcome"])
        outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

    return {
        "signals": total,
        "actionable": actionable,
        "promotion_rate_pct": promotion_rate,
        "actions": action_counts,
        "outcomes": outcome_counts,
        "economic_metric_status": {
            "primary": "minutes of human investigation / economically useful action",
            "north_star": "pipeline dollars generated / operator hour",
            "instrumentation": "not yet captured; do not claim ROI until time and pipeline attribution are recorded",
        },
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/signals")
def create_signal(signal: SignalIn) -> dict[str, Any]:
    _ensure_default_policy(signal.channel)
    try:
        surface, decision = store.process(
            channel=signal.channel,
            title=signal.title,
            url=str(signal.url),
            pain=signal.inference,
            exact_language=signal.observed_fact,
            relevance=signal.relevance,
            urgency=signal.urgency,
            conversation=signal.conversation,
            responded=signal.responded,
            who=signal.who,
        )
    except (ValidationError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "external_id": surface.external_id,
        "observed_fact": surface.exact_language,
        "inference": surface.pain,
        "decision": decision.to_dict(),
    }


@app.get("/api/actions")
def actions(channel: str | None = None) -> list[dict[str, Any]]:
    return store.rows(channel)


@app.get("/api/metrics")
def metrics() -> dict[str, Any]:
    return _economics(store.rows())


@app.post("/api/outcomes/{external_id}")
def outcome(external_id: str, body: OutcomeIn) -> dict[str, str]:
    try:
        store.record_outcome(external_id, body.outcome, body.notes)
    except (ValidationError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"status": "recorded"}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>SignalOps — evidence to justified GTM action</title>
  <style>
    :root { color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #090b10; color: #f5f7fb; }
    main { width: min(1180px, 94vw); margin: 0 auto; padding: 42px 0 72px; }
    .eyebrow { color: #9aa4b2; font-size: 12px; text-transform: uppercase; letter-spacing: .16em; }
    h1 { font-size: clamp(38px, 6vw, 74px); line-height: .98; max-width: 930px; margin: 12px 0 18px; }
    .lead { color: #b8c0cc; font-size: 18px; max-width: 780px; line-height: 1.6; }
    .grid { display: grid; gap: 16px; }
    .metrics { grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); margin: 30px 0; }
    .metric, .panel, .action { background: #11151d; border: 1px solid #222936; border-radius: 16px; }
    .metric { padding: 18px; }
    .metric strong { display: block; font-size: 28px; margin-top: 5px; }
    .panel { padding: 22px; margin-top: 18px; }
    form { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 12px; }
    label { font-size: 12px; color: #aeb7c4; }
    input, textarea, select, button { width: 100%; margin-top: 6px; padding: 11px 12px; border-radius: 10px; border: 1px solid #2a3241; background: #0b0f16; color: #f6f8fb; }
    textarea { min-height: 110px; resize: vertical; }
    .full { grid-column: 1 / -1; }
    button { background: #f4f7fb; color: #0b0d11; font-weight: 700; cursor: pointer; }
    .queue { display: grid; gap: 12px; margin-top: 12px; }
    .action { padding: 16px; }
    .row { display: flex; gap: 10px; justify-content: space-between; align-items: baseline; flex-wrap: wrap; }
    .pill { display: inline-block; padding: 4px 8px; border-radius: 999px; background: #202838; font-size: 12px; }
    .muted { color: #98a3b3; }
    .fact { margin: 10px 0 6px; }
    .inference { color: #c8d1dd; }
    a { color: #b9d6ff; }
    @media (max-width: 720px) { form { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
<main>
  <div class="eyebrow">SignalOps / microSaaS v0</div>
  <h1>From noisy market evidence to justified GTM action.</h1>
  <p class="lead">Preserve the fact. Keep the inference separate. Rank what deserves action. Enforce permission boundaries. Record the outcome.</p>

  <section class="grid metrics" id="metrics"></section>

  <section class="panel">
    <div class="row"><h2>Capture one signal</h2><span class="muted">manual-first by design</span></div>
    <form id="signal-form">
      <label>Channel<input name="channel" value="reddit" required /></label>
      <label>Who / account<input name="who" placeholder="Founder or company" /></label>
      <label class="full">Title<input name="title" placeholder="Launch got users but no qualified conversations" required /></label>
      <label class="full">Source URL<input name="url" type="url" placeholder="https://..." required /></label>
      <label class="full">Observed fact<textarea name="observed_fact" placeholder="Exact public evidence. No interpretation." required></textarea></label>
      <label class="full">Inference<textarea name="inference" placeholder="What this may mean. Keep it falsifiable."></textarea></label>
      <label>Relevance 0–10<input name="relevance" type="number" min="0" max="10" step="0.1" value="7" required /></label>
      <label>Urgency 0–10<input name="urgency" type="number" min="0" max="10" step="0.1" value="6" required /></label>
      <label>Conversation potential 0–10<input name="conversation" type="number" min="0" max="10" step="0.1" value="7" required /></label>
      <label>Prior public response?
        <select name="responded"><option value="false">No</option><option value="true">Yes</option></select>
      </label>
      <div class="full"><button type="submit">Resolve next action</button></div>
    </form>
    <p id="form-status" class="muted"></p>
  </section>

  <section class="panel">
    <div class="row"><h2>Decision queue</h2><button style="width:auto" onclick="refresh()">Refresh</button></div>
    <div id="queue" class="queue"></div>
  </section>
</main>
<script>
const esc = (s='') => String(s).replace(/[&<>'\"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','\"':'&quot;'}[c]));

async function refresh() {
  const [metrics, actions] = await Promise.all([
    fetch('/api/metrics').then(r => r.json()),
    fetch('/api/actions').then(r => r.json())
  ]);
  document.getElementById('metrics').innerHTML = [
    ['Signals', metrics.signals],
    ['Promoted to action', metrics.actionable],
    ['Promotion rate', metrics.promotion_rate_pct + '%'],
    ['Conversions recorded', metrics.outcomes.converted || 0]
  ].map(([k,v]) => `<div class="metric"><span class="muted">${k}</span><strong>${v}</strong></div>`).join('');

  document.getElementById('queue').innerHTML = actions.length ? actions.map(a => `
    <article class="action">
      <div class="row"><strong>${esc(a.title)}</strong><span class="pill">${esc(a.action)} · ${a.score}</span></div>
      <div class="fact"><b>Observed:</b> ${esc(a.exact_language)}</div>
      <div class="inference"><b>Inference:</b> ${esc(a.pain || '—')}</div>
      <p class="muted">${esc(a.reason)}</p>
      <div class="row"><a href="${esc(a.url)}" target="_blank" rel="noreferrer">source</a><span class="muted">${esc(a.channel)} · ${esc(a.who || 'unassigned')}</span></div>
    </article>`).join('') : '<p class="muted">No signals yet.</p>';
}

document.getElementById('signal-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = new FormData(e.currentTarget);
  const body = Object.fromEntries(fd.entries());
  ['relevance','urgency','conversation'].forEach(k => body[k] = Number(body[k]));
  body.responded = body.responded === 'true';
  const res = await fetch('/api/signals', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)});
  const data = await res.json();
  document.getElementById('form-status').textContent = res.ok
    ? `Decision: ${data.decision.action} (${data.decision.score}) — ${data.decision.reason}`
    : `Error: ${data.detail || 'unknown error'}`;
  if (res.ok) refresh();
});

refresh();
</script>
</body>
</html>"""
