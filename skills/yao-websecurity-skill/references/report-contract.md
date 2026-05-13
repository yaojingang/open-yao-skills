# Report Contract

The audit produces one sanitized review JSON plus four rendered artifacts: `security_review.sanitized.json`, `安全审查评分表.xlsx`, `安全审查报告.html`, `安全审查报告.md`, and `安全审查报告.pdf`.

## Status Vocabulary

Use one status per checklist item:

| Status | Chinese Label | Meaning | Score Treatment |
| --- | --- | --- | --- |
| `Safe` | 安全 | Reviewed and no issue found for the current scope. | full credit |
| `Risk Found` | 存在风险 | Evidence indicates a vulnerability, control gap, or exploitable weakness. | no credit |
| `Unclear` | 存疑 | Evidence is insufficient or contradictory; further runtime/account/test data is needed. | half credit |
| `Not Applicable` | 不适用 | The system does not contain this surface or technology. | excluded |
| `Not Checked` | 未检查 | In scope but not reviewed. | coverage gap |

Do not mark `Safe` without evidence. Prefer `Unclear` when the code path exists but runtime behavior, account matrix, or deployment config is unknown.

## Review JSON Shape

```json
{
  "project": {
    "name": "project name",
    "source": "local path or GitHub URL",
    "branch": "",
    "commit": "",
    "scope": "authorized review scope",
    "environment": "repo-only/staging/production-passive",
    "auditor": "",
    "created_at": "ISO 8601"
  },
  "summary": {
    "authorization": "",
    "authorization_en": "",
    "exclusions": "",
    "exclusions_en": "",
    "attack_surface": "",
    "attack_surface_en": "",
    "selected_risk_domains": [],
    "selected_risk_domains_en": [],
    "not_applicable_rationale": "",
    "not_applicable_rationale_en": "",
    "active_test_prerequisites": "",
    "active_test_prerequisites_en": "",
    "methodology": "",
    "methodology_en": "",
    "coverage_ledger": "",
    "coverage_ledger_en": "",
    "coverage_notes": "",
    "coverage_notes_en": "",
    "overall_risk": "TBD",
    "executive_summary": "",
    "executive_summary_en": "",
    "residual_risk": "",
    "residual_risk_en": "",
    "retest_plan": "",
    "retest_plan_en": "",
    "assumptions": []
  },
  "runtime": {
    "audit_mode": "static | dynamic-safe | dynamic-active | online-authorized | hybrid",
    "audit_mode_label": "静态审查",
    "intensity": "passive | runtime | active | destructive",
    "intensity_label": "被动",
    "source_isolation": "目标代码必须复制或克隆到全新临时目录，审查、构建、运行和写入均在该隔离目录中进行。",
    "temp_workdir": "",
    "target_source": "",
    "runtime_dir": "",
    "runtime_url": "",
    "online_target": "",
    "active_test_authorization": "",
    "allowed_dynamic_tests": [],
    "forbidden_actions": [],
    "oob_endpoint": "",
    "test_accounts": "",
    "rate_limits": "",
    "rollback_plan": "",
    "data_reset_plan": "",
    "destructive_scope": ""
  },
  "checks": [
    {
      "check_id": "V001",
      "priority": "P0",
      "domain": "访问控制、租户隔离与授权",
      "check_item": "对象级授权缺失 BOLA/IDOR",
      "applies_to": "多租户 API、后台、移动端 API",
      "method": "枚举对象 ID，用不同权限测试账号访问，核验服务端 ownership 判断",
      "applicability": "Not Triaged",
      "applicability_reason": "",
      "verification_mode": "",
      "scan_depth": "",
      "requires_active_validation": false,
      "test_safety": "",
      "status": "Not Checked",
      "verdict": "",
      "severity": "",
      "confidence": "",
      "evidence": "",
      "evidence_en": "",
      "finding": "",
      "finding_en": "",
      "root_cause": "",
      "root_cause_en": "",
      "impact": "",
      "impact_en": "",
      "remediation": "",
      "remediation_en": "",
      "owner": "",
      "due_date": "",
      "retest_result": "",
      "source_file_or_endpoint": ""
    }
  ]
}
```

## Applicability Contract

Each row should be triaged before deep testing. Valid `applicability` values are `Applicable`, `Possibly Applicable`, `Not Applicable`, `Deferred`, and `Not Triaged`.

- `Not Applicable` requires an evidence-backed reason and is excluded from score.
- `Applicable` and `Possibly Applicable` should have `verification_mode` and `scan_depth`.
- `Deferred` should name missing prerequisites, such as deployed URL, test account, active-test approval, or safe test data.
- Runtime-only checks should not be marked `Safe` from static review alone; use `Unclear` or `Deferred` if behavior cannot be confirmed.

## Review Mode Contract

The auditor supports multiple modes. The user may choose a mode, but every mode starts by copying or cloning the target into a fresh external temporary workdir. Never install dependencies, run migrations, start services, write test artifacts, or generate reports inside the original local source tree.

| Mode | Chinese Label | Default Boundary |
| --- | --- | --- |
| `static` | 静态审查 | Code/config/dependency review only. Use the isolated temp copy as the inspected source. No runtime traffic. |
| `dynamic-safe` | 动态安全审查 | Deploy the temp copy with temporary secrets, test DB, loopback/container networking, smoke tests, passive DAST, runtime headers/cookie checks, and non-destructive synthetic test data. |
| `dynamic-active` | 动态主动审查 | Includes active validation such as blind/OOB callbacks, brute-force resilience checks, upload/path traversal probes, resource-pressure checks, file mutation, and DB writes only against the isolated temp deployment unless explicit online authorization says otherwise. |
| `online-authorized` | 授权线上审查 | Probe a user-owned live/staging target only within the exact written authorization, rate limits, test accounts, and forbidden-action list. Destructive actions are off unless separately authorized. |
| `hybrid` | 混合审查 | Static plus temp deployment dynamic testing, optionally followed by tightly scoped online validation. |

