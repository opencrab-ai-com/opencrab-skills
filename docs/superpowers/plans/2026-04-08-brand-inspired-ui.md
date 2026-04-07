# Brand Inspired UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reusable `design/brand-inspired-ui` skill that selects bundled brand references from `awesome-design-md`, converts them into frontend-friendly guidance, and treats HTML as a first-class design handoff format.

**Architecture:** Keep the skill self-contained inside `design/brand-inspired-ui`. Use a small Python sync script to import `DESIGN.md`, `preview.html`, and `preview-dark.html` from an upstream clone and to generate `references/catalog.md` from the upstream README, while hand-authoring `SKILL.md`, `agents/openai.yaml`, and `references/style-mapping.md`.

**Tech Stack:** Markdown, YAML, Python 3 standard library, unittest, imported HTML reference assets

---

### Task 1: Create the Sync Script Test Harness

**Files:**
- Create: `tests/design/brand_inspired_ui/test_sync_awesome_design_md.py`
- Create: `design/brand-inspired-ui/scripts/sync_awesome_design_md.py`

- [ ] **Step 1: Write the failing test**

```python
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "design/brand-inspired-ui/scripts/sync_awesome_design_md.py"


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


class SyncAwesomeDesignMdTests(unittest.TestCase):
    def test_sync_copies_brand_assets_and_writes_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_root = temp_path / "awesome-design-md"
            dest_root = temp_path / "brand-inspired-ui"

            write_file(
                source_root / "README.md",
                """
                ### Developer Tools & Platforms

                - [**Vercel**](https://github.com/VoltAgent/awesome-design-md/tree/main/design-md/vercel/) - Frontend deployment platform. Black and white precision, Geist font
                """,
            )
            write_file(source_root / "design-md/vercel/DESIGN.md", "# Vercel")
            write_file(source_root / "design-md/vercel/preview.html", "<html>light</html>")
            write_file(source_root / "design-md/vercel/preview-dark.html", "<html>dark</html>")

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--source",
                    str(source_root),
                    "--dest",
                    str(dest_root),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((dest_root / "references/brands/vercel/DESIGN.md").exists())
            self.assertTrue((dest_root / "references/brands/vercel/preview.html").exists())
            self.assertTrue((dest_root / "references/brands/vercel/preview-dark.html").exists())

            catalog = (dest_root / "references/catalog.md").read_text(encoding="utf-8")
            self.assertIn("| Vercel |", catalog)
            self.assertIn("Developer Tools & Platforms", catalog)
            self.assertIn("references/brands/vercel", catalog)

    def test_sync_fails_when_a_required_brand_file_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_root = temp_path / "awesome-design-md"
            dest_root = temp_path / "brand-inspired-ui"

            write_file(
                source_root / "README.md",
                """
                ### Developer Tools & Platforms

                - [**Vercel**](https://github.com/VoltAgent/awesome-design-md/tree/main/design-md/vercel/) - Frontend deployment platform. Black and white precision, Geist font
                """,
            )
            write_file(source_root / "design-md/vercel/DESIGN.md", "# Vercel")
            write_file(source_root / "design-md/vercel/preview.html", "<html>light</html>")

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "--source",
                    str(source_root),
                    "--dest",
                    str(dest_root),
                ],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing required file", result.stderr)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest discover -s tests/design/brand_inspired_ui -p 'test_*.py' -v`
Expected: FAIL because `design/brand-inspired-ui/scripts/sync_awesome_design_md.py` does not exist yet.

- [ ] **Step 3: Create the script directory with a minimal placeholder**

```python
#!/usr/bin/env python3
raise SystemExit("sync_awesome_design_md.py not implemented yet")
```

- [ ] **Step 4: Run test to verify it still fails for the right reason**

Run: `python3 -m unittest discover -s tests/design/brand_inspired_ui -p 'test_*.py' -v`
Expected: FAIL because the script exits non-zero and does not copy assets or write `references/catalog.md`.

