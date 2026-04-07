---
title: Brand Inspired UI Skill Design
date: 2026-04-08
status: approved-in-chat
repo: opencrab-skills
skill_name: brand-inspired-ui
category: design
---

# Brand Inspired UI Skill Design

## Goal

Create a reusable skill in the `opencrab-skills` repository that helps general-purpose AI coding agents pick a brand-inspired visual direction and translate it into frontend-friendly output.

The skill should be useful when a user asks for:

- a page or component inspired by a known brand
- a UI that matches an abstract style description
- a frontend-friendly design handoff
- an HTML mockup, prototype, or visual baseline before framework implementation

The skill is not a `DESIGN.md` authoring tool. Its job is to select and apply existing references from `awesome-design-md`.

## Scope

### In Scope

- Brand-name-first matching, with abstract-style fallback
- Reusing the curated `DESIGN.md` files from `VoltAgent/awesome-design-md`
- Including each brand's `preview.html` and `preview-dark.html` as optional visual references
- Producing outputs that frontend developers can directly consume
- Keeping the skill broadly compatible with Codex, Claude, Cursor, and similar AI coding agents

### Out of Scope

- Generating new `DESIGN.md` files from scratch
- Rebuilding the entire upstream project tooling
- Guaranteeing pixel-perfect cloning of any brand
- Shipping production app code as part of the skill itself

## Recommended Repository Structure

```text
opencrab-skills/
└── design/
    └── brand-inspired-ui/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── catalog.md
            ├── style-mapping.md
            └── brands/
                ├── vercel/
                │   ├── DESIGN.md
                │   ├── preview.html
                │   └── preview-dark.html
                ├── notion/
                │   ├── DESIGN.md
                │   ├── preview.html
                │   └── preview-dark.html
                └── other brand folders
```

## Skill Positioning

The skill should act as a design-reference router plus implementation guide.

Primary path:

- User names a brand directly, for example "make this feel like Vercel" or "use a Notion-like aesthetic"

Secondary path:

- User describes a style without naming a brand, for example "minimal developer tool landing page" or "warm editorial SaaS homepage"

In both cases, the skill should help the agent choose the right reference and then convert that reference into concrete implementation guidance.

## Workflow

### 1. Identify the request type

- If the user names a brand in the library, treat that as the primary match.
- If the user provides only abstract style language, use style mapping to identify two to three candidate brands and recommend one.
- If the user provides both a brand and style keywords, keep the brand as the primary reference and use the keywords only to refine interpretation.

### 2. Use lightweight indexes first

The skill should avoid loading all reference material at once.

- `references/catalog.md` should list all supported brands, aliases, signature traits, suitable product/page types, and reference paths.
- `references/style-mapping.md` should map common abstract aesthetics to a small set of candidate brands.

### 3. Read only the matched brand references

Once a brand is selected:

- read the brand's `DESIGN.md` first
- use `preview.html` and `preview-dark.html` when visual confirmation is helpful
- default to one brand reference
- allow up to two brands only when the task explicitly calls for a mixed reference

### 4. Translate the reference into build guidance

The skill should instruct the agent to produce:

- a short explanation of why the chosen reference fits
- the non-negotiable visual traits to preserve
- the brand-specific details that should not be copied literally
- implementation constraints covering color, typography, spacing, radius, depth, layout, and component treatment
- a practical prompt or implementation brief that can be used for downstream page building

### 5. Use explicit fallback behavior

- If style intent is vague, present two to three candidates with short differences and recommend one.
- If the requested brand is missing, pick the closest supported reference and state clearly that it is a substitute.

## HTML As a First-Class Output

This skill should explicitly treat HTML as a strong delivery format, not just a side artifact.

Reasoning:

- design output is often handed to frontend engineers
- HTML is easy for both humans and AI agents to inspect
- HTML can act as a visual baseline before converting to React, Vue, Next.js, or another stack
- the upstream repository already includes preview files that demonstrate how the design language renders

The skill should tell agents:

- default to a design summary plus implementation constraints
- when the user asks for a mockup, prototype, landing page draft, or frontend-consumable output, strongly consider generating HTML
- when a framework is already chosen, use HTML as the visual baseline rather than forcing HTML to be the final deliverable

## Resource Responsibilities

### `SKILL.md`

Should define:

- triggering conditions
- reading order
- matching workflow
- fallback behavior
- guidance for converting design references into implementation constraints
- when to generate HTML output

### `references/catalog.md`

Should provide a fast brand lookup table, including:

- brand name
- aliases
- signature mood
- common use cases
- file path to the brand reference directory

### `references/style-mapping.md`

Should map abstract style descriptions to brand candidates, for example:

- minimal black-and-white developer aesthetic
- warm editorial productivity feel
- cinematic dark AI interface
- fintech precision
- playful colorful product marketing

### `references/brands/<brand>/DESIGN.md`

Primary text reference for design intent.

### `references/brands/<brand>/preview.html`

Light-theme visual reference for components, spacing, surface treatment, and typography.

### `references/brands/<brand>/preview-dark.html`

Dark-theme visual reference for contrast, layering, and dark-surface components.

## Compatibility Goals

The skill should be written in tool-agnostic language whenever possible.

- It should not assume Codex-specific capabilities for normal operation.
- It may mention that agents with browser or file-view support can open local preview HTML files for richer inspection.
- It should remain useful even in text-only environments by making `DESIGN.md` the default reference.

## Implementation Plan Inputs

After this design is approved as a written spec, implementation should:

1. Create the `design/brand-inspired-ui` skill scaffold.
2. Add `SKILL.md` and `agents/openai.yaml`.
3. Create `references/catalog.md` and `references/style-mapping.md`.
4. Import upstream brand folders from `awesome-design-md`, including `DESIGN.md`, `preview.html`, and `preview-dark.html`.
5. Validate structure and wording so the skill is discoverable and efficient.

## Risks and Guardrails

- Do not overload `SKILL.md` with the contents of every brand.
- Do not require opening HTML for every use.
- Do not present substitute brands as exact matches.
- Do not encourage direct visual cloning of trademark-heavy brand elements.
- Do keep the skill optimized for practical frontend handoff, not just style commentary.

## Success Criteria

The implementation is successful if:

- the skill is discoverable for both brand-name and abstract-style requests
- the skill selects references without loading the full library into context
- agents can produce frontend-friendly guidance from the references
- HTML is treated as a recommended output format when it helps handoff
- the repository gains a clean `design` category and a reusable first skill within it
