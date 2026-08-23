# Devpost Submission — SignalOps × SerpApi

## Project name
SignalOps × SerpApi — External Opportunity Decision Agent

## One-line pitch
Turn live web evidence into a provenance-preserving, AI-assisted, policy-gated queue of justified external actions.

## Problem
Teams drown in external signals: hiring posts, product launches, technical issues, customer complaints, and market changes. The hard part is not finding more information. It is deciding which evidence deserves action without quietly turning model guesses into facts.

## What it does
SignalOps × SerpApi starts with live structured search data from SerpApi, preserves the source URL, search ID and source-provided language, then keeps that **observed evidence** separate from **AI inference**.

A constrained AI assessor may propose a falsifiable interpretation plus bounded relevance, urgency and conversation scores. It cannot authorize outreach. The pre-existing deterministic SignalOps policy resolves the next action and preserves durable state. Outcome receipts append to immutable event history so later results cannot rewrite what the system originally observed.

The resulting path is:

```text
live SerpApi result
→ provenance-bearing observed evidence
→ constrained AI interpretation
→ deterministic policy decision
→ durable action identity
→ externally recorded outcome
→ immutable outcome receipt
```

## Why SerpApi is essential
Without SerpApi, this hackathon application has no live external evidence-acquisition layer. SerpApi supplies structured real-time search results, source URLs, snippets, positions, freshness fields when available, and search IDs that become provenance anchors for the downstream decision flow.

The application deliberately does more than summarize search. It tests whether the same live evidence preserves a stable external identity across repeated processing, then records outcomes separately from the original evidence.

## Sponsor judging criteria → proof map

### Originality
Most AI search applications stop at retrieval, summarization or recommendation. SignalOps treats live search as evidence entering a controlled decision system: observed source language, AI inference, deterministic authorization and later outcome are separate states with separate receipts.

### Technical execution
- real SerpApi adapter with bounded normalization and explicit failure handling;
- constrained OpenAI structured assessment with score bounds and output-count/index validation;
- deterministic SignalOps policy remains sole action authority;
- SQLite durable state and stable external identity on repeated evidence;
- immutable outcome-event append path;
- Python 3.11/3.12/3.13 CI;
- Docker/FastAPI public deployment surface;
- credentialed live-smoke and Cloud Run deployment receipt workflows.

### SerpApi integration
The judge-facing path uses live SerpApi Google Search results as the factual acquisition layer and retains SerpApi search IDs, source URLs, positions, dates when available, titles and observed snippets through downstream decisions.

### Usability
The public FastAPI surface includes a small judge-facing workflow rather than a generic dashboard: enter a live query and goal, inspect source evidence versus AI inference, see the deterministic policy action/reason, open the source, then record an outcome receipt.

### Potential impact
The architecture targets a common operational failure in GTM, recruiting, customer intelligence and technical growth: acting on noisy external signals whose factual basis gets lost after an LLM interprets them. The system preserves enough provenance to inspect why an action was proposed and what happened afterward.

## Built with
- SerpApi Google Search API
- OpenAI Responses API (`gpt-5.6-luna`)
- Python 3.11–3.13
- FastAPI
- SQLite
- deterministic SignalOps policy engine
- Docker / Cloud Run
- GitHub Actions

## Pre-existing work disclosure
The hackathon-specific application layer was built for DevNetwork 2026: SerpApi acquisition, constrained AI assessment, judge-facing discovery UI, immutable outcome receipts, live acceptance tooling, Cloud Run receipt workflow, and submission material.

It explicitly reuses the pre-existing SignalOps deterministic policy/state core. This submission does not claim the original SignalOps workbench was created during the hackathon.

## Try it out
PUBLIC_DEMO_URL_TODO

Expected public endpoints:

```text
GET  /health
GET  /
POST /api/discover
POST /api/outcomes/{external_id}
```

## Source
https://github.com/leadingproblemsolver/signalops-workbench/tree/hackathon/serpapi-opportunity-agent

## Demo video
DEMO_VIDEO_URL_TODO

## Sponsor challenge
SerpApi — Best AI Use Case

## 2–4 minute judge demo

### 0:00–0:25 — Problem + invariant
Explain that live search is useful only if source evidence remains distinguishable from model interpretation and later action/outcome state.

### 0:25–1:20 — Live SerpApi acquisition
Run one live query. Show:
- result count;
- SerpApi search ID;
- source URL;
- observed snippet/source language.

Open one underlying source briefly.

### 1:20–2:10 — AI versus deterministic authority
For one result, show:
- **Observed evidence**;
- **AI inference**;
- bounded scores;
- deterministic action + policy reason.

State explicitly: the model does not authorize the final action.

### 2:10–2:45 — Durable identity + outcome receipt
Show the credentialed receipt proving repeated evidence preserved the same external ID. Then record an outcome from the deployed UI/API and show the returned `outcome_recorded` event receipt.

### 2:45–3:20 — Production/external proof
Show:
- public Cloud Run URL;
- `/health` with both integrations configured;
- exact branch/commit;
- green CI;
- sanitized live receipt artifact containing SerpApi search IDs and immutable outcome receipt.

### 3:20–3:35 — Close
> SerpApi gives the agent live evidence. AI interprets it. Deterministic policy decides whether it deserves action. Immutable receipts preserve what happened next.

Stop. Do not tour unrelated SignalOps features.

## Current proof state
Verified now:
- hackathon branch and public draft PR;
- current-head CI green across supported Python versions;
- SerpApi normalization/provenance contract;
- constrained AI contract;
- deterministic policy/state integration;
- stable evidence identity and immutable outcome logic under tests;
- deployment container and live receipt workflows staged.

Pending until produced externally:
- credentialed SerpApi + OpenAI receipt;
- public Cloud Run URL and deployed live discovery/outcome receipt;
- public demo video;
- Devpost submitted receipt;
- judge response / placement.

## Claim boundary
No customer demand, adoption, conversion, revenue, judge response or placement is claimed without a separate external receipt.
