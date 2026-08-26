# Clay + SignalOps — Human Market-Return Experiment

Date: 2026-08-25

## Why this exists

The prior logistics cold-research loop produced a clean baseline: qualified operators received a specific problem framing and a reciprocal offer, but the first meaningful action still required the stranger to stop, recall a real exception, summarize it, and send it back. Repeating the same request in a follow-up did not increase value delivered before the ask.

The next test therefore changes the unit of distribution from **personalized outbound** to **evidence-backed contribution before ask**.

Clay remains discovery and enrichment. SignalOps owns strategy eligibility, receipts, human-review boundaries, experiment state, and outcome truth.

## Baseline / control

Existing pattern:

`cold research ask -> ask for 2-3 line case -> repeat ask -> wait`

This remains historical control evidence. It must not be rewritten as one of the new strategies.

## Strategy A — RAPPORT_FIRST

Eligibility gate:
- a verifiable personal/public signal exists for the specific person;
- the signal is substantive enough for a sincere response;
- generic praise, scraped biography, title-only personalization, and invented affinity are forbidden.

Sequence:
1. Respond to the person's real viewpoint, work, achievement, or contribution. No request for a case, meeting, demo, or referral.
2. Only after a legitimate relevance bridge exists, contribute one useful observation or artifact related to their remit.
3. Ask for one low-effort reaction/correction or offer one bounded test.

Primary receipt:
- evidence-bearing reply, correction, or voluntary continuation.

Failure mode under test:
- rapport consumes time without creating a legitimate operational bridge.

## Strategy B — USEFUL_ARTIFACT_FIRST

Eligibility gate:
- company/contact evidence is sufficient to build something useful without pretending to know private operations;
- inference boundaries are visibly marked.

Sequence:
1. Build first. Deliver a concise company-relevant artifact: exception map, failure-mode checklist, control-plane sketch, reconstruction example, or diagnostic.
2. Ask only for the easiest possible correction: "which part is wrong / irrelevant / missing?"
3. Incorporate the correction and return the revised artifact.
4. Invite one real or sanitized case only after the recipient has already received value.

Primary receipt:
- correction to the artifact, use of the artifact, real case supplied, or second use.

Failure mode under test:
- artifact looks personalized but is generic or speculative and therefore creates no utility.

## Strategy C — MICRO_PILOT

Eligibility gate:
- one bounded deliverable can be completed from a tiny input;
- the adoption receipt is defined before outreach;
- scope cannot expand into free consulting by default.

Sequence:
1. Show a finished example or functioning demo first.
2. Ask for the smallest usable input: a sanitized event, one choice, one branch, or one existing artifact.
3. Return the promised output with evidence boundaries visible.
4. Test repeat use. Do not call the first reply or first demo view adoption.

Primary adoption receipts:
- `pilot_used` — recipient actually uses the returned output;
- `second_use` — recipient supplies another case or explicitly asks to reuse the workflow;
- `purchase` — commercial conversion with provenance.

Failure mode under test:
- recipient finds the example interesting but will not invest even the tiny input required for use.

## Initial experiment design

Start with 12 new qualified leads where possible: 4 per strategy, one lead per company to minimize contamination. If only 9 high-quality eligible leads are available, start 3 per strategy rather than lowering the evidence bar.

Allocation is constrained by eligibility, then balanced across role seniority, geography, and company size. Do not assign a person to `rapport_first` when no real human signal exists merely to fill a cell.

The existing 14-thread operator cohort remains the historical cold-research baseline and is not recycled immediately into these arms.

## Metrics

Do not optimize for opens or clicks. Record outcomes in this order of evidence strength:

`no_response -> human_reply -> evidence_reply -> correction/referral/pilot_started -> pilot_used -> second_use -> purchase`

An ordinary reply is not adoption. A page view is not adoption. A meeting is not adoption unless the requested workflow is actually used or creates a stronger evidenced transition.

Useful comparison fields:
- qualified leads entered;
- touches executed;
- value-before-ask compliance;
- human reply count;
- evidence-bearing reply count;
- corrections/referrals;
- pilots started;
- pilots used;
- second uses;
- purchases;
- explicit rejection;
- operator time requested before first value;
- operator time requested before first evidence-bearing transition.

## Clay enrichment contract

For each candidate, Clay may collect:
- verified company identity;
- role / work history;
- email where available;
- thought leadership;
- one verifiable human-connection signal;
- recent company operational/change signal;
- recent company news or hiring only when relevant.

Clay evidence may support a route. It may not silently become a fit claim or a message claim.

## Human-review invariants

- No autonomous sending.
- No generic compliment masquerading as rapport.
- No message claims a private workflow fact from public company evidence.
- No repeated ask when the prior touch delivered no new value.
- No contact enters `rapport_first` without a real personal signal.
- No contact enters `useful_artifact_first` without an artifact already built.
- No contact enters `micro_pilot` without a bounded deliverable and explicit adoption receipt.
- Every send remains a human-authorized external action.
- Every meaningful external event becomes a receipt or a falsified hypothesis.

## Chat / repository settlement map

The source of truth is the repository + SignalOps registry, not chat prose. Chats become narrative checkpoints after receipts land.

Technical result chats to settle after their branch checks:
- Convert Clay Workflows -> `signalops-workbench`
- Driver Recruiting Constraint Diagnostic -> `driver-hiring-insight`
- Ulomis QDB / pilot -> `ulomis-continuity-companion`
- DriftGuard -> `driftguard`
- RealityLatch logistics proof -> `realitylatch`
- Quickarity -> `quicklarity`
- TraceCrumb First-60 -> `TraceCrumb`

Controller chats that remain reusable rather than product-specific:
- Market Frontier Watch / Market Assimilation / Accelerator GTM -> `market-intel-pipeline`
- Map Technical Proof Contracts / role proof packs -> `project-spec-compiler`
- Direct GTM / P-1 / Community Embedding / First-$10k -> `direct-delivery-ops` + SignalOps
- Repo OS Generator -> `repo_os_generator`

External market-return checkpoint:
- SignalOps operator-exception GTM loop is the canonical baseline and receives the 3-strategy experiment outcomes.

Do not finalize target-unresolved artifacts until an explicit observer and desired consequence are defined.
