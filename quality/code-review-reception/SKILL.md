---
name: code-review-reception
description: Use when receiving code review feedback and you need to evaluate it carefully before implementing changes, especially when comments may be unclear, incomplete, or technically questionable
---

# Code Review Reception

Use this skill to handle review feedback with technical rigor instead of reflexive agreement.

## Workflow

1. Read all feedback before reacting.
2. Restate or clarify unclear items.
3. Verify the feedback against the codebase and current behavior.
4. Decide whether the suggestion is technically correct for this codebase.
5. Implement one item at a time and verify each change.
6. Push back when feedback is wrong, incomplete, or in conflict with the actual requirements.

## Good Responses

- clarify the technical requirement
- fix the issue and summarize what changed
- explain why a suggestion does not fit the current system

## Guardrails

- Do not implement unclear feedback.
- Do not perform empty agreement.
- Do not assume every review comment is correct.
- Do not batch many risky review fixes without intermediate verification.
