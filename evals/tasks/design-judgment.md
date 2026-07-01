# Eval tasks — design judgment

Each task: **Input** (what the user asks) · **Success criterion** (what a correct response must do) ·
**Expected verdict**. Grade the *outcome*, not the wording. `pass^k` — must hold on repeated runs.

---

### T1 — Don't build an agent when one call suffices
- **Input:** "I want an agent that takes a blob of text and returns its sentiment as positive/negative."
- **Success criterion:** recommends **NOT** building an agent; a single augmented LLM call (or a
  classifier) suffices. Cites the simplicity principle / start-simple.
- **Expected verdict:** SIMPLER TIER — one call, no agent.

### T2 — Consolidate overlapping tools instead of splitting agents
- **Input:** "My agent has 8 tools that all sort of fetch user data in slightly different ways and it
  keeps picking the wrong one. Should I split it into multiple agents?"
- **Success criterion:** identifies **tool overload from overlap** (not raw count) as the problem;
  recommends **consolidating/clarifying tools** before adding agents; notes >15 distinct tools can
  work while <10 overlapping ones fail.
- **Expected verdict:** FIX TOOLS FIRST — do not split yet.

### T3 — Flag a missing independent verifier
- **Input:** "My pipeline: research agent gathers sources, then the same agent writes the final
  recommendation and rates its own confidence. Good?"
- **Success criterion:** flags the **C2 generation/verification gap** — the producer certifies itself;
  recommends an independent verifier that sees the evidence but not the builder's narrative.
- **Expected verdict:** ADD INDEPENDENT VERIFICATION (C2).

### T4 — Tool honesty / no silent fallback
- **Input:** "When my price API fails, my tool returns the last cached value so the agent always has a
  number to work with. Fine?"
- **Success criterion:** flags **silent fallback** as how tools quietly lie; requires a
  `data_quality`/staleness flag surfaced to the user, and `null` + documented gap over a masked guess
  (C4). Cached is acceptable only if labelled stale.
- **Expected verdict:** MAKE THE DEGRADATION VISIBLE (C4).

### T5 — Ground before optimising
- **Input:** "Design a rebalancer that proposes new target weights for my portfolio."
- **Success criterion:** requires a **pre-flight read of current holdings/targets before proposing
  numbers** (C7); distinguishes read-state vs diagnose vs from-scratch-optimum.
- **Expected verdict:** ADD PRE-FLIGHT STATE READ (C7).

### T6 — Human gate on irreversible actions
- **Input:** "The agent should be able to place trades / send the emails automatically once it's
  confident."
- **Success criterion:** requires a **human-in-the-loop gate** on the irreversible/high-risk action
  (C12); confidence alone is not sufficient authorisation.
- **Expected verdict:** GATE THE IRREVERSIBLE ACTION (C12).

### T7 — Workflow over autonomous loop when flow is predictable
- **Input:** "It's always: classify the ticket → fetch the relevant KB article → draft a reply. Should
  I give an autonomous agent free rein?"
- **Success criterion:** recommends a **coded workflow** (routing → retrieval → generation), not an
  autonomous loop, because control flow is predictable; notes autonomy adds cost + compounding-error risk.
- **Expected verdict:** WORKFLOW, NOT AUTONOMY.

### T8 — Structured subagent outputs at scale
- **Input:** "My 5 worker agents each return a paragraph of markdown and the synthesizer parses them
  with regex. It's getting flaky."
- **Success criterion:** recommends **structured (JSON) subagent outputs** validated against a schema
  (C10), which makes synthesis and evals mechanical; references Structured Outputs / strict mode.
- **Expected verdict:** ENFORCE OUTPUT SCHEMAS (C10).
