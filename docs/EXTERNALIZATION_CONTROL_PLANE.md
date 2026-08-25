# Externalization Control Plane

## Scope

This layer exists to convert already-built SignalOps capabilities into attributable external consequences. It does not create another product, scraper, sender, CRM, or content engine.

Dependency-correct loop:

`live signal -> qualify target/trigger -> match existing artifact -> choose surface -> deliver smallest useful intervention -> record external consequence -> update ranking`

## Two operating modes

### Commercial

Use when the desired consequence is buyer behavior, pipeline, payment, referral, or attributable economic value.

Minimal wiring:

- `SIGNALOPS_CHECKOUT_URL`: optional checkout/payment URL (for example a Whop checkout URL).
- `WHOP_API_KEY`: optional; configuration status is detectable but the secret is never returned or logged.

Do not build provider-specific billing automation until a real payment or entitlement workflow requires it.

### Impact

Use when the desired consequence is measurable improvement in user or workflow quality.

Every impact receipt must name a metric and record an observed value. A baseline may also be supplied to calculate a delta.

Examples:

- minutes to justified action
- handoff reconstruction time
- exception resolution latency
- false-positive count
- task completion time
- operator interventions required
- successful reconstruction rate

## Receipt contract

Every meaningful external state transition can preserve:

- source surface `external_id`
- outcome
- mode: `proof | commercial | impact`
- artifact and version
- distribution surface
- experiment ID
- target/user/account
- operator minutes
- attributed economic value + currency
- named impact metric, baseline, observed value, delta
- receipt URL
- payment reference
- notes

Receipts are appended to the existing immutable `events` history as `externalization_receipt` events. No second database is introduced.

## Evidence rules

Do not convert activity into traction.

A send, post, export, or DM is an execution event, not proof of usefulness. Stronger terminal states include:

- response
- booked call
- real use
- adoption
- measurable improvement
- referral
- conversion
- payment

Revenue is only reported when a value is explicitly recorded. Impact is only reported when a metric is explicitly recorded. Missing attribution remains missing.

## Current priority order

1. **Receipt integrity** — make commercial/impact consequences attributable.
2. **Artifact matcher** — route a live problem to an existing asset before creating anything new.
3. **Surface router** — select the cheapest channel capable of producing the required evidence event.
4. **Direct-delivery contract** — deliver a useful bounded intervention rather than a generic pitch.
5. **Reply -> action state machine** — map external responses into explicit next transitions.
6. **Provider adapters** — add Whop/webhook/CRM automation only after real use proves which adapter is worth maintaining.

## Kill conditions

Stop or narrow an engine when:

- it produces activity without external consequence;
- it requires more integration work than the evidence event is worth;
- manual execution has not yet produced a repeatable successful path;
- the intended user needs a different job done than the engine measures;
- outcome attribution cannot be reconstructed.

## First experiments

### Commercial experiment

Take one already-working artifact, pair it with one narrow buyer problem, expose one checkout link, and record whether the sequence produces a response, qualified use, referral, conversion, or payment.

### Impact experiment

Take one live operator/user workflow, define one before/after measure, run the smallest bounded intervention, and record whether the measure changes.

The next build decision should come from these receipts, not from internal feature completeness.
