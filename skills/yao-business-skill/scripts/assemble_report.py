#!/usr/bin/env python3
import argparse
import copy
import json
import re
from pathlib import Path

from render_report import render_html
from score_metrics import score_model
from validate_report import validate_report_payload


FIT_DIMENSIONS = [
    ("channel_fit", "渠道", "Channel"),
    ("payment_fit", "支付", "Payment"),
    ("compliance_fit", "合规", "Compliance"),
    ("trust_fit", "信任", "Trust"),
    ("service_fit", "服务", "Service"),
    ("competition_fit", "竞争", "Competition"),
]
TIER_ORDER = ["S", "A", "B", "C", "D"]
SEVERITY_SCORE = {"low": 25, "medium": 50, "high": 75, "critical": 100}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def with_default_list(payload: dict, key: str) -> None:
    if key not in payload or payload[key] is None:
        payload[key] = []


def pop_score_inputs(item: dict) -> dict | None:
    inputs = item.pop("scoring_inputs", None)
    if inputs is None:
        inputs = item.pop("confidence_inputs", None)
    return inputs


def l10n(zh: str, en: str | None = None) -> dict:
    return {"zh": zh, "en": en or zh}


def ensure_l10n(value: object, fallback: str = "") -> dict:
    if isinstance(value, dict):
        zh = value.get("zh") or value.get("en") or fallback
        en = value.get("en") or value.get("zh") or fallback
        return {"zh": str(zh), "en": str(en)}
    if value is None:
        return {"zh": fallback, "en": fallback}
    return {"zh": str(value), "en": str(value)}


def text(value: object, lang: str = "zh", fallback: str = "") -> str:
    localized = ensure_l10n(value, fallback)
    return localized[lang] or fallback


def short_number(value: float | int) -> str:
    amount = float(value)
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    if amount >= 1_000_000_000:
        return f"{sign}{amount / 1_000_000_000:.2f}B"
    if amount >= 1_000_000:
        return f"{sign}{amount / 1_000_000:.2f}M"
    if amount >= 1_000:
        return f"{sign}{amount / 1_000:.1f}K"
    if amount.is_integer():
        return f"{sign}{int(amount)}"
    return f"{sign}{amount:.1f}"


def extract_year(value: object) -> str | None:
    string = text(value, "en", "")
    match = re.search(r"(20\d{2})", string)
    return match.group(1) if match else None


def maybe_score_environment(report: dict) -> None:
    environment = report.get("market_environment")
    if not isinstance(environment, dict):
        return
    required = [key for key, _, _ in FIT_DIMENSIONS]
    if all(key in environment for key in required):
        result = score_model("environment-fit", environment)
        environment["environment_fit_score"] = result["score"]
        environment["environment_fit_band"] = result["band"]
        if not environment.get("fit_summary"):
            ordered = sorted(
                [(key, environment.get(key, 0)) for key in required],
                key=lambda item: item[1],
                reverse=True,
            )
            strongest = [name.replace("_fit", "") for name, _ in ordered[:2]]
            weakest = [name.replace("_fit", "") for name, _ in ordered[-2:]]
            environment["fit_summary"] = (
                f"Environment fit is {result['band']} at {result['score']}. "
                f"Strongest dimensions: {', '.join(strongest)}. "
                f"Weakest dimensions: {', '.join(weakest)}."
            )


def maybe_score_entity(report: dict) -> None:
    inputs = report.pop("entity_confidence_inputs", None)
    entity = report.get("entity")
    if not inputs or not isinstance(entity, dict):
        return
    result = score_model("confidence", inputs)
    entity["confidence"] = result["score"]
    entity["confidence_band"] = result["band"]


def maybe_score_models(report: dict) -> None:
    for key in ("current_business_models", "financial_estimates", "upgrade_recommendations"):
        items = report.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            inputs = pop_score_inputs(item)
            if inputs:
                result = score_model("confidence", inputs)
                item["confidence"] = result["score"]
                item["confidence_band"] = result["band"]


