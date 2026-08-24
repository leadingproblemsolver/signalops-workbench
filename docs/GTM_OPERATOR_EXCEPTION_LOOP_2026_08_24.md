# SignalOps — Operator Exception GTM Loop

Date: 2026-08-24

## Evidence state

`MARKET_HYPOTHESIS_UNDER_DIRECT_OPERATOR_EVALUATION`

SignalOps is testing the assumption that consequential logistics exceptions become slower or less reliable when evidence, ownership, action, and settlement are fragmented across systems or people.

No adoption, ROI, or operator-impact claim is made yet.

## Live external test

- 14 distinct operator/decision-maker email threads opened across Qatar, UAE, and Saudi Arabia.
- 14 initial operator-research messages sent.
- 14 threaded follow-ups sent with the same comparable causal object and a bounded reciprocity offer.
- 28 outbound email events total.
- Current response state at capture time: `WAITING_EXTERNAL`; no meaningful operator reply received yet.
- Current observed bounce state: `0`.
- Gmail canonical waiting label: `SignalOps GTM / Waiting External`.

The cohort spans freight forwarding, freight networks, ports/terminals, shipping, warehousing/distribution, last-mile, and logistics/digital-transformation roles.

## Common research object

```text
EXCEPTION
  -> EVIDENCE SPLIT
  -> OWNER?
  -> ACTION
  -> TRULY RESOLVED?
```

The message explicitly invites falsification: the actual painful step may be elsewhere.

## Reciprocity contract

Operator input:
- one recent exception in 2–3 lines
- what happened
- what made it slow or uncertain
- what finally counted as resolved

SignalOps return:
- one-page reconstruction
- trigger
- evidence sources
- actors/systems
- ownership transition
- decision/action
- settlement verification

The reconstruction is sent back for correction, rejection, or internal use.

## Receipt assimilation contract

`docs/gtm_receipt_router.yaml` converts every external GTM event into exactly one evidence-state update and at most one next external transition.

Canonical event classes:

- reply with concrete exception
- reply without a concrete exception
- referral
- correction to reconstruction
- explicit second use / repeat request
- bounce
- explicit rejection of the problem framing
- no response

No external event may silently disappear into inbox history or silently promote SignalOps' evidence state.

## Required next evidence event

The loop does not advance on more internal feature work. It advances when one of these occurs:

1. `REAL_WORKFLOW_ACQUIRED` — operator supplies a concrete exception.
2. `OPERATOR_CORRECTION` — operator corrects the returned reconstruction.
3. `SECOND_USE` — operator supplies another case or asks to apply the workflow again.
4. `HYPOTHESIS_FALSIFIED` — qualified operators reject the framing or reveal a materially different bottleneck.
5. `CHANNEL_KILL` — comparable cohort produces no useful response and distribution strategy is changed before product direction.

## Externalization surfaces

- Direct operator email threads — live distribution and primary market-truth surface.
- `docs/operator-exception-probe.html` — reusable observer-facing research artifact.
- `docs/operator-exception-reconstruction-template.html` — reusable operator-correctable return artifact.
- `docs/gtm_receipt_router.yaml` — machine-readable event-to-transition router.
- This repository/PR — public provenance showing what was actually tested and what remains unproven.

## Governing invariant

> No logistics exception may silently transition from uncertain evidence to resolved state.

The market test is specifically intended to determine whether this invariant maps to real operator workflows strongly enough to deserve further product investment.
