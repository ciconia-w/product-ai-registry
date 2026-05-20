#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把合并后的需求 JSON 按批次拆分，供多个子 agent 并行分析。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="拆分需求批次")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--batch-size", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    if isinstance(rows, dict):
        rows = rows.get("rows", [])
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    batch_size = max(1, args.batch_size)
    count = 0
    for start in range(0, len(rows), batch_size):
        count += 1
        batch = rows[start:start + batch_size]
        path = output_dir / f"batch_{count:02d}.json"
        path.write_text(json.dumps(batch, ensure_ascii=False, indent=2), encoding="utf-8")
        print(path)
    print(f"batches={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
