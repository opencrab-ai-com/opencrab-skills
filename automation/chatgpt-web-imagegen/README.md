# chatgpt-web-imagegen

`chatgpt-web-imagegen` 是一个浏览器自动化型 skill。

它的目标是帮助 AI coding agent：

- 通过用户当前已登录的 Google Chrome 会话打开 `https://chatgpt.com/images`
- 发送单条图片生成 prompt
- 等待图片生成完成并保存到本地
- 返回最终保存路径

## Runtime Requirements

当前实现是平台相关的，主要面向：

- `macOS`
- 已安装 `Google Chrome`
- Chrome 中已经登录 ChatGPT
- 当前账号或套餐支持 `https://chatgpt.com/images` 生图
- 允许脚本通过浏览器自动化控制 Chrome

如果用户未登录，或者当前账号不支持生图，脚本会直接报出明确提示。

## Runtime vs Maintenance

这个 skill 在实际使用时，主要依赖：

- `SKILL.md`
- `agents/openai.yaml`
- `scripts/generate_chatgpt_image.py`

测试文件位于：

- `tests/automation/chatgpt_web_imagegen/test_generate_chatgpt_image.py`

它们用于仓库维护和回归验证，不是运行时依赖。

## Layout

```text
chatgpt-web-imagegen/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
└── scripts/
    └── generate_chatgpt_image.py
```

## Notes

- 这是一个单图工作流，不负责批量生成。
- 默认输出目录是 `~/Desktop/ImagesGenByChatgpt`，不存在时会自动创建。
- 该 skill 依赖 ChatGPT Images 当前网页结构，后续如果站点 UI 变化，脚本可能需要同步更新。
