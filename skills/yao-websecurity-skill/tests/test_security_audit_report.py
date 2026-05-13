#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "security_audit_report.py"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, cwd=ROOT)


def run_result(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)


def assert_not_contains(path: Path, forbidden: list[str]) -> None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for value in forbidden:
        assert value not in text, f"{value!r} leaked into {path}"


def test_render_sanitizes_reports_and_adds_required_sections() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        review_path = tmp_path / "review.json"
        out_dir = tmp_path / "report"
        fake_cookie = "sessionid=" + "abc123"
        fake_bearer = "Bearer " + "abcdefghijklmnopqrstuvwxyz123456"
        fake_bearer_short = "Bearer " + "abcdefghijklmnopqrstuvwxyz"
        fake_api_key = "sk-" + "test-secret-token-1234567890"
        run([
            sys.executable,
            str(SCRIPT),
            "init",
            "--project",
            "leak-check",
            "--source",
            "/home/auditor/private-project",
            "--out",
            str(review_path),
        ])

        review = json.loads(review_path.read_text(encoding="utf-8"))
        review["summary"].update(
            {
                "authorization": f"Cookie: {fake_cookie}; csrftoken=def456",
                "methodology": "Reviewed /home/auditor/private-project/app",
                "coverage_ledger": fake_bearer,
                "residual_risk": f"api_key={fake_api_key}",
                "retest_plan": "Retest /home/auditor/private-project/app/routes/admin.py:12",
            }
        )
        item = review["checks"][0]
        item.update(
            {
                "status": "Risk Found",
                "evidence": f"Found in /home/auditor/private-project/app/routes/admin.py:12; Authorization: {fake_bearer_short}",
                "finding": "secret=super-secret-value leaked in logs",
                "root_cause": f"Cookie: {fake_cookie}",
                "source_file_or_endpoint": "/home/auditor/private-project/app/routes/admin.py:12",
                "remediation": "Use repo-relative evidence and rotate token=abc123",
            }
        )
        review_path.write_text(json.dumps(review, ensure_ascii=False, indent=2), encoding="utf-8")

        run([sys.executable, str(SCRIPT), "render", "--review", str(review_path), "--out-dir", str(out_dir)])

        html_path = out_dir / "安全审查报告.html"
        markdown_path = out_dir / "安全审查报告.md"
        pdf_path = out_dir / "安全审查报告.pdf"
        json_path = out_dir / "security_review.sanitized.json"
        xlsx_path = out_dir / "安全审查评分表.xlsx"
        forbidden = [
            "/home/auditor/private-project",
            fake_cookie,
            fake_bearer_short,
            "super-secret-value",
            fake_api_key,
        ]
        assert_not_contains(html_path, forbidden)
        assert_not_contains(markdown_path, forbidden)
        assert_not_contains(json_path, forbidden)
        html_text = html_path.read_text(encoding="utf-8")
        for section in ["审查方法与覆盖", "详细风险发现", "存疑项", "残余风险与复测计划"]:
            assert section in html_text
        for presentation_token in ["#f5f4ed", "#1B365D", "report-shell", "badge-risk", "topbar", "langToggle", 'data-lang="zh"']:
            assert presentation_token in html_text
        markdown_text = markdown_path.read_text(encoding="utf-8")
        for markdown_token in ["# leak-check 安全审查报告", "## 完整评分表", "| 编号 | 优先级 | 风险域 |"]:
            assert markdown_token in markdown_text
        assert pdf_path.read_bytes().startswith(b"%PDF-")

        with zipfile.ZipFile(xlsx_path) as workbook:
            workbook.testzip()
            combined_xml = "\n".join(
                workbook.read(name).decode("utf-8", errors="ignore")
                for name in workbook.namelist()
                if name.startswith("xl/worksheets/")
            )
        for value in forbidden:
            assert value not in combined_xml, f"{value!r} leaked into XLSX worksheets"
        assert "<autoFilter " in combined_xml
        assert "showGridLines=\"0\"" in combined_xml
        assert "<cols>" in combined_xml
        assert "总体风险" in combined_xml
        assert "状态" in combined_xml


