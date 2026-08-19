# SignalOps Workbench

**A policy-driven workbench that converts channel-native public evidence into durable decisions, handoffs, and qualified next actions.**

SignalOps preserves exact observed language separately from interpretation, scores relevance deterministically, enforces channel-specific permission boundaries, upserts repeated surfaces, and renders restartable action state.

## Proof

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/smoke_test.py
```

### Real public-corpus run

A bounded 20-signal run against real public LangChain GitHub issue surfaces is now preserved as an inspectable receipt:

- **20** surfaces processed / **20** durable events;
- **19** routed to `public_reply`;
- **1** routed to `save`;
- high scores still did **not** become DM/call actions because the policy requires a prior public response before private escalation.

Inspect the evidence and claim boundary in [`docs/REAL_RUN_20.md`](docs/REAL_RUN_20.md) and the machine-readable receipt in [`examples/real_run_20_results.json`](examples/real_run_20_results.json).

This demonstrates real-corpus policy/ranking behavior. It does **not** establish maintainer response, selection accuracy, meetings, pipeline, revenue, or production adoption.

## Boundary

Included: manual evidence ingestion, policy gates, SQLite state, ranked actions, handoffs, CRM export. Excluded: scraping, mass outreach, automatic sending, private-data inference, and generative messaging.

## Portfolio signal

The repository demonstrates policy-engine design, provenance, idempotency, human-permission controls, durable workflow state, and deliberate anti-overarchitecture.

## Engineering evidence and provenance

- [Portfolio evidence](PORTFOLIO_EVIDENCE.md)
- [AI–human provenance](AI_HUMAN_PROVENANCE.md)
- [Release checklist](RELEASE_CHECKLIST.md)
