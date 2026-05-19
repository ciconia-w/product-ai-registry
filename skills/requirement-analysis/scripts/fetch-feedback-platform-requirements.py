#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从产品需求反馈平台采集原始需求数据。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from load_local_sources import load_feedback_platform_config, require_keys


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "outputs"
PROGRESS_FILE = SCRIPT_DIR / "product_progress.json"

API_CONFIG = load_feedback_platform_config()


def load_progress() -> set[str]:
    if not PROGRESS_FILE.exists():
        return set()
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        return set(str(item) for item in data.get("processed_rowids", []))
    except Exception:
        return set()


def save_progress(processed_rowids: set[str]) -> None:
    PROGRESS_FILE.write_text(
        json.dumps({"processed_rowids": sorted(processed_rowids)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def post_json(payload: dict[str, Any]) -> dict[str, Any]:
    require_keys(API_CONFIG, ["base_url", "app_key", "sign", "worksheet_id", "view_id"], "需求反馈平台")
    response = requests.post(API_CONFIG["base_url"], json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(f"需求反馈平台返回失败: {data.get('error_msg') or data.get('error_code')}")
    return data


def strip_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_module_names(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return []
    if isinstance(value, dict):
        value = [value]
    if not isinstance(value, list):
        return []

    names: list[str] = []
    for item in value:
        if isinstance(item, dict) and item.get("name"):
            names.append(str(item["name"]))
    return names


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    description = strip_html(str(row.get("5fb771127addad0b2d846174", "")))
    topic = str(row.get("5fb771127addad0b2d846173", "") or "")
    theme = str(row.get("5fb771127addad0b2d846186", "") or "")
    title = topic or theme or description[:50]
    modules = parse_module_names(row.get("611c9210f57e92b2566ffc2a"))
    row_id = str(row.get("rowid", ""))

    return {
        "source": "feedback-platform",
        "source_label": "产品需求反馈平台",
        "record_id": row_id,
        "url": f"https://cooperation.uniontech.com/worksheet/{API_CONFIG['worksheet_id']}/row/{row_id}",
        "title": title,
        "content": description,
        "author": ((row.get("uaid") or {}).get("fullname") or ""),
        "publish_time": row.get("ctime", "") or "",
        "category": "需求反馈",
        "status": row.get("5fb771127addad0b2d846177", "") or row.get("5fb771127addad0b2d84617c", ""),
        "priority": row.get("61dc112c965f3398ac72ea21", "") or "",
        "module": ", ".join(modules),
        "tags": row.get("5fb771127addad0b2d846184", "") or "",
        "raw_row": row,
    }


def collect(days: int, max_count: int, only_new: bool) -> list[dict[str, Any]]:
    processed_rowids = load_progress()
    new_rowids: list[str] = []
    results: list[dict[str, Any]] = []
    cutoff = datetime.now() - timedelta(days=days)

    page_index = 1
    page_size = 100

    while len(results) < max_count:
        payload = {
            "appKey": API_CONFIG["app_key"],
            "sign": API_CONFIG["sign"],
            "worksheetId": API_CONFIG["worksheet_id"],
            "viewId": API_CONFIG["view_id"],
            "listType": 1,
            "pageSize": page_size,
            "pageIndex": page_index,
            "getSystemControl": False,
        }
        data = post_json(payload)
        rows = data.get("data", {}).get("rows", [])
        if not rows:
            break

        reached_cutoff = False
        for row in rows:
            created_text = str(row.get("ctime", "") or "")
            if created_text:
                try:
                    created_at = datetime.strptime(created_text, "%Y-%m-%d %H:%M:%S")
                    if created_at < cutoff:
                        reached_cutoff = True
                        break
                except ValueError:
                    pass

            row_id = str(row.get("rowid", ""))
            if only_new and row_id and row_id in processed_rowids:
                continue

            results.append(normalize_row(row))
            if row_id:
                new_rowids.append(row_id)

            if len(results) >= max_count:
                break

        if reached_cutoff:
            break
        page_index += 1

    if new_rowids:
        processed_rowids.update(new_rowids[:max_count])
        save_progress(processed_rowids)

    return results[:max_count]


def build_output_path(prefix: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return OUTPUT_DIR / f"{prefix}_{ts}.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="采集产品需求反馈平台原始需求")
    parser.add_argument("days", nargs="?", type=int, default=30, help="最近多少天，默认 30")
    parser.add_argument("max_count", nargs="?", type=int, default=50, help="最多采集多少条，默认 50")
    parser.add_argument("--all", action="store_true", help="忽略进度文件，重新采集")
    parser.add_argument("--reset", action="store_true", help="清空进度文件后重新采集")
    parser.add_argument("--output", type=str, help="输出 JSON 路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.reset and PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()

    try:
        require_keys(API_CONFIG, ["base_url", "app_key", "sign", "worksheet_id", "view_id"], "需求反馈平台")
        items = collect(
            days=args.days,
            max_count=args.max_count,
            only_new=not args.all and not args.reset,
        )
    except Exception as exc:
        print(f"需求反馈平台采集失败: {exc}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else build_output_path("requirements_feedback")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"已采集 {len(items)} 条需求反馈平台需求")
    print(f"输出文件: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
