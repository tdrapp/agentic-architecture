# Disclaimer

This repository is for **educational and reference purposes**. It codifies patterns for engineering
agentic AI systems, distilled from primary Anthropic and OpenAI documentation and validated in a
real project.

- **Not official doctrine.** Nothing here is an official Anthropic or OpenAI position. Where a claim
  reflects vendor guidance it is labelled `[verified-doc]` (confirmed in current primary docs — which
  drift; pin the version) or `[idiomatic]` (consistent with published guidance). Claims labelled
  `[house]` are conventions validated in a real project that generalise well but are not vendor
  doctrine. Never cite a `[house]` rule as if a vendor mandated it.
- **Guidance drifts.** SDK option names, tool schemas, and best-practice articles change. Run
  `scripts/doc_freshness_check.py` to check whether the tracked sources still support the claims, and
  re-verify before relying on a specific mechanism.
- **No warranty.** Provided "as is" under the MIT License. You are responsible for how you apply it.
