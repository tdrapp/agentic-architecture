# Authoring & packaging a Claude Skill

How to write a skill, and how to package it as a credible public repo. Certainty labels as in
`patterns.md` (`[verified-doc]` / `[idiomatic]` / `[house]`). Re-check the sourced facts with
`scripts/doc_freshness_check.py`.

---

## 1. What a skill is

A skill is a folder with a `SKILL.md` at its root, discovered by Claude and loaded **on demand**.
`[verified-doc]` (code.claude.com/docs/en/skills; github.com/anthropics/skills)

```
skill-name/
├── SKILL.md          # required: YAML frontmatter + body
├── references/       # optional: docs loaded only when pointed to
├── scripts/          # optional: deterministic executable helpers
└── assets/           # optional: templates/fonts/icons for output
```

## 2. Frontmatter (the trigger)

```yaml
---
name: skill-name                 # kebab-case identifier
description: "<what it does> + <when to use it>, with explicit trigger phrases."
# optional, tool-dependent: allowed-tools / tools, model, version, user-invocable
---
```

The **description is the primary triggering mechanism** — it is the only part always in context, so
it must state *what* and *when* with concrete trigger phrases, and be slightly assertive to avoid
under-triggering. `[idiomatic]` (skill-creator guidance)

## 3. Progressive disclosure (the core discipline)

Three loading tiers — keep each as small as possible: `[verified-doc]`
1. **Metadata** (name + description, ~100 words) — always in context.
2. **SKILL.md body** — loaded when the skill triggers. Target **< 500 lines**.
3. **Bundled resources** (`references/`, `scripts/`, `assets/`) — loaded only when the body points
   to them. No line limit; put depth here, behind clear "read this when…" pointers. Add a table of
   contents to any reference file over ~300 lines.

Design implication: the body routes (a mode-detection table: *trigger → which reference to read*);
the references carry the weight. This mirrors context-engineering guidance (load just-in-time, keep
the always-on context lean). `[idiomatic]`

## 4. Bundled scripts

Put deterministic, repeatable work in `scripts/` and reference it by name from the body. Prefer
**zero external dependencies** (stdlib) so the script runs anywhere; if a tool fetches data, give it
a quality flag and a no-invention contract (see `patterns.md` C4). Test each branch (`tests/`).

## 5. Distribution — three paths `[verified-doc]`

| Path | Where | Who gets it |
|---|---|---|
| Project-local | `<repo>/.claude/skills/<name>/` | that project only |
| User-global | `~/.claude/skills/<name>/` | all your projects |
| Packaged **plugin** | a plugin bundling the skill | anyone who installs it (marketplace) |

This skill's own model: it lives user-global **and** is a public GitHub repo — the copy you run is
the copy you publish (dogfooding).

## 6. Packaging a credible public repo

Imitate `anthropics/skills`: a self-contained skill folder + a README that leads with a one-line
definition, an explicit **Disclaimer**, and install instructions. `[verified-doc]`
(github.com/anthropics/skills)

The single strongest credibility signal to a frontier-lab engineer is **evals + tests + CI**
(`anthropics/anthropic-cookbook` ships `evals/ tests/ .pre-commit`; `openai/openai-cookbook` and
`openai/openai-agents-python` ship `examples/ tests/`). `[verified-doc]`

Include: `README` (objective → use cases → structure → limits → sources), `LICENSE`, `DISCLAIMER`,
`CONTRIBUTING`, `CHANGELOG`, `examples/`, `tests/` + `evals/`, one CI workflow. `[house]`

**Avoid** (reads as a CV project, not real work): `[house]`
- a single "initial commit" that dumps everything — publish an honest, incremental git history;
- badge soup — one CI badge is enough;
- marketing adjectives and benchmark claims with no reproducible harness;
- asserting house conventions as official vendor doctrine — always label the source and certainty.

## 7. Honest history (why the git graph matters)

A reviewer opening the repo judges *real construction vs one-shot dump*: they scan the README in
seconds, the structure, and whether commits tell a build story. So ship the real lifecycle —
`init → develop → feature branches → PR → merge → release` — with truthful timestamps and messages.
Never backdate or pad the graph; the value is that it is true. `[house]`

## Sources
- Agent Skills docs — https://code.claude.com/docs/en/skills
- Skills repo model — https://github.com/anthropics/skills
- Cookbook exemplars — https://github.com/anthropics/anthropic-cookbook · https://github.com/openai/openai-cookbook · https://github.com/openai/openai-agents-python
