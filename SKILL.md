---
name: agentic-architecture
description: "Best practices for DESIGNING and STRUCTURING Claude agent systems — anchored on Anthropic's 'Building Effective Agents' taxonomy (workflows vs agents; augmented LLM; routing, parallelization, orchestrator-workers, evaluator-optimizer) and Claude Code / Agent SDK guidance, extended with validated cross-project patterns. Use this whenever architecting a multi-agent or subagent system, deciding workflow-vs-autonomous-agent, structuring skills/subagents/tools, wiring context isolation, adding a verification/red-team pass, encoding lessons as reusable memory, or packaging a Claude Code workspace as an Agent SDK app (dual-mode). Trigger even if the user only says 'how should I structure this agent', 'should this be a subagent or a tool', 'how do I split this into agents', 'design the orchestration', or 'turn my Claude Code repo into a real app'. NOT for generic application code (use toti-engineering) or a specific product stack (use genai-saas)."
---

# Agentic Architecture

Reusable, Anthropic-grounded patterns for building Claude agent systems that stay simple, transparent, and cheap to run — and that compound across sessions. Anchored on Anthropic's *Building Effective Agents* framework, extended with patterns validated in production personal projects.

## How to use this skill

1. **Start from the taxonomy below** to name what you're building — a *workflow* (predefined code paths) or an *agent* (the model directs its own process). Most robust systems are workflows, or agents with workflow-shaped internals.
2. **Run the design checklist** before writing any orchestration code. It forces the "start simple, add complexity only when it demonstrably helps" discipline.
3. **Pull specific patterns** from `references/patterns.md` (context isolation, generation/verification split, filesystem-first dual-mode, tool honesty, memory-as-files, orchestration shape). Each carries its Anthropic grounding + a why-it-transfers note.

## The Anthropic anchor — *Building Effective Agents*

Source: Anthropic, "Building Effective Agents" (anthropic.com/engineering/building-effective-agents). Represent it faithfully; this taxonomy is the shared vocabulary.

**Workflows vs agents.** *Workflows* orchestrate LLMs and tools through **predefined code paths**. *Agents* let the LLM **dynamically direct its own process and tool use**. Prefer the most predictable form that solves the problem.

**The building block — the augmented LLM.** An LLM enhanced with **retrieval, tools, and memory**, generating its own queries, selecting tools, and deciding what to retain. Everything below composes this block.

**The five workflow patterns:**
- **Prompt chaining** — decompose into sequential steps, each processing the previous output; add programmatic checkpoints between steps.
- **Routing** — classify the input and dispatch to a specialised follow-up. Enables separation of concerns and per-route optimisation.
- **Parallelization** — run tasks simultaneously and aggregate. Two variants: *sectioning* (independent subtasks in parallel) and *voting* (same task run several times for diverse outputs).
- **Orchestrator-workers** — a central LLM breaks a task down, delegates to workers, and synthesises their results (task decomposition is dynamic, not fixed).
- **Evaluator-optimizer** — one LLM generates, a second evaluates and feeds back in a loop for iterative refinement.

**Autonomous agent.** Begins from a command or discussion; once the task is clear, it **plans and operates independently** with environmental feedback, optional human checkpoints, and explicit stopping conditions.

**Three core principles (non-negotiable):**
1. **Simplicity** — the fewest moving parts that work.
2. **Transparency** — explicitly show the agent's planning steps.
3. **Tool craftsmanship** — the agent-computer interface (tool docs + testing) deserves as much care as the prompts.

**When NOT to use an agent.** Agents add cost and compounding-error risk. Start with a single optimised LLM call + retrieval + in-context examples; add agentic complexity **only when it demonstrably improves outcomes**. Many production systems are one good workflow, not an autonomous agent.

## Also cross-checked against OpenAI

Where Anthropic and OpenAI independently agree, treat the practice as fundamental (not fashion):
gate agents against a simpler baseline; **single-agent first, split on measured tool-overload** (not
raw count — ">15 distinct tools ok, <10 overlapping fail"); a central **orchestrator/manager**;
**layered guardrails** + **human-in-the-loop on irreversible actions**; **evals-first**. The one real
divergence to choose consciously: OpenAI makes **handoffs** (peer control transfer) a first-class
primitive, whereas Anthropic keeps an orchestrator in control. Full table + sources in
`references/openai-crosscheck.md`.

## Design checklist (run at project start)

Work top to bottom; stop as soon as a simpler tier solves the problem.

