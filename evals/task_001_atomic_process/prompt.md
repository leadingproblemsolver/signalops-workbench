# Task 001 — Restore atomic projection + event persistence

You are given a small SQLite-backed store derived from SignalOps' durable state model.

`Store.process()` has one correctness invariant:

> A surface projection and the immutable event describing that same processing decision are one logical write. Either both commit, or neither commits.

The fixture contains a mutation that violates this invariant by committing the projection before attempting the event append.

## Your task

Modify only `fixture/store.py` so that:

1. normal creates still persist one surface and one event;
2. normal updates still update the projection and append a second event;
3. if event persistence raises, a brand-new projection is not committed;
4. if event persistence raises during an update, the previous projection remains unchanged;
5. the injected failure still propagates to the caller.

Do not remove or bypass `fail_event`. Do not weaken the event write, change the public method signatures, special-case grader IDs, or alter `grader.py`.

## Success condition

From this task directory:

```bash
python grader.py fixture/store.py
```

must exit `0` with `"passed": true` and `"score": 100`.

The smallest correct repair is preferred over a refactor.