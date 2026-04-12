#!/usr/bin/env python3
"""Generate a single image through the ChatGPT Images web UI in Google Chrome."""

from __future__ import annotations

import argparse
import base64
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import NamedTuple


CHROME_APP_NAME = "Google Chrome"
DOWNLOAD_PREFIX = "ChatGPT Image"
CHATGPT_DOMAINS = ("chatgpt.com", "chat.openai.com")
DEFAULT_TIMEOUT_SECONDS = 240
CHROME_STARTUP_TIMEOUT_SECONDS = 30
CHAT_TAB_OPEN_TIMEOUT_SECONDS = 60
POLL_INTERVAL_SECONDS = 1.0


class ChatGPTTabLocation(NamedTuple):
    window_index: int
    tab_index: int


class ChatGPTTabResolution(NamedTuple):
    action: str
    location: ChatGPTTabLocation


class GalleryImageCard(NamedTuple):
    button_aria: str
    image_src: str


class ResultPageState(NamedTuple):
    generated_image_buttons: tuple[str, ...]
    generated_image_alts: tuple[str, ...]
    has_save_button: bool


class PageAccessState(NamedTuple):
    url: str
    has_editor: bool
    is_login_required: bool
    is_image_generation_unavailable: bool
    text_excerpt: str


def default_output_dir(home: Path) -> Path:
    return home / "Desktop" / "ImagesGenByChatgpt"


def build_default_output_path(*, home: Path, now: datetime, suffix: str) -> Path:
    safe_suffix = suffix if suffix.startswith(".") else f".{suffix}"
    file_name = f"chatgpt-image-{now.strftime('%Y%m%d-%H%M%S')}{safe_suffix}"
    return default_output_dir(home) / file_name


def choose_output_path(
    *,
    requested_out: str | None,
    downloaded_file: Path,
    home: Path,
    now: datetime,
) -> Path:
    if requested_out:
        return Path(requested_out).expanduser()
    return build_default_output_path(home=home, now=now, suffix=downloaded_file.suffix or ".png")


def find_new_download(
    *,
    downloads_dir: Path,
    existing_names: set[str],
    min_mtime: float,
) -> Path | None:
    candidates: list[Path] = []
    if not downloads_dir.exists():
        return None

    for path in downloads_dir.iterdir():
        if not path.is_file():
            continue
        if not path.name.startswith(DOWNLOAD_PREFIX):
            continue
        if path.name in existing_names:
            continue
        if path.suffix.lower() in {".download", ".crdownload", ".part"}:
            continue
        if path.stat().st_mtime < min_mtime:
            continue
        candidates.append(path)

    if not candidates:
        return None

    return max(candidates, key=lambda item: item.stat().st_mtime)


def parse_chatgpt_tab_location(raw: str) -> ChatGPTTabLocation:
    try:
        window_text, tab_text, _url = raw.split("|", 2)
        return ChatGPTTabLocation(window_index=int(window_text), tab_index=int(tab_text))
    except Exception as exc:
        raise RuntimeError("Could not locate an open chatgpt.com tab in Google Chrome.") from exc


def default_chatgpt_url() -> str:
    return "https://chatgpt.com/images"


def is_chatgpt_url(url: str) -> bool:
    return any(domain in url for domain in CHATGPT_DOMAINS)


def is_chatgpt_images_url(url: str) -> bool:
    return is_chatgpt_url(url) and "/images" in url


def is_chatgpt_conversation_url(url: str) -> bool:
    return is_chatgpt_url(url) and "/c/" in url


def parse_chatgpt_tab_rows(raw_rows: list[str]) -> list[tuple[ChatGPTTabLocation, str]]:
    parsed_rows: list[tuple[ChatGPTTabLocation, str]] = []
    for row in raw_rows:
        if not row.strip():
            continue
        try:
            location = parse_chatgpt_tab_location(row)
            _window_text, _tab_text, url = row.split("|", 2)
            parsed_rows.append((location, url))
        except RuntimeError:
            continue
    return parsed_rows


