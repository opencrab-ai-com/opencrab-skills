# opencrab-skills
由 Opencrab 精选或者制作的 skills，欢迎大家使用。

## Categories

- `design/`
  - `brand-inspired-ui/`: 从品牌设计参考中挑选合适风格，并输出前端可消费的设计约束、HTML 原型或实现提示。

## brand-inspired-ui

`design/brand-inspired-ui/` 这个 skill 的核心用途是：

- 根据用户直接给出的品牌名匹配设计参考
- 在用户只描述风格时推荐合适品牌
- 输出前端可消费的设计约束、HTML 原型或实现提示

### 来源

这个 skill 的品牌设计参考来源于 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)。

当前仓库将其中公开整理的品牌参考以适合 skill 使用的方式进行了打包，主要包含：

- `DESIGN.md`
- `preview.html`
- `preview-dark.html`

这些文件被放在 `design/brand-inspired-ui/references/brands/` 下，供 `SKILL.md` 在匹配品牌后读取和使用。

### 关于 scripts/

`design/brand-inspired-ui/scripts/sync_awesome_design_md.py` 是一个维护脚本，用来在需要时重新同步上游 `awesome-design-md` 的参考文件。

它不是 skill 的运行时依赖：

- `Codex`
- `Claude Code`
- `Cursor`

在实际使用这个 skill 时，并不会自动调用这个 Python 脚本。skill 的运行时主要依赖：

- `design/brand-inspired-ui/SKILL.md`
- `design/brand-inspired-ui/references/`

也就是说，`scripts/` 目录主要服务于仓库维护者，而不是 skill 的最终使用者。
