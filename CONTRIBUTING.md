# Contributing

This skill values *earned* patterns over opinions. A pattern is added only when it carries evidence.

## Proposing a pattern
Open a PR that adds or amends a pattern in `references/patterns.md` (or a cross-check in
`references/openai-crosscheck.md`). Each pattern must state, in the house format:

- **What** — the pattern, concretely.
- **Why it transfers** — why it generalises beyond the project it came from.
- **Grounding** — a certainty label and its basis:
  - `[verified-doc]` — a link to current primary Anthropic/OpenAI docs (add the URL to
    `scripts/sources.json` so `doc_freshness_check.py` tracks it).
  - `[idiomatic]` — consistent with published guidance; say which.
  - `[house]` — validated in a real project; describe the incident/result that earned it.
- **Implementation note** — how to apply it, and how to test it.

Never label a `[house]` convention as vendor doctrine.

## Code
Any change under `scripts/` or `tests/` must:
- stay **stdlib-only** (the tool must run anywhere with zero installs);
- keep `ruff check .` and `pytest tests/ -q` green (CI enforces both, no network in tests);
- for anything that fetches data: return a `data_quality` flag and never fabricate a value on
  failure (see `patterns.md` C4).

## Adding an eval
When guidance proves wrong in real use, add the case to `evals/tasks/design-judgment.md` (input +
success criterion + expected verdict). The eval set should grow from reality (pattern C9).

## Commits & history
Conventional Commits (`type(scope): summary`), one concern per commit. Feature branch → PR into
`develop`; `develop` → `main` by release PR only. Honest, incremental history — no dump commits.
