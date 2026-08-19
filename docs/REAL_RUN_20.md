# SignalOps — Real 20-Signal Run

## Evidence state

**P2 / reproducible system behavior against a real public GitHub issue corpus.**

This is not a claim of meetings, pipeline, revenue, maintainer response, or successful outreach. It is a public receipt that the policy/ranking layer was run against 20 real LangChain GitHub issue surfaces and produced deterministic next-action state.

## Corpus

- Channel: `github`
- Source family: public `langchain-ai/langchain` issues
- Records processed: **20**
- Durable events written: **20**
- Policy: reply threshold `6.0`; DM threshold `8.0`; call threshold `9.0`; DM requires a prior public response

## Result

- `public_reply`: **19**
- `save`: **1**
- `dm`: **0**
- `call`: **0**

The absence of DM/call actions is intentional. Even when a score exceeds the private-escalation threshold, policy blocks private escalation until a public response exists.

### Top five ranked surfaces

| Rank | Issue | Score | Action | Observed problem |
|---|---:|---:|---|---|
| 1 | #39039 | 9.7 | public_reply | Responses API streaming can drop failure/error events, making failure indistinguishable from success |
| 2 | #39715 | 9.5 | public_reply | reasoning-block merge can drop IDs/encrypted content |
| 3 | #38719 | 9.2 | public_reply | raw JSON-schema structured output can bypass validation/retry behavior |
| 4 | #39099 | 9.2 | public_reply | incomplete `args_schema` can silently expose no arguments |
| 5 | #38708 | 8.8 | public_reply | duplicate parallel tool calls can create repeated side effects/waste |

## What this proves

- the current SignalOps decision contract can ingest a bounded real evidence set;
- relevance / urgency / conversation scores produce ranked action state;
- permission rules can override an otherwise-high escalation score;
- repeated state is persisted into SQLite rather than existing only as a one-off model response;
- the output preserves exact source title, issue URL, pain label, score, action, and reason.

## What this does **not** prove

- that these scores predict commercial value;
- that maintainers will respond;
- that public replies outperform manual selection;
- that SignalOps has production users;
- that a CRM integration is live;
- that any meeting, pipeline, revenue, or product outcome occurred.

## Reproduce / inspect

The sanitized run output is committed at [`examples/real_run_20_results.json`](../examples/real_run_20_results.json).

Source issues remain linked individually inside that JSON.

## Next evidence event

Act on the highest-ranked permitted surfaces, preserve external responses/non-responses, and compare the selection quality against a manual/random baseline. Until that happens, this remains **real-corpus technical proof**, not outcome proof.
