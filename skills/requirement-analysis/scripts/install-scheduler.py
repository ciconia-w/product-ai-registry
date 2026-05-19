#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装一个本地 cron 任务。
任务执行顺序固定为：
1. 检查飞书表头
2. 表头无变化才进入采集/分析/写入
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
RUNNER_PATH = SCRIPT_DIR / "run-scheduled-workflow.sh"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="安装需求采集分析定时任务")
    parser.add_argument("--schedule", required=True, help='cron 表达式，例如 "0 9 * * *"')
    return parser.parse_args()


def main() -> int:
    cron_line = f'{parse_args().schedule} bash "{RUNNER_PATH}"\n'
    current = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = current.stdout if current.returncode == 0 else ""

    if cron_line in existing:
        print("定时任务已存在")
        return 0

    new_cron = existing + ("\n" if existing and not existing.endswith("\n") else "") + cron_line
    subprocess.run(["crontab", "-"], input=new_cron, text=True, check=True)
    print("定时任务已安装")
    print(cron_line.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
