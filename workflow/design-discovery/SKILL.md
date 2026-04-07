---
name: design-discovery
description: Use when a request involves building or changing a feature, interface, workflow, or system and you need to clarify goals, compare approaches, and agree on a design before implementation
---

# Design Discovery

Use this skill to turn an idea into an approved design before implementation starts.

## Workflow

1. Explore the current context first: codebase, docs, and existing constraints.
2. If the request is too broad, decompose it into smaller units before refining details.
3. Ask clarifying questions one at a time.
4. Propose two or three approaches with trade-offs and a recommendation.
5. Present the proposed design in sections sized to the problem.
6. Get approval before implementation.
7. Write a short design note if the project needs a durable record.

## What Good Output Looks Like

- clear goals and constraints
- explicit scope boundaries
- component or system boundaries
- key data flow and failure handling
- testing or verification considerations

## Guardrails

- Do not start coding before the design is approved.
- Do not treat "simple" requests as exempt from design clarification.
- Prefer small, well-bounded components over large undefined blobs.
