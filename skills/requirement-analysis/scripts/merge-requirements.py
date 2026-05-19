#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并多个原始需求 JSON 文件。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_items(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("rows"), list):
        return [item for item in data.get("rows", []) if isinstance(item, dict)]
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def dedupe(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    merged: list[dict[str, Any]] = []
    for item in items:
        key = (
            str(item.get("source", "")),
            str(item.get("record_id") or item.get("url") or item.get("title") or ""),
        )
        if key in seen:
            continue
        seen.add(key)
        merged.append(item)
    return merged


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="合并原始需求 JSON")
    parser.add_argument("inputs", nargs="+", help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSON 路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    all_items: list[dict[str, Any]] = []
    for raw_path in args.inputs:
        path = Path(raw_path)
        all_items.extend(load_items(path))

    merged = dedupe(all_items)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"输入文件数: {len(args.inputs)}")
    print(f"合并后条数: {len(merged)}")
    print(f"输出文件: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
