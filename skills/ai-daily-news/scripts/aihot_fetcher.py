#!/usr/bin/env python3
"""
AI HOT 抓取器
直接抓取 aihot.virxact.com 并输出结构化 JSON。
如果直接抓取被目标环境拦截，可改用 agent 的网页抓取能力，再把纯文本交给 aihot_parser.py。
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

from aihot_parser import parse_daily_text, parse_mp_text

SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "references" / "sources.yaml"
DEFAULT_DAILY_URL = "https://aihot.virxact.com/daily"
DEFAULT_MP_URL = "https://aihot.virxact.com/mp"


def load_aihot_urls():
    daily_url = DEFAULT_DAILY_URL
    mp_url = DEFAULT_MP_URL
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        chinese_sources = config.get("sources", {}).get("chinese", {})
        for source in chinese_sources.get("primary", []):
            if source.get("parser") == "aihot_fetcher.py":
                daily_url = source.get("url", daily_url)
        for source in chinese_sources.get("supplemental", []):
            if source.get("name") == "AI HOT MP":
                mp_url = source.get("url", mp_url)
    except Exception as e:
        print(f"Warning: failed to load AI HOT config: {e}", file=sys.stderr)
    return daily_url, mp_url


def fetch_text(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://aihot.virxact.com/",
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text("\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="抓取 AI HOT 页面并输出 JSON")
    parser.add_argument("section", nargs="?", default="daily", choices=["daily", "mp", "all"])
    args = parser.parse_args()

    daily_url, mp_url = load_aihot_urls()
    result = {
        "source": "aihot.virxact.com",
        "fetch_time": datetime.now().isoformat(),
    }

    try:
        if args.section in ("daily", "all"):
            text = fetch_text(daily_url)
            date_str, news_list = parse_daily_text(text)
            result["daily"] = {
                "date": date_str,
                "count": len(news_list),
                "news": news_list,
            }
        if args.section in ("mp", "all"):
            text = fetch_text(mp_url)
            articles = parse_mp_text(text)
            result["mp"] = {
                "count": len(articles),
                "articles": articles,
            }
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
