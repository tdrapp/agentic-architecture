"""Tests for the eval harness — proves the loop runs, grades, and aggregates pass^k."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))

import run_evals as ev  # noqa: E402

TASKS = Path(__file__).resolve().parents[1] / "evals" / "tasks.json"


def test_demo_responder_passes_all_tasks():
    report = ev.run(ev.load_tasks(TASKS), ev.demo_responder, k=3)
    assert report["pass_hat_k"] == report["tasks"]
    assert report["pass_rate"] == 1.0


def test_grader_requires_all_keywords():
    task = {"expect": ["alpha", "beta"]}
    assert ev.grade("alpha and beta", task) is True
    assert ev.grade("only alpha", task) is False


def test_empty_responder_fails():
    report = ev.run(ev.load_tasks(TASKS), lambda t: "", k=1)
    assert report["pass_hat_k"] == 0


def test_tasks_file_is_wellformed():
    tasks = ev.load_tasks(TASKS)
    assert tasks and all({"id", "input", "expect"} <= t.keys() for t in tasks)