def pick_preferred_chatgpt_tab(raw_rows: list[str]) -> ChatGPTTabLocation | None:
    parsed_rows = parse_chatgpt_tab_rows(raw_rows)
    for location, url in parsed_rows:
        if is_chatgpt_images_url(url):
            return location
    return None


def choose_or_open_chatgpt_tab(
    *,
    raw_rows: list[str],
    opened_location: ChatGPTTabLocation,
) -> ChatGPTTabResolution:
    existing = pick_preferred_chatgpt_tab(raw_rows)
    if existing is not None:
        return ChatGPTTabResolution(action="reuse", location=existing)
    return ChatGPTTabResolution(action="open", location=opened_location)


def pick_result_chatgpt_tab(
    *,
    before_rows: list[str],
    after_rows: list[str],
    origin_location: ChatGPTTabLocation,
) -> ChatGPTTabLocation | None:
    after_parsed = parse_chatgpt_tab_rows(after_rows)
    for location, url in after_parsed:
        if location == origin_location and is_chatgpt_conversation_url(url):
            return location

    before_set = set(before_rows)
    for row in after_rows:
        if row in before_set:
            continue
        try:
            location = parse_chatgpt_tab_location(row)
            _window_text, _tab_text, url = row.split("|", 2)
        except RuntimeError:
            continue
        if is_chatgpt_conversation_url(url):
            return location

    return None


def find_new_gallery_cards(
    baseline_cards: list[GalleryImageCard],
    current_cards: list[GalleryImageCard],
) -> list[GalleryImageCard]:
    baseline_keys = {(card.button_aria, card.image_src) for card in baseline_cards}
    return [
        card
        for card in current_cards
        if (card.button_aria, card.image_src) not in baseline_keys
    ]


