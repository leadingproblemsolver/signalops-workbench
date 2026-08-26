# Branch Proof Stack — 2026-08-25

A routing branch is not "tested" merely because its manifest parses. Distribution readiness is a ladder of increasingly external proof.

## Proof ladder

| Tier | Question | Required receipt | Default tooling |
| --- | --- | --- | --- |
| T0 — contract | Is the producer/controller interface structurally valid? | schema/contract CI | GitHub Actions |
| T1 — native product | Does the changed repository still satisfy its own acceptance contract? | native test/build/proof command | repository-native CI |
| T2 — security | Did the change introduce obvious code/dependency/security regressions? | scan result | Semgrep; Snyk where connected |
| T3 — quality/coverage | Did tested behavior regress or quality debt increase? | PR quality/coverage check | SonarQube Cloud; Codecov where useful |
| T4 — deploy preview | Does the exact PR build and run in a deployed environment? | immutable or PR-scoped preview URL | Netlify Deploy Preview / equivalent |
| T5 — browser/E2E | Does the real user path work against the deployed preview? | browser test run + trace/screenshots on failure | Playwright |
| T6 — environment/device | Does the public surface survive representative browsers/devices? | cross-browser/device run | BrowserStack or equivalent when material |
| T7 — external observer | Does a real target understand/use/reject/correct it? | reply, use, correction, referral, rejection, meeting, purchase, or measured non-response | SignalOps route -> Direct Delivery human action |
| T8 — operational/economic | Did it change a real operational/economic outcome? | measured outcome with provenance | SignalOps outcome memory / CRM evidence |

## Hard rules

1. T0 never upgrades T1–T8.
2. A deployment URL never proves the workflow works; T5 must exercise the deployed user path.
3. A green E2E test never proves market value; T7 requires a real external observer.
4. Lint/style debt must be visible, but unrelated repository-wide formatting rewrites should not be mixed into a narrow distribution adapter PR.
5. Security scans do not imply production security or compliance.
6. Do not create a market manifest until `wedge`, `target_roles`, `proof_refs`, and `desired_consequence` are explicit and evidence-backed.
7. No router or delivery adapter may convert evidence directly into an external send. SignalOps terminates at `human_review`; Direct Delivery preserves `send_actions_executed: false` until explicit authorization.

## Deploy-preview pattern

For a Git-connected Netlify site, opening a pull request can create a Deploy Preview. The canonical PR preview shape is:

```text
https://deploy-preview-<PR_NUMBER>--<NETLIFY_SITE_NAME>.netlify.app
```

Use the preview itself for review and as the E2E target. Do not treat a production URL as proof for an unmerged branch.

## Playwright deployment-status pattern

For hosts that publish a GitHub deployment status, trigger browser tests only after the deployment reaches `success` and pass the deployment target URL into Playwright:

```yaml
on:
  deployment_status:

jobs:
  e2e:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: '22'
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test
        env:
          PLAYWRIGHT_TEST_BASE_URL: ${{ github.event.deployment_status.target_url }}
```

A repository should only adopt this when it has real browser tests. Do not add a placebo test that only checks HTTP 200.

## Recommended external integrations

- Netlify: PR deploy previews and branch deploys for web artifacts.
- Playwright: browser/E2E tests against the exact deployed preview.
- Semgrep: code-pattern/security scanning, ideally diff-aware in PRs.
- Snyk: dependency/code/license PR checks where a workspace is connected.
- SonarQube Cloud: PR quality gates for larger maintained codebases.
- Codecov: line/branch coverage checks when the native test suite produces meaningful coverage.
- BrowserStack: cross-browser/device execution when browser variance is material.
- Checkly or equivalent synthetic monitoring: post-deploy checks for persistent public endpoints after a real hosted deployment exists.

## Current interpretation rules

- **FULL GREEN**: T0 + T1 green and any required repository-specific security/deployment gates green.
- **FUNCTIONAL GREEN / HYGIENE DEBT**: T0 + core T1 behavior green, but legacy style/lint debt is separately recorded as an issue.
- **ROUTER GREEN / PRODUCT PENDING**: routing contract passes while native product validation is still running or blocked by infrastructure.
- **TARGET UNRESOLVED**: product may be technically strong, but no explicit market observer/consequence is sufficiently grounded; do not emit a manifest.
- **EXTERNAL GATE**: internal proof is sufficient; next legitimate state transition is a real human-authorized collision, not more internal feature work.
