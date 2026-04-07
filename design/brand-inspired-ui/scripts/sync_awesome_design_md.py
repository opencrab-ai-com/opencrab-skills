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
        name.replace(".", "").lower(),
        slug.replace(".", "").lower(),
        slug.replace(".", " ").lower(),
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
        "Use this file when the user names a brand directly or asks which bundled references are available.",
        "",
        "| Brand | Slug | Category | Signature Traits | Aliases | Path |",
        "| --- | --- | --- | --- | --- | --- |",
    ]

    for brand in brands:
        lines.append(
            f"| {brand.name} | `{brand.slug}` | {brand.category} | {brand.summary} | "
            f"`{', '.join(brand.aliases)}` | `references/brands/{brand.slug}` |"
        )

    lines.extend(
        [
            "",
            "Prefer a direct brand match over vibe matching. Use `references/style-mapping.md` only when the user does not name a brand.",
            "",
        ]
    )
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

    brands_root = dest_root / "references" / "brands"
    if brands_root.exists():
        shutil.rmtree(brands_root)
    brands_root.mkdir(parents=True, exist_ok=True)

    for brand in brands:
        copy_brand_assets(source_root, dest_root, brand)

    catalog_path = dest_root / "references" / "catalog.md"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(render_catalog(brands), encoding="utf-8")

    print(f"Synced {len(brands)} brands into {dest_root}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Copy DESIGN.md and preview HTML assets from an awesome-design-md clone."
    )
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
