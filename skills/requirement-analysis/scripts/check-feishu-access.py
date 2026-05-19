#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查本地 lark-cli 对目标飞书资源的访问能力与 scope 完整性。
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

from config_paths import LOCAL_FEISHU_TARGET


SCRIPT_DIR = Path(__file__).resolve().parent
EXAMPLE_PATH = SCRIPT_DIR / "feishu-target.example.json"


def run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "").strip(), (proc.stderr or "").strip()


def parse_json_blob(text: str) -> dict[str, Any]:
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        return {"raw": text}


def main() -> int:
    if not shutil.which("lark-cli"):
        print(json.dumps({
            "ok": False,
            "stage": "missing_larkcli",
            "message": "未安装 lark-cli",
            "next_step": "先运行 npm install -g @larksuite/cli",
        }, ensure_ascii=False, indent=2))
        return 2

    if not LOCAL_FEISHU_TARGET.exists():
        print(json.dumps({
            "ok": False,
            "stage": "missing_target",
            "message": "缺少 feishu-target.json",
            "next_step": f"参考 {EXAMPLE_PATH.name} 在 ~/.config/requirement-analysis/ 下创建 feishu-target.json",
        }, ensure_ascii=False, indent=2))
        return 3

    config = json.loads(LOCAL_FEISHU_TARGET.read_text(encoding="utf-8"))
    wiki_token = config.get("wiki_token")
    spreadsheet_token = config.get("spreadsheet_token")
    sheet_id = config.get("sheet_id")

    checks = []

    code, out, err = run(["lark-cli", "auth", "status"])
    checks.append({
        "name": "auth_status",
        "ok": code == 0,
        "result": parse_json_blob(out or err),
    })

    if wiki_token:
        code, out, err = run([
            "lark-cli", "api", "GET", "/open-apis/wiki/v2/spaces/get_node",
            "--params", json.dumps({"token": wiki_token}, ensure_ascii=False),
            "--format", "json",
            "--as", "user",
        ])
        checks.append({
            "name": "wiki_get_node",
            "ok": code == 0,
            "result": parse_json_blob(out or err),
        })

    if spreadsheet_token:
        code, out, err = run([
            "lark-cli", "sheets", "+info",
            "--spreadsheet-token", str(spreadsheet_token),
            "--as", "user",
        ])
        checks.append({
            "name": "sheets_info",
            "ok": code == 0,
            "result": parse_json_blob(out or err),
        })

    if spreadsheet_token and sheet_id:
        code, out, err = run([
            "lark-cli", "sheets", "+read",
            "--spreadsheet-token", str(spreadsheet_token),
            "--sheet-id", str(sheet_id),
            "--range", "A1:Z2",
            "--as", "user",
        ])
        checks.append({
            "name": "sheets_header_read",
            "ok": code == 0,
            "result": parse_json_blob(out or err),
        })

        code, out, err = run([
            "lark-cli", "auth", "check",
            "--scope", "sheets:spreadsheet:write_only",
        ])
        checks.append({
            "name": "sheets_write_scope",
            "ok": code == 0,
            "result": parse_json_blob(out or err),
        })

    all_ok = all(item["ok"] for item in checks)
    print(json.dumps({
        "ok": all_ok,
        "checks": checks,
        "message": "飞书访问检查通过" if all_ok else "飞书访问检查未通过，请根据每项 result 中的缺失 scope 或 console_url 处理",
    }, ensure_ascii=False, indent=2))
    return 0 if all_ok else 4


if __name__ == "__main__":
    raise SystemExit(main())
