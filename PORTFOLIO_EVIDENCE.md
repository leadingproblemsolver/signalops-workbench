# Portfolio Evidence — SignalOps Workbench

## Functional claim

A deterministic, permission-safe evidence prioritization system that converts scattered signals into ranked actions and durable handoffs.

## Engineering domain

Backend decision systems / operational workflows

## Highest-signal surfaces

- typed domain modeling
- deterministic ranking
- transaction boundaries
- immutable events and handoffs

## Reproduction commands

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python scripts/smoke_test.py
python -m compileall -q src
```

## Validation completed in this upgrade

11 unit tests, smoke test, and Python compilation passed offline.

## Human competence evidence still required

- Complete one implementation/reconstruction sprint on a Tier-1 subsystem.
- Complete one evidence-led debugging sprint.
- Explain the end-to-end runtime flow without notes.
- Complete one bounded live modification and rerun verification.
- Record a deployment or production-like smoke test.

## Unverified or externally blocked

- No production concurrency or large-dataset benchmark has been executed.
- External CRM integration remains an export boundary, not a live connector.

## Claim discipline

Repository state and passing offline checks may be claimed. Live scale, adoption, resilience, latency, and production reliability may not be claimed until measured. See `AI_HUMAN_PROVENANCE.md`.
