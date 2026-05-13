# Yao Websecurity Skill

`yao-websecurity-skill` 是一个面向授权网站、SaaS、API、AI 应用、本地代码仓库和 GitHub 仓库的安全审查 Skill。

它的目标不是替代专业渗透测试团队，也不是提供攻击脚本，而是把一次网站安全审查拆成可复用、可追踪、可输出报告的工作流：先理解系统，再按攻击面筛选检查项，最后生成审查评分表和报告。

## 适用场景

适合：

- 审查一个本地系统代码目录
- 审查一个 GitHub 仓库
- 对授权的 staging/runtime 做低风险动态检查
- 对自有系统做静态审查、动态安全审查或混合审查
- 输出安全评分表、漏洞发现、存疑项、整改建议和复测计划
- 需要中文默认报告，并同时保留 HTML 中英文切换版本

不适合：

- 未授权目标扫描
- 第三方公网目标探测
- 绕过、窃取、隐蔽利用或持久化攻击
- 真实撞库、凭证收集、恶意 payload 投放
- 在生产环境默认执行破坏性文件操作、数据库写入或资源压力测试

## 设计原理

这个 Skill 的核心假设是：安全审查不能只靠“全量扫一遍清单”。

不同系统的攻击面差异很大。一个 Laravel SaaS、一个静态站、一个 AI/RAG 应用、一个多租户 API、一个只有后台的内部系统，应该被审查的风险域并不相同。

因此它采用三层流程：

1. **系统理解优先**：先读代码、路由、认证、会话、模型、上传、队列、部署、依赖、AI/LLM 集成和运行配置。
2. **攻击面驱动筛选**：从 `V001-V275` 漏洞本体中筛出适用、可能适用、不适用、延期和未检查项，避免把无关漏洞类型硬套到项目上。
3. **证据驱动结论**：每个检查项必须有状态、证据、影响、根因、整改建议和置信度；没有证据时不能标记为安全。

这让报告既能覆盖主流安全风险，又能控制 token 和审查时间，把精力放在当前系统真实存在的攻击面上。

## 漏洞知识库

内置 `references/vulnerability-ontology.csv`，包含 `275` 个常见且高价值的网站安全检查项，覆盖：

- 认证、授权、会话、租户隔离
- API 安全、对象级授权、批量赋值、限流
- XSS、CSRF、SSRF、重定向、路径穿越、文件上传
- SQL/NoSQL/命令/模板/表达式注入
- WebSocket、Webhook、后台任务、队列
- 配置、密钥、日志、错误处理
- 依赖、供应链、CI/CD、容器、Kubernetes
- 数据库、缓存、对象存储、备份
- AI/RAG/LLM 提示注入、知识库越权、工具调用和成本 DoS

每个检查项带有优先级、风险域、适用对象和建议验证方法。

## 审查模式

所有模式都必须先把目标复制或克隆到全新的外部临时目录，禁止在原始代码目录里安装依赖、运行迁移、写报告或生成临时文件。

| 模式 | 适用场景 | 默认允许 |
| --- | --- | --- |
| `static` | 只做源码、配置、依赖、部署文件审查 | 只读代码和配置，运行非破坏性的 SAST/SCA/Secrets/IaC 检查 |
| `dynamic-safe` | 用户授权本地临时运行环境检查 | 临时依赖安装、临时 DB、loopback 服务、烟测、被动 DAST、Header/Cookie 检查 |
| `dynamic-active` | 用户授权在隔离环境做主动验证 | 盲测/OOB、受限暴力破解、上传/路径探测、DB 写入、文件变更、资源压力，默认仅限临时部署 |
| `online-authorized` | 用户提供自有线上或 staging 目标并明确授权 | 只探测指定 URL、账号、速率、测试数据和检查类型 |
| `hybrid` | 静态审查 + 临时动态测试 + 可选线上确认 | 先隔离环境审查，线上确认必须单独限定范围 |

动态能力通过 `allowed_dynamic_tests` 显式开启：

- `runtime-check`
- `passive-dast`
- `online-probing`
- `blind-oob`
- `bruteforce`
- `file-mutation`
- `database-write`
- `resource-pressure`

缺少授权、测试账号、回滚方案、数据重置方案或速率限制时，相关检查只能标记为 `存疑` 或 `延期`，不能硬判为安全。

## 边界控制

安全边界是这个 Skill 的一等能力：

- 原始本地代码默认只读，所有构建和测试都在外部临时目录中进行。
- GitHub 仓库必须克隆到新的临时目录，不在用户已有工作区里写入。
- 报告、日志、临时运行文件、依赖安装、数据库、缓存、截图和扫描结果都写到审查工作区。
- 未授权时不做线上探测、不做盲 SSRF/OOB、不做暴力破解、不做破坏性文件操作、不做生产数据库写入。
- 暴力破解测试只能使用测试账号和受限次数，不能使用真实撞库字典。
- OOB 只能使用无害唯一回调 token，不允许把秘密、cookie、token 或个人数据带出。
- 渲染报告前会清洗本地绝对路径、Bearer Token、Cookie、API Key、密码、私钥和长 token-like 字符串。

## 快速使用

准备隔离审查目录：

```bash
python3 scripts/security_audit_report.py prepare-env \
  --source "https://github.com/example/project" \
  --workdir "/tmp/example-security-audit" \
  --project "example-project" \
  --mode static
```

初始化 `275` 项审查台账：

```bash
python3 scripts/security_audit_report.py init \
  --project "example-project" \
  --source "/tmp/example-security-audit/target-source" \
  --mode static \
  --intensity passive \
  --out "/tmp/example-security-audit/security_review.json"
```

在完成代码阅读、工具扫描、动态测试和人工判断后，渲染报告：

```bash
python3 scripts/security_audit_report.py render \
  --review "/tmp/example-security-audit/security_review.json" \
  --out-dir "/tmp/example-security-audit/security-audit-report"
```

默认输出：

- `安全审查评分表.xlsx`
- `安全审查报告.html`
- `安全审查报告.md`
- `安全审查报告.pdf`
- `security_review.sanitized.json`

## 报告能力

报告默认使用简体中文。

- Excel：中文 Sheet、中文表头、中文状态/严重性/整改解释，适合筛选和分派。
- HTML：中文默认视图，右上角支持中英切换，顶部导航滚动置顶。
- Markdown：从同一份评分表和报告内容生成，适合版本管理。
- PDF：从 HTML 打印渲染，强调稳定排版、分页和浏览体验。
- JSON：保留结构化审查台账，便于复测、二次渲染或自动化集成。

## 关键文件

- [Skill 入口](SKILL.md)
- [审查方法](references/security-audit-method.md)
- [审查模式](references/review-modes.md)
- [报告契约](references/report-contract.md)
- [扫描器注册表](references/scanner-registry.md)
- [漏洞本体](references/vulnerability-ontology.csv)
- [报告脚本](scripts/security_audit_report.py)
- [测试](tests/test_security_audit_report.py)

## 发布说明

公开副本已去除本地缓存文件和私人绝对路径。后续如本地源 Skill 有变化，需要同步更新本目录、`docs/skills/yao-websecurity-skill.md`、`registry/skills.json` 和首页目录。
