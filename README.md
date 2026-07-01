# agentic-architecture

> A Claude Skill for engineering agentic systems — every pattern sourced to Anthropic & OpenAI docs, certainty-labelled, and kept honest by a bundled drift-checker.

![ci](https://github.com/tdrapp/agentic-architecture/actions/workflows/ci.yml/badge.svg)

Reusable patterns for building agent systems that stay **simple, transparent, and cheap to run**.
Grounded in primary Anthropic + OpenAI docs; extracted from a real multi-subagent project — used, not theoretical.

## Why
- **Dual-vendor, not vibes** — separates the durable core (where Anthropic & OpenAI agree) from design choices you make consciously.
- **Labelled certainty** — every claim tagged `[verified-doc]` / `[idiomatic]` / `[house]`. No house convention dressed as vendor doctrine.
- **Self-challenging, not frozen** — `doc_freshness_check.py` re-checks the cited docs on demand; weekly CI opens an issue on drift.
- **Shown, not told** — a runnable reference agent + a real eval loop + tests, not just prose.

## Patterns (C1–C12)
`references/patterns.md` — each: *what / why it transfers / grounding (labelled) / how*.

| # | Pattern | # | Pattern |
|---|---|---|---|
| C1 | Subagent context isolation | C7 | Pre-flight state read |
| C2 | Generation ↔ verification split | C8 | Progressive disclosure |
| C3 | Filesystem-first dual-mode | C9 | Evals as a loop |
| C4 | Honest tools (quality flag, no-invention) | C10 | Structured subagent outputs |
| C5 | Encode discipline as files | C11 | Memory: filesystem vs Memory-tool API |
| C6 | Layered persistence | C12 | Layered guardrails + human-in-the-loop |

Cross-vendor map: `references/openai-crosscheck.md`. Authoring/packaging: `references/authoring-and-packaging.md`.

## Run
```bash
python examples/minimal_agent/run.py      # reference: orchestrator → workers → independent verifier
python evals/run_evals.py --demo          # eval loop (pass^k) on design-judgment tasks
python scripts/doc_freshness_check.py     # are the cited docs still saying what we claim?
uv run --with pytest python -m pytest tests/ -q   # 15 tests, no network
```

## Structure
```
SKILL.md                          the skill: taxonomy · checklist · catalog · scope
references/   patterns.md · openai-crosscheck.md · authoring-and-packaging.md
scripts/      doc_freshness_check.py · sources.json      (zero-dep drift tool)
examples/     minimal_agent/run.py · reference-agent-design.md
evals/        run_evals.py · tasks.json · tasks/design-judgment.md
agents/       architecture-reviewer.md                   (optional independent reviewer)
tests/ · .github/workflows/ (ci + weekly doc-freshness)
```

## Not this
- **Not general reasoning rules** (no-invention, say-I-don't-know) — those live in a project's guardrails; assumed here.
- **Not code quality / git** — separate engineering skill.
- **Not a product stack.**
- Scope = **design, structure, and packaging of agent systems**. Guidance drifts — labels + the drift tool keep it honest.

## Sources
Anthropic: Building Effective Agents · Demystifying Evals · Effective Context Engineering · Skills · Agent SDK · Memory tool.
OpenAI: A Practical Guide to Building Agents · Agents SDK · Function calling. URLs in `scripts/sources.json`; re-verify with the drift tool.

## Install
```bash
cp -r agentic-architecture ~/.claude/skills/     # user-global, or <repo>/.claude/skills/ per project
```
Triggers on design/orchestration questions ("how should I structure this agent?").

MIT — see [LICENSE](LICENSE) · [DISCLAIMER](DISCLAIMER.md) · [CONTRIBUTING](CONTRIBUTING.md). Not official Anthropic/OpenAI doctrine.
