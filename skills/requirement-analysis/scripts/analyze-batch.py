#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单批次需求分析入口。

本脚本复用 analyze-requirements.py 的逻辑，但输入是一个 batch json，
输出是该批次自己的 report 与 delivery。
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="分析单个需求批次")
    parser.add_argument("--input", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("--delivery-output", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    subprocess.run(
        [
            "python3",
            str(SCRIPT_DIR / "analyze-requirements.py"),
            "--input", args.input,
            "--report-output", args.report_output,
            "--delivery-output", args.delivery_output,
        ],
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
