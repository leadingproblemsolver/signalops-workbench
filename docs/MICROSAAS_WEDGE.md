# SignalOps MicroSaaS Wedge

## Product thesis

SignalOps should not compete with Clay on enrichment, sequencing, or workflow breadth.

Clay gives operators powerful primitives for finding, enriching, researching, and acting on accounts.

SignalOps should own the decision layer between market evidence and GTM action:

`observe -> preserve evidence -> separate fact from inference -> resolve confidence -> rank intervention -> enforce permission rules -> hand off -> record outcome -> update future prioritization`

The product promise is not "AI GTM intelligence." It is:

> Turn noisy market evidence into a small queue of justified GTM actions with an inspectable reason for each action.

## Economic invariant

A signal is only valuable if it reduces the cost or increases the yield of a real GTM decision.

Primary operating metric:

`minutes of human investigation / economically useful action`

North-star economic metric once revenue attribution exists:

`pipeline dollars generated / operator hour`

Supporting metrics:

- raw signals observed
- evidence-qualified signals
- actions recommended
- actions approved by a human
- actions executed
- responses / meetings / conversions
- false-positive rate
- median time from signal observation to justified action
- operator minutes spent per qualified action

Do not claim pipeline or revenue impact until attribution exists.

## First ICP: post-build, pre-repeatable-GTM B2B micro-SaaS founders

### Exact target state

Solo or very small-team founders who can now ship software rapidly with AI coding tools, have already deployed a working B2B product, but do not yet have a repeatable GTM loop.

### Qualification criteria

Prioritize founders matching at least five of these:

1. A live B2B SaaS or developer-tool product exists.
2. Product was launched within roughly the last 90 days or is still under active rapid iteration.
3. Founder is technical, semi-technical, or visibly using AI coding / no-code / low-code tools heavily.
4. They have fewer than ~20 paying customers or have not demonstrated repeatable acquisition.
5. They are still changing product features more often than running structured market experiments.
6. They manually browse Reddit, X, GitHub, Hacker News, LinkedIn, communities, or directories for demand signals.
7. They do not have a dedicated growth or sales operator.
8. They can name several possible customer segments but cannot rank them from evidence.
9. Their GTM stack is fragmented across notes, browser tabs, spreadsheets, CRMs, and ad hoc prompts.
10. They can execute outreach but struggle to decide who deserves attention now and why.

### Exclude

- idea-stage builders with no deployed product
- consumer apps without a clear monetizable buyer
- agencies whose core problem is lead volume rather than product-market learning
- funded teams with mature RevOps / SDR / growth operations
- founders looking only for automated cold-email generation
- products with no evidence of a painful problem or buyer

## Core job-to-be-done

> "I shipped the product. I can keep building indefinitely. Tell me which market evidence deserves action now, why, and what the smallest justified next move is."

## Trigger moments

High-signal triggers include:

- launch completed but few or no qualified users appear
- founder asks "where do I find my first customers?"
- founder is collecting customer complaints manually across communities
- founder has several ICP hypotheses and no ranking mechanism
- founder keeps adding features after weak launch traction
- founder receives scattered inbound interest but cannot distinguish noise from buying intent
- founder starts outbound but researches every account from scratch
- founder has accumulated many saved posts, issue threads, comments, or competitor reviews without a decision system

## Current workflow

Typical current state:

`browse surfaces -> save links -> ask LLM what matters -> manually inspect people/accounts -> guess priority -> write outreach -> maybe log to CRM -> rarely close the learning loop`

Failure modes:

- fact and inference collapse together
- the loudest signal wins rather than the highest-value signal
- no durable evidence trail
- repeated research on the same account/problem
- premature private outreach
- weak permission boundaries
- no explicit confidence state
- no record of why an action was recommended
- no feedback from downstream outcome into future ranking

## SignalOps v0 workflow

1. **Observe** a public or user-supplied signal.
2. **Preserve the exact evidence** and source URL.
3. **Write the inference separately** from the observed fact.
4. **Score relevance, urgency, and conversation potential** under a transparent policy.
5. **Resolve the permitted next action**: ignore, save, public reply, DM, call, or CRM handoff.
6. **Require human approval** before external execution.
7. **Record the outcome**.
8. **Measure investigation cost and downstream yield**.

