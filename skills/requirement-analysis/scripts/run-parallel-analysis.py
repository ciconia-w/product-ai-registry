#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
并行分析工作流辅助入口。

当前脚本负责：
1. 切分 merged.json
2. 生成每个批次推荐输出路径

它不强绑定任何具体 agent。不同 agent 只需消费这些 batch 文件并按契约产出对应 delivery/report。
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="准备并行分析批次")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--batch-size", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "python3",
            str(SCRIPT_DIR / "split-requirements-batches.py"),
            "--input", args.input,
            "--output-dir", str(output_dir),
            "--batch-size", str(args.batch_size),
        ],
        check=True,
    )

    batch_files = sorted(output_dir.glob("batch_*.json"))
    plan = []
    for batch in batch_files:
        stem = batch.stem
        plan.append({
            "batch_input": str(batch),
            "report_output": str(output_dir / f"{stem}_report.md"),
            "delivery_output": str(output_dir / f"{stem}_delivery.json"),
        })

    plan_path = output_dir / "parallel_plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(plan_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
