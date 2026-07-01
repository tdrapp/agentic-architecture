#!/usr/bin/env python3
"""Minimal, runnable reference implementation of the orchestration shape.

Zero dependencies, no LLM calls — deterministic so it runs in CI and in a test. The "agents" are
plain functions; the point is the *structure*, which mirrors the patterns:

    orchestrator  → parallel workers (C1 isolation, C4 honest structured output, C10 typed schema)
                  → synthesizer (fuses typed fields, invents nothing)
                  → INDEPENDENT verifier (C2: re-derives, can veto)  → verdict

Run:  python examples/minimal_agent/run.py
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Callable

# --- structured worker output (C10): every worker returns the same typed schema, with a quality flag (C4)


@dataclass
class Finding:
    worker: str
    score: float          # 0..1 contribution to the decision
    data_quality: str     # ok | partial | unavailable
    note: str


# --- workers (specialists). Each is isolated: it sees only its slice of the input (C1).


def evidence_worker(case: dict) -> Finding:
    ev = case.get("evidence")
    if ev is None:
        return Finding("evidence", 0.0, "unavailable", "no evidence provided")
    return Finding("evidence", min(len(ev) / 5.0, 1.0), "ok", f"{len(ev)} items")


def risk_worker(case: dict) -> Finding:
    r = case.get("risk")
    if r is None:
        return Finding("risk", 0.0, "unavailable", "no risk estimate")
    return Finding("risk", 1.0 - float(r), "ok", f"risk={r}")


def cost_worker(case: dict) -> Finding:
    c = case.get("cost")
    if c is None:
        return Finding("cost", 0.5, "partial", "cost assumed medium (missing)")
    return Finding("cost", 1.0 - float(c), "ok", f"cost={c}")


WORKERS: list[Callable[[dict], Finding]] = [evidence_worker, risk_worker, cost_worker]


# --- synthesizer: fuse typed fields only; invent nothing; surface gaps.


def synthesize(findings: list[Finding]) -> dict:
    usable = [f for f in findings if f.data_quality != "unavailable"]
    gaps = [f.worker for f in findings if f.data_quality == "unavailable"]
    score = round(sum(f.score for f in usable) / len(usable), 3) if usable else 0.0
    return {
        "score": score,
        "recommendation": "SHIP" if score >= 0.6 else "HOLD",
        "gaps": gaps,
        "findings": [asdict(f) for f in findings],
    }


# --- independent verifier (C2): sees findings + proposal, NOT the synthesizer's reasoning.
# Re-derives the score itself and can veto. Argues against shipping.


def verify(findings: list[Finding], proposal: dict) -> dict:
    reasons: list[str] = []

    usable = [f for f in findings if f.data_quality != "unavailable"]
    recomputed = round(sum(f.score for f in usable) / len(usable), 3) if usable else 0.0
    if recomputed != proposal["score"]:
        reasons.append(f"score mismatch: verifier={recomputed} vs proposal={proposal['score']}")

    if proposal["gaps"]:
        reasons.append(f"missing evidence from: {', '.join(proposal['gaps'])} (unavailable data)")

    if any(f.data_quality == "partial" for f in findings) and proposal["recommendation"] == "SHIP":
        reasons.append("shipping on partial-quality inputs")

    verdict = "BLOCK" if reasons else "SHIP"
    return {"verdict": verdict, "reasons": reasons, "verifier_score": recomputed}


def run(case: dict) -> dict:
    findings = [w(case) for w in WORKERS]          # fan-out
    proposal = synthesize(findings)                 # fuse
    review = verify(findings, proposal)             # independent check (C2)
    return {"proposal": proposal, "review": review}


if __name__ == "__main__":
    demo = {"evidence": ["a", "b", "c", "d"], "risk": 0.2, "cost": 0.3}
    print(json.dumps(run(demo), indent=2))
