# opencrab-skills
由 Opencrab 精选或者制作的通用 AI skills，欢迎大家使用。

本仓库优先追求技能本身的通用性：

- 尽量不绑定某个特定产品或运行时
- 以 `SKILL.md` 作为核心行为说明
- 允许按需附带 `README.md`、脚本、数据或参考资料
- 尽量让 Codex、Claude Code、Cursor 等主流工具都能复用

## Categories

- `automation/`
  - `chatgpt-web-imagegen/`: 通过用户已登录的 Chrome 会话调用 `https://chatgpt.com/images` 生成单张图片，并返回保存路径。详见 [automation/chatgpt-web-imagegen/README.md](automation/chatgpt-web-imagegen/README.md)。

- `design/`
  - `brand-inspired-ui/`: 从品牌设计参考中挑选合适风格，并输出前端可消费的设计约束、HTML 原型或实现提示。详见 [design/brand-inspired-ui/README.md](design/brand-inspired-ui/README.md)。
  - `ui-ux-research/`: 搜索 UI/UX 风格、配色、字体、图表、UX 规则和栈相关设计建议。详见 [design/ui-ux-research/README.md](design/ui-ux-research/README.md)。

- `workflow/`
  - `design-discovery/`: 在实现前澄清需求、比较方案并拿到设计确认。详见 [workflow/design-discovery/README.md](workflow/design-discovery/README.md)。
  - `implementation-planning/`: 将已确认的设计拆成可执行的实现计划。详见 [workflow/implementation-planning/README.md](workflow/implementation-planning/README.md)。
  - `workspace-isolation/`: 用隔离工作区或 git worktree 启动多步骤开发。详见 [workflow/workspace-isolation/README.md](workflow/workspace-isolation/README.md)。

- `quality/`
  - `systematic-debugging/`: 先做根因分析，再修复问题。详见 [quality/systematic-debugging/README.md](quality/systematic-debugging/README.md)。
  - `test-driven-development/`: 用 failing test 驱动实现。详见 [quality/test-driven-development/README.md](quality/test-driven-development/README.md)。
  - `completion-verification/`: 在宣称完成前先做新鲜验证。详见 [quality/completion-verification/README.md](quality/completion-verification/README.md)。
  - `code-review-reception/`: 用技术核验来处理 review 意见，而不是盲从。详见 [quality/code-review-reception/README.md](quality/code-review-reception/README.md)。

- `authoring/`
  - `skill-authoring/`: 创建和迭代高质量、可发现、可复用的 skill。详见 [authoring/skill-authoring/README.md](authoring/skill-authoring/README.md)。

## Notes

- 仓库根 README 只保留分类和导航信息。
- 每个 skill 的来源、目录结构、维护方式和特殊说明，放在各自目录下的 `README.md` 中。
