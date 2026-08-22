from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / "evals" / "task_001_atomic_process"
GRADER = TASK / "grader.py"


def run_grader(candidate: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
    result = subprocess.run(
        [sys.executable, str(GRADER), str(candidate)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result, json.loads(result.stdout)


def test_known_bad_fixture_is_rejected_for_atomicity_failures() -> None:
    result, report = run_grader(TASK / "fixture" / "store.py")

    assert result.returncode == 1
    assert report["passed"] is False
    assert report["score"] == 50
    failed = {check["name"] for check in report["checks"] if not check["passed"]}
    assert failed == {
        "failed_create_rolls_back_projection",
        "failed_update_restores_previous_projection",
    }


def test_reference_solution_passes_every_check() -> None:
    result, report = run_grader(TASK / "reference" / "store.py")

    assert result.returncode == 0
    assert report["passed"] is True
    assert report["score"] == 100
    assert all(check["passed"] for check in report["checks"])
