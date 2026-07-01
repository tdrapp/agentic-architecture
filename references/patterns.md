# Pattern catalog — agentic architecture

Cross-project patterns for Claude agent systems. Each is stated as **What / Why it transfers /
Anthropic grounding / Implementation note**. Grounding is labelled by certainty:
`[verified-doc]` (confirmed in current Anthropic docs — pin the version, options drift),
`[idiomatic]` (consistent with published Anthropic guidance), `[house]` (validated in a real
project, generalises well, but not official doctrine).

---

## C1 — Subagent context isolation (wide-then-narrow)

**What.** When the goal of a search/inventory/audit is a *synthesis you will reason about* (not raw
rows you act on one by one), spawn a subagent that absorbs the noisy tool output and returns only a
compact result. The main thread stays a clean working memory.

**Why it transfers.** The main agent's context is the scarcest resource in any non-trivial system.
Any project with wide exploration (grep across a codebase, enumerate an API, compare two datasets,
"what's in there") benefits identically.

**Grounding.** `[verified-doc]` Subagents exist precisely for context management + parallelization;
this is Anthropic's stated rationale for the orchestrator-workers workflow.

**Implementation note.** Calibrate: if the work is iterative (run → see → adjust, each output
reshaping the next move), stay inline — delegation overhead only pays when you can hand a
self-contained brief whose result you use as-is. Give the subagent a crisp brief and ask for a
bounded report ("under 200 words", "a punch list").

---

## C2 — Generation / verification separation

**What.** Whatever produces a decision must not also certify it. Add an **independent** verifier that
reads the raw evidence and the proposed output — but NOT the builder's persuasive narrative — and
argues the other side (e.g. "three concrete reasons NOT to ship this", each anchored in a measurable
signal).

**Why it transfers.** A model grading its own work rationalises it. A cold, evidence-only second
pass catches the failure the author is blind to. Applies to any decision/QA/review pipeline, not
just finance.

**Grounding.** `[verified-doc]` This is the **evaluator-optimizer** workflow. `[house]` The
refinement that the verifier must be *independent* of the generator (different context, no access to
the builder's rationale) is a validated discipline that materially changes outcomes.

**Implementation note.** Give the verifier the artefacts + the raw inputs, withhold the synthesis
prose. Have it re-derive one load-bearing number itself. Make it a hard, un-skippable stage — not
advisory text the generator can wave away.

---

## C3 — Filesystem-first dual-mode (CLI ↔ Agent SDK)

**What.** Keep configuration as files — `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/*` — so
the SAME source of truth runs both interactively (Claude Code) and programmatically (Agent SDK)
behind a web/CLI/Slack frontend. Add an SDK entrypoint; change nothing about the interactive path.

**Why it transfers.** Any Claude Code workspace worth building will eventually want a
programmatic/hosted surface. If config lives in files from day one, that later step is additive, not
a rewrite.

**Grounding.** `[verified-doc]` The Agent SDK loads filesystem config via `setting_sources`
(Python) / `settingSources` (TS); Skills are filesystem-only (no programmatic registration);
subagents can be filesystem OR programmatic, and filesystem definitions serve both modes. **Pin the
version:** the default for `setting_sources` has changed across releases — set it explicitly rather
than trusting the default.

**Implementation note.** See `#sdk-packaging` below for the concrete refactor.

---

## C4 — Structured tools + uncertainty flag + no-invention

**What.** Every tool returns structured output plus an explicit quality/uncertainty field (e.g.
`ok | partial | proxy | stale | unavailable`). Anything other than `ok` is surfaced in the answer,
not hidden. A missing value is `null` + a documented gap — never a fabricated number.

**Why it transfers.** Silent fallback is how tool-using agents quietly lie. A quality flag turns a
degraded source into a visible caveat the user can weigh. Universal to any retrieval/tool-use system.

**Grounding.** `[verified-doc]` Tool design (the agent-computer interface) is one of Anthropic's
three core principles. `[house]` The specific `data_quality` flag + "documented gap beats a guess"
rule is a validated convention.

**Implementation note.** Test **each tool branch** before wiring — degraded/edge paths are where
silent bugs hide (a wrong dataset name, an off-by-100 unit). Prefer authoritative APIs over scraping;
flag scraping as a last-resort fallback.

---

## C5 — Encode discipline as files, not prompts-of-the-moment

**What.** When a lesson emerges (a postmortem, a correction the user had to make twice), encode it as
a durable artefact — a skill, a guardrail rule, a reusable pattern file, a hook — so it fires
automatically next time. A chat correction evaporates; a file compounds.

**Why it transfers.** This is how a system gets better per use instead of repeating mistakes. The
switching cost / accumulated methodology is also the only real moat for an agent product.

**Grounding.** `[verified-doc]` Skills are Anthropic's mechanism for reusable *procedural* knowledge
loaded on demand. `[house]` The "turn each postmortem into a guardrail/pattern rather than a mental
note" habit is a validated compounding loop.

**Implementation note.** Name the rule, explain the *why* (smart models generalise from reasons, not
from ALL-CAPS MUSTs), and cite the incident that motivated it so future readers trust it.

---

## C6 — Layered persistence / just-in-time memory

**What.** Separate distinct memory roles, each specific, timestamped (absolute dates), retrievable,
de-duplicated: **live state** (the source of truth read first), **immutable decision records** (why,
at a point in time), **per-entity learnings** (chronological priors), **cross-session memory index**
(one concise fact + pointer). Update in place; don't append duplicates.

**Why it transfers.** Any long-lived agent needs to recall without re-reading everything, and to
distinguish "what is true now" from "why we decided X in the past". Conflating them rots the state.

**Grounding.** `[verified-doc]` Matches Anthropic's just-in-time / memory-tool pattern (retrieve the
minimum needed, when needed). `[house]` The four-role split is a validated structure.

