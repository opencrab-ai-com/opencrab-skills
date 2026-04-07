---
name: skill-authoring
description: Use when creating or updating reusable AI skills and you need a process for defining triggers, structuring resources, keeping instructions concise, and validating the result
---

# Skill Authoring

Use this skill to create or refine reusable, high-signal skills.

## Workflow

1. Identify concrete use cases and trigger phrases.
2. Decide what belongs in `SKILL.md` versus scripts, references, or assets.
3. Keep the description focused on when to use the skill, not how it works internally.
4. Keep the body concise and move heavy detail into supporting resources only when needed.
5. Validate naming, frontmatter, and file layout.
6. Test the skill against realistic scenarios and close any loopholes you find.

## Core Principles

- concise beats exhaustive
- trigger conditions matter more than marketing copy
- supporting resources should reduce repetition or add deterministic behavior
- a skill should be easy to discover and cheap to load

## Guardrails

- do not write vague descriptions
- do not hide critical behavior in optional files
- do not add extra documentation unless the repository conventions require it
- do not assume a skill is good until you test how an agent would actually use it
