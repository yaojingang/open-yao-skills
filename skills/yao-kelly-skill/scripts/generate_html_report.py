#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any


def load_payload(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def esc(value: Any) -> str:
    if value is None:
        return "-"
    return html.escape(str(value), quote=True)


def pct(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value) * 100:.1f}%"


def amount(value: Any, resource_unit: str = "currency") -> str:
    if value is None:
        return "-"
    normalized = (resource_unit or "currency").lower()
    if normalized in ("cny", "rmb", "yuan", "¥"):
        return f"¥{float(value):,.0f}"
    if normalized == "currency":
        return f"{float(value):,.0f}"
    return f"{float(value):,.1f} {resource_unit}"


def action_label(value: str) -> str:
    labels = {
        "skip": "不投入",
        "observe-or-tiny-test": "观察或极小试探",
        "small": "小仓位",
        "medium": "中等仓位",
        "large": "高暴露",
    }
    return labels.get(value, value)


def action_headline(value: str) -> str:
    headlines = {
        "skip": "先不投入，把机会放进观察名单",
        "observe-or-tiny-test": "只做极小试探，不要正式加码",
        "small": "先小规模试，不要大规模加码",
        "medium": "可以中等投入，但必须守住上限",
        "large": "优势较强，也要按上限分批执行",
    }
    return headlines.get(value, "先按保守方案执行")


def action_guidance(value: str) -> str:
    guidance = {
        "skip": "当前信息下，最理性的动作是先不投入。继续收集证据，等胜率、回报或下行损失更清楚后再重新计算。",
        "observe-or-tiny-test": "可以用很小的试验验证判断，但不要把它当成正式投入。这个级别更像买信息，而不是追求收益。",
        "small": "可以小规模开始，重点是验证假设。先按建议上限执行，后续只有在真实数据变好时再加码。",
        "medium": "可以作为一个正式投入项，但不要超过报告里的总暴露上限，并保留足够现金或机动资源。",
        "large": "模型显示优势较强，但仍然要分批执行。Kelly 的意义是控制长期风险，不是鼓励一次性压满。",
    }
    return guidance.get(value, "按保守建议执行，并在关键假设变化时重新计算。")


def report_context(report: dict[str, Any]) -> dict[str, str]:
    context = report.get("context") or {}
    objective = report.get("objective") or "当前决策"
    return {
        "background": context.get(
            "background",
            f"这份报告处理的是一个典型的投入决策：{objective}。用户面对的不是单纯要不要做，而是在机会、风险和资源保留之间找到一个可执行比例。",
        ),
        "tension": context.get(
            "tension",
            "真正的矛盾在于：机会看起来有收益，但收益并不确定；如果投入太少，可能错过增长，如果投入太多，又可能在判断错误时消耗过多资源。",
        ),
        "question": context.get(
            "question",
            "用户的核心疑问是：在当前信息还不完美的情况下，到底应该投入多少，才既能参与机会，又不会因为过度自信而承担不必要的损失？",
        ),
        "solution": context.get(
            "solution",
            "解决方案不是拍脑袋定预算，而是先估计每个机会的收益和失败损失，再用 Kelly 思路得到理论投入比例，最后根据置信度、相关性和保留资源要求把它压成保守执行上限。",
        ),
    }


def render_story(report: dict[str, Any], primary_action: str) -> str:
    context = report_context(report)
    return f"""
      <section class="section story-section" id="story">
        <h2>背景、矛盾和问题</h2>
        <div class="story-grid">
          <article>
            <span>背景</span>
            <p>{esc(context["background"])}</p>
          </article>
          <article>
            <span>矛盾点</span>
            <p>{esc(context["tension"])}</p>
          </article>
          <article>
            <span>用户疑惑</span>
            <p>{esc(context["question"])}</p>
          </article>
          <article>
            <span>建议方案</span>
            <p>{esc(context["solution"])} 当前动作判断是：{esc(action_headline(primary_action))}。</p>
          </article>
        </div>
      </section>
    """


