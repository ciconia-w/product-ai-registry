#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把采集/分析结果整理为写入当前 spreadsheet 的统一中间格式。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="整理飞书写入中间格式")
    parser.add_argument("--input", required=True, help="输入 JSON 路径")
    parser.add_argument("--report-path", required=True, help="需求分析报告路径")
    parser.add_argument("--output", required=True, help="输出 JSON 路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else data.get("rows", [])

    out = []
    for row in rows:
        analysis_text = row.get("analysis_summary") or row.get("report_path") or args.report_path
        out.append({
            "来源": row.get("source_label") or row.get("source", ""),
            "发布时间": row.get("publish_time", ""),
            "标题": row.get("title", ""),
            "模块": row.get("module", ""),
            "分类": row.get("category", ""),
            "作者": row.get("author", ""),
            "点赞": row.get("likes", ""),
            "浏览": row.get("views", ""),
            "回复数": row.get("replies", ""),
            "热度": row.get("hot_value", ""),
            "链接": row.get("url", ""),
            "内容": row.get("content", ""),
            "AI需求分析": analysis_text,
        })

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"prepared {len(out)} rows to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
