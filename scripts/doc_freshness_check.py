#!/usr/bin/env python3
"""Auto-challenge tool: has the guidance this skill is grounded in moved?

The skill pins its claims to primary Anthropic + OpenAI docs. Guidance drifts. This tool fetches each
tracked doc and reports, per source, whether the *specific claims* the skill relies on are still
present — not merely whether a byte changed (a page hash flips on a typo). It answers, on demand:
"are my sources still saying what I claim they say?"

Design choices (see references/patterns.md):
- C4 (honest tools): emits structured JSON with a `_meta.data_quality` flag; an unreachable URL
  becomes `unavailable`, never a crash and never a fabricated "unchanged".
- Zero external dependencies (stdlib only) so it runs in any Python >= 3.9, anywhere.

Usage:
    python scripts/doc_freshness_check.py            # --check (default): report drift
    python scripts/doc_freshness_check.py --update    # re-pin page hashes + last_checked
    python scripts/doc_freshness_check.py --sources path/to/sources.json

Read-only: performs GET requests only (see toti-engineering references/api-safety.md).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

USER_AGENT = "agentic-architecture-doc-freshness-check/1.0 (+https://github.com/)"
FETCH_TIMEOUT_S = 20
DEFAULT_SOURCES = Path(__file__).with_name("sources.json")

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fetch(url: str) -> tuple[str | None, str | None]:
    """GET a URL. Return (text, None) on success or (None, reason) on failure. Never raises."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_S) as resp:  # noqa: S310 (https docs only)
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace"), None
    except urllib.error.HTTPError as exc:
        return None, f"http_{exc.code}"
    except urllib.error.URLError as exc:
        return None, f"url_error:{exc.reason}"
    except (TimeoutError, ConnectionError) as exc:
        return None, f"network_error:{exc}"
    except ValueError as exc:  # malformed URL
        return None, f"bad_url:{exc}"


def normalize(html_or_text: str) -> str:
    """Strip tags and collapse whitespace so claim-matching is robust to markup/formatting."""
    text = _TAG_RE.sub(" ", html_or_text)
    return _WS_RE.sub(" ", text).strip().lower()


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _missing_claims(normalized_page: str, tracked_claims: list[str]) -> list[str]:
    return [c for c in tracked_claims if c.strip().lower() not in normalized_page]


def check_source(source: dict[str, Any]) -> dict[str, Any]:
    """Return a per-source report dict. Status is one of:
    unchanged | CLAIM-MISSING (actionable) | PAGE-CHANGED (informational — dynamic pages churn) |
    unpinned | unreachable.
    """
    name = source.get("name", source.get("url", "<unnamed>"))
    url = source["url"]
    tracked = source.get("tracked_claims", [])
    pinned_hash = source.get("page_sha256")

    raw, err = fetch(url)
    if raw is None:
        return {"name": name, "url": url, "status": "unreachable", "reason": err}

    normalized = normalize(raw)
    current_hash = sha256(normalized)
    missing = _missing_claims(normalized, tracked)

    if missing:
        status = "CLAIM-MISSING"
    elif pinned_hash is None:
        status = "unpinned"
    elif current_hash != pinned_hash:
        status = "PAGE-CHANGED"
    else:
        status = "unchanged"

    return {
        "name": name,
        "url": url,
        "status": status,
        "missing_claims": missing,
        "claims_tracked": len(tracked),
        "hash_changed": pinned_hash is not None and current_hash != pinned_hash,
    }


def load_sources(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def run_check(path: Path) -> dict[str, Any]:
    data = load_sources(path)
    sources = data.get("sources", [])
    reports = [check_source(s) for s in sources]

    reachable = [r for r in reports if r["status"] != "unreachable"]
    if not sources:
        data_quality = "unavailable"
    elif not reachable:
        data_quality = "unavailable"
    elif len(reachable) < len(sources):
        data_quality = "partial"
    else:
        data_quality = "ok"

    def n(status: str) -> int:
        return sum(1 for r in reports if r["status"] == status)

    return {
        "mode": "check",
        "summary": {
            "sources": len(sources),
            "unchanged": n("unchanged"),
            "claim_missing": n("CLAIM-MISSING"),   # actionable drift: a tracked claim disappeared
            "page_changed": n("PAGE-CHANGED"),     # informational only: many doc pages are dynamic (SPA/PDF), the hash churns
            "unpinned": n("unpinned"),
            "unreachable": n("unreachable"),
        },
        "sources": reports,
        "_meta": {"tool": "doc_freshness_check", "checked_at": _now_iso(), "data_quality": data_quality},
    }


def run_update(path: Path) -> dict[str, Any]:
    data = load_sources(path)
    sources = data.get("sources", [])
    updated: list[dict[str, Any]] = []
    for s in sources:
        raw, err = fetch(s["url"])
        if raw is None:
            updated.append({"name": s.get("name"), "status": "unreachable", "reason": err})
            continue
        normalized = normalize(raw)
        missing = _missing_claims(normalized, s.get("tracked_claims", []))
        # Do NOT pin a claim that is not currently present — surface it instead of silently blessing it.
        s["page_sha256"] = sha256(normalized)
        s["last_checked"] = _now_iso()
        updated.append(
            {"name": s.get("name"), "status": "repinned", "claims_not_found_now": missing}
        )
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    reachable = [u for u in updated if u["status"] == "repinned"]
    data_quality = "ok" if len(reachable) == len(sources) and sources else (
        "partial" if reachable else "unavailable"
    )
    return {
        "mode": "update",
        "updated": updated,
        "_meta": {"tool": "doc_freshness_check", "checked_at": _now_iso(), "data_quality": data_quality},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check whether tracked Anthropic/OpenAI docs still support this skill's claims.")
    parser.add_argument("--check", action="store_true", help="Report drift (default mode; flag is explicit for clarity).")
    parser.add_argument("--update", action="store_true", help="Re-pin page hashes + last_checked instead of checking.")
    parser.add_argument("--sources", type=Path, default=DEFAULT_SOURCES, help="Path to sources.json.")
    args = parser.parse_args(argv)

    if not args.sources.exists():
        print(json.dumps({"error": f"sources file not found: {args.sources}", "_meta": {"data_quality": "unavailable"}}, indent=2))
        return 2

    result = run_update(args.sources) if args.update else run_check(args.sources)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
