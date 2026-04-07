---
name: ui-ux-research
description: Use when designing or reviewing web or mobile interfaces and you want searchable references for styles, colors, typography, landing patterns, charts, UX rules, or stack-specific UI guidance
---

# UI UX Research

Use this skill to search a bundled UI/UX reference library and turn the results into practical design guidance.

## When to Use

Use this skill when the user asks you to:

- design or improve a web or mobile interface
- choose a visual direction, palette, type pairing, or layout pattern
- recommend chart types or dashboard presentation
- review UX quality, accessibility, or interaction details
- generate a project-specific design system before implementation

## Workflow

1. Extract the product type, industry, style keywords, and target stack from the request.
2. Start with a design-system recommendation:

```bash
python3 design/ui-ux-research/scripts/search.py "<query>" --design-system -p "Project Name"
```

3. If you need more depth, run targeted searches in a domain such as `style`, `color`, `typography`, `landing`, `chart`, `ux`, or `icons`.

```bash
python3 design/ui-ux-research/scripts/search.py "<query>" --domain style
python3 design/ui-ux-research/scripts/search.py "<query>" --domain typography
python3 design/ui-ux-research/scripts/search.py "<query>" --domain ux
```

4. If implementation details matter, search stack-specific guidance.

```bash
python3 design/ui-ux-research/scripts/search.py "<query>" --stack html-tailwind
python3 design/ui-ux-research/scripts/search.py "<query>" --stack react
```

5. Synthesize the results into a concise output:
- recommended pattern
- visual style direction
- color palette and typography
- interaction and accessibility guidance
- anti-patterns to avoid

## Notes

- `html-tailwind` is the default stack when no stack is specified.
- Use `--persist` when a reusable design-system artifact would help a longer project.
- If scripts are unavailable, you can still inspect the CSV data in `data/` directly.

## Guardrails

- Start with `--design-system` before diving into detailed searches.
- Do not treat search results as rigid rules; adapt them to the project context.
- Keep final recommendations coherent instead of mixing too many competing styles.
