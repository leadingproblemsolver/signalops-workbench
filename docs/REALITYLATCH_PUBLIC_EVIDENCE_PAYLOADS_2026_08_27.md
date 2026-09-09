# RealityLatch public-evidence value payloads — 2026-08-27

Purpose: create useful artifacts **before** asking operators for private workflow details. These are market-return payloads, not claims about how any target company actually operates.

## Operating rule

Every payload separates four classes:

- **OBSERVED PUBLIC FACT** — explicitly supported by public company/news material.
- **INFERENCE** — a plausible operational consequence, not asserted as true internally.
- **UNKNOWN** — information only an operator could verify.
- **TESTABLE FAILURE MODE** — a bounded question RealityLatch can reconstruct from a sanitized exception.

The first external touch should deliver the useful artifact. A real case is requested only after value has been given, except in the explicit micro-pilot arm where the requested input is deliberately tiny.

---

## Payload A — Starlinks: robotics + fulfilment settlement boundary

### Observed public facts

- Starlinks and Geek+ received a 2026 Best Use of Robotics award for robotics/intelligent fulfilment infrastructure.
- Starlinks announced the Thuraya Logistics Hub in Riyadh, expanding warehousing, fulfilment and cold-chain capability.
- Starlinks announced an automotive-logistics partnership with Wallan Trading Company for multiple automotive brands in Saudi Arabia.

### Inference

More automated fulfilment plus new facility/cold-chain and automotive flows can increase the number of system and human handoffs involved in exception closure. This does **not** establish that Starlinks has a settlement problem.

### Unknowns

1. Which system is authoritative when a physical recovery succeeds but the digital state remains unresolved?
2. Whether robotics/WMS/TMS exceptions share one owner model or separate owner models.
3. What evidence is required before an exception is considered truly settled.

### Testable failure modes

- physical recovery complete, digital exception remains open;
- digital status closed while evidence/ownership is unresolved;
- cold-chain or automotive exception crosses systems and loses one authoritative owner;
- retry/reprocessing creates duplicate downstream action after the physical action already occurred.

### Tiny micro-pilot

Input: five sanitized event lines from one exception.

Return:

`EVENT -> OBSERVED EVIDENCE -> CURRENT OWNER -> ACTION ALREADY TAKEN? -> CONTRADICTION -> SETTLED / NOT SETTLED`

Operator only marks: **useful / partial / wrong**.

---

## Payload B — Momentum Logistics: cross-border/LTL exception surface

### Observed public facts

- Momentum Logistics publicly announced a fleet expansion including 17 MAN TGX trucks.
- Public material describes last-mile/first-mile and cross-border capability, mixed trailer types, advanced tracking, and regional LTL services.
- Momentum operates transport/warehousing across multiple GCC/Iraq contexts and has announced geographic expansion.

### Inference

A larger owned fleet, cross-border LTL, tracking systems and mixed equipment can increase exception touchpoints across dispatch, telematics, customs, warehousing and handoff states. This is a hypothesis, not a statement about Momentum's internal failure rate.

### Unknowns

1. Where ownership transfers when transport evidence conflicts with customs/warehouse state.
2. Whether telematics events can close an operational case or only inform one.
3. How duplicate actions are prevented after delayed callbacks or manual recovery.

### Testable failure modes

- truck/driver action succeeds but TMS state is stale;
- delayed tracking callback overwrites a newer manually corrected state;
- cross-border document correction occurs without closing the operational exception;
- one shipment segment is settled while the end-to-end exception remains unresolved.

### Tiny micro-pilot

Input: one sanitized shipment exception with timestamps only.

Return: evidence split, stale-event detection, owner boundary, already-happened action check, and minimum evidence required for settlement.

---

## Payload C — Fleet Line Shipping: JAFZA warehouse + project/Ro-Ro handoff map

### Observed public facts

- Fleet Line Shipping announced a new warehouse facility in Jebel Ali Free Zone in 2026.
- Its public service portfolio includes project cargo, heavy lift, break bulk, Ro-Ro, industrial packing/lashing, air freight and 3PL warehousing.
- The company has also published recent Ro-Ro operational updates.

### Inference

Warehouse expansion plus project/Ro-Ro flows can create handoffs between facility operations, cargo preparation, carrier movement and customer-facing closure. This is a generic operational inference, not evidence of an internal defect.

### Unknowns

1. Which record proves that cargo is operationally complete rather than merely handed off.
2. How warehouse, lashing/packing and transport evidence are reconciled when they disagree.
3. Whether closure can occur before all external confirmations arrive.

### Testable failure modes

- cargo leaves one control point while the previous system retains ownership;
- evidence arrives late and reopens/overwrites a settled case;
- a project-cargo action is repeated because the first completion signal was ambiguous;
- warehouse completion is mistaken for end-to-end shipment settlement.

### Tiny micro-pilot

Input: one redacted handoff chain or five event lines.

Return: handoff graph + evidence gaps + exact condition that would justify settlement.

---

## Payload D — Modern Freight Company: heavy-lift evidence/settlement boundary

### Observed public facts

- Modern Freight Company publicly reported additional Jebel Ali warehouse capacity.
- It reported multiple recent heavy-lift/project logistics movements, including 12 heavy-lift modules and a 141-ton pressure-vessel delivery partnership.
- Its public capabilities include contract logistics, customs clearance, project management and freight forwarding.

### Inference

Heavy-lift/project movements involve high-consequence handoffs where action completion, documentary evidence and responsibility can diverge. This does not imply any MFC incident or weakness.

### Unknowns

1. Which event is considered authoritative for completion across partner/carrier/customer boundaries.
2. Whether documentary completion and physical completion can settle independently.
3. How the system prevents re-execution when acknowledgement is delayed.

### Testable failure modes

- physical movement complete but partner acknowledgement delayed;
- documentary state says complete while one operational obligation remains;
- partner callback arrives out of order and mutates a newer state;
- retry is triggered because acknowledgement is missing even though the high-cost action already happened.

### Tiny micro-pilot

Input: one sanitized project-cargo exception timeline.

Return: already-happened action detection, evidence split, unresolved contradiction, current owner, and minimum settlement proof.

---

# Three-arm externalization contract

## Arm A — Rapport first

Eligibility: only a verifiable, substantive human signal. No generic praise or title-based pseudo-rapport.

Touch 1: respond to the real work/viewpoint with **no ask**.

Touch 2: contribute a relevant payload above or equivalent.

Receipt sought: evidence-bearing reply, correction, or voluntary continuation.

## Arm B — Useful artifact first

Eligibility: enough public company evidence to produce one of the payloads above without pretending to know private operations.

Touch 1: send the finished artifact and explicitly mark observed fact / inference / unknown.

Lowest-friction ask: **"Which part is wrong, irrelevant, or missing?"**

Receipt sought: correction, artifact use, real case volunteered, or second use.

## Arm C — Micro-pilot

Eligibility: a bounded input and a bounded return can be defined in advance.

Touch 1: show the finished example and request only the smallest input (e.g. five sanitized event lines).

Return: deterministic reconstruction with evidence boundaries.

Receipt sought: `pilot_used`, then `second_use`; a reply or page view is not adoption.

# Stop conditions

- No repeated ask without new value.
- No invented personal connection.
- No private-workflow claim derived from public evidence.
- No autonomous send.
- No adoption/revenue claim without a receipt.
- After the first balanced cohort, encode the winning interaction pattern only if evidence-bearing outcomes justify it.
