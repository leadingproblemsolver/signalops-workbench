# Gemini Prompt — SignalOps ICP + GTM Surface Mapper

Use this prompt with Gemini Deep Research / a web-connected Gemini model. Its job is not to produce generic startup advice. Its job is to identify the narrowest economically credible initial ICP and the exact public surfaces where SignalOps can observe live buying/GTM failure signals.

---

You are conducting market intelligence for **SignalOps**, a decision-support microSaaS.

SignalOps is **not** another Clay, Apollo, enrichment tool, outreach sequencer, or generic AI marketing agent.

Its intended role is:

`observe market evidence -> preserve exact evidence -> separate fact from inference -> resolve confidence -> rank intervention -> enforce permission rules -> hand off -> record outcome -> improve future prioritization`

The economic hypothesis is that operators currently waste too much time manually investigating noisy market signals before finding a small number of economically useful actions.

Primary metric:

`minutes of human investigation / economically useful action`

Later north-star metric, only once attribution exists:

`pipeline dollars generated / operator hour`

## Starting ICP hypothesis

The current best hypothesis is:

> Post-build, pre-repeatable-GTM B2B micro-SaaS founders, especially solo or very small-team technical/semi-technical founders who can ship rapidly with AI coding/no-code tools but do not yet have a disciplined evidence -> ICP -> channel -> next-action loop.

Typical current state:

- live product already exists
- founder can build/iterate quickly
- very few paying customers or no repeatable acquisition
- no dedicated growth/RevOps/sales operator
- manually searches Reddit, X, GitHub, Hacker News, Product Hunt, LinkedIn, directories, Discord/Slack, reviews, and competitor surfaces
- saves links/notes/prompts but has no durable evidence model
- mixes observed fact with inference
- cannot confidently rank which person/account/problem deserves attention now
- keeps building features because market evidence is noisy
- may already use Clay/Apollo/HubSpot/Attio/Close/spreadsheets, but still lacks a decision layer

Do **not** assume this ICP is correct. Your job is to test it against live evidence and compare it to adjacent segments.

## Research objective

Determine the **single best initial ICP wedge** for SignalOps based on observable pain, economic consequence, reachable distribution, urgency, willingness to try a lightweight tool, and fit with the existing product architecture.

Also determine the **highest-information acquisition surfaces** where SignalOps can dogfood itself to find those users.

## Required adjacent ICPs to compare

At minimum, compare:

1. post-build B2B micro-SaaS founders using AI/vibe-coding heavily
2. indie developer-tool founders with weak GTM capacity
3. small technical agencies/productized-service shops that need to prioritize inbound/outbound signals
4. founder-led sales teams at 2–10 person B2B SaaS companies
5. early GTM engineers / technical growth operators drowning in fragmented signals
6. any materially better segment discovered during research

Do not reward market size by itself. Penalize segments where:

- pain is vague
- users mainly want more lead volume rather than better decisions
- the buyer already has mature RevOps
- the workflow is not externally observable
- user acquisition requires expensive paid channels
- the problem can be solved adequately by one generic LLM prompt
- the existing SignalOps policy/provenance engine creates little advantage

## Evidence rules

For every material claim, distinguish:

`OBSERVED FACT`
`SOURCE`
`DATE`
`INFERENCE`
`CONFIDENCE (0-100)`

Prefer evidence from the last 12 months, especially the last 90 days where possible.

Prioritize:

- first-person founder posts describing failed launches, no users, unclear ICP, manual research, GTM overload, weak distribution, repeated feature-building, or fragmented workflows
- concrete descriptions of tools/stacks they currently use
- direct statements of what they pay for or outsource
- posts where the trigger is visible publicly
- communities with recurring instances of the same pain
- comments/replies showing whether others share the pain
- job posts revealing a company is trying to hire around this workflow
- competitor reviews showing unresolved decision/prioritization pain

Do not treat SEO blogs, vendor listicles, or generic thought leadership as strong demand evidence.

## Platform/surface mapping task

For each candidate ICP, identify where the target publicly reveals the trigger state.

Evaluate at minimum:

- Reddit
- Hacker News / Show HN
- Indie Hackers
- Product Hunt
- X / build-in-public communities
- GitHub issues/discussions/repositories
- LinkedIn
- relevant Slack/Discord communities
- founder directories / recent launch directories
- vertical-specific communities discovered during research

For each platform, score:

`TARGET_DENSITY 0-10`
`TRIGGER_VISIBILITY 0-10`
`PUBLIC_EVIDENCE_QUALITY 0-10`
`ABILITY_TO_RESPOND_PERMISSION-SAFELY 0-10`
`BUYER_INTENT 0-10`
`NOISE 0-10 (higher = worse)`
`AUTOMATION_FEASIBILITY 0-10`
`RISK_OF_SPAM / PLATFORM VIOLATION 0-10 (higher = worse)`
`TIME_TO_FIRST_MEANINGFUL_CONVERSATION 0-10`

