#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
在采集开始前检查飞书表头是否变化。

当前目标资源是 spreadsheet，不是 bitable/base。
"""

from __future__ import annotations

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


def main() -> int:
    if not shutil.which("lark-cli"):
        print(json.dumps({
            "ok": False,
            "stage": "missing_larkcli",
            "message": "未安装 lark-cli，无法检查飞书表头",
            "next_step": "先运行 npm install -g @larksuite/cli，并完成 lark-cli config init --new",
        }, ensure_ascii=False, indent=2))
        return 2

    if not LOCAL_FEISHU_TARGET.exists():
        print(json.dumps({
            "ok": False,
            "stage": "missing_target",
            "message": "缺少 feishu-target.json，尚未绑定目标 spreadsheet",
            "next_step": "复制 feishu-target.example.json 到 ~/.config/requirement-analysis/feishu-target.json，并补全 spreadsheet_token / sheet_id",
        }, ensure_ascii=False, indent=2))
        return 3

    config = json.loads(LOCAL_FEISHU_TARGET.read_text(encoding="utf-8"))
    spreadsheet_token = config.get("spreadsheet_token")
    sheet_id = config.get("sheet_id")
    if not spreadsheet_token or not sheet_id:
        print(json.dumps({
            "ok": False,
            "stage": "bad_target",
            "message": "feishu-target.json 缺少 spreadsheet_token 或 sheet_id",
        }, ensure_ascii=False, indent=2))
        return 4

    try:
        values_payload = run_json([
            "lark-cli", "sheets", "+read",
            "--spreadsheet-token", str(spreadsheet_token),
            "--sheet-id", str(sheet_id),
            "--range", "A1:Z2",
            "--as", "user",
        ])
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "stage": "fetch_failed",
            "message": f"获取飞书表头失败: {exc}",
            "next_step": "先运行 python3 scripts/check-feishu-access.py，确认本地 lark-cli 对目标资源和所需 scope 已就绪",
        }, ensure_ascii=False, indent=2))
        return 5

    rows = (((values_payload.get("data") or {}).get("valueRange") or {}).get("values") or [])
    header_row = rows[0] if rows else []
    remote_fields = [cell for cell in header_row if cell]

    expected = json.loads(DELIVERY_SCHEMA_PATH.read_text(encoding="utf-8")).get("fields", [])
    missing_in_remote = [name for name in expected if name not in remote_fields]
    added_in_remote = [name for name in remote_fields if name not in expected]
    changed = bool(missing_in_remote or added_in_remote)

    snapshot = {
        "remote_fields": remote_fields,
        "expected_fields": expected,
        "missing_in_remote": missing_in_remote,
        "added_in_remote": added_in_remote,
        "changed": changed,
    }
    SCHEMA_SNAPSHOT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps({
        "ok": not changed,
        "stage": "changed" if changed else "aligned",
        "message": "飞书表头已变化，请先纠正输出内容再开始采集" if changed else "飞书表头未变化，可继续采集",
        "snapshot_path": str(SCHEMA_SNAPSHOT_PATH),
        "missing_in_remote": missing_in_remote,
        "added_in_remote": added_in_remote,
    }, ensure_ascii=False, indent=2))
    return 6 if changed else 0


if __name__ == "__main__":
    raise SystemExit(main())
