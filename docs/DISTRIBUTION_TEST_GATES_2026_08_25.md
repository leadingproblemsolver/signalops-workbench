# Distribution / Product Test Gates — 2026-08-25

A market-routing branch is not equivalent to a tested product. Evidence is tracked by separate gates.

## T0 — routing contract

Required for every routable producer:
- valid `market/market-artifact-manifest.json`;
- non-empty repo/artifact/system/wedge/target roles/proof refs/desired consequence;
- no inferred market field silently generated from repository prose.

## T1 — native deterministic product path

Run the repository's own strongest deterministic acceptance commands. Examples already wired in current branches:
- SignalOps: Python matrix tests + smoke + CLI;
- RealityLatch: kernel tests + preserved Case A proof replay;
- DriftGuard: `npm run validate` + production dependency audit;
- Ulomis: lint, build, invariant verification, pilot-readiness verification as independent jobs;
- Reality Handoff: pytest + compileall; Ruff retained as a separate quality signal;
- Driver Hiring Insight: lint and build as independent jobs.

A red T1 gate remains red even if the routing manifest is valid.

## T2 — static, supply-chain, and secret security

Preferred baseline:
1. GitHub push protection / secret scanning;
2. GitHub dependency review on pull requests;
3. reusable Semgrep baseline from SignalOps;
4. CodeQL where the repository/language is supported;
5. optionally Snyk or SonarQube Cloud for an independent second scanner / quality gate.

Do not add multiple scanners merely to create activity. Use the second scanner only when it adds a materially different detection surface.

## T3 — deployed preview + behavioral E2E

For web products:
- connect the repository to Vercel or Netlify so every PR receives a unique preview deployment;
- run Playwright against the deployment URL, not only localhost;
- upload the Playwright HTML report / traces as CI artifacts;
- test the user-critical path and hostile paths, not screenshot existence alone.

Examples:
- Ulomis: create/load thread -> capture -> correction -> next action -> later continuity read;
- Driver Hiring Insight: landing -> intake -> submission -> output/CTA boundary;
- SignalOps web surface: observed evidence -> decision queue -> human action boundary -> outcome record.

## T4 — credentialed external integration receipt

Only after T0-T3 are stable. Run exactly one bounded credentialed path and preserve a sanitized receipt.

Examples:
- Clay: company search -> contact search -> bounded enrichment -> task context -> route receipt;
- HubSpot: explicit approved update -> fresh read-back -> reconciliation;
- DataHub / Reality Handoff: P0 live read -> P1 approval evidence -> P2 mutation -> P3 independent verification -> P4 fresh recovery;
- deployment providers: branch commit -> preview URL -> health/browser acceptance receipt.

No credentialed integration is considered proven merely because an adapter/unit test is green.

## T5 — market consequence

Terminal evidence event:
- reply / referral / correction / rejection;
- real operator case;
- repeated use;
- paid purchase;
- externally reviewed technical receipt.

A valid route with no external action remains `ROUTER_READY`, not `USED` or `ADOPTED`.

## Minimum merge policy

- CONTROL adapters: T0/T1 green + routing invariants green; security signal reviewed.
- PRODUCER manifests: T0 green and native T1 result explicitly recorded, whether green or red.
- Web products intended for users: require T3 before claiming user-ready.
- Third-party integrations: require T4 before claiming the integration works live.
- Adoption/impact claims: require T5.

## Reusable workflow

`leadingproblemsolver/signalops-workbench/.github/workflows/reusable-semgrep-baseline.yml`

During this feature cycle, callers may pin the exact feature ref for testing. After merge, callers should pin a stable default-branch commit/ref rather than depend on a transient feature branch.