def render_kelly_principle() -> str:
    return """
      <section class="section principle-section" id="principle">
        <h2>凯利公式在这里解决什么</h2>
        <div class="principle-copy">
          <p>凯利公式的核心不是让人冒险，而是回答一个更具体的问题：当一个机会长期看起来有优势时，投入多少比例才不会因为一次判断错误而伤到整体资源。</p>
          <p>它会把“胜率或场景概率”“赚的时候赚多少”“亏的时候亏多少”放在一起看。理论 Kelly 给出的是增长最大化比例，但现实里概率常常不准、机会之间会相关、执行还有摩擦，所以报告会把理论值再压成保守建议。</p>
          <p>因此，这份报告里的保守 Kelly 更像一个执行上限：可以低于它，通常不应该高于它。真正的重点是先控制长期生存，再追求增长。</p>
        </div>
      </section>
    """


def plain_reason(item: dict[str, Any]) -> str:
    full = float(item.get("full_kelly_fraction") or 0.0)
    recommended = float(item.get("recommended_fraction") or 0.0)
    confidence = str(item.get("confidence_level", "unknown"))
    dependence = str(item.get("dependence", "unknown"))
    if recommended <= 0:
        return "模型没有给出正向投入比例，所以当前不值得配置。"
    haircut = 1 - (recommended / full) if full > 0 else 0
    return (
        f"理论 Kelly 是 {pct(full)}，但因为置信度是 {confidence}、相关性是 {dependence}，"
        f"执行建议被压到 {pct(recommended)}。这表示可以试，但不应该按理论值直接加满。"
        if haircut > 0.2
        else f"理论 Kelly 和执行建议差距不大，说明当前折扣较轻，但仍需遵守暴露上限。"
    )


def pick_primary_action(opportunities: list[dict[str, Any]]) -> str:
    order = ["large", "medium", "small", "observe-or-tiny-test", "skip"]
    for action in order:
        if any(item.get("action_class") == action for item in opportunities):
            return action
    return "skip"


def render_metric(label: str, value: str, hint: str = "") -> str:
    return f"""
      <div class="metric">
        <span>{esc(label)}</span>
        <strong>{esc(value)}</strong>
        <small>{esc(hint)}</small>
      </div>
    """


def render_bar(label: str, value: float, tone: str = "") -> str:
    width = max(0.0, min(100.0, value * 100))
    return f"""
      <div class="bar-row">
        <div class="bar-label"><span>{esc(label)}</span><strong>{width:.1f}%</strong></div>
        <div class="bar-track"><div class="bar-fill {esc(tone)}" style="width:{width:.2f}%"></div></div>
      </div>
    """


def render_scenarios(opportunity: dict[str, Any]) -> str:
    rows = []
    for scenario in opportunity.get("scenarios", []):
        rows.append(
            f"""
            <tr>
              <td>{esc(scenario.get("name"))}</td>
              <td>{pct(scenario.get("probability"))}</td>
              <td>{pct(scenario.get("return_multiple"))}</td>
              <td>{esc(scenario.get("source", "estimated"))}</td>
            </tr>
            """
        )
    if not rows:
        return ""
    return f"""
      <table>
        <thead>
          <tr><th>场景</th><th>概率</th><th>每 1 单位净回报</th><th>来源</th></tr>
        </thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    """


def render_action_plan(
    report: dict[str, Any],
    opportunities: list[dict[str, Any]],
    resource_unit: str,
    primary_action: str,
) -> str:
    summary = report.get("summary", {})
    recommended_total = amount(summary.get("recommended_total_amount"), resource_unit)
    total_fraction = pct(summary.get("recommended_total_fraction"))
    rows = []
    for item in opportunities:
        rows.append(
            f"""
            <li>
              <strong>{esc(item.get("name"))}: {amount(item.get("recommended_amount"), resource_unit)} ({pct(item.get("recommended_fraction"))})</strong>
              <span>{esc(action_guidance(item.get("action_class", "skip")))}</span>
              <small>{esc(plain_reason(item))}</small>
            </li>
            """
        )
    return f"""
      <section class="section plain-summary" id="plain-summary">
        <h2>普通人版结论</h2>
        <div class="plain-lead">
          <strong>{esc(action_headline(primary_action))}</strong>
          <span>本次建议总投入 {esc(recommended_total)}，约占可用资源的 {esc(total_fraction)}。剩下的资源先保留，不要因为单次机会看起来不错就提前用掉。</span>
        </div>
        <ol class="action-list">{''.join(rows)}</ol>
        <div class="watch-box">
          <strong>什么时候重新计算</strong>
          <span>如果实际转化、成本、成功率、最差情况损失或机会之间的相关性明显变化，就不要沿用这份比例，重新跑一次。</span>
        </div>
      </section>
    """


