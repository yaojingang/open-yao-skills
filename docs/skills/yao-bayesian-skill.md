# Yao Bayesian Skill

`yao-bayesian-skill` 用来把“这件事到底该不该做”的模糊判断，变成一套可追踪、可解释、可迭代的贝叶斯决策流程。

它不只是算一个 `P(H|E)`。它真正解决的是：

- 把用户的问题先定义清楚
- 用当前信息先给一个弱先验和初步判断
- 通过多轮对话持续补信息
- 记录每一轮判断如何变化
- 把概率更新落实到行动建议
- 最后产出一份普通用户也能看懂的报告

当前公开版本默认输出两种结果：

- `Markdown`：中文主报告，适合版本管理、团队协作、复制引用
- `HTML`：双语可切换报告，适合浏览、分享、打印，以及在浏览器里“存储为 PDF”

## 这个 Skill 最适合做什么

适合这几类不确定性决策：

- 产品和增长：某个功能要不要做，某个市场要不要进
- 商业和运营：某个方向是否值得继续投入，某个试点是否该扩大
- 个人决策：旅行、搬家、求职、创业、时间选择
- 风险判断：某个信号是否足够强，某个动作是否该现在做

它特别适合“用户一开始信息不完整”的情况。

也就是说，用户不需要一开始就给全量结构化输入。只要先给出“问题 + 当前现状”，Skill 就可以先工作起来。

## 核心亮点

### 1. 不是一次性报告，而是多轮决策循环

这个 Skill 的一个核心特点，是支持从“不完整输入”开始。

第一轮时它会：

- 先把问题结构化
- 基于当前已知信息给一个弱先验
- 给出一个初步判断
- 指出还缺哪些信息

然后在后续轮次里继续追问，持续更新：

- 先验
- 证据强度
- 后验概率
- 决策准备度
- 最终建议

这比传统“你先把所有字段填完再分析”的模式，更接近真实用户的思考过程。

### 2. 会记录每一轮判断是怎么变的

Skill 不只是输出最后一个结论，它还会记录过程。

报告里会包含：

- 每一轮新增了什么信息
- 这一轮信息对判断有什么影响
- 起点概率和更新后概率
- 中间判断如何变化
- 哪一轮让结论变化最大
- 当前是否已经达到“可以正式决策”的状态

这使得报告从“一个结果”变成“一个过程”。

### 3. 概率不是终点，行动建议才是重点

这个 Skill 的目标不是告诉你“成功概率 47%”，而是回答：

- 现在该做什么
- 为什么是这个动作
- 为什么不是另外两个动作
- 下一个最值得补的信息是什么
- 什么条件下应该重新判断

也就是说，它是从“证据到行动”的报告器，而不是一个公式计算器。

### 4. 报告对普通用户更友好

HTML 报告现在做了这几层处理：

- 顶部先给普通用户能直接看懂的结论
- 中间先看“你现在该怎么做”
- 复杂的先验、证据、敏感性放在折叠区
- 支持中英双语切换
- 右上角支持 `打印` 和 `下载 PDF`
- 打印前会自动展开折叠内容，避免导出的 PDF 不完整

## 它的决策逻辑是怎么工作的

完整链路大致是：

1. 先定义问题
2. 明确假设、时间范围、行动选项、成功标准
3. 根据已有信息给一个初步先验
4. 对证据做分级
5. 用赔率更新或 Beta-binomial 更新后验
6. 做敏感性分析，检查结论是否稳健
7. 把后验概率转成行动建议
8. 给出下一步最值得收集的信息
9. 输出 Markdown 和 HTML 报告

如果用户是多轮对话输入，还会额外做：

10. 记录每一轮变化
11. 计算决策准备度
12. 判断当前是否已经“可以进入正式决策”

## 证据和先验怎么处理

这个 Skill 强调一件事：不要把“常识”直接当成可靠先验。

它会尽量区分：

- 强证据
- 弱证据
- 类比信号
- 需要折扣的依赖证据

