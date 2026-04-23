#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


ANALYSIS_MODES = {"idea_to_model", "model_diagnosis", "company_case_study"}
DELIVERY_DIRECTIONS = {
    "china_to_china",
    "china_to_overseas",
    "overseas_to_china",
    "overseas_to_overseas",
    "custom",
}
EVIDENCE_TIERS = {"S", "A", "B", "C", "D"}
RISK_SEVERITIES = {"low", "medium", "high", "critical"}
AI_ROLES = {"cost_reducer", "differentiator", "billable_unit", "mixed"}
MODEL_STATUSES = {"confirmed", "estimated", "latent", "hypothesis"}
COMPETITOR_TYPES = {"direct", "adjacent", "cross_industry"}


def add_failure(failures: list[str], path: str, message: str) -> None:
    failures.append(f"{path}: {message}")


def require_key(obj: dict, key: str, path: str, failures: list[str]) -> None:
    if key not in obj:
        add_failure(failures, path, f"missing required key `{key}`")


def expect_type(value: object, expected: type, path: str, failures: list[str]) -> bool:
    if not isinstance(value, expected):
        add_failure(failures, path, f"expected {expected.__name__}")
        return False
    return True


def validate_entity(entity: dict, failures: list[str]) -> None:
    require_key(entity, "input", "entity", failures)


def validate_market_environment(environment: dict, failures: list[str]) -> None:
    for key in ("company_origin", "target_market", "delivery_direction"):
        require_key(environment, key, "market_environment", failures)
    direction = environment.get("delivery_direction")
    if direction and direction not in DELIVERY_DIRECTIONS:
        add_failure(failures, "market_environment.delivery_direction", f"invalid direction `{direction}`")


def validate_evidence_items(items: list, failures: list[str]) -> None:
    for index, item in enumerate(items):
        path = f"evidence_items[{index}]"
        if not expect_type(item, dict, path, failures):
            continue
        for key in ("claim", "source_url", "source_tier"):
            require_key(item, key, path, failures)
        tier = item.get("source_tier")
        if tier and tier not in EVIDENCE_TIERS:
            add_failure(failures, f"{path}.source_tier", f"invalid tier `{tier}`")


def validate_current_models(items: list, failures: list[str]) -> None:
    for index, item in enumerate(items):
        path = f"current_business_models[{index}]"
        if not expect_type(item, dict, path, failures):
            continue
        for key in ("model_label", "status", "confidence"):
            require_key(item, key, path, failures)
        status = item.get("status")
        if status and status not in MODEL_STATUSES:
            add_failure(failures, f"{path}.status", f"invalid status `{status}`")


def validate_financial_estimates(items: list, failures: list[str]) -> None:
    for index, item in enumerate(items):
        path = f"financial_estimates[{index}]"
        if not expect_type(item, dict, path, failures):
            continue
        for key in ("label", "formula", "range", "confidence"):
            require_key(item, key, path, failures)


def validate_competitors(items: list, key: str, failures: list[str]) -> None:
    for index, item in enumerate(items):
        path = f"{key}[{index}]"
        if not expect_type(item, dict, path, failures):
            continue
        for required_key in ("type", "name", "score"):
            require_key(item, required_key, path, failures)
        comp_type = item.get("type")
        if comp_type and comp_type not in COMPETITOR_TYPES:
            add_failure(failures, f"{path}.type", f"invalid competitor type `{comp_type}`")


def validate_idea_options(items: list, failures: list[str]) -> None:
    for index, item in enumerate(items):
        path = f"idea_options[{index}]"
        if not expect_type(item, dict, path, failures):
            continue
        for key in ("title", "model_combo", "payer", "pricing_unit", "formula", "priority_score"):
            require_key(item, key, path, failures)


def validate_risks(items: list, failures: list[str]) -> None:
    for index, item in enumerate(items):
        path = f"risk_flags[{index}]"
        if not expect_type(item, dict, path, failures):
            continue
        for key in ("type", "severity"):
            require_key(item, key, path, failures)
        severity = item.get("severity")
        if severity and severity not in RISK_SEVERITIES:
            add_failure(failures, f"{path}.severity", f"invalid severity `{severity}`")


def validate_actions(items: list, key: str, failures: list[str]) -> None:
    for index, item in enumerate(items):
        path = f"{key}[{index}]"
        if not expect_type(item, dict, path, failures):
            continue
        require_key(item, "title", path, failures)


