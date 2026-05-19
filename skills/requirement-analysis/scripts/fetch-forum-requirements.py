#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从论坛 webhook 采集原始需求数据。

说明：
- 该脚本不直接访问论坛网页，而是通过内部 n8n webhook 拉取帖子列表和详情。
- 当接口异常或返回非预期结构时，脚本会明确提示联系吴荣杰排查论坛接口。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from load_local_sources import load_forum_config, require_keys


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "outputs"
PROGRESS_FILE = SCRIPT_DIR / "forum_progress.json"
FORUM_CONFIG = load_forum_config()
THREAD_API = FORUM_CONFIG["thread_api"]
DETAIL_API = FORUM_CONFIG["detail_api"]
CONTACT_HINT = FORUM_CONFIG["contact_hint"]


def load_progress() -> set[str]:
    if not PROGRESS_FILE.exists():
        return set()
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return set(str(item) for item in data.get("processed_ids", []))
    except Exception:
        return set()


def save_progress(processed_ids: set[str]) -> None:
    PROGRESS_FILE.write_text(
        json.dumps(
            {
                "processed_ids": sorted(processed_ids),
                "last_updated": datetime.now().isoformat(timespec="seconds"),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def request_json(url: str, *, params: dict[str, Any] | None = None) -> Any:
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_threads(days: int, offset: int, limit: int, hot_value: int) -> list[dict[str, Any]]:
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    payload = {
        "startTs": int(start_time.timestamp()),
        "endTs": int(end_time.timestamp()),
        "offset": offset,
        "limit": limit,
        "hot_value": hot_value,
    }
    result = request_json(THREAD_API, params=payload)
    data = result.get("data", result) if isinstance(result, dict) else result

    if not isinstance(data, list):
        raise RuntimeError(
            f"论坛列表接口返回结构异常，未获得帖子数组。{CONTACT_HINT}"
        )

    if data and isinstance(data[0], dict) and "headers" in data[0] and "webhookUrl" in data[0]:
        raise RuntimeError(
            f"论坛列表接口返回的是 webhook 调试数据，不是帖子列表。{CONTACT_HINT}"
        )

    return data


def fetch_thread_detail(thread_id: str) -> dict[str, Any] | None:
    result = request_json(DETAIL_API, params={"thread_id": thread_id})
    data = result.get("data", result) if isinstance(result, dict) else result
    if isinstance(data, list) and data:
        first_post = data[0]
        if isinstance(first_post, dict):
            return first_post
    return None


def normalize_thread(thread: dict[str, Any], detail: dict[str, Any] | None) -> dict[str, Any]:
    content = ""
    if detail:
        content = (
            detail.get("message_fmt")
            or detail.get("message")
            or ""
        )

    thread_id = str(thread.get("id", ""))
    return {
        "source": "deepin-forum",
        "source_label": "deepin 论坛",
        "record_id": thread_id,
        "url": f"https://bbs.deepin.org/post/{thread_id}" if thread_id else "",
        "title": thread.get("subject", ""),
        "content": content,
        "author": str(thread.get("user_id", "")),
        "publish_time": thread.get("created_at", "") or "",
        "category": "论坛",
        "likes": thread.get("like_cnt", 0) or 0,
        "views": thread.get("views_cnt", 0) or 0,
        "replies": thread.get("posts_cnt", 0) or 0,
        "hot_value": thread.get("hot_value", 0) or 0,
        "forum_id": thread.get("forum_id"),
        "raw_thread": thread,
        "raw_detail": detail or {},
    }


def collect(days: int, max_count: int, hot_value: int, only_new: bool) -> list[dict[str, Any]]:
    processed_ids = load_progress()
    new_ids: list[str] = []
    results: list[dict[str, Any]] = []
    offset = 0
    page_size = min(max(max_count, 1), 100)

    while len(results) < max_count:
        threads = fetch_threads(days, offset, page_size, hot_value)
        if not threads:
            break

        for thread in threads:
            thread_id = str(thread.get("id", ""))
            if not thread_id:
                continue
            if only_new and thread_id in processed_ids:
                continue

            detail = fetch_thread_detail(thread_id)
            results.append(normalize_thread(thread, detail))
            new_ids.append(thread_id)

            if len(results) >= max_count:
                break

        offset += page_size

    if new_ids:
        processed_ids.update(new_ids)
        save_progress(processed_ids)

    return results


def build_output_path(prefix: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return OUTPUT_DIR / f"{prefix}_{ts}.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="采集 deepin 论坛原始需求")
    parser.add_argument("days", nargs="?", type=int, default=30, help="最近多少天，默认 30")
    parser.add_argument("max_count", nargs="?", type=int, default=50, help="最多采集多少条，默认 50")
    parser.add_argument("--hot-value", type=int, default=0, help="论坛热度阈值，默认 0")
    parser.add_argument("--all", action="store_true", help="忽略进度文件，重新采集")
    parser.add_argument("--reset", action="store_true", help="清空进度文件后重新采集")
    parser.add_argument("--output", type=str, help="输出 JSON 路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.reset and PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()

    try:
        require_keys(FORUM_CONFIG, ["thread_api", "detail_api"], "论坛 webhook")
        items = collect(
            days=args.days,
            max_count=args.max_count,
            hot_value=args.hot_value,
            only_new=not args.all and not args.reset,
        )
    except Exception as exc:
        print(f"论坛采集失败: {exc}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else build_output_path("requirements_forum")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已采集 {len(items)} 条论坛需求")
    print(f"输出文件: {output_path}")
    if not items:
        print(f"未获取到论坛需求；如确认近期应有数据，请联系吴荣杰排查论坛接口。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
