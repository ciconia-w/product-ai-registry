#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对采集到的需求做轻量结构化分析，并生成报告与飞书交付 JSON。
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


def classify_problem(text: str) -> str:
    lowered = text.lower()
    if any(key in text for key in ["打不开", "启动失败", "崩溃", "报错", "异常"]) or "fail" in lowered or "error" in lowered:
        return "稳定性/兼容性"
    if any(key in text for key in ["慢", "卡", "性能", "占用"]):
        return "性能"
    if any(key in text for key in ["希望", "建议", "支持", "新增", "增加", "优化"]):
        return "功能/体验优化"
    if any(key in text for key in ["入口", "找不到", "步骤", "复杂"]):
        return "流程/可发现性"
    return "待人工判断"


def summarize_item(item: dict) -> str:
    text = f"{item.get('title', '')} {item.get('content', '')}"
    problem = classify_problem(text)
    source = item.get("source_label") or item.get("source") or "未知来源"
    module = item.get("module") or "待判定"
    return f"来源：{source}；问题类型：{problem}；建议模块：{module}；建议先进入需求池并结合原文做人工复核。"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成需求分析报告与飞书交付 JSON")
    parser.add_argument("--input", required=True, help="合并后的原始需求 JSON")
    parser.add_argument("--report-output", required=True, help="Markdown 报告输出路径")
    parser.add_argument("--delivery-output", required=True, help="飞书交付 JSON 输出路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("rows", [])

    source_counter = Counter((item.get("source_label") or item.get("source") or "未知") for item in items)
    module_counter = Counter((item.get("module") or "待判定") for item in items)

    analyzed_rows = []
    lines = [
        "# 需求分析报告",
        "",
        "## 1. 分析范围",
        "",
        f"- 样本总数：{len(items)}",
        f"- 数据来源：{', '.join(f'{k}({v})' for k, v in source_counter.items())}",
        "",
        "## 2. 模块分布",
        "",
    ]
    for module, count in module_counter.most_common(10):
        lines.append(f"- {module}: {count}")

    lines.extend([
        "",
        "## 3. 逐条分析",
        "",
    ])

    for index, item in enumerate(items, start=1):
        summary = summarize_item(item)
        raw_content = (item.get("content") or "").strip()
        analyzed_rows.append({
            "来源": item.get("source_label") or item.get("source", ""),
            "发布时间": item.get("publish_time", ""),
            "标题": item.get("title", ""),
            "模块": item.get("module", ""),
            "分类": item.get("category", ""),
            "作者": item.get("author", ""),
            "点赞": item.get("likes", ""),
            "浏览": item.get("views", ""),
            "回复数": item.get("replies", ""),
            "热度": item.get("hot_value", ""),
            "链接": item.get("url", ""),
            "内容": raw_content,
            "AI需求分析": summary,
            "_source": item.get("source", ""),
            "_source_label": item.get("source_label", ""),
            "_record_id": item.get("record_id", ""),
            "_raw_content": raw_content,
            "_raw_title": item.get("title", ""),
        })
        lines.extend([
            f"### {index}. {item.get('title', '未命名需求')}",
            "",
            f"- 来源：{item.get('source_label') or item.get('source')}",
            f"- 发布时间：{item.get('publish_time', '')}",
            f"- 模块：{item.get('module', '') or '待判定'}",
            f"- 分析：{summary}",
            "",
        ])

    report_path = Path(args.report_output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")

    delivery_path = Path(args.delivery_output)
    delivery_path.parent.mkdir(parents=True, exist_ok=True)
    delivery_path.write_text(json.dumps(analyzed_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"report: {report_path}")
    print(f"delivery: {delivery_path}")
    print(f"rows: {len(analyzed_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
