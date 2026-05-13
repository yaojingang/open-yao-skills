# Yao Websecurity Skill

`yao-websecurity-skill` 是一个网站安全审查 Skill，用来把本地代码目录、GitHub 仓库、授权 staging/runtime 或自有线上目标，转成一套可执行的安全审查流程和多格式报告。

它的输出不是简单的扫描器日志，而是一份带有审查范围、风险评分、适用性判断、证据、影响、整改建议、存疑项和复测计划的安全审查交付物。

默认输出：

- `安全审查评分表.xlsx`
- `安全审查报告.html`
- `安全审查报告.md`
- `安全审查报告.pdf`
- `security_review.sanitized.json`

报告默认使用简体中文。HTML 额外提供中文/英文切换，默认显示中文。

## 这个 Skill 解决什么问题

很多网站安全审查会遇到两个相反的问题：

- 只跑工具：能扫出依赖漏洞和明显配置问题，但很难理解业务授权、后台流程、AI/RAG 数据流、队列和部署边界。
- 只靠人工：能理解业务，但检查项不稳定，容易遗漏供应链、容器、缓存、WebSocket、Webhook、LLM 等边缘风险。

`yao-websecurity-skill` 的设计目标是在两者之间做一个可复用的审查工作台：

1. 先完整理解系统代码、技术栈、路由、认证、数据模型、部署和运行边界。
2. 再从 `V001-V275` 漏洞本体中筛出和当前项目相关的检查项。
3. 对相关检查项做静态审查、工具扫描、低风险运行时检查或授权主动验证。
4. 把结果沉淀成评分表和报告，而不是只给一堆命令输出。

## 设计原理

### 1. 攻击面优先，而不是清单优先

内置知识库有 `275` 个检查项，但 Skill 不会机械地把所有项目都按 275 项深测一遍。

它会先识别当前系统真实存在的攻击面：

- 是否有登录、后台、角色、租户和对象级权限
- 是否有公开 API、移动端 API、OpenAPI、GraphQL 或 WebSocket
- 是否有上传、导入、导出、文件清理、路径拼接
- 是否有 Webhook、SSRF 风险点、URL 抓取、图片代理、预览、爬虫
- 是否有队列、后台任务、缓存、Redis、对象存储、定时任务
- 是否有 Docker、Kubernetes、CI/CD、镜像构建和部署配置
- 是否有 AI/RAG、LLM 工具调用、知识库导入、提示词模板和外部模型调用

之后再判断每个漏洞类型是 `适用`、`可能适用`、`不适用`、`延期` 还是 `未分诊`。这能减少无效扫描，也能让“不适用”的理由可审计。

### 2. 证据优先，而不是口头判断

每个检查项都需要尽量记录：

- 状态：安全、存在风险、存疑、不适用、未检查
- 优先级：P0、P1、P2、P3
- 适用性理由
- 验证方式和扫描深度
- 证据、发现、根因、影响、整改建议
- 置信度、负责人、到期日和复测结果

如果只能静态看到代码路径，但缺少账号矩阵、运行时配置或可验证数据，Skill 会把结果标记为 `存疑` 或 `延期`，而不是为了好看标成安全。

### 3. 安全边界内置到流程中

所有本地代码和 GitHub 仓库审查，都必须先进入全新的临时目录：

```text
fresh-workdir/
├── target-source/        # 被复制或克隆的目标代码
├── runtime/              # 临时运行环境
├── logs/                 # 审查日志
├── security_review.json  # 审查台账
└── security-audit-report/
```

原始代码目录默认只读。依赖安装、构建、数据库迁移、服务启动、动态测试、报告生成和临时文件写入，都只能发生在隔离工作区。

这条规则是为了避免安全审查本身污染或破坏用户的真实代码仓库。

## 漏洞知识库

`references/vulnerability-ontology.csv` 包含 275 个检查项，覆盖：

