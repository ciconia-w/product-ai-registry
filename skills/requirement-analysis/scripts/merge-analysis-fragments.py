#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并多个子批次分析输出。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="合并分析碎片")
    parser.add_argument("--delivery-output", required=True)
    parser.add_argument("--report-output", required=True)
    parser.add_argument("deliveries", nargs="+", help="多个 batch delivery.json")
    parser.add_argument("--reports", nargs="*", default=[], help="多个 batch report.md")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    merged_rows = []
    for raw_path in args.deliveries:
        path = Path(raw_path)
        data = json.loads(path.read_text(encoding="utf-8"))
        merged_rows.extend(data if isinstance(data, list) else data.get("rows", []))

    Path(args.delivery_output).write_text(json.dumps(merged_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    report_parts = []
    for report in args.reports:
        report_parts.append(Path(report).read_text(encoding="utf-8"))
    Path(args.report_output).write_text("\n\n".join(report_parts), encoding="utf-8")

    print(f"rows={len(merged_rows)}")
    print(f"delivery={args.delivery_output}")
    print(f"report={args.report_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
