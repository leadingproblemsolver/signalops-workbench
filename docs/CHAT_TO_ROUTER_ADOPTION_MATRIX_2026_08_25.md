# Chat -> Clay/SignalOps Market Router Adoption Matrix — 2026-08-25

This is the canonical coverage map for prior Taha work that can reuse the Clay-backed market distribution router. The rule is: reuse existing repos and contracts; do not copy Clay logic into every artifact.

## Routing classes

- **CONTROL** — owns market discovery, prioritization, proof compilation, execution, or outcome memory; receives real router logic.
- **PRODUCER** — emits a `market/market-artifact-manifest.json`; does not embed Clay.
- **EXTERNALIZATION** — packages proven work for an observer/channel and consumes route receipts.
- **NOT YET ROUTABLE** — no explicit market wedge / target role / proof consequence is sufficiently settled; do not infer one.

| Prior chat / workstream | Canonical repo(s) | Class | Reusable transition |
| --- | --- | --- | --- |
| Convert Clay Workflows | `signalops-workbench` | CONTROL | Clay account/contact evidence -> deterministic route receipt -> human review -> outcome |
| Map Venture Topology | `commercial-systems-proof-os`, `market-intel-pipeline` | CONTROL | venture/artifact registry -> market manifest -> live account/contact route |
| Map Job Applications | `project-spec-compiler`, `devtools-signal-engine` | CONTROL | live role -> requirement/proof gap -> artifact manifest -> hiring observer route |
| Commodity-code / coding proof floor | `commercial-systems-proof-os`, `devtools-signal-engine` | EXTERNALIZATION | verified coding receipts -> role-specific proof manifest; no invented competency |
| Logistics Reply Watch | `signalops-workbench`, `direct-delivery-ops` | CONTROL | logistics operator cohort -> response/non-response/referral receipts -> outcome memory |
| Immediate Gains Chats / P-1 proof floor | `commercial-systems-proof-os`, `direct-delivery-ops`, `stage_minusone` | CONTROL | existing proof assets -> highest-probability observer/channel route |
| Reality ontology chats | `realityloop`, `reality-constrained-context-engine`, `living-context-engine` | NOT YET ROUTABLE | only emit manifests after an explicit wedge + observer + desired external consequence exists |
| Map chats to Logistinfra | `signalops-workbench`, `commercial-systems-proof-os` | CONTROL | Logistinfra artifact registry -> logistics ICP manifests -> Clay-resolved operators |
| Recovery Agent CI proof | `realityhandoff-agent`, `operational-waste-recovery` | PRODUCER | green recovery proof -> reliability/ops buyer manifest -> route |
| Schedule Jobs Limit | no direct producer repo | NOT YET ROUTABLE | scheduling is orchestration, not a market artifact by itself |
| Map Chats For $10k Gains | `commercial-systems-proof-os`, `direct-delivery-ops` | CONTROL | sellable artifact inventory -> route -> external receipt/payment/rejection |
| Market Frontier Watch | `market-intel-pipeline`, `signalops-workbench` | CONTROL | live market signal -> ICP/account discovery -> artifact-to-observer route |
| Direct GTM Chats | `direct-delivery-ops`, `signalops-workbench` | CONTROL | route receipt -> permission-safe human action -> outcome ledger |
| Related Chats Map | `commercial-systems-proof-os`, `signalops-workbench` | CONTROL | canonical workstream registry -> manifest/router state |
| Start Codex Adapter Sprint | `operational-waste-recovery`, `signalops-workbench` | PRODUCER | runtime/adapter proof -> employer/buyer manifest -> external technical review |
| Clarify Ownership and Externalization | `commercial-systems-proof-os` | EXTERNALIZATION | ownership/receipt evidence -> observer-specific proof bundle |
| Prioritize Operational Gaps | `signalops-workbench`, `market-intel-pipeline` | CONTROL | observed gap -> smallest proof-producing artifact -> route |
| Map Technical Proof Contracts | `commercial-systems-proof-os`, `devtools-signal-engine` | CONTROL | capability contract -> proof refs -> role/company route |
| Accelerator GTM Strategy | `market-intel-pipeline`, `direct-delivery-ops` | CONTROL | target cohort -> enriched account/contact -> route receipt |
| Finalize Role Packs | `project-spec-compiler`, `devtools-signal-engine` | EXTERNALIZATION | role proof target -> exact artifact refs -> human application/outreach |
| HubSpot reauthorization / closure | `signalops-workbench` | CONTROL | Clay evidence -> bounded CRM projection -> explicit write -> read-back reconciliation |
| Market Assimilation Scan | `market-intel-pipeline` | CONTROL | market surface -> workflow/pain extraction -> manifest/routing candidates |
| Resume Tailoring / job application chats | `project-spec-compiler` | EXTERNALIZATION | evidence map -> role proof target; no generic resume-first duplication |
| Community Embedding Chats | `chat-to-post-engine`, `direct-delivery-ops` | CONTROL | route receipt -> channel-specific public contribution -> response receipt |
| X signal-scoring / post-comment routing | `chat-to-post-engine`, `signalops-workbench` | CONTROL | public signal -> score/permission gate -> public response route |
| Ulomis QDB / acquisition proof / pilot recruitment | `ulomis-continuity-companion` | PRODUCER | validated Ulomis artifact -> tutor/provider cohort manifest -> route |
| LCE market-driven training ground | `living-context-engine` | PRODUCER | continuity-failure proof -> learning/ops observer manifest only after live failure is explicit |
| Driver Recruiting Constraint Diagnostic / trucking GTM | `driver-hiring-insight`, `direct-delivery-ops` | PRODUCER | $99 diagnostic proof -> fleet/recruiting operator manifest -> route |
| TraceCrumb / data acquisition / continuity | `TraceCrumb`, `tracecrumb-data-acquisition` | PRODUCER | provenance/data-acquisition receipts -> technical buyer/employer manifest |
| DriftGuard | `driftguard` | PRODUCER | drift proof -> explicit reliability observer manifest |
| RealityLatch | `realitylatch` | PRODUCER | evidence-gating proof -> explicit reliability/ops observer manifest |
| DecisionKillSwitch | `thedecisionkillwitch` | PRODUCER | bounded-action proof -> explicit AI/reliability observer manifest |
| Reality Handoff | `realityhandoff-agent` | PRODUCER | reconstructable handoff proof -> reliability/operations manifest |
| IncidentOps / incident cognition | `operational-incident-cognition`, `incident-memory-layer` | PRODUCER | incident reconstruction proof -> ops/SRE observer manifest |
| Quicklarity | `quicklarity` | PRODUCER | verified clarity/decision artifact -> explicit target-role manifest |
| Repo OS Generator | `repo_os_generator` | CONTROL | project spec with explicit `market_route` -> generated market manifest |
| Commercial proof liquidation / first-$10k control plane | `commercial-systems-proof-os` | CONTROL | proof inventory -> routeable manifest set -> external receipts |

## Branch naming rule

Use `feat/clay-signalops-<exact-adapter>-2026-08-25` for logic, and `dist/clay-signalops-<artifact>-manifest-2026-08-25` for producer-only routing contracts.

Examples:

- `feat/clay-signalops-market-manifest-generator-2026-08-25`
- `feat/clay-signalops-market-intel-export-2026-08-25`
- `feat/clay-signalops-role-proof-router-2026-08-25`
- `dist/clay-signalops-ulomis-manifest-2026-08-25`
- `dist/clay-signalops-driftguard-manifest-2026-08-25`

## Testing gate

No branch counts as adopted until its native CI executes the changed path. Producer manifests must at minimum parse as JSON and contain non-empty `repo`, `artifact_id`, `artifact_url`, `system`, `wedge`, `target_roles`, `proof_refs`, and `desired_consequence`. Controller branches require unit/contract tests for provenance, explicit-fit boundaries, deterministic identity, and no implicit external action.
