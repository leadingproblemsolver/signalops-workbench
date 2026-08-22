# Clay → SignalOps proof loop

## Purpose

Use Clay as the discovery/enrichment substrate while SignalOps owns the decision boundary:

`Clay company/contact/job evidence → preserve provenance → decide whether more enrichment is worth buying → rank action → human override → outcome → policy update`

This is intentionally **not** another enrichment engine and does not automate outreach.

## First live use: role descriptions as proof requirements

Current high-caliber role descriptions are treated as external engineering specifications rather than resume-keyword sources.

Example target: an early-career deployed-engineering role can require Python/JavaScript/systems fundamentals, production agent workflows, orchestration/failure handling, technical evaluations/POCs, evals/observability/guardrails, and cloud/container experience.

SignalOps maps those requirements to:

1. exact source evidence;
2. existing bounded receipts;
3. missing proof;
4. the smallest externally reviewed next receipt.

The goal is to close proof **top-down from real employer/customer requirements**.

## Integration boundary

Implemented in this branch:

- `signalops.clay.ClayJob`: bounded Clay job contract;
- exact source description preserved as `Surface.exact_language`;
- interpretation kept in `Surface.pain`;
- stable Clay provenance IDs;
- deterministic `incremental_enrichment_decision()` so another paid enrichment must earn itself against a decision-critical gap;
- `signalops.role_proof`: inspectable role-requirement extraction and proof-gap compilation;
- tests for provenance separation, validation, enrichment gating, and proof-gap state.

Not implemented / not claimed:

- automatic Clay account access;
- CRM/Audiences synchronization;
- automatic DMs/email;
- learned/calibrated enrichment economics;
- hiring outcome prediction;
- production adoption.

## Workspace constraint observed during implementation

The connected Clay workspace did not have Audiences enabled and had no custom subroutines/functions at the time of this implementation. Therefore this branch deliberately uses a stable operator-supplied/authorized result contract rather than coupling the core to unavailable workspace state.

## Next receipt

Run at least one live company/role result through this adapter, close one missing proof item in an externally judged project, and record whether that receipt materially changes employer/customer response.
