# Release Checklist — SignalOps Workbench

## Repository

- [x] Purpose and domain are explicit.
- [x] Signal-bearing code was hardened.
- [x] Offline verification commands are documented.
- [x] License is present.
- [x] AI–human provenance is explicit.
- [x] Portfolio evidence and residual risk are explicit.
- [ ] Human owner has reviewed every changed signal-bearing file.
- [ ] Clean checkout has been verified on a second machine.

## Correctness and reliability

- [x] Deterministic offline tests or structural checks pass.
- [x] Known unsafe authority or state boundaries were corrected where discovered.
- [ ] Live external dependencies have been tested with production-like credentials.
- [ ] Load, concurrency, or failure-injection evidence has been captured.

## Deployability

- [x] Deployment path or container configuration is present where applicable.
- [ ] Production or production-like deployment has been executed by the human owner.
- [ ] Readiness, rollback, telemetry, and data-integrity verification have been captured.

## Distribution and presentation

- [x] Functional utility can be stated in one sentence.
- [x] Evidence gaps are disclosed rather than hidden.
- [ ] Architecture blueprint has been rendered and checked against runtime.
- [ ] Five-to-ten-minute demo has been recorded.
- [ ] Cold-user or cold-reviewer run has been completed.

## Project-specific blockers

- [ ] No production concurrency or large-dataset benchmark has been executed.
- [ ] External CRM integration remains an export boundary, not a live connector.
