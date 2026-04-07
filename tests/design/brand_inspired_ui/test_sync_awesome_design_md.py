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
