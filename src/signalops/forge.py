"""Minimal execution-path ownership gate for SignalOps.

Forge deliberately does not certify ownership. It binds a machine inspection, a
human-authored contract, and a precommitted hostile prediction to one git commit
so the resulting receipt is falsifiable and inspectable.
"""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence
import uuid


TARGET_FILE = Path("src/signalops/hackathon.py")
TARGET_FUNCTION = "discover"
FORGE_DIR = Path(".forge")
OWNERSHIP_FILE = FORGE_DIR / "ownership.md"
PREDICTION_FILE = FORGE_DIR / "prediction.md"
LEDGER_FILE = FORGE_DIR / "receipts.jsonl"
LATEST_RECEIPT_FILE = FORGE_DIR / "latest-receipt.md"
MACHINE_LABEL = "MACHINE_CANDIDATE"

CHALLENGE_ID = "serpapi_http_200_missing_organic_results"
CHALLENGE_DESCRIPTION = (
    "SerpApi returns HTTP 200 with a JSON object that omits organic_results."
)
ALLOWED_PREDICTIONS = {
    "RETURNS_EMPTY_RESULTS",
    "RAISES_SERPAPI_ERROR",
}

CONTRACT_FIELDS: tuple[str, ...] = (
    "Target decision",
    "Entry point",
    "Inputs",
    "Execution path",
    "Source of truth and state",
    "Side effects",
    "Outputs",
    "Invariant",
    "Boundary conditions",
    "Failure semantics",
    "Recovery semantics",
    "Observation vs inference boundary",
    "Authorization boundary",
    "Dangerous failure and tradeoff",
)


