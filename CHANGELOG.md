# Changelog

All notable changes to this skill. Format follows [Keep a Changelog](https://keepachangelog.com);
this project uses date-based, human-readable entries.

## [0.2.0] — 2026-07-01
Showcase release: cross-vendor grounding, tooling, and packaging.

### Added
- `references/openai-crosscheck.md` — Anthropic↔OpenAI convergence/divergence (handoffs, guardrail
  taxonomy, tool-overload heuristic, evals-first), so durable practices are separated from
  vendor-idiomatic ones.
- Frontier patterns **C9–C12** in `references/patterns.md`: evals-as-a-loop, structured subagent
  output schemas, cross-session memory (filesystem vs Memory tool API), layered guardrails + HITL.
- `scripts/doc_freshness_check.py` + `scripts/sources.json` — zero-dependency tool that checks whether
  the primary docs still support the skill's tracked claims (auto-challenge on doc drift).
- `tests/` — no-network unit tests for the tool; `.github/workflows/ci.yml` (ruff + pytest).
- `agents/architecture-reviewer.md` — optional independent design-review subagent (dogfoods C2).
- `references/authoring-and-packaging.md`, `examples/reference-agent-design.md`, `evals/`.
- Repo meta: `README`, `LICENSE` (MIT), `DISCLAIMER`, `CONTRIBUTING`, this changelog.

### Changed
- `SKILL.md` — added the OpenAI cross-check anchor, the C9–C12 catalog rows, a Tools section, a
  reviewer-subagent pointer, and a sharpened "what this is NOT" scope.

## [0.1.0] — earlier
- Initial skill: *Building Effective Agents* taxonomy, design checklist, pattern catalog C1–C8 with
  `[verified-doc]/[idiomatic]/[house]` certainty labels, SDK dual-mode packaging.
