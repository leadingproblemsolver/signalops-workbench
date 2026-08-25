# Chat -> Clay/SignalOps Market Router Adoption Matrix — 2026-08-25

This is the canonical coverage map for prior Taha work that can reuse the Clay-backed market distribution router. The rule is: reuse existing repos and contracts; do not copy Clay logic into every artifact. A historical packaged ZIP is evidence/backup, not a prerequisite for applying the router to an old chat.

## Routing classes

- **CONTROL** — owns market discovery, prioritization, proof compilation, execution, or outcome memory; receives real router logic.
- **PRODUCER** — emits a `market/market-artifact-manifest.json`; does not embed Clay.
- **EXTERNALIZATION** — packages proven work for an observer/channel and consumes route receipts.
- **NOT YET ROUTABLE** — no explicit market wedge / target role / proof consequence is sufficiently settled; do not infer one.

| Prior chat / workstream | Canonical repo(s) | Class | Reusable transition |
| --- | --- | --- | --- |
| Convert Clay Workflows | `signalops-workbench` | CONTROL | Clay account/contact evidence -> deterministic route receipt -> human review -> outcome |
| Create SignalOps MicroSaaS Plan | `signalops-workbench` | CONTROL | Clay company evidence -> deterministic policy -> bounded CRM projection/read-back -> outcome |
| Map Venture Topology | `commercial-systems-proof-os`, `market-intel-pipeline` | CONTROL | venture/artifact registry -> market manifest -> live account/contact route |
| Map Job Applications | `project-spec-compiler`, `devtools-signal-engine` | CONTROL | live role -> requirement/proof gap -> proof artifact packet -> hiring observer route |
| Commodity-code / coding proof floor | `commercial-systems-proof-os`, `devtools-signal-engine` | EXTERNALIZATION | verified coding receipts -> role-specific proof packet; no invented competency |
| Logistics Reply Watch | `signalops-workbench`, `direct-delivery-ops` | CONTROL | logistics operator cohort -> response/non-response/referral receipts -> outcome memory |
| Immediate Gains Chats / P-1 proof floor | `commercial-systems-proof-os`, `direct-delivery-ops`, `stage_minusone` | CONTROL | existing proof assets -> highest-probability observer/channel route |
| Reality ontology chats | `realityloop`, `reality-constrained-context-engine`, `living-context-engine` | NOT YET ROUTABLE | only emit manifests after an explicit wedge + observer + desired external consequence exists |
| Map chats to Logistinfra | `signalops-workbench`, `commercial-systems-proof-os` | CONTROL | Logistinfra artifact registry -> logistics ICP manifests -> Clay-resolved operators |
| Recovery Agent CI proof | `realityhandoff-agent`, `operational-waste-recovery` | PRODUCER | green recovery proof -> explicit reliability/data-platform observer manifest -> route |
| Schedule Jobs Limit | no direct producer repo | NOT YET ROUTABLE | scheduling is orchestration, not a market artifact by itself |
| Map Chats For $10k Gains | `commercial-systems-proof-os`, `direct-delivery-ops` | CONTROL | sellable artifact inventory -> route -> external receipt/payment/rejection |
| Market Frontier Watch | `market-intel-pipeline`, `signalops-workbench` | CONTROL | live market signal -> reviewed company/contact search intent -> artifact-to-observer route |
| Direct GTM Chats | `direct-delivery-ops`, `signalops-workbench` | CONTROL | route receipt -> target gate -> human approval -> external action -> outcome ledger |
| Related Chats Map | `commercial-systems-proof-os`, `signalops-workbench` | CONTROL | canonical workstream registry -> manifest/router state |
| Start Codex Adapter Sprint | `operational-waste-recovery`, `signalops-workbench` | PRODUCER | runtime/adapter proof -> employer/buyer manifest -> external technical review |
| Clarify Ownership and Externalization | `commercial-systems-proof-os` | EXTERNALIZATION | ownership/receipt evidence -> observer-specific proof bundle |
| Prioritize Operational Gaps | `signalops-workbench`, `market-intel-pipeline` | CONTROL | observed gap -> smallest proof-producing artifact -> route |
| Map Technical Proof Contracts | `commercial-systems-proof-os`, `devtools-signal-engine` | CONTROL | capability contract -> proof refs -> role/company route |
| Accelerator GTM Strategy | `market-intel-pipeline`, `direct-delivery-ops` | CONTROL | target cohort -> enriched account/contact -> approval-gated route receipt |
| Finalize Role Packs | `project-spec-compiler`, `devtools-signal-engine` | EXTERNALIZATION | role proof target -> exact artifact refs -> Clay observer search -> human application/outreach |
| HubSpot reauthorization / closure | `signalops-workbench` | CONTROL | Clay evidence -> bounded CRM projection -> explicit write -> fresh read-back reconciliation |
| Market Assimilation Scan | `market-intel-pipeline` | CONTROL | market surface -> workflow/pain extraction -> reviewed search intent -> routing candidates |
| Resume Tailoring / job application chats | `project-spec-compiler` | EXTERNALIZATION | evidence map -> role proof target; no generic resume-first duplication |
| Engage AI / Data Analyst / Dex application lanes | `project-spec-compiler`, `devtools-signal-engine`, `signalops-workbench` | EXTERNALIZATION | live role -> current receipts -> exact missing proof -> observer/contact route |
| Aviator / KOS / Reinforce application packets | `project-spec-compiler`, `devtools-signal-engine`, `operational-waste-recovery` | EXTERNALIZATION | employer requirement -> strongest technical receipts -> hiring observer route |
| Community Embedding Chats | `chat-to-post-engine`, `direct-delivery-ops` | CONTROL | selected route -> channel-specific public contribution -> response receipt |
| X signal-scoring / post-comment routing | `chat-to-post-engine`, `signalops-workbench` | CONTROL | public signal -> score/permission gate -> public response route |
| Operational Research Strategy | `market-intel-pipeline`, `signalops-workbench` | CONTROL | source-linked research evidence -> reviewed search filters -> live companies/operators |
| Intelligence Operations / Persistent Intelligence Ops | `market-intel-pipeline`, `signalops-workbench` | CONTROL | recurring market evidence -> dedupe/provenance -> route-worthy state changes only |
| High-Value Inelastic Problems | `market-intel-pipeline`, `commercial-systems-proof-os` | CONTROL | repeated high-cost workflow pain -> explicit wedge -> artifact manifest -> observer route |
| ICP Pain Signal Extraction | `market-intel-pipeline` | CONTROL | observed language/workflow evidence -> explicit ICP hypothesis -> Clay company filters |
| Constraint Intelligence / MARKETGATE / SIGNAL | `market-intel-pipeline`, `signalops-workbench` | CONTROL | constraint evidence -> priority/permission decision -> market route |
| Distribution-Intelligence MVE Suite | `market-intel-pipeline`, `direct-delivery-ops` | CONTROL | distribution surface evidence -> candidate cohort -> approval-gated execution |
| `mve_04_customer_first_distribution_execution_system` | `direct-delivery-ops`, `signalops-workbench` | CONTROL | customer-first evidence -> selected target -> bounded artifact -> external receipt |
| `elite_comm_eval_finder` / community evaluator lane | `chat-to-post-engine`, `direct-delivery-ops` | CONTROL | community signal -> evaluator/observer selection -> practical public artifact -> response |
| Artifact-to-Asset Engine | `commercial-systems-proof-os`, `repo_os_generator` | CONTROL | existing technical artifact -> explicit market manifest -> distribution route |
| Business Development / CORYX dossiers | `commercial-systems-proof-os`, `direct-delivery-ops` | EXTERNALIZATION | dossier evidence -> company/contact route -> bounded recipient artifact |
| Contra / Catalant commercial lanes | `commercial-systems-proof-os`, `direct-delivery-ops` | EXTERNALIZATION | platform demand/role -> proof-matched offering -> human submission/contact receipt |
| Ulomis QDB / acquisition proof / pilot recruitment | `ulomis-continuity-companion` | PRODUCER | validated Ulomis artifact -> tutor/provider cohort manifest -> real recurring-thread receipt |
| LCE market-driven training ground | `living-context-engine` | PRODUCER | continuity-failure proof -> learning/ops observer manifest only after live failure is explicit |
| Driver Recruiting Constraint Diagnostic / trucking GTM | `driver-hiring-insight`, `direct-delivery-ops` | PRODUCER | historical $99 diagnostic/current $250 audit contract -> fleet/recruiting operator manifest -> purchase/case receipt |
| TraceCrumb / data acquisition / continuity | `TraceCrumb`, `tracecrumb-data-acquisition` | PRODUCER | provenance/data-acquisition receipts -> technical buyer/employer manifest |
| DriftGuard | `driftguard` | PRODUCER | settlement-preflight proof -> runtime/devtools maintainer manifest -> real failure-path review |
| RealityLatch | `realitylatch` | PRODUCER | evidence/permission-gating proof -> logistics/control-tower manifest -> real contradiction case |
| DecisionKillSwitch | `thedecisionkillwitch` | NOT YET ROUTABLE | mechanism exists, but do not invent buyer/observer until a live market wedge is explicit |
| Reality Handoff | `realityhandoff-agent` | PRODUCER | proof-carrying DataHub action -> data/AI-platform observer manifest -> P0-P4 live receipt |
| Operational Waste Recovery | `operational-waste-recovery` | NOT YET ROUTABLE | strong mechanism/proof; explicit commercial observer must be selected before manifest generation |
| IncidentOps / incident cognition | `operational-incident-cognition`, `incident-memory-layer` | PRODUCER | incident reconstruction proof -> ops/SRE observer manifest after current repo evidence is revalidated |
| Quicklarity | `quicklarity` | PRODUCER | verified clarity/decision artifact -> explicit target-role manifest after current proof is re-read |
| Repo OS Generator | `repo_os_generator` | CONTROL | project spec with explicit `market_route` -> generated market manifest; incomplete market state fails closed |
| Commercial proof liquidation / first-$10k control plane | `commercial-systems-proof-os` | CONTROL | proof inventory -> routeable manifest set -> external receipts |

