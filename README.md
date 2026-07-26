# SignalOps Workbench

**A policy-driven workbench that converts channel-native public evidence into durable decisions, handoffs, and qualified next actions.**

SignalOps preserves exact observed language separately from interpretation, scores relevance deterministically, enforces channel-specific permission boundaries, upserts repeated surfaces, and renders restartable action state.

## Proof

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/smoke_test.py
```

## Boundary

Included: manual evidence ingestion, policy gates, SQLite state, ranked actions, handoffs, CRM export. Excluded: scraping, mass outreach, automatic sending, private-data inference, and generative messaging.

## Portfolio signal

The repository demonstrates policy-engine design, provenance, idempotency, human-permission controls, durable workflow state, and deliberate anti-overarchitecture.


## Engineering evidence and provenance

- [Portfolio evidence](PORTFOLIO_EVIDENCE.md)
- [AI–human provenance](AI_HUMAN_PROVENANCE.md)
- [Release checklist](RELEASE_CHECKLIST.md)
