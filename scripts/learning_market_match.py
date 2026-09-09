#!/usr/bin/env python3
"""Smallest executable Learning -> Market Evidence matcher.

GitHub owns intake, persistence, retry and the operator-visible receipt surface.
This module owns only domain-specific learner -> current arena matching.
"""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import re
from pathlib import Path
from typing import Any


FIELD_HEADINGS = {
    "Learner status": "learner_status",
    "Age": "age",
    "Current learning": "current_learning",
    "Capabilities you can already exercise": "capabilities",
    "Access / equipment": "access",
    "Location": "location",
    "Hours available this week": "hours",
    "Evidence you want": "preferred_evidence",
}

CANONICAL = {
    "circuit": "circuits",
    "circuitry": "circuits",
    "stats": "statistics",
    "statistical": "statistics",
    "probabilistic": "probability",
    "electronics": "electronics",
    "electronic": "electronics",
    "embedded": "embedded",
    "sensing": "sensors",
    "sensor": "sensors",
    "coding": "programming",
    "code": "programming",
    "ml": "ml",
}

SYNONYMS = {
    "circuits": {"electronics", "hardware", "embedded", "iot", "sensors"},
    "electronics": {"circuits", "hardware", "embedded", "iot", "sensors"},
    "probability": {"statistics", "data", "analysis", "ml", "ai"},
    "statistics": {"probability", "data", "analysis", "ml", "ai"},
    "python": {"programming", "data", "analysis", "ml", "ai"},
    "programming": {"python", "software"},
    "sensors": {"hardware", "iot", "electronics"},
}


class InputError(ValueError):
    pass


def _clean(value: str) -> str:
    value = value.strip()
    if value in {"_No response_", "No response"}:
        return ""
    return value


