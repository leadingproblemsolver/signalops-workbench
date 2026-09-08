# Gemini Productionization Prompts — SignalOps × SerpApi

These prompts assume the current repository state. They are deliberately dependency-correct: strengthen the evidence-selection product before adding broad automation.

## Global invariant for every prompt

Paste this first whenever using Gemini as a coding agent:

```text
You are modifying https://github.com/leadingproblemsolver/signalops-workbench.

Before editing anything, inspect:
- README.md
- docs/ARCHITECTURE.md
- src/signalops/core.py
- src/signalops/hackathon.py
- src/signalops/serpapi.py
- src/signalops/serp_ai.py
- relevant existing tests

Preserve these invariants:
1. source-provided observed evidence stays separate from AI inference;
2. AI may interpret/score but may not authorize the final action;
3. deterministic SignalOps policy owns action authorization;
4. stable identity and provenance must survive enrichment/deduplication;
5. outcomes append; they do not rewrite the original evidence event;
6. no external mutation occurs without an explicit bounded authorization path;
7. never convert missing/in-progress/error enrichment into fact;
8. every new integration must have deterministic tests with injectable transports or mocks;
9. do not fabricate customer demand, ROI, conversion, production scale, or external success;
10. avoid architecture rewrites unless a real requirement forces them.

After implementation, run the narrow tests plus the complete repository test command. Report exact changed files, exact pass/fail output, and any remaining claim boundary.
```

---

# P0 — Multi-engine SerpApi acquisition

## Why
The current hackathon path uses only the Google Search engine. The strongest sponsor-aligned extension is to make SerpApi itself a richer evidence substrate rather than adding unrelated automation.

Recommended engines:
- Google Search — broad current evidence;
- Google News — company/product/regulatory/change triggers;
- Google Jobs — hiring/expansion/infrastructure demand;
- Google Trends — demand momentum / rising queries;
- Google Maps only when local-business intent is explicit.

## Gemini prompt

```text
Implement a bounded multi-engine SerpApi acquisition layer for SignalOps.

Current state:
- src/signalops/serpapi.py supports only engine=google.
- src/signalops/hackathon.py assumes one list of SerpEvidence.
- deterministic policy in src/signalops/core.py must remain the sole action authority.

Target:
A single discovery run can request a small explicit engine set and normalize each engine into one common provenance-bearing evidence contract.

Implement, in the smallest clean design:
1. an engine enum/type for google, google_news, google_jobs, google_trends;
2. per-engine bounded adapters that extract only fields actually returned by that engine;
3. provenance fields: engine, search_id, source URL, source-provided text, date/freshness when present, original rank/position;
4. a normalized evidence object without erasing engine-specific provenance;
5. deterministic cross-engine deduplication using canonical URL/identity where possible;
6. no semantic fusion by the model before raw evidence rows are preserved;
7. explicit partial-failure behavior: a failed engine is reported as failed and never silently becomes zero results;
8. API input in hackathon.py that allows an explicit engine list with a conservative default;
9. UI badges for source engine and per-engine counts;
10. tests for Normal data, Extreme data, Boundary data, and Abnormal / Erroneous data using Cambridge CIE terminology in test comments/docs.

Do not add autonomous outreach. Do not change the existing score formula. Do not remove the single-engine Google path.

Acceptance:
- existing tests green;
- new deterministic adapter tests green;
- one combined response can visibly prove which engine produced each evidence row;
- raw observed text remains distinguishable from AI inference.
```

---

# P0 — Ranking evaluation harness

## Why
The biggest product-risk is not retrieval; it is whether SignalOps actually selects better opportunities. Production value requires measurable selection quality.

## Gemini prompt

```text
Build an evaluation harness for SignalOps ranking quality without changing the production policy yet.

Goal:
Measure whether the current evidence -> AI scores -> deterministic policy ranking agrees with bounded human labels and, later, real external outcomes.

Implement:
1. a versioned JSONL evaluation format containing evidence, provenance, human label, allowed action, and optional observed outcome;
2. a CLI that runs the current assessor/policy over a fixture or recorded evidence pack;
3. metrics: Precision@K, Recall@K where defined, NDCG@K, action confusion matrix, mean score by human label, calibration buckets, and source/engine breakdown;
4. explicit separation between human-label agreement and commercial-outcome evidence;
5. a baseline comparing current ranking against source order/random order where deterministic reproduction is possible;
6. machine-readable receipt JSON + concise Markdown report;
7. deterministic tests around metric calculations;
8. no tuning against the evaluation set inside the same command.

Use existing examples/ and evals/ conventions before inventing a new layout.

Acceptance:
- one command evaluates a frozen evidence pack;
- output makes false positives visible;
- no metric is called predictive of revenue unless the dataset actually contains externally observed outcomes.
```

---

# P0 — Durable production persistence

## Why
The current Cloud Run deployment uses SQLite under /tmp, which is ephemeral. That is acceptable for judge proof but not durable production state.

## Gemini prompt

