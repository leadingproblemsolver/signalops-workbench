"""Compile a role description into an evidence/proof agenda.

The compiler is intentionally lexical and inspectable. It does not decide whether someone is
qualified. It identifies role requirements, maps known evidence labels supplied by the operator,
and emits missing proof targets that can be closed through real external work.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Mapping, Sequence


REQUIREMENT_PATTERNS: dict[str, tuple[str, ...]] = {
    "python": ("python",),
    "javascript_typescript": ("javascript", "typescript", "node.js", "nodejs"),
    "systems_fundamentals": ("systems fundamentals", "systems thinking", "system design"),
    "agent_workflows": ("agent-based", "agentic", "multi-step workflows", "orchestration"),
    "failure_handling": ("failure handling", "failure modes", "reliability", "resilience"),
    "evaluation": ("evaluation", "evals", "evaluation pipelines", "guardrails"),
    "observability": ("observability", "monitoring", "tracing"),
    "cloud": ("aws", "gcp", "azure", "cloud environments"),
    "containers": ("containers", "docker", "kubernetes"),
    "customer_poc": ("poc", "proof-of-concept", "technical evaluations", "customer engineering"),
    "technical_communication": ("technical communication", "explain technical tradeoffs", "developer audiences"),
    "production_ownership": ("production", "operate", "real-world constraints", "responsibility for outcomes"),
    "open_source": ("open source", "upstream"),
    "provenance": ("provenance", "lineage", "source system"),
    "state_and_idempotency": ("state transitions", "idempotency", "state machines", "durable execution"),
}


@dataclass(frozen=True, slots=True)
class ProofGap:
    requirement: str
    matched_phrases: tuple[str, ...]
    evidence: tuple[str, ...]
    state: str
    next_receipt: str


def extract_requirements(description: str) -> dict[str, tuple[str, ...]]:
    lower = description.lower()
    found: dict[str, tuple[str, ...]] = {}
    for requirement, patterns in REQUIREMENT_PATTERNS.items():
        matches = tuple(pattern for pattern in patterns if pattern.lower() in lower)
        if matches:
            found[requirement] = matches
    return found


def compile_proof_gaps(
    description: str,
    evidence_by_requirement: Mapping[str, Sequence[str]],
) -> list[ProofGap]:
    gaps: list[ProofGap] = []
    for requirement, matches in extract_requirements(description).items():
        evidence = tuple(str(v).strip() for v in evidence_by_requirement.get(requirement, ()) if str(v).strip())
        if evidence:
            state = "evidenced"
            next_receipt = "Strengthen only if a higher proof rung is cheap and externally useful."
        else:
            state = "missing_proof"
            next_receipt = _default_receipt(requirement)
        gaps.append(ProofGap(requirement, matches, evidence, state, next_receipt))
    return gaps


def _default_receipt(requirement: str) -> str:
    receipts = {
        "python": "Ship or contribute a tested Python change reviewed by an external engineer.",
        "javascript_typescript": "Ship a tested TypeScript/JavaScript integration with a real consumer.",
        "systems_fundamentals": "Document invariants/tradeoffs for a real system and survive code/design review.",
        "agent_workflows": "Deploy a multi-step agent workflow with explicit state, tools, and failure handling.",
        "failure_handling": "Create a regression/fault test showing detection, containment, and recovery.",
        "evaluation": "Build an eval set tied to real failures and gate a release/decision with it.",
        "observability": "Instrument a live workflow and preserve traces/metrics for one diagnosed failure.",
        "cloud": "Deploy the actual project to a cloud environment and document operations/failure recovery.",
        "containers": "Containerize and run the real service with reproducible smoke/health checks.",
        "customer_poc": "Run a bounded POC on a real operator workflow and capture their technical evaluation.",
        "technical_communication": "Publish a concise technical write-up or deliver a live architecture walkthrough.",
        "production_ownership": "Operate a real workflow through failure and capture outcome/incident evidence.",
        "open_source": "Submit an upstream issue/PR or get maintainer review on a useful contribution.",
        "provenance": "Implement unbroken source→decision provenance and test unknown/partial-failure states.",
        "state_and_idempotency": "Demonstrate idempotent replay/state-transition tests under retries or duplication.",
    }
    return receipts.get(requirement, "Create the smallest externally reviewed artifact proving this requirement.")


def to_dicts(gaps: Sequence[ProofGap]) -> list[dict[str, object]]:
    return [asdict(gap) for gap in gaps]