## v0 product surface

The smallest commercial product should contain only:

### Inbox

A table of observed signals with:

- exact observed fact
- inference / hypothesis
- source
- target person/account
- confidence
- relevance
- urgency
- conversation potential
- recommended action
- reason / decision trace
- status

### Decision queue

Show only the top justified actions, not every signal.

Each card should answer:

- what happened?
- what do we know versus infer?
- why does it matter for this ICP/account?
- why now?
- what action is permitted?
- what would falsify this recommendation?

### Outcome capture

One-click states:

`ignored | saved | replied | responded | dm_sent | call_booked | converted | rejected`

### Metrics

Do not optimize vanity signal volume.

Expose:

- signals processed
- signals promoted to action
- action acceptance rate
- response / meeting / conversion outcome counts
- time-to-action
- investigation minutes per useful action

## Integration boundary

SignalOps should sit above tools such as Clay, Apollo, HubSpot, Attio, Close, Instantly, Smartlead, spreadsheets, browser research, and public communities.

It should not initially rebuild their primitives.

Initial integration contract:

`SignalOps decides -> downstream system executes / stores -> outcome returns to SignalOps`

Useful first exports:

- CSV / JSON
- webhook
- HubSpot / Attio / Close-compatible action payload
- Clay table enrichment trigger after SignalOps has already justified the account/action

## Why this is defensible

The moat is not another model call. It is the accumulated decision history:

- preserved evidence
- explicit fact/inference separation
- account/ICP-specific policy
- human permission state
- action trace
- outcome data
- learned false-positive / true-positive patterns

Over time this becomes a proprietary map of which evidence patterns actually precede useful GTM outcomes for a given operator and market.

## Pricing hypothesis

Do not start with seat-based enterprise pricing.

Test one narrow founder plan:

- free: limited manual signals + decision queue
- paid: persistent history, higher signal volume, exports/integrations, custom policies, outcome analytics

Price only after measuring willingness to pay through direct founder conversations and live usage. The product must first prove that it saves investigation time or improves action yield.

## Acquisition thesis

Acquire users where post-build founders reveal the failure in public, not where generic "marketers" congregate.

Priority discovery surfaces to validate:

- Reddit communities around SaaS, micro-SaaS, vibe coding, no-code, indie building, and specific verticals
- Indie Hackers
- Hacker News / Show HN launch threads
- Product Hunt launches and launch comments
- X founder/build-in-public posts
- GitHub discussions/issues for developer-tool founders
- founder Slack/Discord communities where self-promotion is permitted
- directories of recently launched products

The channel is chosen from observed target density and trigger visibility, not popularity.

## Market-first acquisition loop

`observe public launch/failure signal -> qualify founder -> preserve evidence -> rank intervention -> send one relevant low-friction action -> record response -> update ICP/channel confidence`

The product should dogfood itself to acquire its first users.

## First external test

Manually collect 50 public signals from recently launched B2B micro-SaaS founders.

For each signal, capture:

- founder/product
- source URL
- exact observed fact
- inferred GTM failure
- confidence
- estimated urgency
- current workaround
- recommended next action
- whether the founder responded to a relevant intervention

Success gate:

At least 10/50 should be genuinely decision-worthy after strict filtering, and at least 3 founders should agree to use the decision queue on their own live GTM evidence.

Kill / narrow condition:

If founders mainly need basic positioning, product validation, or done-for-you distribution rather than evidence prioritization, narrow or reposition SignalOps before adding automation.

## Evidence state

Already demonstrated by the repository:

- deterministic ranking
- policy gates
- SQLite state
- immutable event history
- repeated-surface upserts
- ranked actions
- handoffs / CRM export boundary
- real public-corpus run

Not yet demonstrated:

- paying user demand
- decision-quality lift
- investigation-time savings
- meeting / pipeline / revenue lift
- production multi-user tenancy
- authentication / billing
- live third-party integrations

Those missing states define the next build and market tests.