def validate_ai_fit(ai_fit: dict, failures: list[str]) -> None:
    for key in ("role", "summary"):
        require_key(ai_fit, key, "ai_fit", failures)
    role = ai_fit.get("role")
    if role and role not in AI_ROLES:
        add_failure(failures, "ai_fit.role", f"invalid ai role `{role}`")


def validate_chart_modules(items: list, failures: list[str], warnings: list[str], mode: str | None) -> None:
    for index, item in enumerate(items):
        path = f"chart_modules[{index}]"
        if not expect_type(item, dict, path, failures):
            continue
        for key in ("id", "chart_type", "title", "insight", "data"):
            require_key(item, key, path, failures)
    if mode in {"model_diagnosis", "company_case_study"} and len(items) < 10:
        add_failure(failures, "chart_modules", f"expected at least 10 chart modules for mode `{mode}`")
    elif mode == "idea_to_model" and len(items) < 6:
        warnings.append("chart_modules: fewer than 6 chart modules were generated for idea analysis")


def validate_mode_specific(report: dict, failures: list[str]) -> None:
    mode = report.get("analysis_mode")
    if mode == "idea_to_model":
        for key in ("idea_options", "scenario_forecast", "validation_plan"):
            require_key(report, key, "report", failures)
        validate_idea_options(report.get("idea_options", []), failures)
        validate_actions(report.get("validation_plan", []), "validation_plan", failures)
    elif mode == "model_diagnosis":
        for key in ("current_business_models", "financial_estimates", "direct_competitors", "cross_industry_analogs", "benchmark", "upgrade_recommendations"):
            require_key(report, key, "report", failures)
        validate_current_models(report.get("current_business_models", []), failures)
        validate_financial_estimates(report.get("financial_estimates", []), failures)
        validate_competitors(report.get("direct_competitors", []), "direct_competitors", failures)
        validate_competitors(report.get("cross_industry_analogs", []), "cross_industry_analogs", failures)
    elif mode == "company_case_study":
        for key in ("current_business_models", "profit_pools", "strengths", "weaknesses", "transferable_patterns", "environment_dependencies"):
            require_key(report, key, "report", failures)
        validate_current_models(report.get("current_business_models", []), failures)


def validate_report_payload(report: dict) -> dict:
    failures: list[str] = []
    warnings: list[str] = []

    for key in ("analysis_mode", "entity", "market_environment", "chart_modules", "evidence_items", "risk_flags", "unknowns", "next_validation", "ai_fit"):
        require_key(report, key, "report", failures)

    mode = report.get("analysis_mode")
    if mode not in ANALYSIS_MODES:
        add_failure(failures, "analysis_mode", f"invalid mode `{mode}`")

    entity = report.get("entity")
    if isinstance(entity, dict):
        validate_entity(entity, failures)
    else:
        add_failure(failures, "entity", "expected object")

    environment = report.get("market_environment")
    if isinstance(environment, dict):
        validate_market_environment(environment, failures)
    else:
        add_failure(failures, "market_environment", "expected object")

    chart_modules = report.get("chart_modules")
    if isinstance(chart_modules, list):
        validate_chart_modules(chart_modules, failures, warnings, mode)
    else:
        add_failure(failures, "chart_modules", "expected array")

    evidence_items = report.get("evidence_items")
    if isinstance(evidence_items, list):
        validate_evidence_items(evidence_items, failures)
    else:
        add_failure(failures, "evidence_items", "expected array")

    risk_flags = report.get("risk_flags")
    if isinstance(risk_flags, list):
        validate_risks(risk_flags, failures)
    else:
        add_failure(failures, "risk_flags", "expected array")

    next_validation = report.get("next_validation")
    if isinstance(next_validation, list):
        validate_actions(next_validation, "next_validation", failures)
    else:
        add_failure(failures, "next_validation", "expected array")

    ai_fit = report.get("ai_fit")
    if isinstance(ai_fit, dict):
        validate_ai_fit(ai_fit, failures)
    else:
        add_failure(failures, "ai_fit", "expected object")

    validate_mode_specific(report, failures)

    return {
        "ok": not failures,
        "failures": failures,
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Yao Business Skill report payload.")
    parser.add_argument("report_json", help="Path to the report JSON file")
    args = parser.parse_args()

    report_path = Path(args.report_json).resolve()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    result = validate_report_payload(report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["failures"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
