#!/usr/bin/env python3
"""Build a self-contained HTML/SVG visual pack from a tutorial visual spec."""

from __future__ import annotations

import argparse
import html
import json
import math
import re
from pathlib import Path
from typing import Any


DEFAULT_THEME = {
    "accent": "#1f4e79",
    "accent2": "#6f7682",
    "ink": "#111827",
    "muted": "#5f6673",
    "surface": "#f5f4ed",
    "border": "#d9d6cc",
    "paper": "#faf9f5",
    "canvas": "#f2f0ea",
    "node": "#faf9f5",
    "node_alt": "#f7f5ee",
    "grid": "#e8e4da",
    "strong_border": "#c9c4b8",
}


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug


def normalize_node(node: Any) -> dict[str, str]:
    if isinstance(node, dict):
        label = node.get("label") or node.get("title") or node.get("name") or "Item"
        detail = node.get("detail") or node.get("description") or ""
        return {"label": str(label), "detail": str(detail)}
    text = str(node)
    if "：" in text:
        label, detail = text.split("：", 1)
        return {"label": label.strip(), "detail": detail.strip()}
    if ":" in text:
        label, detail = text.split(":", 1)
        return {"label": label.strip(), "detail": detail.strip()}
    return {"label": text, "detail": ""}


def wrap_text(value: str, max_chars: int = 20, max_lines: int = 3) -> list[str]:
    text = " ".join(str(value).split())
    if not text:
        return [""]
    words = text.split(" ")
    lines: list[str] = []
    current = ""
    if len(words) == 1:
        chunks = [text[i : i + max_chars] for i in range(0, len(text), max_chars)]
        return chunks[:max_lines]
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:max_lines]


def text_block(
    x: float,
    y: float,
    value: str,
    max_chars: int,
    size: int,
    color: str,
    weight: int = 600,
    anchor: str = "middle",
    max_lines: int = 3,
) -> str:
    lines = wrap_text(value, max_chars=max_chars, max_lines=max_lines)
    out = [f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" fill="{color}" font-size="{size}" font-weight="{weight}">']
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else size + 4
        out.append(f'<tspan x="{x:.1f}" dy="{dy}">{esc(line)}</tspan>')
    out.append("</text>")
    return "".join(out)


def theme_color(theme: dict[str, str], key: str) -> str:
    return theme.get(key) or DEFAULT_THEME[key]


def secondary_accent(theme: dict[str, str]) -> str:
    accent = theme_color(theme, "accent")
    accent2 = theme_color(theme, "accent2")
    return accent2 if accent2.lower() != accent.lower() else "#6f7682"


def chapter_number(module_id: str) -> int | None:
    match = re.search(r"(?:module|chapter)-0*([0-9]+)$", module_id, re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def chapter_label(module_id: str, padded: bool = False) -> str:
    number = chapter_number(module_id)
    if number is None:
        return module_id.upper() if module_id else "章节"
    if padded:
        return f"第{number:02d}章"
    return f"第{number}章"


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    theme: dict[str, str],
    width: int = 2,
    arrow: bool = False,
    color: str | None = None,
) -> str:
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    stroke = color or theme_color(theme, "accent")
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round"{marker}/>'


def curved_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    theme: dict[str, str],
    bend: float = 36,
    width: int = 2,
    arrow: bool = True,
    color: str | None = None,
) -> str:
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1
    nx, ny = -dy / length, dx / length
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    cx, cy = mx + nx * bend, my + ny * bend
    marker = ' marker-end="url(#arrow)"' if arrow else ""
    stroke = color or theme_color(theme, "accent")
    return f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{stroke}" stroke-width="{width}" stroke-linecap="round"{marker}/>'


