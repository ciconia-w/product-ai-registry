#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
采集 deepin Home 开放接口中的原始反馈数据。
基于用户提供的本地脚本整理并统一输出结构。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests
from load_local_sources import load_deepin_home_config, require_keys


API_CONFIG = load_deepin_home_config()
BASE_URL = API_CONFIG["base_url"]
APP_KEY = API_CONFIG["app_key"]
SIGN = API_CONFIG["sign"]
WORKSHEET_ID = API_CONFIG["worksheet_id"]

VIEW_IDS = API_CONFIG["view_ids"] or {
    "requirement_feedback": ""
}

SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "outputs"


def api_post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    require_keys(API_CONFIG, ["base_url", "app_key", "sign", "worksheet_id"], "deepin Home 开放接口")
    response = requests.post(f"{BASE_URL}{path}", json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    if not data.get("success"):
        raise RuntimeError(
            f"API request failed: error_code={data.get('error_code')} error_msg={data.get('error_msg')}"
        )
    return data


def get_worksheet_info() -> dict[str, Any]:
    payload = {
        "appKey": APP_KEY,
        "sign": SIGN,
        "worksheetId": WORKSHEET_ID,
    }
    return api_post("/api/v2/open/worksheet/getWorksheetInfo", payload)["data"]


def build_field_map(worksheet_info: dict[str, Any]) -> dict[str, str]:
    field_map = {
        "rowid": "记录ID",
        "ctime": "创建时间",
        "utime": "最近修改时间",
        "caid": "创建人",
        "uaid": "最近修改人",
        "ownerid": "拥有者",
        "ID": "ID",
    }
    for control in worksheet_info.get("controls", []):
        control_id = control.get("controlId")
        control_name = control.get("controlName") or control.get("alias") or control_id
        if control_id:
            field_map[control_id] = control_name
        alias = control.get("alias")
        if alias:
            field_map[alias] = control_name
    return field_map


def fetch_rows(view_id: str, page_size: int, page_index: int) -> list[dict[str, Any]]:
    payload = {
        "appKey": APP_KEY,
        "sign": SIGN,
        "worksheetId": WORKSHEET_ID,
        "viewId": view_id,
        "listType": 1,
        "pageSize": page_size,
        "pageIndex": page_index,
        "getSystemControl": False,
    }
    return api_post("/api/v2/open/worksheet/getFilterRows", payload).get("data", {}).get("rows", [])


def normalize_row(row: dict[str, Any], field_map: dict[str, str]) -> dict[str, Any]:
    normalized = {}
    for key, value in row.items():
        normalized[field_map.get(key, key)] = value
    title = str(normalized.get("标题") or normalized.get("标题描述3") or "")
    content = str(normalized.get("内容") or normalized.get("标题描述2") or "")
    record_id = str(normalized.get("记录ID") or "")
    return {
        "source": "deepin-home-openapi",
        "source_label": "deepin Home 开放接口",
        "record_id": record_id,
        "url": str(normalized.get("论坛帖子链接") or f"https://cooperation.uniontech.com/worksheet/{WORKSHEET_ID}/row/{record_id}" if record_id else ""),
        "title": title,
        "content": content,
        "author": (
            (normalized.get("创建人") or {}).get("fullname")
            if isinstance(normalized.get("创建人"), dict)
            else str(normalized.get("创建人") or "")
        ),
        "publish_time": str(normalized.get("创建时间") or normalized.get("创建日期") or ""),
        "category": str(normalized.get("类型") or "deepin Home"),
        "likes": int(normalized.get("收藏数") or 0),
        "views": 0,
        "replies": int(normalized.get("催促数") or 0),
        "module": str(normalized.get("所属模块") or ""),
        "status": str(normalized.get("需求状态") or normalized.get("BUG状态") or ""),
        "system_version": str(normalized.get("系统版本") or ""),
        "raw_row": normalized,
    }


def build_output_path(prefix: str) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR / f"{prefix}.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch rows from deepin Home open API.")
    parser.add_argument("--view", default="requirement_feedback", choices=sorted(VIEW_IDS.keys()))
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--raw", action="store_true", help="Keep original field names instead of unified requirement schema.")
    parser.add_argument(
        "--output",
        default=str(build_output_path("requirements_deepin_home")),
        help="Output JSON path.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        require_keys(API_CONFIG, ["base_url", "app_key", "sign", "worksheet_id"], "deepin Home 开放接口")
        worksheet_info = get_worksheet_info()
        field_map = build_field_map(worksheet_info)
        view_id = VIEW_IDS[args.view]
        if not view_id:
            raise RuntimeError(f"deepin Home 开放接口缺少视图配置: {args.view}")

        rows: list[dict[str, Any]] = []
        for page_index in range(1, args.pages + 1):
            page_rows = fetch_rows(view_id=view_id, page_size=args.page_size, page_index=page_index)
            if not page_rows:
                break
            rows.extend(page_rows)
            if len(page_rows) < args.page_size:
                break

        if args.raw:
            output_rows = [{field_map.get(k, k): v for k, v in row.items()} for row in rows]
        else:
            output_rows = [normalize_row(row, field_map) for row in rows]

        output = {
            "worksheet": worksheet_info.get("name"),
            "worksheet_id": WORKSHEET_ID,
            "view": args.view,
            "view_id": view_id,
            "row_count": len(output_rows),
            "rows": output_rows,
        }

        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"saved {len(output_rows)} rows to {output_path}")
        return 0
    except Exception as exc:
        print(f"deepin Home 开放接口采集失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
