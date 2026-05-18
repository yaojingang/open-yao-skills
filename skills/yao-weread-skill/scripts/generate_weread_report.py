#!/usr/bin/env python3
# Copyright © 2026 姚金刚. All rights reserved.
# Project: yao-weread-skill
# Created by: 姚金刚
# Date: 2026-05-16
# X: https://x.com/yaojingang

"""Generate a personal or synthetic WeRead visualization report.

The script intentionally stores only local artifacts and never writes the API key.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover - Python < 3.9 fallback is not expected here.
    ZoneInfo = None


API_URL = "https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION = "1.0.3"
TZ_NAME = "Asia/Shanghai"
TZ = ZoneInfo(TZ_NAME) if ZoneInfo else None

BRAND = "#1B365D"
BRAND_LIGHT = "#2D5A8A"
WARM = "#b69b66"
SAGE = "#7d8b70"
RUST = "#a45d4f"
STONE = "#87867f"
PALETTE = [BRAND, WARM, SAGE, RUST, BRAND_LIGHT, "#6f675a", "#9d8062", "#596b7f"]
TREEMAP_LABEL_FORMATTER = (
    "function(params){"
    "var name=String(params.name||'').replace(/\\s+/g,'');"
    "if(!name){return '';}"
    "if(name.indexOf('/')>-1){return name.split('/').filter(Boolean).slice(0,2).join('\\n');}"
    "if(/^[A-Za-z0-9._-]+$/.test(name)){return name.length>10?name.slice(0,10):name;}"
    "if(name.length<=2){return name;}"
    "if(name.length<=4){return name.slice(0,2)+'\\n'+name.slice(2);}"
    "if(name.length<=6){return name.slice(0,3)+'\\n'+name.slice(3);}"
    "return name.slice(0,3)+'\\n'+name.slice(3,6);"
    "}"
)
TREEMAP_LABEL_LAYOUT = (
    "function(params){"
    "var rect=params&&params.rect;"
    "if(rect&&(rect.width<34||rect.height<24)){return {hide:true};}"
    "return {};"
    "}"
)
TREEMAP_TOOLTIP_FORMATTER = (
    "function(params){"
    "var name=String(params.name||'');"
    "var value=params.value==null?0:params.value;"
    "return name+': '+value;"
    "}"
)


class WeReadError(RuntimeError):
    pass


class WeReadClient:
    def __init__(self, api_key: str, timeout: int = 30) -> None:
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "yao-weread-skill/0.1",
            }
        )

    def call(self, api_name: str, **params: Any) -> dict[str, Any]:
        payload = {"api_name": api_name, "skill_version": SKILL_VERSION}
        payload.update(params)
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = self.session.post(API_URL, data=json.dumps(payload, ensure_ascii=False), timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                if "upgrade_info" in data:
                    message = data["upgrade_info"].get("message", "WeRead skill requires upgrade")
                    raise WeReadError(message)
                if data.get("errcode", 0) not in (0, None):
                    message = data.get("errmsg") or data.get("message") or data.get("errstr") or str(data.get("errcode"))
                    raise WeReadError(f"{api_name}: {message}")
                return data
            except Exception as exc:  # noqa: BLE001 - retry wrapper.
                last_error = exc
                time.sleep(0.4 * (attempt + 1))
        raise WeReadError(f"{api_name} failed after retries: {last_error}")


@dataclass
class Range:
    start: date
    end: date

    @property
    def label(self) -> str:
        return f"{self.start.isoformat()} 至 {self.end.isoformat()}"


def now_date() -> date:
    return datetime.now(TZ).date() if TZ else datetime.now().date()


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def default_range(years: int, start: str | None, end: str | None) -> Range:
    end_date = parse_date(end) or now_date()
    start_date = parse_date(start)
    if not start_date:
        start_date = end_date - timedelta(days=365 * years)
    if start_date > end_date:
        raise SystemExit("--start cannot be after --end")
    return Range(start_date, end_date)


def to_ts(day: date) -> int:
    dt = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=TZ)
    return int(dt.timestamp())


def from_ts(value: Any) -> date | None:
    try:
        ts = int(value)
    except Exception:
        return None
    return datetime.fromtimestamp(ts, TZ).date() if TZ else datetime.fromtimestamp(ts).date()


def month_iter(start: date, end: date) -> list[date]:
    cur = date(start.year, start.month, 1)
    last = date(end.year, end.month, 1)
    out: list[date] = []
    while cur <= last:
        out.append(cur)
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return out


def year_iter(start: date, end: date) -> list[int]:
    return list(range(start.year, end.year + 1))


def month_label(day: date) -> str:
    return f"{day.year}-{day.month:02d}"


def hours(seconds: float | int | None) -> float:
    return round((seconds or 0) / 3600, 2)


def minutes(seconds: float | int | None) -> float:
    return round((seconds or 0) / 60, 1)


def format_duration(seconds: float | int | None) -> str:
    total = int(seconds or 0)
    h, rem = divmod(total, 3600)
    m = rem // 60
    if h:
        return f"{h}小时{m}分钟"
    return f"{m}分钟"


def parse_count_text(value: Any) -> int:
    if value is None:
        return 0
    match = re.search(r"[\d,]+", str(value))
    return int(match.group(0).replace(",", "")) if match else 0


def parse_duration_text(value: Any) -> int:
    text = str(value or "")
    h = re.search(r"(\d+(?:\.\d+)?)\s*小时", text)
    m = re.search(r"(\d+(?:\.\d+)?)\s*分钟", text)
    s = re.search(r"(\d+(?:\.\d+)?)\s*秒", text)
    return int(float(h.group(1)) * 3600 if h else 0) + int(float(m.group(1)) * 60 if m else 0) + int(float(s.group(1)) if s else 0)


def safe_title(book: dict[str, Any] | None, fallback: str = "") -> str:
    if not book:
        return fallback
    for key in ("title", "name", "bookName", "titleText"):
        value = book.get(key)
        if value:
            return str(value).strip()
    return fallback


def read_longest_identity(row: dict[str, Any]) -> dict[str, Any] | None:
    """Return a real book/album identity from readLongest, or None for anonymous rows."""
    for key in ("book", "albumInfo", "bookInfo"):
        info = row.get(key) or {}
        title = safe_title(info)
        if not title:
            continue
        return {
            "title": title,
            "author": info.get("author") or info.get("authorName") or "",
            "bookId": info.get("bookId") or info.get("albumId") or "",
        }
    return None


def fetch_monthly_stats(client: WeReadClient, report_range: Range) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    monthly: list[dict[str, Any]] = []
    daily_counter: defaultdict[str, int] = defaultdict(int)
    for month_start in month_iter(report_range.start, report_range.end):
        base_day = date(month_start.year, month_start.month, min(15, 28))
        data = client.call("/readdata/detail", mode="monthly", baseTime=to_ts(base_day))
        label = month_label(month_start)
        read_times = data.get("readTimes") or {}
        filtered_seconds = 0
        filtered_days = 0
        for raw_ts, raw_seconds in read_times.items():
            day = from_ts(raw_ts)
            if not day or not (report_range.start <= day <= report_range.end):
                continue
            seconds = int(raw_seconds or 0)
            filtered_seconds += seconds
            if seconds >= 60:
                filtered_days += 1
            daily_counter[day.isoformat()] += seconds
        seconds = filtered_seconds if read_times else int(data.get("totalReadTime") or 0)
        read_days = filtered_days if read_times else int(data.get("readDays") or 0)
        stat_counts: dict[str, int] = {}
        for item in data.get("readStat") or []:
            stat_counts[str(item.get("stat") or "")] = parse_count_text(item.get("counts"))
        monthly.append(
            {
                "label": label,
                "baseTime": data.get("baseTime"),
                "totalReadTime": int(data.get("totalReadTime") or 0),
                "rangeReadTime": seconds,
                "readDays": read_days,
                "serviceReadDays": int(data.get("readDays") or 0),
                "dayAverageReadTime": int(data.get("dayAverageReadTime") or 0),
                "readStat": stat_counts,
                "readLongest": data.get("readLongest") or [],
                "preferCategory": data.get("preferCategory") or [],
                "preferBooks": data.get("preferBooks") or [],
            }
        )
    daily = [{"date": key, "seconds": value} for key, value in sorted(daily_counter.items())]
    return monthly, daily


def fetch_annual_stats(client: WeReadClient, report_range: Range) -> list[dict[str, Any]]:
    annual: list[dict[str, Any]] = []
    for year in year_iter(report_range.start, report_range.end):
        data = client.call("/readdata/detail", mode="annually", baseTime=to_ts(date(year, 1, 15)))
        data["_year"] = year
        annual.append(data)
    return annual


def fetch_notebooks(client: WeReadClient) -> list[dict[str, Any]]:
    notebooks: list[dict[str, Any]] = []
    last_sort: int | None = None
    seen: set[str] = set()
    while True:
        params: dict[str, Any] = {"count": 100}
        if last_sort:
            params["lastSort"] = last_sort
        data = client.call("/user/notebooks", **params)
        books = data.get("books") or []
        if not books:
            break
        for item in books:
            key = str(item.get("bookId") or item.get("book", {}).get("bookId") or "")
            if key and key not in seen:
                notebooks.append(item)
                seen.add(key)
        if not data.get("hasMore"):
            break
        next_sort = books[-1].get("sort")
        if not next_sort or next_sort == last_sort:
            break
        last_sort = int(next_sort)
    return notebooks


def fetch_reviews(client: WeReadClient, book_id: str) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    synckey: int | None = None
    for _ in range(20):
        params: dict[str, Any] = {"bookid": book_id, "count": 50}
        if synckey:
            params["synckey"] = synckey
        data = client.call("/review/list/mine", **params)
        reviews.extend(data.get("reviews") or [])
        if not data.get("hasMore"):
            break
        next_key = data.get("synckey")
        if not next_key or next_key == synckey:
            break
        synckey = int(next_key)
    return reviews


def fetch_note_detail(client: WeReadClient, notebook: dict[str, Any]) -> dict[str, Any]:
    book_id = str(notebook.get("bookId") or notebook.get("book", {}).get("bookId") or "")
    result = {"bookId": book_id, "highlights": [], "reviews": [], "errors": []}
    if not book_id:
        result["errors"].append("missing bookId")
        return result
    try:
        bookmarks = client.call("/book/bookmarklist", bookId=book_id)
        result["highlights"] = bookmarks.get("updated") or []
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"bookmarklist: {exc}")
    try:
        result["reviews"] = fetch_reviews(client, book_id)
    except Exception as exc:  # noqa: BLE001
        result["errors"].append(f"reviews: {exc}")
    return result


def notebook_total(item: dict[str, Any]) -> int:
    return int(item.get("reviewCount") or 0) + int(item.get("noteCount") or 0) + int(item.get("bookmarkCount") or 0)


def book_info_from_notebook(item: dict[str, Any]) -> dict[str, Any]:
    return item.get("book") or {}


def shelf_book_date(book: dict[str, Any]) -> date | None:
    return from_ts(book.get("readUpdateTime") or book.get("updateTime"))


STOPWORDS = {
    "一个",
    "一种",
    "一样",
    "一些",
    "不是",
    "不能",
    "不会",
    "可以",
    "因为",
    "所以",
    "如果",
    "但是",
    "这个",
    "那个",
    "这些",
    "那些",
    "自己",
    "我们",
    "他们",
    "你们",
    "没有",
    "什么",
    "怎么",
    "只是",
    "已经",
    "可能",
    "应该",
    "需要",
    "时候",
    "事情",
    "问题",
    "就是",
    "对于",
    "通过",
    "进行",
    "以及",
    "或者",
    "而且",
    "其中",
    "这种",
    "这样",
    "为什么",
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "into",
}
STOP_CHARS = set("的一是在了和与及或而也就都很更最被把让使将对中上下来去里者之其并还不我你他她它")
BAD_TERM_PREFIXES = (
    "如果",
    "因为",
    "因此",
    "那么",
    "这个",
    "那个",
    "这些",
    "那些",
    "所有",
    "任何",
    "每个",
    "一个",
    "一种",
    "一些",
    "我们",
    "你们",
    "他们",
    "它们",
    "为了",
    "对于",
    "通过",
    "必须",
    "能够",
    "可以",
    "应该",
    "需要",
    "不要",
    "不能",
    "不会",
    "不是",
    "没有",
)
BAD_TERM_SUFFIXES = (
    "一个",
    "一种",
    "一些",
    "这个",
    "那个",
    "这些",
    "那些",
    "时候",
    "问题",
    "东西",
    "方式",
    "事情",
    "因此",
    "那么",
    "所有",
    "必须",
    "能够",
    "可以",
    "应该",
    "需要",
    "我们",
    "他们",
    "它们",
)
GENERIC_TERMS = {
    "如果你",
    "如果我",
    "有一个",
    "每个人",
    "大多数",
    "大多数人",
    "所有",
    "能够",
    "必须",
    "因此",
    "那么",
    "如何",
    "开始",
    "真正",
    "知道",
    "同时",
    "认为",
    "人们",
    "可能会",
    "不知道",
    "有什么",
    "不同",
    "任何",
    "非常",
    "为他们",
    "第一个",
    "第二",
    "部分",
    "大部分",
    "这一点",
    "我们能",
    "不需要",
    "个问题",
    "他人",
    "只有",
    "无法",
    "努力",
    "别人",
    "小时",
    "分钟",
    "个小时",
    "个方面",
    "家公司",
    "生活方",
    "做的事",
    "尽可能",
    "有可能",
    "我认为",
    "告诉我",
    "为自己",
    "然后",
    "甚至",
    "越来越",
    "比如",
    "才能",
    "完全",
    "不断",
    "拥有",
    "容易",
    "发生",
    "变得",
    "重要",
    "方式",
    "东西",
    "获得",
    "成为",
    "产生",
    "提醒我",
    "验证框架",
    "每周复盘",
}
DOMAIN_TERMS = {
    "AI创业",
    "人工智能",
    "大模型",
    "智能体",
    "提示词",
    "产品经理",
    "产品市场匹配",
    "客户反馈",
    "个人品牌",
    "商业模式",
    "商业化",
    "生活方式",
    "第一性原理",
    "批判性思维",
    "解决问题",
    "价值观",
    "注意力",
    "算力成本",
    "融资节奏",
    "增长飞轮",
    "客户访谈",
    "评测体系",
    "数据飞轮",
    "网络效应",
    "开源模型",
    "组织设计",
    "现金流",
    "护城河",
    "分发渠道",
    "创始人",
    "北极星指标",
    "工作流",
    "工作流重构",
    "模型评测体系",
    "定价",
    "渠道",
    "留存",
    "马拉松",
    "奥尔特曼",
    "马斯克",
    "日本史",
    "创业",
    "管理",
    "产品",
    "训练",
    "跑步",
    "身体",
    "运动",
    "健康",
    "用户",
    "网络",
    "公司",
    "系统",
    "学习",
    "目标",
    "心智",
    "决策",
    "模型",
    "团队",
    "企业",
    "社会",
    "技术",
    "市场",
    "增长",
    "内容",
    "思维",
    "习惯",
    "科学",
    "大脑",
    "肌肉",
    "速度",
    "力量",
}


def extract_terms(texts: list[str], limit: int = 120) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for text in texts:
        clean = re.sub(r"https?://\S+", " ", text or "")
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_+-]{2,}", clean):
            token = word.lower()
            if token not in STOPWORDS:
                counter[token] += 2
        for seq in re.findall(r"[\u4e00-\u9fff]{2,}", clean):
            domain_hit = False
            for term in DOMAIN_TERMS:
                if term in seq:
                    counter[term] += 6
                    domain_hit = True
            if domain_hit:
                continue
            if len(seq) <= 6 and valid_cn_term(seq):
                counter[seq] += term_weight(seq)
            for n in (4, 3, 2):
                for idx in range(0, len(seq) - n + 1):
                    token = seq[idx : idx + n]
                    if valid_cn_term(token):
                        counter[token] += term_weight(token)
    trimmed = remove_substring_noise(counter)
    return [{"name": word, "value": count} for word, count in trimmed.most_common(limit)]


def valid_cn_term(token: str) -> bool:
    if token in DOMAIN_TERMS:
        return True
    if token in STOPWORDS:
        return False
    if token in GENERIC_TERMS:
        return False
    if len(token) < 2:
        return False
    if any(mark in token for mark in ("您", "你", "我们", "他们", "它们")):
        return False
    if any(token.startswith(prefix) for prefix in BAD_TERM_PREFIXES):
        return False
    if any(token.endswith(suffix) for suffix in BAD_TERM_SUFFIXES):
        return False
    if token not in DOMAIN_TERMS and any(token in term and token != term for term in DOMAIN_TERMS):
        return False
    if any(ch in STOP_CHARS for ch in token):
        return False
    return True


def term_weight(token: str) -> int:
    if token in DOMAIN_TERMS:
        return 8
    if len(token) >= 5:
        return 5
    if len(token) >= 3:
        return 3
    return 1


def remove_substring_noise(counter: Counter[str]) -> Counter[str]:
    common = counter.most_common(400)
    result: Counter[str] = Counter()
    for word, count in common:
        larger = [(w, c) for w, c in common if word in w and w != word and len(w) > len(word)]
        if larger:
            best_larger_count = max(c for _, c in larger)
            if len(word) <= 4 and best_larger_count >= count * 0.65:
                continue
            if len(word) <= 2 and best_larger_count >= count * 0.45:
                continue
        result[word] = count
    return result


def bucket(value: int, edges: list[int]) -> str:
    previous = 0
    for edge in edges:
        if value <= edge:
            return f"{previous + 1}-{edge}"
        previous = edge
    return f"{edges[-1]}+"


def clean_quote_text(text: str) -> str:
    clean = re.sub(r"https?://\S+", " ", text or "")
    clean = re.sub(r"\s+", " ", clean).strip()
    clean = clean.strip(" \t\r\n\"'“”‘’")
    return clean


def split_highlight_sentences(text: str) -> list[str]:
    clean = clean_quote_text(text)
    if not clean:
        return []
    pieces = re.findall(r"[^。！？!?；;\n]+[。！？!?；;]?", clean)
    if not pieces:
        pieces = [clean]
    sentences: list[str] = []
    for piece in pieces:
        sentence = clean_quote_text(piece)
        if len(sentence) < 10:
            continue
        if len(sentence) > 180:
            shorter_parts = [clean_quote_text(part) for part in re.split(r"[，,：:]", sentence) if clean_quote_text(part)]
            sentence = next((part for part in shorter_parts if 12 <= len(part) <= 120), sentence[:176] + "...")
        sentences.append(sentence)
    return sentences


def quote_fingerprint(text: str) -> str:
    compact = re.sub(r"[^\w\u4e00-\u9fff]+", "", text).lower()
    return compact[:120]


def quote_keywords(text: str, category: str, top_terms: list[str], top_categories: list[str]) -> list[str]:
    keywords: list[str] = []
    for term in top_terms:
        if term and term in text and term not in keywords:
            keywords.append(term)
    if category and category in top_categories and category not in keywords:
        keywords.append(category)
    for term in DOMAIN_TERMS:
        if len(keywords) >= 4:
            break
        if term in text and term not in keywords:
            keywords.append(term)
    return keywords[:4]


def quote_score(candidate: dict[str, Any], top_terms: list[str], top_categories: list[str], top_titles: list[str]) -> float:
    text = candidate["text"]
    score = 0.0
    score += min(len(text), 120) / 18
    for term in top_terms[:14]:
        if term and term in text:
            score += 8
    for term in DOMAIN_TERMS:
        if term in text:
            score += 3
    if candidate.get("category") in top_categories[:5]:
        score += 5
    if candidate.get("bookTitle") in top_titles[:6]:
        score += 4
    if any(mark in text for mark in ("方法", "系统", "价值", "增长", "行动", "反馈", "判断", "模型", "用户")):
        score += 4
    if len(text) < 16:
        score -= 5
    if len(text) > 140:
        score -= 2
    return score


def build_poetic_summary(data: dict[str, Any]) -> str:
    kpis = data["kpis"]
    top_category = (data["reading"]["categories"][0]["name"] if data["reading"]["categories"] else "多重兴趣")
    top_book = (data["reading"]["topBooks"][0]["title"] if data["reading"]["topBooks"] else "一本本书")
    terms = [row["name"] for row in data["notes"].get("wordCloud", [])[:4]]
    term_phrase = "、".join(terms) if terms else "问题、方法和判断"
    closing = (
        "那些被划下的句子不是碎片，而是路标；它们把兴趣、判断和行动慢慢连成一张个人地图。"
        if kpis.get("highlightsFetchedInRange")
        else "这些阅读记录不是冷冰冰的数字，而是一条持续靠近问题、方法和生活秩序的路径。"
    )
    return (
        f"这位读者把书架当作一间有灯的工作室：在 {kpis['readDays']} 个阅读日里，"
        f"时间流向「{top_category}」和《{top_book}》，又在 {kpis['noteTotal']} 条笔记里沉淀为{term_phrase}。"
        f"{closing}"
    )


def build_reader_portrait(data: dict[str, Any], highlight_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    top_terms = [row["name"] for row in data["notes"].get("wordCloud", [])]
    top_categories = [row["name"] for row in data["reading"].get("categories", [])]
    top_titles = [row["title"] for row in data["reading"].get("topBooks", [])]
    ranked = []
    for candidate in highlight_candidates:
        fingerprint = quote_fingerprint(candidate["text"])
        if not fingerprint:
            continue
        keywords = quote_keywords(candidate["text"], candidate.get("category") or "", top_terms, top_categories)
        ranked.append(
            {
                **candidate,
                "fingerprint": fingerprint,
                "keywords": keywords,
                "reason": "关联：" + " / ".join(keywords[:3]) if keywords else "关联：阅读画像",
                "score": quote_score(candidate, top_terms, top_categories, top_titles),
            }
        )
    ranked.sort(key=lambda row: row["score"], reverse=True)

    selected: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    book_counts: Counter[str] = Counter()
    seen: set[str] = set()
    for row in ranked:
        fingerprint = row["fingerprint"]
        if fingerprint in seen:
            continue
        title = row.get("bookTitle") or "未知书籍"
        if book_counts[title] >= 3:
            deferred.append(row)
            continue
        selected.append(row)
        book_counts[title] += 1
        seen.add(fingerprint)
        if len(selected) >= 20:
            break
    if len(selected) < 20:
        for row in deferred:
            if row["fingerprint"] in seen:
                continue
            selected.append(row)
            seen.add(row["fingerprint"])
            if len(selected) >= 20:
                break

    quotes = []
    for index, row in enumerate(selected[:20], start=1):
        quotes.append(
            {
                "rank": index,
                "text": row["text"],
                "bookTitle": row.get("bookTitle") or "未知书籍",
                "author": row.get("author") or "",
                "category": row.get("category") or "",
                "keywords": row.get("keywords") or [],
                "reason": row.get("reason") or "关联：阅读画像",
            }
        )
    return {
        "poeticSummary": build_poetic_summary(data),
        "goldenQuote": quotes[0] if quotes else None,
        "quotes": quotes,
        "quoteCount": len(quotes),
    }


AI_FOUNDER_BOOK_CATALOG = [
    {"title": "创业维艰", "author": "本·霍洛维茨", "category": "创业管理", "publisher": "中信出版社"},
    {"title": "从0到1", "author": "彼得·蒂尔", "category": "创业管理", "publisher": "中信出版社"},
    {"title": "精益创业", "author": "埃里克·莱斯", "category": "创业管理", "publisher": "中信出版社"},
    {"title": "创新者的窘境", "author": "克莱顿·克里斯坦森", "category": "商业财经", "publisher": "中信出版社"},
    {"title": "高增长手册", "author": "埃拉德·吉尔", "category": "创业管理", "publisher": "机械工业出版社"},
    {"title": "纳瓦尔宝典", "author": "埃里克·乔根森", "category": "认知学习", "publisher": "中信出版社"},
    {"title": "原则", "author": "瑞·达利欧", "category": "组织管理", "publisher": "中信出版社"},
    {"title": "思考，快与慢", "author": "丹尼尔·卡尼曼", "category": "认知学习", "publisher": "中信出版社"},
    {"title": "人工智能：现代方法", "author": "Stuart Russell / Peter Norvig", "category": "AI技术", "publisher": "人民邮电出版社"},
    {"title": "深度学习", "author": "Ian Goodfellow / Yoshua Bengio / Aaron Courville", "category": "AI技术", "publisher": "人民邮电出版社"},
    {"title": "大模型应用开发", "author": "AI工程团队", "category": "AI技术", "publisher": "电子工业出版社"},
    {"title": "AI 2041", "author": "李开复 / 陈楸帆", "category": "AI趋势", "publisher": "浙江人民出版社"},
    {"title": "生命3.0", "author": "Max Tegmark", "category": "AI趋势", "publisher": "浙江教育出版社"},
    {"title": "超级智能", "author": "Nick Bostrom", "category": "AI趋势", "publisher": "中信出版社"},
    {"title": "设计数据密集型应用", "author": "Martin Kleppmann", "category": "工程架构", "publisher": "中国电力出版社"},
    {"title": "架构整洁之道", "author": "Robert C. Martin", "category": "工程架构", "publisher": "人民邮电出版社"},
    {"title": "重构", "author": "Martin Fowler", "category": "工程架构", "publisher": "人民邮电出版社"},
    {"title": "程序员修炼之道", "author": "David Thomas / Andrew Hunt", "category": "工程架构", "publisher": "电子工业出版社"},
    {"title": "系统之美", "author": "德内拉·梅多斯", "category": "系统思维", "publisher": "浙江人民出版社"},
    {"title": "规模", "author": "杰弗里·韦斯特", "category": "系统思维", "publisher": "中信出版社"},
    {"title": "复杂", "author": "梅拉妮·米歇尔", "category": "系统思维", "publisher": "湖南科学技术出版社"},
    {"title": "用户体验要素", "author": "Jesse James Garrett", "category": "产品增长", "publisher": "机械工业出版社"},
    {"title": "启示录", "author": "Marty Cagan", "category": "产品增长", "publisher": "电子工业出版社"},
    {"title": "增长黑客", "author": "Sean Ellis / Morgan Brown", "category": "产品增长", "publisher": "中信出版社"},
    {"title": "定位", "author": "艾·里斯 / 杰克·特劳特", "category": "营销品牌", "publisher": "机械工业出版社"},
    {"title": "影响力", "author": "罗伯特·西奥迪尼", "category": "营销品牌", "publisher": "中国人民大学出版社"},
    {"title": "卓有成效的管理者", "author": "彼得·德鲁克", "category": "组织管理", "publisher": "机械工业出版社"},
    {"title": "管理的实践", "author": "彼得·德鲁克", "category": "组织管理", "publisher": "机械工业出版社"},
    {"title": "OKR工作法", "author": "Christina Wodtke", "category": "组织管理", "publisher": "中信出版社"},
    {"title": "失控", "author": "凯文·凯利", "category": "科技趋势", "publisher": "电子工业出版社"},
    {"title": "必然", "author": "凯文·凯利", "category": "科技趋势", "publisher": "电子工业出版社"},
    {"title": "硅谷钢铁侠", "author": "Ashlee Vance", "category": "人物传记", "publisher": "中信出版社"},
    {"title": "史蒂夫·乔布斯传", "author": "Walter Isaacson", "category": "人物传记", "publisher": "中信出版社"},
    {"title": "芯片战争", "author": "克里斯·米勒", "category": "科技趋势", "publisher": "浙江人民出版社"},
    {"title": "置身事内", "author": "兰小欢", "category": "商业财经", "publisher": "上海人民出版社"},
    {"title": "浪潮之巅", "author": "吴军", "category": "科技趋势", "publisher": "人民邮电出版社"},
    {"title": "腾讯传", "author": "吴晓波", "category": "商业财经", "publisher": "浙江大学出版社"},
    {"title": "详谈：左晖", "author": "李翔", "category": "人物传记", "publisher": "新星出版社"},
    {"title": "穷查理宝典", "author": "查理·芒格", "category": "认知学习", "publisher": "中信出版社"},
    {"title": "事实", "author": "汉斯·罗斯林", "category": "认知学习", "publisher": "文汇出版社"},
    {"title": "刻意练习", "author": "Anders Ericsson / Robert Pool", "category": "认知学习", "publisher": "机械工业出版社"},
    {"title": "被讨厌的勇气", "author": "岸见一郎 / 古贺史健", "category": "心理成长", "publisher": "机械工业出版社"},
]

AI_FOUNDER_NOTE_TEMPLATES = [
    "AI创业最难的不是写出 demo，而是在客户访谈里找到真实痛点，形成产品市场匹配。",
    "智能体产品需要把评测体系前置，否则大模型能力会被幻觉、延迟和算力成本吞掉。",
    "融资节奏不能替代现金流纪律，增长飞轮必须建立在可复购的商业模式上。",
    "开源模型降低了实验成本，但护城河仍然来自数据飞轮、分发渠道和组织执行。",
    "优秀的创业者会把战略拆成每周可验证的假设，把客户反馈变成产品路线图。",
    "网络效应不是口号，只有当用户行为持续改善模型和供给时，飞轮才真正成立。",
    "提示词只是入口，长期价值来自工作流重构、权限边界、评价指标和组织设计。",
    "AI产品的定价要同时考虑节省时间、提升转化率和替代人工的边际价值。",
    "团队管理的核心是减少噪音，让工程、产品、增长围绕同一个北极星指标迭代。",
    "创业公司要警惕伪需求，最好的信号是客户愿意付费、迁移数据并承担切换成本。",
    "如果一个模型能力不能嵌入用户的日常流程，它就只是一段有趣的技术展示。",
    "商业化阶段要把销售话术、成功案例和交付能力做成系统，而不是依赖创始人个人英雄主义。",
    "最好的产品路线图不是功能清单，而是用户工作流里反复出现的阻塞点。",
    "创始人需要同时看见技术曲线和人性惯性，前者决定可能性，后者决定采用速度。",
    "组织设计的目标不是制造层级，而是让信息、责任和决策在正确的位置相遇。",
    "增长不是把漏斗做大，而是让每一次触达都更接近真实价值和长期信任。",
    "真正有效的智能体不会替人炫技，而是在低频错误和高频琐事之间节省注意力。",
    "当市场还没有共识时，最稀缺的能力是把模糊需求翻译成可验证的实验。",
    "一家公司的护城河往往藏在日复一日的流程里，而不是发布会上的形容词里。",
    "读书的意义不是获得确定答案，而是让自己的问题变得更准确、更有行动方向。",
]


def synthetic_book_at(index: int) -> dict[str, Any]:
    base = AI_FOUNDER_BOOK_CATALOG[index % len(AI_FOUNDER_BOOK_CATALOG)]
    cycle = index // len(AI_FOUNDER_BOOK_CATALOG)
    title = base["title"] if cycle == 0 else f"{base['title']}：AI创业复盘 {cycle + 1}"
    return {
        "bookId": f"sample-book-{index + 1:04d}",
        "title": title,
        "author": base["author"],
        "category": base["category"],
        "publisher": base["publisher"],
    }


def synthetic_day(report_range: Range, index: int, offset: int = 0) -> date:
    span = max(1, (report_range.end - report_range.start).days + 1)
    return report_range.start + timedelta(days=(index * 17 + offset * 31) % span)


def build_synthetic_shelf(report_range: Range, scale: int) -> dict[str, Any]:
    ebook_count = 145 * scale
    album_count = 9 * scale
    books = []
    for idx in range(ebook_count):
        book = synthetic_book_at(idx)
        day = synthetic_day(report_range, idx)
        books.append(
            {
                **book,
                "finishReading": 1 if idx % 4 != 0 else 0,
                "secret": 1 if idx % 9 == 0 else 0,
                "readUpdateTime": to_ts(day),
                "updateTime": to_ts(day),
            }
        )

    albums = []
    album_titles = ["AI产品周会", "硅谷创业访谈", "大模型工程实战", "商业模式课", "组织管理复盘", "技术趋势播客"]
    for idx in range(album_count):
        day = synthetic_day(report_range, idx, offset=3)
        title = f"{album_titles[idx % len(album_titles)]} 第{idx // len(album_titles) + 1}季"
        albums.append(
            {
                "albumInfo": {"albumId": f"sample-album-{idx + 1:03d}", "title": title, "name": title, "finish": 1 if idx % 3 != 0 else 0, "updateTime": to_ts(day)},
                "albumInfoExtra": {"secret": 1 if idx % 8 == 0 else 0, "lectureReadUpdateTime": to_ts(day)},
            }
        )

    archive_specs = [
        ("AI创业核心书单", 18),
        ("大模型工程与智能体", 16),
        ("产品增长实验室", 14),
        ("组织管理与OKR", 12),
        ("融资、财务与商业化", 10),
        ("创始人传记", 8),
        ("系统思维与复杂性", 8),
        ("周末深读", 6),
    ]
    archives = [
        {"name": name, "bookIds": [books[(idx * 37 + pos) % len(books)]["bookId"] for pos in range(size * scale)]}
        for idx, (name, size) in enumerate(archive_specs)
    ]
    return {"books": books, "albums": albums, "archive": archives, "mp": {"title": "文章收藏"}}


def build_synthetic_monthly_daily(report_range: Range, scale: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    daily: list[dict[str, Any]] = []
    day = report_range.start
    day_index = 0
    active_threshold = min(84, 20 + 8 * scale)
    while day <= report_range.end:
        score = (day_index * 37 + day.month * 11 + day.day * 17 + day.year) % 100
        if score < active_threshold:
            base_minutes = 16 + ((day_index * 19 + day.month * 7) % 48)
            if day.weekday() in (0, 1, 2):
                base_minutes += 12
            if score % 17 == 0:
                base_minutes += 30
            daily.append({"date": day.isoformat(), "seconds": base_minutes * scale * 60})
        day += timedelta(days=1)
        day_index += 1

    daily_by_month: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in daily:
        label = item["date"][:7]
        daily_by_month[label].append(item)

    monthly = []
    months = month_iter(report_range.start, report_range.end)
    for idx, month_start in enumerate(months):
        label = month_label(month_start)
        rows = daily_by_month.get(label, [])
        month_seconds = sum(int(row["seconds"]) for row in rows)
        read_days = len(rows)
        read_books = int(max(6, (read_days * 0.72 + (idx % 4) * 2) * scale / 2))
        finished_books = max(1, read_books // 5)
        note_count = int(max(12, read_days * 4.2 * scale))
        read_longest = []
        if month_seconds:
            for rank, share in enumerate((0.18, 0.11, 0.07)):
                book = synthetic_book_at((idx * 3 + rank) % len(AI_FOUNDER_BOOK_CATALOG))
                read_longest.append({"book": book, "readTime": int(month_seconds * share) + (rank + 1) * scale * 300})
        monthly.append(
            {
                "label": label,
                "baseTime": to_ts(date(month_start.year, month_start.month, min(15, 28))),
                "totalReadTime": month_seconds,
                "rangeReadTime": month_seconds,
                "readDays": read_days,
                "serviceReadDays": read_days,
                "dayAverageReadTime": int(month_seconds / read_days) if read_days else 0,
                "readStat": {"读过": read_books, "读完": finished_books, "笔记": note_count},
                "readLongest": read_longest,
                "preferCategory": [],
                "preferBooks": [],
            }
        )
    return monthly, daily


def build_synthetic_annual(report_range: Range, daily: list[dict[str, Any]], scale: int) -> list[dict[str, Any]]:
    daily_by_year: defaultdict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in daily:
        daily_by_year[int(row["date"][:4])].append(row)

    category_weights = [
        ("AI技术", 0.28),
        ("创业管理", 0.20),
        ("产品增长", 0.15),
        ("商业财经", 0.12),
        ("组织管理", 0.10),
        ("系统思维", 0.07),
        ("科技趋势", 0.05),
        ("认知学习", 0.03),
    ]
    publisher_names = ["中信出版社", "电子工业出版社", "人民邮电出版社", "机械工业出版社", "浙江人民出版社", "中国人民大学出版社", "上海人民出版社", "新星出版社"]
    annual = []
    for year in year_iter(report_range.start, report_range.end):
        rows = daily_by_year.get(year, [])
        total_seconds = sum(int(row["seconds"]) for row in rows)
        read_days = len(rows)
        prefer_author = []
        for idx, book in enumerate(AI_FOUNDER_BOOK_CATALOG[:12]):
            seconds = int(total_seconds * (0.13 - min(idx, 10) * 0.008))
            prefer_author.append({"name": book["author"], "count": max(1, (12 - idx) * scale), "readTime": format_duration(max(0, seconds))})
        annual.append(
            {
                "_year": year,
                "totalReadTime": total_seconds,
                "readDays": read_days,
                "preferCategory": [
                    {
                        "categoryTitle": name,
                        "parentCategoryTitle": name,
                        "readingTime": int(total_seconds * weight),
                        "readingCount": max(1, int((80 * weight + year % 5) * scale)),
                    }
                    for name, weight in category_weights
                ],
                "preferAuthor": prefer_author,
                "preferPublisher": [{"name": name, "count": max(2, (len(publisher_names) - idx) * scale + (year % 3))} for idx, name in enumerate(publisher_names)],
                "wrReadTime": int(total_seconds * 0.84),
                "wrListenTime": int(total_seconds * 0.16),
            }
        )
    return annual


def build_synthetic_notes(report_range: Range, scale: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    notebook_count = len(AI_FOUNDER_BOOK_CATALOG)
    notebooks: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    for idx in range(notebook_count):
        book = synthetic_book_at(idx)
        note_count = (18 + (idx * 7) % 42) * scale
        review_count = (4 + (idx * 5) % 16) * scale
        bookmark_count = (2 + (idx * 3) % 7) * scale
        progress = min(100, 35 + ((idx * 11) % 78))
        notebooks.append(
            {
                "bookId": book["bookId"],
                "book": book,
                "reviewCount": review_count,
                "noteCount": note_count,
                "bookmarkCount": bookmark_count,
                "readingProgress": progress,
                "sort": to_ts(synthetic_day(report_range, idx, offset=5)),
            }
        )

        highlights = []
        for mark_idx in range(note_count):
            day = synthetic_day(report_range, idx + mark_idx, offset=mark_idx % 11)
            template = AI_FOUNDER_NOTE_TEMPLATES[(idx + mark_idx) % len(AI_FOUNDER_NOTE_TEMPLATES)]
            highlights.append(
                {
                    "createTime": to_ts(day),
                    "markText": f"{template} AI创业。智能体。产品市场匹配。商业化。",
                }
            )
        reviews = []
        for review_idx in range(review_count):
            day = synthetic_day(report_range, idx + review_idx, offset=17)
            template = AI_FOUNDER_NOTE_TEMPLATES[(idx * 2 + review_idx) % len(AI_FOUNDER_NOTE_TEMPLATES)]
            reviews.append(
                {
                    "review": {
                        "createTime": to_ts(day),
                        "content": f"复盘《{book['title']}》：{template} 定价。渠道。留存。模型评测体系。",
                    }
                }
            )
        details.append({"bookId": book["bookId"], "highlights": highlights, "reviews": reviews, "errors": []})
    return notebooks, details


def build_synthetic_ai_founder_report(report_range: Range, scale: int) -> dict[str, Any]:
    scale = max(1, int(scale))
    shelf = build_synthetic_shelf(report_range, scale)
    monthly, daily = build_synthetic_monthly_daily(report_range, scale)
    annual = build_synthetic_annual(report_range, daily, scale)
    notebooks, note_details = build_synthetic_notes(report_range, scale)
    data = aggregate(report_range, shelf, monthly, daily, annual, notebooks, note_details, note_errors=0)
    data["meta"].update(
        {
            "title": "微信读书个人可视化报告：AI创业者版",
            "subtitle": "一个 AI 创业者读者的近两年阅读画像。把阅读时间、书架资产、内容偏好和笔记语义放在同一张纸面上：先看节律，再看兴趣，最后看留下来的句子。",
            "eyebrow": "WeRead AI-Founder Analytics",
            "sampleReport": True,
            "persona": "AI创业者读者",
            "dataCaveat": "月度数据使用 readTimes 做日级过滤；年度偏好模块按触达自然年聚合。",
        }
    )
    data["tables"] = build_tables(data)
    return data


def aggregate(
    report_range: Range,
    shelf: dict[str, Any],
    monthly: list[dict[str, Any]],
    daily: list[dict[str, Any]],
    annual: list[dict[str, Any]],
    notebooks: list[dict[str, Any]],
    note_details: list[dict[str, Any]],
    note_errors: int,
) -> dict[str, Any]:
    books = shelf.get("books") or []
    albums = shelf.get("albums") or []
    archives = shelf.get("archive") or []
    mp_count = 1 if shelf.get("mp") else 0

    daily_map = {item["date"]: int(item["seconds"]) for item in daily}
    total_seconds = sum(daily_map.values()) or sum(int(m.get("rangeReadTime") or 0) for m in monthly)
    read_days = sum(1 for value in daily_map.values() if value >= 60) or sum(int(m.get("readDays") or 0) for m in monthly)

    top_book_seconds: Counter[str] = Counter()
    top_book_meta: dict[str, dict[str, Any]] = {}
    for month in monthly:
        for row in month.get("readLongest") or []:
            identity = read_longest_identity(row)
            if not identity:
                continue
            title = identity["title"]
            top_book_seconds[title] += int(row.get("readTime") or 0)
            top_book_meta[title] = identity

    category_seconds: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()
    author_seconds: Counter[str] = Counter()
    author_counts: Counter[str] = Counter()
    publisher_counts: Counter[str] = Counter()
    read_listen = Counter()
    annual_rows: list[dict[str, Any]] = []
    for year_data in annual:
        year = year_data.get("_year")
        annual_rows.append(
            {
                "year": str(year),
                "seconds": int(year_data.get("totalReadTime") or 0),
                "readDays": int(year_data.get("readDays") or 0),
            }
        )
        for cat in year_data.get("preferCategory") or []:
            name = cat.get("categoryTitle") or cat.get("parentCategoryTitle") or "未分类"
            category_seconds[name] += int(cat.get("readingTime") or 0)
            category_counts[name] += int(cat.get("readingCount") or 0)
        for author in year_data.get("preferAuthor") or []:
            name = author.get("name") or "未知作者"
            author_counts[name] += int(author.get("count") or 0)
            author_seconds[name] += parse_duration_text(author.get("readTime"))
        for publisher in year_data.get("preferPublisher") or []:
            name = publisher.get("name") or "未知出版社"
            publisher_counts[name] += int(publisher.get("count") or 0)
        read_listen["文字阅读"] += int(year_data.get("wrReadTime") or 0)
        read_listen["听书/有声"] += int(year_data.get("wrListenTime") or 0)

    shelf_category_counts: Counter[str] = Counter()
    recent_month_counts: Counter[str] = Counter()
    finish_counts = Counter()
    secret_counts = Counter()
    for book in books:
        shelf_category_counts[book.get("category") or "未分类"] += 1
        finish_counts["已读完" if int(book.get("finishReading") or 0) == 1 else "未读完"] += 1
        secret_counts["私密阅读" if int(book.get("secret") or 0) == 1 else "公开阅读"] += 1
        day = shelf_book_date(book)
        if day and report_range.start <= day <= report_range.end:
            recent_month_counts[month_label(date(day.year, day.month, 1))] += 1
    for album in albums:
        info = album.get("albumInfo") or {}
        extra = album.get("albumInfoExtra") or {}
        shelf_category_counts["有声/专辑"] += 1
        finish_counts["已完结专辑" if int(info.get("finish") or 0) == 1 else "连载/未完结专辑"] += 1
        secret_counts["私密阅读" if int(extra.get("secret") or 0) == 1 else "公开阅读"] += 1
        day = from_ts(extra.get("lectureReadUpdateTime") or info.get("updateTime"))
        if day and report_range.start <= day <= report_range.end:
            recent_month_counts[month_label(date(day.year, day.month, 1))] += 1
    if mp_count:
        shelf_category_counts["文章收藏"] += 1
        secret_counts["私密阅读"] += 1

    notebook_rows = []
    note_type_totals = Counter()
    notebook_category_counts: Counter[str] = Counter()
    for item in notebooks:
        book = book_info_from_notebook(item)
        total = notebook_total(item)
        note_type_totals["划线"] += int(item.get("noteCount") or 0)
        note_type_totals["想法/点评"] += int(item.get("reviewCount") or 0)
        note_type_totals["书签"] += int(item.get("bookmarkCount") or 0)
        notebook_category_counts[book.get("category") or "未分类"] += 1
        notebook_rows.append(
            {
                "bookId": str(item.get("bookId") or book.get("bookId") or ""),
                "title": book.get("title") or "未命名",
                "author": book.get("author") or "",
                "category": book.get("category") or "未分类",
                "total": total,
                "highlightCount": int(item.get("noteCount") or 0),
                "reviewCount": int(item.get("reviewCount") or 0),
                "bookmarkCount": int(item.get("bookmarkCount") or 0),
                "progress": int(item.get("readingProgress") or 0),
                "sort": int(item.get("sort") or 0),
            }
        )
    notebook_rows.sort(key=lambda row: row["total"], reverse=True)

    book_lookup = {row["bookId"]: row for row in notebook_rows if row.get("bookId")}
    text_pool: list[str] = []
    highlight_candidates: list[dict[str, Any]] = []
    note_timeline: Counter[str] = Counter()
    highlight_length: Counter[str] = Counter()
    highlights_in_range = 0
    reviews_in_range = 0
    for detail in note_details:
        detail_book = book_lookup.get(str(detail.get("bookId") or ""), {})
        for item in detail.get("highlights") or []:
            day = from_ts(item.get("createTime"))
            if day and not (report_range.start <= day <= report_range.end):
                continue
            text = item.get("markText") or ""
            if text:
                text_pool.append(text)
                highlights_in_range += 1
                highlight_length[bucket(len(text), [20, 50, 100, 200, 400])] += 1
                for sentence in split_highlight_sentences(text):
                    highlight_candidates.append(
                        {
                            "text": sentence,
                            "bookId": str(detail.get("bookId") or ""),
                            "bookTitle": detail_book.get("title") or "未知书籍",
                            "author": detail_book.get("author") or "",
                            "category": detail_book.get("category") or "",
                            "createdAt": day.isoformat() if day else "",
                        }
                    )
            if day:
                note_timeline[month_label(date(day.year, day.month, 1))] += 1
        for item in detail.get("reviews") or []:
            review = item.get("review") or item
            day = from_ts(review.get("createTime"))
            if day and not (report_range.start <= day <= report_range.end):
                continue
            text = review.get("content") or ""
            if text:
                text_pool.append(text)
                reviews_in_range += 1
            if day:
                note_timeline[month_label(date(day.year, day.month, 1))] += 1

    months = [month_label(m) for m in month_iter(report_range.start, report_range.end)]
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday_heat = defaultdict(int)
    for day_str, seconds in daily_map.items():
        day = datetime.strptime(day_str, "%Y-%m-%d").date()
        weekday_heat[(month_label(date(day.year, day.month, 1)), day.weekday())] += seconds

    cumulative = []
    running = 0
    for day_str in sorted(daily_map):
        running += daily_map[day_str]
        cumulative.append([day_str, hours(running)])

    word_cloud = extract_terms(text_pool, limit=35)
    report_data = {
        "meta": {
            "range": report_range.label,
            "start": report_range.start.isoformat(),
            "end": report_range.end.isoformat(),
            "generatedAt": datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S %Z") if TZ else datetime.now().isoformat(timespec="seconds"),
            "skillVersion": SKILL_VERSION,
            "timezone": TZ_NAME,
            "dataCaveat": "月度数据使用 readTimes 做日级过滤；年度偏好模块按触达自然年聚合。",
        },
        "kpis": {
            "totalReadTime": format_duration(total_seconds),
            "totalReadHours": hours(total_seconds),
            "readDays": read_days,
            "shelfTotal": len(books) + len(albums) + mp_count,
            "ebookCount": len(books),
            "albumCount": len(albums),
            "mpCount": mp_count,
            "notebookBooks": len(notebooks),
            "noteTotal": sum(notebook_total(item) for item in notebooks),
            "highlightsFetchedInRange": highlights_in_range,
            "reviewsFetchedInRange": reviews_in_range,
            "noteFetchErrors": note_errors,
        },
        "series": {
            "months": months,
            "monthlyReadHours": [hours(next((m.get("rangeReadTime") for m in monthly if m["label"] == label), 0)) for label in months],
            "monthlyReadDays": [int(next((m.get("readDays") for m in monthly if m["label"] == label), 0)) for label in months],
            "monthlyReadStat": [
                {
                    "month": label,
                    "readBooks": int(next((m.get("readStat", {}).get("读过") for m in monthly if m["label"] == label), 0) or 0),
                    "finishedBooks": int(next((m.get("readStat", {}).get("读完") for m in monthly if m["label"] == label), 0) or 0),
                    "notes": int(next((m.get("readStat", {}).get("笔记") for m in monthly if m["label"] == label), 0) or 0),
                }
                for label in months
            ],
            "dailyHeat": [[row["date"], round(row["seconds"] / 60, 1)] for row in daily],
            "weekdayHeat": [
                [weekday, months.index(month), hours(seconds)]
                for (month, weekday), seconds in weekday_heat.items()
                if month in months
            ],
            "weekdayNames": weekday_names,
            "cumulativeReadHours": cumulative,
            "annualRows": [{"year": row["year"], "hours": hours(row["seconds"]), "readDays": row["readDays"]} for row in annual_rows],
        },
        "reading": {
            "topBooks": [
                {**top_book_meta[title], "hours": hours(seconds), "seconds": seconds}
                for title, seconds in top_book_seconds.most_common(15)
            ],
            "categories": [
                {"name": name, "hours": hours(seconds), "count": category_counts[name], "seconds": seconds}
                for name, seconds in category_seconds.most_common(12)
            ],
            "authors": [
                {"name": name, "seconds": seconds, "hours": hours(seconds), "count": author_counts[name]}
                for name, seconds in author_seconds.most_common(12)
            ],
            "publishers": [{"name": name, "count": count} for name, count in publisher_counts.most_common(12)],
            "readListen": [{"name": name, "value": hours(value), "seconds": value} for name, value in read_listen.items() if value > 0],
        },
        "shelf": {
            "composition": [
                {"name": "电子书", "value": len(books)},
                {"name": "有声/专辑", "value": len(albums)},
                {"name": "文章收藏", "value": mp_count},
            ],
            "categories": [{"name": name, "value": count} for name, count in shelf_category_counts.most_common(24)],
            "finished": [{"name": name, "value": count} for name, count in finish_counts.items()],
            "privacy": [{"name": name, "value": count} for name, count in secret_counts.items()],
            "archives": [{"name": item.get("name") or "未命名书单", "value": len(item.get("bookIds") or [])} for item in archives],
            "recentActivity": [{"month": label, "count": recent_month_counts.get(label, 0)} for label in months],
        },
        "notes": {
            "topBooks": notebook_rows[:20],
            "typeTotals": [{"name": name, "value": value} for name, value in note_type_totals.items()],
            "progressScatter": [[row["progress"], row["total"], row["title"]] for row in notebook_rows if row["progress"] is not None],
            "wordCloud": word_cloud,
            "timeline": [{"month": label, "count": note_timeline.get(label, 0)} for label in months],
            "highlightLength": [{"bucket": name, "count": count} for name, count in sorted(highlight_length.items())],
            "categories": [{"name": name, "value": count} for name, count in notebook_category_counts.most_common(14)],
        },
    }
    report_data["coverage"] = {
        "monthlyRequests": len(monthly),
        "annualRequests": len(annual),
        "shelfBooks": len(books),
        "shelfAlbums": len(albums),
        "notebooks": len(notebooks),
        "noteDetailBooksFetched": len(note_details),
        "noteFetchErrors": note_errors,
    }
    report_data["readerPortrait"] = build_reader_portrait(report_data, highlight_candidates)
    report_data["charts"] = build_charts(report_data)
    report_data["tables"] = build_tables(report_data)
    report_data["insights"] = build_insights(report_data)
    return report_data


def axis_text() -> dict[str, Any]:
    return {"color": STONE, "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, PingFang SC, sans-serif"}


def chart_base(title: str, subtitle: str, option: dict[str, Any], source: str, empty: bool = False) -> dict[str, Any]:
    return {"id": slug(title), "title": title, "subtitle": subtitle, "source": source, "option": option, "empty": empty, "kind": chart_kind(option)}


def chart_kind(option: dict[str, Any]) -> str:
    series = option.get("series") if isinstance(option, dict) else None
    if isinstance(series, list) and series and isinstance(series[0], dict):
        kind = str(series[0].get("type") or "custom")
        kind = re.sub(r"([a-z])([A-Z])", r"\1-\2", kind).lower()
        return re.sub(r"[^a-z0-9-]+", "-", kind).strip("-") or "custom"
    return "custom"


def slug(text: str) -> str:
    raw = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "-", text).strip("-")
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return "chart-" + digest


def build_charts(data: dict[str, Any]) -> list[dict[str, Any]]:
    months = data["series"]["months"]
    charts: list[dict[str, Any]] = []
    charts.append(
        chart_base(
            "月度阅读时长",
            "按自然月汇总，边界月份使用日级 readTimes 过滤。",
            {
                "color": [BRAND, WARM],
                "tooltip": {"trigger": "axis"},
                "grid": {"left": 46, "right": 24, "top": 34, "bottom": 54, "containLabel": True},
                "xAxis": {"type": "category", "data": months, "axisLabel": axis_text()},
                "yAxis": {"type": "value", "name": "小时", "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
                "series": [{"type": "bar", "name": "阅读小时", "data": data["series"]["monthlyReadHours"], "barMaxWidth": 18}],
            },
            "/readdata/detail monthly",
        )
    )
    charts.append(
        chart_base(
            "月度阅读天数",
            "单日阅读满 1 分钟计为有效阅读日。",
            line_option(months, data["series"]["monthlyReadDays"], "天数"),
            "/readdata/detail monthly",
        )
    )
    daily_buckets = Counter()
    for _, mins in data["series"]["dailyHeat"]:
        daily_buckets[bucket(int(math.ceil(mins)), [5, 15, 30, 60, 120, 240])] += 1
    charts.append(
        chart_base(
            "阅读日时长分布",
            "只统计有阅读记录的日期，按单日分钟数分桶。",
            simple_bar(list(daily_buckets.keys()), list(daily_buckets.values()), "天"),
            "/readdata/detail readTimes",
            empty=not bool(daily_buckets),
        )
    )
    charts.append(
        chart_base(
            "月内星期节律",
            "观察哪些月份的哪些星期更容易读书。",
            {
                "tooltip": {"position": "top"},
                "grid": {"left": 72, "right": 18, "top": 18, "bottom": 70, "containLabel": True},
                "xAxis": {"type": "category", "data": data["series"]["weekdayNames"], "axisLabel": axis_text()},
                "yAxis": {"type": "category", "data": months, "axisLabel": axis_text()},
                "visualMap": {"min": 0, "max": max([v[2] for v in data["series"]["weekdayHeat"]] or [1]), "orient": "horizontal", "left": "center", "bottom": 0, "inRange": {"color": ["#ede9dd", "#d1b98b", BRAND]}},
                "series": [{"type": "heatmap", "data": data["series"]["weekdayHeat"], "label": {"show": False}}],
            },
            "/readdata/detail readTimes",
            empty=not bool(data["series"]["weekdayHeat"]),
        )
    )
    charts.append(
        chart_base(
            "累计阅读小时",
            "近 24 个月阅读时间的累积曲线。",
            {
                "color": [BRAND],
                "tooltip": {"trigger": "axis"},
                "grid": {"left": 48, "right": 22, "top": 24, "bottom": 50, "containLabel": True},
                "xAxis": {"type": "time", "axisLabel": axis_text()},
                "yAxis": {"type": "value", "name": "小时", "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
                "series": [{"name": "累计小时", "type": "line", "smooth": True, "areaStyle": {"color": "#E4ECF5"}, "data": data["series"]["cumulativeReadHours"]}],
            },
            "/readdata/detail readTimes",
        )
    )
    charts.append(
        chart_base(
            "月度读过/读完/笔记",
            "来自月度 readStat 文案解析，用于趋势观察。",
            stacked_bar_option(
                months,
                [
                    ("读过", [row["readBooks"] for row in data["series"]["monthlyReadStat"]]),
                    ("读完", [row["finishedBooks"] for row in data["series"]["monthlyReadStat"]]),
                    ("笔记", [row["notes"] for row in data["series"]["monthlyReadStat"]]),
                ],
            ),
            "/readdata/detail readStat",
        )
    )
    charts.append(
        chart_base(
            "触达自然年对比",
            "年度接口按自然年返回；默认报告范围跨到的年份都会展示。",
            grouped_bar_option(
                [row["year"] for row in data["series"]["annualRows"]],
                [("阅读小时", [row["hours"] for row in data["series"]["annualRows"]]), ("阅读天数", [row["readDays"] for row in data["series"]["annualRows"]])],
            ),
            "/readdata/detail annually",
        )
    )
    charts.append(chart_base("读得最久的书", "按月度 readLongest 聚合，避免直接用书架推断时长。", horizontal_bar(data["reading"]["topBooks"], "title", "hours", "小时"), "/readdata/detail readLongest", empty=not data["reading"]["topBooks"]))
    charts.append(chart_base("阅读分类雷达", "按年度偏好分类 readingTime 聚合。", radar_option(data["reading"]["categories"]), "/readdata/detail preferCategory", empty=not data["reading"]["categories"]))
    charts.append(chart_base("分类阅读时长", "分类按阅读小时降序。", horizontal_bar(data["reading"]["categories"], "name", "hours", "小时"), "/readdata/detail preferCategory", empty=not data["reading"]["categories"]))
    charts.append(chart_base("分类阅读地图", "面积代表分类阅读时长。", treemap_option(data["reading"]["categories"], "hours"), "/readdata/detail preferCategory", empty=not data["reading"]["categories"]))
    charts.append(chart_base("偏好作者", "作者偏好来自年度接口，时长字段按中文时长解析。", horizontal_bar(data["reading"]["authors"], "name", "hours", "小时"), "/readdata/detail preferAuthor", empty=not data["reading"]["authors"]))
    charts.append(chart_base("偏好出版社", "按年度接口返回的出版社阅读本数聚合。", horizontal_bar(data["reading"]["publishers"], "name", "count", "本"), "/readdata/detail preferPublisher", empty=not data["reading"]["publishers"]))
    charts.append(chart_base("文字阅读与听书", "接口仅在满足展示阈值时返回，按触达自然年聚合。", pie_option(data["reading"]["readListen"], "value"), "/readdata/detail wrReadTime/wrListenTime", empty=not data["reading"]["readListen"]))
    charts.append(chart_base("书架构成", "书架总数包含电子书、专辑/有声书和文章收藏入口。", pie_option(data["shelf"]["composition"], "value"), "/shelf/sync", empty=False))
    charts.append(chart_base("书架分类资产", "按书架条目 category 分布；有声和文章收藏单独归类。", treemap_option(data["shelf"]["categories"], "value"), "/shelf/sync books/albums/mp", empty=not data["shelf"]["categories"]))
    charts.append(chart_base("书架读完状态", "电子书用 finishReading，专辑用完结状态。", pie_option(data["shelf"]["finished"], "value"), "/shelf/sync", empty=not data["shelf"]["finished"]))
    charts.append(chart_base("公开/私密阅读", "文章收藏入口固定计入私密阅读。", pie_option(data["shelf"]["privacy"], "value"), "/shelf/sync", empty=not data["shelf"]["privacy"]))
    charts.append(chart_base("书单规模", "archive[].bookIds 的数量。", horizontal_bar(data["shelf"]["archives"], "name", "value", "本"), "/shelf/sync archive", empty=not data["shelf"]["archives"]))
    charts.append(chart_base("近两年书架活动", "按最近阅读或更新时间聚合的书架活动条目数。", line_option(months, [row["count"] for row in data["shelf"]["recentActivity"]], "条目"), "/shelf/sync readUpdateTime", empty=not any(row["count"] for row in data["shelf"]["recentActivity"])))
    charts.append(chart_base("笔记最多的书", "总笔记数 = 划线 + 想法/点评 + 书签。", horizontal_bar(data["notes"]["topBooks"][:15], "title", "total", "条"), "/user/notebooks", empty=not data["notes"]["topBooks"]))
    charts.append(chart_base("笔记类型构成", "书签只展示数量，当前接口不能导出书签内容。", pie_option(data["notes"]["typeTotals"], "value"), "/user/notebooks", empty=not data["notes"]["typeTotals"]))
    charts.append(
        chart_base(
            "阅读进度与笔记量",
            "每个点是一本文档；横轴阅读进度，纵轴笔记总数。",
            {
                "color": [BRAND],
                "tooltip": {"formatter": "{b}<br/>进度: {@[0]}%<br/>笔记: {@[1]}条"},
                "grid": {"left": 46, "right": 24, "top": 24, "bottom": 44, "containLabel": True},
                "xAxis": {"type": "value", "name": "进度%", "min": 0, "max": 100, "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
                "yAxis": {"type": "value", "name": "笔记", "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
                "series": [{"type": "scatter", "symbolSize": 8, "data": data["notes"]["progressScatter"]}],
            },
            "/user/notebooks readingProgress",
            empty=not data["notes"]["progressScatter"],
        )
    )
    charts.append(chart_base("划线与想法词云", "由近两年划线和想法文本抽取高频短语。", {"tooltip": {}, "series": [{"type": "wordCloud", "shape": "circle", "gridSize": 6, "sizeRange": [12, 48], "rotationRange": [-25, 25], "textStyle": {"fontFamily": "TsangerJinKai02, Source Han Serif SC, serif", "color": "function(){var c=['#1B365D','#7d8b70','#a45d4f','#6f675a','#2D5A8A'];return c[Math.floor(Math.random()*c.length)]}"}, "data": data["notes"]["wordCloud"]}]}, "/book/bookmarklist + /review/list/mine", empty=not data["notes"]["wordCloud"]))
    charts.append(chart_base("笔记时间线", "按划线和想法创建时间聚合。", line_option(months, [row["count"] for row in data["notes"]["timeline"]], "条"), "/book/bookmarklist createTime + /review/list/mine createTime", empty=not any(row["count"] for row in data["notes"]["timeline"])))
    charts.append(chart_base("划线长度分布", "按划线原文字数分桶。", simple_bar([row["bucket"] for row in data["notes"]["highlightLength"]], [row["count"] for row in data["notes"]["highlightLength"]], "条"), "/book/bookmarklist markText", empty=not data["notes"]["highlightLength"]))
    return charts


def line_option(labels: list[str], values: list[Any], name: str) -> dict[str, Any]:
    return {
        "color": [BRAND],
        "tooltip": {"trigger": "axis"},
        "grid": {"left": 46, "right": 24, "top": 26, "bottom": 54, "containLabel": True},
        "xAxis": {"type": "category", "data": labels, "axisLabel": axis_text()},
        "yAxis": {"type": "value", "name": name, "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
        "series": [{"name": name, "type": "line", "smooth": True, "symbolSize": 5, "data": values}],
    }


def simple_bar(labels: list[str], values: list[Any], name: str) -> dict[str, Any]:
    return {
        "color": [BRAND],
        "tooltip": {"trigger": "axis"},
        "grid": {"left": 42, "right": 24, "top": 26, "bottom": 44, "containLabel": True},
        "xAxis": {"type": "category", "data": labels, "axisLabel": axis_text()},
        "yAxis": {"type": "value", "name": name, "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
        "series": [{"type": "bar", "data": values, "barMaxWidth": 22}],
    }


def stacked_bar_option(labels: list[str], series: list[tuple[str, list[Any]]]) -> dict[str, Any]:
    return {
        "color": PALETTE,
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
        "legend": {"top": 0, "textStyle": axis_text()},
        "grid": {"left": 46, "right": 24, "top": 34, "bottom": 54, "containLabel": True},
        "xAxis": {"type": "category", "data": labels, "axisLabel": axis_text()},
        "yAxis": {"type": "value", "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
        "series": [{"name": name, "type": "bar", "stack": "total", "data": values, "barMaxWidth": 18} for name, values in series],
    }


def grouped_bar_option(labels: list[str], series: list[tuple[str, list[Any]]]) -> dict[str, Any]:
    return {
        "color": PALETTE,
        "tooltip": {"trigger": "axis"},
        "legend": {"top": 0, "textStyle": axis_text()},
        "grid": {"left": 46, "right": 24, "top": 34, "bottom": 44, "containLabel": True},
        "xAxis": {"type": "category", "data": labels, "axisLabel": axis_text()},
        "yAxis": {"type": "value", "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
        "series": [{"name": name, "type": "bar", "data": values, "barMaxWidth": 22} for name, values in series],
    }


def horizontal_bar(rows: list[dict[str, Any]], name_key: str, value_key: str, unit: str) -> dict[str, Any]:
    labels = [str(row.get(name_key) or "") for row in rows][::-1]
    values = [row.get(value_key) or 0 for row in rows][::-1]
    return {
        "color": [BRAND],
        "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}, "valueFormatter": f"function(v){{return v + '{unit}'}}"},
        "grid": {"left": 128, "right": 24, "top": 24, "bottom": 36, "containLabel": True},
        "xAxis": {"type": "value", "axisLabel": axis_text(), "splitLine": {"lineStyle": {"color": "#e8e6dc"}}},
        "yAxis": {"type": "category", "data": labels, "axisLabel": {**axis_text(), "width": 112, "overflow": "truncate"}},
        "series": [{"type": "bar", "data": values, "barMaxWidth": 14}],
    }


def pie_option(rows: list[dict[str, Any]], value_key: str) -> dict[str, Any]:
    return {
        "color": PALETTE,
        "tooltip": {"trigger": "item"},
        "legend": {"bottom": 0, "textStyle": axis_text()},
        "series": [
            {
                "type": "pie",
                "radius": ["42%", "68%"],
                "center": ["50%", "44%"],
                "avoidLabelOverlap": True,
                "label": {"formatter": "{b}: {d}%"},
                "data": [{"name": row.get("name"), "value": row.get(value_key) or 0} for row in rows],
            }
        ],
    }


def treemap_data(rows: list[dict[str, Any]], value_key: str, max_items: int = 14) -> list[dict[str, Any]]:
    compact_rows = [
        {"name": str(row.get("name") or "未分类"), "value": row.get(value_key) or 0}
        for row in rows
        if (row.get(value_key) or 0) > 0
    ]
    if len(compact_rows) <= max_items:
        return compact_rows
    head = compact_rows[: max_items - 1]
    other_value = sum(row["value"] for row in compact_rows[max_items - 1 :])
    if other_value:
        head.append({"name": "其他", "value": other_value})
    return head


def treemap_option(rows: list[dict[str, Any]], value_key: str) -> dict[str, Any]:
    return {
        "color": PALETTE,
        "tooltip": {"formatter": TREEMAP_TOOLTIP_FORMATTER},
        "series": [
            {
                "type": "treemap",
                "left": 0,
                "right": 0,
                "top": 0,
                "bottom": 0,
                "width": "100%",
                "height": "100%",
                "roam": False,
                "nodeClick": False,
                "visibleMin": 1,
                "squareRatio": 1.12,
                "breadcrumb": {"show": False},
                "label": {
                    "show": True,
                    "color": "#faf9f5",
                    "fontSize": 13,
                    "fontWeight": 600,
                    "lineHeight": 17,
                    "overflow": "break",
                    "minMargin": 4,
                    "formatter": TREEMAP_LABEL_FORMATTER,
                },
                "labelLayout": TREEMAP_LABEL_LAYOUT,
                "upperLabel": {"show": False},
                "itemStyle": {"borderColor": "#faf9f5", "borderWidth": 3, "gapWidth": 2},
                "emphasis": {"label": {"show": True}},
                "data": treemap_data(rows, value_key),
            }
        ],
    }


def radar_option(rows: list[dict[str, Any]]) -> dict[str, Any]:
    selected = rows[:8]
    max_value = max([row.get("hours") or 0 for row in selected] or [1])
    return {
        "color": [BRAND],
        "tooltip": {},
        "radar": {
            "indicator": [{"name": row["name"], "max": max_value * 1.15} for row in selected],
            "axisName": axis_text(),
            "splitLine": {"lineStyle": {"color": "#e8e6dc"}},
            "splitArea": {"areaStyle": {"color": ["#faf9f5", "#f5f4ed"]}},
            "axisLine": {"lineStyle": {"color": "#e8e6dc"}},
        },
        "series": [{"type": "radar", "areaStyle": {"color": "#E4ECF5"}, "data": [{"value": [row.get("hours") or 0 for row in selected], "name": "阅读小时"}]}],
    }


def build_tables(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "topNoteBooks": data["notes"]["topBooks"][:10],
        "topReadBooks": data["reading"]["topBooks"][:10],
        "coverage": [{"name": key, "value": value} for key, value in data.get("coverage", {}).items()],
    }


def build_insights(data: dict[str, Any]) -> list[str]:
    kpis = data["kpis"]
    insights = [
        f"近两年累计阅读 {kpis['totalReadTime']}，有效阅读 {kpis['readDays']} 天。",
        f"书架共有 {kpis['shelfTotal']} 个条目，其中电子书 {kpis['ebookCount']} 本、有声/专辑 {kpis['albumCount']} 个、文章收藏入口 {kpis['mpCount']} 个。",
        f"有笔记的书 {kpis['notebookBooks']} 本，笔记总量 {kpis['noteTotal']} 条；本次抓取到近两年划线 {kpis['highlightsFetchedInRange']} 条、想法/点评 {kpis['reviewsFetchedInRange']} 条用于语义分析。",
    ]
    if data["reading"]["topBooks"]:
        top = data["reading"]["topBooks"][0]
        insights.append(f"月度记录中读得最久的是《{top['title']}》，累计约 {top['hours']} 小时。")
    if data["reading"]["categories"]:
        top_cat = data["reading"]["categories"][0]
        insights.append(f"年度偏好聚合中，最高分类是「{top_cat['name']}」，约 {top_cat['hours']} 小时。")
    return insights


def build_html(data: dict[str, Any]) -> str:
    report_title = data["meta"].get("title") or "微信读书个人可视化报告"
    report_subtitle = data["meta"].get("subtitle") or "把近两年的阅读时间、书架资产、内容偏好和笔记语义放在同一张纸面上：先看节律，再看兴趣，最后看留下来的句子。"
    report_eyebrow = data["meta"].get("eyebrow") or "WeRead Personal Analytics"
    overview_copy = data["meta"].get("overviewCopy") or "这里的数字来自微信读书账户数据。阅读时长按秒计算后转成人类可读格式，书架总数包含电子书、有声/专辑和文章收藏入口。"
    portrait = data.get("readerPortrait") or {}
    golden_quote = portrait.get("goldenQuote") or {}
    poetic_summary = portrait.get("poeticSummary") or ""
    charts_json = json.dumps(data["charts"], ensure_ascii=False).replace("</", "<\\/")
    data_json = json.dumps(
        {
            "meta": data["meta"],
            "kpis": data["kpis"],
            "tables": data["tables"],
            "insights": data["insights"],
            "coverage": data["coverage"],
            "readerPortrait": portrait,
        },
        ensure_ascii=False,
    ).replace("</", "<\\/")
    chart_card_items = [
        f"""
        <article class="chart-card chart-card--{escape_html(chart.get('kind') or 'custom')}" data-chart-card="{chart['id']}">
          <div class="chart-head">
            <div>
              <h3>{escape_html(chart['title'])}</h3>
              <p>{escape_html(chart['subtitle'])}</p>
            </div>
            <span>{escape_html(chart['source'])}</span>
          </div>
          <div class="chart" id="{chart['id']}"></div>
          <div class="empty-state" data-empty-for="{chart['id']}">当前接口没有返回足够数据，已保留模块位置。</div>
        </article>
        """
        for chart in data["charts"]
    ]
    groups = {
        "time": "\n".join(chart_card_items[0:7]),
        "reading": "\n".join(chart_card_items[7:14]),
        "shelf": "\n".join(chart_card_items[14:20]),
        "notes": "\n".join(chart_card_items[20:]),
    }
    kpi_cards = "\n".join(
        f"""<div class="metric"><span class="metric-value">{escape_html(str(value))}</span><span class="metric-label">{escape_html(label)}</span></div>"""
        for label, value in [
            ("阅读时长", data["kpis"]["totalReadTime"]),
            ("有效阅读日", data["kpis"]["readDays"]),
            ("书架条目", data["kpis"]["shelfTotal"]),
            ("笔记总量", data["kpis"]["noteTotal"]),
            ("有笔记书籍", data["kpis"]["notebookBooks"]),
            ("语义文本", data["kpis"]["highlightsFetchedInRange"] + data["kpis"]["reviewsFetchedInRange"]),
        ]
    )
    insights = "\n".join(f"<li>{escape_html(item)}</li>" for item in data["insights"])
    top_notes = "\n".join(
        f"<tr><td>{idx + 1}</td><td>{escape_html(row['title'])}</td><td>{escape_html(row.get('author') or '')}</td><td>{row['total']}</td><td>{row['highlightCount']}</td><td>{row['reviewCount']}</td><td>{row['bookmarkCount']}</td></tr>"
        for idx, row in enumerate(data["tables"]["topNoteBooks"])
    )
    top_reads = "\n".join(
        f"<tr><td>{idx + 1}</td><td>{escape_html(row['title'])}</td><td>{escape_html(row.get('author') or '')}</td><td>{row['hours']}</td></tr>"
        for idx, row in enumerate(data["tables"]["topReadBooks"])
    )
    coverage = "\n".join(f"<tr><td>{escape_html(row['name'])}</td><td>{escape_html(str(row['value']))}</td></tr>" for row in data["tables"]["coverage"])
    meta_tags = [
        ("范围", data["meta"]["range"]),
        ("生成", data["meta"]["generatedAt"]),
        ("图表", f"{len(data['charts'])} 个模块"),
    ]
    if data["meta"].get("persona"):
        meta_tags.append(("画像", data["meta"]["persona"]))
    meta_badges = "\n".join(f'<span class="tag">{escape_html(label)}：{escape_html(str(value))}</span>' for label, value in meta_tags)
    golden_quote_html = ""
    if golden_quote:
        quote_source = f"《{golden_quote.get('bookTitle') or '未知书籍'}》"
        if golden_quote.get("author"):
            quote_source += f" · {golden_quote['author']}"
        golden_quote_html = f"""
      <figure class="golden-quote">
        <blockquote>{escape_html(golden_quote.get('text') or '')}</blockquote>
        <figcaption>画像金句 · {escape_html(quote_source)}</figcaption>
      </figure>
        """
    portrait_summary_html = ""
    if poetic_summary:
        portrait_summary_html = f"""
      <div class="portrait-summary">
        <span>读者画像</span>
        <p>{escape_html(poetic_summary)}</p>
      </div>
        """
    quote_items = []
    for quote in portrait.get("quotes") or []:
        source = f"《{quote.get('bookTitle') or '未知书籍'}》"
        if quote.get("author"):
            source += f" · {quote['author']}"
        quote_items.append(
            f"""
        <article class="quote-card">
          <span class="quote-index">{int(quote.get('rank') or 0):02d}</span>
          <p>{escape_html(quote.get('text') or '')}</p>
          <footer>{escape_html(source)}<em>{escape_html(quote.get('reason') or '关联：阅读画像')}</em></footer>
        </article>
            """
        )
    portrait_quotes_html = "\n".join(quote_items) if quote_items else '<div class="quote-empty">当前没有足够划线文本生成画像清单。</div>'
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape_html(report_title)}</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/echarts-wordcloud@2/dist/echarts-wordcloud.min.js"></script>
<style>
  :root {{
    --parchment:#f5f4ed;
    --ivory:#faf9f5;
    --near-black:#141413;
    --dark-warm:#3d3d3a;
    --charcoal:#4d4c48;
    --olive:#5e5d59;
    --stone:#87867f;
    --brand:#1B365D;
    --brand-light:#2D5A8A;
    --border:#e8e6dc;
    --border-soft:#e5e3d8;
    --tag-bg:#E4ECF5;
  }}
  * {{ box-sizing:border-box; }}
  html, body {{ margin:0; background:var(--parchment); color:var(--near-black); overflow-x:hidden; }}
  body {{
    font-family:"Inter","Source Han Sans SC","Noto Sans CJK SC",-apple-system,BlinkMacSystemFont,"PingFang SC",Arial,sans-serif;
    line-height:1.5;
  }}
  h1, h2, h3, .serif {{
    font-family:"TsangerJinKai02","Source Han Serif SC","Noto Serif CJK SC","Songti SC",Georgia,serif;
    font-weight:500;
    letter-spacing:0;
  }}
  .page {{ max-width:1240px; margin:0 auto; padding:40px 28px 72px; overflow-x:hidden; }}
  .cover {{
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    border-bottom:1px solid var(--border);
    padding:48px 0 34px;
  }}
  .cover > div, .section-title, .insights, .metric, .chart-card {{ min-width:0; }}
  .eyebrow {{ color:var(--brand); font-size:13px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:18px; }}
  h1 {{ font-size:clamp(38px, 6vw, 76px); line-height:1.08; margin:0 0 22px; max-width:920px; }}
  .subtitle {{ max-width:760px; color:var(--olive); font-size:20px; line-height:1.5; margin:0; }}
  .meta-line {{ display:flex; flex-wrap:wrap; gap:10px; color:var(--stone); font-size:14px; margin-top:30px; }}
  .tag {{ background:var(--tag-bg); color:var(--brand); border-radius:4px; padding:4px 8px; }}
  .portrait-summary {{ max-width:860px; margin-top:30px; padding-left:16px; border-left:3px solid var(--brand); }}
  .portrait-summary span {{ display:block; color:var(--brand); font-size:12px; letter-spacing:.08em; text-transform:uppercase; margin-bottom:8px; }}
  .portrait-summary p {{ margin:0; color:var(--dark-warm); font-family:"TsangerJinKai02","Source Han Serif SC","Noto Serif CJK SC","Songti SC",serif; font-size:24px; line-height:1.58; }}
  .golden-quote {{ max-width:820px; margin:26px 0 0; padding:0; }}
  .golden-quote blockquote {{ margin:0; color:var(--near-black); font-family:"TsangerJinKai02","Source Han Serif SC","Noto Serif CJK SC","Songti SC",serif; font-size:28px; line-height:1.45; }}
  .golden-quote figcaption {{ margin-top:10px; color:var(--stone); font-size:13px; }}
  section {{ padding:42px 0; border-bottom:1px solid var(--border); }}
  .section-title {{ border-left:3px solid var(--brand); padding-left:12px; margin-bottom:18px; }}
  .section-title h2 {{ margin:0; font-size:28px; line-height:1.2; }}
  .section-title p {{ margin:7px 0 0; color:var(--olive); max-width:760px; }}
  .metrics {{ display:grid; grid-template-columns:repeat(6, minmax(0, 1fr)); gap:12px; margin:28px 0 22px; }}
  .metric {{ background:var(--ivory); border:1px solid var(--border); border-radius:8px; padding:16px 16px 14px; min-height:92px; }}
  .metric-value {{ display:block; color:var(--brand); font-family:"TsangerJinKai02","Source Han Serif SC",serif; font-size:28px; line-height:1.05; overflow-wrap:anywhere; }}
  .metric-label {{ display:block; color:var(--olive); font-size:13px; margin-top:8px; }}
  .insights {{ background:var(--ivory); border:1px solid var(--border); border-radius:8px; padding:22px 24px; }}
  .insights ul {{ margin:0; padding-left:22px; }}
  .insights li {{ margin:7px 0; color:var(--charcoal); }}
  .chart-grid {{ display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:18px; align-items:stretch; }}
  .chart-card {{ background:var(--ivory); border:1px solid var(--border); border-radius:8px; padding:16px; min-width:0; overflow:hidden; display:flex; flex-direction:column; }}
  .chart-head {{ display:flex; justify-content:space-between; gap:16px; align-items:flex-start; margin-bottom:8px; min-height:64px; }}
  .chart-head > div {{ min-width:0; }}
  .chart-head h3 {{ margin:0 0 5px; font-size:18px; line-height:1.2; color:var(--near-black); }}
  .chart-head p {{ margin:0; color:var(--olive); font-size:13px; line-height:1.35; }}
  .chart-head span {{ flex:0 0 auto; max-width:180px; color:var(--stone); font-size:11px; line-height:1.3; text-align:right; overflow-wrap:anywhere; }}
  .chart {{ height:320px; width:100%; min-width:0; flex:0 0 auto; }}
  .chart-card--treemap .chart, .chart-card--word-cloud .chart {{ height:348px; }}
  .empty-state {{ display:none; height:300px; align-items:center; justify-content:center; color:var(--stone); border:1px dashed var(--border); border-radius:6px; text-align:center; padding:20px; }}
  .chart-card.is-empty .chart {{ display:none; }}
  .chart-card.is-empty .empty-state {{ display:flex; }}
  .table-wrap {{ overflow:auto; background:var(--ivory); border:1px solid var(--border); border-radius:8px; margin-top:16px; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; }}
  th, td {{ padding:10px 12px; border-bottom:1px solid var(--border-soft); text-align:left; white-space:nowrap; }}
  th {{ color:var(--brand); font-weight:600; background:#f0eee6; }}
  td {{ color:var(--charcoal); }}
  .appendix {{ display:grid; grid-template-columns:1.2fr .8fr; gap:18px; }}
  .note {{ color:var(--olive); background:var(--ivory); border:1px solid var(--border); border-radius:8px; padding:18px 20px; }}
  .note p {{ margin:0 0 10px; }}
  .quote-grid {{ display:grid; grid-template-columns:repeat(2, minmax(0, 1fr)); gap:14px; }}
  .quote-card {{ position:relative; min-width:0; background:var(--ivory); border:1px solid var(--border); border-radius:8px; padding:18px 18px 16px 54px; }}
  .quote-index {{ position:absolute; left:18px; top:20px; color:var(--brand); font-family:"TsangerJinKai02","Source Han Serif SC",serif; font-size:18px; line-height:1; }}
  .quote-card p {{ margin:0; color:var(--near-black); font-family:"TsangerJinKai02","Source Han Serif SC","Noto Serif CJK SC","Songti SC",serif; font-size:19px; line-height:1.55; }}
  .quote-card footer {{ margin-top:12px; color:var(--stone); font-size:12px; line-height:1.45; }}
  .quote-card footer em {{ display:block; margin-top:4px; color:var(--olive); font-style:normal; overflow-wrap:anywhere; }}
  .quote-empty {{ background:var(--ivory); border:1px dashed var(--border); border-radius:8px; padding:22px; color:var(--stone); }}
  @media (max-width: 920px) {{
    .page {{ padding:28px 16px 52px; }}
    h1 {{ max-width:100%; font-size:30px; line-height:1.18; white-space:normal; word-break:break-all; overflow-wrap:anywhere; }}
    .subtitle {{ max-width:100%; font-size:18px; white-space:normal; word-break:break-all; overflow-wrap:anywhere; }}
    .metrics {{ grid-template-columns:repeat(2, minmax(0, 1fr)); }}
    .chart-grid {{ grid-template-columns:1fr; }}
    .quote-grid {{ grid-template-columns:1fr; }}
    .appendix {{ grid-template-columns:1fr; }}
    .chart-head {{ display:block; min-height:auto; }}
    .chart-head span {{ display:block; max-width:none; text-align:left; margin-top:8px; }}
  }}
  @media print {{
    .page {{ max-width:none; padding:0; }}
    .chart-card, .metric, .insights, .note, .table-wrap {{ break-inside:avoid; }}
    section {{ break-after:auto; }}
  }}
</style>
</head>
<body>
<main class="page">
  <header class="cover">
    <div>
      <div class="eyebrow">{escape_html(report_eyebrow)}</div>
      <h1>{escape_html(report_title)}</h1>
      <p class="subtitle">{escape_html(report_subtitle)}</p>
      {portrait_summary_html}
      {golden_quote_html}
      <div class="meta-line">{meta_badges}</div>
    </div>
  </header>

  <section>
    <div class="section-title">
      <h2>总览</h2>
      <p>{escape_html(overview_copy)}</p>
    </div>
    <div class="metrics">{kpi_cards}</div>
    <div class="insights"><ul>{insights}</ul></div>
  </section>

  <section>
    <div class="section-title">
      <h2>时间节律</h2>
      <p>月、日、星期三个尺度一起看，能区分持续阅读、阶段性冲刺和短期空窗。</p>
    </div>
    <div class="chart-grid">{groups['time']}</div>
  </section>

  <section>
    <div class="section-title">
      <h2>阅读偏好</h2>
      <p>这部分使用月度读得最久的书和年度偏好字段。年度字段按触达自然年聚合，因此更适合看长期兴趣结构，而不是精确滚动区间。</p>
    </div>
    <div class="chart-grid">{groups['reading']}</div>
  </section>

  <section>
    <div class="section-title">
      <h2>书架资产</h2>
      <p>书架是阅读资产的全量视角：未读、已读、有声、私密、书单和最近活动都在这里。</p>
    </div>
    <div class="chart-grid">{groups['shelf']}</div>
  </section>

  <section>
    <div class="section-title">
      <h2>笔记与语义</h2>
      <p>划线和想法是阅读后真正留下来的东西。词云是高频短语抽取，不等于严格自然语言分词。</p>
    </div>
    <div class="chart-grid">{groups['notes']}</div>
  </section>

  <section>
    <div class="section-title">
      <h2>画像划线清单</h2>
      <p>从近两年划线中挑出最贴近本报告画像的句子。顶部金句来自这组清单的第一条。</p>
    </div>
    <div class="quote-grid">{portrait_quotes_html}</div>
  </section>

  <section>
    <div class="section-title">
      <h2>重点列表</h2>
      <p>用于复核图表背后的具体书名。</p>
    </div>
    <h3>笔记最多的书</h3>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>书名</th><th>作者</th><th>总笔记</th><th>划线</th><th>想法/点评</th><th>书签</th></tr></thead><tbody>{top_notes}</tbody></table></div>
    <h3>读得最久的书</h3>
    <div class="table-wrap"><table><thead><tr><th>#</th><th>书名</th><th>作者</th><th>小时</th></tr></thead><tbody>{top_reads}</tbody></table></div>
  </section>

  <section>
    <div class="section-title">
      <h2>附录</h2>
      <p>数据覆盖、边界和生成口径。</p>
    </div>
    <div class="appendix">
      <div class="note">
        <p><strong>口径说明</strong></p>
        <p>{escape_html(data['meta']['dataCaveat'])}</p>
        <p>书签内容当前不能通过接口导出，报告只展示书签数量。词云只使用你自己的划线与想法文本，不包含书籍正文。</p>
      </div>
      <div class="table-wrap"><table><thead><tr><th>覆盖项</th><th>数量</th></tr></thead><tbody>{coverage}</tbody></table></div>
    </div>
  </section>
</main>
<script>
const REPORT_CONTEXT = {data_json};
const CHARTS = {charts_json};
const CHART_REGISTRY = [];
const CHART_OBSERVER = window.ResizeObserver ? new ResizeObserver((entries) => {{
  entries.forEach((entry) => {{
    const chart = entry.target.__wereadChart;
    if (chart) chart.resize();
  }});
}}) : null;
function reviveFunctions(option) {{
  if (!option || typeof option !== 'object') return option;
  for (const key of Object.keys(option)) {{
    const value = option[key];
    if (typeof value === 'string' && value.startsWith('function(')) {{
      try {{ option[key] = new Function('return (' + value + ')')(); }} catch (err) {{}}
    }} else if (value && typeof value === 'object') {{
      reviveFunctions(value);
    }}
  }}
  return option;
}}
function resizeCharts() {{
  CHART_REGISTRY.forEach(chart => chart.resize());
}}
function scheduleChartResize() {{
  window.requestAnimationFrame(resizeCharts);
  window.setTimeout(resizeCharts, 180);
}}
function bootCharts() {{
  if (!window.echarts) {{
    document.querySelectorAll('.chart-card').forEach(card => card.classList.add('is-empty'));
    return;
  }}
  CHARTS.forEach(item => {{
    const el = document.getElementById(item.id);
    const card = document.querySelector(`[data-chart-card="${{item.id}}"]`);
    if (!el || !card) return;
    if (item.empty) {{
      card.classList.add('is-empty');
      return;
    }}
    const chart = echarts.init(el, null, {{ renderer: 'canvas' }});
    chart.setOption(reviveFunctions(item.option));
    el.__wereadChart = chart;
    CHART_REGISTRY.push(chart);
    if (CHART_OBSERVER) CHART_OBSERVER.observe(el);
  }});
  scheduleChartResize();
}}
bootCharts();
window.addEventListener('resize', scheduleChartResize, {{ passive: true }});
if (document.fonts && document.fonts.ready) {{
  document.fonts.ready.then(scheduleChartResize).catch(() => {{}});
}}
</script>
</body>
</html>
"""


