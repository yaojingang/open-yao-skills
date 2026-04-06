# openyao-skills

`openyao-skills` 是一个面向公开分享的 Skill 合集仓库。它只收录适合开源、可长期维护、可被他人直接理解和复用的 Skill。

这个目录同时承担两件事：

- 作为 GitHub 开源合集的本地工作区。
- 作为本地同步管理中心，记录哪些 Skill 已纳入合集、当前公开状态如何、说明页是否已更新。
- 作为后续版本迭代的发布入口，在每次确认更新后同步推送到 GitHub。

## 仓库目标

- 把零散的本地 Skill 整理成一个稳定的公开合集。
- 为每个公开 Skill 保留清晰的来源、收录路径、同步状态和许可证信息。
- 用统一规则筛选 Skill，避免把私有数据、输出产物和实验垃圾一起推到公开仓库。

## 公开收录标准

- 主题清晰：别人看到 Skill 名称和说明就知道它解决什么问题。
- 可复用：不依赖你个人电脑上的私有上下文才能运行。
- 可清理：能移除敏感信息、缓存、输出物、账号痕迹和内部文档。
- 可维护：你愿意继续修复、迭代和解释它。

详细规则见：

- [docs/repository-design.md](/Users/laoyao/AI Coding/03-Development/Skills/openyao-skills/docs/repository-design.md)
- [docs/publishing-rules.md](/Users/laoyao/AI Coding/03-Development/Skills/openyao-skills/docs/publishing-rules.md)

## 目录结构

```text
openyao-skills/
├── README.md
├── docs/
├── registry/
├── scripts/
└── skills/
```

- `docs/`: 仓库设计、发布规则、同步规范。
- `registry/`: Skill 登记表，是本地和公开状态的事实源。
- `scripts/`: 更新登记表和 README 的辅助脚本。
- `skills/`: 真正收录进公开合集的 Skill 副本。

## 工作流

1. 你给出一个本地 Skill 路径。
2. 按规则判断这个 Skill 是否适合公开。
3. 清理敏感文件和无关产物后，复制到 `skills/<slug>/`。
4. 在 `registry/skills.json` 写入或更新登记信息。
5. 运行 README 渲染脚本，刷新合集说明页。
6. 如果你要发布，再把仓库推到 GitHub 的 `openyao-skills`。

## GitHub 发布约定

- GitHub 仓库名固定为 `openyao-skills`。
- 本地集合完成变更后，先更新 `registry/skills.json` 和 README，再执行 Git 提交与推送。
- 只有实际完成推送后，相关 Skill 才能标记为 `published`，并写入 `last_synced_at`。
- 如果后续本地源 Skill 有变化，但 GitHub 还没更新，对应记录应标记为 `needs-update`。

## 本地管理 Skill

这个仓库内置了一个管理 Skill：

- [skills/openyao-skills-sync/SKILL.md](/Users/laoyao/AI Coding/03-Development/Skills/openyao-skills/skills/openyao-skills-sync/SKILL.md)

它的职责是：

- 接收你给的本地 Skill 路径。
- 判断是否适合公开。
- 按合集规则导入到 `openyao-skills`。
- 维护登记表和 README 目录页。
- 记录这个 Skill 是否已经同步到 GitHub，以及线上对应路径。

## Skill Catalog

<!-- catalog:start -->
| Skill | Lifecycle | Sync | Collection Path | Source Path | GitHub |
| --- | --- | --- | --- | --- | --- |
| `openyao-skills-sync` | `active` | `local-only` | `skills/openyao-skills-sync` | `/Users/laoyao/AI Coding/03-Development/Skills/openyao-skills/skills/openyao-skills-sync` | `pending` |
<!-- catalog:end -->

## 后续约定

- `registry/skills.json` 是事实源。
- README 中的目录表由脚本生成，不手工维护。
- 任何新收录 Skill，都必须先过发布规则，再更新登记表和 README。
- 任何准备公开的变更，都应在整理完成后推送到 GitHub 远程仓库。