def maybe_score_competitors(report: dict) -> None:
    for key, model_name in (
        ("direct_competitors", "direct-competitor"),
        ("cross_industry_analogs", "cross-industry"),
    ):
        items = report.get(key)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            inputs = item.pop("scoring_inputs", None)
            if inputs:
                result = score_model(model_name, inputs)
                item["score"] = result["score"]
                item["score_band"] = result["band"]
        items.sort(key=lambda item: item.get("score", 0), reverse=True)


def maybe_score_ideas(report: dict) -> None:
    ideas = report.get("idea_options")
    if not isinstance(ideas, list):
        return
    for item in ideas:
        if not isinstance(item, dict):
            continue
        inputs = item.pop("scoring_inputs", None)
        if inputs:
            result = score_model("idea-option", inputs)
            item["priority_score"] = result["score"]
            item["priority_band"] = result["band"]
    ideas.sort(key=lambda item: item.get("priority_score", 0), reverse=True)


def ensure_core_defaults(report: dict) -> None:
    with_default_list(report, "chart_modules")
    with_default_list(report, "evidence_items")
    with_default_list(report, "risk_flags")
    with_default_list(report, "unknowns")
    with_default_list(report, "next_validation")
    report.setdefault("appendix", {})

    mode = report.get("analysis_mode")
    if mode == "idea_to_model":
        with_default_list(report, "idea_options")
        with_default_list(report, "scenario_forecast")
        with_default_list(report, "validation_plan")
    elif mode == "model_diagnosis":
        with_default_list(report, "current_business_models")
        with_default_list(report, "financial_estimates")
        with_default_list(report, "direct_competitors")
        with_default_list(report, "cross_industry_analogs")
        report.setdefault("benchmark", {})
        with_default_list(report, "upgrade_recommendations")
    elif mode == "company_case_study":
        with_default_list(report, "current_business_models")
        with_default_list(report, "profit_pools")
        with_default_list(report, "strengths")
        with_default_list(report, "weaknesses")
        with_default_list(report, "transferable_patterns")
        with_default_list(report, "environment_dependencies")


def merge_chart_modules(existing: list, derived: list) -> list:
    merged: list = []
    seen: set[str] = set()
    for item in existing + derived:
        if not isinstance(item, dict):
            continue
        chart_id = item.get("id")
        if not chart_id or chart_id in seen:
            continue
        merged.append(item)
        seen.add(chart_id)
    return merged


