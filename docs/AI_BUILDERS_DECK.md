# AI Builders Hackathon 2026 — SignalOps Deck Storyboard

Maximum: 10 slides. Target: 8 slides. One idea per slide.

## Slide 1 — SignalOps
**Headline:** Live evidence → justified action.

**Subhead:** A decision layer for teams that need to act on public external signals without letting AI inference silently become fact or authority.

**Visual:** one horizontal flow:
`Live signal → Evidence → AI interpretation → Policy decision → Outcome receipt`

**Proof line:** Working product + public source.

---

## Slide 2 — The problem
**Headline:** Search is abundant. Accountable action is scarce.

Teams repeatedly inspect hiring posts, customer complaints, product launches, technical issues, and market changes. The expensive step is deciding what deserves action while retaining the source and the reason.

**Failure modes:**
- source language gets replaced by a summary;
- model guesses become operational facts;
- high scores become unauthorized action;
- repeated evidence gets duplicated;
- later outcomes overwrite the original decision context.

**Do not use fabricated market-size numbers.**

---

## Slide 3 — Who it is for
**Headline:** Small technical teams operating close to live market signals.

Primary users:
- founders / technical operators;
- GTM engineers;
- recruiting / market-intelligence operators;
- customer and technical-growth teams.

**Job to be done:**
`Given more public signals than I can manually investigate, show me which ones deserve attention, why, and what happened afterward — without hiding the evidence boundary.`

---

## Slide 4 — Product workflow
**Headline:** One inspectable path from evidence to consequence.

1. Enter live query + decision goal.
2. Retrieve current structured evidence through SerpApi.
3. Preserve source URL + provenance + observed language.
4. AI proposes bounded interpretation and scores.
5. Deterministic SignalOps policy authorizes the next action.
6. Repeated evidence keeps durable identity.
7. Operator records outcome.
8. Outcome appends without rewriting original evidence.

**Visual:** screenshot of judge UI with labels over Observed evidence / AI inference / policy action / outcome receipt.

---

## Slide 5 — Why the AI boundary matters
**Headline:** Inference is useful. Inference is not authority.

**AI owns:**
- interpretation against operator goal;
- bounded relevance / urgency / conversation scores.

**AI does not own:**
- source truth;
- final action authorization;
- durable identity;
- outcome history.

**Key quote:**
> The model may interpret evidence, but it cannot authorize the final action or rewrite what the source originally said.

---

## Slide 6 — Technical architecture
**Headline:** AI-assisted where judgment helps; deterministic where authority matters.

```text
Operator
  ↓
SerpApi live evidence
  ↓
Observed evidence + provenance
  ├──────────────→ deterministic SignalOps policy
  ↓                                   ↑
Constrained AI assessor ───────────────┘
  ↓
Durable SQLite identity/state
  ↓
Justified action
  ↓
Append-only outcome receipt
```

**Built with:** Python, FastAPI, SerpApi, OpenAI Responses API, SQLite, Docker, Google Cloud Run proof path, GitHub Actions.

---

## Slide 7 — What is already working
**Headline:** This is a product path, not a concept deck.

Show only externally inspectable capabilities:
- working query → result UI;
- real source links;
- observed evidence separated from AI inference;
- deterministic action + reason;
- stable external IDs;
- append-only outcome receipts;
- failure handling and schema validation;
- public repository + CI.

**Receipt boundary:** do not claim public deployment VERIFIED unless the current live receipt proves it.

---

## Slide 8 — Value + roadmap
**Headline:** From signal overload to an accountable operating queue.

**Immediate value:**
- less manual triage;
- preserved provenance;
- inspectable action reasoning;
- safer AI-assisted workflows;
- durable learning from outcomes.

**Next external validations, not feature fantasies:**
1. measure operator investigation time per economically useful action;
2. test with one narrow GTM/recruiting workflow;
3. measure outcome quality and override rate;
4. integrate only the acquisition/CRM surfaces demanded by real use.

**North-star only after real attribution exists:**
`pipeline dollars generated / operator hour`

**Close:**
> Search finds the signal. SignalOps decides what the signal is allowed to become.

---

# Presentation design rules
- 8 slides preferred; never exceed 10.
- Minimum text; large screenshots and diagrams.
- Do not repeat the demo transcript.
- Use one product screenshot on Slides 4 or 7.
- Architecture only once.
- No fake TAM, adoption, savings, revenue, customer logos, testimonials, or integrations.
- Every claim should map to repo evidence, a live run, or clearly labeled future validation.