def node_card(
    x: float,
    y: float,
    w: float,
    h: float,
    node: dict[str, str],
    theme: dict[str, str],
    index: int | None = None,
    accent: bool = False,
    fill: str | None = None,
) -> str:
    node_fill = fill or (theme_color(theme, "node_alt") if accent else theme_color(theme, "node"))
    border = theme_color(theme, "accent") if accent else theme_color(theme, "border")
    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" fill="{node_fill}" stroke="{border}" stroke-width="1.4" filter="url(#soft-shadow)"/>'
    ]
    if accent:
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="5" rx="2.5" fill="{theme_color(theme, "accent")}"/>')
    text_x = x + 22
    if index is not None:
        parts.append(
            f'<circle cx="{x + 26:.1f}" cy="{y + 28:.1f}" r="15" fill="{theme_color(theme, "accent")}"/>'
        )
        parts.append(
            text_block(x + 26, y + 33, str(index), 2, 12, "#ffffff", 800, max_lines=1)
        )
        text_x = x + 52
    parts.append(text_block(text_x, y + 33, node["label"], 15, 17, theme_color(theme, "ink"), 760, anchor="start", max_lines=2))
    if node["detail"]:
        parts.append(text_block(x + 22, y + h - 28, node["detail"], 22, 12, theme_color(theme, "muted"), 560, anchor="start", max_lines=2))
    return "\n  ".join(parts)


def svg_shell(
    title: str,
    body: str,
    theme: dict[str, str],
    module_id: str = "",
    summary: str = "",
    width: int = 1200,
    height: int = 675,
) -> str:
    kicker = esc(chapter_label(module_id))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}" font-family="Noto Sans SC, Source Han Sans SC, PingFang SC, system-ui, sans-serif">
  <defs>
    <filter id="soft-shadow" x="-8%" y="-12%" width="116%" height="128%">
      <feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#111827" flood-opacity="0.08"/>
    </filter>
    <pattern id="dot-grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <circle cx="1.5" cy="1.5" r="1.2" fill="{theme_color(theme, "grid")}" opacity="0.85"/>
    </pattern>
    <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
      <path d="M2,2 L10,6 L2,10" fill="none" stroke="{theme_color(theme, "accent")}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
    </marker>
  </defs>
  <rect width="{width}" height="{height}" fill="{theme_color(theme, "surface")}"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="{theme_color(theme, "paper")}" stroke="{theme_color(theme, "border")}" stroke-width="1.6"/>
  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="url(#dot-grid)" opacity="0.34"/>
  <rect x="72" y="206" width="1056" height="390" rx="16" fill="{theme_color(theme, "surface")}" stroke="{theme_color(theme, "border")}" stroke-width="1.1" opacity="0.82"/>
  <text x="84" y="82" fill="{theme_color(theme, "accent")}" font-size="12" font-weight="800" letter-spacing="1.2">{kicker}</text>
  <text x="1116" y="82" text-anchor="end" fill="{theme_color(theme, "muted")}" font-size="11" font-weight="700" letter-spacing="1">教学图示</text>
  <rect x="84" y="100" width="54" height="4" rx="2" fill="{theme_color(theme, "accent")}"/>
  {text_block(84, 136, title, 28, 31, theme_color(theme, "ink"), 800, anchor="start", max_lines=2)}
  {text_block(84, 178, summary, 58, 15, theme_color(theme, "muted"), 500, anchor="start", max_lines=2) if summary else ""}
  {body}
