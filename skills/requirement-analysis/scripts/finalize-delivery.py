#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终写飞书前的整理步骤：
- 补 K 列链接
- 检测非中文条目
- 输出待翻译队列
- 应用 agent 提供的翻译结果
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from load_local_sources import load_deepin_home_config, load_feedback_platform_config


def looks_foreign(text: str) -> bool:
    if not text:
        return False
    ascii_letters = sum(1 for ch in text if ("a" <= ch.lower() <= "z"))
    chinese_chars = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    return ascii_letters > 30 and chinese_chars < 20 and ascii_letters > chinese_chars * 3


def fallback_link(row: dict) -> str:
    if row.get("链接"):
        return row["链接"]
    source = row.get("_source", "")
    record_id = row.get("_record_id", "")
    if not record_id:
        return ""
    if source == "deepin-forum":
        return f"https://bbs.deepin.org/post/{record_id}"
    if source == "feedback-platform":
        cfg = load_feedback_platform_config()
        worksheet_id = cfg.get("worksheet_id")
        if worksheet_id:
            return f"https://cooperation.uniontech.com/worksheet/{worksheet_id}/row/{record_id}"
    if source == "deepin-home-openapi":
        cfg = load_deepin_home_config()
        worksheet_id = cfg.get("worksheet_id")
        if worksheet_id:
            return f"https://cooperation.uniontech.com/worksheet/{worksheet_id}/row/{record_id}"
    return ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="最终整理飞书交付 JSON")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--translation-queue", required=True)
    parser.add_argument("--translations", help="agent 翻译结果 JSON，可选")
    parser.add_argument("--report-link", help="飞书中的分析报告链接，可选")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = json.loads(Path(args.input).read_text(encoding="utf-8"))
    translations = {}
    if args.translations:
        payload = json.loads(Path(args.translations).read_text(encoding="utf-8"))
        translations = {int(item["index"]): item["content"] for item in payload.get("translations", [])}

    queue = []
    finalized = []

    for index, row in enumerate(rows, start=1):
        row = dict(row)
        row["链接"] = fallback_link(row)

        content = row.get("内容", "") or ""
        raw_content = row.get("_raw_content", "") or content
        raw_title = row.get("_raw_title", "") or row.get("标题", "")
        needs_translation = (
            "中文翻译:" not in content
            and (looks_foreign(raw_content) or looks_foreign(raw_title))
        )

        if needs_translation:
            if index in translations:
                row["内容"] = translations[index]
            else:
                queue.append({
                    "index": index,
                    "title": row.get("标题", ""),
                    "source": row.get("来源", ""),
                    "link": row.get("链接", ""),
                    "original_text": raw_content,
                })
        row["分析报告链接"] = args.report_link or row.get("分析报告链接", "")
        finalized.append(row)

    Path(args.output).write_text(json.dumps(finalized, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.translation_queue).write_text(json.dumps({"translations": queue}, ensure_ascii=False, indent=2), encoding="utf-8")

    if queue:
        print(f"存在 {len(queue)} 条非中文内容，需 agent 翻译后再写飞书。")
        print(f"queue: {args.translation_queue}")
        print(f"output: {args.output}")
        return 10

    print(f"finalized: {args.output}")
    print("所有条目已可写入飞书。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
