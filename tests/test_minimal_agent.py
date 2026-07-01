"""Tests for the reference implementation — proves the loop runs and the verifier can veto."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples" / "minimal_agent"))

import run as ref  # noqa: E402


def test_clean_case_ships():
    out = ref.run({"evidence": ["a", "b", "c", "d"], "risk": 0.2, "cost": 0.3})
    assert out["proposal"]["recommendation"] == "SHIP"
    assert out["review"]["verdict"] == "SHIP"
    assert out["review"]["reasons"] == []


def test_missing_evidence_is_vetoed():
    out = ref.run({"risk": 0.1, "cost": 0.1})  # no evidence → worker reports unavailable
    assert "evidence" in out["proposal"]["gaps"]
    assert out["review"]["verdict"] == "BLOCK"


def test_verifier_recomputes_the_score_independently():
    case = {"evidence": ["a", "b"], "risk": 0.5, "cost": 0.5}
    out = ref.run(case)
    assert out["review"]["verifier_score"] == out["proposal"]["score"]


def test_every_finding_carries_a_data_quality_flag():
    out = ref.run({"evidence": ["a"]})
    assert all("data_quality" in f for f in out["proposal"]["findings"])
