#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测 lark-cli 是否已安装且已配置。
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


INSTALL_HINTS = [
    "npm install -g @larksuite/cli",
    "lark-cli config init --new",
    "lark-cli auth login --scope \"wiki:wiki wiki:wiki:readonly wiki:node:read wiki:space:retrieve sheets:spreadsheet:read sheets:spreadsheet.meta:read sheets:spreadsheet:write_only\"",
]


def main() -> int:
    cli = shutil.which("lark-cli")
    if not cli:
        print(json.dumps({
            "ok": False,
            "stage": "missing",
            "message": "未检测到 lark-cli",
            "install_hints": INSTALL_HINTS,
        }, ensure_ascii=False, indent=2))
        return 1

    result = subprocess.run(
        ["lark-cli", "auth", "status"],
        capture_output=True,
        text=True,
    )
    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    raw = stdout or stderr

    configured = result.returncode == 0
    payload = {
        "ok": configured,
        "stage": "ready" if configured else "unconfigured",
        "cli_path": cli,
        "message": "lark-cli 已可用" if configured else "lark-cli 已安装但尚未配置",
        "install_hints": [] if configured else INSTALL_HINTS,
        "raw": raw,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if configured else 2


if __name__ == "__main__":
    raise SystemExit(main())