def build_chart_modules(report: dict) -> list[dict]:
    charts: list[dict] = []
    mode = report.get("analysis_mode")
    env = report.get("market_environment", {})
    evidence = report.get("evidence_items", [])
    models = report.get("current_business_models", [])
    financials = report.get("financial_estimates", [])
    direct = report.get("direct_competitors", [])
    analogs = report.get("cross_industry_analogs", [])
    benchmark = report.get("benchmark", {})
    recommendations = report.get("upgrade_recommendations", [])
    risks = report.get("risk_flags", [])
    ai_fit = report.get("ai_fit", {})

    env_metrics = []
    for key, zh_label, en_label in FIT_DIMENSIONS:
        value = env.get(key)
        if isinstance(value, (int, float)):
            env_metrics.append({"label": l10n(zh_label, en_label), "value": float(value)})
    if env_metrics:
        ordered = sorted(env_metrics, key=lambda item: item["value"], reverse=True)
        strongest = ordered[:2]
        weakest = ordered[-2:]
        charts.append(
            {
                "id": "environment_radar",
                "chart_type": "radar",
                "title": l10n("经营环境六维雷达图", "Operating Environment Radar"),
                "subtitle": l10n("用六个经营维度看这个模式的外部适配轮廓。", "Six operating dimensions show the shape of environment fit."),
                "insight": l10n(
                    f"最强维度是{text(strongest[0]['label'])}和{text(strongest[1]['label'])}，最弱维度是{text(weakest[0]['label'])}和{text(weakest[1]['label'])}。",
                    f"The strongest dimensions are {text(strongest[0]['label'], 'en')} and {text(strongest[1]['label'], 'en')}, while the weakest are {text(weakest[0]['label'], 'en')} and {text(weakest[1]['label'], 'en')}."
                ),
                "data": {"metrics": env_metrics, "max_value": 100},
            }
        )
        charts.append(
            {
                "id": "environment_heatmap",
                "chart_type": "heatmap",
                "title": l10n("经营环境热力图", "Environment Heatmap"),
                "subtitle": l10n("把六维适配度压缩成高低温区，优先识别短板。", "Compress the six fit scores into a quick hot-cold view."),
                "insight": l10n(
                    f"低于 80 分的维度需要优先补强；当前最需要关注的是{text(weakest[0]['label'])}。",
                    f"Anything below 80 needs active reinforcement; the first watch item is {text(weakest[0]['label'], 'en')}."
                ),
                "data": {"cells": env_metrics},
            }
        )

    if isinstance(evidence, list) and evidence:
        tier_counts = {tier: 0 for tier in TIER_ORDER}
        year_counts: dict[str, int] = {}
        for item in evidence:
            tier = item.get("source_tier")
            if tier in tier_counts:
                tier_counts[tier] += 1
            year = extract_year(item.get("source_date"))
            if year:
                year_counts[year] = year_counts.get(year, 0) + 1
        strong_count = tier_counts["S"] + tier_counts["A"]
        charts.append(
            {
                "id": "evidence_tier_distribution",
                "chart_type": "ranked_bar",
                "title": l10n("证据层级分布图", "Evidence Tier Distribution"),
                "subtitle": l10n("看结论到底依赖强证据还是弱证据。", "See whether the report stands on strong or weak evidence."),
                "insight": l10n(
                    f"当前共有 {len(evidence)} 条证据，其中强证据（S/A）占 {strong_count} 条。",
                    f"The report currently uses {len(evidence)} evidence items, with {strong_count} in the strongest S/A tiers."
                ),
                "data": {
                    "items": [
                        {"label": tier, "value": tier_counts[tier], "meta": l10n("证据数量", "Evidence count")}
                        for tier in TIER_ORDER
                    ],
                    "max_value": max(tier_counts.values()) if tier_counts else 1,
                },
            }
        )
        if year_counts:
            sorted_years = sorted(year_counts.items(), key=lambda item: item[0])
            latest_year, latest_count = sorted_years[-1]
            charts.append(
                {
                    "id": "evidence_recency_timeline",
                    "chart_type": "timeline",
                    "title": l10n("证据时间线", "Evidence Recency Timeline"),
                    "subtitle": l10n("看主要证据是否足够新，避免报告被旧信息主导。", "Check whether the report is anchored in current evidence."),
                    "insight": l10n(
                        f"最新证据主要集中在 {latest_year} 年，共 {latest_count} 条。",
                        f"The most recent evidence is concentrated in {latest_year}, with {latest_count} items."
                    ),
                    "data": {
                        "items": [
                            {"label": year, "value": count, "meta": l10n("证据条数", "Evidence count")}
                            for year, count in sorted_years
                        ],
                        "max_value": max(year_counts.values()),
                    },
                }
            )

    if mode in {"model_diagnosis", "company_case_study"} and isinstance(models, list) and models:
        ranked_models = sorted(models, key=lambda item: item.get("confidence", 0), reverse=True)
        top_model = ranked_models[0]
        charts.append(
            {
                "id": "model_confidence_ranking",
                "chart_type": "ranked_bar",
                "title": l10n("商业模式置信度排行", "Business Model Confidence Ranking"),
                "subtitle": l10n("对比各模式线的确定性，避免把潜在线当成核心盘。", "Compare certainty across monetization lines."),
                "insight": l10n(
                    f"当前最确定的模式线是{text(top_model.get('model_label'))}，可信度 {top_model.get('confidence', 0)}。",
                    f"The highest-confidence model line is {text(top_model.get('model_label'), 'en')}, at {top_model.get('confidence', 0)}."
                ),
                "data": {
                    "items": [
                        {
                            "label": ensure_l10n(item.get("model_label")),
                            "value": item.get("confidence", 0),
                            "meta": ensure_l10n(item.get("status")),
                        }
                        for item in ranked_models[:8]
                    ],
                    "max_value": 100,
                },
            }
        )

    if isinstance(financials, list) and financials:
        ranged_items = []
        mix_items = []
        for item in financials:
            range_data = item.get("range") or {}
            if not isinstance(range_data, dict):
                continue
            low = range_data.get("low")
            base = range_data.get("base")
            high = range_data.get("high")
            currency = text(range_data.get("currency"), "en", "")
            if all(isinstance(value, (int, float)) for value in (low, base, high)):
                ranged_items.append(
                    {
                        "label": ensure_l10n(item.get("label")),
                        "low": low,
                        "base": base,
                        "high": high,
                        "unit": currency,
                    }
                )
                if base > 0:
                    mix_items.append({"label": ensure_l10n(item.get("label")), "value": base, "unit": currency})
        if ranged_items:
            largest_line = max(ranged_items, key=lambda item: item["base"])
            charts.append(
                {
                    "id": "financial_range_comparison",
                    "chart_type": "range_bar",
                    "title": l10n("财务区间对比图", "Financial Range Comparison"),
                    "subtitle": l10n("所有关键收入线都以 low / base / high 区间展示。", "Every key financial line is shown as low / base / high instead of fake precision."),
                    "insight": l10n(
                        f"基准情景下最大的收入线是{text(largest_line['label'])}，约 {short_number(largest_line['base'])} {largest_line['unit']}。",
                        f"In the base case, the largest revenue line is {text(largest_line['label'], 'en')} at about {short_number(largest_line['base'])} {largest_line['unit']}."
                    ),
                    "data": {"items": ranged_items[:8]},
                }
            )
        if mix_items:
            total_base = sum(item["value"] for item in mix_items)
            primary = max(mix_items, key=lambda item: item["value"])
            share = (primary["value"] / total_base * 100) if total_base else 0
            charts.append(
                {
                    "id": "financial_mix_share",
                    "chart_type": "stacked_bar",
                    "title": l10n("收入结构堆叠图", "Revenue Mix Share"),
                    "subtitle": l10n("看主要收入盘和第二曲线的结构。", "See the main revenue engine and the secondary curves."),
                    "insight": l10n(
                        f"当前收入结构高度集中在{text(primary['label'])}，约占基准情景的 {share:.1f}%。",
                        f"The revenue mix is concentrated in {text(primary['label'], 'en')}, which represents about {share:.1f}% of the base case."
                    ),
                    "data": {"items": mix_items[:8], "total": total_base},
                }
            )

    if isinstance(direct, list) and direct:
        top_direct = sorted(direct, key=lambda item: item.get("score", 0), reverse=True)
        leader = top_direct[0]
        charts.append(
            {
                "id": "direct_competitor_ranking",
                "chart_type": "ranked_bar",
                "title": l10n("直接竞品得分排行", "Direct Competitor Ranking"),
                "subtitle": l10n("最值得持续监控的正面对手。", "The direct threats that deserve the closest watch."),
                "insight": l10n(
                    f"当前最强的正面对手是{text(leader.get('name'))}，竞争相似度 {leader.get('score', 0)}。",
                    f"The strongest direct threat is {text(leader.get('name'), 'en')} with a similarity score of {leader.get('score', 0)}."
                ),
                "data": {
                    "items": [
                        {
                            "label": ensure_l10n(item.get("name")),
                            "value": item.get("score", 0),
                            "meta": ensure_l10n(item.get("category")),
                        }
                        for item in top_direct[:10]
                    ],
                    "max_value": 100,
                },
            }
        )

    if isinstance(analogs, list) and analogs:
        top_analogs = sorted(analogs, key=lambda item: item.get("score", 0), reverse=True)
        leader = top_analogs[0]
        charts.append(
            {
                "id": "cross_industry_analog_ranking",
                "chart_type": "ranked_bar",
                "title": l10n("跨行业类比分排行", "Cross-Industry Analog Ranking"),
                "subtitle": l10n("看哪些模式值得迁移，而不是只盯同类产品。", "Show which models are most transferable from other categories."),
                "insight": l10n(
                    f"当前最强的跨行业类比是{text(leader.get('name'))}，说明其平台扩展逻辑最值得借鉴。",
                    f"The strongest cross-industry analog is {text(leader.get('name'), 'en')}, suggesting its expansion logic is highly transferable."
                ),
                "data": {
                    "items": [
                        {
                            "label": ensure_l10n(item.get("name")),
                            "value": item.get("score", 0),
                            "meta": ensure_l10n(item.get("category")),
                        }
                        for item in top_analogs[:10]
                    ],
                    "max_value": 100,
                },
            }
        )

    scorecard = benchmark.get("scorecard", []) if isinstance(benchmark, dict) else []
    if isinstance(scorecard, list) and scorecard:
        gap_items = []
        for item in scorecard:
            current = item.get("target")
            peer = item.get("peer_median")
            if isinstance(current, (int, float)) and isinstance(peer, (int, float)):
                gap_items.append(
                    {
                        "label": ensure_l10n(item.get("dimension")),
                        "current": current,
                        "peer": peer,
                        "delta": current - peer,
                        "meta": ensure_l10n(item.get("gap_note")),
                    }
                )
        if gap_items:
            best = max(gap_items, key=lambda item: item["delta"])
            worst = min(gap_items, key=lambda item: item["delta"])
            charts.append(
                {
                    "id": "benchmark_gap",
                    "chart_type": "gap_bar",
                    "title": l10n("Benchmark 差距图", "Benchmark Gap Chart"),
                    "subtitle": l10n("把关键维度放到同行中位数旁边看。", "Place key dimensions next to the peer median."),
                    "insight": l10n(
                        f"相对同行最强的领先项是{text(best['label'])}，最弱的短板是{text(worst['label'])}。",
                        f"The best lead over peers is {text(best['label'], 'en')}, while the clearest gap is {text(worst['label'], 'en')}."
                    ),
                    "data": {"items": gap_items[:8], "max_value": 100},
                }
            )

    if isinstance(recommendations, list) and recommendations:
        quadrant_items = []
        for item in recommendations:
            impact = item.get("impact")
            effort = item.get("effort")
            risk = item.get("risk", 0)
            if isinstance(impact, (int, float)) and isinstance(effort, (int, float)):
                quadrant_items.append(
                    {
                        "label": ensure_l10n(item.get("title")),
                        "x": effort,
                        "y": impact,
                        "tone": "high_risk" if risk >= 70 else "balanced",
                        "risk": risk,
                    }
                )
        if quadrant_items:
            quick_wins = [item for item in quadrant_items if item["x"] <= 45 and item["y"] >= 70]
            charts.append(
                {
                    "id": "upgrade_impact_effort",
                    "chart_type": "quadrant",
                    "title": l10n("升级建议影响-投入矩阵", "Upgrade Impact-Effort Matrix"),
                    "subtitle": l10n("先做高影响、低投入，再决定哪些建议值得重投入。", "Prioritize high-impact, low-effort upgrades first."),
                    "insight": l10n(
                        f"当前可优先推进的 quick wins 有 {len(quick_wins)} 项。",
                        f"There are {len(quick_wins)} clear quick wins in the current recommendation set."
                    ),
                    "data": {
                        "items": quadrant_items[:8],
                        "x_label": l10n("投入", "Effort"),
                        "y_label": l10n("影响", "Impact"),
                    },
                }
            )

    if isinstance(risks, list) and risks:
        risk_items = []
        highest = None
        for item in risks:
            severity = item.get("severity")
            if severity not in SEVERITY_SCORE:
                continue
            risk_item = {
                "label": ensure_l10n(item.get("type")),
                "value": SEVERITY_SCORE[severity],
                "meta": l10n(severity, severity),
            }
            risk_items.append(risk_item)
            if highest is None or risk_item["value"] > highest["value"]:
                highest = risk_item
        if risk_items and highest:
            charts.append(
                {
                    "id": "risk_severity_map",
                    "chart_type": "heatmap",
                    "title": l10n("风险热力图", "Risk Severity Map"),
                    "subtitle": l10n("把风险强度和风险类型一起摆出来。", "Keep downside visible by mapping risk type and severity."),
                    "insight": l10n(
                        f"当前最高风险项是{text(highest['label'])}。",
                        f"The highest-severity current risk is {text(highest['label'], 'en')}."
                    ),
                    "data": {"cells": risk_items},
                }
            )

    if isinstance(ai_fit, dict) and (ai_fit.get("leverage_points") or ai_fit.get("disruption_risks")):
        leverage_points = ai_fit.get("leverage_points", [])
        disruption_risks = ai_fit.get("disruption_risks", [])
        charts.append(
            {
                "id": "ai_leverage_balance",
                "chart_type": "balance",
                "title": l10n("AI 杠杆与冲击平衡图", "AI Leverage Balance"),
                "subtitle": l10n("同时看 AI 带来的增长点和它带来的新压力。", "Hold AI upside and AI pressure in the same frame."),
                "insight": l10n(
                    f"当前识别出 {len(leverage_points)} 个 AI 杠杆点，和 {len(disruption_risks)} 个 AI 冲击风险。",
                    f"The report identifies {len(leverage_points)} AI leverage points and {len(disruption_risks)} disruption risks."
                ),
                "data": {
                    "positive": [ensure_l10n(item) for item in leverage_points[:6]],
                    "negative": [ensure_l10n(item) for item in disruption_risks[:6]],
                },
            }
        )

    return charts