## Current implementation branches

| Repo | Branch | State |
| --- | --- | --- |
| `signalops-workbench` | `feat/clay-market-distribution-router-2026-08-25` | route contract + contact normalization + URL-carrying receipts + adoption/test docs + reusable security workflow |
| `repo_os_generator` | `feat/clay-signalops-market-manifest-generator-2026-08-25` | explicit market-route spec -> generated manifest; CI green |
| `market-intel-pipeline` | `feat/clay-signalops-market-intel-export-2026-08-25` | reviewed evidence -> Clay company/contact search intent; CI green |
| `project-spec-compiler` | `feat/clay-signalops-role-proof-router-2026-08-25` | role proof -> Clay observer search packet; CI green after correcting test-only ordering assumption |
| `direct-delivery-ops` | `feat/clay-signalops-route-receipt-import-2026-08-25` | SignalOps route -> Direct Delivery candidate contract; target/selection/send remain unset |
| `driver-hiring-insight` | `dist/clay-signalops-fleet-recruiting-audit-manifest-2026-08-25` | T0 green; build green; lint red |
| `ulomis-continuity-companion` | `dist/clay-signalops-ulomis-learning-continuity-manifest-2026-08-25` | T0 green; build/invariants/pilot-readiness green; lint red |
| `driftguard` | `dist/clay-signalops-driftguard-settlement-preflight-manifest-2026-08-25` | T0 green; native product validation being rerun with repo-declared npm version after runner npm crash |
| `realitylatch` | `dist/clay-signalops-realitylatch-logistics-proof-manifest-2026-08-25` | T0 + kernel/proof replay green; reusable Semgrep harness corrected and rerunning |
| `realityhandoff-agent` | `dist/clay-signalops-reality-handoff-datahub-manifest-2026-08-25` | T0 green; pytest 55/55 + compile green; Ruff red with existing static-quality debt; live DataHub P0-P4 unproven |

## Branch naming rule

Use `feat/clay-signalops-<exact-adapter>-2026-08-25` for logic, and `dist/clay-signalops-<artifact>-manifest-2026-08-25` for producer-only routing contracts.

Examples:

- `feat/clay-signalops-market-manifest-generator-2026-08-25`
- `feat/clay-signalops-market-intel-export-2026-08-25`
- `feat/clay-signalops-role-proof-router-2026-08-25`
- `feat/clay-signalops-route-receipt-import-2026-08-25`
- `dist/clay-signalops-ulomis-learning-continuity-manifest-2026-08-25`
- `dist/clay-signalops-driftguard-settlement-preflight-manifest-2026-08-25`

## Testing gate

No branch counts as adopted until its native CI executes the changed path. Producer manifests must at minimum parse as JSON and contain non-empty `repo`, `artifact_id`, `artifact_url`, `system`, `wedge`, `target_roles`, `proof_refs`, and `desired_consequence`. Controller branches require unit/contract tests for provenance, explicit-fit boundaries, deterministic identity, and no implicit external action. See `docs/DISTRIBUTION_TEST_GATES_2026_08_25.md` for T0-T5 evidence states.
