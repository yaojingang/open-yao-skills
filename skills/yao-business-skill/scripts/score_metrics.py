#!/usr/bin/env python3
import argparse
import json
import math
import sys
from pathlib import Path


MODELS = {
    "confidence": {
        "weights": {
            "source_quality": 0.28,
            "direct_observability": 0.22,
            "triangulation": 0.18,
            "benchmark_fit": 0.12,
            "recency": 0.10,
            "accounting_clarity": 0.10,
            "risk_penalty": -1.0,
        },
        "ranges": {
            "source_quality": (0, 100),
            "direct_observability": (0, 100),
            "triangulation": (0, 100),
            "benchmark_fit": (0, 100),
            "recency": (0, 100),
            "accounting_clarity": (0, 100),
            "risk_penalty": (0, 30),
        },
        "formula": "0.28*source_quality + 0.22*direct_observability + 0.18*triangulation + 0.12*benchmark_fit + 0.10*recency + 0.10*accounting_clarity - risk_penalty",
    },
    "environment-fit": {
        "weights": {
            "channel_fit": 0.22,
            "payment_fit": 0.20,
            "compliance_fit": 0.20,
            "trust_fit": 0.15,
            "service_fit": 0.13,
            "competition_fit": 0.10,
        },
        "ranges": {
            "channel_fit": (0, 100),
            "payment_fit": (0, 100),
            "compliance_fit": (0, 100),
            "trust_fit": (0, 100),
            "service_fit": (0, 100),
            "competition_fit": (0, 100),
        },
        "formula": "0.22*channel_fit + 0.20*payment_fit + 0.20*compliance_fit + 0.15*trust_fit + 0.13*service_fit + 0.10*competition_fit",
    },
    "direct-competitor": {
        "weights": {
            "customer_overlap": 0.16,
            "need_overlap": 0.16,
            "feature_overlap": 0.14,
            "pricing_model_overlap": 0.12,
            "channel_overlap": 0.10,
            "financial_comparability": 0.12,
            "evidence_quality": 0.10,
            "scale_signal": 0.06,
            "risk_similarity": 0.04,
        },
        "ranges": {
            "customer_overlap": (0, 100),
            "need_overlap": (0, 100),
            "feature_overlap": (0, 100),
            "pricing_model_overlap": (0, 100),
            "channel_overlap": (0, 100),
            "financial_comparability": (0, 100),
            "evidence_quality": (0, 100),
            "scale_signal": (0, 100),
            "risk_similarity": (0, 100),
        },
        "formula": "0.16*customer_overlap + 0.16*need_overlap + 0.14*feature_overlap + 0.12*pricing_model_overlap + 0.10*channel_overlap + 0.12*financial_comparability + 0.10*evidence_quality + 0.06*scale_signal + 0.04*risk_similarity",
    },
    "cross-industry": {
        "weights": {
            "revenue_mechanism_similarity": 0.25,
            "unit_economics_similarity": 0.20,
            "growth_flywheel_similarity": 0.18,
            "supply_demand_structure_similarity": 0.12,
            "pricing_psychology_similarity": 0.10,
            "operating_constraint_similarity": 0.08,
            "stage_adaptation": 0.07,
        },
        "ranges": {
            "revenue_mechanism_similarity": (0, 100),
            "unit_economics_similarity": (0, 100),
            "growth_flywheel_similarity": (0, 100),
            "supply_demand_structure_similarity": (0, 100),
            "pricing_psychology_similarity": (0, 100),
            "operating_constraint_similarity": (0, 100),
            "stage_adaptation": (0, 100),
        },
        "formula": "0.25*revenue_mechanism_similarity + 0.20*unit_economics_similarity + 0.18*growth_flywheel_similarity + 0.12*supply_demand_structure_similarity + 0.10*pricing_psychology_similarity + 0.08*operating_constraint_similarity + 0.07*stage_adaptation",
    },
    "idea-option": {
        "weights": {
            "market_pain": 0.18,
            "willingness_to_pay": 0.16,
            "margin_potential": 0.14,
            "repurchase_frequency": 0.12,
            "channel_reach": 0.10,
            "moat": 0.10,
            "compliance_control": 0.08,
            "data_advantage": 0.08,
            "execution_complexity": -0.06,
        },
        "ranges": {
            "market_pain": (0, 100),
            "willingness_to_pay": (0, 100),
            "margin_potential": (0, 100),
            "repurchase_frequency": (0, 100),
            "channel_reach": (0, 100),
            "moat": (0, 100),
            "compliance_control": (0, 100),
            "data_advantage": (0, 100),
            "execution_complexity": (0, 100),
        },
        "formula": "0.18*market_pain + 0.16*willingness_to_pay + 0.14*margin_potential + 0.12*repurchase_frequency + 0.10*channel_reach + 0.10*moat + 0.08*compliance_control + 0.08*data_advantage - 0.06*execution_complexity",
    },
}


def load_payload(input_path: str | None) -> dict:
    if input_path:
        return json.loads(Path(input_path).read_text(encoding="utf-8"))
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("No input JSON provided.")
    return json.loads(raw)


def ensure_number(value: object, key: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"Field {key} must be numeric.")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"Field {key} must be finite.")
    return number


def classify_score(model_name: str, score: float) -> str:
    if model_name == "confidence":
        if score >= 85:
            return "high_confidence"
        if score >= 70:
            return "fairly_strong"
        if score >= 50:
            return "moderate_estimate"
        if score >= 30:
            return "weak_hypothesis"
        return "unsupported"
    if score >= 80:
        return "very_strong"
    if score >= 65:
        return "strong"
    if score >= 50:
        return "moderate"
    if score >= 35:
        return "weak"
    return "poor"


def score_model(model_name: str, payload: dict) -> dict:
    if model_name not in MODELS:
        raise ValueError(f"Unsupported model: {model_name}")
    model = MODELS[model_name]
    weights = model["weights"]
    ranges = model["ranges"]

    missing = [key for key in weights if key not in payload]
    if missing:
        raise ValueError(f"Missing fields: {', '.join(missing)}")

    warnings = []
    contributions = {}
    raw_score = 0.0
    normalized_inputs = {}

    for key, weight in weights.items():
        value = ensure_number(payload[key], key)
        normalized_inputs[key] = value
        lower, upper = ranges[key]
        if value < lower or value > upper:
            warnings.append(f"{key} outside expected range {lower}-{upper}: {value}")
        contribution = weight * value
        contributions[key] = round(contribution, 3)
        raw_score += contribution

    clipped_score = max(0.0, min(100.0, raw_score))
    return {
        "model": model_name,
        "formula": model["formula"],
        "inputs": normalized_inputs,
        "weighted_breakdown": contributions,
        "raw_score": round(raw_score, 3),
        "score": round(clipped_score, 1),
        "band": classify_score(model_name, clipped_score),
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Score business-model metrics using the Yao Business Skill formulas.")
    parser.add_argument(
        "model",
        choices=sorted(MODELS.keys()),
        help="Which scoring model to run",
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Path to a JSON file. If omitted, JSON is read from stdin.",
    )
    args = parser.parse_args()

    payload = load_payload(args.input)
    result = score_model(args.model, payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
