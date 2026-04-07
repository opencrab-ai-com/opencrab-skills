---
name: workspace-isolation
description: Use when starting feature work that should be isolated from the current workspace, especially in repositories where git worktrees or parallel branches reduce risk
---

# Workspace Isolation

Use this skill to create an isolated workspace before substantial implementation work.

## Workflow

1. Check whether the repository already uses `.worktrees/` or `worktrees/`.
2. If not, ask where the isolated workspace should live.
3. For project-local worktree directories, verify they are ignored by git.
4. Create a new worktree on a new branch.
5. Run project setup commands if needed.
6. Run a clean baseline verification so new failures are easy to spot.
7. Report the worktree path and current status.

## Guardrails

- Never create a project-local worktree directory without checking `.gitignore`.
- Never start feature work from a failing baseline without making that explicit.
- Prefer isolation when the task is multi-step, risky, or likely to overlap with other work.