- 访问控制、租户隔离与授权
- 认证、会话、Token、MFA 和账户安全
- API 安全、BOLA、BFLA、批量赋值和限流
- 输入验证、XSS、CSRF、SSRF、开放重定向
- SQL/NoSQL/命令/模板/表达式注入
- 文件上传、路径处理、导入导出和对象存储
- WebSocket、Webhook、后台任务、消息队列
- 配置、密钥、日志、错误处理和审计
- 依赖、供应链、CI/CD、容器和 IaC
- 数据库、Redis、缓存、备份和恢复
- AI/RAG/LLM 提示注入、知识库越权、工具调用和成本 DoS

每个检查项包含编号、优先级、风险域、检查项、适用对象和建议方法。编号采用 `V001-V275`，便于在报告、Excel、复测和 Issue 里稳定引用。

## 审查模式

Skill 支持多种模式，用户可以按授权和风险承受能力选择。

| 模式 | 中文名称 | 适用情况 | 默认边界 |
| --- | --- | --- | --- |
| `static` | 静态审查 | 只审查代码、配置、依赖、部署文件 | 不启动服务，不发送运行时流量 |
| `dynamic-safe` | 动态安全审查 | 允许在临时环境启动系统并做低风险检查 | 烟测、被动 DAST、Header/Cookie、认证流程、只读 API 验证 |
| `dynamic-active` | 动态主动审查 | 允许在隔离临时部署中做主动验证 | 盲测/OOB、受限暴力破解、上传探测、DB 写入、文件变更、资源压力，仅限隔离环境默认开启 |
| `online-authorized` | 授权线上审查 | 用户提供自有 live/staging 目标和明确授权 | 只测指定 URL、账号、速率、测试数据和检查类型 |
| `hybrid` | 混合审查 | 静态 + 临时动态 + 可选线上确认 | 先隔离环境审查，线上确认单独授权 |

主动测试类型必须显式记录在 `allowed_dynamic_tests` 中：

- `runtime-check`
- `passive-dast`
- `online-probing`
- `blind-oob`
- `bruteforce`
- `file-mutation`
- `database-write`
- `resource-pressure`

如果用户只说“扫描一下”，默认应该使用 `static` 或在授权明确时使用 `dynamic-safe`。涉及盲 SSRF/OOB、暴力破解、文件破坏、数据库写入、资源压力或线上探测时，必须有明确授权、测试账号、速率限制、停止条件和回滚/重置方案。

## 边界控制

这个 Skill 把边界控制写进了流程和脚本：

- `prepare-env` 会把本地路径复制到外部 `target-source`，或把 GitHub 仓库克隆到外部 `target-source`。
- 如果输出路径位于被审查源码目录内部，脚本会拒绝写入。
- 默认排除 `node_modules`、`vendor`、`.git`、构建缓存等依赖和生成目录，避免复制无关大文件。
- 原始仓库不做格式化、不装依赖、不跑迁移、不写报告、不提交、不推送。
- 动态测试默认只针对临时部署；线上目标必须单独授权。
- 破坏性动作默认只允许在隔离临时部署内执行。
- 报告渲染会清洗本地绝对路径、Cookie、Bearer Token、API Key、密码、私钥、云密钥和长 token-like 字符串。
- 报告证据只保留复核需要的信息，例如相对路径、端点、请求 ID、hash 或 fingerprint。

这意味着它可以支持更强的动态审查，但默认姿态仍然是防御性、授权内、可回滚、可解释。

## 典型工作流

### 1. 准备隔离环境

```bash
python3 scripts/security_audit_report.py prepare-env \
  --source "https://github.com/example/project" \
  --workdir "/tmp/example-security-audit" \
  --project "example-project" \
  --mode static
```

### 2. 初始化审查台账

```bash
python3 scripts/security_audit_report.py init \
  --project "example-project" \
  --source "/tmp/example-security-audit/target-source" \
  --mode static \
  --intensity passive \
  --out "/tmp/example-security-audit/security_review.json"
```

