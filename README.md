# Yao Open Skills

*A curated collection of production-ready AI skills for research, decision, business, learning, and document generation*

`OpenYao` 延续 `YAO = Yielding AI Outcomes` 这条方法线。重点不是继续堆更多 prompt 文本，而是把有效的方法、流程、评估、审美约束和执行边界沉淀成可复用的 AI 资产，并最终产生真实可交付的结果。

Yao Open Skills is a growing collection of AI-native skills designed for real-world work: turning uncertain decisions into reports, turning business questions into structured analysis, and turning topics or reference packets into polished tutorial documents.

这个目录同时承担两件事：

- 作为 GitHub 开源合集的本地工作区。
- 作为本地同步管理中心，记录哪些 Skill 已纳入合集、当前公开状态如何、说明页是否已更新。
- 作为后续版本迭代的发布入口，在每次确认更新后同步推送到 GitHub。

## Navigation

- [OpenYao 理念](#openyao-理念)
- [推荐入口](#推荐入口)
- [Published Skill Guides](#published-skill-guides)
- [Featured Published Skills](#featured-published-skills)
- [Skill Catalog](#skill-catalog)
- [发布规则](docs/publishing-rules.md)
- [命名规范](docs/naming-conventions.md)
- [仓库设计](docs/repository-design.md)

## OpenYao 理念

`yao-open-skills` 想公开的不是“零散 prompt 收藏”，而是一套更稳定的 AI 资产观：

- Skill 应该服务真实任务结果，而不是只服务对话过程。
- Skill 应该可复用、可维护、可评估，而不是一次性技巧。
- Skill 应该能沉淀为团队资产，而不是停留在个人记忆和聊天记录里。
- 开源合集应该强调方法质量、边界清晰和持续演进，而不是数量堆叠。

换句话说，`OpenYao` 是把 `YAO` 的方法论往公开知识库推进一步：让那些值得分享的 Skill，不只存在于本地，而是成为可以被发现、引用、改进和复用的公开能力集合。

## Featured Skill Lines

这部分展示的是 `OpenYao` 计划长期建设的能力线，风格上会尽量保持“功能导向 + 动词感”，避免命名体系散掉。

**Skill Doctor**
Diagnose and fix issues in skills automatically.

**Skill Optimizer**
Improve performance, structure, and effectiveness.

**Skill Ranker**
Evaluate and rank skills based on real impact.

这些名称代表的是产品方向，不等于它们现在都已经作为独立 Skill 收录进仓库。当前仓库会把“已发布能力”和“规划中的能力线”区分开维护。

## 推荐入口

如果你想理解 `OpenYao` 背后的元方法，优先看 [`yao-meta-skill`](https://github.com/yaojingang/yao-meta-skill)。

这是 `YAO` 方法线里的元 Skill 项目，用来把工作流、提示词、笔记和执行经验，进一步沉淀成可创建、可评估、可治理、可打包的 Skill 资产。

在这两个仓库之间，关系可以简单理解为：

- [`yao-meta-skill`](https://github.com/yaojingang/yao-meta-skill): 定义如何系统化地创建、评估、治理和打包 Skill
- [`yao-open-skills`](https://github.com/yaojingang/yao-open-skills): 收录那些已经值得公开分享的 Skill 成果

如果把 `yao-meta-skill` 理解成“元方法引擎”，那么 `yao-open-skills` 更像“公开产品化陈列层”。

## 仓库目标

- 把零散的本地 Skill 整理成一个稳定的公开合集。
- 为每个公开 Skill 保留清晰的来源、收录路径、同步状态和许可证信息。
- 用统一规则筛选 Skill，避免把私有数据、输出产物和实验垃圾一起推到公开仓库。
- 让 `YAO` 方法论下真正有价值的 Skill 形成一个持续演进的公开资产库。

## 公开收录标准

- 主题清晰：别人看到 Skill 名称和说明就知道它解决什么问题。
- 可复用：不依赖你个人电脑上的私有上下文才能运行。
- 可清理：能移除敏感信息、缓存、输出物、账号痕迹和内部文档。
- 可维护：你愿意继续修复、迭代和解释它。

详细规则见：

- [docs/repository-design.md](docs/repository-design.md)
- [docs/naming-conventions.md](docs/naming-conventions.md)
- [docs/publishing-rules.md](docs/publishing-rules.md)

## 目录结构

```text
yao-open-skills/
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

## Planned Capability Families

为了让这个仓库像生态而不是像杂货堆，先预留两条能力家族目录：

- `skills/skill-builder/`
- `skills/skill-analyzer/`

它们当前只是占位目录，用来约束未来的扩展方向。

## Published Skill Guides

- [Skill Guides Index](docs/skills/README.md)
- [Yao Open Skills Sync](docs/skills/yao-open-skills-sync.md)
- [Skill Doctor](docs/skills/skill-doctor.md)
- [Yao Bayesian Skill](docs/skills/yao-bayesian-skill.md)
- [Yao Business Skill](docs/skills/yao-business-skill.md)
- [Yao Kelly Skill](docs/skills/yao-kelly-skill.md)
- [Yao Tutorial Skill](docs/skills/yao-tutorial-skill.md)

## Featured Published Skills

### Yao Tutorial Skill

[`yao-tutorial-skill`](docs/skills/yao-tutorial-skill.md) 是一个“从主题或资料包到完整教程成品”的生产型 Skill。

它不是简单帮你写一篇说明文，而是把输入主题、用户给定资料、权威来源、论文、GitHub 实践和案例证据组织成一套可交付教程包：先归一化需求，再做研究取证，再生成面向小白的章节大纲，最后输出带配图的 `Markdown + Word + PDF + HTML`。

它的公开版本现在有这些比较突出的特点：

- 支持只输入一个主题，也支持输入一组资料、链接、论文、仓库或草稿
- 优先以用户给定资料为核心，资料不足时再补充外部权威来源
- 面向新手写作，标题有用户利益，大纲说人话，章节结构通俗、可执行
- 公开成品不显示 `[U1]`、`[X1]` 这类内部证据角标，也不写“基于原文整理”
- 每个章节都必须有一张对应的可视化配图
- 配图先生成 HTML 画板，再截图嵌入教程内容
- HTML 报告支持居中内容容器、左侧目录、日期、章节跳转和清爽阅读排版
- Word/PDF 默认去掉页眉页脚，避免导出路径、页码和浏览器打印信息干扰阅读
- 内置验证脚本，检查章节、配图、引用、导出文件和本地路径泄漏

如果你想快速理解这个 Skill，建议按这个顺序看：

1. [公开说明文档](docs/skills/yao-tutorial-skill.md)
2. [Skill 入口](skills/yao-tutorial-skill/SKILL.md)
3. [输入适配规则](skills/yao-tutorial-skill/references/input-adaptation.md)
4. [教程写作规则](skills/yao-tutorial-skill/references/tutorial-outline-and-writing.md)
5. [可视化画板规则](skills/yao-tutorial-skill/references/visual-html-workflow.md)
6. [导出与验证脚本](skills/yao-tutorial-skill/scripts/validate_package.py)

### Yao Bayesian Skill

[`yao-bayesian-skill`](docs/skills/yao-bayesian-skill.md) 是当前公开合集里最完整的一类“证据到行动”型 Skill。

它的重点不是把贝叶斯定理讲一遍，而是把一个现实里的不确定问题，压缩成一个能执行、能复盘、能继续迭代的决策流程。

它的公开版本现在有这些比较突出的特点：

- 支持从不完整输入开始，先给弱先验和初步判断
- 支持多轮追问，持续更新先验、后验和决策准备度
- 内置贝叶斯先验检查，从 20 条生活判断原则中挑出本次最相关的 3 到 5 条
- 会记录每一轮对话里，哪些信息改变了判断
- 报告先给普通用户可读的结论，再展示技术细节
- 默认生成 `Markdown + 双语 HTML`
- HTML 支持中英切换、粘性导航、打印，以及在浏览器里直接存储为 PDF

如果你想快速理解这个 Skill，建议按这个顺序看：

1. [公开说明文档](docs/skills/yao-bayesian-skill.md)
2. [Skill 入口](skills/yao-bayesian-skill/SKILL.md)
3. [详细案例输入](skills/yao-bayesian-skill/input/detailed_growth_case.json)
4. [导出脚本](skills/yao-bayesian-skill/scripts/generate_report_bundle.py)
5. [示例报告目录](skills/yao-bayesian-skill/reports/README.md)

## 工作流

1. 你给出一个本地 Skill 路径。
2. 按规则判断这个 Skill 是否适合公开。
3. 清理敏感文件和无关产物后，复制到 `skills/<slug>/`。
4. 在 `registry/skills.json` 写入或更新登记信息。
5. 运行 README 渲染脚本，刷新合集说明页。
6. 如果你要发布，再把仓库推到 GitHub 的 `yao-open-skills`。

## GitHub 发布约定

- GitHub 仓库名固定为 `yao-open-skills`。
- 本地集合完成变更后，先更新 `registry/skills.json` 和 README，再执行 Git 提交与推送。
- 只有实际完成推送后，相关 Skill 才能标记为 `published`，并写入 `last_synced_at`。
- 如果后续本地源 Skill 有变化，但 GitHub 还没更新，对应记录应标记为 `needs-update`。

## 本地管理 Skill

这个仓库内置了一个管理 Skill：

- [skills/yao-open-skills-sync/SKILL.md](skills/yao-open-skills-sync/SKILL.md)

它的职责是：

- 接收你给的本地 Skill 路径。
- 判断是否适合公开。
- 按合集规则导入到 `yao-open-skills`。
- 维护登记表和 README 目录页。
- 记录这个 Skill 是否已经同步到 GitHub，以及线上对应路径。

## Skill Catalog

<!-- catalog:start -->
| Skill | Guide | Lifecycle | Sync | Collection Path | Source Path | GitHub |
| --- | --- | --- | --- | --- | --- | --- |
| [learning-builder](skills/learning-builder/SKILL.md) | [guide](docs/skills/learning-builder.md) | `active` | `published` | [skills/learning-builder](skills/learning-builder) | `external-local-source` | [link](https://github.com/yaojingang/yao-open-skills/tree/main/skills/learning-builder) |
| [skill-doctor](skills/skill-doctor/SKILL.md) | [guide](docs/skills/skill-doctor.md) | `active` | `published` | [skills/skill-doctor](skills/skill-doctor) | `external-local-source` | [link](https://github.com/yaojingang/yao-open-skills/tree/main/skills/skill-doctor) |
| [yao-bayesian-skill](skills/yao-bayesian-skill/SKILL.md) | [guide](docs/skills/yao-bayesian-skill.md) | `active` | `published` | [skills/yao-bayesian-skill](skills/yao-bayesian-skill) | `external-local-source` | [link](https://github.com/yaojingang/yao-open-skills/tree/main/skills/yao-bayesian-skill) |
| [yao-business-skill](skills/yao-business-skill/SKILL.md) | [guide](docs/skills/yao-business-skill.md) | `active` | `published` | [skills/yao-business-skill](skills/yao-business-skill) | `external-local-source` | [link](https://github.com/yaojingang/yao-open-skills/tree/main/skills/yao-business-skill) |
| [yao-kelly-skill](skills/yao-kelly-skill/SKILL.md) | [guide](docs/skills/yao-kelly-skill.md) | `active` | `published` | [skills/yao-kelly-skill](skills/yao-kelly-skill) | `external-local-source` | [link](https://github.com/yaojingang/yao-open-skills/tree/main/skills/yao-kelly-skill) |
| [yao-open-skills-sync](skills/yao-open-skills-sync/SKILL.md) | [guide](docs/skills/yao-open-skills-sync.md) | `active` | `published` | [skills/yao-open-skills-sync](skills/yao-open-skills-sync) | [skills/yao-open-skills-sync](skills/yao-open-skills-sync) | [link](https://github.com/yaojingang/yao-open-skills/tree/main/skills/yao-open-skills-sync) |
| [yao-tutorial-skill](skills/yao-tutorial-skill/SKILL.md) | [guide](docs/skills/yao-tutorial-skill.md) | `active` | `published` | [skills/yao-tutorial-skill](skills/yao-tutorial-skill) | `external-local-source` | [link](https://github.com/yaojingang/yao-open-skills/tree/main/skills/yao-tutorial-skill) |
<!-- catalog:end -->

## 后续约定

- `registry/skills.json` 是事实源。
- README 中的目录表由脚本生成，不手工维护。
- 任何新收录 Skill，都必须先过发布规则，再更新登记表和 README。
- 任何准备公开的变更，都应在整理完成后推送到 GitHub 远程仓库。
