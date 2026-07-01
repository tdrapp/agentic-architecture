# Worked example — designing a "decision with independent review" system

A concrete walk of the design checklist on ONE realistic case, mapping each choice to a pattern
(C1–C12) and to the Anthropic/OpenAI vocabulary. Domain-neutral on purpose: this shape recurs in
research assistants, incident triage, code review, underwriting, investment decisions — anywhere a
system must gather evidence, decide, and be trusted.

## The task
> "Given a request, gather evidence from several specialised sources, produce a recommended decision
> with justification, and make it trustworthy enough to act on."

## Step 0 — Do we even need an agent?
Run the checklist's escape hatch. One augmented LLM call can't do this well: the evidence is
multi-source and unstructured, the judgement is nuanced, and trust requires an independent check.
So: not a single call. But the control flow **is** predictable → build a **workflow**, not an
autonomous loop. (Anthropic: start simple; OpenAI: deterministic solution first. Verdict: workflow.)

## The pipeline (named stages)
```
intake/brief
  → pre-flight state read            (C7)   ground before proposing anything
  → routing                          [Anthropic: routing]   which sub-flow applies
  → parallel fan-out of specialists  (C1)   [Anthropic: parallelization / orchestrator-workers;
                                             OpenAI: manager / agents-as-tools]
  → synthesis (one agent fuses)      (C4/C10) invents nothing; consumes structured worker outputs
  → INDEPENDENT verification         (C2)   [Anthropic: evaluator-optimizer] argues against shipping
  → human decision point            (C12)   gate the irreversible action
  → log across persistence layers    (C6)   + encode any new lesson as a file (C5)
```

## Why each stage earns its place (and where we cut)
- **Pre-flight (C7).** Read the real current state first, or you optimise in a vacuum and contradict
  the user's own targets. Hard-block on incoherent state.
- **Routing.** Cheap classification so each sub-flow is specialised — but if there's only one kind of
  request, *cut this stage* (simplicity principle).
- **Parallel specialists (C1).** Each runs in an isolated context and returns a compact synthesis, so
  the main thread stays clean. Use the **orchestrator-workers / manager** topology: one coordinator
  keeps the single voice. (If a specialist should *own* the rest of the interaction, that's a
  **handoff** — an OpenAI-first-class alternative; see `references/openai-crosscheck.md`. Here we keep
  central control, so no handoff.)
- **Synthesis (C4/C10).** One agent fuses the workers' **structured JSON** outputs (not free prose),
  so fusion + later evals are mechanical. Any field it can't source is `null` + a documented gap.
- **Independent verification (C2).** The verifier (see `agents/architecture-reviewer.md` for the
  design-review analogue) sees the evidence and the proposal but **not** the synthesizer's narrative,
  and argues three concrete reasons not to ship. The producer never certifies itself.
- **Human gate (C12).** The one irreversible action waits for explicit human approval.
- **Log + encode (C6/C5).** Persist live state / decision record / memory separately; turn any
  postmortem into a durable guardrail or pattern, not a mental note.

## What we deliberately did NOT do
- No autonomous agent loop — control flow was predictable (avoided cost + compounding errors).
- No handoffs — we wanted one synthesised voice; central orchestration suffices.
- No extra "manager of managers" — a single coordinator + specialists is enough (cut on simplicity).

## Making it real (checklist → artefacts)
- Evals (C9): 20–50 tasks from real failures; grade the *outcome* (was the decision + invalidation
  right), not the step sequence; track `pass^k` for reliability.
- Tools (C4): each specialist's data tool returns a `data_quality` flag; test each branch.
- Dual-mode (C3): keep config filesystem-first so the same system runs interactively and behind an
  SDK/HTTP frontend.

This is the exact shape validated in a production multi-subagent system; the finance specifics are
omitted — what transfers is the *structure*, not the domain.