Then calculate a transparent weighted ranking. Explain the weights.

## What counts as a good acquisition signal

Good signals are not just demographic matches. They are **trigger events** such as:

- "launched and got 0 users"
- "I built X but have no idea how to get customers"
- "which niche should I target?"
- "how do I find my first 10 B2B users?"
- "I keep adding features but nothing converts"
- "I am manually checking Reddit/GitHub/LinkedIn for leads"
- "I have many potential segments but do not know where to focus"
- "we use Clay/Apollo but still spend hours researching what is actually worth acting on"
- "our founder-led sales process is inconsistent because evidence lives everywhere"

Search for semantically equivalent language rather than only these exact phrases.

## Competitive/substitute analysis

Map what the ICP currently uses instead of SignalOps:

- Clay
- Apollo
- Common Room
- Unify
- HubSpot
- Attio
- Close
- spreadsheets
- Notion
- saved tabs/bookmarks
- ChatGPT/Gemini/Claude
- manual virtual assistants
- founder intuition
- social listening tools
- community monitoring tools

For each substitute, answer:

1. what primitive does it already solve well?
2. where does the decision burden still remain human/manual?
3. does SignalOps add a real layer, or merely duplicate functionality?
4. what integration relationship is more credible than competition?

## Self-scaling GTM architecture

Design a **manual-first, then progressively automated** acquisition system in which SignalOps dogfoods its own engine.

The system should look conceptually like:

`public surface -> observed trigger -> evidence record -> ICP qualification -> decision score -> permission-safe intervention -> response/outcome -> updated ICP/channel confidence`

Propose automation only after showing the manual step and validation gate.

For each stage, specify:

`INPUT`
`TRANSFORMATION`
`OUTPUT`
`HUMAN DECISION`
`AUTOMATION CANDIDATE`
`FAILURE MODE`
`PERMISSION / PLATFORM CONSTRAINT`
`MEASUREMENT`

The acquisition system must never default to mass messaging. It should optimize for a small number of justified interventions.

## Required final output

Return exactly these sections:

# 1. EXECUTIVE DECISION

- winning ICP
- one-sentence reason
- confidence 0-100
- strongest observed evidence
- strongest disconfirming evidence

# 2. ICP SCORECARD

A table comparing all candidate ICPs on:

- pain frequency
- economic consequence
- trigger observability
- reachable density
- willingness to try
- likely willingness to pay
- product-architecture fit
- existing-tool saturation
- time to first external proof
- overall score

# 3. WINNING ICP — PRECISE DEFINITION

Include:

- firmographic / founder attributes
- current product stage
- stack
- behavior
- trigger
- current workflow
- failure
- workaround
- consequence
- buyer/user
- explicit exclusions

# 4. TOP 10 TRIGGER PHRASES / BEHAVIORS

Use real observed language where legally/copyright-permissible; otherwise tightly paraphrase and cite.

# 5. PLATFORM RANKING

Rank the best surfaces using the scoring model above.

For each top platform include:

- why this ICP is there
- exact trigger patterns visible there
- best discovery queries/filters
- allowed/appropriate first intervention
- what not to automate

# 6. COMPETITOR / SUBSTITUTE MAP

Show where SignalOps sits relative to Clay/Apollo/Common Room/Unify/CRM/manual research.

# 7. FIRST 50-SIGNAL DATASET PLAN

Specify exactly how to collect 50 public signals manually.

Provide schema:

`signal_id`
`date`
`platform`
`source_url`
`founder_or_company`
`product`
`observed_fact`
`inference`
`confidence`
`trigger_type`
`relevance`
`urgency`
`conversation_potential`
`current_workaround`
`recommended_action`
`permission_state`
`outcome`
`notes`

# 8. FIRST 10 INTERVENTIONS

Give ten examples of **permission-safe**, high-information interventions aimed at learning rather than selling aggressively.

# 9. SELF-SCALING GTM LOOP

Show the manual v0, semi-automated v1, and automated-if-proven v2.

# 10. PRICING / WILLINGNESS-TO-PAY TEST

Do not invent pricing confidence. Design the fastest test to determine whether users pay for:

- decision queue
- saved investigation time
- evidence history
- integrations
- outcome analytics

# 11. KILL CONDITIONS

State what evidence would make us abandon or materially narrow this ICP.

# 12. NEXT 24 HOURS

Give the smallest dependency-correct sequence that ends in external evidence, not more research.

The sequence must terminate in at least one of:

- founder conversation
- user agrees to test own live signals
- observed refusal/rejection pattern
- willingness-to-pay evidence
- falsified ICP hypothesis

## Final discipline

Do not recommend broad content marketing, SEO, paid ads, or large-scale automation unless the evidence specifically supports them.

Do not confuse activity with proof.

Optimize for:

1. external consequence
2. information gain
3. observable trigger density
4. permission-safe access
5. measurable reduction in GTM decision cost
6. compounding evidence history

The desired answer is a market decision system, not a startup advice essay.