- [ ] **Step 5: Commit**

```bash
git add tests/design/brand_inspired_ui/test_sync_awesome_design_md.py design/brand-inspired-ui/scripts/sync_awesome_design_md.py
git commit -m "test: add sync script coverage for brand-inspired-ui"
```

### Task 2: Implement the Upstream Sync Script

**Files:**
- Modify: `design/brand-inspired-ui/scripts/sync_awesome_design_md.py`
- Test: `tests/design/brand_inspired_ui/test_sync_awesome_design_md.py`

- [ ] **Step 1: Replace the placeholder with the working sync script**

```python
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

REQUIRED_FILES = ("DESIGN.md", "preview.html", "preview-dark.html")
BRAND_PATTERN = re.compile(
    r"- \[\*\*(?P<name>.+?)\*\*\]\((?P<url>[^)]+)\) - (?P<summary>.+)"
)


@dataclass(frozen=True)
class Brand:
    name: str
    slug: str
    category: str
    summary: str
    aliases: tuple[str, ...]


def slug_from_url(url: str) -> str:
    marker = "/design-md/"
    if marker not in url:
        raise ValueError(f"Could not find design-md path in URL: {url}")
    return url.split(marker, 1)[1].strip("/")


def aliases_for(name: str, slug: str) -> tuple[str, ...]:
    values = {
        name.lower(),
        slug.lower(),
        slug.replace(".", "").lower(),
        slug.replace(".", " ").lower(),
        name.replace(".", "").lower(),
    }
    return tuple(sorted(values))


def parse_brands(readme_path: Path) -> list[Brand]:
    brands: list[Brand] = []
    category: str | None = None

    for raw_line in readme_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("### "):
            category = line[4:].strip()
            continue

        match = BRAND_PATTERN.match(line)
        if match and category:
            name = match.group("name").strip()
            slug = slug_from_url(match.group("url").strip())
            summary = match.group("summary").strip()
            brands.append(
                Brand(
                    name=name,
                    slug=slug,
                    category=category,
                    summary=summary,
                    aliases=aliases_for(name, slug),
                )
            )

    if not brands:
        raise ValueError(f"No brands parsed from {readme_path}")

    return brands


def render_catalog(brands: list[Brand]) -> str:
    lines = [
        "# Brand Catalog",
        "",
        "Use this file when the user names a brand or asks which bundled references are available.",
        "",
        "| Brand | Slug | Category | Signature Traits | Aliases | Path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for brand in brands:
        lines.append(
            f"| {brand.name} | `{brand.slug}` | {brand.category} | {brand.summary} | "
            f"`{', '.join(brand.aliases)}` | `references/brands/{brand.slug}` |"
        )

    lines.append("")
    return "\n".join(lines)


def copy_brand_assets(source_root: Path, dest_root: Path, brand: Brand) -> None:
    source_brand_dir = source_root / "design-md" / brand.slug
    dest_brand_dir = dest_root / "references" / "brands" / brand.slug
    dest_brand_dir.mkdir(parents=True, exist_ok=True)

    for filename in REQUIRED_FILES:
        source_file = source_brand_dir / filename
        if not source_file.exists():
            raise FileNotFoundError(
                f"Missing required file for {brand.slug}: {source_file}"
            )
        shutil.copy2(source_file, dest_brand_dir / filename)


def sync(source_root: Path, dest_root: Path) -> int:
    brands = parse_brands(source_root / "README.md")
    for brand in brands:
        copy_brand_assets(source_root, dest_root, brand)

    catalog_path = dest_root / "references" / "catalog.md"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(render_catalog(brands), encoding="utf-8")

    print(f"Synced {len(brands)} brands into {dest_root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--dest", required=True, type=Path)
    args = parser.parse_args()

    try:
        return sync(args.source.resolve(), args.dest.resolve())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: Run the tests to verify the script passes**

Run: `python3 -m unittest discover -s tests/design/brand_inspired_ui -p 'test_*.py' -v`
Expected: PASS with 2 tests, 0 failures.

- [ ] **Step 3: Make the script executable**

```bash
chmod +x design/brand-inspired-ui/scripts/sync_awesome_design_md.py
```

- [ ] **Step 4: Re-run the tests after the chmod change**

Run: `python3 -m unittest discover -s tests/design/brand_inspired_ui -p 'test_*.py' -v`
Expected: PASS with 2 tests, 0 failures.

- [ ] **Step 5: Commit**

```bash
git add design/brand-inspired-ui/scripts/sync_awesome_design_md.py tests/design/brand_inspired_ui/test_sync_awesome_design_md.py
git commit -m "feat: add brand reference sync script"
```

### Task 3: Author the Skill Metadata and Style Guidance

**Files:**
- Create: `design/brand-inspired-ui/SKILL.md`
- Create: `design/brand-inspired-ui/agents/openai.yaml`
- Create: `design/brand-inspired-ui/references/style-mapping.md`

- [ ] **Step 1: Write `SKILL.md`**

```markdown
---
name: brand-inspired-ui
description: Use when a user wants a page, component, or HTML mockup inspired by a known brand, or describes a visual style and needs a matching reference from the bundled design library
---