常见更新路径包括：

- 赔率更新：适合似然比、竞争性证据、快速判断
- Beta-binomial：适合计数型数据，例如试点转化率、预订率、样本成功数
- 多轮补信息：适合用户逐步补充上下文时的迭代式判断

## 报告最终会包含什么

最终的人类可读报告通常包括：

- 一句话结论
- 你现在该怎么做
- 这份建议成立的前提
- 为什么不是另外两个选项
- 多轮对话过程与决策准备度
- 决策问题
- 先验设置
- 证据摘要
- 贝叶斯更新
- 行动比较
- 敏感性分析
- 下一步最有价值的信息
- 风险与注意事项
- Skill 流程与能力说明

## 典型使用场景

### 场景 1：产品是否上线

例如：

> 我们要不要在本季度发布 AI Deal Coach 增值包？

Skill 会把问题拆成：

- 假设：这个能力值得在当前季度推进
- 时间范围：本季度
- 关键阈值：增购率、留存率、执行成本
- 行动选项：直接全量上线、先跑试点、延后

然后给出结论，例如：

- 当前不适合直接大范围上线
- 更合理的是先跑一个 6 周的付费试点
- 如果增购率和留存达到阈值，再推进

### 场景 2：旅行是否值得现在订

例如：

> 我想下个月从北京飞三亚旅行，我现在还在北京上班。

Skill 可以先基于已知现状给初步判断，再追问：

- 能请几天假
- 预算多少
- 一个人还是同行
- 具体日期是什么

随着补充信息，报告会从“演示级判断”升级为“真实决策报告”。

### 场景 3：市场是否值得进入

例如：

> 我们要不要进入美国 GEO 服务市场？

Skill 会把市场判断转成：

- 参考类
- 现有客户与案例基础
- 交付能力
- 销售周期和风险
- 行动阈值

最后给出更像“先跑验证”还是“可以正式投入”的决策建议。

## 详细案例

公开仓库里最适合上手的详细样例，是这个输入文件：

- [`skills/yao-bayesian-skill/input/detailed_growth_case.json`](../../skills/yao-bayesian-skill/input/detailed_growth_case.json)

它对应的是一个典型的 SaaS 产品决策问题：

> NimbusCRM 应该在本季度发布 AI Deal Coach 增值包吗？

这个案例展示了：

- 如何从初始弱先验开始
- 如何通过 4 轮对话不断补信息
- 如何把行为信号、执行风险、管理员控制能力等因素加入判断
- 如何从“有机会”收敛到“先确认，再推进”
- 如何输出给普通用户看得懂的最终行动建议

## 示例报告

公开仓库也附带了几组已经生成好的案例报告，方便直接查看最终效果。

### 产品与商业判断

- [detailed-growth-case.html](../../skills/yao-bayesian-skill/reports/detailed-growth-case.html)
- [detailed-growth-case.pdf](../../skills/yao-bayesian-skill/reports/detailed-growth-case.pdf)
- [example-decision-report.html](../../skills/yao-bayesian-skill/reports/example-decision-report.html)
- [example-decision-report.pdf](../../skills/yao-bayesian-skill/reports/example-decision-report.pdf)
- [geo-overseas-service-case.html](../../skills/yao-bayesian-skill/reports/geo-overseas-service-case.html)
- [geo-overseas-service-case.pdf](../../skills/yao-bayesian-skill/reports/geo-overseas-service-case.pdf)

### 个人决策判断

- [sanya-travel-case.html](../../skills/yao-bayesian-skill/reports/sanya-travel-case.html)
- [sanya-travel-case.pdf](../../skills/yao-bayesian-skill/reports/sanya-travel-case.pdf)
- [sanya-travel-real-report.html](../../skills/yao-bayesian-skill/reports/sanya-travel-real-report.html)
- [sanya-travel-real-report.pdf](../../skills/yao-bayesian-skill/reports/sanya-travel-real-report.pdf)