```text
Add a durable production storage path to SignalOps while preserving SQLite for local/test use.

Current state:
- src/signalops/core.py Store is SQLite-backed.
- Cloud Run currently uses SIGNALOPS_DB=/tmp/signalops-hackathon.db.
- append-only event history and stable identity semantics must not change.

Target:
Introduce the smallest storage abstraction needed for a production Postgres-compatible backend (Cloud SQL Postgres or equivalent) while retaining SQLite as the default local adapter.

Requirements:
1. preserve the current Store public behavior wherever practical;
2. add a backend boundary instead of scattering SQL conditionals through product code;
3. transactional upsert + append-only event semantics must remain atomic;
4. stable external IDs must remain unchanged across backends;
5. migrations must be explicit and versioned;
6. DATABASE_URL selects Postgres; SIGNALOPS_DB keeps SQLite local behavior;
7. connection failures fail closed and do not downgrade silently to ephemeral SQLite;
8. add health output that identifies backend type but never credentials;
9. integration tests may use a disposable Postgres service if CI already supports one; otherwise keep deterministic contract tests and document the missing external receipt;
10. provide exact Cloud Run + Cloud SQL deployment configuration, but do not claim it was deployed unless an actual receipt exists.

Do not rewrite the policy engine.
```

---

# P0 — Temporal change / trigger detection

## Why
A market-interpretation product becomes much more useful when it distinguishes "this exists" from "this changed now."

## Gemini prompt

```text
Implement provenance-preserving temporal change detection for SignalOps.

Target behavior:
Repeated scheduled evidence for the same stable surface should produce explicit change state rather than duplicate noise.

Add:
1. snapshot identity tied to stable external_id + acquisition timestamp + SerpApi search provenance;
2. deterministic comparison of source-observed fields between snapshots;
3. states: FIRST_OBSERVED, UNCHANGED, CHANGED, DISAPPEARED only when the data actually supports each state;
4. a compact change receipt showing exactly which observed fields changed;
5. freshness/novelty as separate deterministic metadata, not AI-generated fact;
6. optional AI interpretation of the observed delta only after the raw diff is preserved;
7. UI grouping by "new / changed / unchanged";
8. tests for replay, duplicate snapshots, missing dates, changed snippets, and source disappearance.

Do not call a change commercially important merely because it changed. Policy authority remains separate.
```

---

# P1 — Existing Clay enrichment as a post-selection step

## Why
The repository already has Clay company enrichment proof. The highest-value product move is not "more enrichment"; it is to enrich only after SignalOps selects a justified surface.

## Gemini prompt

```text
Connect the existing SignalOps SerpApi decision queue to the existing Clay adapter without weakening provenance.

First inspect:
- src/signalops/clay.py
- tests/test_clay_api.py
- tests/test_clay_and_role_proof.py
- docs/GTM_STACK_PROOF_RUN_2026_08_22.md

Target flow:
SerpApi live signal -> SignalOps decision -> explicit operator request for enrichment -> Clay bounded enrichment -> enrichment receipt -> refreshed decision context.

Rules:
1. do not enrich every search result automatically;
2. only a selected/approved surface may request Clay enrichment;
3. keep SerpApi evidence and Clay evidence as separate provenance records;
4. Clay in-progress/error values never become observed facts;
5. enrichment may add evidence, but AI still cannot authorize external action;
6. the UI must show "source evidence" vs "enrichment evidence" distinctly;
7. preserve existing Clay tests and add an end-to-end contract test using mocks/fixtures;
8. do not claim a live Clay API call unless a real receipt exists.

Acceptance:
One selected result can visibly move from source evidence -> requested enrichment -> bounded enrichment receipt without contaminating the original evidence event.
```

---

# P1 — Existing HubSpot handoff + read-back reconciliation

## Why
The repository already implements a bounded HubSpot company write and independent read-back reconciliation. This is the strongest downstream consequence proof once authorization exists.

## Gemini prompt

```text
Expose the existing bounded HubSpot CRM handoff from the SignalOps decision surface.

First inspect:
- src/signalops/crm.py
- tests/test_hubspot_client.py
- tests/test_crm_projection.py
- docs/GTM_STACK_PROOF_RUN_2026_08_22.md

Target flow:
selected evidence -> operator explicitly approves CRM handoff -> deterministic safe projection -> HubSpot update -> fresh GET -> reconciliation receipt.

Requirements:
1. never auto-create or mutate CRM records from AI inference;
2. only allow fields already permitted by the existing projection contract unless separately justified;
3. show intended fields before mutation;
4. require an explicit human confirmation boundary in the API/UI;
5. after HTTP success, perform the existing fresh read-back reconciliation before calling the transition VERIFIED;
6. mismatch must be visible and must not be presented as success;
7. store the HubSpot receipt as a separate outcome/handoff receipt linked to the source surface;
8. preserve secrets outside browser-visible state;
9. tests must cover approve, deny/no mutation, API failure, read-back mismatch, and verified match;
10. do not claim a real CRM write without a real external receipt.
```

---

# P1 — Scheduled monitors on Google Cloud

## Gemini prompt

