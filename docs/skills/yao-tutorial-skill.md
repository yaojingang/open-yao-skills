# Yao Tutorial Skill

## 中文说明

`yao-tutorial-skill` 用来把一个主题、资料包、链接列表、论文集合、GitHub 仓库列表或已有草稿，生产成一套适合新手阅读的完整教程。

它的核心不是“直接写文章”，而是把教程生产拆成一个可复用流程：先理解用户给的资料和目标，再按需要补充外部权威来源，接着设计大纲和章节，最后为每章生成可视化配图，并导出 `Markdown`、`Word`、`PDF` 和 `HTML`。

### 适合什么时候用

- 你想把任意主题做成系统化教程
- 你已经有一批资料、链接、论文或仓库，希望整理成教材
- 你希望内容既通俗易懂，又有来源支撑
- 你需要 Word、PDF、HTML 和 Markdown 多格式交付
- 你希望每个章节都有示意图、模型图、流程图或知识结构图

### 核心流程

1. 归一化输入：主题、受众、目标、已有资料、输出格式和风格偏好。
2. 资料优先级判断：用户资料足够时以用户资料为主；资料不足时补充权威来源、论文、GitHub 和实践案例。
3. 研究取证：生成来源登记和证据映射，避免凭空编造引用。
4. 大纲设计：用“专业内容 + 用户痛点”和“点线面体”方法，把资料重构成面向小白的学习路径。
5. 正文写作：默认中文教程约 `5000-10000` 字，使用正式对外成品口吻，不暴露内部来源角标或资料来源话术。
6. 章节配图：每章生成一个 HTML 可视化画板，再截图嵌入对应章节。
7. 多格式导出：生成 `tutorial.md`、`tutorial.docx`、`tutorial.pdf`、`tutorial.html`。
8. 质量验证：检查章节配图一一对应、引用覆盖、导出文件、截图尺寸、页眉页脚和本地路径泄漏。

### 输出物

标准输出目录通常包含：

- `brief.json`: 输入归一化结果
- `research/source-register.md`: 来源登记
- `research/evidence-map.md`: 证据映射
- `outline.md`: 教程大纲
- `tutorial.md`: 教程正文
- `visuals/visual-spec.json`: 每章配图规格
- `visuals/index.html`: 配图 HTML 画板
- `assets/screenshots/*.png`: 每章配图截图
- `exports/tutorial.html`: 网页报告
- `exports/tutorial.docx`: Word 文档
- `exports/tutorial.pdf`: PDF 文档

### 设计特点

- **资料优先**：先尊重用户给的材料，只有信息不足时才扩大外部检索。
- **证据内化**：重要判断要能在内部研究记录中回到来源，但公开成品不显示 `[U1]` 这类内部 ID。
- **新手友好**：避免默认读者已经懂术语，把概念拆成问题、例子和操作步骤。
- **课程化结构**：标题要有用户利益，大纲要说人话，小节标题要与具体学习任务对应。
- **章节有图**：每个编号章节都要有对应配图，验证器会检查缺失。
- **排版克制**：HTML 使用居中报告容器和粘性目录；Word/PDF 默认不显示页眉页脚。
- **可验证交付**：内置脚本会检查结构、导出物、图片、引用和本地路径。

### 重要边界

不要把这个 Skill 用在：

- 一句话快速解释
- 无来源观点文
- 单纯网页或文档格式转换
- 只画图、不写教程的任务
- 需要实时授课、批改作业或班级运营的教学场景

## English Usage

`yao-tutorial-skill` turns a topic, source packet, URL list, paper set, GitHub repo list, or draft into a source-backed beginner tutorial package.

It is designed for finished educational deliverables rather than quick answers. The workflow normalizes the brief, prioritizes user-provided material, adds external research only when needed, creates a beginner-friendly outline, writes the tutorial, generates one visual per chapter, and exports Markdown, DOCX, PDF, and HTML.

Use it when you need:

- a long-form tutorial from a broad topic
- a textbook-like guide backed by references
- chapter-level diagrams or visual models
- clean HTML, Word, and PDF deliverables
- validation that every chapter has a visual and that exports do not leak local paths

Primary entry points:

- [Skill file](../../skills/yao-tutorial-skill/SKILL.md)
- [Input adaptation](../../skills/yao-tutorial-skill/references/input-adaptation.md)
- [Research sourcing](../../skills/yao-tutorial-skill/references/research-sourcing.md)
- [Tutorial writing](../../skills/yao-tutorial-skill/references/tutorial-outline-and-writing.md)
- [Course design principles](../../skills/yao-tutorial-skill/references/course-design-principles.md)
- [Visual workflow](../../skills/yao-tutorial-skill/references/visual-html-workflow.md)
- [Export workflow](../../skills/yao-tutorial-skill/references/export-workflow.md)
