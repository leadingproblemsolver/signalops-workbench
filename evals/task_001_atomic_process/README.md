# Task 001 — Atomic projection + event receipt

This evaluation is derived from the durability boundary in `src/signalops/core.py`: SignalOps writes the current `surfaces` projection and its immutable `events` receipt inside the same SQLite transaction.

## Invariant

A caller must never observe a new or updated surface unless the event describing that processing step committed too.

## Why this task exists

A plausible coding-agent mutation splits those writes into two successful-looking transactions. Happy-path behavior remains correct, but an event-write failure leaves the durable projection ahead of the event history. The grader attacks that boundary directly.

## Layout

- `prompt.md` — task presented to the coding agent
- `fixture/store.py` — deliberately non-atomic candidate
- `reference/store.py` — smallest correct repair
- `grader.py` — deterministic black-box grader
- `expected.json` — acceptance/calibration contract

## Calibration

Run from the repository root:

```bash
python evals/task_001_atomic_process/grader.py evals/task_001_atomic_process/fixture/store.py
```

Expected: exit 1, score 50. The two ordinary behavior checks pass; both failure-atomicity checks fail.

```bash
python evals/task_001_atomic_process/grader.py evals/task_001_atomic_process/reference/store.py
```

Expected: exit 0, score 100.

The grader therefore distinguishes a superficially functional implementation from one that preserves the durability invariant under failure.

## Human reconstruction

Execution path:

```text
Store.process
  -> open SQLite transaction
  -> upsert current surface projection
  -> append immutable processing event
  -> commit both
```

Hostile case:

```text
projection upsert succeeds
  -> event append raises
  -> transaction rolls back
  -> no new projection / no partial update survives
```

The known-bad mutation breaks the path by ending the first transaction before the event append begins.