```text
Add a production-safe scheduled monitoring path for SignalOps on Google Cloud.

Architecture target:
Cloud Scheduler -> authenticated Cloud Run endpoint -> explicit saved monitor -> SerpApi acquisition -> change detection -> deterministic policy -> receipt.

Requirements:
1. monitors are explicit stored objects containing query, engines, location, goal, cadence metadata, and owner/workspace;
2. scheduler endpoint must require authenticated service-to-service access;
3. do not allow arbitrary unauthenticated users to trigger expensive monitor runs;
4. one monitor execution gets a run_id and complete acquisition receipt;
5. dedupe unchanged evidence;
6. only new/changed policy-relevant signals become notification candidates;
7. no external outreach from the monitor itself;
8. include idempotency/replay behavior;
9. structured logs with run_id/monitor_id but no API keys;
10. tests plus exact gcloud configuration steps.
```

---

# P1 — Notification/webhook boundary

## Gemini prompt

```text
Add a generic outbound webhook notification boundary to SignalOps, then make Slack/email adapters thin consumers of it.

Target:
A new/changed SignalOps decision may create a notification candidate, but sending remains an explicit policy-controlled transition.

Requirements:
1. generic webhook contract first;
2. signed request or shared-secret verification where appropriate;
3. retry with bounded backoff and idempotency key;
4. event receipt for attempted/sent/failed states;
5. do not send source secrets or internal credentials;
6. notification payload must include source URL, observed evidence, separate AI inference, policy action/reason, run_id, and stable external_id;
7. no generic autonomous outreach to prospects;
8. tests for duplicate delivery prevention and failure behavior.
```

---

# P1 — Authentication / workspaces

## Gemini prompt

```text
Add the minimum multi-user boundary needed to make the Cloud Run surface safe for real use.

Prefer Google-native identity/IAP or another low-complexity OIDC path compatible with Cloud Run.

Requirements:
1. authenticated user/workspace identity;
2. saved monitors, evidence, outcomes, and CRM handoffs scoped to workspace;
3. no cross-workspace access by stable_id guessing;
4. public /health may remain minimal; product/API routes require identity;
5. audit actor identity for outcome/approval events;
6. no home-grown password storage;
7. tests for authorization boundaries;
8. document how the public hackathon demo mode differs from production auth mode.
```

---

# P2 — Google Maps / local-market mode

Use only for explicit local-business workflows.

```text
Add an optional SerpApi Google Maps acquisition adapter for local-market SignalOps use cases.

Do not mix Maps results into the generic web-search schema blindly. Preserve place identity, rating/review count only as source-returned evidence, coordinates/address when present, SerpApi search_id, and query/location provenance.

Create a local-business decision mode that can answer evidence-grounded questions such as new competitor emergence, review deterioration, category density, or location-specific demand signals. AI may interpret; deterministic policy remains action authority.

Add tests and keep this mode opt-in so generic GTM search does not become location-biased.
```

---

# P2 — YouTube / public-conversation mode

```text
Add an optional SerpApi YouTube Search adapter to detect current long-form public conversation around a target problem/category.

Preserve video URL/id, channel, title, source-provided metadata, upload/freshness fields when available, and SerpApi search provenance. Do not infer sentiment or pain as fact. If AI summarizes a video/search result, label it inference and cite the exact evidence fields used.

Keep this adapter opt-in and test normalization/failure behavior.
```

---

# P2 — Model-provider A/B evaluation (Gemini vs current OpenAI assessor)

```text
Refactor the bounded OpportunityAssessor behind a small provider interface so the current OpenAI Responses API implementation remains supported and an optional Gemini implementation can be evaluated under the exact same schema.

Do not make model choice affect deterministic policy authority.

Requirements:
1. identical OpportunityAssessment contract across providers;
2. same source rows and goal fed to both providers in evaluation mode;
3. strict structured-output validation;
4. record model/provider/version in assessment receipt;
5. evaluation command compares score agreement, human-label agreement, invalid-output rate, latency, and cost fields when observable;
6. no claim that one model is better without the frozen evaluation result;
7. production default remains explicit through configuration.
```

---

# P0 reliability/security hardening prompt

```text
Perform a production-readiness hardening pass on SignalOps × SerpApi without adding product features.

Inspect all network boundaries and the Cloud Run deployment path.

Cover:
- secrets via Google Secret Manager rather than literal deployment CLI env values;
- request/run IDs in structured logs;
- bounded retries only for retry-safe acquisition failures;
- rate limiting / abuse protection for expensive public discovery;
- explicit upstream timeout reporting;
- prompt-injection boundary: source text is untrusted evidence, never instructions;
- output schema validation remains fail-closed;
- security headers/CSP for the single-page UI;
- HTML/URL escaping and safe external links;
- API input limits already present must remain or improve;
- no secrets in receipts/logs;
- dependency vulnerability scan and pinned production image strategy;
- health/readiness distinction where useful;
- graceful zero-result state;
- tests for Normal, Extreme, Boundary, and Abnormal / Erroneous inputs.

Return a prioritized list of issues before editing. Implement only P0/P1 issues whose failure would cause false evidence, unauthorized action, secret exposure, duplicate consequence, or an unusable production surface.
```
