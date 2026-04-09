# open-yao-skills 仓库设计

## 0. 理念

`open-yao-skills` 采用 `YAO = Yielding AI Outcomes` 的方法视角。

这里的重点不是累积更多提示词，而是沉淀更好的 AI 资产。一个 Skill 值得进入这个公开合集，不是因为它“能聊”，而是因为它能稳定支持某类真实任务，能被复用，能被维护，也能被别人理解和继续改进。

因此这个仓库的设计目标从一开始就不是“仓储式归档”，而是“公开资产治理”：

- 以结果为导向，而不是以 prompt 数量为导向
- 以方法和边界为导向，而不是以一次性技巧为导向
- 以长期维护为导向，而不是以短期堆叠为导向

与这个公开合集最相关的元项目是：

- [yao-meta-skill](https://github.com/yaojingang/yao-meta-skill)

它定义的是如何创建、评估、治理和打包 Skill；而 `open-yao-skills` 负责承接其中那些已经值得公开分享的成果。

相关命名规则见：

- [naming-conventions.md](naming-conventions.md)

## 1. 定位

`open-yao-skills` 不是“当前 Skills 工作区的完整镜像”，而是一个精选的公开合集仓库。

它只收录满足下面条件的 Skill：

- 适合开源分享
- 有明确用途和边界
- 可以脱离个人隐私环境进行理解和复用
- 值得长期维护

这意味着原始工作区和公开合集之间必须允许存在差异。公开合集优先追求质量、一致性和可维护性，不追求全量收录。

## 2. 事实源

仓库内有三个核心事实源，各自职责固定：

- `skills/<slug>/`: 公开版 Skill 实体目录
- `registry/skills.json`: 收录、同步和来源状态的结构化登记表
- `README.md`: 面向人阅读的合集首页，由登记表生成目录区块
- `docs/skills/<slug>.md`: 面向人阅读的每个 Skill 使用说明

约束如下：

- Skill 的真实公开内容以 `skills/<slug>/` 为准
- Skill 的状态以 `registry/skills.json` 为准
- README 只做展示，不手工当事实源维护
- 每个已开源 Skill 都应有对应的 guide 文档

## 3. 目录规则

```text
open-yao-skills/
├── README.md
├── .gitignore
├── docs/
│   ├── repository-design.md
│   └── publishing-rules.md
├── registry/
│   └── skills.json
├── scripts/
│   ├── register_skill.py
│   └── render_readme_catalog.py
└── skills/
    └── <skill-slug>/
        ├── SKILL.md
        ├── scripts/         # optional
        ├── references/      # optional
        └── assets/          # optional
```

设计原则：

- `skills/` 目录只放“公开副本”，不做软链接。
- 每个收录 Skill 都使用稳定 slug，目录名和登记表 slug 一致。
- `docs/` 解释仓库治理，不替代 Skill 自身说明。
- `scripts/` 只放仓库级维护脚本，不放具体 Skill 的业务脚本。
- 可以为未来能力家族预留空目录，例如 `skill-builder`、`skill-analyzer`，但不要把占位目录当成已发布 Skill 登记。

## 3.1 命名系统

`OpenYao` 需要的是一套稳定的产品命名系统，而不是临时想到什么就加什么。

推荐长期保持这种风格：

- 功能导向
- 动词感明确
- 名称一眼能被传播和记忆

例如：

- `skill-doctor`
- `skill-optimizer`
- `skill-ranker`

不建议在同一层核心产品线中混入风格偏散的名称，例如：

- `audit`
- `hygiene`
- `inspector`

原因不是这些词不能用，而是它们会打散用户对整套体系的认知。仓库需要的是“系列感”，不是局部准确但整体松散的命名。

## 4. 状态模型

每个 Skill 记录两组状态：

- `lifecycle`
- `sync_status`

推荐枚举：

- `lifecycle`: `active` / `deprecated` / `archived`
- `sync_status`: `local-only` / `staged` / `published` / `needs-update`

含义：

- `local-only`: 已在本地集合中登记，但还没公开推送到 GitHub
- `staged`: 已整理进合集目录，待最终发布确认
- `published`: 已同步到 GitHub 公共仓库
- `needs-update`: 线上已有版本，但本地源 Skill 发生变化，待重新同步

## 5. 收录模型

每个 Skill 至少记录这些字段：

- `slug`
- `title`
- `summary`
- `source_local_path`
- `collection_path`
- `lifecycle`
- `sync_status`
- `github_repo`
- `github_url`
- `guide_path`
- `license`
- `tags`
- `last_synced_at`
- `updated_at`

这样做的目的是解决三个管理问题：

- 我本地的哪个 Skill 已被收录
- 它在合集中的哪个目录
- 它是否已经同步到 GitHub 公开仓库
- 它的使用说明应该去哪里看

其中 `source_local_path` 记录的是原始来源路径，通常是导入前的本地目录，而不是复制进合集之后的 `collection_path`。

其中 GitHub 同步状态不是推断值，而是显式登记值。只有仓库已经成功推送后，才允许标记为 `published`。

## 6. 导入原则

从原始工作区导入 Skill 时，默认遵循这些规则：

- 复制公开版副本，不直接暴露原始目录
- 优先保留 `SKILL.md`、必要 `scripts/`、必要 `references/`、必要 `assets/`
- 删除 `output/`、`downloads/`、`node_modules/`、`.venv/`、缓存、临时文件、私有日志
- 先检查该 Skill 已生成的本地输出文件是否包含绝对路径、报告数据、私有样本、账号信息或其他敏感内容
- 原则上不上传本地运行后产生的输出目录、扫描结果、缓存和操作脚本
- 删除账号、令牌、Cookie、内网地址、私有数据样本
- 若依赖个人私有路径，需改成公开可解释的路径或写成说明
- 导入完成后，为该 Skill 新增 `docs/skills/<slug>.md` 使用说明

## 7. README 同步规则

README 的 Skill 目录区块必须从 `registry/skills.json` 自动渲染，不能手工维护。

原因：

- 降低遗漏
- 保证格式统一
- 让 README 和登记表保持一致

## 9. GitHub 发布规则

这个目录默认对应一个公开 GitHub 仓库：

- repo: `yaojingang/open-yao-skills`

发布顺序固定：

1. 更新公开 Skill 内容
2. 更新 `registry/skills.json`
3. 渲染 `README.md`
4. 提交 Git 变更
5. 推送到 GitHub
6. 将已推送 Skill 的 `sync_status` 维护为 `published`

如果本地内容已更新但还没推送，状态应为 `needs-update` 或 `staged`，不能直接写成 `published`。

## 10. 后续扩展

如果以后要把它做成更强的公开项目，可以继续增加：

- 自动校验脚本
- 元数据 schema 校验
- GitHub Actions 校验流程
- 每个 Skill 的预览卡片或示例页

但当前阶段先保持轻量，优先把“收录规则 + 登记 + README 同步”跑通。
