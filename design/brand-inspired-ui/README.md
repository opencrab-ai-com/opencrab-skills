# brand-inspired-ui

`brand-inspired-ui` 是一个设计参考型 skill。

它的目标是帮助 AI coding agent：

- 根据用户直接给出的品牌名匹配设计参考
- 在用户只描述视觉风格时推荐合适品牌
- 输出前端可消费的设计约束、HTML 原型或实现提示

## Source

这个 skill 中的品牌设计参考主要来源于 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md)。

当前仓库将其中适合直接复用的参考文件整理进了本 skill，主要包括：

- `DESIGN.md`
- `preview.html`
- `preview-dark.html`

这些文件位于：

- `references/brands/<brand>/`

## Runtime vs Maintenance

这个 skill 在实际使用时，主要依赖：

- `SKILL.md`
- `references/catalog.md`
- `references/style-mapping.md`
- `references/brands/`

`scripts/sync_awesome_design_md.py` 不是运行时依赖。

它只是一个维护脚本，用来在需要时从上游 `awesome-design-md` 重新同步参考文件。

也就是说，主流 AI coding agent 在调用这个 skill 时，不会自动执行这个 Python 脚本。

## Layout

```text
brand-inspired-ui/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── catalog.md
│   ├── style-mapping.md
│   └── brands/
└── scripts/
    └── sync_awesome_design_md.py
```

## Notes

- `SKILL.md` 是行为说明的来源
- `agents/openai.yaml` 是面向部分运行时的可选元数据补充
- `scripts/` 目录主要服务于仓库维护者，而不是 skill 的最终使用者