class ForgeError(RuntimeError):
    """Raised when Forge cannot produce a trustworthy local receipt."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha(repo: Path) -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ForgeError(f"cannot read git commit: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "not a git repository"
        raise ForgeError(f"cannot read git commit: {detail}")
    return completed.stdout.strip()


def _callee(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _callee(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    if isinstance(node, ast.Call):
        prefix = _callee(node.func)
        return f"{prefix}()" if prefix else "call()"
    return ""


class _CallCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.calls: list[tuple[int, str]] = []

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 - ast visitor API
        self.calls.append((node.lineno, _callee(node.func)))
        self.generic_visit(node)


def _candidate(value: str, *, line: int) -> dict[str, Any]:
    return {"label": MACHINE_LABEL, "value": value, "line": line}


def _discover_function(tree: ast.Module) -> ast.FunctionDef:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == TARGET_FUNCTION:
            return node
    raise ForgeError(f"target function not found: {TARGET_FUNCTION}")


def _literal_invariant(function: ast.FunctionDef) -> tuple[int, str] | None:
    for node in ast.walk(function):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values, strict=True):
            if (
                isinstance(key, ast.Constant)
                and key.value == "invariant"
                and isinstance(value, ast.Constant)
                and isinstance(value.value, str)
            ):
                return value.lineno, value.value
    return None


def inspect_repo(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    target = repo / TARGET_FILE
    if not target.is_file():
        raise ForgeError(f"target file not found: {TARGET_FILE}")

    source = target.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(target))
    except SyntaxError as exc:
        raise ForgeError(f"cannot parse target file: {exc}") from exc

    function = _discover_function(tree)
    function_calls = _CallCollector()
    function_calls.visit(function)

    path_markers = (
        "SerpApiClient().search_google",
        "OpportunityAssessor().assess",
        "_ensure_serp_policy",
        "store.process",
    )
    execution_path = [
        _candidate(callee, line=line)
        for line, callee in sorted(function_calls.calls)
        if callee in path_markers
    ]
    if not execution_path:
        raise ForgeError("no execution-path candidates found in target function")

    file_calls = _CallCollector()
    file_calls.visit(tree)
    state_reads = [
        _candidate(callee, line=line)
        for line, callee in sorted(file_calls.calls)
        if callee == "store.policy"
    ]
    state_writes = [
        _candidate(callee, line=line)
        for line, callee in sorted(file_calls.calls)
        if callee in {"store.configure_policy", "store.process", "store.record_outcome"}
    ]

    invariant = _literal_invariant(function)
    candidate_invariants = (
        [_candidate(invariant[1], line=invariant[0])] if invariant else []
    )

    return {
        "schema_version": 1,
        "repo": str(repo),
        "commit": _git_sha(repo),
        "target_file": str(TARGET_FILE),
        "target_function": TARGET_FUNCTION,
        "execution_path": execution_path,
        "state_reads": state_reads,
        "state_writes": state_writes,
        "candidate_invariants": candidate_invariants,
        "claim_boundary": (
            "All path/state/invariant items are machine candidates, not human ownership claims."
        ),
    }


def _render_ownership_contract(repo: Path, commit: str) -> str:
    lines = [
        "# Forge Ownership Contract",
        "",
        "<!-- forge-binding",
        f"repo={repo.resolve()}",
        f"commit={commit}",
        f"target={TARGET_FILE}",
        "-->",
        "",
        "Fill every field personally. Generated completion does not establish ownership.",
        "",
    ]
    for index, field in enumerate(CONTRACT_FIELDS, start=1):
        lines.extend([f"## {index:02d}. {field}", "", "", ""])
    return "\n".join(lines).rstrip() + "\n"


def _binding(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    inside = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line == "<!-- forge-binding":
            inside = True
            continue
        if inside and line == "-->":
            break
        if inside and "=" in line:
            key, value = line.split("=", 1)
            fields[key.strip()] = value.strip()
    return fields


def _section_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    lines = text.splitlines()
    positions: list[tuple[int, str]] = []
    for line_index, line in enumerate(lines):
        for index, field in enumerate(CONTRACT_FIELDS, start=1):
            if line.strip() == f"## {index:02d}. {field}":
                positions.append((line_index, field))
                break
    for idx, (start, field) in enumerate(positions):
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(lines)
        body = "\n".join(lines[start + 1 : end]).strip()
        values[field] = body
    return values


def _validate_ownership(repo: Path, commit: str) -> None:
    path = repo / OWNERSHIP_FILE
    if not path.is_file():
        raise ForgeError(f"ownership contract missing: {OWNERSHIP_FILE}; run `forge own .`")

    text = path.read_text(encoding="utf-8")
    binding = _binding(text)
    if binding.get("commit") != commit:
        raise ForgeError(
            "ownership contract is stale: its commit binding does not match current HEAD"
        )
    if binding.get("target") != str(TARGET_FILE):
        raise ForgeError("ownership contract target does not match the Forge target file")

    values = _section_values(text)
    missing = [field for field in CONTRACT_FIELDS if not values.get(field, "").strip()]
    if missing:
        raise ForgeError(
            "ownership contract is incomplete; fill personally: " + ", ".join(missing)
        )


def write_ownership_contract(repo: Path) -> Path:
    repo = repo.resolve()
    commit = _git_sha(repo)
    target = repo / TARGET_FILE
    if not target.is_file():
        raise ForgeError(f"target file not found: {TARGET_FILE}")

    path = repo / OWNERSHIP_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ForgeError(
            f"refusing to overwrite existing human work: {OWNERSHIP_FILE}"
        )
    path.write_text(_render_ownership_contract(repo, commit), encoding="utf-8")
    return path


def _parse_prediction(path: Path) -> tuple[str, bytes]:
    if not path.is_file():
        raise ForgeError(
            f"prediction missing: {PREDICTION_FILE}; create it personally before verify"
        )
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ForgeError("prediction must be UTF-8 text") from exc

    expected = ""
    for line in text.splitlines():
        if line.strip().startswith("EXPECTED_OUTCOME:"):
            expected = line.split(":", 1)[1].strip()
            break
    if expected not in ALLOWED_PREDICTIONS:
        choices = ", ".join(sorted(ALLOWED_PREDICTIONS))
        raise ForgeError(
            "prediction must contain `EXPECTED_OUTCOME: <value>` where value is one of: "
            + choices
        )
    return expected, raw


def _append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(
        event,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    with path.open("a", encoding="utf-8") as handle:
        handle.write(encoded + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _run_hostile_challenge(repo: Path) -> dict[str, Any]:
    # The command is fixed here. Forge never executes a user-supplied command.
    script = r"""
import json
from signalops.serpapi import SerpApiClient, SerpApiError

payload = {"search_metadata": {"id": "forge-hostile-200", "status": "Success"}}
client = SerpApiClient(
    "forge-test-key",
    transport=lambda _request, _timeout: json.dumps(payload).encode("utf-8"),
)
try:
    rows = client.search_google("forge hostile schema boundary", limit=1)
except SerpApiError as exc:
    result = {"outcome": "RAISES_SERPAPI_ERROR", "detail": str(exc)}
else:
    if rows == []:
        result = {"outcome": "RETURNS_EMPTY_RESULTS", "count": 0}
    else:
        result = {"outcome": "RETURNS_RESULTS", "count": len(rows)}