def assemble_report(input_payload: dict) -> dict:
    report = copy.deepcopy(input_payload)
    ensure_core_defaults(report)
    maybe_score_entity(report)
    maybe_score_environment(report)
    maybe_score_models(report)
    maybe_score_competitors(report)
    maybe_score_ideas(report)
    report["chart_modules"] = merge_chart_modules(report.get("chart_modules", []), build_chart_modules(report))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Assemble a Yao Business Skill report from structured input.")
    parser.add_argument("input_json", help="Structured input JSON path")
    parser.add_argument(
        "--output-json",
        default=None,
        help="Optional output JSON path. Defaults to <input>.report.json",
    )
    parser.add_argument(
        "--render-html",
        action="store_true",
        help="Render HTML after assembling the JSON report.",
    )
    parser.add_argument(
        "--output-html",
        default=None,
        help="Optional output HTML path. Defaults to the output JSON path with .html suffix.",
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Optional HTML template path. Defaults to templates/report-skeleton.html.",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip built-in report validation before finishing.",
    )
    args = parser.parse_args()

    input_path = Path(args.input_json).resolve()
    output_json = Path(args.output_json).resolve() if args.output_json else input_path.with_suffix(".report.json")
    template_path = Path(args.template).resolve() if args.template else Path(__file__).resolve().parent.parent / "templates" / "report-skeleton.html"
    output_html = Path(args.output_html).resolve() if args.output_html else output_json.with_suffix(".html")

    assembled = assemble_report(load_json(input_path))
    write_json(output_json, assembled)

    validation = validate_report_payload(assembled)
    if not args.skip_validate and validation["failures"]:
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        raise SystemExit(2)

    result = {
        "ok": True,
        "output_json": str(output_json),
    }
    if validation["warnings"]:
        result["warnings"] = validation["warnings"]

    if args.render_html:
        render_html(template_path, output_json, output_html)
        result["output_html"] = str(output_html)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
