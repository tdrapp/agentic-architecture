"""Unit tests for the doc-freshness tool. No network: the fetch function is monkeypatched."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import doc_freshness_check as dfc  # noqa: E402


def _write_sources(tmp_path: Path, sources: list[dict]) -> Path:
    p = tmp_path / "sources.json"
    p.write_text(json.dumps({"sources": sources}), encoding="utf-8")
    return p


def test_unchanged_when_hash_matches_and_claims_present(tmp_path, monkeypatch):
    page = "<html><body>Workflows and an ORCHESTRATOR pattern.</body></html>"
    pinned = dfc.sha256(dfc.normalize(page))
    src = _write_sources(tmp_path, [{
        "name": "x", "url": "https://example.test/a",
        "tracked_claims": ["workflows", "orchestrator"], "page_sha256": pinned,
    }])
    monkeypatch.setattr(dfc, "fetch", lambda url: (page, None))
    result = dfc.run_check(src)
    assert result["sources"][0]["status"] == "unchanged"
    assert result["_meta"]["data_quality"] == "ok"


def test_claim_missing_is_flagged_with_the_missing_claim(tmp_path, monkeypatch):
    page = "<p>Only workflows here.</p>"
    src = _write_sources(tmp_path, [{
        "name": "x", "url": "https://example.test/a",
        "tracked_claims": ["workflows", "evaluator-optimizer"], "page_sha256": dfc.sha256(dfc.normalize(page)),
    }])
    monkeypatch.setattr(dfc, "fetch", lambda url: (page, None))
    result = dfc.run_check(src)
    row = result["sources"][0]
    assert row["status"] == "CLAIM-MISSING"
    assert "evaluator-optimizer" in row["missing_claims"]


def test_page_changed_when_hash_differs_but_claims_present(tmp_path, monkeypatch):
    page = "<p>workflows and orchestrator, plus a new paragraph.</p>"
    src = _write_sources(tmp_path, [{
        "name": "x", "url": "https://example.test/a",
        "tracked_claims": ["workflows"], "page_sha256": "deadbeef",
    }])
    monkeypatch.setattr(dfc, "fetch", lambda url: (page, None))
    result = dfc.run_check(src)
    assert result["sources"][0]["status"] == "PAGE-CHANGED"


def test_unreachable_sets_data_quality_unavailable_and_never_crashes(tmp_path, monkeypatch):
    src = _write_sources(tmp_path, [{
        "name": "x", "url": "https://example.test/a", "tracked_claims": ["workflows"], "page_sha256": "abc",
    }])
    monkeypatch.setattr(dfc, "fetch", lambda url: (None, "network_error:down"))
    result = dfc.run_check(src)
    assert result["sources"][0]["status"] == "unreachable"
    assert result["_meta"]["data_quality"] == "unavailable"


def test_partial_data_quality_when_some_reachable(tmp_path, monkeypatch):
    ok_page = "<p>workflows</p>"
    src = _write_sources(tmp_path, [
        {"name": "ok", "url": "https://example.test/ok", "tracked_claims": ["workflows"], "page_sha256": dfc.sha256(dfc.normalize(ok_page))},
        {"name": "down", "url": "https://example.test/down", "tracked_claims": [], "page_sha256": "x"},
    ])

    def fake_fetch(url: str):
        return (ok_page, None) if url.endswith("/ok") else (None, "http_503")

    monkeypatch.setattr(dfc, "fetch", fake_fetch)
    result = dfc.run_check(src)
    assert result["_meta"]["data_quality"] == "partial"


def test_update_repins_hash_and_reports_absent_claims(tmp_path, monkeypatch):
    page = "<p>workflows only</p>"
    src = _write_sources(tmp_path, [{
        "name": "x", "url": "https://example.test/a",
        "tracked_claims": ["workflows", "handoff"], "page_sha256": None,
    }])
    monkeypatch.setattr(dfc, "fetch", lambda url: (page, None))
    result = dfc.run_update(src)
    assert result["updated"][0]["status"] == "repinned"
    assert "handoff" in result["updated"][0]["claims_not_found_now"]
    repinned = json.loads(src.read_text())["sources"][0]
    assert repinned["page_sha256"] == dfc.sha256(dfc.normalize(page))
    assert repinned["last_checked"] is not None


def test_normalize_strips_tags_and_collapses_whitespace():
    assert dfc.normalize("<h1>A</h1>\n\n  B  ") == "a b"
