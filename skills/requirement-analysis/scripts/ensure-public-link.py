#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
确保飞书文件链接为互联网获得链接可见。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess


FILE_TOKEN_RE = re.compile(r"/file/([A-Za-z0-9]+)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="把飞书文件设置为公网链接可见")
    parser.add_argument("--url", required=True, help="飞书文件链接")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    m = FILE_TOKEN_RE.search(args.url)
    if not m:
        raise SystemExit("无法从 URL 解析 file token")
    token = m.group(1)
    subprocess.run([
        "lark-cli", "drive", "permission.public", "patch",
        "--yes",
        "--params", json.dumps({"token": token, "type": "file"}, ensure_ascii=False),
        "--data", json.dumps({
            "external_access": True,
            "link_share_entity": "anyone_readable",
            "security_entity": "anyone_can_view",
        }, ensure_ascii=False),
        "--as", "user",
    ], check=True)
    print(token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
