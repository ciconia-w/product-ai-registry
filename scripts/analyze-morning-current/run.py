#!/usr/bin/env python3
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Compare a morning capture payload against a current aggregated JSON payload.")
    parser.add_argument("morning_json", help="path to the morning captured responses JSON")
    parser.add_argument("current_json", help="path to the current aggregated JSON payload")
    args = parser.parse_args()

    print("早上捕获的数据分析")
    print("=" * 70)

    with open(args.morning_json, "r", encoding="utf-8") as f:
        morning = json.load(f)

    morning_total = None
    for resp in morning:
        body = resp.get("body", {})
        schema = body.get("row", {}).get("schema", [])
        if isinstance(schema, list):
            cols = [c.get("name") for c in schema]
            if "UOSAI" in cols:
                rows = body.get("row", {}).get("rows", [])
                print("应用统计 (UOSAI, AI Writing, 等):")
                for row in rows:
                    print(f'  {row.get("xAxis")}: UOSAI={row.get("UOSAI", 0)}, Writing={row.get("AI Writing", 0)}')
                morning_total = sum(r.get("UOSAI", 0) for r in rows)
                print(f"  UOSAI 总和: {morning_total}")
                print()
                break

    with open(args.current_json, "r", encoding="utf-8") as f:
        current = json.load(f)

    current_total = None
    for item in current:
        if item.get("type") == "app_stats":
            rows = item.get("data", {}).get("row", {}).get("rows", [])
            print("当前 API 获取的应用统计:")
            for row in rows:
                print(f'  {row.get("xAxis")}: UOSAI={row.get("UOSAI", 0)}, Writing={row.get("AI Writing", 0)}')
            current_total = sum(r.get("UOSAI", 0) for r in rows)
            print(f"  UOSAI 总和: {current_total}")
            break

    print()
    print("结论:")
    if morning_total is None or current_total is None:
        print("无法完成对比：缺少 UOSAI 数据。")
        return
    print(f"早上总和: {morning_total}")
    print(f"当前总和: {current_total}")
    print(f"差值: {current_total - morning_total:+d}")


if __name__ == "__main__":
    main()
