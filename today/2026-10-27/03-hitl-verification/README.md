# HITL verification proof

Run exactly 10 cases through:
input -> AI output -> verification -> correction -> human decision -> final output

Track:
- AI errors
- errors caught
- errors missed
- false alarms
- human review time
- total processing time
- final acceptance/rework

If organic errors are insufficient, seed at least two known errors.

Primary metric: unsafe error escape rate after verification.

Exit: 10 cases, every failure logged, no unreviewed consequential action.
