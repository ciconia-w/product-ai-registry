#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 Markdown 报告发布到飞书，并输出链接。
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="发布分析报告到飞书 Markdown")
    parser.add_argument("--file", required=True, help="本地 Markdown 文件路径")
    parser.add_argument("--name", required=True, help="飞书文档名称")
    parser.add_argument("--public", action="store_true", default=True, help="默认将链接分享设置为互联网获得链接可读")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    file_path = Path(args.file).resolve()
    workdir = file_path.parent
    rel_path = f"./{file_path.name}"
    proc = subprocess.run(
        ["lark-cli", "markdown", "+create", "--file", rel_path, "--name", args.name, "--as", "user"],
        capture_output=True,
        text=True,
        check=True,
        cwd=workdir,
    )
    data = json.loads(proc.stdout)
    if args.public:
        token = (((data.get("data") or {}).get("file_token")) or "")
        if token:
            subprocess.run(
                [
                    "lark-cli", "drive", "permission.public", "patch",
                    "--yes",
                    "--params", json.dumps({"token": token, "type": "file"}, ensure_ascii=False),
                    "--data", json.dumps(
                        {
                            "external_access": True,
                            "link_share_entity": "anyone_readable",
                            "security_entity": "anyone_can_view",
                        },
                        ensure_ascii=False,
                    ),
                    "--as", "user",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
