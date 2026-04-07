---
name: test-driven-development
description: Use when implementing a feature, fixing a bug, or changing behavior and you want to drive the work with a failing test first
---

# Test Driven Development

Write the test first. Watch it fail. Write the minimum code to pass.

## Workflow

1. Write one failing test for one behavior.
2. Run it and confirm the failure is real and relevant.
3. Write the minimum implementation needed to pass.
4. Run the test again and confirm it passes.
5. Refactor only after the test is green.
6. Repeat for the next behavior.

## Requirements

- one behavior per test
- clear test names
- no production code before a failing test exists
- no "I will add tests later" shortcuts

## Guardrails

- If a test passes immediately, it is not proving the new behavior.
- If a test fails for the wrong reason, fix the test first.
- Do not smuggle extra features into the green phase.