def render_opportunities(opportunities: list[dict[str, Any]], resource_unit: str) -> str:
    blocks = []
    amount_hint = (
        "基于资金口径"
        if resource_unit.lower() in ("currency", "cny", "rmb", "yuan", "¥")
        else "基于资源口径"
    )
    for item in opportunities:
        recommended = float(item.get("recommended_fraction") or 0.0)
        full = float(item.get("full_kelly_fraction") or 0.0)
        notes = "".join(f"<li>{esc(note)}</li>" for note in item.get("notes", []))
        blocks.append(
            f"""
            <article class="opportunity">
              <div class="opportunity-head">
                <div>
                  <h3>{esc(item.get("name"))}</h3>
                  <p>{esc(item.get("formula_path"))}</p>
                </div>
                <span class="pill">{esc(action_label(item.get("action_class", "skip")))}</span>
              </div>
              <div class="plain-note">
                <strong>怎么做</strong>
                <span>{esc(action_guidance(item.get("action_class", "skip")))}</span>
              </div>
              <div class="allocation-grid">
                {render_bar("理论 Kelly，不建议直接照做", full, "raw")}
                {render_bar("保守建议，可作为执行上限", recommended, "safe")}
              </div>
              <div class="mini-grid">
                {render_metric("建议投入", amount(item.get("recommended_amount"), resource_unit), amount_hint)}
                {render_metric("期望收益/单位", pct(item.get("expected_return_per_unit")), "未扣除所有现实摩擦")}
                {render_metric("折扣系数", f"{float(item.get('fractional_multiplier') or 0):.2f}x", "置信度折扣")}
                {render_metric("相关性折扣", f"{float(item.get('dependence_multiplier') or 0):.2f}x", esc(item.get("dependence")))}
              </div>
              {render_scenarios(item)}
              <ul class="notes">{notes}</ul>
            </article>
            """
        )
    return "".join(blocks)


def render_round_log(round_log: list[dict[str, Any]], readiness: dict[str, Any]) -> str:
    if not round_log:
        stop_reason = "; ".join(readiness.get("stop_reasons", [])) or "当前信息足够形成保守建议"
        round_log = [
            {
                "round": 1,
                "stage": "初始结构化",
                "summary": "从样例 brief 直接生成 Kelly 报告。",
                "readiness": readiness.get("score"),
                "stop_reason": stop_reason,
            }
        ]

    items = []
    for entry in round_log:
        items.append(
            f"""
            <li>
              <strong>Round {esc(entry.get("round", "-"))}: {esc(entry.get("stage", "更新"))}</strong>
              <span>{esc(entry.get("summary") or entry.get("user_input_summary") or "")}</span>
              <em>Readiness: {pct(entry.get("readiness")) if entry.get("readiness") is not None else "-"}</em>
              <small>{esc(entry.get("stop_reason") or entry.get("next_question") or "")}</small>
            </li>
            """
        )
    return f"<ol class=\"timeline\">{''.join(items)}</ol>"


