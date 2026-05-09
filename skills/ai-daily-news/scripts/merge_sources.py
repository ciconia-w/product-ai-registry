#!/usr/bin/env python3
"""
合并中文新闻源。
支持把脚本主源、AI HOT、以及必要时的备用 RSS 源合并为统一结果。
"""

import argparse
import json
import sys
from typing import Dict, List


def load_news(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "news" in data:
            return data["news"]
        if "daily" in data and isinstance(data["daily"], dict) and "news" in data["daily"]:
            return data["daily"]["news"]
    raise ValueError(f"unsupported news payload: {path}")


def dedupe_news(primary: List[Dict], secondary: List[Dict]) -> List[Dict]:
    merged = []
    seen = {}
    for source_name, news_list in (("primary", primary), ("secondary", secondary)):
        for item in news_list:
            key = item.get("title", "")[:30]
            if not key:
                continue
            if key not in seen:
                seen[key] = len(merged)
                merged.append(item)
                continue
            existing = merged[seen[key]]
            current_len = len(item.get("content", ""))
            existing_len = len(existing.get("content", ""))
            if current_len > existing_len:
                merged[seen[key]] = item
    return merged


def main():
    parser = argparse.ArgumentParser(description="合并日报中文信源")
    parser.add_argument("--primary", required=True, help="脚本主源 JSON 路径")
    parser.add_argument("--aihot", required=True, help="AI HOT JSON 路径")
    parser.add_argument("--fallback", help="备用中文源 JSON 路径")
    args = parser.parse_args()

    primary_news = load_news(args.primary)
    aihot_news = load_news(args.aihot)
    fallback_news = load_news(args.fallback) if args.fallback else []

    if not aihot_news:
        print("AI HOT news missing; this source is mandatory for the daily workflow", file=sys.stderr)
        raise SystemExit(1)

    if primary_news:
        chinese_news = dedupe_news(primary_news, aihot_news)
        source_summary = {
            "primary": len(primary_news),
            "aihot": len(aihot_news),
        }
    elif fallback_news:
        chinese_news = dedupe_news(fallback_news, aihot_news)
        source_summary = {
            "fallback": len(fallback_news),
            "aihot": len(aihot_news),
        }
    else:
        print("Neither primary nor fallback Chinese source is available", file=sys.stderr)
        raise SystemExit(1)

    result = {
        "count": len(chinese_news),
        "sources": source_summary,
        "news": chinese_news,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
