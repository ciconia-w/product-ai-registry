#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将统一中间格式写入飞书 spreadsheet。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from config_paths import LOCAL_FEISHU_TARGET


SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_SNAPSHOT_PATH = SCRIPT_DIR / "feishu-table-schema.snapshot.json"
DELIVERY_SCHEMA_PATH = SCRIPT_DIR / "requirements_delivery_schema.json"


def run_json(cmd: list[str]) -> dict:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout).strip() or "command failed")
    text = (result.stdout or "").strip()
    return json.loads(text) if text else {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="写入飞书表")
    parser.add_argument("--input", required=True, help="统一交付 JSON 路径")
    parser.add_argument("--dry-run", action="store_true", help="只打印待写入 payload")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not shutil.which("lark-cli"):
        print("未安装 lark-cli，无法写入飞书。请先运行 python3 scripts/check-larkcli.py", file=sys.stderr)
        return 2
    if not LOCAL_FEISHU_TARGET.exists():
        print("缺少 feishu-target.json，无法写入飞书。", file=sys.stderr)
        return 3
    if not SCHEMA_SNAPSHOT_PATH.exists():
        print("缺少表头检查快照，请先运行 python3 scripts/check-feishu-table-schema.py", file=sys.stderr)
        return 4

    schema_snapshot = json.loads(SCHEMA_SNAPSHOT_PATH.read_text(encoding="utf-8"))
    if schema_snapshot.get("changed"):
        print("飞书表头已变化，必须先纠正输出内容，再开始写入。", file=sys.stderr)
        return 5

    config = json.loads(LOCAL_FEISHU_TARGET.read_text(encoding="utf-8"))
    delivery_fields = json.loads(DELIVERY_SCHEMA_PATH.read_text(encoding="utf-8")).get("fields", [])
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("rows", [])

    payload_rows = []
    for row in rows:
        payload_rows.append([row.get(field, "") for field in delivery_fields])

    payload = payload_rows

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    existing = run_json([
        "lark-cli", "sheets", "+read",
        "--spreadsheet-token", str(config["spreadsheet_token"]),
        "--sheet-id", str(config["sheet_id"]),
        "--range", "A1:A5000",
        "--as", "user",
    ])
    existing_rows = (((existing.get("data") or {}).get("valueRange") or {}).get("values") or [])
    last_nonempty = 1
    for index, row in enumerate(existing_rows, start=1):
        cell = row[0] if row else None
        if cell not in (None, ""):
            last_nonempty = index

    start_row = max(int(config.get("start_row", 2)), last_nonempty + 1)
    end_row = start_row + max(len(payload_rows), 1) - 1
    end_col = chr(ord("A") + len(delivery_fields) - 1)
    range_ref = f"A{start_row}:{end_col}{end_row}"

    result = run_json([
        "lark-cli", "sheets", "+write",
        "--spreadsheet-token", str(config["spreadsheet_token"]),
        "--sheet-id", str(config["sheet_id"]),
        "--range", range_ref,
        "--as", "user",
        "--values", json.dumps(payload, ensure_ascii=False),
    ])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