### 3. 进行审查

审查时按攻击面分组，而不是按编号机械推进：

- 先看项目结构、框架、路由和入口
- 再看认证、授权、会话、Token、后台、API
- 接着看输入输出、上传、URL 导入、外部请求和文件处理
- 然后看部署、容器、依赖、CI/CD、密钥和日志
- 如果是 AI 应用，再看 RAG 数据边界、提示词注入、工具调用和成本控制
- 对运行时才能确认的问题，按授权选择 `dynamic-safe` 或 `dynamic-active`

### 4. 渲染报告

```bash
python3 scripts/security_audit_report.py render \
  --review "/tmp/example-security-audit/security_review.json" \
  --out-dir "/tmp/example-security-audit/security-audit-report"
```

## 报告设计

### Excel

Excel 是给工程分派和复测使用的操作型评分表：

- 中文 Sheet 名和中文表头
- 冻结表头、隐藏网格线、固定列宽
- 状态、优先级、严重性条件样式
- 包含总览、完整评分表、风险发现、存疑和未检查、清单基准
- 所有解释默认中文，代码标识符和路径保持原样

### HTML

HTML 是给浏览、会议和打印使用的报告：

- 默认中文
- 右上角语言切换，可切到英文
- 顶部导航栏滚动置顶
- 首屏展示总体风险、得分、覆盖率、风险数量、存疑数量
- 风险发现、存疑项、覆盖缺口和复测计划分区呈现
- 使用适合安全审查文档的紧凑排版，而不是营销页布局

### Markdown

Markdown 适合放入仓库、Issue、复测记录或知识库：

- 从同一份审查 JSON 生成
- 默认中文
- 包含完整评分表、风险发现、存疑项、残余风险和复测计划

### PDF

PDF 用于快速浏览和正式分发：

- 从 HTML 打印渲染，避免 Markdown 直转造成表格和分页错乱
- 默认中文
- 控制页边距、分页、字体、长路径和宽表格换行

## 与普通扫描器的区别

普通扫描器更像工具，输入目标，输出发现。

这个 Skill 更像一个安全审查代理流程：

- 它会先理解系统，而不是直接全量跑规则。
- 它会区分适用和不适用，减少无意义检查。
- 它会把缺少运行时证据的问题标记为存疑。
- 它会把静态结果、动态结果、工具结果和人工判断放在同一份台账里。
- 它会输出面向管理层和工程团队都能读的交付物。
- 它把“不能破坏原始代码、不能越权测试、不能泄露秘密”写成默认约束。

## 关键文件

- [Skill 入口](../../skills/yao-websecurity-skill/SKILL.md)
- [目录说明](../../skills/yao-websecurity-skill/README.md)
- [审查方法](../../skills/yao-websecurity-skill/references/security-audit-method.md)
- [审查模式](../../skills/yao-websecurity-skill/references/review-modes.md)
- [报告契约](../../skills/yao-websecurity-skill/references/report-contract.md)
- [扫描器注册表](../../skills/yao-websecurity-skill/references/scanner-registry.md)
- [漏洞本体](../../skills/yao-websecurity-skill/references/vulnerability-ontology.csv)
- [报告脚本](../../skills/yao-websecurity-skill/scripts/security_audit_report.py)
- [回归测试](../../skills/yao-websecurity-skill/tests/test_security_audit_report.py)

## 维护约定

这个 Skill 的本地源路径以 `registry/skills.json` 中的 `source_local_path` 为准。

公开发布时应同步：

- `skills/yao-websecurity-skill/`
- `docs/skills/yao-websecurity-skill.md`
- `docs/skills/README.md`
- `registry/skills.json`
- `README.md`

如果本地源 Skill 后续更新，但公开仓库未同步，应把登记表中的 `sync_status` 调整为 `needs-update`。
