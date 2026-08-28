# GTM Execution HITL Checklist — 2026-08-28

This is the only human-action queue required to turn the current GTM engineering proof into live execution receipts. Do not add another integration before these transitions are resolved.

## A. Clay → SignalOps live HTTP receipt

### Goal
Create one real external receipt proving that a Clay-qualified row crossed a deployed HTTP boundary into SignalOps, produced a deterministic receipt, and remained gated at `human_review`.

### Human actions

- [ ] **A1 — Select hosting with persistent storage.** Deploy branch `feat/gtm-live-integration-proof-2026-08-28` to a host where `data/gtm_ingress_receipts.jsonl` survives requests/restarts, or mount a persistent volume. Do not use ephemeral serverless filesystem as the evidence store.
- [ ] **A2 — Start command.** Configure the service command exactly as:
  ```bash
  uvicorn signalops.gtm_web:app --host 0.0.0.0 --port $PORT
  ```
- [ ] **A3 — Create webhook secret.** Generate a new random value for `SIGNALOPS_CLAY_WEBHOOK_TOKEN`; store it only in host/Clay secret settings. Never commit it, screenshot it, or paste it into public proof.
- [ ] **A4 — Set receipt path.** Set `SIGNALOPS_GTM_RECEIPTS` to a persistent path, e.g. `/data/gtm_ingress_receipts.jsonl` if the host mounts `/data`.
- [ ] **A5 — Health check.** Open `https://<host>/health`. Required response:
  ```json
  {"status":"ok","surface":"gtm-integration-proof"}
  ```
- [ ] **A6 — Open proof surface.** Open `https://<host>/gtm`; before the first live event it should explicitly say that no live ingress receipt exists yet.
- [ ] **A7 — Pick exactly one Clay row.** Use one already-qualified logistics row. Do not include raw email in the HTTP body. Prefer a row with a real public evidence signal; if Clay says `no strong signal`, preserve that as `no_signal` instead of manufacturing personalization.
- [ ] **A8 — Map Clay fields.** Map only:
  - company name → `account.name`
  - company domain → `account.domain`
  - current role/title → `contact.title`
  - Clay stable entity ID → `contact.source_id`
  - public/research evidence → `signals[]`
  - explicit operator fit reason → `fit_reasons[]`
- [ ] **A9 — Configure HTTP POST.** Target:
  `https://<host>/integrations/clay/events`
  with headers:
  - `Content-Type: application/json`
  - `X-SignalOps-Webhook-Token: <secret>`
- [ ] **A10 — First execution.** Run only that one Clay row. Required response predicates:
  - `status = recorded`
  - `persisted = true`
  - `receipt.next_action = human_review`
  - `receipt.send_actions_executed = false`
  - `receipt.crm_mutation_executed = false`
- [ ] **A11 — Duplicate execution.** Run the exact same row again without changing the normalized evidence. Required response predicates:
  - `status = duplicate`
  - `persisted = false`
  - same `receipt_id` as A10
- [ ] **A12 — Confirm UI.** Reload `/gtm`. Confirm the account/role appears once and that no contact source ID or email is visible.
- [ ] **A13 — Preserve receipt.** Save a sanitized response JSON and one `/gtm` screenshot. Remove secrets and unrelated/private data.
- [ ] **A14 — Promote claim only now.** Safe claim after A1–A13:
  **Executed a live Clay → SignalOps HTTP integration with evidence-state preservation, deterministic duplicate suppression, and human-review gating.**

### Stop conditions
Stop immediately if:
- the host filesystem is ephemeral and cannot preserve the receipt;
- a payload would expose raw email/PII publicly;
- the Clay signal is inferred but being labeled `fact`;
- the endpoint returns anything indicating a send or CRM mutation.

---

## B. HubSpot bounded write + read-back receipt

### Current permission fact
As inspected on 2026-08-28, HubSpot COMPANY/CONTACT/DEAL reads are available, while corresponding writes require reauthorization. Therefore a live mutation is currently blocked at authorization, not engineering.

