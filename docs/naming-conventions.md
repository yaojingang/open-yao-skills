# open-yao-skills 命名规范

## 1. 目标

`open-yao-skills` 里的名字不是随手起的目录名，而是公开资产的产品名。

一个好名字至少要同时满足这几件事：

- 让人一眼看懂这个 Skill 解决什么问题
- 在目录、README、GitHub 链接里都足够稳定
- 便于传播、记忆和复述
- 能和同仓库其他 Skill 形成系列感
- 后续功能扩展时不至于很快过时

## 2. 基础规则

所有公开 Skill 的 slug 默认遵循这些规则：

1. 使用英文 `kebab-case`
2. 只用小写字母、数字和连字符
3. 尽量控制在 `2-3` 个词
4. 优先表达“能力结果”，不要表达“内部实现”
5. slug 一旦公开，尽量不改

例如：

- `skill-doctor`
- `tutorial-builder`
- `release-orchestrator`
- `note-cleanup`

## 3. 默认命名原则

### 3.1 先看它操作什么

先判断这个 Skill 的核心对象：

- 如果它操作的是“Skill 本身”，属于元技能
- 如果它操作的是“文档、教程、报告、页面、流程”等业务对象，属于业务技能

### 3.2 再看它的主动作

再判断它最主要的动作：

- 生成
- 清理
- 分析
- 诊断
- 编排
- 同步
- 评审

名字优先采用：

`对象 + 动作`

而不是：

`平台 + 项目名 + 动作 + 细节`

## 4. 推荐模式

### 4.1 元技能

只有当 Skill 的核心工作对象就是“Skill”时，才推荐保留 `skill-*` 前缀。

推荐模式：

- `skill-builder`
- `skill-analyzer`
- `skill-doctor`
- `skill-reviewer`
- `skill-publisher`

适用条件：

- 这个 Skill 主要用来创建、分析、诊断、治理、发布其他 Skill

不适合：

- 普通业务任务
- 单一垂直领域任务

### 4.2 内容与文档生成类

推荐模式：

- `<artifact>-builder`
- `<artifact>-generator`
- `<artifact>-writer`

例子：

- `tutorial-builder`
- `report-generator`
- `brief-writer`

选择建议：

- `builder`: 更强调“从输入到成品的完整构建”
- `generator`: 更强调“自动生成”
- `writer`: 更强调“写作产出本身”

### 4.3 清理整理类

推荐模式：

- `<target>-cleanup`
- `<target>-organizer`
- `<target>-normalizer`

例子：

- `note-cleanup`
- `asset-organizer`

### 4.4 分析诊断类

推荐模式：

- `<target>-analyzer`
- `<target>-reviewer`
- `<target>-doctor`

例子：

- `frontend-reviewer`
- `seo-analyzer`
- `skill-doctor`

选择建议：

- `analyzer`: 偏分析、判断、评估
- `reviewer`: 偏人工检查视角、风险发现
- `doctor`: 偏诊断和修复导向，适合强产品感命名

### 4.5 编排协调类

推荐模式：

- `<domain>-orchestrator`
- `<domain>-governor`
- `<domain>-coordinator`

例子：

- `release-orchestrator`
- `incident-governor`

### 4.6 同步发布类

推荐模式：

- `<scope>-sync`
- `<scope>-publisher`
- `<scope>-registry`

例子：

- `collection-sync`
- `skills-publisher`

## 5. 默认不推荐的命名

### 5.1 把 `skill` 写进所有名字里

不推荐：

- `skill-learning-tutorial-builder`
- `skill-note-cleanup`

原因：

- 它们已经在 `skills/` 目录下，重复
- 普通业务能力不需要再声明自己是 skill

### 5.2 把仓库名、组织名或方法名塞进普通 slug

不推荐：

- `open-yao-skills-sync`
- `yao-learning-tutorial-builder`

原因：

- 耦合过强
- 脱离本仓库语境后可读性更差
- 以后迁移、复用或拆分时成本更高

### 5.3 名字只描述实现细节

不推荐：

- `pandoc-browser-pdf-export`
- `official-docs-research-flow`

原因：

- 实现细节会变
- 对外不如结果导向名字稳定

### 5.4 过长或堆叠修饰语

不推荐：

- `personalized-authoritative-learning-tutorial-builder`
- `advanced-multi-format-study-guide-generator`

原因：

- 太长
- 不利于传播
- 很快会显得局促

## 6. 命名决策顺序

给一个新 Skill 起名时，按这个顺序判断：

1. 它是在操作 skill 本身，还是在操作业务对象？
2. 它最重要的成果是什么？
3. 它的主动作是什么？
4. 这个名字在扩展后是否仍然成立？
5. 是否可以缩短到 `2-3` 个词？

如果一个名字同时满足“清楚、短、稳、可扩展”，它通常就是更好的选择。

## 7. 当前仓库中的应用建议

### 已经比较好的名字

- `skill-builder`
- `skill-analyzer`
- `skill-doctor`

这些名字属于元技能家族，风格统一，保留 `skill-*` 是合理的。

### 可接受但偏长的名字

- `learning-tutorial-builder`

这个名字目前可用，边界也清楚，但它比理想状态略长。

如果未来需要新起同类名字，优先考虑更短版本，例如：

- `tutorial-builder`
- `learning-guide-builder`
- `tutorial-writer`

### 仓库治理类技能

像同步、登记、发布这类只服务本仓库的技能，允许带范围词，但仍应尽量避免把整个仓库名塞进 slug。

优先候选：

- `collection-sync`
- `skills-publisher`

只有在“必须突出它只服务这个仓库”时，才考虑保留仓库作用域。

## 8. 破例规则

以下情况可以破例：

- 已经公开发布，改名会带来明显迁移成本
- 某个名字已经形成品牌识别
- 该 Skill 只服务一个明确仓库或产品，作用域必须写入

但即使破例，也应该满足：

- 可读
- 不误导
- 不和现有家族命名冲突

## 9. 一句话规则

- 元技能：`skill-*`
- 业务技能：`对象 + 动作`
- 名字越短越好，但不能牺牲清晰度
- 不把仓库名和实现细节塞进普通 slug
