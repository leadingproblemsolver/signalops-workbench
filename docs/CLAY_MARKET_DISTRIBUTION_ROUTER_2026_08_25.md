# Clay Market Distribution Router — 2026-08-25

## Objective

Turn proven Clay workflows into reusable distribution infrastructure for repository outputs without rebuilding Clay, auto-sending outreach, or inflating unproven CRM/revenue claims.

Canonical flow:

`repo artifact -> artifact manifest -> Clay company/account evidence -> Clay contact evidence -> explicit fit decision -> deterministic route receipt -> human action -> external response/outcome -> SignalOps memory`

## Successful Clay workflows recovered

### 1. Clay job / role evidence -> proof-gap compilation

Already implemented and should remain split across the existing systems:

- SignalOps: bounded Clay job normalization, stable provenance IDs, incremental-enrichment gating.
- Project Spec Compiler: role-description -> requirement -> current receipt -> proof gap -> smallest next external receipt.

Do not duplicate this logic in a new project.

### 2. Clay company enrichment -> SignalOps evidence

Already implemented in `signalops.clay.ClayCompanySignal`:

- company identity and descriptive evidence are normalized;
- enrichment states remain explicit;
- only completed values become observed evidence;
- provenance is stable;
- company search/enrichment remains a Clay responsibility.

### 3. Clay contact discovery + thought-leadership enrichment

The live HubSpot.com workflow returned three engineering / AI / solution-engineering contacts and completed `Find Thought Leadership` enrichment. This was successful external tool evidence but had no reusable contact-level SignalOps contract.

Implemented here as `signalops.distribution.ClayContactSignal`.

It preserves:

- contact identity;
- current role/company;
- company domain;
- profile URL;
- enrichment state;
- completed positive, completed negative, and completed-null outcomes without silently converting missing values into facts.

### 4. HubSpot read boundary / CRM projection

Keep this in existing `signalops.crm`.

The proven boundary is read + deterministic projection/reconciliation code. A live HubSpot write/read-back is not yet proven, so the distribution router does not auto-mutate CRM state.

## New canonical cross-repo primitive

Any repo that has something worth distributing emits one `RepoArtifactManifest` containing:

- repository;
- artifact ID and URL;
- system/category;
- commercial wedge;
- target observer roles;
- observed pain signals;
- proof references;
- desired external consequence.

SignalOps then combines that manifest with Clay company/contact evidence and requires at least one explicit fit reason before producing a `DistributionRouteReceipt`.

The receipt preserves both the search identity and Clay-observed identity. Example: the successful HubSpot flow searched `hubspot.com` while Clay returned `hubs.ly`; the router flags this discrepancy rather than overwriting either identity.

## Hard boundaries

The router does **not** claim or perform:

- automatic outreach;
- autonomous personalization;
- CRM writes;
- scheduled Clay sync;
- meeting creation;
- pipeline/revenue attribution;
- learned fit scoring;
- hiring prediction.

Its terminal state is `human_review` until an operator explicitly chooses the external action.

## Ownership map

| Capability | Canonical owner |
| --- | --- |
| public company/contact discovery | Clay |
| company/contact enrichment | Clay |
| job/company/contact normalization | SignalOps |
| provenance and asynchronous evidence state | SignalOps |
| incremental-enrichment decision | SignalOps |
| repo artifact market manifest | SignalOps distribution contract |
| role -> proof-gap compilation | Project Spec Compiler |
| CRM projection/read-back reconciliation | SignalOps CRM boundary |
| final outreach/action authorization | human operator |
| response/outcome memory | SignalOps |

## Next external receipt

Use one real repository artifact, route it to one Clay-resolved account/contact, perform one human-authorized external action, and write the response/non-response back into the SignalOps outcome ledger. That changes the evidence state. More router features do not.
