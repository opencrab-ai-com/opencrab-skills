# ui-ux-research

`ui-ux-research` is a design-intelligence skill for researching styles, palettes, typography, UX rules, landing patterns, charts, and stack-specific UI guidance.

## Source

This skill is adapted from the `ui-ux-pro-max` skill, then rewritten to be more generic and cross-agent friendly.

## What It Includes

- `SKILL.md`: the runtime guidance for choosing and using the reference library
- `data/`: CSV datasets for styles, colors, typography, UX guidance, charts, and stacks
- `scripts/`: Python search and design-system generation tools

## Runtime Notes

This skill can be used in two ways:

- text-first: read `SKILL.md` and the CSV/reference material directly
- script-assisted: run `scripts/search.py` to get ranked results and design-system recommendations

## Typical Commands

```bash
python3 design/ui-ux-research/scripts/search.py "fintech dashboard" --design-system -p "Northstar"
python3 design/ui-ux-research/scripts/search.py "hero social proof pricing" --domain landing
python3 design/ui-ux-research/scripts/search.py "keyboard focus accessibility" --domain ux
python3 design/ui-ux-research/scripts/search.py "admin table filters" --stack react
```