</svg>
'''


def module_nodes(module: dict[str, Any]) -> list[dict[str, str]]:
    nodes = module.get("nodes") or []
    return [normalize_node(node) for node in nodes][:8]


def draw_flow(module: dict[str, Any], theme: dict[str, str]) -> str:
    nodes = module_nodes(module)[:6] or [{"label": "Step", "detail": ""}]
    count = len(nodes)
    y = 334
    card_h = 148
    gap = 18
    usable_w = 1012
    card_w = (usable_w - gap * (count - 1)) / count
    start_x = 94
    parts = [
        f'<text x="94" y="252" fill="{theme_color(theme, "muted")}" font-size="12" font-weight="700">从输入到结果的最短学习路径</text>',
        f'<line x1="94" y1="274" x2="1106" y2="274" stroke="{theme_color(theme, "border")}" stroke-width="1.4"/>',
    ]
    for index, node in enumerate(nodes):
        x = start_x + index * (card_w + gap)
        if index < count - 1:
            parts.append(line(x + card_w + 8, y + card_h / 2, x + card_w + gap - 8, y + card_h / 2, theme, 3, True))
        parts.append(node_card(x, y, card_w, card_h, node, theme, index=index + 1, accent=index in {0, count - 1}))
    return svg_shell(str(module.get("title", "Flow")), "\n  ".join(parts), theme, str(module.get("id", "")), str(module.get("summary", "")))


def draw_layers(module: dict[str, Any], theme: dict[str, str]) -> str:
    nodes = module_nodes(module)[:6] or [{"label": "Layer", "detail": ""}]
    count = len(nodes)
    start_y = 236
    layer_h = min(54, (330 - (count - 1) * 12) / count)
    parts = [
        f'<text x="168" y="222" fill="{theme_color(theme, "muted")}" font-size="12" font-weight="700">越往下越接近底层机制，越往上越接近用户可见结果</text>',
    ]
    for index, node in enumerate(nodes):
        y = start_y + index * (layer_h + 12)
        x = 168 + index * 28
        w = 864 - index * 56
        fill = theme_color(theme, "node") if index % 2 == 0 else theme_color(theme, "node_alt")
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{layer_h:.1f}" rx="8" fill="{fill}" stroke="{theme_color(theme, "border")}" stroke-width="1.4" filter="url(#soft-shadow)"/>')
        parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="7" height="{layer_h:.1f}" rx="3.5" fill="{theme_color(theme, "accent")}"/>')
        parts.append(text_block(x + 30, y + layer_h / 2 + 7, node["label"], 18, 19, theme_color(theme, "ink"), 780, anchor="start", max_lines=1))
        if node["detail"]:
            parts.append(text_block(x + w - 24, y + layer_h / 2 + 5, node["detail"], 22, 13, theme_color(theme, "muted"), 560, anchor="end", max_lines=1))
    return svg_shell(str(module.get("title", "Layers")), "\n  ".join(parts), theme, str(module.get("id", "")), str(module.get("summary", "")))


def draw_comparison(module: dict[str, Any], theme: dict[str, str]) -> str:
    columns = module.get("columns")
    if not isinstance(columns, list) or len(columns) < 2:
        nodes = module_nodes(module)
        midpoint = max(1, math.ceil(len(nodes) / 2))
        columns = [
            {"title": "Before", "items": [node["label"] for node in nodes[:midpoint]]},
            {"title": "After", "items": [node["label"] for node in nodes[midpoint:]]},
        ]
    columns = columns[:2]
    parts = []
    colors = [theme_color(theme, "accent"), secondary_accent(theme)]
    for index, column in enumerate(columns):
        x = 94 + index * 520
        title = str(column.get("title", f"Option {index + 1}")) if isinstance(column, dict) else f"Option {index + 1}"
        items = column.get("items", []) if isinstance(column, dict) else []
        parts.append(f'<rect x="{x}" y="222" width="492" height="344" rx="12" fill="{theme_color(theme, "node")}" stroke="{theme_color(theme, "border")}" stroke-width="1.6"/>')
        parts.append(f'<rect x="{x}" y="222" width="492" height="58" rx="12" fill="{colors[index]}" opacity="0.96"/>')
        parts.append(f'<rect x="{x}" y="262" width="492" height="18" fill="{colors[index]}" opacity="0.96"/>')
        parts.append(text_block(x + 28, 258, title, 24, 21, "#ffffff", 800, anchor="start", max_lines=1))
        for item_index, item in enumerate(items[:5]):
            y = 324 + item_index * 46
            parts.append(f'<circle cx="{x + 36}" cy="{y - 6}" r="6" fill="{colors[index]}"/>')
            parts.append(text_block(x + 56, y, str(item), 38, 17, theme_color(theme, "ink"), 600, anchor="start", max_lines=2))
    return svg_shell(str(module.get("title", "Comparison")), "\n  ".join(parts), theme, str(module.get("id", "")), str(module.get("summary", "")))


def draw_cycle(module: dict[str, Any], theme: dict[str, str]) -> str:
    nodes = module_nodes(module)[:6] or [{"label": "Iterate", "detail": ""}]
    count = len(nodes)
    cx, cy = 600, 408
    positions = [
        (600, 244),
        (840, 318),
        (748, 508),
        (452, 508),
        (360, 318),
        (600, 560),
    ][:count]
    parts = [
        f'<circle cx="{cx}" cy="{cy}" r="168" fill="none" stroke="{theme_color(theme, "border")}" stroke-width="1.2" stroke-dasharray="5 9"/>',
    ]
    centers = [(x, y) for x, y in positions]
    card_w, card_h = 172, 84

    def edge_point(source: tuple[float, float], target: tuple[float, float]) -> tuple[float, float]:
        dx, dy = target[0] - source[0], target[1] - source[1]
        if dx == 0 and dy == 0:
            return source
        sx = (card_w / 2 + 8) / abs(dx) if dx else float("inf")
        sy = (card_h / 2 + 8) / abs(dy) if dy else float("inf")
        scale = min(sx, sy)
        return source[0] + dx * scale, source[1] + dy * scale

    for index, source in enumerate(centers):
        target = centers[(index + 1) % count]
        sx, sy = edge_point(source, target)
        ex, ey = edge_point(target, source)
        parts.append(curved_line(sx, sy, ex, ey, theme, bend=22, width=2, arrow=True, color=secondary_accent(theme)))
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="86" fill="{theme_color(theme, "node_alt")}" stroke="{theme_color(theme, "border")}" stroke-width="1.4" filter="url(#soft-shadow)"/>')
    center = str(module.get("center") or module.get("title") or "Cycle")
    parts.append(text_block(cx, cy - 4, center, 16, 20, theme_color(theme, "ink"), 800, max_lines=2))
    for index, node in enumerate(nodes):
        x, y = positions[index]
        parts.append(node_card(x - card_w / 2, y - card_h / 2, card_w, card_h, node, theme, index=index + 1, accent=index == 0))
    return svg_shell(str(module.get("title", "Cycle")), "\n  ".join(parts), theme, str(module.get("id", "")), str(module.get("summary", "")))


def draw_matrix(module: dict[str, Any], theme: dict[str, str]) -> str:
    quadrants = module.get("quadrants")
    if not isinstance(quadrants, list) or len(quadrants) < 4:
        nodes = module_nodes(module)[:4]
        quadrants = [{"title": node["label"], "detail": node["detail"]} for node in nodes]
    quadrants = quadrants[:4]
    coords = [(104, 236), (624, 236), (104, 424), (624, 424)]
    parts = [
        f'<line x1="600" y1="220" x2="600" y2="588" stroke="{theme_color(theme, "strong_border")}" stroke-width="2"/>',
        f'<line x1="86" y1="406" x2="1114" y2="406" stroke="{theme_color(theme, "strong_border")}" stroke-width="2"/>',
    ]
    for index, quadrant in enumerate(quadrants):
        x, y = coords[index]
        title = str(quadrant.get("title", f"Quadrant {index + 1}")) if isinstance(quadrant, dict) else str(quadrant)
        detail = str(quadrant.get("detail", "")) if isinstance(quadrant, dict) else ""
        node = {"label": title, "detail": detail}
        parts.append(node_card(x, y, 472, 142, node, theme, index=index + 1, accent=index == 0))
        if detail:
            pass
    return svg_shell(str(module.get("title", "Matrix")), "\n  ".join(parts), theme, str(module.get("id", "")), str(module.get("summary", "")))


def draw_mindmap(module: dict[str, Any], theme: dict[str, str]) -> str:
    nodes = module_nodes(module)[:6] or [{"label": "Idea", "detail": ""}]
    cx, cy = 600, 408
    positions = [
        (210, 246),
        (802, 246),
        (164, 372),
        (848, 372),
        (210, 498),
        (802, 498),
    ][: len(nodes)]
    parts = []
    for x, y in positions:
        end_x = x + 204 if x < cx else x
        parts.append(line(cx, cy, end_x, y + 43, theme, 2, False, theme_color(theme, "border")))
    parts.append(f'<rect x="452" y="350" width="296" height="116" rx="14" fill="{theme_color(theme, "accent")}"/>')
    center = str(module.get("center") or module.get("title") or "Core idea")
    parts.append(text_block(cx, cy - 4, center, 18, 21, "#ffffff", 800, max_lines=2))
    for index, node in enumerate(nodes):
        x, y = positions[index]
        parts.append(node_card(x, y, 204, 86, node, theme, index=None, accent=index == 0))
    return svg_shell(str(module.get("title", "Mindmap")), "\n  ".join(parts), theme, str(module.get("id", "")), str(module.get("summary", "")))


def draw_network(module: dict[str, Any], theme: dict[str, str]) -> str:
    nodes = module_nodes(module)[:6] or [{"label": "Node", "detail": ""}]
    positions = [
        (184, 260),
        (486, 232),
        (812, 260),
        (930, 470),
        (540, 512),
        (226, 470),
    ][: len(nodes)]
    parts = []
    edges = module.get("edges")
    if isinstance(edges, list) and edges:
        for edge in edges[:10]:
            if not isinstance(edge, dict):
                continue
            try:
                source = int(str(edge.get("source", "1")).replace("node-", "")) - 1
                target = int(str(edge.get("target", "1")).replace("node-", "")) - 1
            except ValueError:
                continue
            if source < 0 or target < 0 or source >= len(positions) or target >= len(positions):
                continue
            x1, y1 = positions[source]
            x2, y2 = positions[target]
            parts.append(line(x1 + 102, y1 + 43, x2 + 102, y2 + 43, theme, 2, True, secondary_accent(theme)))
    else:
        for index in range(len(positions) - 1):
            x1, y1 = positions[index]
            x2, y2 = positions[index + 1]
            parts.append(line(x1 + 102, y1 + 43, x2 + 102, y2 + 43, theme, 2, True, secondary_accent(theme)))
    for index, node in enumerate(nodes):
        x, y = positions[index]
        parts.append(node_card(x, y, 204, 86, node, theme, index=index + 1, accent=index == 0))
    return svg_shell(str(module.get("title", "Network")), "\n  ".join(parts), theme, str(module.get("id", "")), str(module.get("summary", "")))


def draw_timeline(module: dict[str, Any], theme: dict[str, str]) -> str:
    nodes = module_nodes(module)[:6] or [{"label": "Event", "detail": ""}]
    count = len(nodes)
    y = 410
    start_x = 128
    end_x = 1072
    step = 0 if count == 1 else (end_x - start_x) / (count - 1)
    parts = [line(start_x, y, end_x, y, theme, 3, False)]
    for index, node in enumerate(nodes):
        x = start_x + index * step
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{theme_color(theme, "accent")}"/>')
        card_y = 252 if index % 2 == 0 else 456
        parts.append(line(x, y, x, card_y + (88 if index % 2 == 0 else 0), theme, 1, False, theme_color(theme, "border")))
        parts.append(node_card(x - 88, card_y, 176, 88, node, theme, index=index + 1, accent=index == 0))
    return svg_shell(str(module.get("title", "Timeline")), "\n  ".join(parts), theme, str(module.get("id", "")), str(module.get("summary", "")))


def draw_module(module: dict[str, Any], theme: dict[str, str]) -> str:
    diagram_type = str(module.get("diagram_type", "mindmap")).lower()
    if diagram_type == "flow":
        return draw_flow(module, theme)
    if diagram_type == "layer":
        return draw_layers(module, theme)
    if diagram_type == "comparison":
        return draw_comparison(module, theme)
    if diagram_type == "cycle":
        return draw_cycle(module, theme)
    if diagram_type == "matrix":
        return draw_matrix(module, theme)
    if diagram_type == "network":
        return draw_network(module, theme)
    if diagram_type == "timeline":
        return draw_timeline(module, theme)
    return draw_mindmap(module, theme)


def build_index(spec: dict[str, Any], modules: list[dict[str, str]], theme: dict[str, str]) -> str:
    title = esc(spec.get("title", "Tutorial Visual Pack"))
    nav_items = []
    sections = []
    for module in modules:
        nav_items.append(f'<a href="#{esc(module["id"])}"><span>{esc(chapter_label(module["id"]))}</span>{esc(module["title"])}</a>')
        sections.append(
            f'''<section class="chapter" id="{esc(module["id"])}">
  <figure class="artboard">
    <img src="{esc(module["file"])}" alt="{esc(chapter_label(module["id"]))}：{esc(module["title"])} diagram">
  </figure>
  <p class="caption">{esc(module["caption"])}</p>
