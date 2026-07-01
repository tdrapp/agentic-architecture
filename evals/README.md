# Evals

This skill is a body of *design judgment*. These evals check that the judgment it encodes is applied
correctly — they double as regression tests for the skill's guidance and as trigger tests for its
description.

## Philosophy (sourced)
- **Tasks / graders / transcripts / outcomes.** Each eval task has an input and a success criterion;
  a grader scores the response. `[verified-doc]` Anthropic, "Demystifying Evals for AI Agents"
  (https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
- **Grade outcomes, not step sequences.** Reward reaching the right verdict, not following a fixed
  path — an agent that finds a valid alternative route must not be penalised. `[verified-doc]`
- **Reliability metrics.** `pass@k` (≥1 success in k tries) vs `pass^k` (all k succeed). For judgment
  we care about `pass^k` — the guidance must hold every time, not on average. `[verified-doc]`
- **Evals-first, both labs.** Prototype on the strongest model; keep guidance only where evals still
  pass. `[verified-doc]` OpenAI, "A Practical Guide to Building Agents".

## What's here
- `tasks/design-judgment.md` — hand-written tasks: an input scenario, the success criterion, and the
  expected verdict. These are graded by a human (or a model grader) reading the response against the
  criterion; they are intentionally about *judgment*, which resists a pure code grader.

## How to run
These are model/human-graded tasks, not code tests (the code tests live in `../tests/`). To run one:
paste the task's **input** into a Claude session where this skill is available, then check the
response against the task's **success criterion**. A task passes only if the criterion is fully met
(`pass^k`: run it a few times; flaky guidance is a fail).

For the deterministic tooling, the code tests are:
```
uv run --with pytest python -m pytest tests/ -q      # or: pip install pytest && pytest tests/
```

## Turning failures into tasks
When the skill gives bad guidance in real use, add that case here as a new task (this is pattern C9 —
tasks sourced from real failures — applied to the skill itself). The eval set should grow from
reality, not from imagination.
