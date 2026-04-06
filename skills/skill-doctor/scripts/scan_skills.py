#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".turbo",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "_skill_doctor_reports",
    "_skill_doctor_archive",
    "_skill_doctor_quarantine",
    "_skill_doctor_deleted",
}

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".py",
    ".sh",
    ".bash",
    ".zsh",
    ".js",
    ".cjs",
    ".mjs",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".css",
    ".sql",
    ".ini",
    ".cfg",
    ".conf",
    ".env",
    ".xml",
}

USAGE_FILE_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".html",
    ".js",
}

MAX_TEXT_BYTES = 512 * 1024
NOW = datetime.now(timezone.utc)

SECRET_FILE_PATTERNS = [
    (re.compile(r"^\.env\.example$", re.IGNORECASE), "low", "example env file present inside skill"),
    (re.compile(r"^\.env($|\.(local|prod|production|development|staging|test))", re.IGNORECASE), "high", "env file present inside skill"),
    (re.compile(r".*\.(pem|key|p12|pfx)$", re.IGNORECASE), "critical", "private key or certificate file present inside skill"),
]

RISK_PATTERNS = [
    ("hardcoded-secret", "critical", re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|DSA|PRIVATE) KEY-----"), "embedded private key material"),
    ("hardcoded-secret", "high", re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS-style access key found"),
    ("hardcoded-secret", "high", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "GitHub token-like value found"),
    ("hardcoded-secret", "high", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token-like value found"),
    ("hardcoded-secret", "high", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "API key-like value found"),
    (
        "hardcoded-secret",
        "high",
        re.compile(
            r"(?im)^[^\n]*\b(api(?:[_-]?|)key|access(?:[_-]?|)token|secret(?:[_-]?|)key|client(?:[_-]?|)secret|refresh(?:[_-]?|)token)\b[^\n]{0,40}[:=]\s*['\"]([^'\"]{8,})['\"]"
        ),
        "hardcoded secret assignment found",
    ),
    ("unsafe-exec", "critical", re.compile(r"\b(curl|wget)\b[^\n|]{0,200}\|\s*(sh|bash)\b"), "remote script is piped into a shell"),
    ("unsafe-exec", "critical", re.compile(r"\brm\s+-rf\s+/\b"), "destructive shell command targets root"),
    ("unsafe-exec", "high", re.compile(r"\beval\s*\("), "dynamic eval detected"),
    ("unsafe-exec", "high", re.compile(r"\bexec\s*\("), "dynamic exec detected"),
    ("unsafe-exec", "high", re.compile(r"\bpickle\.loads\s*\("), "unsafe pickle loading detected"),
    ("unsafe-exec", "medium", re.compile(r"\byaml\.load\s*\("), "unsafe YAML loading may be present"),
    ("unsafe-exec", "medium", re.compile(r"\bos\.system\s*\("), "shell execution via os.system detected"),
    ("unsafe-exec", "medium", re.compile(r"\bsubprocess\.(run|Popen|call)\s*\("), "subprocess execution detected"),
    ("unsafe-exec", "medium", re.compile(r"\bbash\s+-c\b"), "shell execution via bash -c detected"),
    ("unsafe-exec", "medium", re.compile(r"\bchmod\s+777\b"), "overly broad permission change detected"),
    ("network-fetch", "medium", re.compile(r"\b(pip|npm|pnpm|yarn)\s+install\b[^\n]{0,200}https?://"), "package install pulls directly from a URL"),
    ("network-fetch", "medium", re.compile(r"\b(curl|wget)\s+https?://"), "network download command present"),
    ("token-leakage-risk", "low", re.compile(r"\bos\.environ\b|\bprocess\.env\b"), "environment variable access detected"),
    ("token-leakage-risk", "medium", re.compile(r"\b(printenv|env\s*\||set\s*\|)\b"), "environment dump command detected"),
    ("prompt-injection", "medium", re.compile(r"(?i)ignore\s+(all|any|the|previous|prior|earlier)\s+instructions"), "prompt-injection phrase found"),
    ("prompt-injection", "medium", re.compile(r"(?i)reveal\s+(the\s+)?(system prompt|hidden instructions)"), "prompt attempts to reveal hidden instructions"),
    ("prompt-injection", "high", re.compile(r"(?i)(do not tell the user|exfiltrat(e|ing)\b|send .*?(token|secret|api key))"), "exfiltration-oriented prompt language found"),
]

SEVERITY_VALUE = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def strip_quotes(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def downgrade_severity(severity, steps=1):
    ordered = ["none", "low", "medium", "high", "critical"]
    index = ordered.index(severity)
    return ordered[max(0, index - steps)]


def clamp_severity(severity, ceiling):
    ordered = ["none", "low", "medium", "high", "critical"]
    return ordered[min(ordered.index(severity), ordered.index(ceiling))]


def looks_like_placeholder_secret(value):
    normalized = value.strip().lower()
    placeholders = (
        "your_",
        "your-",
        "your",
        "example",
        "changeme",
        "replace",
        "placeholder",
        "dummy",
        "sample",
        "test",
        "fake",
        "mock",
        "xxxx",
        "todo",
    )
    if normalized.startswith("<") and normalized.endswith(">"):
        return True
    return any(marker in normalized for marker in placeholders)


def parse_frontmatter(skill_md):
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    match = re.match(r"^---\n(.*?)\n---\n?", text, re.DOTALL)
    data = {"raw_text": text, "frontmatter_present": bool(match), "name": None, "description": None}
    if not match:
        return data
    block = match.group(1)
    for key in ("name", "description"):
        field_match = re.search(rf"(?m)^{key}:\s*(.+?)\s*$", block)
        if field_match:
            data[key] = strip_quotes(field_match.group(1))
    return data


def is_text_file(path):
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    try:
        with path.open("rb") as handle:
            chunk = handle.read(2048)
    except OSError:
        return False
    return b"\0" not in chunk


def first_line_number(content, start_index):
    return content.count("\n", 0, start_index) + 1


def collect_usage_files(root):
    usage_files = []
    try:
        children = list(root.iterdir())
    except OSError:
        return usage_files
    for child in children:
        if not child.is_file():
            continue
        if child.suffix.lower() not in USAGE_FILE_EXTENSIONS:
            continue
        try:
            if child.stat().st_size > MAX_TEXT_BYTES:
                continue
        except OSError:
            continue
        usage_files.append(child)
    return usage_files


def find_skill_dirs(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        if "SKILL.md" in filenames:
            found.append(Path(dirpath))
    return sorted(found)


def collect_skill_files(skill_dir):
    files = []
    for dirpath, dirnames, filenames in os.walk(skill_dir):
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]
        for filename in filenames:
            files.append(Path(dirpath) / filename)
    return files


def summarize_purpose(frontmatter):
    description = frontmatter.get("description")
    if description:
        sentence = description.split(". ")[0].strip()
        return sentence.rstrip(".")
    body = frontmatter.get("raw_text", "")
    headings = re.findall(r"(?m)^#\s+(.+)$", body)
    if headings:
        return headings[0].strip()
    return "No purpose summary found"


def has_agent_metadata(skill_dir):
    agents_dir = skill_dir / "agents"
    if not agents_dir.exists():
        return False
    return (agents_dir / "openai.yaml").exists() or (agents_dir / "interface.yaml").exists()


def usage_estimate(latest_mtime, mention_count):
    if latest_mtime is None:
        return "unknown", "low", ["no readable files found"]

    age_days = max(0, int((NOW - latest_mtime).total_seconds() // 86400))
    evidence = [f"latest file modified {age_days} day(s) ago"]
    if mention_count:
        evidence.append(f"mentioned {mention_count} time(s) in top-level inventory files")

    score = 0
    if age_days <= 30:
        score += 2
    elif age_days <= 90:
        score += 1
    elif age_days > 180:
        score -= 1
    if mention_count >= 3:
        score += 2
    elif mention_count >= 1:
        score += 1

    if score >= 3:
        label = "active"
    elif score >= 1:
        label = "warm"
    elif age_days > 180 and mention_count == 0:
        label = "cold"
    else:
        label = "unknown"

    if age_days <= 90 and mention_count >= 1:
        confidence = "high"
    elif age_days <= 90 or mention_count >= 1 or age_days > 180:
        confidence = "medium"
    else:
        confidence = "low"

    return label, confidence, evidence


def cleanup_assessment(skill_dir, frontmatter, files, latest_mtime, security_level):
    reasons = []
    direction = "keep"
    level = "low"
    text = frontmatter.get("raw_text", "")
    age_days = None
    if latest_mtime is not None:
        age_days = max(0, int((NOW - latest_mtime).total_seconds() // 86400))

    if not frontmatter.get("frontmatter_present"):
        reasons.append("missing YAML frontmatter")
    if not frontmatter.get("name"):
        reasons.append("missing frontmatter name")
    if not frontmatter.get("description"):
        reasons.append("missing frontmatter description")
    if "TODO:" in text or "[TODO" in text:
        reasons.append("placeholder TODO text remains")
    if not has_agent_metadata(skill_dir):
        reasons.append("agents metadata is missing")
    if len(files) <= 2:
        reasons.append("skill is structurally thin")
    if age_days is not None and age_days > 365:
        reasons.append("skill appears stale for more than one year")

    disposable_markers = {"dist", "tmp", "fixture", "fixtures", "snapshot", "generated"}
    if any(part.lower() in disposable_markers for part in skill_dir.parts):
        reasons.append("path suggests generated or disposable artifact")

    if security_level in {"high", "critical"}:
        return "critical", "quarantine", ["security risk overrides routine cleanup"]

    if any("generated or disposable artifact" in reason for reason in reasons):
        direction = "backup-then-delete"
        level = "high"
    elif any("stale" in reason for reason in reasons) and len(reasons) >= 2:
        direction = "backup-then-archive"
        level = "high"
    elif reasons:
        direction = "repair"
        level = "medium"

    return level, direction, reasons or ["no cleanup pressure detected"]


def scan_security(skill_dir, files):
    findings = []
    seen = set()

    for path in files:
        rel_path = path.relative_to(skill_dir).as_posix()

        for pattern, severity, message in SECRET_FILE_PATTERNS:
            if pattern.match(path.name):
                key = (rel_path, severity, message)
                if key not in seen:
                    seen.add(key)
                    findings.append(
                        {
                            "category": "secret-file",
                            "severity": severity,
                            "path": rel_path,
                            "line": None,
                            "message": message,
                        }
                    )

        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > MAX_TEXT_BYTES or not is_text_file(path):
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        for category, severity, regex, message in RISK_PATTERNS:
            match = regex.search(content)
            if not match:
                continue
            line = first_line_number(content, match.start())
            line_text = content.splitlines()[line - 1] if content.splitlines() else ""
            adjusted_severity = severity
            adjusted_message = message

            if category == "hardcoded-secret" and match.lastindex:
                candidate_value = match.group(match.lastindex)
                if looks_like_placeholder_secret(candidate_value):
                    continue

            if rel_path.startswith("references/") and category in {
                "prompt-injection",
                "unsafe-exec",
                "network-fetch",
                "token-leakage-risk",
            }:
                adjusted_severity = clamp_severity(adjusted_severity, "low")
                adjusted_message += " (contextual mention in reference docs)"

            if "re.compile(" in line_text:
                adjusted_severity = clamp_severity(adjusted_severity, "low")
                adjusted_message += " (pattern definition context)"

            if adjusted_severity == "none":
                continue

            key = (category, adjusted_severity, rel_path, adjusted_message)
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                {
                    "category": category,
                    "severity": adjusted_severity,
                    "path": rel_path,
                    "line": line,
                    "message": adjusted_message,
                }
            )

    if not findings:
        return "none", []

    severity_counter = Counter(item["severity"] for item in findings)
    highest = max(findings, key=lambda item: SEVERITY_VALUE[item["severity"]])["severity"]
    if highest == "high" and severity_counter["high"] >= 2:
        highest = "critical"

    return highest, sorted(
        findings,
        key=lambda item: (
            -SEVERITY_VALUE[item["severity"]],
            item["path"],
            item["line"] or 0,
            item["category"],
        ),
    )


def count_mentions(skill_dir, frontmatter, usage_files):
    tokens = {skill_dir.name.lower()}
    if frontmatter.get("name"):
        tokens.add(frontmatter["name"].lower())
    count = 0
    for usage_file in usage_files:
        try:
            content = usage_file.read_text(encoding="utf-8", errors="replace").lower()
        except OSError:
            continue
        for token in tokens:
            count += content.count(token)
    return count


def latest_mtime(files):
    timestamps = []
    for path in files:
        try:
            timestamps.append(datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc))
        except OSError:
            continue
    return max(timestamps) if timestamps else None


def scan_root(root):
    usage_files = collect_usage_files(root)
    skill_dirs = find_skill_dirs(root)
    reports = []

    for skill_dir in skill_dirs:
        files = collect_skill_files(skill_dir)
        frontmatter = parse_frontmatter(skill_dir / "SKILL.md")
        mention_count = count_mentions(skill_dir, frontmatter, usage_files)
        modified_at = latest_mtime(files)
        usage_label, usage_confidence, usage_evidence = usage_estimate(modified_at, mention_count)
        security_level, security_findings = scan_security(skill_dir, files)
        cleanup_level, cleanup_direction, cleanup_reasons = cleanup_assessment(
            skill_dir, frontmatter, files, modified_at, security_level
        )

        reports.append(
            {
                "path": str(skill_dir.resolve()),
                "declared_name": frontmatter.get("name") or skill_dir.name,
                "purpose_summary": summarize_purpose(frontmatter),
                "file_count": len(files),
                "resource_dirs": [
                    name for name in ("agents", "scripts", "references", "assets") if (skill_dir / name).exists()
                ],
                "last_modified_utc": modified_at.isoformat().replace("+00:00", "Z") if modified_at else None,
                "usage_estimate": usage_label,
                "usage_confidence": usage_confidence,
                "usage_evidence": usage_evidence,
                "cleanup_level": cleanup_level,
                "cleanup_direction": cleanup_direction,
                "cleanup_reasons": cleanup_reasons,
                "security_level": security_level,
                "security_findings": security_findings,
            }
        )

    return reports


def markdown_report(roots, reports):
    lines = []
    lines.append("# Skill Doctor Report")
    lines.append("")
    lines.append(f"Scanned roots: {', '.join(str(root.resolve()) for root in roots)}")
    lines.append(f"Skills found: {len(reports)}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Skill | Usage | Cleanup | Direction | Security |")
    lines.append("| --- | --- | --- | --- | --- |")
    for item in reports:
        lines.append(
            f"| `{item['declared_name']}` | `{item['usage_estimate']}` | `{item['cleanup_level']}` | "
            f"`{item['cleanup_direction']}` | `{item['security_level']}` |"
        )

    for item in reports:
        lines.append("")
        lines.append(f"## {item['declared_name']}")
        lines.append("")
        lines.append(f"- Path: `{item['path']}`")
        lines.append(f"- Purpose: {item['purpose_summary']}")
        lines.append(
            f"- Usage: `{item['usage_estimate']}` with `{item['usage_confidence']}` confidence"
        )
        lines.append(f"- Usage evidence: {'; '.join(item['usage_evidence'])}")
        lines.append(
            f"- Cleanup: `{item['cleanup_level']}` -> `{item['cleanup_direction']}`"
        )
        lines.append(f"- Cleanup reasons: {'; '.join(item['cleanup_reasons'])}")
        lines.append(f"- Security: `{item['security_level']}`")
        if item["security_findings"]:
            lines.append("- Security findings:")
            for finding in item["security_findings"][:10]:
                location = finding["path"]
                if finding["line"]:
                    location += f":{finding['line']}"
                lines.append(
                    f"  - [{finding['severity']}] {finding['category']} at `{location}`: {finding['message']}"
                )
        else:
            lines.append("- Security findings: none")

    return "\n".join(lines)


def sort_reports(reports):
    reports.sort(
        key=lambda item: (
            -SEVERITY_VALUE[item["security_level"]],
            -SEVERITY_VALUE[item["cleanup_level"]],
            item["declared_name"].lower(),
        )
    )
    return reports


def build_payload(roots, reports):
    return {
        "scanned_roots": [str(root.resolve()) for root in roots],
        "generated_at_utc": NOW.isoformat().replace("+00:00", "Z"),
        "skill_count": len(reports),
        "skills": reports,
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Scan local skill folders for hygiene and security issues.")
    parser.add_argument("roots", nargs="+", help="Root directories to scan")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    roots = [Path(root).expanduser() for root in args.roots]

    all_reports = []
    for root in roots:
        if not root.exists():
            print(f"[ERROR] Root does not exist: {root}", file=sys.stderr)
            return 1
        all_reports.extend(scan_root(root))

    sort_reports(all_reports)

    if args.format == "json":
        payload = build_payload(roots, all_reports)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(markdown_report(roots, all_reports))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