**Implementation note.** Keep a one-line memory index that points to detail files. On any state
change, update every affected layer in the same turn so they never drift.

---

## C7 — Pre-flight state read (ground first, conclude second)

**What.** Before the system emits any number, level, or recommendation, a mandatory pre-flight step
reads the real current state and states what it contains; a coherence/drift check can hard-block on
incoherent state.

**Why it transfers.** Optimising in a vacuum produces answers that contradict the user's own stated
targets. Distinguish three questions before acting: *what is currently held* (read), *is the current
structure defective* (diagnose vs targets), *what is the from-scratch optimum* (re-plan).

**Grounding.** `[house]` Validated from a real failure (recommending changes before reading the
targets file). Consistent with `[idiomatic]` read-before-write / memory-first guidance.

**Implementation note.** Wire the state read into the entry gate so it can't be skipped under time
pressure; surface drift/staleness to the user before sizing anything.

---

## C8 — Progressive disclosure

**What.** Load a resource only when its trigger fires. Metadata (name + description) always in
context; the skill/doc body only when it triggers; heavy references only when pointed to.

**Why it transfers.** Keeps the always-on context small and cheap while making deep knowledge
available on demand. The core mechanism behind Skills.

**Grounding.** `[verified-doc]` Skills' three-level loading (metadata → body → bundled resources).
`[idiomatic]` Anthropic context-engineering guidance.

**Implementation note.** Keep the always-loaded description tight and specific (it is the trigger).
Put large reference material behind clear pointers with a table of contents.

---

## Orchestration shape (composition)

A robust default that composes the above into one pipeline:

```
intake / brief
  → pre-flight state read (C7)
  → routing (which sub-flow)                      [Anthropic: routing]
  → parallel fan-out of specialised subagents (C1) [Anthropic: parallelization / orchestrator-workers]
  → synthesis (one agent fuses, invents nothing, C4)
  → INDEPENDENT verification / red-team (C2)       [Anthropic: evaluator-optimizer]
  → human decision point (transparency)
  → log across persistence layers (C6) + encode any new lesson (C5)
```

Every stage earns its place against principle 1 (simplicity); cut any that doesn't improve the
output.

---

## SDK packaging {#sdk-packaging}

Concrete dual-mode refactor for an existing Claude Code workspace (see C3).

**Keep identical:** `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/*`, tools, state files.

**Add (additive only):**
- An SDK entrypoint (e.g. `sdk_server.py`) that wraps the SDK's `query()` loop in a small
  web/CLI frontend and sets `setting_sources=["user","project"]` **explicitly** so the SDK loads the
  same CLAUDE.md + subagents + skills.
- A task runner (`Makefile`) with two targets: `run-cli` (interactive `claude`, unchanged) and
  `run-sdk` (serve the SDK app).
- An **optional** dependency group for the SDK deps, so the interactive path needs nothing new.

**Tools — Bash vs MCP.** Keep tools as Bash-invoked scripts for dual-mode simplicity (works in both
runtimes unchanged). Wrap them as an in-process MCP server (`create_sdk_mcp_server()`) only when you
need lower latency / typed I/O at scale, or cross-product reuse. `[verified-doc]`

**Hosted vs self-hosted.** Self-host the SDK loop (FastAPI around `query()`) for file-heavy, local,
personal use. Consider Anthropic **Managed Agents** (hosted REST + server-side session state) when
you want no runtime ops. `[verified-doc]` — confirm current beta headers/option names against the
docs, they change.

**Verify before claiming done.** `uv sync --extra sdk && make run-sdk`; confirm the SDK actually
loaded the filesystem config (subagents + skills visible); reconfirm the `setting_sources` option
name/values against the installed SDK version.
