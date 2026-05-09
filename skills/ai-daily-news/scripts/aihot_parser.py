#!/usr/bin/env python3
"""
AI HOT 新闻解析工具
从网页抓取返回的纯文本内容中解析 AI HOT 日报或公众号热文。
"""

import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Tuple


SOURCE_KEYWORDS = ["官方", "综合资讯", "X·KOL", "学术机构", "X："]


def parse_daily_text(text: str) -> Tuple[str, List[Dict]]:
    """解析日报页面纯文本。"""
    news_list = []

    vol_match = re.search(r"VOL\.(\d{4})\.(\d{2})\.(\d{2})", text)
    if vol_match:
        date_str = f"{vol_match.group(1)}-{vol_match.group(2)}-{vol_match.group(3)}"
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")

    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if (
            not line
            or "VOL." in line
            or "STORIES" in line
            or "DAILY" in line
            or "星期" in line
            or "今日事件" in line
            or "一手报道" in line
            or "信源" in line
        ):
            i += 1
            continue

        is_source = any(keyword in line for keyword in SOURCE_KEYWORDS)
        if not is_source:
            i += 1
            continue

        source = line
        title = ""
        if i > 0:
            prev_line = lines[i - 1].strip()
            if prev_line and not any(keyword in prev_line for keyword in SOURCE_KEYWORDS):
                title = prev_line

        content_lines = []
        j = i + 1
        while j < len(lines):
            next_line = lines[j].strip()
            if not next_line:
                j += 1
                continue
            if any(keyword in next_line for keyword in SOURCE_KEYWORDS):
                break
            if "今日事件" in next_line or "一手报道" in next_line:
                break
            content_lines.append(next_line)
            j += 1
            if len(content_lines) >= 2:
                break

        content = " ".join(content_lines)
        link = ""
        link_match = re.search(r"https?://[^\s\)\]]+", content)
        if link_match:
            link = link_match.group(0)

        if title and content:
            news_list.append(
                {
                    "title": title,
                    "link": link,
                    "source": source,
                    "content": content,
                    "category": "未分类",
                    "date": date_str,
                }
            )

        i = j

    seen = set()
    unique = []
    for item in news_list:
        key = item["title"][:30]
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return date_str, unique


def parse_mp_text(text: str) -> List[Dict]:
    """解析公众号热文文本。"""
    news_list = []
    lines = text.split("\n")
    current_item = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", line)
        if date_match:
            if current_item and current_item.get("title"):
                news_list.append(current_item)
            current_item = {"date": date_match.group(1)}

            title_match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", line)
            if title_match:
                current_item["title"] = title_match.group(1).strip()
                current_item["link"] = title_match.group(2).strip()
            continue

        if current_item and current_item.get("title"):
            if "原创" in line or (re.match(r"^[\u4e00-\u9fa5]+", line) and not current_item.get("account")):
                current_item["account"] = line.replace("原创", "").strip()
                current_item["is_original"] = "原创" in line
                continue

            if re.match(r"^\d+$", line):
                num = int(line)
                if not current_item.get("views"):
                    current_item["views"] = num
                elif not current_item.get("likes"):
                    current_item["likes"] = num
                elif not current_item.get("shares"):
                    current_item["shares"] = num

    if current_item and current_item.get("title"):
        news_list.append(current_item)

    return news_list


def main():
    import argparse

    parser = argparse.ArgumentParser(description="解析 AI HOT 页面内容")
    parser.add_argument("section", nargs="?", default="daily", choices=["daily", "mp"])
    parser.add_argument("--compact", action="store_true", help="紧凑输出")
    args = parser.parse_args()

    text = sys.stdin.read()
    if args.section == "daily":
        date_str, news_list = parse_daily_text(text)
        result = {
            "section": "daily",
            "date": date_str,
            "fetch_time": datetime.now().isoformat(),
            "count": len(news_list),
            "news": news_list,
        }
    else:
        news_list = parse_mp_text(text)
        result = {
            "section": "mp",
            "fetch_time": datetime.now().isoformat(),
            "count": len(news_list),
            "articles": news_list,
        }

    if args.compact:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
