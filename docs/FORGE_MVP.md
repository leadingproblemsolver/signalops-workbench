# Forge MVP — one SignalOps ownership receipt

Forge is a deliberately narrow gate between AI-assisted implementation and a claim you can defend yourself. This MVP covers one existing SignalOps execution path only:

`SerpApi acquisition → bounded AI assessment → deterministic policy gate → durable SignalOps state`

Target: `src/signalops/hackathon.py::discover`.

## Scope

Implemented:

- `forge inspect .` — one Python AST parse of the target file plus current git SHA. Every inferred path/state/invariant item is labeled `MACHINE_CANDIDATE`.
- `forge own .` — creates a blank 14-field Markdown ownership contract bound to repository, commit, and target path. Forge refuses to overwrite it.
- `forge verify .` — requires the completed human contract and a human-authored prediction, hash-locks that prediction into the append-only ledger, then executes one fixed hostile fixture and records predicted vs observed.
- `.forge/receipts.jsonl` — append-only event source. Each verification first appends `PREDICTION_LOCKED`, then `VERIFICATION_RESULT`.
- `.forge/latest-receipt.md` — derived human-readable render of the latest result.

Not implemented: SQLite ledger, `status`, Semgrep, Hypothesis, multi-file graphing, contradiction auditor, examiner/builder separation, generalized challenge selection, dashboard, or automatic ownership answers.

## Run

Install the repository as usual:

```bash
python -m pip install -e .
```

### 1. Inspect

```bash
forge inspect .
```

The output is JSON. Treat it as a machine-generated candidate map, not as proof that you understand the path.

### 2. Own

```bash
forge own .
```

This creates `.forge/ownership.md` with exactly these blank fields:

1. Target decision
2. Entry point
3. Inputs
4. Execution path
5. Source of truth and state
6. Side effects
7. Outputs
8. Invariant
9. Boundary conditions
10. Failure semantics
11. Recovery semantics
12. Observation vs inference boundary
13. Authorization boundary
14. Dangerous failure and tradeoff

Fill every field yourself. `forge verify` will refuse an incomplete contract or a contract bound to a different `HEAD` commit.

### 3. Predict, then verify

The single hostile challenge is fixed:

> SerpApi returns HTTP 200 with a JSON object that omits `organic_results`.

Create `.forge/prediction.md` yourself before running verification. It must contain one of the two bounded outcomes below plus your own reasoning:

```text
EXPECTED_OUTCOME: <RAISES_SERPAPI_ERROR or RETURNS_EMPTY_RESULTS>
WHY:
<your reasoning before execution>
```

Then run:

```bash
forge verify .
```

Forge hashes the exact prediction bytes and appends the lock event **before** executing the hostile fixture. The fixture is hardcoded inside Forge; no user-supplied shell command is accepted. The result becomes either:

- `HOSTILE_VERIFIED` — your precommitted prediction matched the observed behavior; or
- `GAP_EXPOSED` — it did not, which identifies a concrete ownership gap.

Both states are local evidence only. Neither is external engineering judgment, production use, adoption, or proof of ownership by itself.

## Why the runner is not pytest

SignalOps currently standardizes on Python `unittest` in CI and does not depend on pytest. The MVP therefore does not add a test framework solely for Forge. The hostile verification path is a fixed Python subprocess over the real `SerpApiClient`; `tests/test_forge.py` exercises the Forge machinery under the repository's existing `unittest` suite.

## Definition of done

The implementation is complete when all of the following are true:

1. `forge inspect .` emits commit-bound machine candidates for the one SignalOps path.
2. You complete `.forge/ownership.md` manually.
3. You write `.forge/prediction.md` manually before execution.
4. `forge verify .` creates a `PREDICTION_LOCKED → VERIFICATION_RESULT` pair in `.forge/receipts.jsonl` and renders `.forge/latest-receipt.md`.
5. The receipt changes or sharpens what you can honestly claim about this exact path.

The next evidence gate after that is external inspection by an engineer; Forge does not manufacture that state.
