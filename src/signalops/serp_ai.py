"""Constrained AI interpretation for SerpApi evidence.

The model may propose an inference and bounded scores, but it never chooses the final
SignalOps action. Source text remains authoritative evidence; the existing deterministic
policy engine owns escalation.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Callable, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .serpapi import SerpEvidence


class AIAssessmentError(RuntimeError):
    """Raised when the assessment model fails its structured-output contract."""


@dataclass(frozen=True, slots=True)
class OpportunityAssessment:
    index: int
    inference: str
    relevance: float
    urgency: float
    conversation: float
    who: str = ""


Transport = Callable[[Request, float], bytes]


def _default_transport(request: Request, timeout: float) -> bytes:
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS endpoint
            return response.read()
    except HTTPError as exc:
        raise AIAssessmentError(f"OpenAI HTTP error: {exc.code}") from exc
    except URLError as exc:
        raise AIAssessmentError(f"OpenAI network error: {exc.reason}") from exc


def _response_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str) and direct.strip():
        return direct.strip()

    chunks: list[str] = []
    output = payload.get("output") or []
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content") or []
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                text = part.get("text")
                if isinstance(text, str) and text.strip():
                    chunks.append(text.strip())
    if not chunks:
        raise AIAssessmentError("OpenAI response contained no text output")
    return "\n".join(chunks)


def _bounded_score(value: Any, name: str) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError) as exc:
        raise AIAssessmentError(f"{name} must be numeric") from exc
    if not 0 <= score <= 10:
        raise AIAssessmentError(f"{name} must be within 0..10")
    return round(score, 2)


class OpportunityAssessor:
    """Batch-assess live search evidence without allowing the model to authorize action."""

    endpoint = "https://api.openai.com/v1/responses"

    def __init__(
        self,
        api_key: str | None = None,
        *,
        model: str | None = None,
        timeout: float = 30.0,
        transport: Transport | None = None,
    ) -> None:
        self.api_key = (api_key or os.getenv("OPENAI_API_KEY", "")).strip()
        if not self.api_key:
            raise AIAssessmentError("OPENAI_API_KEY is required for AI assessment")
        self.model = (model or os.getenv("OPENAI_MODEL", "gpt-5.6-luna")).strip()
        if not self.model:
            raise AIAssessmentError("OPENAI_MODEL cannot be empty")
        self.timeout = float(timeout)
        self.transport = transport or _default_transport

    def assess(
        self,
        evidence: Sequence[SerpEvidence],
        *,
        goal: str,
    ) -> list[OpportunityAssessment]:
        if not evidence:
            return []
        normalized_goal = goal.strip()
        if not normalized_goal:
            raise ValueError("goal is required")

        source_rows = [
            {
                "index": index,
                "title": row.title,
                "url": row.url,
                "snippet": row.observed_fact[:1600],
                "source": row.source,
                "date": row.date,
                "position": row.position,
            }
            for index, row in enumerate(evidence)
        ]
        prompt = f"""You are a bounded market-opportunity triage model.

GOAL:
{normalized_goal}

RULES:
- Use ONLY the supplied search-result fields as factual evidence.
- Never claim a budget, deadline, role, pain, owner, or urgency unless the source text supports it.
- Keep inference explicitly hypothetical and falsifiable.
- Score relevance, urgency, and conversation potential from 0 to 10.
- High urgency requires evidence of a current trigger; absence of freshness evidence must reduce urgency.
- conversation means probability that a useful human interaction could follow from this evidence, not likelihood of a sale.
- `who` must be copied or conservatively inferred from title/source text; use an empty string if unknown.
- Return EXACTLY one JSON array, no markdown, with one object for every input index.
- Object keys: index, inference, relevance, urgency, conversation, who.

SOURCE RESULTS:
{json.dumps(source_rows, ensure_ascii=False)}
"""

        body = json.dumps({"model": self.model, "input": prompt}).encode("utf-8")
        request = Request(
            self.endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        raw = self.transport(request, self.timeout)
        try:
            response_payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AIAssessmentError("OpenAI returned invalid JSON") from exc
        if not isinstance(response_payload, dict):
            raise AIAssessmentError("OpenAI response must be a JSON object")

        text = _response_text(response_payload)
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise AIAssessmentError("model output was not valid JSON") from exc
        if not isinstance(parsed, list):
            raise AIAssessmentError("model output must be a JSON array")
        if len(parsed) != len(evidence):
            raise AIAssessmentError("model output count must match evidence count")

        assessments: list[OpportunityAssessment] = []
        seen: set[int] = set()
        for item in parsed:
            if not isinstance(item, dict):
                raise AIAssessmentError("each assessment must be a JSON object")
            try:
                index = int(item["index"])
            except (KeyError, TypeError, ValueError) as exc:
                raise AIAssessmentError("assessment index is required") from exc
            if not 0 <= index < len(evidence) or index in seen:
                raise AIAssessmentError("assessment indices must be unique and in range")
            seen.add(index)
            assessments.append(
                OpportunityAssessment(
                    index=index,
                    inference=str(item.get("inference") or "").strip(),
                    relevance=_bounded_score(item.get("relevance"), "relevance"),
                    urgency=_bounded_score(item.get("urgency"), "urgency"),
                    conversation=_bounded_score(item.get("conversation"), "conversation"),
                    who=str(item.get("who") or "").strip()[:240],
                )
            )

        return sorted(assessments, key=lambda row: row.index)