def render_html(payload: dict[str, Any]) -> str:
    report = payload.get("report", payload)
    summary = report.get("summary", {})
    readiness = summary.get("decision_readiness", {})
    opportunities = report.get("opportunities", [])
    resource_unit = str(report.get("resource_unit", "currency"))
    capital_label = "资金口径" if resource_unit.lower() in ("currency", "cny", "rmb", "yuan", "¥") else "资源口径"
    primary_action = pick_primary_action(opportunities)
    missing_questions = readiness.get("missing_questions", [])
    stop_reasons = readiness.get("stop_reasons", [])
    next_questions = "".join(
        f"<li>{esc(item.get('question'))}</li>" for item in missing_questions
    ) or "<li>当前没有高影响缺口。</li>"
    stop_reason_html = "".join(f"<li>{esc(item)}</li>" for item in stop_reasons) or "<li>动作级别已经稳定。</li>"
    generated_at = report.get("generated_at", "")

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kelly Allocation Report</title>
  <style>
    :root {{
      --ink: #1e2722;
      --muted: #63706a;
      --line: #d7ded6;
      --paper: #fbfaf6;
      --panel: #ffffff;
      --green: #1e7f5c;
      --blue: #225d8f;
      --rust: #a54f2b;
      --gold: #c29b2e;
      --shadow: 0 16px 40px rgba(22, 31, 26, 0.10);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        linear-gradient(180deg, rgba(30,127,92,0.08), transparent 320px),
        var(--paper);
      font-family: "Avenir Next", "Helvetica Neue", "PingFang SC", sans-serif;
      line-height: 1.55;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: rgba(251, 250, 246, 0.92);
      backdrop-filter: blur(14px);
      position: sticky;
      top: 0;
      z-index: 2;
    }}
    .nav {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 14px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 700;
    }}
    .brand-mark {{
      width: 28px;
      height: 28px;
      border-radius: 7px;
      background: conic-gradient(from 220deg, var(--green), var(--blue), var(--gold), var(--green));
    }}
    button {{
      border: 1px solid var(--line);
      background: var(--panel);
      color: var(--ink);
      border-radius: 7px;
      padding: 8px 12px;
      font: inherit;
      cursor: pointer;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 22px 60px;
    }}
    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
      gap: 22px;
      align-items: stretch;
      margin-bottom: 24px;
    }}
    .summary-panel, .decision-panel, .opportunity, .section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}
    .summary-panel {{
      padding: 28px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: 38px;
      line-height: 1.12;
      letter-spacing: 0;
    }}
    h2, h3 {{ letter-spacing: 0; }}
    p {{ color: var(--muted); margin: 0; }}
    .decision-panel {{
      padding: 22px;
      display: grid;
      gap: 16px;
    }}
    .action {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 16px;
    }}
    .action strong {{
      font-size: 30px;
      color: var(--green);
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-height: 30px;
      border: 1px solid rgba(30, 127, 92, 0.24);
      background: rgba(30, 127, 92, 0.10);
      color: var(--green);
      border-radius: 999px;
      padding: 4px 10px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }}
    .mini-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin: 16px 0;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fffefa;
      min-width: 0;
    }}
    .metric span, .metric small {{
      display: block;
      color: var(--muted);
      font-size: 12px;
    }}
    .metric strong {{
      display: block;
      margin: 4px 0;
      font-size: 22px;
      overflow-wrap: anywhere;
    }}
    .section {{
      padding: 22px;
      margin-top: 18px;
    }}
    .story-section {{
      border-top: 5px solid var(--blue);
    }}
    .story-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    .story-grid article {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 15px;
      background: #fffefa;
    }}
    .story-grid span {{
      display: inline-block;
      margin-bottom: 8px;
      color: var(--blue);
      font-weight: 700;
    }}
    .story-grid p {{
      color: var(--muted);
    }}
    .plain-summary {{
      border-top: 5px solid var(--green);
    }}
    .plain-lead {{
      display: grid;
      gap: 8px;
      padding: 16px;
      border: 1px solid rgba(30, 127, 92, 0.24);
      border-radius: 8px;
      background: rgba(30, 127, 92, 0.08);
      margin-bottom: 14px;
    }}
    .plain-lead strong {{
      font-size: 22px;
    }}
    .plain-lead span {{
      color: var(--muted);
    }}
    .action-list {{
      display: grid;
      gap: 12px;
      padding-left: 0;
      list-style: none;
    }}
    .action-list li {{
      display: grid;
      gap: 5px;
      padding: 14px 0;
      border-bottom: 1px solid var(--line);
    }}
    .action-list span, .action-list small {{
      color: var(--muted);
    }}
    .watch-box, .plain-note {{
      display: grid;
      gap: 5px;
      border-left: 3px solid var(--gold);
      padding: 10px 12px;
      background: #fffdf2;
      color: var(--muted);
    }}
    .watch-box strong, .plain-note strong {{
      color: var(--ink);
    }}
    .plain-note {{
      margin-bottom: 14px;
    }}
    .principle-section {{
      border-top: 5px solid var(--gold);
    }}
    .principle-copy {{
      display: grid;
      gap: 12px;
      max-width: 920px;
    }}
    .section h2, .opportunity h3 {{
      margin: 0 0 10px;
    }}
    .opportunity {{
      padding: 20px;
      margin-top: 14px;
    }}
    .opportunity-head {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
      margin-bottom: 14px;
    }}
    .opportunity-head p {{
      font-size: 13px;
    }}
    .allocation-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .bar-row {{ display: grid; gap: 8px; }}
    .bar-label {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      font-size: 13px;
      color: var(--muted);
    }}
    .bar-label strong {{ color: var(--ink); }}
    .bar-track {{
      height: 14px;
      background: #e9eee8;
      border-radius: 999px;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      background: var(--green);
    }}
    .bar-fill.raw {{ background: var(--rust); }}
    .bar-fill.safe {{ background: var(--green); }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      font-size: 13px;
    }}
    th, td {{
      text-align: left;
      padding: 9px 8px;
      border-bottom: 1px solid var(--line);
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
    }}
    .split {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }}
    ul, ol {{ padding-left: 20px; }}
    li {{ margin: 8px 0; }}
    .notes {{
      color: var(--muted);
      font-size: 13px;
      margin-bottom: 0;
    }}
    .timeline {{
      list-style: none;
      padding-left: 0;
      display: grid;
      gap: 12px;
    }}
    .timeline li {{
      border-left: 3px solid var(--blue);
      padding-left: 14px;
      margin: 0;
      display: grid;
      gap: 3px;
    }}
    .timeline span, .timeline small, .timeline em {{
      color: var(--muted);
      font-style: normal;
    }}
    footer {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 0 22px 34px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 860px) {{
      .hero, .split, .allocation-grid, .metrics, .mini-grid, .story-grid {{
        grid-template-columns: 1fr;
      }}
      h1 {{ font-size: 30px; }}
      .nav {{ align-items: flex-start; }}
      .action {{ align-items: flex-start; flex-direction: column; }}
    }}
    @media print {{
      header button {{ display: none; }}
      body {{ background: white; }}
      header {{ position: static; }}
      .summary-panel, .decision-panel, .opportunity, .section {{
        box-shadow: none;
        break-inside: avoid;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="nav">
      <div class="brand"><span class="brand-mark"></span><span>Kelly Allocation Report</span></div>
      <button onclick="window.print()">Print / Save PDF</button>
    </div>
  </header>
  <main>
    <section class="hero">
      <div class="summary-panel">
        <h1>{esc(action_headline(primary_action))}：总投入 {pct(summary.get("recommended_total_fraction"))}</h1>
        <p>目标：{esc(report.get("objective"))}。先看行动建议，再看计算依据；Full Kelly 是理论值，真正执行看保守建议。</p>
        <div class="metrics">
          {render_metric(capital_label, amount(report.get("capital_base"), resource_unit), "capital base")}
          {render_metric("建议总投入", amount(summary.get("recommended_total_amount"), resource_unit), "recommended")}
          {render_metric("决策成熟度", pct(readiness.get("score")), esc(readiness.get("band")))}
          {render_metric("总暴露上限", pct(summary.get("total_exposure_cap")), "cap")}
        </div>
      </div>
      <aside class="decision-panel">
        <div class="action">
          <div>
            <p>Action Class</p>
            <strong>{esc(action_label(primary_action))}</strong>
          </div>
          <span class="pill">{esc(report.get("case_type"))}</span>
        </div>
        {render_bar("Recommended Exposure", float(summary.get("recommended_total_fraction") or 0), "safe")}
        {render_bar("Cash Reserve", float(summary.get("min_cash_reserve_ratio") or 0), "raw")}
        <p>生成时间：{esc(generated_at)}</p>
      </aside>
    </section>

    {render_story(report, primary_action)}

    {render_action_plan(report, opportunities, resource_unit, primary_action)}

    {render_kelly_principle()}

    <section class="section" id="opportunities">
      <h2>具体方法和解释</h2>
      {render_opportunities(opportunities, resource_unit)}
    </section>

    <section class="section split" id="readiness">
      <div>
        <h2>为什么停止追问</h2>
        <ul>{stop_reason_html}</ul>
      </div>
      <div>
        <h2>剩余高影响问题</h2>
        <ul>{next_questions}</ul>
      </div>
    </section>

    <section class="section" id="log">
      <h2>轮次日志</h2>
      {render_round_log(report.get("round_log", []), readiness)}
    </section>
  </main>
  <footer>
    Kelly sizing is a decision-sizing framework, not licensed investment, legal, or tax advice. Treat assumption-heavy inputs as provisional.
  </footer>
</body>
</html>
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a Kelly JSON report as standalone HTML.")
    parser.add_argument("--input", required=True, help="Path to JSON report.")
    parser.add_argument("--output", required=True, help="Path to HTML output.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = load_payload(args.input)
    html_text = render_html(payload)
    Path(args.output).write_text(html_text, encoding="utf-8")
    print(json.dumps({"ok": True, "output": args.output}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
