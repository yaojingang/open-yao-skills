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


def money(value: Any) -> str:
    if value is None:
        return "-"
    return f"{float(value):,.0f}"


def action_label(value: str) -> str:
    labels = {
        "skip": "不投入",
        "observe-or-tiny-test": "观察或极小试探",
        "small": "小仓位",
        "medium": "中等仓位",
        "large": "高暴露",
    }
    return labels.get(value, value)


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


def render_opportunities(opportunities: list[dict[str, Any]]) -> str:
    blocks = []
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
              <div class="allocation-grid">
                {render_bar("Full Kelly", full, "raw")}
                {render_bar("Conservative Kelly", recommended, "safe")}
              </div>
              <div class="mini-grid">
                {render_metric("建议金额", money(item.get("recommended_amount")), "基于资金口径")}
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
      .hero, .split, .allocation-grid, .metrics, .mini-grid {{
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
        <h1>建议采用 {esc(action_label(primary_action))}，总投入 {pct(summary.get("recommended_total_fraction"))}</h1>
        <p>目标：{esc(report.get("objective"))}。本报告使用保守版 Kelly，将原始 Kelly、置信度折扣、相关性折扣和总暴露上限分开呈现。</p>
        <div class="metrics">
          {render_metric("资金口径", money(report.get("capital_base")), "capital base")}
          {render_metric("建议总金额", money(summary.get("recommended_total_amount")), "recommended")}
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

    <section class="section" id="opportunities">
      <h2>机会分配</h2>
      {render_opportunities(opportunities)}
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
