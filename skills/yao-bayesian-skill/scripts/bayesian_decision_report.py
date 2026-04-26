#!/usr/bin/env python3
import argparse
import bisect
import json
import math
import sys
from pathlib import Path


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def round_float(value: float | None, digits: int = 4) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def normalize_value(value):
    if isinstance(value, float):
        return round_float(value)
    if isinstance(value, int):
        return value
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: normalize_value(item) for key, item in value.items()}
    return value


def localize_text(value, lang: str = "zh") -> str | None:
    if value is None:
        return None
    if isinstance(value, dict):
        key_groups = {
            "zh": ("zh", "zh-CN", "zh_cn", "cn"),
            "en": ("en", "en-US", "en_us"),
        }
        for key in key_groups.get(lang, ()):
            text = value.get(key)
            if isinstance(text, str) and text.strip():
                return text.strip()
        for fallback in ("zh", "zh-CN", "en", "en-US"):
            text = value.get(fallback)
            if isinstance(text, str) and text.strip():
                return text.strip()
        for text in value.values():
            if isinstance(text, str) and text.strip():
                return text.strip()
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, str):
        return value
    return str(value)


def localize_list(values, lang: str = "zh") -> list[str]:
    return [localize_text(item, lang) for item in (values or []) if localize_text(item, lang)]


def confidence_label_zh(code: str | None) -> str | None:
    mapping = {
        "low": "低",
        "medium": "中",
        "medium-high": "中高",
    }
    return mapping.get(code, code)


def direction_label_zh(direction: str | None) -> str:
    mapping = {
        "support": "支持",
        "against": "削弱",
    }
    return mapping.get(direction or "", direction or "未知")


PRIOR_HYGIENE_LIBRARY_SIZE = 20


PRIOR_HYGIENE_RULES = {
    "fallibility": {
        "principle": "我可能错",
        "principle_en": "I may be wrong",
        "core_sentence": "任何判断先给自己留一条退路。",
        "core_sentence_en": "Leave room for every judgment to be wrong.",
        "score": 25,
    },
    "base_rate": {
        "principle": "基础率优先",
        "principle_en": "Base rates first",
        "core_sentence": "先看一般规律，再看个别故事。",
        "core_sentence_en": "Start with the general pattern before the individual story.",
        "score": 25,
    },
    "evidence_grade": {
        "principle": "证据有等级",
        "principle_en": "Evidence has grades",
        "core_sentence": "独立、重复、可验证的证据更强。",
        "core_sentence_en": "Independent, repeatable, verifiable evidence is stronger.",
        "score": 25,
    },
    "strong_evidence": {
        "principle": "强结论需要强证据",
        "principle_en": "Strong claims need strong evidence",
        "core_sentence": "越惊人的说法，证据门槛越高。",
        "core_sentence_en": "The stronger the claim, the stronger the evidence should be.",
        "score": 24,
    },
    "small_sample": {
        "principle": "小样本很吵",
        "principle_en": "Small samples are noisy",
        "core_sentence": "一两个案例不能代表整体。",
        "core_sentence_en": "One or two cases rarely represent the whole population.",
        "score": 24,
    },
    "ruin_risk": {
        "principle": "避免毁灭性风险",
        "principle_en": "Avoid ruin risk",
        "core_sentence": "先避免输光，再追求赢很多。",
        "core_sentence_en": "Avoid unrecoverable loss before chasing large upside.",
        "score": 24,
    },
    "causality": {
        "principle": "相关不等于因果",
        "principle_en": "Correlation is not causation",
        "core_sentence": "两件事一起发生，不代表一件导致另一件。",
        "core_sentence_en": "Two things moving together does not prove one caused the other.",
        "score": 23,
    },
    "reversibility": {
        "principle": "保留可逆选项",
        "principle_en": "Keep reversible options",
        "core_sentence": "不确定时，优先选择还能调整的路。",
        "core_sentence_en": "Under uncertainty, prefer paths you can adjust.",
        "score": 22,
    },
    "disconfirming": {
        "principle": "反面证据最珍贵",
        "principle_en": "Disconfirming evidence is valuable",
        "core_sentence": "能改变你看法的证据，最值得看。",
        "core_sentence_en": "The evidence that could change your mind is the most valuable.",
        "score": 22,
    },
    "stale_prior": {
        "principle": "先验会过期",
        "principle_en": "Priors can expire",
        "core_sentence": "世界变了，旧经验要重新校准。",
        "core_sentence_en": "When the world changes, old experience needs recalibration.",
        "score": 21,
    },
}


