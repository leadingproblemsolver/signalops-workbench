# SignalOps microSaaS wedge

## Positioning

SignalOps is **the decision layer between market evidence and GTM action**.

It does not replace enrichment/research systems such as Clay. Those systems provide powerful primitives for finding, enriching, researching, and executing workflows. SignalOps starts where raw evidence becomes an operational decision:

`observe → preserve evidence → separate evidence from interpretation → score → enforce permission → rank action → human review → outcome receipt`

## Smallest buyer loop

1. Configure a channel policy.
2. Add one observed market signal with exact source language.
3. SignalOps deterministically ranks the next permission-safe action and exposes its reason/trace.
4. A human reviews and executes (or rejects) the action.
5. Record the actual investigation time, outcome, and any attributable pipeline value.
6. Inspect economics across the queue.

## Primary economic metrics

- `minutes_per_useful_action` — observed operator investigation minutes / outcomes that reached response, booked call, or conversion.
- `pipeline_per_operator_hour` — operator-attributed pipeline value / observed investigation hours.
- `estimated_minutes_saved` — operator-estimated manual baseline minus observed SignalOps investigation time.

The API labels estimated baseline/time-saved metrics separately from observed metrics. Pipeline value is recorded by the operator and should not be presented as independently verified revenue.

## Run locally

```bash
python -m pip install -e .
signalops-web
```

Open `http://localhost:8000`.

The app persists to `.signalops/signalops.db` by default. Set `SIGNALOPS_DB` to override it.

## Container

```bash
docker build -f Dockerfile.web -t signalops-web .
docker run --rm -p 8000:8000 -v signalops-data:/data signalops-web
```

## API surface

- `POST /api/policies`
- `POST /api/signals`
- `GET /api/actions`
- `POST /api/actions/{external_id}/review`
- `GET /api/metrics`
- `GET /health`

## Deliberate exclusions for this cut

No authentication, billing, automated scraping, automatic outreach, private-data inference, generative messaging, or CRM write-back is included yet. Those are product gates, not missing decoration. The immediate test is whether a real GTM operator will repeatedly feed signals into the queue and whether the resulting ranked actions reduce investigation time or increase economically useful action density.

## Next evidence event

Use the app on a bounded real account/signal set and produce a receipt containing:

- signals ingested;
- actions qualified;
- actions reviewed;
- useful outcomes;
- observed investigation minutes;
- operator-estimated manual baseline;
- attributable pipeline value, if any;
- false positives / rejected recommendations.

The wedge survives only if it creates a measurable improvement in **human investigation per economically useful action** or produces higher-quality/faster action selection than the operator's existing workflow.
