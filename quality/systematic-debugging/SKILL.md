---
name: systematic-debugging
description: Use when a bug, test failure, build issue, performance problem, or other unexpected behavior appears and you need root-cause analysis before proposing fixes
---

# Systematic Debugging

Random fixes create more bugs. Use this skill to find root cause before changing code.

## Workflow

1. Read the full error or failure output.
2. Reproduce the issue reliably.
3. Check recent changes and environmental differences.
4. Gather evidence at each boundary in multi-step systems.
5. Trace bad data or state back to the source.
6. Compare against working examples or reference implementations.
7. Form one hypothesis at a time and test it with the smallest useful change.
8. Fix the root cause, not just the visible symptom.

## Guardrails

- No fixes before investigation.
- No multiple speculative fixes at once.
- If repeated fixes fail, question the architecture instead of thrashing.

## Verification

Create a minimal failing reproduction before the final fix when possible, then verify the issue is resolved without introducing regressions.