def load_request(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_output(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def log_beta_fn(alpha: float, beta: float) -> float:
    return math.lgamma(alpha) + math.lgamma(beta) - math.lgamma(alpha + beta)


def beta_quantiles_grid(alpha: float, beta: float, probs: tuple[float, float] = (0.05, 0.95), steps: int = 4000) -> list[float]:
    if alpha <= 0 or beta <= 0:
        raise ValueError("alpha and beta must be positive")
    xs = [(index + 0.5) / steps for index in range(steps)]
    log_norm = log_beta_fn(alpha, beta)
    log_weights = []
    for x in xs:
        log_pdf = (alpha - 1.0) * math.log(x) + (beta - 1.0) * math.log(1.0 - x) - log_norm
        log_weights.append(log_pdf)
    max_log = max(log_weights)
    weights = [math.exp(item - max_log) for item in log_weights]
    total = sum(weights)
    cdf = []
    running = 0.0
    for weight in weights:
        running += weight / total
        cdf.append(running)
    quantiles = []
    for prob in probs:
        idx = bisect.bisect_left(cdf, prob)
        idx = min(idx, steps - 1)
        quantiles.append(xs[idx])
    return quantiles


def beta_stats(alpha: float, beta: float) -> dict:
    mean = alpha / (alpha + beta)
    low, high = beta_quantiles_grid(alpha, beta)
    return {
      "mean": mean,
      "credible_interval": [low, high],
      "equivalent_sample_size": alpha + beta,
    }


def build_prior(prior: dict, warnings: list[str]) -> dict:
    alpha = prior.get("alpha")
    beta = prior.get("beta")
    probability = prior.get("probability")
    ess = prior.get("equivalent_sample_size")

    if alpha is not None and beta is not None:
        alpha = float(alpha)
        beta = float(beta)
        stats = beta_stats(alpha, beta)
        if probability is None:
            probability = stats["mean"]
        if ess is None:
            ess = alpha + beta
        return {
            "mode": "beta",
            "alpha": alpha,
            "beta": beta,
            "probability": float(probability),
            "equivalent_sample_size": float(ess),
            "credible_interval": stats["credible_interval"],
            "source_summary": localize_list(prior.get("source_summary", []), "zh"),
            "source_quality": localize_text(prior.get("source_quality"), "zh"),
            "confidence": confidence_label_zh(localize_text(prior.get("confidence"), "zh")),
        }

    if probability is None:
        raise ValueError("prior must include either alpha/beta or probability")

    probability = clamp(float(probability), 1e-6, 1 - 1e-6)
    payload = {
        "mode": "probability",
        "probability": probability,
        "equivalent_sample_size": float(ess) if ess is not None else None,
        "source_summary": localize_list(prior.get("source_summary", []), "zh"),
        "source_quality": localize_text(prior.get("source_quality"), "zh"),
        "confidence": confidence_label_zh(localize_text(prior.get("confidence"), "zh")),
    }
    if ess is not None:
        alpha = probability * float(ess)
        beta = (1 - probability) * float(ess)
        if alpha > 0 and beta > 0:
            stats = beta_stats(alpha, beta)
            payload.update(
                {
                    "mode": "beta",
                    "alpha": alpha,
                    "beta": beta,
                    "credible_interval": stats["credible_interval"],
                }
            )
    else:
        warnings.append("未提供先验等效样本量，先验强度相关的敏感性判断会更弱。")
    return payload


def effective_lr(item: dict) -> float:
    lr = float(item.get("likelihood_ratio", 1.0))
    if lr <= 0:
        raise ValueError(f"likelihood_ratio must be positive for evidence item {item.get('name', '<unnamed>')}")
    direction = item.get("direction", "support")
    if direction == "against":
        lr = 1.0 / lr
    discount = clamp(float(item.get("dependency_discount", 1.0)), 0.0, 1.0)
    return math.exp(math.log(lr) * discount)


def apply_odds_update(prior_probability: float, evidence: list[dict], lr_power: float = 1.0) -> tuple[float, list[dict], float, float]:
    prior_probability = clamp(prior_probability, 1e-6, 1 - 1e-6)
    prior_odds = prior_probability / (1.0 - prior_probability)
    odds = prior_odds
    log = []
    for item in evidence:
        base_effective_lr = effective_lr(item)
        effective_with_power = math.exp(math.log(base_effective_lr) * lr_power)
        before = odds
        odds *= effective_with_power
        log.append(
            {
                "name": item.get("name"),
                "quality": item.get("quality"),
                "direction": item.get("direction", "support"),
                "base_likelihood_ratio": round_float(float(item.get("likelihood_ratio", 1.0))),
                "dependency_discount": round_float(float(item.get("dependency_discount", 1.0))),
                "effective_likelihood_ratio": round_float(base_effective_lr),
                "lr_power": round_float(lr_power),
                "applied_likelihood_ratio": round_float(effective_with_power),
                "odds_before": round_float(before),
                "odds_after": round_float(odds),
            }
        )
    posterior_probability = odds / (1.0 + odds)
    return posterior_probability, log, prior_odds, odds


def apply_beta_binomial(prior_payload: dict, observations: dict) -> dict:
    alpha = float(prior_payload["alpha"])
    beta = float(prior_payload["beta"])
    trials = int(observations["trials"])
    successes = int(observations["successes"])
    failures = trials - successes
    if successes < 0 or failures < 0:
        raise ValueError("observations.successes must be between 0 and observations.trials")
    post_alpha = alpha + successes
    post_beta = beta + failures
    stats = beta_stats(post_alpha, post_beta)
    return {
        "posterior_alpha": post_alpha,
        "posterior_beta": post_beta,
        "posterior_probability": stats["mean"],
        "credible_interval": stats["credible_interval"],
        "calculation_log": [
            {
                "step": "prior",
                "alpha": round_float(alpha),
                "beta": round_float(beta),
            },
            {
                "step": "data",
                "trials": trials,
                "successes": successes,
                "failures": failures,
            },
            {
                "step": "posterior",
                "alpha": round_float(post_alpha),
                "beta": round_float(post_beta),
            },
        ],
    }


def readiness_code(value: float | None) -> str | None:
    if value is None:
        return None
    if value >= 0.75:
        return "ready"
    if value >= 0.45:
        return "nearly-ready"
    return "collecting"


def readiness_label_zh(value: float | None) -> str:
    mapping = {
        "ready": "可以决策",
        "nearly-ready": "接近可决策",
        "collecting": "仍需补信息",
    }
    return mapping.get(readiness_code(value), "未评估")


def status_labels(code: str | None) -> tuple[str, str]:
    mapping = {
        "ready": ("可以进入决策", "Ready to decide"),
        "needs-more-info": ("还需补充信息", "Need more information"),
        "in-progress": ("继续迭代判断", "Keep iterating"),
        "blocked": ("当前被阻塞", "Blocked"),
    }
    return mapping.get(code or "", ("继续迭代判断", "Keep iterating"))


def _fmt_pct_text(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{float(value) * 100:.1f}%"


def build_round_formula(round_item: dict, prior_before: float | None, posterior_after: float | None, index: int) -> dict:
    bayes_update = round_item.get("bayes_update") or {}
    method = bayes_update.get("update_method") or round_item.get("update_method") or "manual"
    detail = {
        "update_method": method,
        "formula_zh": "本轮没有足够的结构化参数，采用记录中的更新结果。",
        "formula_en": "This round does not provide enough structured parameters, so the recorded update result is used directly.",
    }

    if method == "odds-update" and prior_before is not None:
        likelihood_ratio = bayes_update.get("likelihood_ratio")
        if likelihood_ratio is not None:
            direction = bayes_update.get("direction", "support")
            dependency_discount = clamp(float(bayes_update.get("dependency_discount", 1.0)), 0.0, 1.0)
            item = {
                "name": f"round-{index}",
                "likelihood_ratio": likelihood_ratio,
                "direction": direction,
                "dependency_discount": dependency_discount,
            }
            computed_probability, _, prior_odds, posterior_odds = apply_odds_update(float(prior_before), [item])
            if posterior_after is None:
                posterior_after = computed_probability
            display_posterior_odds = float(posterior_after) / (1.0 - float(posterior_after))
            detail.update(
                {
                    "prior_odds": round_float(prior_odds),
                    "posterior_odds": round_float(display_posterior_odds),
                    "computed_posterior_odds": round_float(posterior_odds),
                    "computed_posterior_probability": round_float(computed_probability),
                    "likelihood_ratio": round_float(float(likelihood_ratio)),
                    "dependency_discount": round_float(dependency_discount),
                    "direction": direction,
                    "posterior_probability": round_float(posterior_after),
                    "formula_zh": (
                        f"把本轮起点概率 {_fmt_pct_text(prior_before)} 转成先验 odds {prior_odds:.3f}，"
                        f"再结合本轮记录的证据强度，得到后验 odds {display_posterior_odds:.3f}，"
                        f"对应概率约 {_fmt_pct_text(posterior_after)}。"
                    ),
                    "formula_en": (
                        f"Convert the starting belief {_fmt_pct_text(prior_before)} into prior odds {prior_odds:.3f}, "
                        f"combine it with the recorded evidence strength to get posterior odds {display_posterior_odds:.3f}, "
                        f"which maps to about {_fmt_pct_text(posterior_after)}."
                    ),
                }
            )
            return detail

    if method == "beta-binomial":
        prior_alpha = bayes_update.get("prior_alpha")
        prior_beta = bayes_update.get("prior_beta")
        trials = bayes_update.get("trials")
        successes = bayes_update.get("successes")
        if None not in (prior_alpha, prior_beta, trials, successes):
            posterior_block = apply_beta_binomial(
                {"alpha": float(prior_alpha), "beta": float(prior_beta)},
                {"trials": int(trials), "successes": int(successes)},
            )
            posterior_after = posterior_after if posterior_after is not None else posterior_block["posterior_probability"]
            detail.update(
                {
                    "prior_alpha": round_float(float(prior_alpha)),
                    "prior_beta": round_float(float(prior_beta)),
                    "posterior_alpha": round_float(float(posterior_block["posterior_alpha"])),
                    "posterior_beta": round_float(float(posterior_block["posterior_beta"])),
                    "trials": int(trials),
                    "successes": int(successes),
                    "posterior_probability": round_float(posterior_after),
                    "formula_zh": (
                        f"把先验 Beta({round_float(float(prior_alpha))}, {round_float(float(prior_beta))}) "
                        f"与新观察 {int(successes)}/{int(trials)} 合并，得到后验 "
                        f"Beta({round_float(float(posterior_block['posterior_alpha']))}, {round_float(float(posterior_block['posterior_beta']))})，"
                        f"均值约 {_fmt_pct_text(posterior_after)}。"
                    ),
                    "formula_en": (
                        f"Combine the prior Beta({round_float(float(prior_alpha))}, {round_float(float(prior_beta))}) "
                        f"with new observations {int(successes)}/{int(trials)} to get posterior "
                        f"Beta({round_float(float(posterior_block['posterior_alpha']))}, {round_float(float(posterior_block['posterior_beta']))}), "
                        f"with a mean near {_fmt_pct_text(posterior_after)}."
                    ),
                }
            )
            return detail

    if prior_before is not None and posterior_after is not None:
        detail.update(
            {
                "posterior_probability": round_float(posterior_after),
                "formula_zh": f"本轮把判断从 {_fmt_pct_text(prior_before)} 更新到了 {_fmt_pct_text(posterior_after)}。",
                "formula_en": f"This round moves the belief from {_fmt_pct_text(prior_before)} to {_fmt_pct_text(posterior_after)}.",
            }
        )
    return detail


def build_conversation_process(request: dict, initial_prior_probability: float, final_posterior_probability: float, recommendation: str) -> dict | None:
    conversation = request.get("conversation") or {}
    rounds_input = conversation.get("rounds") or []
    current_state = localize_text(conversation.get("initial_state"), "zh") or localize_text(request.get("current_state"), "zh")
    if not rounds_input and not current_state:
        return None

    threshold = clamp(float(conversation.get("decision_ready_threshold", 0.75)), 0.0, 1.0)
    rounds = []
    trajectory = []
    last_posterior = initial_prior_probability

    for index, item in enumerate(rounds_input, start=1):
        prior_before = item.get("prior_probability_before")
        if prior_before is None:
            prior_before = last_posterior
        prior_before = clamp(float(prior_before), 1e-6, 1 - 1e-6) if prior_before is not None else None

        posterior_after = item.get("posterior_probability_after")
        posterior_after = clamp(float(posterior_after), 1e-6, 1 - 1e-6) if posterior_after is not None else None
        formula = build_round_formula(item, prior_before, posterior_after, index)
        if posterior_after is None and formula.get("posterior_probability") is not None:
            posterior_after = clamp(float(formula["posterior_probability"]), 1e-6, 1 - 1e-6)

        readiness = item.get("decision_readiness")
        readiness = clamp(float(readiness), 0.0, 1.0) if readiness is not None else None
        delta = None
        if prior_before is not None and posterior_after is not None:
            delta = posterior_after - prior_before
            last_posterior = posterior_after

        round_payload = {
            "round": int(item.get("round", index)),
            "stage": localize_text(item.get("stage"), "zh") or f"第 {index} 轮",
            "prior_probability_before": round_float(prior_before),
            "posterior_probability_after": round_float(posterior_after),
            "delta_probability": round_float(delta),
            "decision_readiness": round_float(readiness),
            "decision_readiness_label": readiness_label_zh(readiness),
            "user_input_summary": localize_text(item.get("user_input_summary"), "zh"),
            "assistant_focus": localize_text(item.get("assistant_focus"), "zh"),
            "new_information": localize_list(item.get("new_information"), "zh"),
            "assistant_next_questions": localize_list(item.get("assistant_next_questions"), "zh"),
            "missing_information": localize_list(item.get("missing_information"), "zh"),
            "interim_judgment": localize_text(item.get("interim_judgment"), "zh"),
            "bayes_update": normalize_value(formula),
        }
        rounds.append(round_payload)
        trajectory.append(
            {
                "round": round_payload["round"],
                "stage": round_payload["stage"],
                "prior_probability": round_payload["prior_probability_before"],
                "posterior_probability": round_payload["posterior_probability_after"],
                "decision_readiness": round_payload["decision_readiness"],
                "delta_probability": round_payload["delta_probability"],
            }
        )

    final_readiness = conversation.get("final_readiness")
    if final_readiness is None and rounds:
        final_readiness = rounds[-1].get("decision_readiness")
    final_readiness = clamp(float(final_readiness), 0.0, 1.0) if final_readiness is not None else None

    open_questions = localize_list(conversation.get("open_questions"), "zh")
    if not open_questions and rounds:
        open_questions = rounds[-1].get("missing_information", [])

    decision_ready = conversation.get("decision_ready")
    if decision_ready is None:
        decision_ready = bool(final_readiness is not None and final_readiness >= threshold and not open_questions)

    status_code = localize_text(conversation.get("decision_status"), "zh")
    if status_code not in {"ready", "needs-more-info", "in-progress", "blocked"}:
        if decision_ready:
            status_code = "ready"
        elif open_questions:
            status_code = "needs-more-info"
        else:
            status_code = "in-progress"

    status_zh, status_en = status_labels(status_code)
    strongest_round = None
    if rounds:
        strongest_round = max(rounds, key=lambda item: abs(float(item.get("delta_probability") or 0.0)))

    strongest_text = ""
    if strongest_round and strongest_round.get("delta_probability") is not None:
        strongest_text = (
            f"变化最大的轮次是第 {strongest_round['round']} 轮，概率变动约为 "
            f"{float(strongest_round['delta_probability']) * 100:+.1f} 个百分点。"
        )

    analysis_zh = (
        f"本次决策一共记录了 {len(rounds)} 轮对话，判断从初始先验 {_fmt_pct_text(initial_prior_probability)} "
        f"演化到了当前后验 {_fmt_pct_text(final_posterior_probability)}。{strongest_text} "
        f"当前决策准备度约为 {_fmt_pct_text(final_readiness)}，阈值为 {_fmt_pct_text(threshold)}，"
        f"{'已经' if decision_ready else '尚未'}达到“可以进入决策”的状态。"
    )
    analysis_en = (
        f"This decision captured {len(rounds)} rounds of dialogue, moving from an initial prior of "
        f"{_fmt_pct_text(initial_prior_probability)} to a current posterior of {_fmt_pct_text(final_posterior_probability)}. "
        f"The current readiness is {_fmt_pct_text(final_readiness)} versus a threshold of {_fmt_pct_text(threshold)}, "
        f"so the session has {'reached' if decision_ready else 'not yet reached'} a ready-to-decide state."
    )

    return {
        "enabled": True,
        "initial_state": current_state or "-",
        "initial_problem_statement": localize_text(conversation.get("initial_problem_statement"), "zh") or localize_text(request.get("question"), "zh"),
        "round_count": len(rounds),
        "decision_ready_threshold": round_float(threshold),
        "final_readiness": round_float(final_readiness),
        "final_readiness_label": readiness_label_zh(final_readiness),
        "decision_ready": bool(decision_ready),
        "status": status_zh,
        "status_code": status_code,
        "status_en": status_en,
        "analysis": analysis_zh,
        "analysis_en": analysis_en,
        "open_questions": open_questions,
        "recommended_action_at_close": recommendation,
        "trajectory": trajectory,
        "rounds": rounds,
    }


def update_interval_with_evidence(interval: list[float], evidence: list[dict]) -> list[float]:
    updated = [apply_odds_update(value, evidence)[0] for value in interval]
    return sorted(updated)


def default_prior_scenarios(prior_payload: dict) -> list[float]:
    if prior_payload.get("mode") == "beta":
        alpha = float(prior_payload["alpha"])
        beta = float(prior_payload["beta"])
        low, high = beta_quantiles_grid(alpha, beta, probs=(0.1, 0.9))
        base = float(prior_payload["probability"])
        return sorted({round(low, 4), round(base, 4), round(high, 4)})
    base = float(prior_payload["probability"])
    low = clamp(base * 0.6, 0.01, 0.99)
    high = clamp(max(base * 1.4, base + 0.1), 0.01, 0.99)
    return sorted({round(low, 4), round(base, 4), round(high, 4)})


def utilities_for_action(action: dict) -> tuple[float, float]:
    if "utility_if_h_true" in action and "utility_if_h_false" in action:
        return float(action["utility_if_h_true"]), float(action["utility_if_h_false"])
    cost = float(action.get("cost", 0.0))
    upside_if_true = float(action.get("upside_if_h_true", 0.0))
    downside_if_false = float(action.get("downside_if_h_false", 0.0))
    opportunity_cost = float(action.get("opportunity_cost", 0.0))
    utility_true = upside_if_true - cost + opportunity_cost
    utility_false = downside_if_false - cost + opportunity_cost
    return utility_true, utility_false


def action_threshold(utility_true: float, utility_false: float) -> float | None:
    delta = utility_true - utility_false
    if abs(delta) < 1e-12:
        return None
    threshold = -utility_false / delta
    if threshold < 0:
        return 0.0
    if threshold > 1:
        return 1.0
    return threshold


def evaluate_actions(actions: list[dict], posterior_probability: float) -> list[dict]:
    evaluated = []
    for action in actions:
        utility_true, utility_false = utilities_for_action(action)
        expected_value = posterior_probability * utility_true + (1.0 - posterior_probability) * utility_false
        threshold = action_threshold(utility_true, utility_false)
        evaluated.append(
            {
                "name": action["name"],
                "utility_if_h_true": round_float(utility_true),
                "utility_if_h_false": round_float(utility_false),
                "expected_value": round_float(expected_value),
                "action_threshold": round_float(threshold),
            }
        )
    evaluated.sort(key=lambda item: item["expected_value"], reverse=True)
    return evaluated


def recommendation_confidence(warnings: list[str], stability: str, evidence: list[dict]) -> str:
    weak_count = sum(1 for item in evidence if item.get("quality") in {"D", "E"})
    if stability == "unstable" or len(warnings) >= 3 or weak_count >= 2:
        return "low"
    if stability == "mixed" or len(warnings) >= 1 or weak_count >= 1:
        return "medium"
    return "medium-high"


def natural_frequency(prior_probability: float, posterior_probability: float, base: int = 100) -> dict:
    prior_cases = round(prior_probability * base)
    posterior_cases = round(posterior_probability * base)
    return {
        "base_population": base,
        "prior_expected_successes": prior_cases,
        "posterior_expected_successes": posterior_cases,
        "explanation": (
            f"在 {base} 个相似案例里，先验大约意味着其中 {prior_cases} 个会成功。"
            f"加入当前证据后，估计会成功的案例约为 {posterior_cases} 个。"
        ),
    }


def information_value_hint(actions: list[dict], posterior_probability: float, candidates: list[str]) -> dict:
    best = actions[0] if actions else None
    second = actions[1] if len(actions) > 1 else None
    gap = None
    if best and second:
        gap = float(best["expected_value"]) - float(second["expected_value"])
    near_threshold = False
    if best and best.get("action_threshold") is not None:
        near_threshold = abs(posterior_probability - float(best["action_threshold"])) <= 0.1
    high_value = near_threshold or (gap is not None and abs(gap) <= max(5000.0, abs(float(best["expected_value"])) * 0.15))
    candidate = candidates[0] if candidates else None
    if candidate is None:
        candidate = "优先收集一个比口头兴趣更接近真实行为的低成本信号。"
    return {
        "high_value": high_value,
        "recommended_next_information": candidate,
        "reason": (
            "当前结果已经接近关键行动阈值，新增信息有较大概率改变建议。"
            if high_value
            else "继续补充信息仍然有价值，但当前建议对边界变化没有那么敏感。"
        ),
    }


def action_text_blob(actions: list[dict], evaluated_actions: list[dict]) -> str:
    parts = []
    for item in actions + evaluated_actions:
        if item.get("name"):
            parts.append(str(item["name"]))
    return " ".join(parts).lower()


def add_hygiene_check(checks: list[dict], rule_id: str, priority: int, trigger: str, trigger_en: str, decision_use: str, decision_use_en: str) -> None:
    rule = PRIOR_HYGIENE_RULES[rule_id]
    checks.append(
        {
            "id": rule_id,
            "priority": priority,
            "principle": rule["principle"],
            "principle_en": rule["principle_en"],
            "core_sentence": rule["core_sentence"],
            "core_sentence_en": rule["core_sentence_en"],
            "score": rule["score"],
            "trigger": trigger,
            "trigger_en": trigger_en,
            "decision_use": decision_use,
            "decision_use_en": decision_use_en,
        }
    )


def build_prior_hygiene_checks(
    request: dict,
    prior_payload: dict,
    evidence: list[dict],
    actions: list[dict],
    evaluated_actions: list[dict],
    sensitivity: dict,
    warnings: list[str],
    next_info: dict,
) -> dict:
    config = request.get("prior_hygiene") or {}
    max_reported = int(config.get("max_reported", 5))
    max_reported = max(3, min(max_reported, 8))
    checks: list[dict] = []
    observations = request.get("observations") or {}
    trials = observations.get("trials")
    weak_evidence_count = sum(1 for item in evidence if item.get("quality") in {"C", "D", "E"})
    dependent_count = sum(1 for item in evidence if float(item.get("dependency_discount", 1.0)) < 1.0)
    min_false_utility = min((utilities_for_action(item)[1] for item in actions), default=0.0)
    text_blob = action_text_blob(actions, evaluated_actions)

    add_hygiene_check(
        checks,
        "fallibility",
        100,
        "当前报告存在后验区间、敏感性结果和警示项，需要保留可更新余地。",
        "The report has an interval, sensitivity results, and warnings, so the judgment should remain updateable.",
        "在结论里保留置信度、剩余缺口和触发重新判断的条件。",
        "Keep confidence, remaining gaps, and update triggers visible in the conclusion.",
    )
    add_hygiene_check(
        checks,
        "base_rate",
        95,
        f"先验来自 {localize_text(prior_payload.get('source_quality'), 'zh') or '未标明'} 等级来源，当前判断需要先从参考类出发。",
        f"The prior uses {localize_text(prior_payload.get('source_quality'), 'en') or 'unspecified'} quality sources, so the judgment should start from the reference class.",
        "先把参考类作为起点，再用当前个案证据上调或下调。",
        "Use the reference class as the starting point, then update with case-specific evidence.",
    )
    if evidence:
        add_hygiene_check(
            checks,
            "evidence_grade",
            90,
            f"本次使用了 {len(evidence)} 条证据，其中 {weak_evidence_count} 条属于 C/D/E 或更弱等级。",
            f"This report uses {len(evidence)} evidence items; {weak_evidence_count} are C/D/E or weaker signals.",
            "弱证据可以影响方向，但更新幅度要小，并在敏感性分析里重跑。",
            "Weak evidence may guide direction, but it should update less and be stress-tested.",
        )
    if sensitivity.get("conclusion_stability_code") != "stable" or weak_evidence_count or warnings:
        add_hygiene_check(
            checks,
            "strong_evidence",
            84,
            "当前结论仍受证据强度、依赖折扣或敏感性变化影响。",
            "The conclusion is still affected by evidence strength, dependency discounts, or sensitivity changes.",
            "重投入或强承诺需要更强证据；现阶段优先用低成本验证补证据。",
            "Heavy commitment needs stronger evidence; use a low-cost validation step first.",
        )
    if trials is not None and float(trials) < 30:
        add_hygiene_check(
            checks,
            "small_sample",
            82,
            f"当前可观察样本量为 {int(float(trials))}，仍属于容易波动的小样本。",
            f"The observed sample size is {int(float(trials))}, which is still noisy.",
            "把观察结果当成方向性信号，而不是直接当成稳定规律。",
            "Treat observations as directional signals rather than a stable pattern.",
        )
    if request.get("high_risk_domain") or min_false_utility <= -50000:
        add_hygiene_check(
            checks,
            "ruin_risk",
            88,
            "至少一个行动存在较大失败损失，或该领域本身属于高风险辅助判断。",
            "At least one action has substantial downside, or the domain itself is high-risk decision support.",
            "即使后验概率较高，也要先控制不可恢复损失和退出路径。",
            "Even with a high posterior, control unrecoverable downside and exit paths first.",
        )
    if dependent_count:
        add_hygiene_check(
            checks,
            "causality",
            78,
            f"{dependent_count} 条证据存在依赖折扣，说明这些信号不能完全独立相乘。",
            f"{dependent_count} evidence items received dependency discounts, so these signals should not be multiplied as fully independent.",
            "把相关信号当作线索，继续寻找更接近因果或行为结果的证据。",
            "Treat correlated signals as clues and seek more causal or behavioral evidence.",
        )
    if any(token in text_blob for token in ("试", "test", "pilot", "landing", "小规模", "分阶段", "先做")):
        add_hygiene_check(
            checks,
            "reversibility",
            76,
            "备选行动里已经存在试点、测试或分阶段方案。",
            "The action set already includes a pilot, test, or staged option.",
            "在不确定性较高时，优先选择能撤回、能学习、能继续更新的行动。",
            "Under uncertainty, prefer actions that are reversible, informative, and updateable.",
        )
    if next_info.get("recommended_next_information"):
        add_hygiene_check(
            checks,
            "disconfirming",
            72,
            "报告已经识别出下一步最有价值的信息。",
            "The report has identified the next most valuable information to collect.",
            "把下一步信息设计成能推翻当前建议的测试，而不是只寻找支持证据。",
            "Design the next information step to challenge the recommendation, not only confirm it.",
        )
    if prior_payload.get("source_summary"):
        add_hygiene_check(
            checks,
            "stale_prior",
            64,
            "当前先验依赖历史经验、类比或已有样本。",
            "The prior depends on historical experience, analogy, or previous samples.",
            "如果环境、用户群或市场周期已变化，需要重新校准先验。",
            "If the environment, user segment, or market cycle has changed, recalibrate the prior.",
        )

    checks.sort(key=lambda item: item["priority"], reverse=True)
    selected = checks[:max_reported]
    for item in selected:
        item.pop("priority", None)
    return {
        "principles_total": PRIOR_HYGIENE_LIBRARY_SIZE,
        "reported_count": len(selected),
        "selection_rule": f"从 {PRIOR_HYGIENE_LIBRARY_SIZE} 条生活贝叶斯先验中，只展示本次最相关的 {len(selected)} 条。",
        "selection_rule_en": f"From {PRIOR_HYGIENE_LIBRARY_SIZE} everyday Bayesian priors, show only the {len(selected)} most relevant checks for this decision.",
        "checks": selected,
    }


def build_sensitivity(method: str, prior_payload: dict, evidence: list[dict], actions: list[dict], observations: dict | None, sensitivity: dict) -> dict:
    prior_scenarios = sensitivity.get("prior_probabilities") or default_prior_scenarios(prior_payload)
    prior_scenarios = [clamp(float(value), 1e-6, 1 - 1e-6) for value in prior_scenarios]
    lr_power_factors = sensitivity.get("lr_power_factors") or [0.75, 1.0, 1.25]
    lr_power_factors = [float(value) for value in lr_power_factors]

    scenario_results = []
    recommended_actions = []
    for prior_probability in prior_scenarios:
        if method.startswith("beta-binomial") and prior_payload.get("mode") == "beta" and observations is not None:
            ess = float(prior_payload["equivalent_sample_size"])
            alpha = prior_probability * ess
            beta = (1.0 - prior_probability) * ess
            posterior = apply_beta_binomial({"alpha": alpha, "beta": beta}, observations)
            base_probability = posterior["posterior_probability"]
            if evidence:
                for lr_power in lr_power_factors:
                    posterior_probability, _, _, _ = apply_odds_update(base_probability, evidence, lr_power=lr_power)
                    evaluated = evaluate_actions(actions, posterior_probability) if actions else []
                    recommended = evaluated[0]["name"] if evaluated else None
                    recommended_actions.append(recommended)
                    scenario_results.append(
                        {
                            "scenario_type": "combined",
                            "prior_probability": round_float(prior_probability),
                            "beta_binomial_probability": round_float(base_probability),
                            "lr_power": round_float(lr_power),
                            "posterior_probability": round_float(posterior_probability),
                            "recommended_action": recommended,
                        }
                    )
            else:
                posterior_probability = base_probability
                evaluated = evaluate_actions(actions, posterior_probability) if actions else []
                recommended = evaluated[0]["name"] if evaluated else None
                recommended_actions.append(recommended)
                scenario_results.append(
                    {
                        "scenario_type": "prior",
                        "prior_probability": round_float(prior_probability),
                        "posterior_probability": round_float(posterior_probability),
                        "credible_interval": [round_float(value) for value in posterior["credible_interval"]],
                        "recommended_action": recommended,
                    }
                )
        else:
            for lr_power in lr_power_factors:
                posterior_probability, _, _, _ = apply_odds_update(prior_probability, evidence, lr_power=lr_power)
                evaluated = evaluate_actions(actions, posterior_probability) if actions else []
                recommended = evaluated[0]["name"] if evaluated else None
                recommended_actions.append(recommended)
                scenario_results.append(
                    {
                        "scenario_type": "combined",
                        "prior_probability": round_float(prior_probability),
                        "lr_power": round_float(lr_power),
                        "posterior_probability": round_float(posterior_probability),
                        "recommended_action": recommended,
                    }
                )

    posterior_values = [float(item["posterior_probability"]) for item in scenario_results]
    unique_actions = {item for item in recommended_actions if item}
    if len(unique_actions) <= 1:
        stability = "stable"
    elif len(unique_actions) == 2:
        stability = "mixed"
    else:
        stability = "unstable"

    return {
        "scenarios": scenario_results,
        "posterior_range": [round_float(min(posterior_values)), round_float(max(posterior_values))],
        "conclusion_stability": {
            "stable": "稳定",
            "mixed": "混合",
            "unstable": "不稳定",
        }[stability],
        "conclusion_stability_code": stability,
    }


def choose_method(request: dict, prior_payload: dict) -> str:
    method = request.get("method", "auto")
    if method != "auto":
        return method
    observations = request.get("observations") or {}
    if observations.get("trials") is not None and observations.get("successes") is not None and prior_payload.get("mode") == "beta":
        return "beta-binomial"
    return "odds-update"


def build_report(request: dict) -> dict:
    warnings = []
    prior_payload = build_prior(request["prior"], warnings)
    method = choose_method(request, prior_payload)
    evidence = [
        {
            **item,
            "name": localize_text(item.get("name"), "zh"),
            "summary": localize_text(item.get("summary"), "zh"),
            "notes": localize_text(item.get("notes"), "zh"),
        }
        for item in request.get("evidence", [])
    ]
    actions = [
        {
            **item,
            "name": localize_text(item.get("name"), "zh"),
        }
        for item in request.get("actions", [])
    ]
    observations = request.get("observations") or None

    if method == "beta-binomial":
        if observations is None:
            raise ValueError("beta-binomial method requires observations.trials and observations.successes")
        posterior_block = apply_beta_binomial(prior_payload, observations)
        beta_posterior_probability = posterior_block["posterior_probability"]
        calculation_log = list(posterior_block["calculation_log"])
        posterior_probability = beta_posterior_probability
        posterior_interval = posterior_block["credible_interval"]
        prior_probability = float(prior_payload["probability"])
        if evidence:
            method = "beta-binomial+odds"
            posterior_probability, evidence_log, prior_odds, posterior_odds = apply_odds_update(beta_posterior_probability, evidence)
            posterior_interval = update_interval_with_evidence(posterior_interval, evidence)
            posterior_block.update(
                {
                    "beta_binomial_probability": beta_posterior_probability,
                    "prior_odds_before_evidence": prior_odds,
                    "posterior_odds_after_evidence": posterior_odds,
                    "posterior_probability": posterior_probability,
                    "credible_interval": posterior_interval,
                }
            )
            calculation_log.append(
                {
                    "step": "odds_update_after_beta_binomial",
                    "starting_probability": round_float(beta_posterior_probability),
                    "prior_odds": round_float(prior_odds),
                    "posterior_odds": round_float(posterior_odds),
                }
            )
            calculation_log.extend(evidence_log)
            warnings.append("在 Beta-binomial 更新之后又追加了证据更新，请确认这些证据没有被重复包含在已观测计数中。")
    elif method == "odds-update":
        prior_probability = float(prior_payload["probability"])
        posterior_probability, calculation_log, prior_odds, posterior_odds = apply_odds_update(prior_probability, evidence)
        posterior_interval = None
        posterior_block = {
            "prior_odds": prior_odds,
            "posterior_odds": posterior_odds,
            "posterior_probability": posterior_probability,
        }
    else:
        raise ValueError(f"Unsupported method: {method}")

    if any(item.get("quality") in {"D", "E"} for item in evidence):
        warnings.append("部分证据较弱或较间接，后验判断应视为更脆弱。")
    if any(float(item.get("dependency_discount", 1.0)) < 1.0 for item in evidence):
        warnings.append("至少有一条证据因依赖关系被折扣处理，不应把这次更新理解为完全独立证据的简单叠加。")
    if request.get("high_risk_domain"):
        warnings.append("本报告仅用于辅助决策，不替代持证专业人士的正式判断。")

    sensitivity = build_sensitivity(method, prior_payload, evidence, actions, observations, request.get("sensitivity") or {})
    if posterior_interval is None:
        posterior_interval = sensitivity["posterior_range"]
        warnings.append("这里的后验区间来自赔率更新下的敏感性包络，并非严格统计意义上的可信区间。")

    evaluated_actions = evaluate_actions(actions, posterior_probability) if actions else []
    recommendation = evaluated_actions[0]["name"] if evaluated_actions else "先继续收集信息"
    next_info = information_value_hint(
        evaluated_actions,
        posterior_probability,
        localize_list((request.get("next_information") or {}).get("candidates", []), "zh"),
    )
    prior_hygiene = build_prior_hygiene_checks(
        request,
        prior_payload,
        evidence,
        actions,
        evaluated_actions,
        sensitivity,
        warnings,
        next_info,
    )
    conversation_process = build_conversation_process(
        request,
        float(prior_payload["probability"]),
        posterior_probability,
        recommendation,
    )
    confidence_code = recommendation_confidence(warnings, sensitivity["conclusion_stability_code"], evidence)
    confidence = confidence_label_zh(confidence_code)

    summary_sentence = f"当前后验概率约为 {posterior_probability:.1%}；在现有证据下，更优的行动是 {recommendation}。"
    if conversation_process:
        status_text = "已经达到可决策状态" if conversation_process["decision_ready"] else "还未达到可决策状态"
        summary_sentence = f"{summary_sentence} 多轮对话后的判断是：{status_text}。"
        if not conversation_process["decision_ready"]:
            warnings.append("多轮对话后仍有关键缺口，建议先补充剩余信息，再进入最终决策。")

    return {
        "title": localize_text(request["title"], "zh"),
        "method": method,
        "summary": {
            "posterior_probability": round_float(posterior_probability),
            "credible_interval": [round_float(value) for value in posterior_interval] if posterior_interval else None,
            "recommendation": recommendation,
            "confidence": confidence,
            "confidence_code": confidence_code,
            "decision_ready": conversation_process["decision_ready"] if conversation_process else None,
            "decision_readiness": conversation_process["final_readiness"] if conversation_process else None,
            "decision_status": conversation_process["status"] if conversation_process else None,
            "one_sentence": summary_sentence,
        },
        "question": {
            "decision_question": localize_text(request.get("question"), "zh"),
            "hypothesis": localize_text(request.get("hypothesis"), "zh"),
            "time_horizon": localize_text(request.get("time_horizon"), "zh"),
            "decision_deadline": localize_text(request.get("decision_deadline"), "zh"),
            "success_metric": localize_text(request.get("success_metric"), "zh"),
            "domain": localize_text(request.get("domain"), "zh"),
            "high_risk_domain": request.get("high_risk_domain", False),
        },
        "prior": {
            "probability": round_float(prior_payload["probability"]),
            "distribution": (
                f"Beta({round_float(prior_payload['alpha'])}, {round_float(prior_payload['beta'])})"
                if prior_payload.get("alpha") is not None and prior_payload.get("beta") is not None
                else "point prior"
            ),
            "source_summary": prior_payload.get("source_summary", []),
            "source_quality": localize_text(prior_payload.get("source_quality"), "zh"),
            "confidence": localize_text(prior_payload.get("confidence"), "zh"),
            "equivalent_sample_size": round_float(prior_payload.get("equivalent_sample_size")),
            "credible_interval": [round_float(value) for value in prior_payload.get("credible_interval", [])] or None,
        },
        "evidence": [
            {
                "name": item.get("name"),
                "summary": item.get("summary"),
                "quality": item.get("quality"),
                "direction": direction_label_zh(item.get("direction", "support")),
                "direction_code": item.get("direction", "support"),
                "likelihood_ratio": round_float(float(item.get("likelihood_ratio", 1.0))),
                "dependency_discount": round_float(float(item.get("dependency_discount", 1.0))),
                "notes": item.get("notes"),
            }
            for item in evidence
        ],
        "posterior": {
            "probability": round_float(posterior_probability),
            "credible_interval": [round_float(value) for value in posterior_interval] if posterior_interval else None,
            "method": method,
            "details": {key: normalize_value(value) for key, value in posterior_block.items()},
        },
        "decision": {
            "recommended_action": recommendation,
            "expected_value_ranking": evaluated_actions,
            "decision_ready": conversation_process["decision_ready"] if conversation_process else None,
            "decision_readiness": conversation_process["final_readiness"] if conversation_process else None,
            "decision_status": conversation_process["status"] if conversation_process else None,
            "remaining_open_questions": conversation_process["open_questions"] if conversation_process else [],
            "reason": (
                "当前基于后验概率的期望值比较，支持把这个行动作为首选。"
                if evaluated_actions
                else "没有提供行动效用参数，因此报告无法直接比较行动优先级。"
            ),
        },
        "sensitivity": sensitivity,
        "natural_frequency": natural_frequency(prior_payload["probability"], posterior_probability),
        "next_information": next_info,
        "prior_hygiene": prior_hygiene,
        "warnings": warnings,
        "conversation_process": conversation_process,
        "calculation_log": calculation_log,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a Bayesian decision-report payload from a structured request.")
    parser.add_argument("input_json", help="Path to the structured decision request JSON file.")
    parser.add_argument("--output-json", help="Optional output path. Defaults to stdout when omitted.")
    args = parser.parse_args()

    try:
        request = load_request(Path(args.input_json))
        report = build_report(request)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(2) from exc

    if args.output_json:
        save_output(Path(args.output_json), report)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
