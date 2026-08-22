# SignalOps — 20-surface revalidation receipt (2026-08-22)

## Why this exists

The original real-corpus run proved deterministic ranking and permission policy over 20 real public GitHub issue surfaces. It did **not** prove that a high score remains a good intervention target later.

Before acting on the top-ranked rows, the surfaces were re-checked manually for current state and intervention saturation.

## Revalidated surfaces

| Issue | Prior score | Current state | Intervention state | Decision |
|---|---:|---|---|---|
| langchain-ai/langchain#39039 | 9.7 | open | saturated: multiple independent root-cause/fix investigations already present | **NO ACTION** |
| langchain-ai/langchain#39715 | 9.5 | closed / completed | resolved | **NO ACTION** |
| langchain-ai/langchain#38719 | 9.2 | closed / completed | resolved | **NO ACTION** |
| langchain-ai/langchain#39099 | 9.2 | closed / completed | resolved | **NO ACTION** |
| langchain-ai/langchain#39700 | 8.7 | open | saturated/deeply narrowed: real-graph reproduction and retaining-reference trace already in thread | **NO ACTION** |
| langchain-ai/langchain#38223 | 8.5 | open | saturated: multiple fix analyses and workaround already supplied | **NO ACTION** |

## Result

**External comments sent from this revalidation: 0.**

That is intentional. Posting a redundant comment would optimize activity volume while reducing maintainer trust.

The revalidation falsifies this operational assumption:

> `high historical SignalOps score => high current intervention value`

The surviving rule is:

> `ranked constraint value` and `current intervention value` are separate states.

A surface must pass a human pre-action gate immediately before engagement:

1. **Freshness:** is the surface still open/current?
2. **Saturation:** has the useful diagnosis/fix already been supplied?
3. **Novelty:** can we add a distinct reproduction, boundary, counterexample, patch, or operator fact?
4. **Ownership:** is the issue owned/active enough that the contribution can change behavior?
5. **Trust cost:** would the comment reduce or increase maintainer work?

If any of 1–3 fails, default action is `preserve / no_action`, not public engagement.

## Evidence-state update

- Original 20-surface run: **P2 real-corpus policy execution**.
- This artifact: **dated manual revalidation / falsified intervention assumption**.
- Still unproved: ranking quality vs baseline, maintainer response lift, meetings, pipeline, revenue, production adoption.

## Next evidence event

Do not automate this new gate yet. Apply it manually to a fresh small cohort. Only when one surface survives freshness + saturation + novelty should SignalOps cause a public action; then preserve the response/non-response and compare that selection against a manual baseline.