1. **Can one augmented LLM call do it?** (prompt + retrieval + examples + a couple of tools). If yes, stop here — do not build an agent.
2. **If not, is the control flow predictable?** If yes, build a **workflow** (chaining / routing / parallelization / orchestrator-workers) in code, not an autonomous agent. Reserve autonomy for genuinely open-ended tasks with good feedback signals.
3. **Draw the pipeline as named stages** — e.g. `intake → routing → parallel fan-out → synthesis → independent verification → log`. Each stage = one responsibility.
4. **Assign context boundaries.** Which stages should run in an isolated sub-context that returns only a synthesis (to protect the main thread from raw tool output)? See pattern C1.
5. **Separate generation from verification.** Whatever produces the decision must NOT also bless it — add an independent evaluator/red-team that sees the raw evidence, not the builder's narrative. See pattern C2.
6. **Design the tools as an interface.** Structured outputs, an explicit uncertainty/quality flag, and a no-invention rule (return `null` + a documented gap, never a guess). Test each tool branch. See pattern C4.
7. **Decide what must persist and where.** Live state vs immutable record vs cross-session memory. Encode recurring discipline as files (skills / guardrails / patterns), not as prompt-of-the-moment. See patterns C5–C6.
8. **Ground before acting.** A pre-flight step reads real state before the system emits any number/decision. See pattern C7.
9. **Plan for two runtimes from day one.** Keep config filesystem-first (`CLAUDE.md`, `.claude/agents/*.md`, skills) so the same source serves interactive Claude Code AND the Agent SDK. See pattern C3 + `references/patterns.md#sdk-packaging`.
10. **Justify every added stage against principle 1 (simplicity).** If a stage doesn't demonstrably improve the output, cut it.

## Pattern catalog

Read `references/patterns.md` for the full catalog. Each pattern is stated as **what / why it transfers / Anthropic grounding**, with a concrete implementation note.

| Need | Pattern |
|---|---|
| Keep the main context clean during wide exploration | C1 — Subagent context isolation (wide-then-narrow) |
| Stop motivated reasoning in a decision pipeline | C2 — Generation/verification separation |
| One codebase, both interactive CLI and SDK app | C3 — Filesystem-first dual-mode |
| Tools that never silently lie | C4 — Structured tools + uncertainty flag + no-invention |
| Lessons that compound across sessions | C5 — Encode discipline as files, not prompts |
| Recall without re-reading everything | C6 — Layered persistence / just-in-time memory |
| Don't optimise in a vacuum | C7 — Pre-flight state read (ground first) |
| Load only what the moment needs | C8 — Progressive disclosure |
| Measure that it works + catch regressions | C9 — Evals as a first-class loop |
| Fuse many workers without regex-parsing prose | C10 — Structured subagent output schemas |
| Remember across sessions, portably | C11 — Filesystem layers vs the Memory tool API |
| Defend in layers; gate irreversible actions | C12 — Layered guardrails + human-in-the-loop |

## Tools

`scripts/doc_freshness_check.py` — a zero-dependency script that fetches the primary Anthropic + OpenAI
docs this skill is grounded in (`scripts/sources.json`) and reports whether the **specific claims** the
skill relies on are still present. Run it when the user asks whether best practices have evolved, or
before publishing/citing a mechanism:
```
python scripts/doc_freshness_check.py            # report drift (claim-missing / page-changed / unreachable)
python scripts/doc_freshness_check.py --update    # re-pin hashes after verifying claims
```
It dogfoods C4: structured JSON output with a `_meta.data_quality` flag; an unreachable source becomes
`unavailable`, never a fabricated "unchanged".

Runnable proofs (not just prose): `examples/minimal_agent/run.py` is a zero-dep reference of the
orchestration shape (orchestrator → workers → independent verifier, C1/C2/C4/C10); `evals/run_evals.py`
is a real eval loop (pattern C9) over `evals/tasks.json`.

## Optional reviewer subagent

`agents/architecture-reviewer.md` is an independent, skeptical reviewer that runs the design checklist
as a cold pass and argues *against* added complexity (dogfooding C2). Use it to review a proposed
design — the agent that produced a design should not be the one that blesses it. Usable in Claude Code
or wired via the Agent SDK `agents=` parameter.

## What this skill is NOT

- **Not general reasoning directives.** "Never invent, say I-don't-know, cite sources" belong in the
  consuming project's guardrails, not here. This skill assumes them; it doesn't restate them.
- **Not code quality.** Planning discipline, refactoring, quality gates, git conventions live in
  `toti-engineering`.
- **Not a product stack.** Framework/stack specifics live in a stack skill (e.g. `genai-saas`).
- **Scope = design & structure of agent systems.** How to shape, split, verify, ground, and package
  them — nothing more.

## A caution on certainty

When you cite a mechanism as "Anthropic best practice", distinguish what is **verified in current docs** (taxonomy, principles, SDK option names — which drift across versions, so pin them) from what is **idiomatic guidance** and from a team's **own validated discipline**. Never present house conventions as official Anthropic doctrine; label the source.