</section>'''
        )
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{
      --ink: {theme["ink"]};
      --muted: {theme["muted"]};
      --accent: {theme["accent"]};
      --accent2: {theme["accent2"]};
      --border: {theme["border"]};
      --surface: {theme["surface"]};
      --paper: {theme["paper"]};
      --canvas: {theme_color(theme, "canvas")};
      --grid: {theme_color(theme, "grid")};
    }}
    * {{
      box-sizing: border-box;
    }}
    html {{
      scroll-behavior: smooth;
    }}
    body {{
      margin: 0;
      background:
        radial-gradient(circle at 1px 1px, var(--grid) 1px, transparent 1.4px),
        var(--canvas);
      background-size: 26px 26px;
      color: var(--ink);
      font-family: "Noto Sans SC", "Source Han Sans SC", "PingFang SC", system-ui, sans-serif;
    }}
    .shell {{
      display: grid;
      grid-template-columns: minmax(260px, 330px) minmax(0, 1fr);
      gap: clamp(24px, 4vw, 56px);
      max-width: 1440px;
      margin: 0 auto;
      padding: clamp(24px, 4vw, 56px);
    }}
    .rail {{
      position: sticky;
      top: 32px;
      align-self: start;
      min-height: calc(100vh - 64px);
      padding-right: 20px;
      border-right: 1px solid var(--border);
    }}
    .rail h1 {{
      margin: 0;
      padding-bottom: 18px;
      border-bottom: 2px solid var(--accent);
      font-size: clamp(1.45rem, 2.3vw, 2.35rem);
      line-height: 1.12;
      letter-spacing: 0;
    }}
    .rail nav {{
      display: grid;
      gap: 10px;
      margin-top: 24px;
    }}
    .rail a {{
      color: var(--muted);
      text-decoration: none;
      font-size: 0.94rem;
      line-height: 1.35;
    }}
    .rail a:hover {{
      color: var(--ink);
    }}
    .rail span {{
      display: block;
      margin-bottom: 3px;
      color: var(--accent);
      font-family: "IBM Plex Mono", "SFMono-Regular", monospace;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .workspace {{
      display: grid;
      gap: clamp(34px, 5vw, 72px);
    }}
    .chapter {{
      scroll-margin-top: 32px;
    }}
    p {{
      margin: 0;
      line-height: 1.6;
    }}
    .artboard {{
      margin: 0;
      aspect-ratio: 16 / 9;
      border: 1px solid var(--border);
      border-radius: 10px;
      background: var(--paper);
      overflow: hidden;
    }}
    img {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .caption {{
      margin: 12px auto 0;
      max-width: 820px;
      color: var(--muted);
      text-align: center;
      font-size: 0.95rem;
    }}
    @media (max-width: 860px) {{
      .shell {{
        display: block;
        padding: 20px;
      }}
      .rail {{
        position: sticky;
        top: 0;
        z-index: 2;
        min-height: auto;
        margin: -20px -20px 28px;
        padding: 18px 20px 16px;
        border-right: 0;
        border-bottom: 1px solid var(--border);
        background: color-mix(in srgb, var(--canvas) 92%, white);
      }}
      .rail h1 {{
        font-size: 1.6rem;
      }}
      .rail nav {{
        grid-auto-flow: column;
        grid-auto-columns: minmax(140px, 1fr);
        overflow-x: auto;
        gap: 16px;
      }}
      .workspace {{
        gap: 42px;
      }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <aside class="rail">
      <h1>{title}</h1>
      <nav>
        {"".join(nav_items)}
      </nav>
    </aside>
    <main class="workspace">
      {"".join(sections)}
    </main>
  </div>
</body>
</html>
'''


