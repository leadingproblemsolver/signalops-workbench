# PQL Activation Engine — Segment 1 Evidence

## What this is

A refactor of the SignalOps decision/handoff kernel for one high-value GTM state transfer:

`product usage -> qualified account state -> accountable owner/action -> verifiable destination state`

This is not a generic lead-scoring demo. The implementation is designed around the parts that become expensive when product telemetry is allowed to trigger commercial action: stale evidence, ambiguous account state, missing ownership, opaque scoring, duplicate handoffs, and unverifiable writes.

## Why this matters

A common PLG/GTM stack looks like:

`PostHog / Segment / Amplitude -> warehouse / scoring -> Hightouch / custom sync -> HubSpot / Salesforce / Attio -> rep action`

The valuable engineering surface is the transition between product truth and revenue action. A high score is not sufficient by itself; the system needs evidence freshness, accountable ownership, an explainable reason payload, idempotent handoff semantics, and a destination state that can be checked after the write.

## Current implementation

`src/signalops/pql.py` turns a normalized account-usage signal into one of five explicit states:

- `monitor`
- `pql`
- `expansion_ready`
- `review`
- `stale`

The routable actions are deliberately narrower:

- `route_pql`
- `route_expansion`

Everything else terminates in `monitor` or `human_review`.

## State-transfer invariants

1. **Freshness before action** — stale usage evidence cannot produce an automatic sales route, regardless of score.
2. **Accountability before action** — a strong signal without an accountable owner is routed to human review, not silently dispatched.
3. **Commercial context before action** — missing seat denominator blocks automatic commercial routing because the adoption signal cannot be interpreted safely.
4. **Deterministic explanation** — every decision carries the component scores, thresholds, evidence age, and owner-presence trace used to reach it.
5. **Idempotent handoff** — the same account evidence, state, timestamp, and owner produce the same handoff/idempotency key.
6. **Evidence-preserving handoff** — the downstream payload carries the original usage evidence plus the expected CRM destination state rather than only an opaque score.
7. **No non-routable write** — monitor/review/stale decisions cannot be converted into a CRM handoff by the kernel.

## Current proof

`tests/test_pql.py` locks the initial contract across:

- high-usage expansion routing;
- missing-owner review;
- stale-evidence blocking;
- low-activity monitoring;
- missing seat denominator review;
- future timestamp review;
- deterministic handoff identity;
- refusal to build a handoff from a non-routable decision;
- monotonic policy thresholds.

A runnable fixture is preserved in `examples/pql_activation_cases.json` and exercised by `scripts/pql_activation_demo.py`.

## What is deliberately not claimed yet

This branch does **not** establish:

- a live PostHog/Segment/Amplitude integration;
- a live HubSpot/Salesforce/Attio write;
- read-after-write reconciliation;
- PQL precision against real historical conversions;
- rep acceptance rate;
- meetings, pipeline, expansion revenue, or production adoption.

Those are the next external receipts, not claims to infer from local tests.

## Next irreversible transition

Connect one real/sandbox telemetry source and one real CRM destination:

`product event source -> normalized account signal -> PQL kernel -> CRM write -> CRM read-back -> expected/actual state comparison`

Minimum evidence packet:

- source event/account payload;
- deterministic decision trace;
- generated idempotency key;
- outbound CRM payload;
- destination record after write;
- reconciliation result;
- one stale/ambiguous case that is correctly blocked from automatic routing.

## Employer parse

The relevant claim, once the next boundary is executed, is:

> Built an explainable product-usage activation layer that converts account telemetry into PQL/expansion actions while enforcing freshness, ownership and commercial-context gates; emits idempotent evidence-preserving CRM handoffs; and verifies the intended destination state after writes.

The value is not the scoring formula. The value is owning the state transition from noisy product telemetry to a commercial action that another system and human can safely trust.
