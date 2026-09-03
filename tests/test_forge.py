from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from signalops.forge import (
    ALLOWED_PREDICTIONS,
    CONTRACT_FIELDS,
    MACHINE_LABEL,
    _append_event,
    _parse_prediction,
    _render_ownership_contract,
    _run_hostile_challenge,
    _section_values,
    inspect_repo,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class ForgeTests(unittest.TestCase):
    def test_installed_forge_inspect_command_returns_json(self) -> None:
        completed = subprocess.run(
            ["forge", "inspect", "."],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["target_file"], "src/signalops/hackathon.py")
        self.assertTrue(payload["execution_path"])

    def test_inspect_emits_labeled_candidates_for_signalops_path(self) -> None:
        result = inspect_repo(REPO_ROOT)

        path = [item["value"] for item in result["execution_path"]]
        self.assertIn("SerpApiClient().search_google", path)
        self.assertIn("OpportunityAssessor().assess", path)
        self.assertIn("_ensure_serp_policy", path)
        self.assertIn("store.process", path)

        inferred = (
            result["execution_path"]
            + result["state_reads"]
            + result["state_writes"]
            + result["candidate_invariants"]
        )
        self.assertTrue(inferred)
        self.assertTrue(all(item["label"] == MACHINE_LABEL for item in inferred))
        self.assertEqual(result["target_file"], "src/signalops/hackathon.py")
        self.assertTrue(result["commit"])

    def test_ownership_template_has_exactly_fourteen_blank_fields(self) -> None:
        text = _render_ownership_contract(Path("/tmp/example-repo"), "abc123")
        values = _section_values(text)

        self.assertEqual(tuple(values), CONTRACT_FIELDS)
        self.assertEqual(len(values), 14)
        self.assertTrue(all(value == "" for value in values.values()))
        self.assertIn("commit=abc123", text)
        self.assertIn("target=src/signalops/hackathon.py", text)

    def test_prediction_parser_accepts_only_bounded_outcomes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "prediction.md"
            path.write_text(
                "EXPECTED_OUTCOME: RAISES_SERPAPI_ERROR\nWHY:\nmanual reasoning\n",
                encoding="utf-8",
            )
            expected, raw = _parse_prediction(path)
            self.assertEqual(expected, "RAISES_SERPAPI_ERROR")
            self.assertTrue(raw)

            path.write_text("EXPECTED_OUTCOME: INVENTED\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "one of"):
                _parse_prediction(path)

    def test_hostile_fixture_exposes_one_of_the_two_bounded_schema_outcomes(self) -> None:
        observed = _run_hostile_challenge(REPO_ROOT)
        self.assertEqual(observed["exit_code"], 0)
        self.assertIn(observed["outcome"], ALLOWED_PREDICTIONS)

    def test_receipt_ledger_is_append_only_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipts.jsonl"
            _append_event(path, {"event": "PREDICTION_LOCKED", "run_id": "one"})
            _append_event(path, {"event": "VERIFICATION_RESULT", "run_id": "one"})

            lines = path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            first, second = map(json.loads, lines)
            self.assertEqual(first["event"], "PREDICTION_LOCKED")
            self.assertEqual(second["event"], "VERIFICATION_RESULT")


if __name__ == "__main__":
    unittest.main()
