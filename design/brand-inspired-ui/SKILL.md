---
name: brand-inspired-ui
description: Use when a user wants a page, component, or HTML mockup inspired by a known brand, or describes a visual style and needs a matching reference from the bundled design library
---

# Brand Inspired UI

Use this skill to choose a bundled brand reference and turn it into frontend-friendly design guidance.

## When to Use

Use this skill when the user:

- names a brand and wants the UI to feel similar
- describes a vibe and needs a matching visual reference
- wants a landing page, section, component, mockup, or prototype
- needs output a frontend engineer can directly consume

Do not use this skill to generate a new `DESIGN.md` from scratch.

## Workflow

1. If the user names a brand, start with `references/catalog.md`.
2. If the user gives only style language, read `references/style-mapping.md` and narrow to two or three candidates.
3. Read the chosen brand's `references/brands/<brand>/DESIGN.md` before making implementation decisions.
4. Open `preview.html` or `preview-dark.html` only when you need visual confirmation for spacing, surface treatment, component tone, or dark mode behavior.
5. Prefer one reference brand. Blend two only when the user explicitly asks for a mixed aesthetic.

## Deliverables

Always provide:

- why the reference fits
- the visual traits that must survive implementation
- the brand-specific details that should not be copied literally
- implementation constraints for color, typography, spacing, radius, depth, layout, and component behavior

If the user wants a mockup, prototype, or frontend-consumable artifact, strongly consider HTML as the output format. If the project already has a target framework, use HTML as the visual baseline and then translate it into the requested stack.

## Fallbacks

- If the requested brand is not bundled, name the closest bundled substitute and say clearly that it is a substitute.
- If the style prompt is vague, present two or three candidates with short trade-offs and recommend one.
- If the user names a bundled brand directly, `references/catalog.md` takes priority over `references/style-mapping.md`.

## Guardrails

- Do not load every bundled brand into context.
- Do not require opening preview HTML files for every request.
- Do not present substitute brands as exact matches.
- Do not encourage direct copying of trademark-heavy assets or branded copy.
