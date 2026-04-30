#!/usr/bin/env python3
import argparse
import json
import pandas as pd


APP_PV_FIELDS = [
    "UOSAI", "AI Writing", "AI Translation", "个人知识助手",
    "UOS玩机助手", "商店下载三方", "AI Text Processing",
]
SAIL_FIELDS = ["polish", "扩写", "纠错", "总结", "翻译", "续写", "搜索", "解释"]
WRITING_FIELDS = ["写通知", "工作总结", "公众号", "调研报告", "写大纲", "演讲稿", "写文章"]


def main():
    parser = argparse.ArgumentParser(description="Compare benchmark workbook totals against a morning captured response set.")
    parser.add_argument("benchmark_xlsx", help="path to the benchmark Excel workbook")
    parser.add_argument("morning_json", help="path to the morning captured responses JSON")
    args = parser.parse_args()

    df = pd.read_excel(args.benchmark_xlsx)
    benchmark = df.iloc[0].to_dict()

    print("标杆数据 (Excel 第1行 - 汇总):")
    print(f'  AI 助手PV: {benchmark.get("AI 助手PV", 0)}')
    print(f'  UOSAI: {benchmark.get("UOSAI", 0)}')
    print(f'  随航使用次数: {benchmark.get("随航使用次数", 0)}')
    print(f'  写作PV: {benchmark.get("写作PV", 0)}')
    print()

    with open(args.morning_json, "r", encoding="utf-8") as f:
        morning = json.load(f)

    morning_date_data = {}
    for resp in morning:
        body = resp.get("body", {})
        rows = body.get("row", {}).get("rows", [])
        schema = body.get("row", {}).get("schema", [])
        if not rows or not schema:
            continue
        for row in rows:
            date = row.get("xAxis")
            if not date:
                continue
            morning_date_data.setdefault(date, {})
            for key, value in row.items():
                if key != "xAxis":
                    morning_date_data[date][key] = value

    morning_sums = {}
    for date_data in morning_date_data.values():
        for key, value in date_data.items():
            morning_sums[key] = morning_sums.get(key, 0) + value

    morning_sums["AI 助手PV"] = sum(morning_sums.get(field, 0) for field in APP_PV_FIELDS)
    morning_sums["随航使用次数"] = sum(morning_sums.get(field, 0) for field in SAIL_FIELDS)
    morning_sums["写作PV"] = sum(morning_sums.get(field, 0) for field in WRITING_FIELDS)

    print("早上捕获数据汇总:")
    print(f'  AI 助手PV: {morning_sums["AI 助手PV"]}')
    print(f'  UOSAI: {morning_sums.get("UOSAI", 0)}')
    print(f'  随航使用次数: {morning_sums["随航使用次数"]}')
    print(f'  写作PV: {morning_sums["写作PV"]}')
    print()

    print("对比分析:")
    print("=" * 70)
    print(f'{"指标":<15} {"标杆":<12} {"早上":<12} {"差异":<15}')
    print("-" * 54)

    keys = ["AI 助手PV", "UOSAI", "随航使用次数", "写作PV"]
    for key in keys:
        bench_val = benchmark.get(key, 0)
        morn_val = morning_sums.get(key, 0)
        diff = morn_val - bench_val
        diff_pct = (diff / bench_val * 100) if bench_val else 0
        print(f"{key:<15} {bench_val:<12} {morn_val:<12} {diff:>+5} ({diff_pct:+.1f}%)")


if __name__ == "__main__":
    main()
