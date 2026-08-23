# SignalOps × SerpApi — External Opportunity Decision Agent

**One-line pitch:** Turn live web evidence into a provenance-preserving, AI-assisted, policy-gated queue of justified external actions.

## Why SerpApi is central

SignalOps previously accepted manually supplied public evidence. This hackathon branch adds a live acquisition path powered by SerpApi's Google Search API:

`SerpApi live results -> source-linked evidence -> constrained AI interpretation -> deterministic SignalOps policy -> durable action queue -> outcome receipt`

Without SerpApi, this branch has no live web acquisition layer; the sponsor API is therefore functionally central rather than decorative.

## Trust boundary

- SerpApi supplies the source URL, title, snippet, freshness metadata, position, and search ID.
- Source-provided language is stored as observed evidence.
- The AI assessor may produce only a separate inference plus bounded relevance/urgency/conversation scores.
- The model cannot authorize outreach or overwrite observed evidence.
- Existing SignalOps policy deterministically resolves `ignore`, `save`, `public_reply`, `dm`, or `call`.
- Existing permission rules still block private escalation without a prior public response.
- SQLite preserves durable surfaces and immutable event history.

## Configure

```bash
export SERPAPI_API_KEY='...'
export OPENAI_API_KEY='...'
# optional
export OPENAI_MODEL='gpt-5.6-luna'
export SIGNALOPS_DB='data/hackathon.db'
```

## Run

```bash
python -m pip install -e .
uvicorn signalops.hackathon:app --reload
```

Open `http://127.0.0.1:8000`.

## Judge demo path

1. Enter a live query describing a current operational problem or buyer trigger.
2. Click **Discover and resolve**.
3. Show the SerpApi result count and source-linked cards.
4. Open one card's source in a new tab to prove provenance.
5. Point out the separate **Observed evidence** and **AI inference** fields.
6. Point out the deterministic action + score and policy reason.
7. Re-run the same query/result and show durable deduplication/upsert behavior in SignalOps state.
8. Record one outcome and show that the event history remains distinct from the original evidence.

## Machine-checkable gates

```bash
python -m unittest discover -s tests -v
python scripts/smoke_test.py
signalops --help
```

Live acceptance additionally requires:

- `GET /health` reports both SerpApi and AI configured;
- `POST /api/discover` returns at least one real source-linked SerpApi result;
- every returned decision contains observed evidence, a source URL, separate inference, and deterministic decision trace;
- a repeated source maps to the same stable SignalOps external ID;
- no API key appears in browser output, logs committed to the repo, screenshots, or submission artifacts.

## Claim boundary

### Verified by repository tests once CI passes

- SerpApi JSON normalization contract.
- source-language preservation.
- bounded AI assessment schema and score validation.
- deterministic SignalOps policy and durable event state inherited from the existing workbench.

### Requires live judge-run evidence

- successful SerpApi request with real credentials;
- successful OpenAI assessment with real credentials;
- deployed public demo URL;
- end-to-end latency and live-search usefulness;
- external user/judge response.

Do not claim hackathon placement, adoption, conversion, revenue, or production demand without external receipts.
