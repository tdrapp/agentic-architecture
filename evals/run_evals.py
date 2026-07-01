#!/usr/bin/env python3
"""Minimal but real eval loop (pattern C9), zero dependencies.

task → responder(input) → grader(output, task) → pass/fail, aggregated over k runs (pass^k).

The responder is pluggable: point `--responder module:function` at a real model to grade live
guidance. The default `--demo` responder is deterministic so `python evals/run_evals.py` and CI run
green without network. Grading is keyword-based (all `expect` substrings must be present) — swap in a
model grader for nuance.

Run:  python evals/run_evals.py --demo
      python evals/run_evals.py --responder mymod:answer -k 3
"""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Callable

TASKS = Path(__file__).with_name("tasks.json")


def load_tasks(path: Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["tasks"]


def grade(output: str, task: dict) -> bool:
    text = output.lower()
    return all(kw.lower() in text for kw in task["expect"])


def demo_responder(task: dict) -> str:
    """Canned correct answers keyed by task id — proves the harness runs, not the model."""
    return task.get("_demo_answer", "")


def load_responder(spec: str) -> Callable[[dict], str]:
    module_name, func_name = spec.split(":", 1)
    return getattr(importlib.import_module(module_name), func_name)


def run(tasks: list[dict], responder: Callable[[dict], str], k: int) -> dict:
    results = []
    for t in tasks:
        passes = [grade(responder(t), t) for _ in range(k)]
        results.append({
            "id": t["id"],
            "pass_at_k": any(passes),
            "pass_hat_k": all(passes),   # must hold every run
            "runs": sum(passes),
        })
    passed = sum(1 for r in results if r["pass_hat_k"])
    return {
        "tasks": len(tasks),
        "k": k,
        "pass_hat_k": passed,
        "pass_rate": round(passed / len(tasks), 3) if tasks else 0.0,
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Run the design-judgment eval set.")
    p.add_argument("--responder", help="module:function returning a str answer for a task dict.")
    p.add_argument("--demo", action="store_true", help="Use the built-in deterministic responder.")
    p.add_argument("-k", type=int, default=1, help="Runs per task (pass^k).")
    p.add_argument("--tasks", type=Path, default=TASKS)
    args = p.parse_args(argv)

    responder = demo_responder if args.demo or not args.responder else load_responder(args.responder)
    report = run(load_tasks(args.tasks), responder, args.k)
    print(json.dumps(report, indent=2))
    return 0 if report["pass_hat_k"] == report["tasks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
