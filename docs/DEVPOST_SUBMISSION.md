# Devpost Submission — SignalOps × SerpApi

## Project name
SignalOps × SerpApi — External Opportunity Decision Agent

## Elevator pitch
Turn live web evidence into a provenance-preserving, AI-assisted, policy-gated queue of justified external actions.

## Whole story
Teams drown in external signals: hiring posts, product launches, support pain, technical issues, customer complaints, and market changes. The hard part is not finding more information. It is deciding which evidence deserves action without quietly turning model guesses into facts.

SignalOps × SerpApi starts with live structured search data from SerpApi, preserves the source URL and source-provided language, and keeps that observed evidence separate from AI interpretation. A constrained AI assessor may propose a falsifiable inference and bounded relevance, urgency, and conversation scores, but it cannot authorize outreach. The existing deterministic SignalOps policy resolves the next action and preserves durable state. Outcome receipts append to immutable event history so later results cannot rewrite what the system originally observed.

The hackathon-specific application layer was built for DevNetwork 2026: SerpApi acquisition, constrained AI assessment, judge-facing discovery UI, immutable outcome receipts, live acceptance tooling, and deployment entrypoint. It explicitly reuses the pre-existing SignalOps deterministic policy/state core as a disclosed component.

## Why SerpApi matters
Without SerpApi, this hackathon application has no live external evidence acquisition layer. SerpApi supplies structured real-time search results, source URLs, snippets, positions, freshness fields when available, and search IDs that become provenance anchors for the downstream decision flow.

## Built with
- SerpApi Google Search API
- Python 3.13
- FastAPI
- SQLite
- OpenAI Responses API
- deterministic SignalOps policy engine
- Docker
- GitHub Actions

## Try it out
PUBLIC_DEMO_URL_TODO

## Source
https://github.com/leadingproblemsolver/signalops-workbench/tree/hackathon/serpapi-opportunity-agent

## Demo video
DEMO_VIDEO_URL_TODO

## Sponsor challenge
SerpApi — Best AI Use Case

## Judge demo
1. Run a live query.
2. Show SerpApi result count and inspect a source URL.
3. Show observed evidence separated from AI inference.
4. Show deterministic decision and policy reason.
5. Repeat a result to demonstrate stable identity/durable upsert behavior.
6. Record an outcome receipt and show that the original evidence is unchanged.

## Claim boundary
Repository CI and deterministic contracts are verified. Live SerpApi/OpenAI smoke, public deployment, external judge response, hackathon placement, adoption, conversion, and revenue remain unclaimed until separately evidenced.
