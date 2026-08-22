# GTM Stack Proof Run — 2026-08-22

## Objective

Demonstrate that SignalOps can sit between a real GTM enrichment substrate and a CRM handoff without rebuilding either system.

`Clay search/enrichment -> evidence-bounded normalization -> SignalOps decision surface -> CRM-ready projection -> HubSpot read/write boundary`

## Live receipts

### Clay

A connected Clay company search was executed for small software-development companies using AI/developer-tool language. Three companies were then selected for bounded enrichment:

- Halr
- Soul AI
- Notchup

Requested data points:

- Tech Stack
- Open Jobs
- Recent News

The machine-readable bounded receipt is preserved in [`../examples/clay_company_live_2026_08_22.json`](../examples/clay_company_live_2026_08_22.json).

The important failure-state behavior is preserved too: in-progress enrichments are not converted into facts. `ClayCompanySignal` carries enrichment state separately and only promotes completed values into evidence text.

### HubSpot

The connected HubSpot portal was inspected before any mutation.

Observed capability boundary on 2026-08-22:

- COMPANY read: available
- CONTACT read: available
- DEAL read: available
- COMPANY/CONTACT/DEAL write: requires connector reauthorization

A real company read returned the HubSpot company record. No CRM write was attempted because the connector did not have current write authorization.

The bounded receipt is preserved in [`../examples/hubspot_read_receipt_2026_08_22.json`](../examples/hubspot_read_receipt_2026_08_22.json).

## Engineering change

`src/signalops/clay.py` now supports company-level Clay search/enrichment results in addition to job results.

The company adapter:

1. requires source identity and source description;
2. preserves observed company/enrichment evidence separately from operator interpretation;
3. carries enrichment state explicitly;
4. excludes in-progress/error enrichment values from evidence;
5. derives a stable provenance identifier from the source company identity;
6. converts the bounded receipt into the existing SignalOps `Surface` contract.

Tests cover completed vs in-progress enrichment, observed-vs-interpreted separation, provenance and batch ordering.

## What this proves

Safe claims after CI passes:

- integrated a live Clay search/enrichment workflow with SignalOps' evidence contract;
- handled asynchronous enrichment states without presenting incomplete values as facts;
- inspected and used a live HubSpot CRM read path;
- respected the CRM authorization boundary rather than fabricating a write-path result;
- preserved machine-readable receipts for the proof run.

## What this does not prove

Do not claim:

- production Clay API integration;
- automatic prospecting or outreach;
- HubSpot write synchronization;
- replies, meetings, pipeline or revenue;
- improved conversion;
- customer adoption.

## Highest-value next transition

After CI passes, the next stronger GTM-engineering receipt is one bounded CRM write after HubSpot reauthorization:

`one Clay-enriched company -> SignalOps decision -> one explicitly approved HubSpot test/company update -> read-back verification`

That is higher-signal than adding more integrations or enriching a larger list.