def parse_issue_body(body: str) -> dict[str, str]:
    """Parse the stable headings emitted by the repository issue form."""
    found: dict[str, str] = {}
    pattern = re.compile(r"^### (?P<heading>[^\n]+)\n\n(?P<value>.*?)(?=^### |\Z)", re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(body or ""):
        key = FIELD_HEADINGS.get(match.group("heading").strip())
        if key:
            found[key] = _clean(match.group("value"))
    return found


def _parse_number(value: str, *, field: str, integer: bool = False) -> float | int | None:
    if not value:
        return None
    match = re.search(r"\d+(?:\.\d+)?", value)
    if not match:
        raise InputError(f"{field} must contain a number")
    number = float(match.group(0))
    return int(number) if integer else number


def validate_learner(fields: dict[str, str]) -> dict[str, Any]:
    learning = fields.get("current_learning", "").strip()
    capabilities = fields.get("capabilities", "").strip()
    status = fields.get("learner_status", "").strip()
    if not learning:
        raise InputError("Current learning is required")
    if not capabilities:
        raise InputError("At least one capability you can exercise is required")
    if not status:
        raise InputError("Learner status is required")

    age = _parse_number(fields.get("age", ""), field="Age", integer=True)
    hours = _parse_number(fields.get("hours", ""), field="Hours available this week")
    return {
        **fields,
        "current_learning": learning,
        "capabilities": capabilities,
        "learner_status": status,
        "is_student": "student" in status.lower(),
        "age_number": age,
        "hours_number": hours,
    }


def _normalized_words(text: str) -> set[str]:
    raw = re.findall(r"[a-z0-9+#]+", (text or "").lower())
    return {CANONICAL.get(word, word) for word in raw if len(word) > 1 or word in {"c", "r"}}


def capability_terms(learner: dict[str, Any]) -> set[str]:
    terms = _normalized_words(learner["current_learning"] + " " + learner["capabilities"])
    expanded = set(terms)
    for term in tuple(terms):
        expanded.update(SYNONYMS.get(term, set()))
    return expanded


def _normalize_phrase(text: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", (text or "").lower()))


def _has_required_access(access_text: str, requirement: str) -> bool:
    access = _normalize_phrase(access_text)
    required = _normalize_phrase(requirement)
    negatives = (
        f"no {required}",
        f"without {required}",
        f"do not have {required}",
        f"dont have {required}",
    )
    if any(negative in access for negative in negatives):
        return False
    return required in access


def _eligible(learner: dict[str, Any], opportunity: dict[str, Any], as_of: date) -> tuple[bool, str]:
    valid_from = date.fromisoformat(opportunity["valid_from"])
    valid_until = date.fromisoformat(opportunity["valid_until"])
    if as_of < valid_from:
        return False, "not open yet"
    if as_of > valid_until:
        return False, "expired"

    eligibility = opportunity.get("eligibility", {})
    if eligibility.get("student_only") and not learner["is_student"]:
        return False, "student-only arena"
    age = learner.get("age_number")
    min_age = eligibility.get("min_age")
    max_age = eligibility.get("max_age")
    if min_age is not None and age is not None and age < min_age:
        return False, f"minimum age is {min_age}"
    if max_age is not None and age is not None and age > max_age:
        return False, f"maximum age is {max_age}"
    for requirement in eligibility.get("required_access", []):
        if not _has_required_access(learner.get("access", ""), requirement):
            return False, f"requires existing access to {requirement}"
    return True, "eligible"


def _opportunity_terms(opportunity: dict[str, Any]) -> set[str]:
    text = " ".join(opportunity.get("capability_tags", []) + opportunity.get("learning_tags", []))
    terms = _normalized_words(text)
    expanded = set(terms)
    for term in tuple(terms):
        expanded.update(SYNONYMS.get(term, set()))
    return expanded


def rank_matches(learner: dict[str, Any], registry: dict[str, Any], *, as_of: date) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    learner_terms = capability_terms(learner)
    ranked: list[dict[str, Any]] = []
    rejected: list[dict[str, str]] = []

    for opportunity in registry.get("opportunities", []):
        eligible, reason = _eligible(learner, opportunity, as_of)
        if not eligible:
            rejected.append({"id": opportunity["id"], "reason": reason})
            continue

        overlap = sorted(learner_terms & _opportunity_terms(opportunity))
        if not overlap:
            rejected.append({"id": opportunity["id"], "reason": "no capability overlap"})
            continue

        days_left = (date.fromisoformat(opportunity["valid_until"]) - as_of).days
        urgency = 4 if days_left <= 7 else 2 if days_left <= 30 else 1
        preferred = learner.get("preferred_evidence", "").lower()
        evidence_bonus = 2 if preferred and any(e.lower() in preferred or preferred in e.lower() for e in opportunity.get("evidence_types", [])) else 0
        score = len(overlap) * 10 + urgency + evidence_bonus
        ranked.append({
            "score": score,
            "days_left": days_left,
            "matched_terms": overlap,
            "opportunity": opportunity,
        })

    ranked.sort(key=lambda row: (-row["score"], row["days_left"], row["opportunity"]["id"]))
    return ranked, rejected


def _receipt_id(learner: dict[str, Any], opportunity_id: str, as_of: date) -> str:
    material = json.dumps(
        {
            "learning": learner["current_learning"],
            "capabilities": learner["capabilities"],
            "access": learner.get("access", ""),
            "opportunity": opportunity_id,
            "as_of": as_of.isoformat(),
        },
        sort_keys=True,
    )
    return "lme_" + hashlib.sha256(material.encode("utf-8")).hexdigest()[:12]


def render_result(learner: dict[str, Any], ranked: list[dict[str, Any]], rejected: list[dict[str, str]], *, as_of: date, registry: dict[str, Any]) -> str:
    if not ranked:
        rejected_text = "\n".join(f"- `{row['id']}` — {row['reason']}" for row in rejected) or "- Registry contained no opportunities."
        return f"""## Learning → Market Evidence — NO ELIGIBLE CURRENT ACTION

**As of:** {as_of.isoformat()}

No current registry entry passed both the eligibility/access gates and capability-overlap gate.

{rejected_text}

### Recovery
Edit this issue with corrected capabilities/access or wait for the registry to be refreshed. Editing the issue automatically reruns the matcher; prior comments remain as the observable execution history.

**Boundary:** no generic arena is emitted when the engine cannot support a concrete current action.
"""

    best = ranked[0]
    opportunity = best["opportunity"]
    receipt_id = _receipt_id(learner, opportunity["id"], as_of)
    terms = ", ".join(best["matched_terms"][:8])
    alternatives = ""
    if len(ranked) > 1:
        alt = ranked[1]["opportunity"]
        alternatives = f"\n**Fallback if the first action is impossible:** [{alt['title']}]({alt['url']}) — {alt['action']}\n"

    return f"""## Learning → Market Evidence — ACTIONABLE

**Execution receipt:** `{receipt_id}`  
**As of:** {as_of.isoformat()}  
**Registry verified:** {registry.get('verified_on', 'unknown')}

### Capability extracted
`{terms}`

### Arena
**[{opportunity['title']}]({opportunity['url']})** — {opportunity['arena']}

**Why this matches:** {len(best['matched_terms'])} capability/learning terms overlap with the verified arena; the opportunity is currently inside its valid window and passed the learner eligibility/access gates.

### Do this now
{opportunity['action']}

### Own this contribution
{opportunity['contribution']}

### Deadline
{opportunity['deadline_text']}

### Evidence to capture
{opportunity['receipt']}

### Close the loop
After taking the external action, reply to this issue with the external receipt URL or exact status. That reply is the first market-evidence state transition; the recommendation itself is not evidence of outcome.
{alternatives}
### Failure / retry
If the arena rejects eligibility, required access is unavailable, or the source page is no longer open, do **not** improvise around the gate. Edit this issue with the observed failure/access change; the workflow reruns and preserves the prior receipt comment.

**Boundary:** this MVExecutable ranks only the small manually verified registry. It does not claim exhaustive opportunity discovery, adoption, evaluator response, or outcome until an external receipt exists.
"""


def run_from_event(event: dict[str, Any], registry: dict[str, Any], *, as_of: date) -> tuple[int, str]:
    issue = event.get("issue") or {}
    try:
        learner = validate_learner(parse_issue_body(str(issue.get("body") or "")))
    except InputError as exc:
        return 2, f"""## Learning → Market Evidence — INPUT FAILURE

**Failure:** {exc}

### Recovery
Edit the issue and supply the missing/corrected field. Issue edits automatically rerun the workflow; the failed receipt remains observable in the issue history.
"""

    ranked, rejected = rank_matches(learner, registry, as_of=as_of)
    if not ranked:
        return 3, render_result(learner, ranked, rejected, as_of=as_of, registry=registry)
    return 0, render_result(learner, ranked, rejected, as_of=as_of, registry=registry)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, help="GitHub event JSON path")
    parser.add_argument("--opportunities", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--as-of", help="YYYY-MM-DD; defaults to runner date")
    args = parser.parse_args()

    event = json.loads(Path(args.event).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.opportunities).read_text(encoding="utf-8"))
    as_of = date.fromisoformat(args.as_of) if args.as_of else date.today()
    code, markdown = run_from_event(event, registry, as_of=as_of)
    Path(args.output).write_text(markdown.rstrip() + "\n", encoding="utf-8")
    print(markdown)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