如果你想快速感受这个 Skill 的“普通用户结论 + 技术折叠区 + 可打印 HTML”风格，建议先打开 `detailed-growth-case.html`。

## 如何使用

### 1. 用自然语言触发

你可以直接这样说：

```text
Use $yao-bayesian-skill to decide whether we should build this feature now.
Start with a weak prior if the input is incomplete, ask follow-up questions,
record each round, update the posterior, compare actions, and export the final report as Markdown and bilingual HTML.
```

### 2. 用结构化输入运行

如果你已经有 JSON 输入，可以直接运行：

```bash
python3 skills/yao-bayesian-skill/scripts/generate_report_bundle.py input.json out/
```

例如：

```bash
python3 skills/yao-bayesian-skill/scripts/generate_report_bundle.py \
  skills/yao-bayesian-skill/input/detailed_growth_case.json \
  out/ \
  --basename detailed-growth-case
```

默认会生成：

- `out/detailed-growth-case.md`
- `out/detailed-growth-case.html`

### 3. 在 HTML 里导出 PDF

打开生成后的 HTML 报告后：

1. 点击右上角 `下载 PDF`
2. 浏览器会打开打印面板
3. 选择“存储为 PDF”

Skill 会在打印前自动展开折叠区，避免导出的 PDF 漏掉证据、先验或附录部分。

## 输入上不需要一次到位

这是这个 Skill 的一个实际优势。

你不需要一开始就准备好所有字段。下面两种输入都能工作：

### 简单输入

```text
我想下个月去三亚旅行，现在还在北京上班。
```

### 更完整输入

```json
{
  "title": "是否应该开发某个 AI 功能",
  "hypothesis": "目标用户会愿意为该功能付费",
  "time_horizon": "30 天",
  "success_metric": "至少 5% 目标用户预订或付费",
  "actions": [
    "立即开发 MVP",
    "先做 landing page 测试",
    "暂缓"
  ]
}
```

Skill 会根据输入完整度自动选择：

- 先给弱先验和初步判断
- 或直接进入更完整的正式分析

## 这个公开版本有哪些特点

- 中文主报告优先
- HTML 支持中英双语切换
- HTML 顶部导航支持 sticky 跟随
- 证据、先验、敏感性等技术段落默认折叠
- 报告先给普通用户结论，再展示技术细节
- 输出与示例使用方式对齐，便于复现

## 不适合做什么

这个 Skill 不适合：

- 纯教学式贝叶斯定理讲解
- 教科书概率作业
- 不需要明确行动建议的泛泛讨论
- 代替持证专业人士做最终医疗、法律、金融判断

在医疗、法律、金融这类高风险场景里，它应该被看作辅助分析工具，而不是最终意见。

## 开源边界

公开仓库里保留的是可复用 Skill 本体：

- `SKILL.md`
- 输入模板和案例输入
- 引用文档
- 评测配置
- 导出脚本与模板

运行时生成的本地报告产物，不作为公开副本的一部分持续维护。

## 快速入口

- Skill 入口：[`skills/yao-bayesian-skill/SKILL.md`](../../skills/yao-bayesian-skill/SKILL.md)
- 结构化模板：[`skills/yao-bayesian-skill/input/bayesian_decision_request.template.json`](../../skills/yao-bayesian-skill/input/bayesian_decision_request.template.json)
- 详细样例：[`skills/yao-bayesian-skill/input/detailed_growth_case.json`](../../skills/yao-bayesian-skill/input/detailed_growth_case.json)
- 导出脚本：[`skills/yao-bayesian-skill/scripts/generate_report_bundle.py`](../../skills/yao-bayesian-skill/scripts/generate_report_bundle.py)

## English Summary

`yao-bayesian-skill` turns uncertain choices into an auditable Bayesian decision process with:

- weak-prior-first analysis for incomplete input
- multi-turn evidence collection and round logging
- posterior and action-threshold updates
- plain-language recommendations
- synchronized Markdown and bilingual HTML output

The public version is optimized for real decision support rather than theorem tutoring.