def escape_html(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def validate_output(html: str, data: dict[str, Any]) -> list[str]:
    errors = []
    if len(data.get("charts") or []) < 20:
        errors.append("expected at least 20 chart modules")
    forbidden = ["WEREAD_API_KEY", "TODO", "{{文档", "__API_KEY__"]
    for token in forbidden:
        if token in html:
            errors.append(f"forbidden token in HTML: {token}")
    for chart in data.get("charts") or []:
        option = chart.get("option") or {}
        for series in option.get("series") or []:
            if not isinstance(series, dict) or series.get("type") != "treemap":
                continue
            if any(series.get(edge) != 0 for edge in ("left", "right", "top", "bottom")):
                errors.append(f"treemap must fill chart bounds: {chart.get('title')}")
            label = series.get("label") or {}
            if not label.get("formatter") or not series.get("labelLayout"):
                errors.append(f"treemap label guard missing: {chart.get('title')}")
    portrait = data.get("readerPortrait") or {}
    quotes = portrait.get("quotes") or []
    golden_quote = portrait.get("goldenQuote")
    if data.get("meta", {}).get("sampleReport") and len(quotes) < 20:
        errors.append("sample report expected 20 portrait quotes")
    if quotes and (not golden_quote or golden_quote.get("text") != quotes[0].get("text")):
        errors.append("golden quote must be the first portrait quote")
    if quotes and "画像划线清单" not in html:
        errors.append("portrait quote section missing in HTML")
    return errors


def write_outputs(output_dir: Path, data: dict[str, Any]) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    html = "\n".join(line.rstrip() for line in build_html(data).splitlines()) + "\n"
    errors = validate_output(html, data)
    if errors:
        raise SystemExit("Output validation failed:\n" + "\n".join(f"- {item}" for item in errors))
    html_path = output_dir / "weread-report.html"
    data_path = output_dir / "weread-report-data.json"
    summary_path = output_dir / "weread-raw-summary.json"
    html_path.write_text(html, encoding="utf-8")
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {
        "meta": data["meta"],
        "kpis": data["kpis"],
        "coverage": data["coverage"],
        "chartCount": len(data["charts"]),
        "portraitQuoteCount": data.get("readerPortrait", {}).get("quoteCount", 0),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return html_path, data_path, summary_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a personal WeRead visual report.")
    parser.add_argument("--years", type=int, default=2, help="Default lookback years when --start is not supplied.")
    parser.add_argument("--start", help="Start date YYYY-MM-DD.")
    parser.add_argument("--end", help="End date YYYY-MM-DD.")
    parser.add_argument("--output", default="reports/generated", help="Output directory.")
    parser.add_argument("--max-note-books", type=int, default=0, help="Max notebook books for highlight/thought detail. 0 means all.")
    parser.add_argument("--workers", type=int, default=6, help="Parallel workers for note detail calls.")
    parser.add_argument("--sample-ai-founder", action="store_true", help="Generate an AI-founder sample reader report without calling WeRead APIs.")
    parser.add_argument("--sample-scale", type=int, default=5, help="Scale factor for sample data.")
    parser.add_argument("--synthetic-ai-founder", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--synthetic-scale", type=int, help=argparse.SUPPRESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report_range = default_range(args.years, args.start, args.end)
    if args.sample_ai_founder or args.synthetic_ai_founder:
        sample_scale = args.synthetic_scale or args.sample_scale
        print(f"正在生成 AI 创业者示例报告：{report_range.label}...")
        data = build_synthetic_ai_founder_report(report_range, sample_scale)
        html_path, data_path, summary_path = write_outputs(Path(args.output), data)
        print(f"HTML: {html_path}")
        print(f"DATA: {data_path}")
        print(f"SUMMARY: {summary_path}")
        print(f"CHARTS: {len(data['charts'])}")
        return 0

    api_key = os.environ.get("WEREAD_API_KEY")
    if not api_key:
        print("未设置 WEREAD_API_KEY。请先执行：export WEREAD_API_KEY=<你的_WEREAD_API_KEY>", file=sys.stderr)
        return 2
    client = WeReadClient(api_key)

    print(f"Fetching WeRead data for {report_range.label}...")
    shelf = client.call("/shelf/sync")
    monthly, daily = fetch_monthly_stats(client, report_range)
    annual = fetch_annual_stats(client, report_range)
    notebooks = fetch_notebooks(client)

    selected = sorted(notebooks, key=notebook_total, reverse=True)
    if args.max_note_books and args.max_note_books > 0:
        selected = selected[: args.max_note_books]
    print(f"Fetching note details for {len(selected)} notebook books...")
    note_details: list[dict[str, Any]] = []
    note_errors = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        future_map = {executor.submit(fetch_note_detail, client, item): item for item in selected}
        for idx, future in enumerate(concurrent.futures.as_completed(future_map), start=1):
            try:
                detail = future.result()
            except Exception as exc:  # noqa: BLE001
                note_errors += 1
                detail = {"bookId": "", "highlights": [], "reviews": [], "errors": [str(exc)]}
            if detail.get("errors"):
                note_errors += len(detail["errors"])
            note_details.append(detail)
            if idx % 25 == 0 or idx == len(selected):
                print(f"  note detail progress: {idx}/{len(selected)}")

    data = aggregate(report_range, shelf, monthly, daily, annual, notebooks, note_details, note_errors)
    html_path, data_path, summary_path = write_outputs(Path(args.output), data)
    print(f"HTML: {html_path}")
    print(f"DATA: {data_path}")
    print(f"SUMMARY: {summary_path}")
    print(f"CHARTS: {len(data['charts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