`allowed_dynamic_tests` uses these keys: `runtime-check`, `passive-dast`, `online-probing`, `blind-oob`, `bruteforce`, `file-mutation`, `database-write`, and `resource-pressure`.

Dynamic and destructive testing rules:

- The original source and any production target are read-only by default.
- Destructive file operations, database writes, migrations, high-rate brute force, resource pressure, upload probes, and blind SSRF/OOB tests default to the temporary deployment.
- Online probing requires explicit target URL, authorization, rate limit, test account/data boundary, stop condition, and rollback owner.
- Brute-force tests must use test accounts and capped attempts; do not use real credential stuffing lists.
- OOB tests must use harmless unique callback tokens and record only callback metadata needed to prove reachability.
- If a runtime cannot be safely deployed, mark affected runtime-only items `Unclear` or `Deferred`, not `Safe`.

## Scoring Model

Priority weights:

- `P0`: 5
- `P1`: 3
- `P2`: 2
- `P3`: 1

The renderer calculates:

- `coverage`: reviewed applicable weight divided by all applicable weight
- `reviewed_safety_score`: safe/unclear weighted score divided by reviewed applicable weight
- `overall_score`: `coverage * reviewed_safety_score`

`Risk Found` items always drive the risk summary before numeric score. Any open `P0` makes the overall risk `Critical`; any open `P1` makes it at least `High`.

## Sanitization Contract

Rendered artifacts and `security_review.sanitized.json` must redact local absolute paths, authorization headers, cookies, bearer tokens, API keys, passwords, private keys, cloud access keys, and long token-like secrets. Use repo-relative paths, endpoint names, request IDs, hashes, and fingerprints instead of sensitive raw values.

## Output Location Contract

Review JSON, sanitized JSON, XLSX, HTML, Markdown, PDF, logs, runtime files, generated files, dependency installs, and temporary files must be written outside the audited local source directory. The renderer and environment preparer should fail rather than create artifacts inside the target code tree.

## Language Contract

Reports are Simplified Chinese by default:

- Excel uses Chinese sheet names, Chinese headers, and Chinese status/severity/risk labels.
- Excel row-level interpretation fields are Chinese by default, including verdict, evidence, finding, root cause, impact, remediation, applicability reason, verification mode, scan depth, and test-safety notes. Repository identifiers, URLs, package names, code symbols, file paths, branch names, and commit hashes may remain as-is.
- Markdown is generated from the same Chinese scorecard/report content as Excel.
- PDF is a Chinese-first browsing copy for quick review. Prefer browser/HTML print rendering when available so typography, spacing, wrapping, and page breaks are visually stable. It should prioritize executive summary, scope, P0/P1, detailed findings, unclear items, retest plan, and a compact full-scorecard appendix.
- HTML defaults to Chinese and must include an English alternate view. Use optional `_en` fields such as `executive_summary_en`, `finding_en`, `evidence_en`, `impact_en`, and `remediation_en` when a translated finding is available; otherwise the renderer may fall back to the Chinese/source text for row-level evidence.

## Required Report Sections

- Scope, authorization, environment, and exclusions
- Attack-surface summary, selected risk domains, methodology, and coverage ledger
- Score summary and status distribution
- P0/P1 focus findings
- Full checklist scorecard
- Detailed findings with evidence, finding, root cause, impact, remediation, owner, SLA, and retest status
- Unclear and not-checked items
- Residual risk and retest plan

## Presentation Standard

Reports use a Kami-inspired professional document language while staying operational and evidence-first:

- HTML uses a warm parchment page (`#f5f4ed`), ivory report surface (`#faf9f5`), ink-blue emphasis (`#1B365D`), warm gray borders, serif-led section hierarchy, compact metric blocks, and restrained risk/status badges.
- HTML must keep the first screen focused on decision data: overall risk, score, coverage, risk count, unclear count, scope, and authorization boundary. Avoid decorative hero sections, marketing language, screenshots, or unsupported claims.
- HTML must provide a sticky top menu for major sections and a top-right language toggle. The default view is Chinese; the alternate view is English.
- HTML tables should be horizontally scrollable, dense, and readable. Priority, severity, and status should render as badges so P0/P1 and `Risk Found` rows are easy to scan.
- Excel should be a working triage workbook, not a raw CSV export: frozen header row, wrapped text, fixed column widths, hidden gridlines, warm header fill, and conditional styling for status, priority, severity, and key overview rows.
- Excel must preserve sortable row-level data and include all operational fields: evidence, root cause, impact, remediation, source file or endpoint, owner, due date, and retest result.
- Markdown should preserve the same Chinese scorecard and operational fields as Excel, with compact tables that are readable in plain Markdown viewers.
- PDF should be optimized for browsing and printing rather than spreadsheet triage: concise summary first, P0/P1 and detailed findings next, residual risk/retest plan, then a compact scorecard appendix.
- Do not use `rgba()` colors in HTML/CSS report templates; use solid hex colors to avoid print/rendering artifacts.

## Artifact Rules

HTML should be a compact high-trust report, not a marketing page. It must avoid decorative cards, unsupported claims, and absolute local filesystem paths. Excel should be useful for triage: sortable rows, frozen header, wrapped text, styled priority/status/severity cells, priority/status counts, and owner/SLA fields. Markdown and PDF are read-only report artifacts and must be generated from the sanitized review data, not from unredacted source evidence.