def demo_spec() -> dict[str, Any]:
    return {
        "title": "Demo Tutorial Visual Pack",
        "chapters": [
            {
                "id": "chapter-01",
                "title": "From Confusion To Model",
                "diagram_type": "flow",
                "summary": "A beginner path from raw topic to first useful example.",
                "nodes": ["Raw topic", "Key question", "Mental model", "First example"],
                "caption": "A useful tutorial turns confusion into a small successful action.",
            },
            {
                "id": "chapter-02",
                "title": "The Learning Stack",
                "diagram_type": "layer",
                "summary": "A topic can be taught as stacked levels of understanding.",
                "nodes": ["Goal", "Workflow", "Concepts", "Tools", "Tradeoffs"],
                "caption": "The learner needs to know where each new idea belongs.",
            },
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build tutorial chapter visuals as SVG files plus an index HTML page.")
    parser.add_argument("spec", nargs="?", help="Path to visual-spec.json.")
    parser.add_argument("output_dir", nargs="?", help="Directory for SVG and HTML outputs.")
    parser.add_argument("--demo", action="store_true", help="Generate a demo visual pack without a spec file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.demo:
        spec = demo_spec()
        output_dir = Path(args.output_dir or args.spec or "visuals-demo").resolve()
    else:
        if not args.spec or not args.output_dir:
            raise SystemExit("Usage: build_visual_pack.py visual-spec.json output_dir/ or use --demo output_dir/")
        spec_path = Path(args.spec).resolve()
        if not spec_path.exists():
            raise SystemExit(f"Spec file not found: {spec_path}")
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        output_dir = Path(args.output_dir).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)
    theme = {**DEFAULT_THEME, **(spec.get("theme") or {})}
    raw_modules = spec.get("chapters") or spec.get("modules") or []
    if not raw_modules:
        raise SystemExit("No chapters found in visual spec.")

    index_modules: list[dict[str, str]] = []
    used_ids: set[str] = set()
    for number, module in enumerate(raw_modules, start=1):
        module = dict(module)
        raw_id = str(module.get("id") or "")
        module_id = slugify(raw_id) or f"chapter-{number:02d}"
        if module_id in used_ids:
            module_id = f"{module_id}-{number:02d}"
        used_ids.add(module_id)
        module["id"] = module_id
        title = str(module.get("title") or module_id.replace("-", " ").title())
        svg = draw_module(module, theme)
        file_name = f"{module_id}.svg"
        (output_dir / file_name).write_text(svg, encoding="utf-8")
        index_modules.append(
            {
                "id": module_id,
                "title": title,
                "summary": str(module.get("summary") or ""),
                "caption": str(module.get("caption") or ""),
                "file": file_name,
            }
        )

    index_html = build_index(spec, index_modules, theme)
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")
    print(f"Visual pack written to {output_dir}")
    for module in index_modules:
        print(f"- {module['file']}")


if __name__ == "__main__":
    main()