print(json.dumps(result, sort_keys=True))
""".strip()

    env = os.environ.copy()
    src = str(repo / "src")
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = src if not existing else src + os.pathsep + existing
    command = [sys.executable, "-c", script]

    try:
        completed = subprocess.run(
            command,
            cwd=repo,
            env=env,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ForgeError(f"hostile fixture could not run: {exc}") from exc

    if completed.returncode != 0:
        raise ForgeError(
            "hostile fixture failed to execute: "
            + (completed.stderr.strip() or f"exit {completed.returncode}")
        )
    try:
        observed = json.loads(completed.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError) as exc:
        raise ForgeError("hostile fixture returned unreadable output") from exc
    if not isinstance(observed, dict) or not isinstance(observed.get("outcome"), str):
        raise ForgeError("hostile fixture returned an invalid result object")

    return {
        "runner": "fixed_python_subprocess",
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
        **observed,
    }


def _render_receipt(result: dict[str, Any]) -> str:
    state = result["evidence_state"]
    match_text = "yes" if result["prediction_matched"] else "no"
    return "\n".join(
        [
            "# Forge Verification Receipt",
            "",
            f"- **Run:** `{result['run_id']}`",
            f"- **Commit:** `{result['commit']}`",
            f"- **Target:** `{result['target_file']}`",
            f"- **Challenge:** {result['challenge_description']}",
            f"- **Prediction locked:** `{result['prediction_locked_at']}`",
            f"- **Prediction SHA-256:** `{result['prediction_sha256']}`",
            f"- **Predicted:** `{result['predicted_outcome']}`",
            f"- **Observed:** `{result['observed_outcome']}`",
            f"- **Prediction matched:** {match_text}",
            f"- **Evidence state:** `{state}`",
            "",
            "This is a local hostile-verification receipt only. It is not external "
            "engineering judgment, production use, or proof of human ownership by itself.",
            "",
        ]
    )


def verify_repo(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    commit = _git_sha(repo)
    if not (repo / TARGET_FILE).is_file():
        raise ForgeError(f"target file not found: {TARGET_FILE}")

    _validate_ownership(repo, commit)
    predicted, prediction_bytes = _parse_prediction(repo / PREDICTION_FILE)

    run_id = uuid.uuid4().hex
    locked_at = _now()
    prediction_sha = hashlib.sha256(prediction_bytes).hexdigest()
    ledger = repo / LEDGER_FILE

    _append_event(
        ledger,
        {
            "schema_version": 1,
            "event": "PREDICTION_LOCKED",
            "run_id": run_id,
            "repo": str(repo),
            "commit": commit,
            "target_file": str(TARGET_FILE),
            "challenge_id": CHALLENGE_ID,
            "challenge_description": CHALLENGE_DESCRIPTION,
            "prediction_sha256": prediction_sha,
            "predicted_outcome": predicted,
            "locked_at": locked_at,
        },
    )

    observed = _run_hostile_challenge(repo)
    matched = predicted == observed["outcome"]
    result = {
        "schema_version": 1,
        "event": "VERIFICATION_RESULT",
        "run_id": run_id,
        "repo": str(repo),
        "commit": commit,
        "target_file": str(TARGET_FILE),
        "challenge_id": CHALLENGE_ID,
        "challenge_description": CHALLENGE_DESCRIPTION,
        "prediction_locked_at": locked_at,
        "prediction_sha256": prediction_sha,
        "predicted_outcome": predicted,
        "observed_outcome": observed["outcome"],
        "prediction_matched": matched,
        "evidence_state": "HOSTILE_VERIFIED" if matched else "GAP_EXPOSED",
        "runner": observed["runner"],
        "runner_exit_code": observed["exit_code"],
        "runner_stdout": observed["stdout"],
        "runner_stderr": observed["stderr"],
        "observed_at": _now(),
    }
    _append_event(ledger, result)

    markdown = repo / LATEST_RECEIPT_FILE
    markdown.write_text(_render_receipt(result), encoding="utf-8")
    result["ledger"] = str(LEDGER_FILE)
    result["markdown_receipt"] = str(LATEST_RECEIPT_FILE)
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="forge",
        description=(
            "Bind one SignalOps execution path to a human contract and hostile prediction."
        ),
    )
    commands = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("inspect", "Emit machine-candidate execution-path JSON"),
        ("own", "Create the blank human ownership contract"),
        ("verify", "Hash-lock a human prediction, run one hostile fixture, append receipt"),
    ):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("repo", nargs="?", default=".", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "inspect":
            print(
                json.dumps(
                    inspect_repo(args.repo),
                    indent=2,
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        elif args.command == "own":
            path = write_ownership_contract(args.repo)
            print(path)
        elif args.command == "verify":
            print(
                json.dumps(
                    verify_repo(args.repo),
                    indent=2,
                    ensure_ascii=False,
                    sort_keys=True,
                )
            )
        return 0
    except (ForgeError, OSError) as exc:
        print(f"forge: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