def test_refuses_to_write_artifacts_inside_target_source() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        target = tmp_path / "target-source"
        target.mkdir()
        blocked_review = target / "security_review.json"
        result = run_result([
            sys.executable,
            str(SCRIPT),
            "init",
            "--project",
            "blocked",
            "--source",
            str(target),
            "--out",
            str(blocked_review),
        ])
        assert result.returncode != 0
        assert "Refusing to write audit artifacts inside the target source directory" in result.stderr
        assert not blocked_review.exists()

        review_path = tmp_path / "review.json"
        run([
            sys.executable,
            str(SCRIPT),
            "init",
            "--project",
            "blocked-render",
            "--source",
            str(target),
            "--out",
            str(review_path),
        ])
        result = run_result([
            sys.executable,
            str(SCRIPT),
            "render",
            "--review",
            str(review_path),
            "--out-dir",
            str(target / "report"),
        ])
        assert result.returncode != 0
        assert "Refusing to write audit artifacts inside the target source directory" in result.stderr
        assert not (target / "report").exists()


def test_prepare_env_copies_local_source_to_isolated_workdir_and_records_mode() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        source = tmp_path / "source"
        source.mkdir()
        (source / "app.py").write_text("print('hello')\n", encoding="utf-8")
        (source / "node_modules").mkdir()
        (source / "node_modules" / "ignored.js").write_text("ignored\n", encoding="utf-8")
        workdir = tmp_path / "audit-work"

        result = run_result([
            sys.executable,
            str(SCRIPT),
            "prepare-env",
            "--source",
            str(source),
            "--workdir",
            str(workdir),
            "--project",
            "mode-check",
            "--mode",
            "dynamic-active",
            "--intensity",
            "destructive",
            "--allowed-tests",
            "runtime-check,blind-oob,database-write,file-mutation",
        ])
        assert result.returncode == 0, result.stderr
        manifest = json.loads((workdir / "audit-environment.json").read_text(encoding="utf-8"))
        assert manifest["skill"] == "yao-websecurity-skill"
        assert manifest["mode"] == "dynamic-active"
        assert manifest["intensity"] == "destructive"
        assert manifest["target_source"].endswith("target-source")
        assert (workdir / "target-source" / "app.py").exists()
        assert not (workdir / "target-source" / "node_modules").exists()
        assert (workdir / "target-source" / ".env.audit").exists()

        blocked = run_result([
            sys.executable,
            str(SCRIPT),
            "prepare-env",
            "--source",
            str(source),
            "--workdir",
            str(source / "audit-work"),
        ])
        assert blocked.returncode != 0
        assert "Refusing to write audit artifacts inside the target source directory" in blocked.stderr


def test_init_records_selected_runtime_mode_and_dynamic_gates() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        review_path = Path(tmp) / "review.json"
        run([
            sys.executable,
            str(SCRIPT),
            "init",
            "--project",
            "mode-ledger",
            "--source",
            "https://github.com/example/repo",
            "--mode",
            "dynamic-safe",
            "--intensity",
            "runtime",
            "--allowed-tests",
            "runtime-check,passive-dast",
            "--runtime-url",
            "http://127.0.0.1:8080",
            "--oob-endpoint",
            "https://oob.example/callback",
            "--out",
            str(review_path),
        ])
        review = json.loads(review_path.read_text(encoding="utf-8"))
        runtime = review["runtime"]
        assert runtime["audit_mode"] == "dynamic-safe"
        assert runtime["intensity"] == "runtime"
        assert runtime["allowed_dynamic_tests"] == ["runtime-check", "passive-dast"]
        assert runtime["runtime_url"] == "http://127.0.0.1:8080"
        assert runtime["oob_endpoint"] == "https://oob.example/callback"


if __name__ == "__main__":
    test_render_sanitizes_reports_and_adds_required_sections()
    test_refuses_to_write_artifacts_inside_target_source()
    test_prepare_env_copies_local_source_to_isolated_workdir_and_records_mode()
    test_init_records_selected_runtime_mode_and_dynamic_gates()
