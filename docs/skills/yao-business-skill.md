# Yao Business Skill

## 中文说明

`yao-business-skill` 用来做商业模式设计、诊断和案例拆解，并输出结构化 JSON 与可视化 HTML 报告。

它不是泛泛而谈的商业分析，而是把问题拆成几层：

- 分析对象和经营方向
- 目标市场与区域经营环境
- 当前或候选商业模式
- 财务区间与可信度
- 直接竞品与跨行业类比
- AI 融合点与 AI 冲击风险
- 升级建议、风险和下一步验证动作

这份 skill 特别强调：

- 中国 / 海外 / 出海 / 入华 的经营环境差异
- `fact / estimate / hypothesis / recommendation` 的明确区分
- 至少 `10` 个图表分析模块
- 最终用统一 JSON 驱动 HTML 报告

### 适合什么时候用

- 你有一个新点子，想设计几种更靠谱的商业模式
- 你已经有产品或官网，想系统诊断当前商业模式
- 你想研究成熟公司，学习它的模式、优势、短板和 AI 时代升级点
- 你希望输出一份适合决策者阅读、同时又可审计的商业模式报告

### 三种主场景

1. `idea_to_model`
   把一个想法拆成 `3-5` 个候选商业模式方案，并给出验证路径。

2. `model_diagnosis`
   对已有产品或公司做商业模式诊断，输出环境适配、收入结构、竞品、类比和升级建议。

3. `company_case_study`
   拆解成熟公司的商业模式，区分哪些能力可迁移、哪些只是环境红利。

### 主流程

1. 先判断分析分支和经营方向
2. 建立 `market_environment` 画像
3. 收集证据并区分强弱证据
4. 生成商业模式、财务、竞品、AI 和风险分析
5. 输出 JSON 和双语 HTML 报告

### 主要输出

- 结构化报告 `json`
- 双语可视化报告 `html`
- 图表分析模块，默认覆盖环境、证据、财务、竞争、建议和风险

### 命令

从结构化输入生成正式报告：

```bash
python3 skills/yao-business-skill/scripts/assemble_report.py input.json --render-html
```

只把已有报告 JSON 渲染成 HTML：

```bash
python3 skills/yao-business-skill/scripts/render_report.py report.json
```

校验报告结构：

```bash
python3 skills/yao-business-skill/scripts/validate_report.py report.json
```

### 公开发布约定

本仓库默认公开 skill 本体、脚本、模板、引用资料和说明文档。运行过程中生成的本地报告 HTML、JSON 样例和其他输出产物默认不纳入公开副本。

## English Usage

`yao-business-skill` designs, diagnoses, and studies business models, then exports a structured JSON payload plus a bilingual HTML report.

It does more than produce a generic strategy memo. It breaks the task into:

- entity and route definition
- market and operating environment
- current or candidate business models
- financial ranges and confidence
- direct competitors and cross-industry analogs
- AI leverage and AI disruption
- recommendations, risks, and next validation actions

### When to use it

- when a new idea needs several viable business model options
- when an existing product or website needs a structured model diagnosis
- when a mature company should be studied as a business model case
- when the output needs to be both decision-friendly and auditable

### Main modes

1. `idea_to_model`
2. `model_diagnosis`
3. `company_case_study`

### Command

```bash
python3 skills/yao-business-skill/scripts/assemble_report.py input.json --render-html
```

### Publishing boundary

The public copy keeps the reusable skill sources, scripts, templates, references, and guides. Generated local HTML and JSON reports are treated as local outputs by default and are not part of the published collection.
