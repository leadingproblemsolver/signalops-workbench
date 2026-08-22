#!/usr/bin/env python3
"""Deterministic grader for task_001_atomic_process."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
import traceback


def load_candidate(path: Path):
    spec = importlib.util.spec_from_file_location("candidate_store", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import candidate: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_check(name, fn):
    try:
        fn()
        return {"name": name, "passed": True, "error": None}
    except Exception as exc:
        return {"name": name, "passed": False, "error": f"{type(exc).__name__}: {exc}"}


def grade(candidate_path: Path) -> dict:
    module = load_candidate(candidate_path)
    Store = module.Store

    def fresh_store():
        tempdir = tempfile.TemporaryDirectory()
        store = Store(Path(tempdir.name) / "signalops.db")
        return tempdir, store

    def normal_create():
        tempdir, store = fresh_store()
        try:
            store.process("s-1", "first", 7.5)
            assert store.surface("s-1") == {
                "external_id": "s-1",
                "title": "first",
                "score": 7.5,
            }
            events = store.events("s-1")
            assert len(events) == 1
            assert events[0]["event_type"] == "surface_processed"
            assert events[0]["payload"] == "first"
        finally:
            tempdir.cleanup()

    def normal_update():
        tempdir, store = fresh_store()
        try:
            store.process("s-1", "first", 7.5)
            store.process("s-1", "second", 8.5)
            assert store.surface("s-1")["title"] == "second"
            assert store.surface("s-1")["score"] == 8.5
            events = store.events("s-1")
            assert [event["payload"] for event in events] == ["first", "second"]
        finally:
            tempdir.cleanup()

    def failed_create_is_atomic():
        tempdir, store = fresh_store()
        try:
            try:
                store.process("s-fail", "must-not-commit", 9.0, fail_event=True)
            except RuntimeError as exc:
                assert "injected event write failure" in str(exc)
            else:
                raise AssertionError("injected event failure did not propagate")

            assert store.surface("s-fail") is None, (
                "projection committed even though its event receipt failed"
            )
            assert store.events("s-fail") == []
        finally:
            tempdir.cleanup()

    def failed_update_is_atomic():
        tempdir, store = fresh_store()
        try:
            store.process("s-1", "original", 6.0)
            try:
                store.process("s-1", "corrupt-update", 10.0, fail_event=True)
            except RuntimeError:
                pass
            else:
                raise AssertionError("injected event failure did not propagate")

            assert store.surface("s-1") == {
                "external_id": "s-1",
                "title": "original",
                "score": 6.0,
            }, "failed update changed the durable projection"
            events = store.events("s-1")
            assert len(events) == 1
            assert events[0]["payload"] == "original"
        finally:
            tempdir.cleanup()

    checks = [
        run_check("normal_create", normal_create),
        run_check("normal_update", normal_update),
        run_check("failed_create_rolls_back_projection", failed_create_is_atomic),
        run_check("failed_update_restores_previous_projection", failed_update_is_atomic),
    ]
    passed = sum(check["passed"] for check in checks)
    return {
        "task_id": "task_001_atomic_process",
        "candidate": str(candidate_path),
        "score": int(100 * passed / len(checks)),
        "passed": passed == len(checks),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate", type=Path)
    args = parser.parse_args()
    try:
        result = grade(args.candidate.resolve())
    except Exception:
        result = {
            "task_id": "task_001_atomic_process",
            "candidate": str(args.candidate),
            "score": 0,
            "passed": False,
            "grader_error": traceback.format_exc(),
        }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
