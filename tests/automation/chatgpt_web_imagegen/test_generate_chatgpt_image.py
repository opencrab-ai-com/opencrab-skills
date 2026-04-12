from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO_ROOT / "automation/chatgpt-web-imagegen/scripts/generate_chatgpt_image.py"
SPEC = importlib.util.spec_from_file_location("generate_chatgpt_image", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ChatGPTWebImagegenTests(unittest.TestCase):
    def test_default_output_dir_uses_home_desktop_images_folder(self) -> None:
        home = Path("/tmp/fake-home")

        self.assertEqual(
            MODULE.default_output_dir(home),
            home / "Desktop" / "ImagesGenByChatgpt",
        )

    def test_choose_output_path_defaults_under_desktop_images_folder(self) -> None:
        output_path = MODULE.choose_output_path(
            requested_out=None,
            downloaded_file=Path("ChatGPT Image.png"),
            home=Path("/tmp/fake-home"),
            now=datetime(2026, 4, 12, 23, 45, 10),
        )

        self.assertEqual(
            output_path,
            Path("/tmp/fake-home/Desktop/ImagesGenByChatgpt/chatgpt-image-20260412-234510.png"),
        )

    def test_parse_page_access_state_detects_login_required(self) -> None:
        state = MODULE.parse_page_access_state(
            json.dumps(
                {
                    "url": "https://chatgpt.com/auth/login",
                    "has_editor": False,
                    "is_login_required": True,
                    "is_image_generation_unavailable": False,
                    "text_excerpt": "Log in to continue",
                }
            )
        )

        self.assertEqual(
            MODULE.describe_page_access_issue(state),
            "ChatGPT is not logged in in Google Chrome. Please log in to https://chatgpt.com/images and try again.",
        )

    def test_parse_page_access_state_detects_image_generation_unavailable(self) -> None:
        state = MODULE.parse_page_access_state(
            json.dumps(
                {
                    "url": "https://chatgpt.com/images",
                    "has_editor": False,
                    "is_login_required": False,
                    "is_image_generation_unavailable": True,
                    "text_excerpt": "Upgrade to Plus to use image generation",
                }
            )
        )

        self.assertEqual(
            MODULE.describe_page_access_issue(state),
            "This ChatGPT account or session does not currently support image generation on https://chatgpt.com/images. Please switch to an account with image generation access and try again.",
        )


if __name__ == "__main__":
    unittest.main()