# Brand Inspired UI

Use this skill to pick a bundled brand reference and translate it into frontend-friendly design output.

## Workflow

1. If the user names a brand, look it up in `references/catalog.md` and use that brand first.
2. If the user gives only vibe words, use `references/style-mapping.md` to narrow to two or three brands and recommend one.
3. Read the chosen brand directory under `references/brands/` and open its `DESIGN.md` before making implementation decisions.
4. Open `preview.html` or `preview-dark.html` only when you need to confirm component tone, spacing, surface layering, or dark-mode treatment.
5. Prefer one brand reference. Blend two only when the user explicitly asks for a mixed aesthetic.

## Output

Always provide:

- why the reference fits
- what visual traits must survive implementation
- what should not be copied literally
- implementation constraints for color, typography, spacing, radius, depth, layout, and component behavior

When the user wants a mockup, prototype, landing page draft, or frontend-consumable output, strongly consider HTML as the delivery format.

## Fallbacks

- If the requested brand is missing, name the closest bundled substitute and say that it is a substitute.
- If the style prompt is vague, present two or three candidates with short trade-offs and recommend one.
```

- [ ] **Step 2: Write `agents/openai.yaml`**

```yaml
interface:
  display_name: "Brand Inspired UI"
  short_description: "Pick brand references for frontend UI"
  default_prompt: "Use $brand-inspired-ui to choose a bundled brand reference and turn it into frontend-friendly design guidance."

policy:
  allow_implicit_invocation: true
```

- [ ] **Step 3: Write `references/style-mapping.md`**

```markdown
# Style Mapping

Use this file when the user describes a visual direction without naming a brand.

| Style cue | Primary recommendation | Strong alternatives | When to prefer the primary pick |
| --- | --- | --- | --- |
| Minimal black-and-white developer tool | Vercel | Raycast, HashiCorp | Choose Vercel when typography and precision should carry the design |
| Warm editorial productivity | Notion | Airtable, Intercom | Choose Notion when you want calm whitespace and softer neutral tones |
| Cinematic dark AI interface | ElevenLabs | RunwayML, Minimax | Choose ElevenLabs when the interface should feel immersive and media-rich |
| Blueprint infrastructure aesthetic | Together AI | HashiCorp, ClickHouse | Choose Together AI when the product should feel technical and systems-oriented |
| Friendly colorful SaaS marketing | Zapier | Figma, Airtable | Choose Zapier when warmth and accessibility matter more than minimalism |
| Premium fintech precision | Stripe | Revolut, Wise | Choose Stripe when elegance, gradient polish, and trust cues matter most |
| Playful creative-builder energy | Framer | Webflow, Lovable | Choose Framer when motion and design-forward presentation are central |
| Clean documentation-first developer UX | Mintlify | MongoDB, ClickHouse | Choose Mintlify when reading comfort and docs hierarchy matter most |
| Dark code-centric product surface | Cursor | Warp, OpenCode AI | Choose Cursor when the product should feel like a modern coding environment |
| Radical automotive minimalism | Tesla | BMW, Ferrari | Choose Tesla when subtraction and cinematic hero framing are the main goals |

