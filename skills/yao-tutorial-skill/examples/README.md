# yao-tutorial-skill Examples

这里放三套完整的教程生成示例，用来验证 `yao-tutorial-skill` 的正式输出能力。

每个示例都包含：

- `brief.json`：输入归一化结果
- `outline.md`：教程大纲
- `tutorial.md`：正式教程正文
- `research/`：内部证据登记
- `visuals/`：配图 HTML 画板与 SVG
- `assets/screenshots/`：章节配图截图
- `exports/`：HTML、Word、PDF 和预览图

## 示例目录

| 目录 | 主题 | 用途 |
|---|---|---|
| `meta-skill-giants-shoulders/` | 如何写出高质量元Skill | 方法论类教程，展示从观点素材到体系化教程的转换。 |
| `python-beginner-to-mastery/` | Python 从入门到精通 | 技术学习类教程，展示从基础概念到项目化应用的教学路径。 |
| `english-freedom-route/` | 少年英语自由路径 | 家庭教育/学习方法类教程，展示把长文素材重构成正式课程型教程。 |

## 验证状态

三套示例均已通过 `scripts/validate_package.py --formats docx html pdf --check-deps`：

- 每个编号章节都有对应视觉规格和嵌入配图。
- HTML 具备居中正文容器、粘性目录、日期和表格包裹。
- Word 不包含页眉页脚引用。
- PDF 为无页眉页脚的干净导出。
- 公开 Markdown/HTML/Word/PDF 不暴露 `[U1]`、`[X1]` 等内部角标。
- 公开正文不使用“基于用户资料”“根据原文整理”等内部来源话术。

当前环境仅有一个非阻断警告：未安装 `python-docx`，默认 Word reference 样式生成可能跳过；本次示例的 `.docx` 已正常导出并通过结构检查。
