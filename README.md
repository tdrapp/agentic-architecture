# agentic-architecture

> A Claude Skill for engineering agentic systems — every pattern sourced to Anthropic & OpenAI docs,
> with a built-in tool that checks whether that guidance still holds.

Reusable, dual-vendor-grounded patterns for building agent systems that stay simple, transparent, and
cheap to run — and that compound across sessions. Grounded in primary **Anthropic + OpenAI** docs
(every claim carries a certainty label), and **dogfooded** in a production multi-subagent system the
author runs daily. Not a CV project — the copy you read is the copy that runs.

![ci](https://github.com/tdrapp/agentic-architecture/actions/workflows/ci.yml/badge.svg)

## Why it exists
- Most "how to build agents" advice is vendor-idiomatic or vibes. This separates the **durable** core
  (where Anthropic and OpenAI independently agree) from **design choices** you should make consciously.
- It turns hard-won, postmortem-driven lessons into a checklist + a pattern catalog you can apply to
  the next system instead of relearning them.
- **Self-challenging, not frozen (the real edge).** A bundled tool (`doc_freshness_check.py`)
  re-checks the skill's claims against the *current* Anthropic & OpenAI docs on demand, and every
  pattern layers expert judgment (a labelled `[house]`/`[idiomatic]`/`[verified-doc]` synthesis) on top
  of the raw docs — so the guidance stays at the frontier and honest about drift, instead of a
  one-time snapshot that silently rots.

## Use cases
- Design a multi-agent / subagent system without over-engineering it.
- Decide **workflow vs autonomous agent**, and **single-agent vs split**.
- Add an independent verification/red-team pass to a decision pipeline.
- Make tools honest (quality flags, no silent fallback) and outputs structured.
- Package a Claude Code workspace as an Agent SDK app (dual-mode) without a rewrite.
- Check, on demand, whether the best practices this skill cites have drifted.

## What's inside
```
SKILL.md                         # the skill: taxonomy, design checklist, pattern catalog, scope
references/
  patterns.md                    # C1–C12, each: what / why it transfers / grounding (labelled) / how
  openai-crosscheck.md           # Anthropic ↔ OpenAI convergence & divergence (handoffs, guardrails, evals)
  authoring-and-packaging.md     # how to write a SKILL.md and package it as a credible repo
scripts/
  doc_freshness_check.py         # zero-dep tool: are the cited docs still saying what we claim?
  sources.json                   # the pinned primary sources it tracks
agents/architecture-reviewer.md  # optional independent design-reviewer subagent (dogfoods C2)
examples/reference-agent-design.md  # the checklist walked end-to-end on one realistic case
evals/                           # design-judgment tasks (grade outcomes, pass^k)
tests/                           # no-network unit tests for the tool
```

## The patterns
C1 context isolation · C2 generation/verification separation · C3 filesystem-first dual-mode ·
C4 honest tools (quality flag + no-invention) · C5 encode discipline as files · C6 layered persistence ·
C7 pre-flight state read · C8 progressive disclosure · **C9 evals as a loop** ·
**C10 structured subagent outputs** · **C11 memory: filesystem vs Memory-tool API** ·
**C12 layered guardrails + human-in-the-loop**. Each carries a certainty label: `[verified-doc]`
(confirmed in current primary docs — pin the version), `[idiomatic]`, or `[house]` (validated in a
real project; not vendor doctrine).

## Tools
```
python scripts/doc_freshness_check.py            # report drift vs the pinned sources
python scripts/doc_freshness_check.py --update    # re-pin after verifying claims
```
Emits structured JSON with a `data_quality` flag; an unreachable source is reported as `unavailable`,
never a fabricated "unchanged".

## What this is NOT
- **Not general reasoning directives** (no-invention, say-I-don't-know) — those belong in a project's
  guardrails; this skill assumes them.
- **Not code quality / git discipline** — that's a separate engineering skill.
- **Not a product/framework stack.**
- **Scope = the design and structure of agent systems**, and how to package one.
- Guidance drifts: SDK options and schemas change. Labels + `doc_freshness_check.py` exist so you
  never present a stale or house convention as official doctrine.

## Grounding & sources
Anthropic: Building Effective Agents · Demystifying Evals for AI Agents · Effective Context
Engineering · Agent Skills docs · Agent SDK overview · Memory tool. OpenAI: A Practical Guide to
Building Agents · Agents SDK · Function calling. Exact URLs live in `scripts/sources.json` and each
reference file; run the freshness tool to re-verify.

## Install & use
Copy into your Claude config so Claude auto-triggers it:
```
cp -r agentic-architecture ~/.claude/skills/        # user-global (all projects)
# or into <repo>/.claude/skills/ for a single project
```
Then just describe what you're building ("how should I structure this agent?") — the skill triggers on
design/orchestration questions.

## Development
```
uv run --with pytest python -m pytest tests/ -q     # or: pip install pytest ruff && pytest tests/
ruff check .
```

## License & disclaimer
[MIT](LICENSE). For educational/reference use — see [DISCLAIMER](DISCLAIMER.md); nothing here is
official Anthropic or OpenAI doctrine. Contributions: see [CONTRIBUTING](CONTRIBUTING.md).
