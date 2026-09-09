# RealityLatch market-return receipt semantics

Use existing SignalOps externalization/event storage. Do not create another CRM or experiment database.

## Minimum receipt fields

- experiment id
- strategy (`rapport_first`, `useful_artifact_first`, `micro_pilot`)
- company-safe route key (no raw email in public repo)
- artifact id/version
- surface/channel
- event timestamp
- outcome
- value-before-ask flag
- operator minutes requested before first value
- evidence reference when the outcome is evidence-bearing

## Outcome ladder

`no_response -> human_reply -> evidence_reply -> correction_or_referral -> pilot_started -> pilot_used -> second_use -> purchase`

Only evidence-bearing transitions should change the proof floor.

## Truth rules

- A human reply is engagement, not adoption.
- A booked call is not adoption.
- A pilot request is intent, not use.
- `pilot_used` requires evidence that the returned artifact/output was actually consumed in the target workflow or evaluated by the operator.
- `second_use` requires a distinct later use.
- `purchase` requires a payment receipt/reference.
- Every stronger outcome should have a receipt URL/ref or concise provenance note when possible.

## Experiment comparison

Compare arms on:

1. evidence-bearing engagements per qualified lead;
2. operator minutes requested before first value;
3. pilots used;
4. second uses;
5. purchases.

Do not procedurize a winner from opens/clicks/replies alone.
