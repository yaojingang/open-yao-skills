#!/usr/bin/env python3
"""Initialize and render web security audit review artifacts.

The script intentionally uses only Python's standard library so the skill can
produce XLSX, HTML, Markdown, and PDF reports in constrained local environments.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape as xml_escape


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ONTOLOGY = ROOT / "references" / "vulnerability-ontology.csv"
DEFAULT_TEMPLATE = ROOT / "templates" / "review-template.json"
SKILL_NAME = "yao-websecurity-skill"
AUDIT_MODES = {
    "static": "静态审查",
    "dynamic-safe": "动态安全审查",
    "dynamic-active": "动态主动审查",
    "online-authorized": "授权线上审查",
    "hybrid": "混合审查",
}
AUDIT_INTENSITIES = {
    "passive": "被动",
    "runtime": "运行时",
    "active": "主动",
    "destructive": "破坏性",
}
ACTIVE_TEST_CLASSES = {
    "runtime-check": "运行时检查",
    "passive-dast": "被动 DAST",
    "online-probing": "线上目标探测",
    "blind-oob": "盲测/OOB 回连验证",
    "bruteforce": "暴力破解韧性测试",
    "file-mutation": "文件写入/删除验证",
    "database-write": "数据库写入验证",
    "resource-pressure": "资源压力验证",
}

STATUS_ALIASES = {
    "safe": "Safe",
    "pass": "Safe",
    "passed": "Safe",
    "ok": "Safe",
    "安全": "Safe",
    "通过": "Safe",
    "risk": "Risk Found",
    "risk found": "Risk Found",
    "found": "Risk Found",
    "fail": "Risk Found",
    "failed": "Risk Found",
    "vulnerable": "Risk Found",
    "存在风险": "Risk Found",
    "有风险": "Risk Found",
    "发现风险": "Risk Found",
    "unclear": "Unclear",
    "unknown": "Unclear",
    "questionable": "Unclear",
    "needs review": "Unclear",
    "存疑": "Unclear",
    "不确定": "Unclear",
    "not applicable": "Not Applicable",
    "n/a": "Not Applicable",
    "na": "Not Applicable",
    "不适用": "Not Applicable",
    "not checked": "Not Checked",
    "unchecked": "Not Checked",
    "todo": "Not Checked",
    "未检查": "Not Checked",
}

STATUS_ZH = {
    "Safe": "安全",
    "Risk Found": "存在风险",
    "Unclear": "存疑",
    "Not Applicable": "不适用",
    "Not Checked": "未检查",
}

PRIORITY_WEIGHTS = {"P0": 5, "P1": 3, "P2": 2, "P3": 1}
SEVERITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Info": 0, "": 0}
LOCAL_PATH_RE = re.compile(
    r"(?<![\w:/.-])(?P<path>(?:/(?:Users|home|private/tmp|tmp|var/folders|Volumes)/[^\s<>'\")\]]+)|(?:[A-Za-z]:\\(?:Users|Documents and Settings|Temp|tmp)\\[^\s<>'\")\]]+))"
)
PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.IGNORECASE | re.DOTALL,
)
SENSITIVE_HEADER_RE = re.compile(r"(?i)\b(authorization|cookie|set-cookie|x-api-key)\s*:\s*[^\n\r]+")
BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}")
SENSITIVE_ASSIGNMENT_RE = re.compile(
    r"(?i)\b([A-Za-z0-9_.-]*(?:token|secret|password|passwd|api[_-]?key|access[_-]?key|private[_-]?key|jwt|session|cookie)[A-Za-z0-9_.-]*)\s*([:=])\s*([^\s,;&]+)"
)
AWS_ACCESS_KEY_RE = re.compile(r"\bA(?:KIA|SIA)[A-Z0-9]{16}\b")
GENERIC_LONG_SECRET_RE = re.compile(r"(?i)\b(?:sk|pk|ghp|github_pat|xox[baprs])[-_A-Za-z0-9]{16,}\b")


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local_source_root(source: Any) -> Path | None:
    text = str(source or "").strip()
    if not text or re.match(r"^[a-z][a-z0-9+.-]*://", text, re.IGNORECASE) or text.startswith("git@"):
        return None
    source_path = Path(text).expanduser()
    is_path_like = source_path.is_absolute() or source_path.exists() or text.startswith((".", "~"))
    if not is_path_like:
        return None
    if source_path.exists() and source_path.is_file():
        source_path = source_path.parent
    elif not source_path.exists() and source_path.suffix:
        source_path = source_path.parent
    return source_path.resolve(strict=False)


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except ValueError:
        return False


def ensure_outputs_outside_source(source: Any, output_paths: list[Path]) -> None:
    root = local_source_root(source)
    if root is None:
        return
    blocked = [
        path
        for path in output_paths
        if is_relative_to(path.expanduser(), root)
    ]
    if blocked:
        blocked_text = ", ".join(str(path) for path in blocked)
        raise SystemExit(
            "Refusing to write audit artifacts inside the target source directory. "
            f"Target source: {root}. Blocked output path(s): {blocked_text}. "
            "Choose an external workdir for review JSON, XLSX, and HTML outputs."
        )


def is_git_source(source: Any) -> bool:
    text = str(source or "").strip()
    return bool(
        re.match(r"^(?:https?|ssh)://", text, re.IGNORECASE)
        or text.startswith("git@")
        or text.endswith(".git")
    )


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "-", value.strip()).strip("-._")
    return slug[:60] or "target"


def parse_csv_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [part.strip() for part in str(value or "").split(",") if part.strip()]


def write_audit_env(target_dir: Path, runtime_dir: Path, mode: str) -> str:
    env_path = target_dir / ".env.audit"
    lines = [
        "# Generated for isolated security audit runtime. Do not use in production.",
        "APP_ENV=testing",
        "APP_DEBUG=false",
        f"AUDIT_MODE={mode}",
        f"AUDIT_RUNTIME_DIR={runtime_dir}",
        f"DB_DATABASE={runtime_dir / 'audit.sqlite'}",
        "CACHE_DRIVER=array",
        "QUEUE_CONNECTION=sync",
        "MAIL_MAILER=array",
    ]
    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(env_path)


def prepare_env(args: argparse.Namespace) -> None:
    mode = args.mode
    intensity = args.intensity
    allowed = parse_csv_list(args.allowed_tests)
    if mode == "static" and intensity != "passive":
        raise SystemExit("Static mode only allows passive intensity. Choose dynamic-safe, dynamic-active, online-authorized, or hybrid.")
    if intensity == "destructive" and mode not in {"dynamic-active", "hybrid"}:
        raise SystemExit("Destructive intensity is only allowed for dynamic-active or hybrid mode, and should run against the isolated temp deployment.")
    unknown_tests = sorted(set(allowed) - set(ACTIVE_TEST_CLASSES))
    if unknown_tests:
        raise SystemExit(f"Unknown active test class(es): {', '.join(unknown_tests)}")

    workdir = Path(args.workdir).expanduser().resolve(strict=False)
    ensure_outputs_outside_source(args.source, [workdir])
    workdir.mkdir(parents=True, exist_ok=True)
    if any(workdir.iterdir()) and not args.reuse:
        raise SystemExit(f"Workdir is not empty: {workdir}. Use --reuse or choose a fresh temp directory.")

    target_dir = workdir / "target-source"
    runtime_dir = workdir / "runtime"
    reports_dir = workdir / "report"
    logs_dir = workdir / "logs"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not target_dir.exists():
        if is_git_source(args.source):
            clone_cmd = ["git", "clone", "--depth", "1", str(args.source), str(target_dir)]
            subprocess.run(clone_cmd, check=True)
        else:
            source_root = local_source_root(args.source)
            if source_root is None or not source_root.exists():
                raise SystemExit(f"Local source not found or not path-like: {args.source}")
            ignore = shutil.ignore_patterns(
                ".git",
                "node_modules",
                "vendor",
                ".venv",
                "venv",
                "__pycache__",
                "dist",
                "build",
                ".next",
                "storage/logs",
                "tmp",
            )
            shutil.copytree(source_root, target_dir, ignore=ignore)

    env_file = write_audit_env(target_dir, runtime_dir, mode)
    manifest = {
        "skill": SKILL_NAME,
        "created_at": now_iso(),
        "project": args.project or safe_slug(Path(str(args.source).rstrip("/")).name or "target"),
        "source": str(args.source),
        "target_source": str(target_dir),
        "runtime_dir": str(runtime_dir),
        "reports_dir": str(reports_dir),
        "logs_dir": str(logs_dir),
        "audit_env_file": env_file,
        "mode": mode,
        "mode_label": AUDIT_MODES.get(mode, mode),
        "intensity": intensity,
        "intensity_label": AUDIT_INTENSITIES.get(intensity, intensity),
        "runtime_url": args.runtime_url,
        "online_target": args.online_target,
        "oob_endpoint": args.oob_endpoint,
        "allowed_tests": allowed,
        "allowed_test_labels": [ACTIVE_TEST_CLASSES[test] for test in allowed],
        "forbidden_by_default": [
            "No writes to original source tree",
            "No production data mutation",
            "No credential stuffing with real passwords",
            "No destructive test against online target unless explicitly authorized",
        ],
        "next_steps": [
            "Install dependencies and run framework-specific setup only inside target_source/runtime_dir.",
            "Start local services bound to loopback or isolated containers.",
            "Record runtime URL, test accounts, rate limits, rollback/reset command, and active-test evidence in security_review.json.",
        ],
    }
    manifest_path = workdir / "audit-environment.json"
    write_json(manifest_path, manifest)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


def normalize_status(value: Any) -> str:
    raw = str(value or "Not Checked").strip()
    return STATUS_ALIASES.get(raw.lower(), raw if raw in STATUS_ZH else "Not Checked")


def priority_weight(priority: Any) -> int:
    return PRIORITY_WEIGHTS.get(str(priority or "").strip().upper(), 1)


def _redact_path_match(match: re.Match[str]) -> str:
    raw = match.group("path")
    line_suffix = ""
    line_match = re.search(r"(:\d+(?::\d+)?)$", raw)
    path_part = raw
    if line_match:
        line_suffix = line_match.group(1)
        path_part = raw[: -len(line_suffix)]
    basename = re.split(r"[\\/]", path_part.rstrip("/\\"))[-1] or "path"
    return f"[local-path-redacted:{basename}{line_suffix}]"


def sanitize_report_value(value: Any) -> Any:
    if value is None or isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    text = str(value)
    text = PRIVATE_KEY_RE.sub("[private-key-redacted]", text)
    text = SENSITIVE_HEADER_RE.sub(lambda m: f"{m.group(1)}: [redacted]", text)
    text = BEARER_RE.sub("Bearer [redacted]", text)
    text = SENSITIVE_ASSIGNMENT_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}[redacted]", text)
    text = AWS_ACCESS_KEY_RE.sub("[aws-access-key-redacted]", text)
    text = GENERIC_LONG_SECRET_RE.sub("[secret-redacted]", text)
    text = LOCAL_PATH_RE.sub(_redact_path_match, text)
    return text


def sanitize_structure(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize_structure(inner) for key, inner in value.items()}
    if isinstance(value, list):
        return [sanitize_structure(inner) for inner in value]
    return sanitize_report_value(value)


def redact_local_path(value: str) -> str:
    return str(sanitize_report_value(value or ""))


def load_ontology(path: Path = DEFAULT_ONTOLOGY) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Ontology file not found: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    required = {"check_id", "priority", "domain", "check_item", "applies_to", "method"}
    missing = required - set(rows[0].keys() if rows else [])
    if missing:
        raise SystemExit(f"Ontology missing columns: {', '.join(sorted(missing))}")
    return rows


def extract_kb_from_source(source: Path, out: Path) -> int:
    rows: list[dict[str, str]] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\|\s*V\d{3}\s*\|", line):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) < 6:
            continue
        check_id, priority, domain, check_item, applies_to, method = parts[:6]
        rows.append(
            {
                "check_id": check_id,
                "priority": priority,
                "domain": domain,
                "check_item": check_item,
                "applies_to": applies_to,
                "method": method,
            }
        )
    if not rows:
        raise SystemExit(f"No V001-style checklist rows found in {source}")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["check_id", "priority", "domain", "check_item", "applies_to", "method"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def init_review(args: argparse.Namespace) -> None:
    ensure_outputs_outside_source(args.source, [Path(args.out)])
    ontology = load_ontology(Path(args.ontology))
    if Path(args.template).exists():
        review = read_json(Path(args.template))
    else:
        review = {"project": {}, "summary": {}, "checks": []}

    project = review.setdefault("project", {})
    project["name"] = args.project
    project["source"] = args.source
    project["scope"] = args.scope
    project["environment"] = args.environment
    project.setdefault("branch", "")
    project.setdefault("commit", "")
    project.setdefault("auditor", "")
    project["created_at"] = now_iso()

    summary = review.setdefault("summary", {})
    summary.setdefault("authorization", "")
    summary.setdefault("authorization_en", "")
    summary.setdefault("exclusions", "")
    summary.setdefault("exclusions_en", "")
    summary.setdefault("attack_surface", "")
    summary.setdefault("attack_surface_en", "")
    summary.setdefault("selected_risk_domains", [])
    summary.setdefault("selected_risk_domains_en", [])
    summary.setdefault("not_applicable_rationale", "")
    summary.setdefault("not_applicable_rationale_en", "")
    summary.setdefault("active_test_prerequisites", "")
    summary.setdefault("active_test_prerequisites_en", "")
    summary.setdefault("methodology", "")
    summary.setdefault("methodology_en", "")
    summary.setdefault("coverage_ledger", "")
    summary.setdefault("coverage_ledger_en", "")
    summary.setdefault("coverage_notes", "")
    summary.setdefault("coverage_notes_en", "")
    summary.setdefault("overall_risk", "TBD")
    summary.setdefault("executive_summary", "")
    summary.setdefault("executive_summary_en", "")
    summary.setdefault("residual_risk", "")
    summary.setdefault("residual_risk_en", "")
    summary.setdefault("retest_plan", "")
    summary.setdefault("retest_plan_en", "")
    summary.setdefault("assumptions", [])

    runtime = review.setdefault("runtime", {})
    runtime["audit_mode"] = args.mode
    runtime["audit_mode_label"] = AUDIT_MODES.get(args.mode, args.mode)
    runtime["intensity"] = args.intensity
    runtime["intensity_label"] = AUDIT_INTENSITIES.get(args.intensity, args.intensity)
    runtime.setdefault("source_isolation", "必须在全新临时目录中复制或克隆目标代码；不得在原始源码树中安装依赖、构建、运行迁移或写入报告。")
    runtime.setdefault("temp_workdir", "")
    runtime.setdefault("target_source", "")
    runtime.setdefault("runtime_dir", "")
    runtime["runtime_url"] = args.runtime_url
    runtime["online_target"] = args.online_target
    runtime.setdefault("active_test_authorization", "")
    runtime["allowed_dynamic_tests"] = parse_csv_list(args.allowed_tests)
    runtime.setdefault("forbidden_actions", [
        "未授权线上目标探测",
        "针对真实账号的撞库或高强度暴力破解",
        "生产数据写入或删除",
        "原始源码树写入、迁移、格式化、依赖安装或构建产物",
    ])
    runtime["oob_endpoint"] = args.oob_endpoint
    runtime.setdefault("test_accounts", "")
    runtime.setdefault("rate_limits", "")
    runtime.setdefault("rollback_plan", "")
    runtime.setdefault("data_reset_plan", "")
    runtime.setdefault("destructive_scope", "")

    review["checks"] = [
        {
            "check_id": row["check_id"],
            "priority": row["priority"],
            "domain": row["domain"],
            "check_item": row["check_item"],
            "applies_to": row["applies_to"],
            "method": row["method"],
            "applicability": "Not Triaged",
            "applicability_reason": "",
            "verification_mode": "",
            "scan_depth": "",
            "requires_active_validation": False,
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
            "source_file_or_endpoint": "",
        }
        for row in ontology
    ]
    write_json(Path(args.out), review)
    print(f"Initialized review JSON with {len(review['checks'])} checks: {Path(args.out).resolve()}")


def summarize(review: dict[str, Any]) -> dict[str, Any]:
    checks = review.get("checks", [])
    status_counts = {status: 0 for status in STATUS_ZH}
    priority_counts: dict[str, dict[str, int]] = {}
    applicable_weight = 0
    reviewed_weight = 0
    positive_weight = 0.0
    risk_items = []
    unclear_items = []
    not_checked_items = []

    for item in checks:
        status = normalize_status(item.get("status"))
        item["status"] = status
        priority = str(item.get("priority") or "P3").upper()
        weight = priority_weight(priority)
        status_counts[status] = status_counts.get(status, 0) + 1
        priority_counts.setdefault(priority, {s: 0 for s in STATUS_ZH})
        priority_counts[priority][status] = priority_counts[priority].get(status, 0) + 1

        if status == "Not Applicable":
            continue
        applicable_weight += weight
        if status != "Not Checked":
            reviewed_weight += weight
        if status == "Safe":
            positive_weight += weight
        elif status == "Unclear":
            positive_weight += weight * 0.5
            unclear_items.append(item)
        elif status == "Risk Found":
            risk_items.append(item)
        elif status == "Not Checked":
            not_checked_items.append(item)

    coverage = reviewed_weight / applicable_weight if applicable_weight else 1.0
    reviewed_safety = positive_weight / reviewed_weight if reviewed_weight else 0.0
    overall_score = coverage * reviewed_safety

    max_risk = "Low"
    if any(i.get("priority") == "P0" and normalize_status(i.get("status")) == "Risk Found" for i in checks):
        max_risk = "Critical"
    elif any(i.get("priority") == "P1" and normalize_status(i.get("status")) == "Risk Found" for i in checks):
        max_risk = "High"
    elif risk_items:
        max_risk = "Medium"
    elif unclear_items or not_checked_items:
        max_risk = "Unclear"

    return {
        "total_checks": len(checks),
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "coverage": round(coverage * 100, 1),
        "reviewed_safety_score": round(reviewed_safety * 100, 1),
        "overall_score": round(overall_score * 100, 1),
        "overall_risk": max_risk,
        "risk_items": risk_items,
        "unclear_items": unclear_items,
        "not_checked_items": not_checked_items,
    }


def safe_sheet_name(name: str) -> str:
    cleaned = re.sub(r"[\[\]:*?/\\]", " ", name).strip() or "Sheet"
    return cleaned[:31]


def col_name(index: int) -> str:
    result = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        result = chr(65 + remainder) + result
    return result


def excel_column_widths(sheet_name: str, max_cols: int) -> list[float]:
    presets = {
        "总览": [24, 92],
        "安全评分表": [10, 10, 24, 26, 26, 34, 16, 34, 18, 14, 14, 24, 15, 12, 28, 12, 12, 46, 36, 36, 42, 46, 14, 14, 18, 28],
        "风险发现": [10, 10, 24, 30, 12, 12, 20, 14, 48, 36, 36, 32, 44, 48, 14, 14, 18],
        "存疑和未检查": [10, 10, 24, 30, 12, 12, 20, 14, 48, 36, 36, 32, 44, 48, 14, 14, 18],
        "清单基准": [10, 10, 26, 30, 34, 48],
    }
    widths = presets.get(sheet_name, [])
    if len(widths) < max_cols:
        widths = widths + [22] * (max_cols - len(widths))
    return widths[:max_cols]


def excel_style_for_cell(
    sheet_name: str,
    headers: list[Any],
    row: list[Any],
    row_index: int,
    col_index: int,
    value: Any,
) -> int:
    if row_index == 1:
        return 1

    header = str(headers[col_index - 1] if col_index - 1 < len(headers) else "")
    text = str(value or "")
    field = str(row[0] if row else "")

    if sheet_name == "总览":
        if col_index == 1:
            return 16
        if field in {"Overall Risk", "总体风险"}:
            return {
                "Critical": 11,
                "严重": 11,
                "High": 12,
                "高": 12,
                "Medium": 13,
                "中": 13,
                "Low": 14,
                "低": 14,
                "Unclear": 4,
                "存疑": 4,
            }.get(text, 0)
        if field in {"Overall Score", "Coverage", "Reviewed Safety Score", "Total Checks", "总体得分", "覆盖率", "已审安全得分", "检查项总数"}:
            return 15

    if header in {"Status", "Status CN", "状态"}:
        return {
            "Risk Found": 2,
            "存在风险": 2,
            "Safe": 3,
            "安全": 3,
            "Unclear": 4,
            "存疑": 4,
            "Not Applicable": 5,
            "不适用": 5,
            "Not Checked": 6,
            "未检查": 6,
        }.get(text, 0)

    if header in {"Priority", "优先级"}:
        return {"P0": 7, "P1": 8, "P2": 9, "P3": 10}.get(text, 0)

    if header in {"Severity", "严重性"}:
        return {
            "Critical": 11,
            "严重": 11,
            "High": 12,
            "高": 12,
            "Medium": 13,
            "中": 13,
            "Low": 14,
            "低": 14,
            "Info": 14,
            "信息": 14,
        }.get(text, 0)

    return 0


def cell_xml(row_index: int, col_index: int, value: Any, style: int = 0) -> str:
    ref = f"{col_name(col_index)}{row_index}"
    style_attr = f' s="{style}"' if style else ""
    if value is None:
        value = ""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f'<c r="{ref}"{style_attr}><v>{value}</v></c>'
    text = str(sanitize_report_value(value))
    if len(text) > 32767:
        text = text[:32700] + "...[truncated]"
    escaped = xml_escape(text)
    return f'<c r="{ref}" t="inlineStr"{style_attr}><is><t xml:space="preserve">{escaped}</t></is></c>'


def worksheet_xml(sheet_name: str, rows: list[list[Any]]) -> str:
    row_xml = []
    max_cols = max((len(row) for row in rows), default=1)
    headers = rows[0] if rows else []
    for row_index, row in enumerate(rows, start=1):
        height = ' ht="24" customHeight="1"' if row_index == 1 else ""
        cells = "".join(
            cell_xml(
                row_index,
                col_index,
                value,
                excel_style_for_cell(sheet_name, headers, row, row_index, col_index, value),
            )
            for col_index, value in enumerate(row, start=1)
        )
        row_xml.append(f'<row r="{row_index}"{height}>{cells}</row>')
    col_xml = "".join(
        f'<col min="{idx}" max="{idx}" width="{width}" customWidth="1"/>'
        for idx, width in enumerate(excel_column_widths(sheet_name, max_cols), start=1)
    )
    auto_filter = f'<autoFilter ref="A1:{col_name(max_cols)}{max(len(rows), 1)}"/>' if rows else ""
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheetViews><sheetView workbookViewId="0" showGridLines="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" state="frozen"/></sheetView></sheetViews>'
        '<sheetFormatPr defaultRowHeight="34"/>'
        f'<cols>{col_xml}</cols>'
        '<sheetData>'
        + "".join(row_xml)
        + '</sheetData>'
        + auto_filter
        + '<pageMargins left="0.45" right="0.45" top="0.55" bottom="0.55" header="0.3" footer="0.3"/>'
        + '</worksheet>'
    )


def write_xlsx(path: Path, sheets: dict[str, list[list[Any]]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sheet_items = [(safe_sheet_name(name), rows) for name, rows in sheets.items()]
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
            + "".join(
                f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                for i in range(1, len(sheet_items) + 1)
            )
            + "</Types>",
        )
        z.writestr(
            "_rels/.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            "</Relationships>",
        )
        workbook_sheets = "".join(
            f'<sheet name="{xml_escape(name)}" sheetId="{i}" r:id="rId{i}"/>'
            for i, (name, _) in enumerate(sheet_items, start=1)
        )
        z.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            f"<sheets>{workbook_sheets}</sheets></workbook>",
        )
        workbook_rels = "".join(
            f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
            for i in range(1, len(sheet_items) + 1)
        )
        workbook_rels += (
            f'<Relationship Id="rId{len(sheet_items) + 1}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
        )
        z.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            + workbook_rels
            + "</Relationships>",
        )
        z.writestr(
            "xl/styles.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<fonts count="5">'
            '<font><sz val="10"/><color rgb="FF141413"/><name val="Arial"/></font>'
            '<font><b/><sz val="10"/><color rgb="FFFDFCF8"/><name val="Arial"/></font>'
            '<font><b/><sz val="10"/><color rgb="FF1B365D"/><name val="Arial"/></font>'
            '<font><b/><sz val="10"/><color rgb="FF9D1C20"/><name val="Arial"/></font>'
            '<font><b/><sz val="10"/><color rgb="FF5E5D59"/><name val="Arial"/></font>'
            '</fonts>'
            '<fills count="12">'
            '<fill><patternFill patternType="none"/></fill>'
            '<fill><patternFill patternType="gray125"/></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FF1B365D"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFF8E7E5"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFEAF4EA"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFFFF2D6"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFE8E6DC"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFF4EFE4"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFE4ECF5"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFD6E1EE"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FFFAF9F5"/><bgColor indexed="64"/></patternFill></fill>'
            '<fill><patternFill patternType="solid"><fgColor rgb="FF30302E"/><bgColor indexed="64"/></patternFill></fill>'
            '</fills>'
            '<borders count="2">'
            '<border><left/><right/><top/><bottom/><diagonal/></border>'
            '<border><left style="thin"><color rgb="FFE8E5DA"/></left><right style="thin"><color rgb="FFE8E5DA"/></right><top style="thin"><color rgb="FFE8E5DA"/></top><bottom style="thin"><color rgb="FFE8E5DA"/></bottom><diagonal/></border>'
            '</borders>'
            '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
            '<cellXfs count="17">'
            '<xf numFmtId="0" fontId="0" fillId="10" borderId="1" xfId="0" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="1" fillId="2" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="center"/></xf>'
            '<xf numFmtId="0" fontId="3" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="2" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="2" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="4" fillId="6" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="4" fillId="7" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="3" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>'
            '<xf numFmtId="0" fontId="2" fillId="9" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>'
            '<xf numFmtId="0" fontId="2" fillId="8" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>'
            '<xf numFmtId="0" fontId="4" fillId="6" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>'
            '<xf numFmtId="0" fontId="3" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="3" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="2" fillId="5" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="2" fillId="8" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '<xf numFmtId="0" fontId="2" fillId="8" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment horizontal="left" vertical="center"/></xf>'
            '<xf numFmtId="0" fontId="2" fillId="10" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
            '</cellXfs>'
            '<cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>'
            "</styleSheet>",
        )
        z.writestr(
            "docProps/core.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            f"<dc:creator>{SKILL_NAME}</dc:creator>"
            f"<dcterms:created xsi:type=\"dcterms:W3CDTF\">{dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}</dcterms:created>"
            "</cp:coreProperties>",
        )
        z.writestr(
            "docProps/app.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            f"<Application>{SKILL_NAME}</Application></Properties>",
        )
        for i, (name, rows) in enumerate(sheet_items, start=1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", worksheet_xml(name, rows))


SEVERITY_ZH = {
    "Critical": "严重",
    "High": "高",
    "Medium": "中",
    "Low": "低",
    "Info": "信息",
    "": "",
}
RISK_ZH = {
    "Critical": "严重",
    "High": "高",
    "Medium": "中",
    "Low": "低",
    "Unclear": "存疑",
}
APPLICABILITY_ZH = {
    "Applicable": "适用",
    "Possibly Applicable": "可能适用",
    "Not Applicable": "不适用",
    "Deferred": "延后",
    "Not Triaged": "未分流",
}
CONFIDENCE_ZH = {
    "High": "高",
    "Medium": "中",
    "Low": "低",
    "Info": "信息",
    "Unknown": "未知",
}
FIELD_VALUE_ZH = {
    "applicability_reason": {
        "No corresponding component, business flow, or technology was present in this Laravel CMS/AI content repository for this repo-only review.": "本次仓库级审查中，未在该 Laravel CMS/AI 内容仓库发现对应组件、业务流程或技术栈。",
        "Relevant to GEOFlow repository architecture and reviewed code path.": "与 GEOFlow 仓库架构和已审查代码路径相关。",
        "No Elasticsearch dependency/configuration found.": "未发现 Elasticsearch 依赖或配置。",
        "No MongoDB dependency/configuration found.": "未发现 MongoDB 依赖或配置。",
    },
    "verification_mode": {
        "Repo static triage": "仓库静态分流",
        "Static code review": "静态代码审查",
        "Repo config review; active endpoint needed": "仓库配置审查；需要线上端点验证",
        "Tool availability check": "工具可用性检查",
        "Static data-flow review": "静态数据流审查",
    },
    "scan_depth": {
        "Architecture-aware applicability triage": "结合架构的适用性分流",
        "Targeted": "定向审查",
        "Configuration only": "仅配置审查",
        "Not executed": "未执行",
    },
    "test_safety": {
        "No active test performed; source tree kept read-only.": "未执行主动测试；源码树保持只读。",
        "Passive only; no mutation or active probing": "仅被动审查；未修改数据或主动探测。",
        "Requires authorized live endpoint; not performed": "需要授权线上端点；本次未执行。",
    },
    "verdict": {
        "Not in scope for this codebase after triage.": "经分流后，该项不属于当前代码库范围。",
    },
    "evidence": {
        "Repository inventory and route/config review did not identify this technology or flow.": "仓库盘点及路由/配置审查未发现该技术或流程。",
    },
    "remediation": {
        "Keep this control covered by regression tests and configuration review.": "继续通过回归测试和配置审查覆盖该控制项。",
        "Keep this behavior under regression coverage.": "继续将该行为纳入回归覆盖。",
    },
}


def localized_dict_value(source: dict[str, Any], field: str, lang: str = "zh", fallback: Any = "") -> Any:
    if lang == "en":
        return source.get(f"{field}_en") or source.get(field) or fallback
    value = source.get(f"{field}_zh") or source.get(field) or fallback
    return translate_field_value(field, value)


def translate_field_value(field: str, value: Any) -> Any:
    if isinstance(value, list):
        return [translate_field_value(field, item) for item in value]
    text = str(value or "")
    return FIELD_VALUE_ZH.get(field, {}).get(text, value)


def display_list(value: Any, empty: str = "") -> str:
    if value is None or value == "":
        return empty
    if isinstance(value, list):
        return "\n".join(str(item) for item in value) if value else empty
    return str(value)


def status_value(status: Any, lang: str = "zh") -> str:
    normalized = normalize_status(status)
    return STATUS_ZH.get(normalized, normalized) if lang == "zh" else normalized


def severity_value(severity: Any, lang: str = "zh") -> str:
    text = str(severity or "")
    return SEVERITY_ZH.get(text, text) if lang == "zh" else text


def confidence_value(confidence: Any, lang: str = "zh") -> str:
    text = str(confidence or "")
    return CONFIDENCE_ZH.get(text, text) if lang == "zh" else text


def risk_value(risk: Any, lang: str = "zh") -> str:
    text = str(risk or "")
    return RISK_ZH.get(text, text) if lang == "zh" else text


def applicability_value(value: Any, lang: str = "zh") -> str:
    text = str(value or "")
    return APPLICABILITY_ZH.get(text, text) if lang == "zh" else text


def bool_value(value: Any, lang: str = "zh") -> str:
    if value is True:
        return "是" if lang == "zh" else "Yes"
    if value is False:
        return "否" if lang == "zh" else "No"
    return str(value or "")


def scorecard_rows(review: dict[str, Any], lang: str = "zh") -> list[list[Any]]:
    headers_zh = [
        "编号",
        "优先级",
        "风险域",
        "检查项",
        "适用对象",
        "核查方法",
        "适用性",
        "适用性原因",
        "验证方式",
        "扫描深度",
        "需主动验证",
        "测试安全边界",
        "状态",
        "结论",
        "严重性",
        "置信度",
        "证据",
        "发现",
        "根因",
        "影响",
        "修复建议",
        "负责人",
        "到期日",
        "复测结果",
        "源码文件或端点",
    ]
    headers_en = [
        "ID",
        "Priority",
        "Domain",
        "Check Item",
        "Applies To",
        "Method",
        "Applicability",
        "Applicability Reason",
        "Verification Mode",
        "Scan Depth",
        "Requires Active Validation",
        "Test Safety",
        "Status",
        "Verdict",
        "Severity",
        "Confidence",
        "Evidence",
        "Finding",
        "Root Cause",
        "Impact",
        "Remediation",
        "Owner",
        "Due Date",
        "Retest",
        "Source File or Endpoint",
    ]
    rows = [headers_zh if lang == "zh" else headers_en]
    for item in review.get("checks", []):
        status = normalize_status(item.get("status"))
        rows.append(
            [
                item.get("check_id", ""),
                item.get("priority", ""),
                localized_dict_value(item, "domain", lang),
                localized_dict_value(item, "check_item", lang),
                localized_dict_value(item, "applies_to", lang),
                localized_dict_value(item, "method", lang),
                applicability_value(item.get("applicability", ""), lang),
                localized_dict_value(item, "applicability_reason", lang),
                localized_dict_value(item, "verification_mode", lang),
                localized_dict_value(item, "scan_depth", lang),
                bool_value(item.get("requires_active_validation", ""), lang),
                localized_dict_value(item, "test_safety", lang),
                status_value(status, lang),
                localized_dict_value(item, "verdict", lang),
                severity_value(item.get("severity", ""), lang),
                confidence_value(item.get("confidence", ""), lang),
                localized_dict_value(item, "evidence", lang),
                localized_dict_value(item, "finding", lang),
                localized_dict_value(item, "root_cause", lang),
                localized_dict_value(item, "impact", lang),
                localized_dict_value(item, "remediation", lang),
                item.get("owner", ""),
                item.get("due_date", ""),
                localized_dict_value(item, "retest_result", lang),
                item.get("source_file_or_endpoint", ""),
            ]
        )
    return rows


def overview_rows(review: dict[str, Any], summary: dict[str, Any], lang: str = "zh") -> list[list[Any]]:
    project = review.get("project", {})
    report_summary = review.get("summary", {})
    runtime = review.get("runtime", {})
    selected_domains = display_list(localized_dict_value(report_summary, "selected_risk_domains", lang))
    if lang == "en":
        rows = [
            ["Field", "Value"],
            ["Project", project.get("name", "")],
            ["Source", redact_local_path(project.get("source", ""))],
            ["Branch", project.get("branch", "")],
            ["Commit", project.get("commit", "")],
            ["Scope", localized_dict_value(project, "scope", lang)],
            ["Environment", project.get("environment", "")],
            ["Audit Mode", runtime.get("audit_mode", "")],
            ["Intensity", runtime.get("intensity", "")],
            ["Temp Workdir", runtime.get("temp_workdir", "")],
            ["Isolated Runtime URL", runtime.get("runtime_url", "")],
            ["Online Target", runtime.get("online_target", "")],
            ["Allowed Dynamic Tests", display_list(runtime.get("allowed_dynamic_tests", []))],
            ["Forbidden Actions", display_list(runtime.get("forbidden_actions", []))],
            ["Rollback Plan", runtime.get("rollback_plan", "")],
            ["Exclusions", localized_dict_value(report_summary, "exclusions", lang)],
            ["Attack Surface", localized_dict_value(report_summary, "attack_surface", lang)],
            ["Selected Risk Domains", selected_domains],
            ["Not Applicable Rationale", localized_dict_value(report_summary, "not_applicable_rationale", lang)],
            ["Active Test Prerequisites", localized_dict_value(report_summary, "active_test_prerequisites", lang)],
            ["Methodology", localized_dict_value(report_summary, "methodology", lang)],
            ["Coverage Ledger", localized_dict_value(report_summary, "coverage_ledger", lang)],
            ["Auditor", project.get("auditor", "")],
            ["Created", project.get("created_at", "")],
            ["Rendered", now_iso()],
            ["Overall Risk", risk_value(summary["overall_risk"], lang)],
            ["Overall Score", summary["overall_score"]],
            ["Coverage", summary["coverage"]],
            ["Reviewed Safety Score", summary["reviewed_safety_score"]],
            ["Total Checks", summary["total_checks"]],
            ["Authorization", localized_dict_value(report_summary, "authorization", lang)],
            ["Coverage Notes", localized_dict_value(report_summary, "coverage_notes", lang)],
            ["Residual Risk", localized_dict_value(report_summary, "residual_risk", lang)],
            ["Retest Plan", localized_dict_value(report_summary, "retest_plan", lang)],
            ["Executive Summary", localized_dict_value(report_summary, "executive_summary", lang)],
        ]
        rows.append([])
        rows.append(["Status", "Count"])
        rows.extend([[status_value(status, lang), count] for status, count in summary["status_counts"].items()])
        return rows

    rows = [
        ["字段", "值"],
        ["项目", project.get("name", "")],
        ["来源", redact_local_path(project.get("source", ""))],
        ["分支", project.get("branch", "")],
        ["提交", project.get("commit", "")],
        ["范围", localized_dict_value(project, "scope", lang)],
        ["环境", project.get("environment", "")],
        ["审查模式", runtime.get("audit_mode_label") or AUDIT_MODES.get(runtime.get("audit_mode", ""), runtime.get("audit_mode", ""))],
        ["测试强度", runtime.get("intensity_label") or AUDIT_INTENSITIES.get(runtime.get("intensity", ""), runtime.get("intensity", ""))],
        ["临时工作区", runtime.get("temp_workdir", "")],
        ["隔离运行地址", runtime.get("runtime_url", "")],
        ["授权线上目标", runtime.get("online_target", "")],
        ["允许的动态测试", display_list(runtime.get("allowed_dynamic_tests", []))],
        ["禁止动作", display_list(runtime.get("forbidden_actions", []))],
        ["回滚计划", runtime.get("rollback_plan", "")],
        ["排除范围", localized_dict_value(report_summary, "exclusions", lang)],
        ["攻击面", localized_dict_value(report_summary, "attack_surface", lang)],
        ["选定风险域", selected_domains],
        ["不适用判定依据", localized_dict_value(report_summary, "not_applicable_rationale", lang)],
        ["主动测试前置条件", localized_dict_value(report_summary, "active_test_prerequisites", lang)],
        ["方法", localized_dict_value(report_summary, "methodology", lang)],
        ["覆盖台账", localized_dict_value(report_summary, "coverage_ledger", lang)],
        ["审查人", project.get("auditor", "")],
        ["创建时间", project.get("created_at", "")],
        ["生成时间", now_iso()],
        ["总体风险", risk_value(summary["overall_risk"], lang)],
        ["总体得分", summary["overall_score"]],
        ["覆盖率", summary["coverage"]],
        ["已审安全得分", summary["reviewed_safety_score"]],
        ["检查项总数", summary["total_checks"]],
        ["授权说明", localized_dict_value(report_summary, "authorization", lang)],
        ["覆盖说明", localized_dict_value(report_summary, "coverage_notes", lang)],
        ["残余风险", localized_dict_value(report_summary, "residual_risk", lang)],
        ["复测计划", localized_dict_value(report_summary, "retest_plan", lang)],
        ["执行摘要", localized_dict_value(report_summary, "executive_summary", lang)],
    ]
    rows.append([])
    rows.append(["状态", "数量"])
    rows.extend([[status_value(status, lang), count] for status, count in summary["status_counts"].items()])
    return rows


def findings_rows(items: list[dict[str, Any]], lang: str = "zh") -> list[list[Any]]:
    headers_zh = [
        "编号",
        "优先级",
        "状态",
        "风险域",
        "标题",
        "严重性",
        "置信度",
        "验证方式",
        "扫描深度",
        "证据",
        "发现",
        "根因",
        "源码文件或端点",
        "影响",
        "修复建议",
        "负责人",
        "到期日",
        "复测结果",
    ]
    headers_en = [
        "ID",
        "Priority",
        "Status",
        "Domain",
        "Title",
        "Severity",
        "Confidence",
        "Verification Mode",
        "Scan Depth",
        "Evidence",
        "Finding",
        "Root Cause",
        "Source File or Endpoint",
        "Impact",
        "Remediation",
        "Owner",
        "Due Date",
        "Retest",
    ]
    rows = [headers_zh if lang == "zh" else headers_en]
    for item in sorted(
        items,
        key=lambda x: (-priority_weight(x.get("priority")), -SEVERITY_ORDER.get(str(x.get("severity", "")), 0), x.get("check_id", "")),
    ):
        status = normalize_status(item.get("status"))
        rows.append(
            [
                item.get("check_id", ""),
                item.get("priority", ""),
                status_value(status, lang),
                localized_dict_value(item, "domain", lang),
                localized_dict_value(item, "check_item", lang),
                severity_value(item.get("severity", ""), lang),
                confidence_value(item.get("confidence", ""), lang),
                localized_dict_value(item, "verification_mode", lang),
                localized_dict_value(item, "scan_depth", lang),
                localized_dict_value(item, "evidence", lang),
                localized_dict_value(item, "finding", lang),
                localized_dict_value(item, "root_cause", lang),
                item.get("source_file_or_endpoint", ""),
                localized_dict_value(item, "impact", lang),
                localized_dict_value(item, "remediation", lang),
                item.get("owner", ""),
                item.get("due_date", ""),
                localized_dict_value(item, "retest_result", lang),
            ]
        )
    return rows


def ontology_rows(review: dict[str, Any], lang: str = "zh") -> list[list[Any]]:
    rows = [["编号", "优先级", "风险域", "检查项", "适用对象", "核查方法"]] if lang == "zh" else [["ID", "Priority", "Domain", "Check Item", "Applies To", "Method"]]
    for item in review.get("checks", []):
        rows.append(
            [
                item.get("check_id", ""),
                item.get("priority", ""),
                localized_dict_value(item, "domain", lang),
                localized_dict_value(item, "check_item", lang),
                localized_dict_value(item, "applies_to", lang),
                localized_dict_value(item, "method", lang),
            ]
        )
    return rows


def badge_class(header: str, text: str) -> str:
    value = text.strip()
    if header in {"Status", "Status CN", "状态"}:
        return {
            "Risk Found": "badge badge-risk",
            "存在风险": "badge badge-risk",
            "Safe": "badge badge-safe",
            "安全": "badge badge-safe",
            "Unclear": "badge badge-unclear",
            "存疑": "badge badge-unclear",
            "Not Applicable": "badge badge-na",
            "不适用": "badge badge-na",
            "Not Checked": "badge badge-unchecked",
            "未检查": "badge badge-unchecked",
        }.get(value, "")
    if header in {"Priority", "优先级"}:
        return {
            "P0": "badge badge-p0",
            "P1": "badge badge-p1",
            "P2": "badge badge-p2",
            "P3": "badge badge-p3",
        }.get(value, "")
    if header in {"Severity", "严重性"}:
        return {
            "Critical": "badge badge-critical",
            "严重": "badge badge-critical",
            "High": "badge badge-high",
            "高": "badge badge-high",
            "Medium": "badge badge-medium",
            "中": "badge badge-medium",
            "Low": "badge badge-low",
            "低": "badge badge-low",
            "Info": "badge badge-info",
            "信息": "badge badge-info",
        }.get(value, "")
    return ""


def html_cell(header: str, value: Any) -> str:
    raw = sanitize_report_value(value) or ""
    text = str(raw)
    escaped = html.escape(text).replace("\n", "<br>")
    cls = badge_class(header, text)
    if cls:
        return f'<span class="{cls}">{escaped}</span>'
    return escaped


def html_table(rows: list[list[Any]], limit: int | None = None, css_class: str = "report-table") -> str:
    if not rows:
        return ""
    body_rows = rows[1 : limit + 1 if limit else None]
    headers = [str(value) for value in rows[0]]
    header = "".join(f"<th>{html.escape(str(sanitize_report_value(value)))}</th>" for value in headers)
    body = []
    for row in body_rows:
        cells = "".join(
            f"<td>{html_cell(headers[idx] if idx < len(headers) else '', value)}</td>"
            for idx, value in enumerate(row)
        )
        body.append(f"<tr>{cells}</tr>")
    return f'<div class="table-wrap"><table class="{css_class}"><thead><tr>{header}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


def html_report_text(value: Any, fallback: str) -> str:
    text = display_list(value, fallback)
    return html.escape(str(sanitize_report_value(text))).replace("\n", "<br>")


def dual_text(zh: Any, en: Any) -> str:
    zh_text = html.escape(str(sanitize_report_value(zh or "")))
    en_text = html.escape(str(sanitize_report_value(en or zh or "")))
    return f'<span class="lang-inline lang-zh">{zh_text}</span><span class="lang-inline lang-en">{en_text}</span>'


def dual_html(zh_html: str, en_html: str, block: bool = False) -> str:
    cls = "lang-panel" if block else "lang-inline"
    return f'<span class="{cls} lang-zh">{zh_html}</span><span class="{cls} lang-en">{en_html}</span>'


def bilingual_table(zh_rows: list[list[Any]], en_rows: list[list[Any]], limit: int | None = None) -> str:
    return (
        f'<div class="lang-panel lang-zh">{html_table(zh_rows, limit=limit)}</div>'
        f'<div class="lang-panel lang-en">{html_table(en_rows, limit=limit)}</div>'
    )


def p0_p1_focus_items(risk_items: list[dict[str, Any]], unclear_items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    focus = [
        item
        for item in risk_items + unclear_items
        if str(item.get("priority", "")).upper() in {"P0", "P1"}
    ]
    return sorted(focus, key=lambda x: (-priority_weight(x.get("priority")), x.get("check_id", "")))


def compact_source_label(project: dict[str, Any]) -> str:
    source = redact_local_path(project.get("source", ""))
    branch = project.get("branch", "")
    commit = str(project.get("commit", ""))
    parts = [source]
    if branch:
        parts.append(f"branch {branch}")
    if commit:
        parts.append(f"commit {commit[:12]}")
    return " · ".join(str(sanitize_report_value(part)) for part in parts if part)


def methodology_rows(review: dict[str, Any], lang: str = "zh") -> list[list[Any]]:
    project = review.get("project", {})
    report_summary = review.get("summary", {})
    runtime = review.get("runtime", {})
    if lang == "en":
        return [
            ["Field", "Value"],
            ["Environment", project.get("environment", "")],
            ["Audit Mode", runtime.get("audit_mode", "")],
            ["Intensity", runtime.get("intensity", "")],
            ["Source Isolation", runtime.get("source_isolation", "")],
            ["Allowed Dynamic Tests", display_list(runtime.get("allowed_dynamic_tests", []), "No active/dynamic tests authorized.")],
            ["OOB Endpoint", runtime.get("oob_endpoint", "")],
            ["Rate Limits", runtime.get("rate_limits", "")],
            ["Rollback/Data Reset", " / ".join(part for part in [runtime.get("rollback_plan", ""), runtime.get("data_reset_plan", "")] if part)],
            ["Exclusions", localized_dict_value(report_summary, "exclusions", lang, "No exclusions documented.")],
            ["Attack Surface", localized_dict_value(report_summary, "attack_surface", lang, "No attack-surface summary documented.")],
            ["Selected Risk Domains", display_list(localized_dict_value(report_summary, "selected_risk_domains", lang), "No selected risk domains documented.")],
            ["Not Applicable Rationale", localized_dict_value(report_summary, "not_applicable_rationale", lang, "No not-applicable rationale documented.")],
            ["Active Test Prerequisites", localized_dict_value(report_summary, "active_test_prerequisites", lang, "No active-test prerequisites documented.")],
            ["Methodology", localized_dict_value(report_summary, "methodology", lang, "Reviewed code, configuration, dependencies, authn/authz, APIs, business logic, logs, and AI/LLM controls against V001-V275.")],
            ["Coverage Ledger", localized_dict_value(report_summary, "coverage_ledger", lang, localized_dict_value(report_summary, "coverage_notes", lang, "No coverage ledger documented."))],
            ["Assumptions", display_list(localized_dict_value(report_summary, "assumptions", lang), "No assumptions documented.")],
        ]
    return [
        ["字段", "值"],
        ["环境", project.get("environment", "")],
        ["审查模式", runtime.get("audit_mode_label") or AUDIT_MODES.get(runtime.get("audit_mode", ""), runtime.get("audit_mode", ""))],
        ["测试强度", runtime.get("intensity_label") or AUDIT_INTENSITIES.get(runtime.get("intensity", ""), runtime.get("intensity", ""))],
        ["源码隔离", runtime.get("source_isolation", "")],
        ["允许的动态测试", display_list(runtime.get("allowed_dynamic_tests", []), "未授权主动/动态测试。")],
        ["OOB 端点", runtime.get("oob_endpoint", "")],
        ["限速边界", runtime.get("rate_limits", "")],
        ["回滚/数据重置", " / ".join(part for part in [runtime.get("rollback_plan", ""), runtime.get("data_reset_plan", "")] if part)],
        ["排除范围", localized_dict_value(report_summary, "exclusions", lang, "未填写排除范围。")],
        ["攻击面", localized_dict_value(report_summary, "attack_surface", lang, "未填写攻击面摘要。")],
        ["选定风险域", display_list(localized_dict_value(report_summary, "selected_risk_domains", lang), "未填写相关风险域。")],
        ["不适用判定依据", localized_dict_value(report_summary, "not_applicable_rationale", lang, "未填写不适用项判定依据。")],
        ["主动测试前置条件", localized_dict_value(report_summary, "active_test_prerequisites", lang, "未填写主动/盲测前置条件。")],
        ["方法", localized_dict_value(report_summary, "methodology", lang, "按 V001-V275 清单执行代码、配置、依赖、认证授权、API、业务逻辑、日志与 AI/LLM 安全审查。")],
        ["覆盖台账", localized_dict_value(report_summary, "coverage_ledger", lang, localized_dict_value(report_summary, "coverage_notes", lang, "未填写覆盖台账。"))],
        ["假设", display_list(localized_dict_value(report_summary, "assumptions", lang), "未填写假设。")],
    ]


def residual_rows(review: dict[str, Any], lang: str = "zh") -> list[list[Any]]:
    report_summary = review.get("summary", {})
    if lang == "en":
        return [
            ["Field", "Value"],
            ["Residual Risk", localized_dict_value(report_summary, "residual_risk", lang, "No residual risk documented.")],
            ["Retest Plan", localized_dict_value(report_summary, "retest_plan", lang, "No retest plan documented.")],
        ]
    return [
        ["字段", "值"],
        ["残余风险", localized_dict_value(report_summary, "residual_risk", lang, "未填写残余风险。")],
        ["复测计划", localized_dict_value(report_summary, "retest_plan", lang, "未填写复测计划。")],
    ]


def status_distribution_rows(summary: dict[str, Any], lang: str = "zh") -> list[list[Any]]:
    if lang == "en":
        return [["Status", "Count"]] + [[status_value(status, lang), count] for status, count in summary["status_counts"].items()]
    return [["状态", "数量"]] + [[status_value(status, lang), count] for status, count in summary["status_counts"].items()]


def render_html(review: dict[str, Any], summary: dict[str, Any], out: Path) -> None:
    project = review.get("project", {})
    report_summary = review.get("summary", {})
    risk_items = summary["risk_items"]
    unclear_items = summary["unclear_items"]
    not_checked_items = summary["not_checked_items"]
    rendered_at = now_iso()
    project_name = str(project.get("name", "Security Audit"))
    title_zh = f"{project_name} 安全审查报告"
    title_en = f"{project_name} Security Audit Report"
    focus_items = p0_p1_focus_items(risk_items, unclear_items)
    source_label = compact_source_label(project)

    css = """
    :root {
      --paper: #f5f4ed;
      --ivory: #faf9f5;
      --sand: #e8e6dc;
      --brand: #1B365D;
      --brand-soft: #E4ECF5;
      --ink: #141413;
      --charcoal: #4d4c48;
      --muted: #5e5d59;
      --line: #e8e5da;
      --critical: #9d1c20;
      --ok: #166534;
      --warn: #8a5a00;
      --mono: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      --serif: "Source Han Serif SC", "Noto Serif CJK SC", "Songti SC", Georgia, serif;
      --sans: "Source Han Sans SC", "Noto Sans CJK SC", -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body { margin: 0; font-family: var(--sans); color: var(--ink); background: var(--paper); line-height: 1.52; }
    .topbar { position: sticky; top: 0; z-index: 30; background: #fffdf8; border-bottom: 1px solid var(--line); box-shadow: 0 1px 0 #f0eee6; }
    .topbar-inner { max-width: 1240px; margin: 0 auto; padding: 10px 28px; display: flex; align-items: center; gap: 16px; }
    .brand-mark { font-size: 12px; font-weight: 800; letter-spacing: 0.06em; color: var(--brand); white-space: nowrap; }
    .nav-links { display: flex; align-items: center; gap: 8px; overflow-x: auto; flex: 1; }
    .nav-links a, .lang-toggle { min-height: 32px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf8; color: var(--charcoal); padding: 6px 10px; text-decoration: none; font-size: 12px; white-space: nowrap; }
    .nav-links a:hover, .lang-toggle:hover { border-color: var(--brand); color: var(--brand); }
    .lang-toggle { cursor: pointer; font-weight: 700; }
    main { max-width: 1240px; margin: 0 auto; padding: 28px 28px 72px; }
    .report-shell { background: var(--ivory); border: 1px solid var(--line); border-radius: 14px; padding: 34px; box-shadow: 0 0 0 1px #f0eee6; }
    section[id] { scroll-margin-top: 76px; }
    .kicker { color: var(--brand); font-size: 12px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; margin: 0 0 10px; }
    h1 { margin: 0; font-family: var(--serif); font-size: clamp(30px, 4.2vw, 52px); font-weight: 500; line-height: 1.12; letter-spacing: 0; color: var(--ink); }
    h2 { margin: 36px 0 14px; font-family: var(--serif); font-size: 22px; font-weight: 500; line-height: 1.22; border-left: 4px solid var(--brand); padding-left: 12px; }
    p { margin: 8px 0; }
    .meta { color: var(--muted); margin-top: 12px; max-width: 920px; }
    .lead { font-size: 15px; color: var(--charcoal); max-width: 980px; }
    .metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 26px 0 24px; }
    .metric { border: 1px solid var(--line); border-radius: 8px; background: #fffdf8; padding: 12px 14px; min-height: 76px; }
    .metric b { display: block; font-family: var(--serif); font-size: 25px; font-weight: 500; line-height: 1.1; color: var(--brand); font-variant-numeric: tabular-nums; }
    .metric span { display: block; margin-top: 6px; color: var(--muted); font-size: 12px; }
    .metric .risk, .risk { color: var(--critical); }
    .ok { color: var(--ok); }
    .brief-grid { display: grid; grid-template-columns: minmax(0, 1.5fr) minmax(280px, 0.8fr); gap: 18px; margin: 16px 0 8px; }
    .panel { border: 1px solid var(--line); border-radius: 8px; background: #fffdf8; padding: 16px 18px; }
    .panel-title { margin: 0 0 8px; color: var(--brand); font-size: 12px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; }
    .section-note { background: #fff8e8; border-left: 4px solid var(--warn); padding: 10px 12px; margin: 12px 0; color: var(--charcoal); }
    .table-wrap { width: 100%; overflow-x: auto; margin: 12px 0 26px; border: 1px solid var(--line); border-radius: 8px; background: #fffdf8; }
    table { width: 100%; border-collapse: collapse; font-size: 12.5px; line-height: 1.42; }
    th, td { border-bottom: 1px solid var(--line); border-right: 1px solid var(--line); padding: 8px 9px; vertical-align: top; }
    th:last-child, td:last-child { border-right: 0; }
    tr:last-child td { border-bottom: 0; }
    th { position: sticky; top: 46px; z-index: 1; background: var(--brand); color: #fffdf8; text-align: left; font-size: 11px; letter-spacing: 0.02em; }
    td { word-break: break-word; color: var(--charcoal); }
    .report-table td:nth-child(1), .report-table td:nth-child(2), .report-table td:nth-child(3), .report-table td:nth-child(6), .report-table td:nth-child(7) { white-space: nowrap; }
    .badge { display: inline-flex; align-items: center; min-height: 20px; padding: 2px 7px; border-radius: 999px; font-size: 11px; font-weight: 700; white-space: nowrap; }
    .badge-risk, .badge-critical, .badge-p0 { background: #f8e7e5; color: var(--critical); }
    .badge-high, .badge-p1 { background: #fff2d6; color: #8a3f00; }
    .badge-medium, .badge-p2, .badge-unclear { background: #fff8e8; color: var(--warn); }
    .badge-safe { background: #eaf4ea; color: var(--ok); }
    .badge-na, .badge-info, .badge-p3 { background: var(--brand-soft); color: var(--brand); }
    .badge-low, .badge-unchecked { background: var(--sand); color: var(--muted); }
    code { font-family: var(--mono); font-size: 0.92em; background: #f4efe4; border: 1px solid var(--line); border-radius: 5px; padding: 1px 4px; }
    .lang-inline.lang-en, .lang-panel.lang-en { display: none; }
    .lang-panel.lang-zh { display: block; }
    body[data-lang="en"] .lang-inline.lang-zh, body[data-lang="en"] .lang-panel.lang-zh { display: none; }
    body[data-lang="en"] .lang-inline.lang-en { display: inline; }
    body[data-lang="en"] .lang-panel.lang-en { display: block; }
    @media print {
      .topbar { position: static; }
      th { position: static; }
      body { background: #ffffff; }
      main { padding: 0; }
      .report-shell { border: 0; box-shadow: none; }
    }
    @media (max-width: 820px) {
      .topbar-inner { padding: 9px 12px; align-items: flex-start; }
      .brand-mark { display: none; }
      main { padding: 18px 12px 44px; }
      .report-shell { padding: 20px 14px; border-radius: 10px; }
      .brief-grid { grid-template-columns: 1fr; }
      h2 { margin-top: 28px; }
    }
    """
    script = """
    (function () {
      const button = document.getElementById("langToggle");
      function setLang(lang) {
        document.body.dataset.lang = lang;
        document.documentElement.lang = lang === "en" ? "en" : "zh-CN";
        button.textContent = lang === "en" ? "中文" : "English";
        button.setAttribute("aria-label", lang === "en" ? "切换到中文" : "Switch to English");
      }
      button.addEventListener("click", function () {
        setLang(document.body.dataset.lang === "en" ? "zh" : "en");
      });
      setLang("zh");
    })();
    """
    empty_focus = dual_html(
        '<p class="ok">没有已记录的 P0/P1 风险或存疑重点。</p>',
        '<p class="ok">No recorded P0/P1 risk or unclear focus items.</p>',
        block=True,
    )
    empty_risks = dual_html(
        '<p class="ok">没有已记录的风险发现。</p>',
        '<p class="ok">No recorded risk findings.</p>',
        block=True,
    )
    empty_unclear = dual_html(
        '<p class="ok">没有存疑项。</p>',
        '<p class="ok">No unclear items.</p>',
        block=True,
    )
    empty_not_checked = dual_html(
        '<p class="ok">没有未检查项。</p>',
        '<p class="ok">No not-checked items.</p>',
        block=True,
    )
    html_text = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title_zh)}</title>
  <style>{css}</style>
</head>
<body data-lang="zh">
<header class="topbar">
  <div class="topbar-inner">
    <div class="brand-mark">YAO SECURITY</div>
    <nav class="nav-links" aria-label="Report sections">
      <a href="#overview">{dual_text("概览", "Overview")}</a>
      <a href="#method">{dual_text("方法", "Method")}</a>
      <a href="#findings">{dual_text("风险发现", "Findings")}</a>
      <a href="#unclear">{dual_text("存疑项", "Unclear")}</a>
      <a href="#scorecard">{dual_text("评分表", "Scorecard")}</a>
      <a href="#retest">{dual_text("复测", "Retest")}</a>
    </nav>
    <button class="lang-toggle" id="langToggle" type="button">English</button>
  </div>
</header>
<main>
  <article class="report-shell">
    <section id="overview">
      <p class="kicker">{dual_text("授权安全审查", "Authorized Security Review")}</p>
      <h1>{dual_text(title_zh, title_en)}</h1>
      <p class="meta">{dual_text(f"{source_label} · 生成时间 {rendered_at}", f"{source_label} · Rendered {rendered_at}")}</p>

      <div class="metrics">
        <div class="metric"><b class="risk">{dual_text(risk_value(summary["overall_risk"], "zh"), risk_value(summary["overall_risk"], "en"))}</b><span>{dual_text("总体风险", "Overall Risk")}</span></div>
        <div class="metric"><b>{summary["overall_score"]}</b><span>{dual_text("总体得分", "Overall Score")}</span></div>
        <div class="metric"><b>{summary["coverage"]}%</b><span>{dual_text("覆盖率", "Coverage")}</span></div>
        <div class="metric"><b>{len(risk_items)}</b><span>{dual_text("存在风险", "Risk Found")}</span></div>
        <div class="metric"><b>{len(unclear_items)}</b><span>{dual_text("存疑", "Unclear")}</span></div>
        <div class="metric"><b>{len(not_checked_items)}</b><span>{dual_text("未检查", "Not Checked")}</span></div>
      </div>

      <h2>{dual_text("执行摘要", "Executive Summary")}</h2>
      <div class="brief-grid">
        <div class="panel">
          <p class="panel-title">{dual_text("摘要", "Summary")}</p>
          <p class="lead">{dual_html(html_report_text(localized_dict_value(report_summary, "executive_summary", "zh"), "未填写执行摘要。"), html_report_text(localized_dict_value(report_summary, "executive_summary", "en"), "No executive summary documented."))}</p>
        </div>
        <div class="panel">
          <p class="panel-title">{dual_text("边界", "Boundary")}</p>
          <p><strong>{dual_text("授权：", "Authorization: ")}</strong>{dual_html(html_report_text(localized_dict_value(report_summary, "authorization", "zh"), "未填写授权说明。"), html_report_text(localized_dict_value(report_summary, "authorization", "en"), "No authorization note documented."))}</p>
          <p><strong>{dual_text("范围：", "Scope: ")}</strong>{dual_html(html_report_text(localized_dict_value(project, "scope", "zh"), "未填写范围。"), html_report_text(localized_dict_value(project, "scope", "en"), "No scope documented."))}</p>
        </div>
      </div>
      <p class="section-note"><strong>{dual_text("覆盖说明：", "Coverage Notes: ")}</strong>{dual_html(html_report_text(localized_dict_value(report_summary, "coverage_notes", "zh"), "未填写覆盖说明。"), html_report_text(localized_dict_value(report_summary, "coverage_notes", "en"), "No coverage notes documented."))}</p>
    </section>

    <section id="method">
      <h2>{dual_text("审查方法与覆盖", "Methodology and Coverage")}</h2>
      {bilingual_table(methodology_rows(review, "zh"), methodology_rows(review, "en"))}

      <h2>{dual_text("状态分布", "Status Distribution")}</h2>
      {bilingual_table(status_distribution_rows(summary, "zh"), status_distribution_rows(summary, "en"))}
    </section>

    <section id="findings">
      <h2>{dual_text("P0/P1 与存疑重点", "P0/P1 and Unclear Focus")}</h2>
      {bilingual_table(findings_rows(focus_items, "zh"), findings_rows(focus_items, "en"), limit=50) if focus_items else empty_focus}

      <h2>{dual_text("详细风险发现", "Detailed Risk Findings")}</h2>
      {bilingual_table(findings_rows(risk_items, "zh"), findings_rows(risk_items, "en")) if risk_items else empty_risks}
    </section>

    <section id="unclear">
      <h2>{dual_text("存疑项", "Unclear Items")}</h2>
      {bilingual_table(findings_rows(unclear_items, "zh"), findings_rows(unclear_items, "en")) if unclear_items else empty_unclear}

      <h2>{dual_text("未检查项", "Not Checked Items")}</h2>
      <div class="section-note">{dual_text("未检查项会降低覆盖率。若属于运行时或主动测试范围，需要补充授权、测试账号、部署 URL 或安全窗口。", "Not-checked items reduce coverage. Runtime or active-test items require authorization, test accounts, a deployed URL, or a safe test window.")}</div>
      {bilingual_table(findings_rows(not_checked_items[:50], "zh"), findings_rows(not_checked_items[:50], "en"), limit=50) if not_checked_items else empty_not_checked}
    </section>

    <section id="retest">
      <h2>{dual_text("残余风险与复测计划", "Residual Risk and Retest Plan")}</h2>
      {bilingual_table(residual_rows(review, "zh"), residual_rows(review, "en"))}
    </section>

    <section id="scorecard">
      <h2>{dual_text("完整评分表", "Full Scorecard")}</h2>
      {bilingual_table(scorecard_rows(review, "zh"), scorecard_rows(review, "en"))}
    </section>
  </article>
</main>
<script>{script}</script>
</body>
</html>
"""
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_text, encoding="utf-8")


def markdown_escape(value: Any) -> str:
    text = display_list(sanitize_report_value(value), "")
    text = text.replace("|", "\\|").replace("\n", "<br>")
    return text


def markdown_table(rows: list[list[Any]], limit: int | None = None) -> str:
    if not rows:
        return ""
    body_rows = rows[1 : limit + 1 if limit else None]
    headers = [markdown_escape(value) for value in rows[0]]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in body_rows:
        cells = [markdown_escape(row[idx] if idx < len(row) else "") for idx in range(len(headers))]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_markdown(review: dict[str, Any], summary: dict[str, Any], out: Path) -> None:
    project = review.get("project", {})
    report_summary = review.get("summary", {})
    risk_items = summary["risk_items"]
    unclear_items = summary["unclear_items"]
    not_checked_items = summary["not_checked_items"]
    focus_items = p0_p1_focus_items(risk_items, unclear_items)
    lines = [
        f"# {markdown_escape(project.get('name', 'Security Audit'))} 安全审查报告",
        "",
        f"- 来源：{markdown_escape(compact_source_label(project))}",
        f"- 生成时间：{markdown_escape(now_iso())}",
        f"- 总体风险：{markdown_escape(risk_value(summary['overall_risk'], 'zh'))}",
        f"- 总体得分：{summary['overall_score']}",
        f"- 覆盖率：{summary['coverage']}%",
        f"- 风险发现：{len(risk_items)}",
        f"- 存疑项：{len(unclear_items)}",
        f"- 未检查项：{len(not_checked_items)}",
        "",
        "## 执行摘要",
        "",
        display_list(sanitize_report_value(localized_dict_value(report_summary, "executive_summary", "zh")), "未填写执行摘要。"),
        "",
        "## 范围与授权",
        "",
        markdown_table(
            [
                ["字段", "值"],
                ["授权", localized_dict_value(report_summary, "authorization", "zh") or "未填写授权说明。"],
                ["范围", localized_dict_value(project, "scope", "zh") or "未填写范围。"],
                ["环境", project.get("environment", "")],
                ["覆盖说明", localized_dict_value(report_summary, "coverage_notes", "zh") or "未填写覆盖说明。"],
            ]
        ),
        "",
        "## 审查方法与覆盖",
        "",
        markdown_table(methodology_rows(review, "zh")),
        "",
        "## 状态分布",
        "",
        markdown_table(status_distribution_rows(summary, "zh")),
        "",
        "## P0/P1 与存疑重点",
        "",
        markdown_table(findings_rows(focus_items, "zh"), limit=50) if focus_items else "没有已记录的 P0/P1 风险或存疑重点。",
        "",
        "## 详细风险发现",
        "",
        markdown_table(findings_rows(risk_items, "zh")) if risk_items else "没有已记录的风险发现。",
        "",
        "## 存疑项",
        "",
        markdown_table(findings_rows(unclear_items, "zh")) if unclear_items else "没有存疑项。",
        "",
        "## 未检查项",
        "",
        "未检查项会降低覆盖率。若属于运行时或主动测试范围，需要补充授权、测试账号、部署 URL 或安全窗口。",
        "",
        markdown_table(findings_rows(not_checked_items[:50], "zh"), limit=50) if not_checked_items else "没有未检查项。",
        "",
        "## 残余风险与复测计划",
        "",
        markdown_table(residual_rows(review, "zh")),
        "",
        "## 完整评分表",
        "",
        markdown_table(scorecard_rows(review, "zh")),
    ]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


PDF_WIDTH = 595.28
PDF_HEIGHT = 841.89
PDF_MARGIN_X = 44.0
PDF_MARGIN_TOP = 54.0
PDF_MARGIN_BOTTOM = 44.0


def pdf_text_units(text: str) -> float:
    units = 0.0
    for ch in text:
        units += 0.55 if ord(ch) < 128 else 1.0
    return units


def pdf_wrap_text(text: Any, max_units: float) -> list[str]:
    raw = display_list(sanitize_report_value(text), "")
    lines: list[str] = []
    for paragraph in raw.splitlines() or [""]:
        current = ""
        current_units = 0.0
        for ch in paragraph:
            ch_units = 0.55 if ord(ch) < 128 else 1.0
            if current and current_units + ch_units > max_units:
                lines.append(current)
                current = ch
                current_units = ch_units
            else:
                current += ch
                current_units += ch_units
        lines.append(current)
    return lines


def pdf_hex_text(text: Any) -> str:
    return str(text or "").encode("utf-16-be", errors="replace").hex().upper()


def pdf_color(color: tuple[float, float, float]) -> str:
    return " ".join(f"{channel:.3f}" for channel in color)


class PdfReport:
    def __init__(self) -> None:
        self.pages: list[list[str]] = []
        self.y = PDF_HEIGHT - PDF_MARGIN_TOP
        self.new_page()

    def new_page(self) -> None:
        self.pages.append([])
        self.y = PDF_HEIGHT - PDF_MARGIN_TOP

    @property
    def commands(self) -> list[str]:
        return self.pages[-1]

    def ensure_space(self, height: float) -> None:
        if self.y - height < PDF_MARGIN_BOTTOM:
            self.new_page()

    def rect(self, x: float, y: float, width: float, height: float, color: tuple[float, float, float]) -> None:
        self.commands.append(f"q {pdf_color(color)} rg {x:.2f} {y:.2f} {width:.2f} {height:.2f} re f Q\n")

    def text(self, x: float, y: float, text: Any, size: float = 10.0, color: tuple[float, float, float] = (0.08, 0.08, 0.07)) -> None:
        if text is None or text == "":
            return
        self.commands.append(
            f"BT /F1 {size:.2f} Tf {pdf_color(color)} rg 1 0 0 1 {x:.2f} {y:.2f} Tm <{pdf_hex_text(text)}> Tj ET\n"
        )

    def line(self, text: Any, size: float = 9.0, indent: float = 0.0, color: tuple[float, float, float] = (0.08, 0.08, 0.07), gap: float = 2.0) -> None:
        max_width = PDF_WIDTH - PDF_MARGIN_X * 2 - indent
        max_units = max_width / size
        for wrapped in pdf_wrap_text(text, max_units):
            self.ensure_space(size * 1.45 + gap)
            self.text(PDF_MARGIN_X + indent, self.y, wrapped, size=size, color=color)
            self.y -= size * 1.45
        self.y -= gap

    def section(self, title: str) -> None:
        self.ensure_space(32)
        self.rect(PDF_MARGIN_X, self.y - 4, 4, 18, (0.105, 0.212, 0.365))
        self.text(PDF_MARGIN_X + 10, self.y, title, size=13, color=(0.105, 0.212, 0.365))
        self.y -= 26

    def metric_row(self, metrics: list[tuple[str, Any]]) -> None:
        self.ensure_space(64)
        gap = 7.0
        box_width = (PDF_WIDTH - PDF_MARGIN_X * 2 - gap * (len(metrics) - 1)) / len(metrics)
        top = self.y
        for idx, (label, value) in enumerate(metrics):
            x = PDF_MARGIN_X + idx * (box_width + gap)
            self.rect(x, top - 44, box_width, 44, (1.0, 0.992, 0.972))
            self.text(x + 7, top - 16, value, size=13, color=(0.105, 0.212, 0.365))
            self.text(x + 7, top - 33, label, size=8, color=(0.36, 0.36, 0.35))
        self.y -= 58


def write_pdf_file(path: Path, pages: list[list[str]]) -> None:
    objects: list[bytes] = []
    objects.append(b"")  # catalog
    objects.append(b"")  # pages
    objects.append(
        b"<< /Type /Font /Subtype /Type0 /BaseFont /STSong-Light /Encoding /UniGB-UCS2-H /DescendantFonts [4 0 R] >>"
    )
    objects.append(
        b"<< /Type /Font /Subtype /CIDFontType0 /BaseFont /STSong-Light /CIDSystemInfo << /Registry (Adobe) /Ordering (GB1) /Supplement 5 >> /DW 1000 >>"
    )
    kids: list[str] = []
    total_pages = len(pages)
    for idx, page_commands in enumerate(pages, start=1):
        footer = (
            f"BT /F1 8.00 Tf 0.360 0.360 0.350 rg 1 0 0 1 {PDF_MARGIN_X:.2f} 24.00 Tm "
            f"<{pdf_hex_text(f'{SKILL_NAME} · 第 {idx}/{total_pages} 页')}> Tj ET\n"
        )
        stream = ("".join(page_commands) + footer).encode("ascii")
        stream_id = len(objects) + 1
        page_id = stream_id + 1
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode("ascii") + stream + b"\nendstream")
        objects.append(
            (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PDF_WIDTH:.2f} {PDF_HEIGHT:.2f}] "
                f"/Resources << /ProcSet [/PDF /Text] /Font << /F1 3 0 R >> >> /Contents {stream_id} 0 R >>"
            ).encode("ascii")
        )
        kids.append(f"{page_id} 0 R")
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(kids)} >>".encode("ascii")

    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj_id, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{obj_id} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_offset}\n%%EOF\n"
        ).encode("ascii")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(pdf))


def render_pdf_builtin(review: dict[str, Any], summary: dict[str, Any], out: Path) -> None:
    project = review.get("project", {})
    report_summary = review.get("summary", {})
    risk_items = summary["risk_items"]
    unclear_items = summary["unclear_items"]
    not_checked_items = summary["not_checked_items"]
    focus_items = p0_p1_focus_items(risk_items, unclear_items)
    pdf = PdfReport()
    pdf.rect(0, PDF_HEIGHT - 96, PDF_WIDTH, 96, (0.965, 0.957, 0.925))
    pdf.text(PDF_MARGIN_X, PDF_HEIGHT - 52, f"{project.get('name', 'Security Audit')} 安全审查报告", size=18, color=(0.08, 0.08, 0.07))
    pdf.text(PDF_MARGIN_X, PDF_HEIGHT - 76, f"{compact_source_label(project)} · 生成时间 {now_iso()}", size=8.5, color=(0.36, 0.36, 0.35))
    pdf.y = PDF_HEIGHT - 124
    pdf.metric_row(
        [
            ("总体风险", risk_value(summary["overall_risk"], "zh")),
            ("总体得分", summary["overall_score"]),
            ("覆盖率", f"{summary['coverage']}%"),
            ("风险发现", len(risk_items)),
            ("存疑", len(unclear_items)),
        ]
    )
    pdf.section("执行摘要")
    pdf.line(localized_dict_value(report_summary, "executive_summary", "zh", "未填写执行摘要。"), size=9.5)
    pdf.section("范围与授权")
    pdf.line(f"授权：{localized_dict_value(report_summary, 'authorization', 'zh', '未填写授权说明。')}", size=9)
    pdf.line(f"范围：{localized_dict_value(project, 'scope', 'zh', '未填写范围。')}", size=9)
    pdf.line(f"覆盖说明：{localized_dict_value(report_summary, 'coverage_notes', 'zh', '未填写覆盖说明。')}", size=9)
    pdf.section("审查方法与覆盖")
    for row in methodology_rows(review, "zh")[1:]:
        pdf.line(f"{row[0]}：{row[1]}", size=8.5)
    pdf.section("状态分布")
    pdf.line("；".join(f"{status_value(status, 'zh')} {count}" for status, count in summary["status_counts"].items()), size=9)

    pdf.section("P0/P1 与存疑重点")
    if focus_items:
        for item in focus_items:
            pdf.line(f"{item.get('check_id')} {item.get('priority')} {status_value(item.get('status'), 'zh')} {severity_value(item.get('severity'), 'zh')} {localized_dict_value(item, 'check_item', 'zh')}", size=9.5, color=(0.105, 0.212, 0.365))
            for label, field in [("证据", "evidence"), ("发现", "finding"), ("影响", "impact"), ("修复建议", "remediation")]:
                value = localized_dict_value(item, field, "zh")
                if value:
                    pdf.line(f"{label}：{value}", size=8.2, indent=10)
    else:
        pdf.line("没有已记录的 P0/P1 风险或存疑重点。", size=9)

    pdf.section("详细风险发现")
    if risk_items:
        for item in sorted(risk_items, key=lambda x: (-priority_weight(x.get("priority")), -SEVERITY_ORDER.get(str(x.get("severity", "")), 0), x.get("check_id", ""))):
            pdf.line(f"{item.get('check_id')} {item.get('priority')} {severity_value(item.get('severity'), 'zh')} {localized_dict_value(item, 'check_item', 'zh')}", size=9.5, color=(0.62, 0.11, 0.13))
            for label, field in [("证据", "evidence"), ("发现", "finding"), ("根因", "root_cause"), ("影响", "impact"), ("修复建议", "remediation")]:
                value = localized_dict_value(item, field, "zh")
                if value:
                    pdf.line(f"{label}：{value}", size=8.2, indent=10)
    else:
        pdf.line("没有已记录的风险发现。", size=9)

    pdf.section("存疑与未检查")
    if unclear_items:
        for item in unclear_items:
            pdf.line(f"{item.get('check_id')} {item.get('priority')} 存疑 {localized_dict_value(item, 'check_item', 'zh')}：{localized_dict_value(item, 'evidence', 'zh')}", size=8.4)
    else:
        pdf.line("没有存疑项。", size=8.5)
    if not_checked_items:
        pdf.line(f"未检查项数量：{len(not_checked_items)}。完整明细见 Markdown/Excel 评分表。", size=8.5)

    pdf.section("残余风险与复测计划")
    for row in residual_rows(review, "zh")[1:]:
        pdf.line(f"{row[0]}：{row[1]}", size=8.8)

    pdf.section("完整评分表摘要")
    for item in review.get("checks", []):
        pdf.line(
            f"{item.get('check_id')} | {item.get('priority')} | {status_value(item.get('status'), 'zh')} | {localized_dict_value(item, 'domain', 'zh')} | {localized_dict_value(item, 'check_item', 'zh')}",
            size=7.4,
        )
    write_pdf_file(out, pdf.pages)


def pdf_print_text(value: Any, fallback: str = "") -> str:
    text = display_list(sanitize_report_value(value), fallback)
    return html.escape(text).replace("\n", "<br>")


def pdf_print_table(rows: list[list[Any]], css_class: str = "") -> str:
    if not rows:
        return ""
    headers = rows[0]
    head = "".join(f"<th>{pdf_print_text(value)}</th>" for value in headers)
    body = []
    for row in rows[1:]:
        cells = "".join(f"<td>{pdf_print_text(row[idx] if idx < len(row) else '')}</td>" for idx in range(len(headers)))
        body.append(f"<tr>{cells}</tr>")
    return f'<table class="{css_class}"><thead><tr>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'


def pdf_finding_blocks(items: list[dict[str, Any]], empty: str, limit: int | None = None) -> str:
    selected = items[:limit] if limit else items
    if not selected:
        return f'<p class="empty">{html.escape(empty)}</p>'
    blocks = []
    for item in sorted(
        selected,
        key=lambda x: (-priority_weight(x.get("priority")), -SEVERITY_ORDER.get(str(x.get("severity", "")), 0), x.get("check_id", "")),
    ):
        title = f"{item.get('check_id', '')} {item.get('priority', '')} · {localized_dict_value(item, 'check_item', 'zh')}"
        meta = " / ".join(
            part
            for part in [
                status_value(item.get("status"), "zh"),
                severity_value(item.get("severity"), "zh"),
                confidence_value(item.get("confidence"), "zh"),
                item.get("source_file_or_endpoint", ""),
            ]
            if part
        )
        detail_rows = []
        for label, field in [("证据", "evidence"), ("发现", "finding"), ("根因", "root_cause"), ("影响", "impact"), ("修复建议", "remediation")]:
            value = localized_dict_value(item, field, "zh")
            if value:
                detail_rows.append(f'<p><strong>{label}：</strong>{pdf_print_text(value)}</p>')
        blocks.append(
            '<article class="finding">'
            f'<h3>{pdf_print_text(title)}</h3>'
            f'<p class="finding-meta">{pdf_print_text(meta)}</p>'
            + "".join(detail_rows)
            + "</article>"
        )
    return "".join(blocks)


def scorecard_appendix_rows(review: dict[str, Any]) -> list[list[Any]]:
    rows = [["编号", "优先级", "风险域", "检查项", "状态", "严重性", "证据摘要"]]
    for item in review.get("checks", []):
        rows.append(
            [
                item.get("check_id", ""),
                item.get("priority", ""),
                localized_dict_value(item, "domain", "zh"),
                localized_dict_value(item, "check_item", "zh"),
                status_value(item.get("status"), "zh"),
                severity_value(item.get("severity"), "zh"),
                localized_dict_value(item, "evidence", "zh"),
            ]
        )
    return rows


def render_pdf_print_html(review: dict[str, Any], summary: dict[str, Any]) -> str:
    project = review.get("project", {})
    report_summary = review.get("summary", {})
    risk_items = summary["risk_items"]
    unclear_items = summary["unclear_items"]
    not_checked_items = summary["not_checked_items"]
    focus_items = p0_p1_focus_items(risk_items, unclear_items)
    rendered_at = now_iso()
    status_text = "；".join(f"{status_value(status, 'zh')} {count}" for status, count in summary["status_counts"].items())
    css = """
    @page { size: A4; margin: 14mm 13mm 15mm; }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: #141413;
      background: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Source Han Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", Arial, sans-serif;
      font-size: 10.5px;
      line-height: 1.55;
      letter-spacing: 0;
    }
    .cover {
      padding: 18px 0 16px;
      border-bottom: 2px solid #1B365D;
      margin-bottom: 14px;
    }
    .kicker {
      color: #1B365D;
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.06em;
      margin: 0 0 5px;
      text-transform: uppercase;
    }
    h1 {
      margin: 0;
      font-size: 27px;
      line-height: 1.15;
      font-weight: 650;
      letter-spacing: 0;
    }
    .meta {
      margin-top: 7px;
      color: #5e5d59;
      font-size: 9.5px;
      word-break: break-word;
    }
    .metrics {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 7px;
      margin: 12px 0 16px;
    }
    .metric {
      min-height: 46px;
      padding: 8px 9px;
      background: #faf9f5;
      border: 1px solid #e8e5da;
      border-radius: 4px;
    }
    .metric b {
      display: block;
      color: #1B365D;
      font-size: 15px;
      line-height: 1.1;
      font-weight: 700;
      letter-spacing: 0;
    }
    .metric span {
      display: block;
      margin-top: 5px;
      color: #5e5d59;
      font-size: 8.8px;
    }
    section {
      margin-top: 13px;
      break-inside: auto;
    }
    h2 {
      margin: 13px 0 7px;
      padding-left: 8px;
      border-left: 4px solid #1B365D;
      color: #1B365D;
      font-size: 15px;
      line-height: 1.25;
      font-weight: 650;
      letter-spacing: 0;
      break-after: avoid;
    }
    h3 {
      margin: 0 0 4px;
      color: #141413;
      font-size: 11.5px;
      line-height: 1.3;
      font-weight: 700;
      letter-spacing: 0;
    }
    p { margin: 0 0 5px; }
    .note {
      padding: 8px 10px;
      background: #fff8e8;
      border-left: 4px solid #8a5a00;
      margin: 8px 0;
      break-inside: avoid;
    }
    .finding {
      margin: 0 0 8px;
      padding: 8px 10px;
      border: 1px solid #e8e5da;
      border-left: 4px solid #9d1c20;
      border-radius: 4px;
      background: #fffdf8;
      break-inside: avoid;
      page-break-inside: avoid;
    }
    .finding-meta {
      color: #5e5d59;
      font-size: 8.8px;
      margin-bottom: 5px;
      word-break: break-word;
    }
    .empty { color: #166534; }
    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      margin: 6px 0 10px;
      break-inside: auto;
      page-break-inside: auto;
    }
    thead { display: table-header-group; }
    tr { break-inside: avoid; page-break-inside: avoid; }
    th, td {
      border: 1px solid #e8e5da;
      padding: 4px 5px;
      vertical-align: top;
      word-break: break-word;
      overflow-wrap: anywhere;
    }
    th {
      background: #1B365D;
      color: #ffffff;
      font-size: 8.5px;
      text-align: left;
      font-weight: 700;
    }
    td { font-size: 8.3px; }
    .method-table td:first-child, .status-table td:first-child { width: 24%; font-weight: 700; color: #1B365D; }
    .scorecard { font-size: 7.2px; }
    .scorecard th, .scorecard td { padding: 3px 4px; font-size: 7.2px; }
    .scorecard th:nth-child(1), .scorecard td:nth-child(1) { width: 7%; }
    .scorecard th:nth-child(2), .scorecard td:nth-child(2) { width: 6%; }
    .scorecard th:nth-child(3), .scorecard td:nth-child(3) { width: 14%; }
    .scorecard th:nth-child(4), .scorecard td:nth-child(4) { width: 20%; }
    .scorecard th:nth-child(5), .scorecard td:nth-child(5) { width: 8%; }
    .scorecard th:nth-child(6), .scorecard td:nth-child(6) { width: 8%; }
    .scorecard th:nth-child(7), .scorecard td:nth-child(7) { width: 37%; }
    .page-break { break-before: page; page-break-before: always; }
    """
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <title>{pdf_print_text(project.get('name', 'Security Audit'))} 安全审查报告</title>
  <style>{css}</style>
</head>
<body>
  <header class="cover">
    <p class="kicker">Authorized Security Review</p>
    <h1>{pdf_print_text(project.get('name', 'Security Audit'))} 安全审查报告</h1>
    <p class="meta">{pdf_print_text(compact_source_label(project))} · 生成时间 {pdf_print_text(rendered_at)}</p>
  </header>

  <div class="metrics">
    <div class="metric"><b>{pdf_print_text(risk_value(summary["overall_risk"], "zh"))}</b><span>总体风险</span></div>
    <div class="metric"><b>{summary["overall_score"]}</b><span>总体得分</span></div>
    <div class="metric"><b>{summary["coverage"]}%</b><span>覆盖率</span></div>
    <div class="metric"><b>{len(risk_items)}</b><span>风险发现</span></div>
    <div class="metric"><b>{len(unclear_items)}</b><span>存疑</span></div>
  </div>

  <section>
    <h2>执行摘要</h2>
    <p>{pdf_print_text(localized_dict_value(report_summary, "executive_summary", "zh"), "未填写执行摘要。")}</p>
  </section>

  <section>
    <h2>范围与授权</h2>
    <p><strong>授权：</strong>{pdf_print_text(localized_dict_value(report_summary, "authorization", "zh"), "未填写授权说明。")}</p>
    <p><strong>范围：</strong>{pdf_print_text(localized_dict_value(project, "scope", "zh"), "未填写范围。")}</p>
    <p><strong>覆盖说明：</strong>{pdf_print_text(localized_dict_value(report_summary, "coverage_notes", "zh"), "未填写覆盖说明。")}</p>
  </section>

  <section>
    <h2>审查方法与覆盖</h2>
    {pdf_print_table(methodology_rows(review, "zh"), "method-table")}
  </section>

  <section>
    <h2>状态分布</h2>
    <p>{pdf_print_text(status_text)}</p>
    {pdf_print_table(status_distribution_rows(summary, "zh"), "status-table")}
  </section>

  <section>
    <h2>P0/P1 与存疑重点</h2>
    {pdf_finding_blocks(focus_items, "没有已记录的 P0/P1 风险或存疑重点。")}
  </section>

  <section class="page-break">
    <h2>详细风险发现</h2>
    {pdf_finding_blocks(summary["risk_items"], "没有已记录的风险发现。")}
  </section>

  <section>
    <h2>存疑项</h2>
    {pdf_finding_blocks(summary["unclear_items"], "没有存疑项。")}
    <div class="note">未检查项数量：{len(not_checked_items)}。若后续加入运行时或主动测试范围，需要补充授权、测试账号、部署 URL 或安全窗口。</div>
  </section>

  <section>
    <h2>残余风险与复测计划</h2>
    {pdf_print_table(residual_rows(review, "zh"), "method-table")}
  </section>

  <section class="page-break">
    <h2>完整评分表摘要</h2>
    {pdf_print_table(scorecard_appendix_rows(review), "scorecard")}
  </section>
</body>
</html>
"""


def find_pdf_browser() -> str | None:
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    executable_names = [
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "microsoft-edge",
        "msedge",
    ]
    for name in executable_names:
        path = shutil.which(name)
        if path:
            return path
    return None


def render_pdf_with_browser(review: dict[str, Any], summary: dict[str, Any], out: Path, browser: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="yao-security-pdf-") as tmp:
        tmp_path = Path(tmp)
        html_path = tmp_path / "report-print.html"
        pdf_path = tmp_path / "report-print.pdf"
        html_path.write_text(render_pdf_print_html(review, summary), encoding="utf-8")
        user_data_dir = tmp_path / "chrome-profile"
        command_base = [
            browser,
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            "--disable-dev-shm-usage",
            "--disable-background-networking",
            "--disable-extensions",
            f"--user-data-dir={user_data_dir}",
            "--no-pdf-header-footer",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ]
        for headless_flag in ("--headless=new", "--headless"):
            proc = subprocess.Popen(
                [command_base[0], headless_flag, *command_base[1:]],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            try:
                last_size = -1
                stable_ticks = 0
                deadline = time.monotonic() + 45
                while time.monotonic() < deadline:
                    if pdf_path.exists():
                        size = pdf_path.stat().st_size
                        if size > 1000 and size == last_size:
                            stable_ticks += 1
                        else:
                            stable_ticks = 0
                        last_size = size
                        if stable_ticks >= 3:
                            proc.terminate()
                            try:
                                proc.wait(timeout=3)
                            except subprocess.TimeoutExpired:
                                proc.kill()
                            shutil.copyfile(pdf_path, out)
                            return
                    if proc.poll() is not None:
                        break
                    time.sleep(0.25)
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                if pdf_path.exists() and pdf_path.stat().st_size > 1000:
                    shutil.copyfile(pdf_path, out)
                    return
            finally:
                if proc.poll() is None:
                    proc.kill()
        raise RuntimeError("Headless browser PDF rendering failed")


def render_pdf(review: dict[str, Any], summary: dict[str, Any], out: Path) -> None:
    browser = find_pdf_browser()
    if browser:
        try:
            render_pdf_with_browser(review, summary, out, browser)
            return
        except Exception:
            pass
    render_pdf_builtin(review, summary, out)


def render_review(args: argparse.Namespace) -> None:
    raw_review = read_json(Path(args.review))
    out_dir = Path(args.out_dir)
    guard_paths = [out_dir]
    if args.update_review:
        guard_paths.append(Path(args.review))
    ensure_outputs_outside_source(raw_review.get("project", {}).get("source", ""), guard_paths)
    review = sanitize_structure(raw_review)
    summary = summarize(review)
    review.setdefault("summary", {})["overall_risk"] = summary["overall_risk"]

    xlsx_path = out_dir / "安全审查评分表.xlsx"
    html_path = out_dir / "安全审查报告.html"
    markdown_path = out_dir / "安全审查报告.md"
    pdf_path = out_dir / "安全审查报告.pdf"
    json_path = out_dir / "security_review.sanitized.json"
    if args.update_review:
        write_json(Path(args.review), review)
    write_json(json_path, review)
    sheets = {
        "总览": overview_rows(review, summary),
        "安全评分表": scorecard_rows(review),
        "风险发现": findings_rows(summary["risk_items"]),
        "存疑和未检查": findings_rows(summary["unclear_items"] + summary["not_checked_items"]),
        "清单基准": ontology_rows(review),
    }
    write_xlsx(xlsx_path, sheets)
    render_html(review, summary, html_path)
    render_markdown(review, summary, markdown_path)
    render_pdf(review, summary, pdf_path)
    compact_summary = {
        key: value
        for key, value in summary.items()
        if key not in {"risk_items", "unclear_items", "not_checked_items"}
    }
    compact_summary["risk_item_count"] = len(summary["risk_items"])
    compact_summary["unclear_item_count"] = len(summary["unclear_items"])
    compact_summary["not_checked_item_count"] = len(summary["not_checked_items"])
    print(
        json.dumps(
            {
                "xlsx": str(xlsx_path.resolve()),
                "html": str(html_path.resolve()),
                "markdown": str(markdown_path.resolve()),
                "pdf": str(pdf_path.resolve()),
                "json": str(json_path.resolve()),
                "summary": compact_summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Web security audit report helper")
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser("extract-kb", help="extract V001-V275 ontology CSV from the source method report")
    p_extract.add_argument("--source-report", required=True)
    p_extract.add_argument("--out", default=str(DEFAULT_ONTOLOGY))
    p_extract.set_defaults(func=lambda args: print(f"Extracted {extract_kb_from_source(Path(args.source_report), Path(args.out))} checks: {Path(args.out).resolve()}"))

    p_prepare = sub.add_parser("prepare-env", help="copy/clone a target into an isolated audit workdir and create temp runtime metadata")
    p_prepare.add_argument("--source", required=True)
    p_prepare.add_argument("--workdir", required=True)
    p_prepare.add_argument("--project", default="")
    p_prepare.add_argument("--mode", choices=sorted(AUDIT_MODES), default="static")
    p_prepare.add_argument("--intensity", choices=sorted(AUDIT_INTENSITIES), default="passive")
    p_prepare.add_argument("--allowed-tests", default="", help="comma-separated active test classes; valid keys include runtime-check, passive-dast, online-probing, blind-oob, bruteforce, file-mutation, database-write, resource-pressure")
    p_prepare.add_argument("--runtime-url", default="")
    p_prepare.add_argument("--online-target", default="")
    p_prepare.add_argument("--oob-endpoint", default="")
    p_prepare.add_argument("--reuse", action="store_true", help="allow using an existing non-empty audit workdir")
    p_prepare.set_defaults(func=prepare_env)

    p_init = sub.add_parser("init", help="initialize a review JSON from the ontology")
    p_init.add_argument("--project", required=True)
    p_init.add_argument("--source", required=True)
    p_init.add_argument("--scope", default="authorized defensive security review")
    p_init.add_argument("--environment", default="repo-only")
    p_init.add_argument("--mode", choices=sorted(AUDIT_MODES), default="static")
    p_init.add_argument("--intensity", choices=sorted(AUDIT_INTENSITIES), default="passive")
    p_init.add_argument("--allowed-tests", default="")
    p_init.add_argument("--runtime-url", default="")
    p_init.add_argument("--online-target", default="")
    p_init.add_argument("--oob-endpoint", default="")
    p_init.add_argument("--ontology", default=str(DEFAULT_ONTOLOGY))
    p_init.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    p_init.add_argument("--out", required=True)
    p_init.set_defaults(func=init_review)

    p_render = sub.add_parser("render", help="render XLSX, HTML, Markdown, and PDF reports from a completed review JSON")
    p_render.add_argument("--review", required=True)
    p_render.add_argument("--out-dir", required=True)
    p_render.add_argument("--update-review", action="store_true", help="write normalized statuses and overall risk back to the review JSON")
    p_render.set_defaults(func=render_review)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