### Goal
Prove one explicitly authorized, harmless test-company update with exact identity resolution, one mutation, and fresh read-back reconciliation.

### Human actions

- [ ] **B1 — Reauthorize HubSpot.** Reconnect/reauthorize the HubSpot integration so `COMPANY.write` becomes available, or use a private-app/OAuth token scoped only for the required company read/write operations.
- [ ] **B2 — Choose a disposable company record.** Use a dedicated test company, never a live prospect/customer record for portfolio proof.
- [ ] **B3 — Record identity.** Capture its exact HubSpot company object ID and unique domain.
- [ ] **B4 — Choose one harmless reversible field.** Prefer `name` on the dedicated test record. Do not use inferred enrichment or overwrite operator-authored narrative.
- [ ] **B5 — Store credential locally.** If using the repo runner, set `HUBSPOT_ACCESS_TOKEN` outside GitHub. Never commit it.
- [ ] **B6 — Run dry preview first.** Execute `scripts/hubspot_bounded_write.py` without `--approve-write` and with `--expected-object-id <ID>`.
- [ ] **B7 — Verify preview identity.** Required:
  - `executed = false`
  - `hubspot_object_id` equals B3
  - `changes` contains only the exact field/value intended in B4
- [ ] **B8 — Explicitly approve exact change.** Approval is for that object ID + that field + that current value + that proposed value only.
- [ ] **B9 — Execute once.** Repeat the command with `--approve-write`.
- [ ] **B10 — Verify reconciliation receipt.** Required:
  - `status = verified`
  - `executed = true`
  - `reconciliation_diff = []`
  - returned/read-back properties match intended projection
- [ ] **B11 — Verify in HubSpot UI.** Open the exact test company and visually confirm the intended value.
- [ ] **B12 — Preserve sanitized proof.** Save `proof/hubspot-write-live.json` plus a screenshot showing only the test record and relevant field. Never expose token or unrelated CRM records.
- [ ] **B13 — Revert if desired through the same bounded runner.** Preserve the revert receipt separately.
- [ ] **B14 — Promote claim only now.** Safe claim after B1–B13:
  **Implemented and executed a controlled Clay-to-HubSpot company update with domain deduplication, explicit human authorization, and fresh read-back reconciliation.**

### Stop conditions
Stop immediately if:
- domain lookup returns multiple companies;
- observed object ID differs from the expected test object ID;
- preview contains any field not explicitly approved;
- write permission remains unavailable;
- read-back produces a reconciliation diff.

---

## C. What happens only after A + B

Do not build another integration first. Once A and B have real receipts:

- [ ] **C1 — Promote the two receipts into `/gtm` and the employer proof surface.**
- [ ] **C2 — Move to controlled outbound execution:** approval → provider message ID → delivery receipt → response receipt.
- [ ] **C3 — Execute the existing 9–12-touch three-arm market experiment.**
- [ ] **C4 — Record only observed states:** sent, delivered, reply, correction, qualified, pilot_started, pilot_used, second_use, purchase.
- [ ] **C5 — Update portfolio/CV only from those receipts.** No meeting, pipeline, adoption, or revenue language without corresponding external evidence.

## Current state summary

| Proof | Engineering | CI | External execution | HITL blocker |
| --- | --- | --- | --- | --- |
| Clay → SignalOps ingress | complete | green on integration branch prior to this checklist commit | pending | deployment + one Clay row |
| Duplicate suppression / evidence classes | complete | tested | pending live duplicate | same as above |
| `/gtm` employer dashboard | complete | tested | pending live data | deployment |
| HubSpot exact lookup / projection / PATCH→GET reconciliation | complete | tested | read path previously live-inspected; write pending | HubSpot reauthorization + one explicit test write |
| Autonomous send | intentionally absent | n/a | disabled | not a blocker |
| Buyer adoption/revenue | n/a | n/a | not demonstrated | real market response/use/payment |
