# Anthropic ↔ OpenAI cross-check

Why this file exists: the pattern catalog is Anthropic-anchored. To claim a practice is *durable*
(worth codifying) rather than *vendor-idiomatic* (a framework choice), it helps to see where the two
leading labs **converge** — convergence is the strongest signal a practice is fundamental — and where
they **diverge**, which flags a genuine design choice you should make consciously.

Certainty labels match `patterns.md`: `[verified-doc]` (confirmed in current primary docs — pin the
version, guidance drifts), `[idiomatic]` (consistent with published guidance), `[house]` (validated
in a real project; generalises; not official doctrine).

Sources are listed at the bottom; re-check them with `scripts/doc_freshness_check.py`.

---

## Convergence — the durable practices (safe to codify)

Where Anthropic and OpenAI independently say the same thing, treat it as a fundamental, not a fashion.

| Practice | Anthropic framing | OpenAI framing | Take |
|---|---|---|---|
| **Don't build an agent unless you must** | Start with one augmented LLM call; add agentic complexity only when it demonstrably helps `[verified-doc]` | "Agents suit workflows where deterministic/rule-based approaches fall short"; otherwise "a deterministic solution may suffice" `[verified-doc]` | Gate every agent against a simpler baseline. This is the #1 shared principle. |
| **Single-agent first, split on real pressure** | Prefer the simplest composition; add stages only if they improve output `[verified-doc]` | "Maximize a single agent's capabilities first"; split on prompt-branch explosion or **tool overload** — *not* raw count (">15 distinct tools ok, <10 overlapping fail") `[verified-doc]` | Split on measured failure, not anticipation. |
| **Central-coordinator pattern** | **Orchestrator-workers**: a central LLM decomposes, delegates, synthesises `[verified-doc]` | **Manager / "agents as tools"**: a central LLM delegates via tool calls and synthesises `[verified-doc]` | Same shape, two names. This is the default multi-agent topology on both sides. |
| **Layered guardrails** | Tool craftsmanship + transparency as core principles `[verified-doc]` | Explicit layered defense: relevance/safety/PII/moderation + **tool safeguards** (rate each tool on read-vs-write, reversibility, impact) + output validation `[verified-doc]` | See pattern C12 — OpenAI's taxonomy is the more explicit checklist; adopt it. |
| **Human-in-the-loop for irreversible actions** | Human checkpoints + explicit stopping conditions in autonomous agents `[verified-doc]` | HITL triggers: exceeding failure thresholds, and high-risk/irreversible actions (payments, deletes) `[verified-doc]` | Gate irreversible side-effects behind a human. Matches this repo's "never auto-execute" rule. |
| **Evals are the baseline discipline** | Tasks/graders/transcripts/outcomes; grade outcomes not steps; `pass^k` `[verified-doc]` | Evals-first model selection: prototype on the most capable model, downgrade where evals still pass `[verified-doc]` | See pattern C9. Both treat evals as non-optional before production. |
| **Keep components composable** | "Simple, composable patterns rather than complex frameworks" `[verified-doc]` | Code-first primitives (agents, tools, handoffs) you compose in code `[verified-doc]` | Avoid heavyweight declarative frameworks; compose small pieces. |
| **Tools are an interface to design** | The agent-computer interface deserves prompt-level care `[verified-doc]` | Explicit function/param descriptions; say *when not* to call; `strict:true` Structured Outputs `[verified-doc]` | See patterns C4, C10. |

## Divergence — conscious design choices (flag, don't paper over)

| Axis | Anthropic | OpenAI | How to choose |
|---|---|---|---|
| **Control transfer** | Taxonomy has **no handoff primitive**; an orchestrator *retains* control and synthesises worker output `[verified-doc]` | **Handoffs** are first-class: a peer agent takes over one-way, carrying conversation state (a handoff *is* a tool) `[verified-doc]` | Default to orchestrator-retains-control when you need one voice / one synthesis. Use handoffs (decentralised) when a specialist should *own* the rest of the interaction and no central synthesis is needed. |
| **Control-flow expression** | A spectrum of composable **workflows** (chaining, routing, parallelization, evaluator-optimizer) vs autonomous agents `[verified-doc]` | **Code-first / non-declarative**: you express control flow in Python; no graph DSL `[verified-doc]` | Both reject heavy DSLs. If on Claude, the workflow vocabulary is your design language; if on OpenAI SDK, it's plain code + handoffs. |
| **Cross-session memory** | **Memory tool** API (`memory_20250818`) + filesystem/just-in-time retrieval `[verified-doc]` (pin the id) | **Sessions** primitive for persistent memory `[verified-doc]` | See pattern C11. Both externalise memory; the mechanism is vendor-specific — keep your *state model* portable (C6) and treat the API as an adapter. |
| **Tracing/observability** | Via SDK + your own logging | **Tracing on by default** (disabled under ZDR) `[verified-doc]` | If on OpenAI, you get tracing free; on Claude, wire your own transcript logging for evals (C9). |

---

## The one-paragraph synthesis

The convergent core — *gate agents against a simpler baseline, prefer a single agent then split on
measured tool-overload, use a central orchestrator/manager, layer guardrails, put a human on
irreversible actions, and run evals before production* — is vendor-independent and safe to build on.
The real fork is **handoffs vs orchestrator-retains-control**: a decentralised topology (OpenAI's
first-class handoff) versus a coordinator that keeps one voice (Anthropic's orchestrator-workers).
Choose it deliberately per use case; don't inherit it from whichever SDK you happened to start with.

---

## Sources
OpenAI `[verified-doc]`:
- A Practical Guide to Building Agents (PDF) — https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf
- Agents SDK — https://openai.github.io/openai-agents-python/
- Function calling — https://developers.openai.com/api/docs/guides/function-calling

Anthropic `[verified-doc]`:
- Building Effective Agents — https://www.anthropic.com/engineering/building-effective-agents
- Demystifying Evals for AI Agents — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Effective Context Engineering — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Memory tool — https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
