# SignalOps Workbench

**A policy-driven workbench that converts channel-native public evidence into durable decisions, handoffs, and qualified next actions.**

SignalOps preserves exact observed language separately from interpretation, scores relevance deterministically, enforces channel-specific permission boundaries, upserts repeated surfaces, and renders restartable action state.

## SignalOps × SerpApi — judge path

The current hackathon application turns **live SerpApi search evidence** into a provenance-preserving, AI-assisted, policy-gated queue of justified external actions:

```text
live SerpApi result
→ observed evidence + provenance
→ separate bounded AI inference
→ deterministic SignalOps policy
→ durable external identity
→ append-only outcome receipt
```

**Core invariant:** the model may interpret evidence, but it cannot authorize the final action or rewrite what the source originally said.

Start here:

- [SerpApi hackathon build](docs/HACKATHON_SERPAPI.md)
- [judge/Devpost submission pack](docs/DEVPOST_SUBMISSION.md)
- [canonical live deploy + receipt workflow](.github/workflows/hackathon-live-deploy.yml)
- [public live-status receipt](https://github.com/leadingproblemsolver/signalops-workbench/blob/proof/serpapi-live-status/proof/serpapi-live-latest.json) — authoritative only after it reports `proof_status: VERIFIED`

No additional hackathon architecture is planned before the live receipt, demo video, and submission are complete.

## MicroSaaS v0

SignalOps is being narrowed into a decision layer between market evidence and GTM action:

`observe -> preserve evidence -> separate fact/inference -> resolve confidence -> rank intervention -> enforce permission -> hand off -> record outcome`

The first ICP hypothesis is **post-build, pre-repeatable-GTM B2B micro-SaaS founders**: small technical teams that can ship rapidly but still manually decide which market evidence deserves action.

See:

- [`docs/MICROSAAS_WEDGE.md`](docs/MICROSAAS_WEDGE.md) — product wedge, ICP, economic invariant, integration boundary, market test, and kill conditions.
- [`docs/GEMINI_ICP_GTM_MAPPING_PROMPT.md`](docs/GEMINI_ICP_GTM_MAPPING_PROMPT.md) — web-research prompt for falsifying/refining the ICP and ranking acquisition surfaces.

### Run the web surface

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e .
uvicorn signalops.web:app --reload
```

Open `http://127.0.0.1:8000`.

The v0 web surface intentionally does **not** scrape or automatically send outreach. It accepts manually supplied evidence, applies the existing deterministic policy engine, exposes the decision queue, and records outcomes.

Economic metric to instrument next:

`minutes of human investigation / economically useful action`

North-star metric only after real attribution exists:

`pipeline dollars generated / operator hour`

## Proof

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/smoke_test.py
```

### Real public-corpus run

A bounded 20-signal run against real public LangChain GitHub issue surfaces is now preserved as an inspectable receipt:

- **20** surfaces processed / **20** durable events;
- **19** routed to `public_reply`;
- **1** routed to `save`;
- high scores still did **not** become DM/call actions because the policy requires a prior public response before private escalation.

Inspect the evidence and claim boundary in [`docs/REAL_RUN_20.md`](docs/REAL_RUN_20.md) and the machine-readable receipt in [`examples/real_run_20_results.json`](examples/real_run_20_results.json).

This demonstrates real-corpus policy/ranking behavior. It does **not** establish maintainer response, selection accuracy, meetings, pipeline, revenue, production adoption, or microSaaS demand.

## Boundary

Included: manual evidence ingestion, policy gates, SQLite state, ranked actions, handoffs, CRM export, minimal web decision queue, outcome capture. Excluded: scraping, mass outreach, automatic sending, private-data inference, and generative messaging.

## Portfolio signal

The repository demonstrates policy-engine design, provenance, idempotency, human-permission controls, durable workflow state, and deliberate anti-overarchitecture.

## Engineering evidence and provenance

- [Portfolio evidence](PORTFOLIO_EVIDENCE.md)
- [AI–human provenance](AI_HUMAN_PROVENANCE.md)
- [Release checklist](RELEASE_CHECKLIST.md)