def run_osascript(script: str, *args: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".applescript", delete=False) as script_file:
        script_file.write(script)
        script_path = Path(script_file.name)

    try:
        result = subprocess.run(
            ["osascript", str(script_path), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        script_path.unlink(missing_ok=True)

    if result.returncode != 0:
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()
        message = stderr or stdout or "osascript failed"
        raise RuntimeError(message)

    return result.stdout.strip()


def is_chrome_running() -> bool:
    result = subprocess.run(
        ["pgrep", "-x", CHROME_APP_NAME],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def ensure_chrome_running(timeout_seconds: int = CHROME_STARTUP_TIMEOUT_SECONDS) -> None:
    if is_chrome_running():
        return

    result = subprocess.run(
        ["open", "-a", CHROME_APP_NAME],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Could not start Google Chrome."
        raise RuntimeError(message)

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if is_chrome_running():
            return
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError("Timed out while starting Google Chrome.")


def list_chrome_tab_rows() -> list[str]:
    if not is_chrome_running():
        return []

    script = f"""
on run
  tell application "{CHROME_APP_NAME}"
    set outputLines to {{}}
    repeat with w from 1 to count of windows
      repeat with t from 1 to count of tabs of window w
        try
          set theUrl to URL of tab t of window w
          copy (w as string) & "|" & (t as string) & "|" & theUrl to end of outputLines
        end try
      end repeat
    end repeat

    set AppleScript's text item delimiters to linefeed
    set outputText to outputLines as text
    set AppleScript's text item delimiters to ""
    return outputText
  end tell
end run
"""
    raw = run_osascript(script)
    return [line.strip() for line in raw.splitlines() if line.strip()]


def open_chatgpt_tab(url: str) -> None:
    result = subprocess.run(
        ["open", "-a", CHROME_APP_NAME, url],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"Could not open {url} in Google Chrome."
        raise RuntimeError(message)


def wait_for_opened_chatgpt_tab(
    *,
    existing_rows: set[str],
    timeout_seconds: int = CHAT_TAB_OPEN_TIMEOUT_SECONDS,
) -> ChatGPTTabLocation:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        raw_rows = list_chrome_tab_rows()
        preferred = pick_preferred_chatgpt_tab(raw_rows)
        if preferred is not None:
            new_rows = [row for row in raw_rows if row not in existing_rows]
            opened_location = pick_preferred_chatgpt_tab(new_rows)
            if opened_location is not None:
                return choose_or_open_chatgpt_tab(
                    raw_rows=raw_rows,
                    opened_location=opened_location,
                ).location
            return preferred
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError("Timed out while opening a usable chatgpt.com chat tab in Google Chrome.")


def locate_chatgpt_tab() -> ChatGPTTabLocation:
    ensure_chrome_running()
    raw_rows = list_chrome_tab_rows()
    existing = pick_preferred_chatgpt_tab(raw_rows)
    if existing is not None:
        return existing

    existing_rows = set(raw_rows)
    open_chatgpt_tab(default_chatgpt_url())
    return wait_for_opened_chatgpt_tab(existing_rows=existing_rows)


def focus_chatgpt_tab(location: ChatGPTTabLocation) -> None:
    script = f"""
on run argv
  set windowIndex to (item 1 of argv) as integer
  set tabIndex to (item 2 of argv) as integer
  tell application "{CHROME_APP_NAME}"
    activate
    set active tab index of window windowIndex to tabIndex
  end tell
end run
"""
    run_osascript(script, str(location.window_index), str(location.tab_index))


def execute_chrome_javascript(location: ChatGPTTabLocation, javascript: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as js_file:
        js_file.write(javascript)
        js_path = Path(js_file.name)

    script = f"""
on run argv
  set jsPath to item 1 of argv
  set windowIndex to (item 2 of argv) as integer
  set tabIndex to (item 3 of argv) as integer
  set jsText to read POSIX file jsPath
  tell application "{CHROME_APP_NAME}"
    return execute (tab tabIndex of window windowIndex) javascript jsText
  end tell
end run
"""

    try:
        return run_osascript(script, str(js_path), str(location.window_index), str(location.tab_index))
    finally:
        js_path.unlink(missing_ok=True)


def build_close_modal_js() -> str:
    return """
(() => {
  const clickButton = (button) => {
    if (!button) return false;
    button.click();
    return true;
  };

  const buttons = [...document.querySelectorAll('button')];
  const closeButton = buttons.find((button) => {
    const label = (button.getAttribute('aria-label') || '').trim();
    const text = (button.innerText || button.textContent || '').trim();
    return label === 'Close' || label === '关闭' || text === 'Close' || text === '关闭';
  });

  if (clickButton(closeButton)) {
    return 'CLOSED';
  }

  document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  document.dispatchEvent(new KeyboardEvent('keyup', { key: 'Escape', bubbles: true }));
  return 'ESCAPED';
})();
"""


def build_image_count_js() -> str:
    return """
(() => {
  const openImageCount = [...document.querySelectorAll('button')].filter((button) => {
    const label = (button.getAttribute('aria-label') || '').trim();
    return label.startsWith('Open image:');
  }).length;
  const editCount = document.querySelectorAll('button[aria-label="Edit image"]').length;
  const imageCount = [...document.querySelectorAll('img')].filter((img) => {
    const alt = (img.alt || '').trim();
    return alt.startsWith('Generated image:');
  }).length;
  return String(Math.max(openImageCount, editCount, imageCount));
})();
"""


def build_result_page_state_js() -> str:
    return """
(() => {
  const generatedPrefixes = ['Generated image:', '生成的图片：'];
  const matchesGenerated = (text) => {
    const trimmed = (text || '').trim();
    return generatedPrefixes.some((prefix) => trimmed.startsWith(prefix));
  };

  const generatedImageButtons = [...document.querySelectorAll('button')]
    .map((button) => {
      const label = (button.getAttribute('aria-label') || '').trim();
      if (matchesGenerated(label)) {
        return label;
      }

      const image = button.querySelector('img');
      const alt = image ? (image.alt || '').trim() : '';
      if (matchesGenerated(alt)) {
        return alt;
      }

      return null;
    })
    .filter(Boolean);

  const generatedImageAlts = [...document.querySelectorAll('img')]
    .map((img) => (img.alt || '').trim())
    .filter((alt) => matchesGenerated(alt));

  const hasSaveButton = [...document.querySelectorAll('button')].some((button) => {
    if (button.disabled) return false;
    const label = (button.getAttribute('aria-label') || '').trim();
    const text = (button.innerText || button.textContent || '').trim();
    return label === 'Save' || label === '保存' || text === 'Save' || text === '保存';
  });

  return JSON.stringify({
    generated_image_buttons: generatedImageButtons,
    generated_image_alts: generatedImageAlts,
    has_save_button: hasSaveButton,
  });
})();
"""


def build_gallery_cards_js() -> str:
    return """
(() => {
  const getImageSrc = (button) => {
    let node = button;
    for (let depth = 0; depth < 8 && node; depth += 1, node = node.parentElement) {
      const image = node.querySelector('img');
      if (!image) continue;
      const src = image.currentSrc || image.src || '';
      if (src && !src.startsWith('data:')) {
        return src;
      }
    }
    return '';
  };

  const cards = [...document.querySelectorAll('button')]
    .map((button) => {
      const label = (button.getAttribute('aria-label') || '').trim();
      if (!label.startsWith('Open image:')) {
        return null;
      }
      const src = getImageSrc(button);
      if (!src) {
        return null;
      }
      return {
        button_aria: label,
        image_src: src,
      };
    })
    .filter(Boolean);

  return JSON.stringify(cards);
})();
"""


def build_fill_prompt_js(prompt: str) -> str:
    prompt_base64 = base64.b64encode(prompt.encode("utf-8")).decode("ascii")
    return f"""
(() => {{
  const promptBytes = Uint8Array.from(atob({json.dumps(prompt_base64)}), (char) => char.charCodeAt(0));
  const prompt = new TextDecoder().decode(promptBytes);
  const editors = [...document.querySelectorAll('[contenteditable="true"]')];
  const editor = editors.find((element) => element.classList.contains('ProseMirror'))
    || editors.find((element) => element.getAttribute('role') === 'textbox')
    || editors[0]
    || document.querySelector('textarea[aria-label="Chat with ChatGPT"]');
  const textarea = document.querySelector('textarea[aria-label="Chat with ChatGPT"]');

  if (!editor) {{
    return 'EDITOR_NOT_FOUND';
  }}

  editor.focus();
  editor.textContent = prompt;
  editor.dispatchEvent(new InputEvent('input', {{
    bubbles: true,
    cancelable: true,
    data: prompt,
    inputType: 'insertText',
  }}));
  editor.dispatchEvent(new Event('change', {{ bubbles: true }}));

  if (textarea) {{
    textarea.value = prompt;
    textarea.dispatchEvent(new InputEvent('input', {{
      bubbles: true,
      cancelable: true,
      data: prompt,
      inputType: 'insertText',
    }}));
    textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
  }}

  return 'FILLED';
}})();
"""


def build_prompt_ui_ready_js() -> str:
    return """
(() => {
  const editors = [...document.querySelectorAll('[contenteditable="true"]')];
  const editor = editors.find((element) => element.classList.contains('ProseMirror'))
    || editors.find((element) => element.getAttribute('role') === 'textbox')
    || document.querySelector('textarea[aria-label="Chat with ChatGPT"]');
  return editor ? 'READY' : 'WAITING';
})();
"""


def build_page_access_state_js() -> str:
    return """
(() => {
  const bodyText = (document.body?.innerText || '').replace(/\\s+/g, ' ').trim();
  const text = bodyText.slice(0, 1200);
  const editors = [...document.querySelectorAll('[contenteditable="true"]')];
  const editor = editors.find((element) => element.classList.contains('ProseMirror'))
    || editors.find((element) => element.getAttribute('role') === 'textbox')
    || document.querySelector('textarea[aria-label="Chat with ChatGPT"]');

  const includesAny = (phrases) => phrases.some((phrase) => text.includes(phrase));
  const isLoginRequired = location.href.includes('/auth')
    || includesAny([
      'Log in',
      'Sign up',
      'Continue with Google',
      'Continue with Apple',
      'Continue with email',
      '登录',
      '注册',
      '继续使用 Google',
      '继续使用 Apple',
      '使用邮箱继续',
    ]);
  const isImageGenerationUnavailable = includesAny([
    'image generation is unavailable',
    'Image generation is unavailable',
    'You do not have access to image generation',
    'You do not have access to images',
    'Your plan does not include image generation',
    'Upgrade to Plus',
    'Upgrade plan',
    'Get Plus',
    '图像生成不可用',
    '图像生成功能不可用',
    '当前套餐不支持图像生成',
    '你当前无法使用图像生成',
    '升级到 Plus',
    '升级套餐',
  ]);

  return JSON.stringify({
    url: location.href,
    has_editor: Boolean(editor),
    is_login_required: isLoginRequired,
    is_image_generation_unavailable: isImageGenerationUnavailable,
    text_excerpt: text,
  });
})();
"""


def build_send_button_ready_js() -> str:
    return """
(() => {
  const sendButton = [...document.querySelectorAll('button')].find((button) => {
    const label = (button.getAttribute('aria-label') || '').trim();
    const text = (button.innerText || button.textContent || '').trim();
    return !button.disabled && (label === 'Send prompt' || label === '发送' || text === 'Send' || text === '发送');
  });
  return sendButton ? 'READY' : 'WAITING';
})();
"""


def build_click_send_button_js() -> str:
    return """
(() => {
  const sendButton = [...document.querySelectorAll('button')].find((button) => {
    const label = (button.getAttribute('aria-label') || '').trim();
    const text = (button.innerText || button.textContent || '').trim();
    return !button.disabled && (label === 'Send prompt' || label === '发送' || text === 'Send' || text === '发送');
  });
  if (!sendButton) {
    return 'SEND_NOT_FOUND';
  }
  sendButton.click();
  return 'SUBMITTED';
})();
"""


def build_open_latest_image_js() -> str:
    return """
(() => {
  const generatedPrefixes = ['Generated image:', '生成的图片：'];
  const matchesGenerated = (text) => {
    const trimmed = (text || '').trim();
    return generatedPrefixes.some((prefix) => trimmed.startsWith(prefix));
  };

  const fireDoubleClick = (node) => {
    if (!node) return false;
    node.scrollIntoView({ block: 'center', inline: 'center', behavior: 'instant' });
    for (const type of ['pointerdown', 'mousedown', 'mouseup', 'click', 'pointerdown', 'mousedown', 'mouseup', 'click', 'dblclick']) {
      const EventCtor = type.startsWith('pointer') ? PointerEvent : MouseEvent;
      node.dispatchEvent(new EventCtor(type, { bubbles: true, cancelable: true, view: window }));
    }
    if (typeof node.click === 'function') {
      node.click();
      node.click();
    }
    return true;
  };

  const generatedButtons = [...document.querySelectorAll('button')].filter((button) => {
    const label = (button.getAttribute('aria-label') || '').trim();
    if (matchesGenerated(label)) {
      return true;
    }
    const image = button.querySelector('img');
    return image ? matchesGenerated(image.alt || '') : false;
  });

  const openButton = generatedButtons.at(-1);
  if (fireDoubleClick(openButton)) {
    return 'OPENED';
  }

  const images = [...document.querySelectorAll('img')].filter((img) => {
    return matchesGenerated(img.alt || '');
  });

  const target = images.at(-1);
  if (!target) {
    return 'IMAGE_NOT_FOUND';
  }

  const clickable = target.closest('[role="button"], button, a') || target;
  return fireDoubleClick(clickable) ? 'OPENED' : 'IMAGE_NOT_FOUND';
})();
"""


def build_open_gallery_card_js(card: GalleryImageCard) -> str:
    return f"""
(() => {{
  const targetLabel = {json.dumps(card.button_aria)};
  const targetSrc = {json.dumps(card.image_src)};
  const getImageSrc = (button) => {{
    let node = button;
    for (let depth = 0; depth < 8 && node; depth += 1, node = node.parentElement) {{
      const image = node.querySelector('img');
      if (!image) continue;
      const src = image.currentSrc || image.src || '';
      if (src && !src.startsWith('data:')) {{
        return src;
      }}
    }}
    return '';
  }};

  const button = [...document.querySelectorAll('button')].find((candidate) => {{
    const label = (candidate.getAttribute('aria-label') || '').trim();
    if (label !== targetLabel) {{
      return false;
    }}
    return getImageSrc(candidate) === targetSrc;
  }});

  if (!button) {{
    return 'IMAGE_NOT_FOUND';
  }}

  button.scrollIntoView({{ block: 'center', inline: 'center', behavior: 'instant' }});
  button.click();
  button.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
  return 'OPENED';
}})();
"""


def build_save_image_js() -> str:
    return """
(() => {
  const buttons = [...document.querySelectorAll('button')];
  const saveButton = buttons.find((button) => {
    if (button.disabled) return false;
    const label = (button.getAttribute('aria-label') || '').trim();
    const text = (button.innerText || button.textContent || '').trim();
    return label === 'Save' || label === '保存' || text === 'Save' || text === '保存';
  });

  if (!saveButton) {
    return 'SAVE_NOT_FOUND';
  }

  saveButton.click();
  return 'SAVE_CLICKED';
})();
"""


def parse_result_page_state(raw: str) -> ResultPageState:
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse result page state from Chrome: {raw!r}") from exc

    button_values = tuple(
        str(value).strip() for value in parsed.get("generated_image_buttons", []) if str(value).strip()
    )
    alt_values = tuple(
        str(value).strip() for value in parsed.get("generated_image_alts", []) if str(value).strip()
    )
    has_save_button = bool(parsed.get("has_save_button"))
    return ResultPageState(
        generated_image_buttons=button_values,
        generated_image_alts=alt_values,
        has_save_button=has_save_button,
    )


def parse_page_access_state(raw: str) -> PageAccessState:
    try:
        parsed = json.loads(raw or "{}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse page access state from Chrome: {raw!r}") from exc

    return PageAccessState(
        url=str(parsed.get("url", "")).strip(),
        has_editor=bool(parsed.get("has_editor")),
        is_login_required=bool(parsed.get("is_login_required")),
        is_image_generation_unavailable=bool(parsed.get("is_image_generation_unavailable")),
        text_excerpt=str(parsed.get("text_excerpt", "")).strip(),
    )


def get_result_page_state(location: ChatGPTTabLocation) -> ResultPageState:
    raw = execute_chrome_javascript(location, build_result_page_state_js())
    return parse_result_page_state(raw)


def get_page_access_state(location: ChatGPTTabLocation) -> PageAccessState:
    raw = execute_chrome_javascript(location, build_page_access_state_js())
    return parse_page_access_state(raw)


def describe_page_access_issue(state: PageAccessState) -> str | None:
    if state.is_login_required:
        return "ChatGPT is not logged in in Google Chrome. Please log in to https://chatgpt.com/images and try again."
    if state.is_image_generation_unavailable:
        return "This ChatGPT account or session does not currently support image generation on https://chatgpt.com/images. Please switch to an account with image generation access and try again."
    return None


def result_page_has_generated_image(state: ResultPageState) -> bool:
    return bool(state.generated_image_buttons or state.generated_image_alts)


def get_gallery_cards(location: ChatGPTTabLocation) -> list[GalleryImageCard]:
    raw = execute_chrome_javascript(location, build_gallery_cards_js())
    try:
        parsed = json.loads(raw or "[]")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse gallery cards from Chrome: {raw!r}") from exc

    cards: list[GalleryImageCard] = []
    for item in parsed:
        button_aria = str(item.get("button_aria", "")).strip()
        image_src = str(item.get("image_src", "")).strip()
        if button_aria and image_src:
            cards.append(GalleryImageCard(button_aria=button_aria, image_src=image_src))
    return cards


def wait_for_gallery_cards_to_settle(
    location: ChatGPTTabLocation,
    *,
    timeout_seconds: int = 20,
    settle_seconds: float = 2.0,
) -> list[GalleryImageCard]:
    deadline = time.time() + timeout_seconds
    last_cards: list[GalleryImageCard] | None = None
    stable_since: float | None = None

    while time.time() < deadline:
        cards = get_gallery_cards(location)
        if cards == last_cards:
            if stable_since is None:
                stable_since = time.time()
            if time.time() - stable_since >= settle_seconds:
                return cards
        else:
            last_cards = cards
            stable_since = time.time()
        time.sleep(POLL_INTERVAL_SECONDS)

    return last_cards or []


def wait_for_new_gallery_card(
    location: ChatGPTTabLocation,
    *,
    baseline_cards: list[GalleryImageCard],
    timeout_seconds: int,
) -> GalleryImageCard:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        current_cards = get_gallery_cards(location)
        new_cards = find_new_gallery_cards(baseline_cards, current_cards)
        if new_cards:
            return new_cards[0]
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError("Timed out while waiting for a newly generated image card in ChatGPT Images.")


def wait_for_result_chatgpt_tab(
    *,
    origin_location: ChatGPTTabLocation,
    before_rows: list[str],
    timeout_seconds: int,
) -> ChatGPTTabLocation:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        after_rows = list_chrome_tab_rows()
        result_location = pick_result_chatgpt_tab(
            before_rows=before_rows,
            after_rows=after_rows,
            origin_location=origin_location,
        )
        if result_location is not None:
            return result_location
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError("Timed out while waiting for the ChatGPT Images request to open its result page.")


def wait_for_generated_image_on_result_page(
    location: ChatGPTTabLocation,
    *,
    timeout_seconds: int,
) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if result_page_has_generated_image(get_result_page_state(location)):
            return
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError("Timed out while waiting for the generated image to appear on the result page.")


def wait_for_image_preview_on_result_page(
    location: ChatGPTTabLocation,
    *,
    timeout_seconds: int,
) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if get_result_page_state(location).has_save_button:
            return
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError("Timed out while waiting for the generated image preview to open in ChatGPT.")


def wait_for_js_result(
    location: ChatGPTTabLocation,
    javascript: str,
    *,
    expected: str,
    timeout_seconds: int,
) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        result = execute_chrome_javascript(location, javascript).strip()
        if result == expected:
            return
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError(f"Timed out while waiting for Chrome result {expected!r}.")


def wait_for_prompt_ui_ready(
    location: ChatGPTTabLocation,
    *,
    timeout_seconds: int,
) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        state = get_page_access_state(location)
        access_issue = describe_page_access_issue(state)
        if access_issue is not None:
            raise RuntimeError(access_issue)
        if state.has_editor:
            return
        time.sleep(POLL_INTERVAL_SECONDS)

    state = get_page_access_state(location)
    access_issue = describe_page_access_issue(state)
    if access_issue is not None:
        raise RuntimeError(access_issue)
    raise RuntimeError("Timed out while waiting for the ChatGPT Images prompt editor to load in Google Chrome.")


def wait_for_download(
    *,
    downloads_dir: Path,
    existing_names: set[str],
    min_mtime: float,
    timeout_seconds: int,
) -> Path:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        download = find_new_download(
            downloads_dir=downloads_dir,
            existing_names=existing_names,
            min_mtime=min_mtime,
        )
        if download is not None:
            return download
        time.sleep(POLL_INTERVAL_SECONDS)

    raise RuntimeError(f"Timed out while waiting for a new download in {downloads_dir}.")


def move_download_to_output(downloaded_file: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        raise RuntimeError(f"Output path already exists: {output_path}")
    shutil.move(str(downloaded_file), str(output_path))
    return output_path


def generate_image(
    *,
    prompt: str,
    requested_out: str | None,
    downloads_dir: Path,
    timeout_seconds: int,
) -> Path:
    location = locate_chatgpt_tab()
    focus_chatgpt_tab(location)
    wait_for_prompt_ui_ready(location, timeout_seconds=60)
    execute_chrome_javascript(location, build_close_modal_js())
    time.sleep(0.5)

    before_rows = list_chrome_tab_rows()
    fill_result = execute_chrome_javascript(location, build_fill_prompt_js(prompt)).strip()
    if fill_result == "EDITOR_NOT_FOUND":
        raise RuntimeError("Could not find the ChatGPT prompt editor in the current Chrome tab.")
    if fill_result != "FILLED":
        raise RuntimeError(f"Unexpected prompt fill result: {fill_result}")

    wait_for_js_result(
        location,
        build_send_button_ready_js(),
        expected="READY",
        timeout_seconds=30,
    )
    submit_result = execute_chrome_javascript(location, build_click_send_button_js()).strip()
    if submit_result != "SUBMITTED":
        raise RuntimeError(f"Unexpected prompt submission result: {submit_result}")

    result_location = wait_for_result_chatgpt_tab(
        origin_location=location,
        before_rows=before_rows,
        timeout_seconds=timeout_seconds,
    )
    focus_chatgpt_tab(result_location)
    wait_for_generated_image_on_result_page(
        result_location,
        timeout_seconds=timeout_seconds,
    )

    open_result = execute_chrome_javascript(result_location, build_open_latest_image_js()).strip()
    if open_result != "OPENED":
        raise RuntimeError("Could not open the newly generated image preview in ChatGPT.")
    wait_for_image_preview_on_result_page(
        result_location,
        timeout_seconds=30,
    )

    existing_names = {path.name for path in downloads_dir.iterdir()} if downloads_dir.exists() else set()
    min_mtime = time.time()

    wait_for_js_result(
        result_location,
        build_save_image_js(),
        expected="SAVE_CLICKED",
        timeout_seconds=30,
    )

    downloaded_file = wait_for_download(
        downloads_dir=downloads_dir,
        existing_names=existing_names,
        min_mtime=min_mtime,
        timeout_seconds=timeout_seconds,
    )

    output_path = choose_output_path(
        requested_out=requested_out,
        downloaded_file=downloaded_file,
        home=Path.home(),
        now=datetime.now(),
    )
    return move_download_to_output(downloaded_file, output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate one image via https://chatgpt.com/images in the current Google Chrome session.",
    )
    parser.add_argument("--prompt", required=True, help="Prompt to send to https://chatgpt.com/images for image generation.")
    parser.add_argument("--out", help="Optional absolute or relative output path for the saved image.")
    parser.add_argument(
        "--downloads-dir",
        default=str(Path.home() / "Downloads"),
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=argparse.SUPPRESS,
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = generate_image(
        prompt=args.prompt,
        requested_out=args.out,
        downloads_dir=Path(args.downloads_dir).expanduser(),
        timeout_seconds=args.timeout_seconds,
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
