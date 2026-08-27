# RealityLatch three-arm cohort allocation — 2026-08-27

This file records allocation logic without contact email addresses or other raw PII.

## Cohort target

Prefer 12 qualified leads, 4 per strategy, one lead per company where possible. If only 9 strong eligible leads exist, use 3 per strategy rather than lowering the evidence bar.

The historical 14-thread cold-outreach cohort remains a baseline and is not recycled into this experiment.

## Eligibility-first allocation

### Rapport first

Use only contacts with a verified public human signal that is substantive enough to respond to sincerely.

Current clearly qualified signal:

- Hala Supply Chain Services — Digital Transformation Director: recent public profile update describing ERP/WMS/CRM integrations and BI dashboard launches.

Do not fill the remaining rapport slots from contacts whose enrichment says `no strong signal`. Search for additional genuine signals instead.

### Useful artifact first

Best current company-level candidates because there is enough public operational evidence to create value before requesting operator time:

- Starlinks — robotics/intelligent fulfilment + new logistics-hub/cold-chain capability.
- Momentum Logistics — fleet/cross-border/LTL/tracking expansion.
- Fleet Line Shipping — JAFZA warehouse expansion + project/Ro-Ro operations.
- Modern Freight Company — warehouse expansion + recent heavy-lift/project logistics.

Use the corresponding public-evidence payload. Keep inference boundaries visible.

### Micro-pilot

Select operational leaders at companies where a five-line sanitized exception can plausibly exercise RealityLatch's evidence-to-settlement model. Avoid using the same person/company in another arm when possible.

The ask is fixed:

> Redact names and send whatever five event lines already exist from one ugly exception. The return is an evidence split, current owner, action-already-happened check, unresolved contradiction, and settlement condition. Your only review is useful / partial / wrong.

## Measurement

Record per touch:

- strategy;
- value delivered before ask (`true/false`);
- operator minutes requested before first value;
- human reply;
- evidence-bearing reply;
- correction/referral;
- pilot started;
- pilot used;
- second use;
- purchase;
- explicit rejection;
- receipt reference when one exists.

Do not promote `human_reply`, meeting, open, click, or page view to adoption.

## Decision rule

Do not optimize on response rate alone. Prefer the arm that produces stronger evidence-bearing transitions with less requested operator effort, then test whether that advantage survives through pilot use, second use, and purchase.
