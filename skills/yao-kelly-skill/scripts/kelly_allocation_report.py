#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

READINESS_THRESHOLD = 0.78
EPSILON = 1e-9


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def first_present(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def load_brief(path: str) -> dict[str, Any]:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(payload: dict[str, Any], path: str | None) -> None:
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if path:
        Path(path).write_text(text + "\n", encoding="utf-8")
        return
    print(text)


def collect_opportunities(brief: dict[str, Any]) -> list[dict[str, Any]]:
    if isinstance(brief.get("opportunities"), list):
        return list(brief["opportunities"])
    if isinstance(brief.get("opportunity"), dict):
        return [brief["opportunity"]]
    return []


def infer_case_type(brief: dict[str, Any], opportunities: list[dict[str, Any]]) -> str:
    explicit = brief.get("case_type")
    if explicit:
        return str(explicit)
    if len(opportunities) > 1:
        return "multi-opportunity-allocation"
    first = opportunities[0]
    if first.get("scenario_returns"):
        return "scenario-sizing"
    if first.get("win_probability") is not None and first.get("odds") is not None:
        return "binary-bet"
    return "scenario-sizing"


def parse_odds(opportunity: dict[str, Any]) -> float:
    odds = opportunity.get("odds")
    if odds is None:
        raise ValueError("Missing odds for binary opportunity.")
    if isinstance(odds, (int, float)):
        return float(odds)
    if not isinstance(odds, dict):
        raise ValueError("odds must be a number or an object with format and value.")
    fmt = str(odds.get("format", "net")).lower()
    value = float(odds["value"])
    if fmt == "net":
        return value
    if fmt == "decimal":
        return value - 1.0
    raise ValueError(f"Unsupported odds format: {fmt}")


def normalize_scenarios(
    scenarios: list[dict[str, Any]], notes: list[str]
) -> list[dict[str, Any]]:
    total_probability = sum(float(item["probability"]) for item in scenarios)
    if total_probability <= 0:
        raise ValueError("Scenario probabilities must sum to a positive value.")
    if abs(total_probability - 1.0) > 0.03:
        raise ValueError(
            f"Scenario probabilities must sum close to 1.0, got {total_probability:.4f}."
        )
    if abs(total_probability - 1.0) > 1e-6:
        notes.append(
            f"Scenario probabilities were normalized from {total_probability:.4f} to 1.0000."
        )
    normalized: list[dict[str, Any]] = []
    for item in scenarios:
        normalized.append(
            {
                "name": item.get("name", "scenario"),
                "probability": float(item["probability"]) / total_probability,
                "return_multiple": float(item["return_multiple"]),
                "source": item.get("source", "estimated"),
            }
        )
    return normalized


def build_scenarios(
    opportunity: dict[str, Any], notes: list[str]
) -> tuple[list[dict[str, Any]], str, float | None]:
    if opportunity.get("scenario_returns"):
        raw_scenarios = list(opportunity["scenario_returns"])
        fees_fraction = float(opportunity.get("fees_fraction", 0.0))
        adjusted = []
        for item in raw_scenarios:
            adjusted.append(
                {
                    "name": item.get("name", "scenario"),
                    "probability": item["probability"],
                    "return_multiple": float(item["return_multiple"]) - fees_fraction,
                    "source": item.get("source", "estimated"),
                }
            )
        if fees_fraction:
            notes.append(
                f"Subtracted fees_fraction={fees_fraction:.4f} from all scenario returns."
            )
        return normalize_scenarios(adjusted, notes), "scenario-log-growth-grid-search", None

    if opportunity.get("win_probability") is None or opportunity.get("odds") is None:
        raise ValueError(
            "Each opportunity needs either scenario_returns or win_probability plus odds."
        )

    win_probability = float(opportunity["win_probability"])
    if not 0 <= win_probability <= 1:
        raise ValueError("win_probability must be between 0 and 1.")
    net_odds = parse_odds(opportunity)
    loss_fraction = float(opportunity.get("loss_fraction", 1.0))
    fees_fraction = float(opportunity.get("fees_fraction", 0.0))
    scenarios = [
        {
            "name": "win",
            "probability": win_probability,
            "return_multiple": net_odds - fees_fraction,
            "source": opportunity.get("win_probability_source", "estimated"),
        },
        {
            "name": "lose",
            "probability": 1.0 - win_probability,
            "return_multiple": -loss_fraction - fees_fraction,
            "source": opportunity.get("loss_source", "estimated"),
        },
    ]
    if fees_fraction:
        notes.append(f"Applied fees_fraction={fees_fraction:.4f} to win and loss outcomes.")
    return scenarios, "binary-kelly-closed-form", net_odds


def max_fraction_bound(
    scenarios: list[dict[str, Any]],
    requested_cap: float,
    allow_leverage: bool,
) -> float:
    cap = requested_cap if requested_cap > 0 else (2.0 if allow_leverage else 1.0)
    if not allow_leverage:
        cap = min(cap, 1.0)
    for item in scenarios:
        outcome = float(item["return_multiple"])
        if outcome < 0:
            cap = min(cap, (-1.0 / outcome) * 0.999999)
    return max(0.0, cap)


def expected_log_growth(scenarios: list[dict[str, Any]], fraction: float) -> float:
    total = 0.0
    for item in scenarios:
        wealth_multiple = 1.0 + fraction * float(item["return_multiple"])
        if wealth_multiple <= 0:
            return float("-inf")
        total += float(item["probability"]) * math.log(wealth_multiple)
    return total


def expected_return(scenarios: list[dict[str, Any]]) -> float:
    return sum(
        float(item["probability"]) * float(item["return_multiple"]) for item in scenarios
    )


def binary_closed_form_fraction(
    win_probability: float, net_odds: float, loss_fraction: float
) -> float | None:
    if abs(loss_fraction - 1.0) > EPSILON or net_odds <= 0:
        return None
    loss_probability = 1.0 - win_probability
    return (net_odds * win_probability - loss_probability) / net_odds


def grid_search_fraction(
    scenarios: list[dict[str, Any]], cap: float
) -> tuple[float, float]:
    if cap <= 0:
        return 0.0, 0.0
    steps = max(400, min(6000, int(cap * 5000) + 600))
    best_fraction = 0.0
    best_growth = 0.0
    for index in range(steps + 1):
        fraction = cap * index / steps
        growth = expected_log_growth(scenarios, fraction)
        if growth > best_growth:
            best_growth = growth
            best_fraction = fraction
    return round(best_fraction, 6), round(best_growth, 6)


def fractional_multiplier(
    opportunity: dict[str, Any], constraints: dict[str, Any], notes: list[str]
) -> float:
    explicit = first_present(
        opportunity.get("fractional_kelly"),
        constraints.get("fractional_kelly_mode"),
    )
    if isinstance(explicit, (int, float)):
        value = clamp(float(explicit), 0.0, 1.0)
        notes.append(f"Used explicit fractional Kelly multiplier {value:.2f}.")
        return value

    aliases = {
        "full": 1.0,
        "half": 0.5,
        "quarter": 0.25,
        "tenth": 0.10,
    }
    if isinstance(explicit, str) and explicit.lower() in aliases:
        value = aliases[explicit.lower()]
        notes.append(f"Used named fractional Kelly mode {explicit.lower()} => {value:.2f}.")
        return value

    confidence_level = str(
        first_present(opportunity.get("confidence_level"), constraints.get("confidence_level"), "low")
    ).lower()
    auto_map = {
        "high": 0.50,
        "medium": 0.25,
        "low": 0.10,
        "very_low": 0.05,
        "unknown": 0.10,
    }
    value = auto_map.get(confidence_level, 0.10)
    notes.append(
        f"Used auto fractional Kelly multiplier {value:.2f} from confidence_level={confidence_level}."
    )
    return value


def dependence_multiplier(
    opportunity: dict[str, Any], opportunity_count: int, notes: list[str]
) -> float:
    if opportunity_count <= 1:
        return 1.0
    dependence = str(opportunity.get("dependence", "unknown")).lower()
    mapping = {
        "independent": 1.00,
        "low": 0.85,
        "medium": 0.65,
        "high": 0.50,
        "unknown": 0.50,
        "exclusive": 0.50,
    }
    value = mapping.get(dependence, 0.50)
    notes.append(f"Applied dependence multiplier {value:.2f} for dependence={dependence}.")
    return value


def action_class(fraction: float) -> str:
    if fraction <= 0:
        return "skip"
    if fraction < 0.02:
        return "observe-or-tiny-test"
    if fraction < 0.10:
        return "small"
    if fraction < 0.25:
        return "medium"
    return "large"


def derive_total_exposure_cap(
    constraints: dict[str, Any], notes: list[str]
) -> tuple[float, float]:
    min_cash_reserve_ratio = constraints.get("min_cash_reserve_ratio")
    if min_cash_reserve_ratio is None:
        min_cash_reserve_ratio = 0.50
        notes.append("Assumed min_cash_reserve_ratio=0.50.")
    min_cash_reserve_ratio = clamp(float(min_cash_reserve_ratio), 0.0, 1.0)

    explicit_total_cap = constraints.get("total_exposure_cap")
    if explicit_total_cap is None:
        explicit_total_cap = 0.25
        notes.append("Assumed total_exposure_cap=0.25.")
    explicit_total_cap = clamp(float(explicit_total_cap), 0.0, 1.0)

    cap_from_reserve = clamp(1.0 - min_cash_reserve_ratio, 0.0, 1.0)
    return min(explicit_total_cap, cap_from_reserve), min_cash_reserve_ratio


def assess_readiness(
    brief: dict[str, Any],
    opportunities: list[dict[str, Any]],
    case_type: str,
    constraints: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        (
            "objective",
            bool(brief.get("objective")),
            0.12,
            "这次你更想要长期增长、控制回撤，还是固定预算内的最优试探？",
        ),
        (
            "capital_base",
            isinstance(brief.get("capital_base"), (int, float))
            and float(brief["capital_base"]) > 0,
            0.14,
            "这次真正允许参与的资金或资源总盘子是多少？有没有必须保留、完全不能动的部分？",
        ),
        (
            "payoff_model",
            all(item.get("has_model") for item in opportunities),
            0.22,
            "请给我每个机会的赔率，或者最好 / 基准 / 最差几种结果、各自概率、以及每投入 1 单位后的净收益或净亏损。",
        ),
        (
            "probabilities",
            all(item.get("probability_complete") for item in opportunities),
            0.18,
            "你认可的胜率或各场景概率是多少？如果不确定，可以给 best / base / bear 三档。",
        ),
        (
            "constraints",
            any(
                key in constraints
                for key in (
                    "total_exposure_cap",
                    "min_cash_reserve_ratio",
                    "max_fraction_cap",
                    "max_drawdown_tolerance",
                )
            ),
            0.12,
            "单次上限、总暴露上限、最大可接受亏损、最少保留现金分别是多少？",
        ),
        (
            "confidence",
            all(item.get("confidence_explicit") for item in opportunities),
            0.10,
            "你对这些概率和收益估计的把握高 / 中 / 低？",
        ),
        (
            "dependence",
            len(opportunities) <= 1 or all(item.get("dependence_explicit") for item in opportunities),
            0.07,
            "这些机会之间是独立、相关、互斥，还是你现在也不确定？",
        ),
        (
            "friction",
            any(
                item.get("friction_explicit") for item in opportunities
            )
            or any(key in constraints for key in ("fees_fraction", "min_ticket_size", "lockup_days")),
            0.05,
            "有没有手续费、滑点、锁定期、最小下注额或流动性限制？",
        ),
    ]

    score = 0.0
    missing: list[dict[str, Any]] = []
    for key, passed, weight, question in checks:
        if passed:
            score += weight
            continue
        missing.append({"key": key, "weight": weight, "question": question})

    missing.sort(key=lambda item: item["weight"], reverse=True)
    stop_reasons: list[str] = []
    if score >= READINESS_THRESHOLD:
        stop_reasons.append("decision_readiness reached the default threshold")

    non_zero_actions = [item for item in opportunities if item.get("action_class") not in ("skip", None)]
    if opportunities and not non_zero_actions and score >= 0.45:
        stop_reasons.append(
            "all modeled opportunities already map to skip, so more questions are unlikely to change the action class"
        )

    if not missing:
        stop_reasons.append("no high-impact information gaps remain")

    return {
        "case_type": case_type,
        "score": round(score, 3),
        "threshold": READINESS_THRESHOLD,
        "band": (
            "insufficient"
            if score < 0.45
            else "provisional"
            if score < READINESS_THRESHOLD
            else "ready"
        ),
        "stop_asking": bool(stop_reasons),
        "stop_reasons": stop_reasons,
        "missing_questions": missing[:3],
    }


def build_opportunity_result(
    opportunity: dict[str, Any],
    opportunity_index: int,
    opportunity_count: int,
    constraints: dict[str, Any],
) -> dict[str, Any]:
    notes: list[str] = []
    scenarios, formula_path, binary_net_odds = build_scenarios(opportunity, notes)
    requested_cap = float(
        first_present(
            opportunity.get("max_fraction_cap"),
            constraints.get("max_fraction_cap"),
            1.0,
        )
    )
    allow_leverage = bool(
        first_present(opportunity.get("allow_leverage"), constraints.get("allow_leverage"), False)
    )
    cap = max_fraction_bound(scenarios, requested_cap, allow_leverage)
    full_kelly_fraction, best_log_growth = grid_search_fraction(scenarios, cap)
    full_edge = expected_return(scenarios)

    confidence_explicit = opportunity.get("confidence_level") is not None
    dependence_explicit = opportunity.get("dependence") is not None
    friction_explicit = opportunity.get("fees_fraction") is not None
    probability_complete = True
    has_model = True

    if binary_net_odds is not None:
        closed_form = binary_closed_form_fraction(
            float(opportunity["win_probability"]),
            binary_net_odds,
            float(opportunity.get("loss_fraction", 1.0)),
        )
        if closed_form is not None:
            full_kelly_fraction = round(clamp(closed_form, 0.0, cap), 6)
    else:
        closed_form = None

    fraction_multiplier = fractional_multiplier(opportunity, constraints, notes)
    dependence_penalty = dependence_multiplier(opportunity, opportunity_count, notes)
    preliminary_fraction = round(
        clamp(full_kelly_fraction * fraction_multiplier * dependence_penalty, 0.0, cap), 6
    )

    return {
        "name": opportunity.get("name", f"opportunity-{opportunity_index}"),
        "formula_path": formula_path,
        "expected_return_per_unit": round(full_edge, 6),
        "full_kelly_fraction": round(full_kelly_fraction, 6),
        "closed_form_fraction": round(closed_form, 6) if closed_form is not None else None,
        "fractional_multiplier": round(fraction_multiplier, 6),
        "dependence_multiplier": round(dependence_penalty, 6),
        "preliminary_fraction": preliminary_fraction,
        "max_fraction_bound": round(cap, 6),
        "best_expected_log_growth": round(best_log_growth, 6),
        "confidence_level": str(
            first_present(opportunity.get("confidence_level"), constraints.get("confidence_level"), "low")
        ).lower(),
        "dependence": str(opportunity.get("dependence", "unknown")).lower(),
        "action_class": action_class(preliminary_fraction),
        "scenarios": scenarios,
        "notes": notes,
        "has_model": has_model,
        "probability_complete": probability_complete,
        "confidence_explicit": confidence_explicit,
        "dependence_explicit": dependence_explicit or opportunity_count <= 1,
        "friction_explicit": friction_explicit,
    }


def build_report(brief: dict[str, Any]) -> dict[str, Any]:
    opportunities = collect_opportunities(brief)
    if not opportunities:
        raise ValueError("The brief must include opportunity or opportunities.")

    case_type = infer_case_type(brief, opportunities)
    constraints = dict(brief.get("constraints", {}))
    report_notes: list[str] = []
    total_exposure_cap, min_cash_reserve_ratio = derive_total_exposure_cap(constraints, report_notes)
    capital_base = brief.get("capital_base")
    if capital_base is not None:
        capital_base = float(capital_base)

    results = [
        build_opportunity_result(opportunity, index + 1, len(opportunities), constraints)
        for index, opportunity in enumerate(opportunities)
    ]

    preliminary_total = sum(item["preliminary_fraction"] for item in results)
    scaling_factor = 1.0
    if preliminary_total > total_exposure_cap > 0:
        scaling_factor = total_exposure_cap / preliminary_total
        report_notes.append(
            f"Scaled preliminary recommendations by {scaling_factor:.4f} to respect total_exposure_cap={total_exposure_cap:.4f}."
        )

    for item in results:
        recommended_fraction = round(item["preliminary_fraction"] * scaling_factor, 6)
        item["recommended_fraction"] = recommended_fraction
        item["recommended_amount"] = (
            round(capital_base * recommended_fraction, 2) if capital_base is not None else None
        )
        item["action_class"] = action_class(recommended_fraction)

    readiness = assess_readiness(brief, results, case_type, constraints)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_type": case_type,
        "objective": brief.get("objective"),
        "capital_base": capital_base,
        "summary": {
            "decision_readiness": readiness,
            "total_exposure_cap": round(total_exposure_cap, 6),
            "min_cash_reserve_ratio": round(min_cash_reserve_ratio, 6),
            "preliminary_total_fraction": round(preliminary_total, 6),
            "recommended_total_fraction": round(
                sum(item["recommended_fraction"] for item in results), 6
            ),
            "recommended_total_amount": (
                round(
                    sum(item["recommended_amount"] or 0.0 for item in results),
                    2,
                )
                if capital_base is not None
                else None
            ),
        },
        "opportunities": results,
        "notes": report_notes,
        "round_log": brief.get("round_log", []),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a conservative Kelly sizing report from a structured brief."
    )
    parser.add_argument("--input", required=True, help="Path to input JSON, or - for stdin.")
    parser.add_argument("--output", help="Optional path for output JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        brief = load_brief(args.input)
        report = build_report(brief)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    write_json({"ok": True, "report": report}, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
