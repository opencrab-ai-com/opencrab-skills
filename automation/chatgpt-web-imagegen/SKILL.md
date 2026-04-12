---
name: "chatgpt-web-imagegen"
description: "Use when the user wants to generate a single bitmap image, especially when browser-based generation through the logged-in ChatGPT Images website in Google Chrome should be the preferred path."
---

# ChatGPT Web Imagegen

Generate one image through `https://chatgpt.com/images` in the user's existing Google Chrome session.

## When to use

- Prefer this skill for single-image generation requests that can use the ChatGPT website in Chrome
- The user explicitly wants browser-based generation through ChatGPT itself
- The user wants to reuse an already logged-in Chrome session
- The task is a one-image-at-a-time workflow

## Workflow

1. Run `scripts/generate_chatgpt_image.py --prompt "..."`.
2. Let the script reuse an existing `https://chatgpt.com/images` tab or open a fresh one.
3. Wait for the image to finish generating.
4. Return the saved absolute file path.

## Defaults

- Output directory: `~/Desktop/ImagesGenByChatgpt`
- Create the output directory first if it does not already exist
- Browser: `Google Chrome`
- One image per run

## Notes

- The script opens `https://chatgpt.com/images` automatically if there is no usable tab.
- It expects the user to already be logged into ChatGPT in Chrome.
- If ChatGPT is not logged in, the script should tell the user to log in first.
- If the current ChatGPT account or plan does not support image generation, the script should tell the user directly.