## Notes

- Start with the primary recommendation unless the user's wording clearly favors one of the alternatives.
- Use no more than two references in a single concept unless the user explicitly asks for blending.
- If a user names a brand directly, `references/catalog.md` wins over this mapping file.
```

- [ ] **Step 4: Verify the created files are present**

Run: `find design/brand-inspired-ui -maxdepth 3 -type f | sort`
Expected: lists `SKILL.md`, `agents/openai.yaml`, `references/style-mapping.md`, and `scripts/sync_awesome_design_md.py`.

- [ ] **Step 5: Commit**

```bash
git add design/brand-inspired-ui/SKILL.md design/brand-inspired-ui/agents/openai.yaml design/brand-inspired-ui/references/style-mapping.md
git commit -m "feat: add brand-inspired-ui skill metadata"
```

### Task 4: Import Brand References, Update Repository Docs, and Validate

**Files:**
- Modify: `README.md`
- Create: `design/brand-inspired-ui/references/catalog.md`
- Create: `design/brand-inspired-ui/references/brands/vercel/{DESIGN.md,preview.html,preview-dark.html}` and the same generated file triplet for every imported brand
- Verify: `design/brand-inspired-ui/**`

- [ ] **Step 1: Run the sync script against the upstream clone**

Run: `python3 design/brand-inspired-ui/scripts/sync_awesome_design_md.py --source /tmp/awesome-design-md --dest design/brand-inspired-ui`
Expected: prints `Synced 58 brands into /Users/sky/codex/opencrab-skills/design/brand-inspired-ui` and creates `references/catalog.md` plus 58 brand subdirectories under `references/brands/`.

- [ ] **Step 2: Update the repository README so the new category is discoverable**

```markdown
# opencrab-skills
由 Opencrab 精选或者制作的 skills，欢迎大家使用。

## Categories

- `design/`
  - `brand-inspired-ui/`: 从品牌设计参考中挑选合适风格，并输出前端可消费的设计约束、HTML 原型或实现提示。
```

- [ ] **Step 3: Validate the skill structure and imported references**

Run: `python3 /Users/sky/.codex/skills/.system/skill-creator/scripts/quick_validate.py design/brand-inspired-ui`
Expected: `Skill is valid!`

Run:

```bash
python3 - <<'PY'
from pathlib import Path

skill_root = Path("design/brand-inspired-ui")
brand_dirs = sorted((skill_root / "references" / "brands").iterdir())
assert len(brand_dirs) == 58, len(brand_dirs)
for brand_dir in brand_dirs:
    for filename in ("DESIGN.md", "preview.html", "preview-dark.html"):
        assert (brand_dir / filename).exists(), f"Missing {filename} in {brand_dir.name}"
print(f"Verified {len(brand_dirs)} brand directories")
PY
```

Expected: `Verified 58 brand directories`

- [ ] **Step 4: Run the sync script tests one more time**

Run: `python3 -m unittest discover -s tests/design/brand_inspired_ui -p 'test_*.py' -v`
Expected: PASS with 2 tests, 0 failures.

- [ ] **Step 5: Commit**

```bash
git add README.md design/brand-inspired-ui/references design/brand-inspired-ui/scripts/sync_awesome_design_md.py tests/design/brand_inspired_ui/test_sync_awesome_design_md.py
git commit -m "feat: add brand-inspired-ui design skill"
```
