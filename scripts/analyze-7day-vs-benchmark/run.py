#!/usr/bin/env python3
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description="Analyze day-by-day UOS AI app stats from a captured current JSON payload.")
    parser.add_argument("current_json", help="path to the current aggregated JSON payload")
    args = parser.parse_args()

    with open(args.current_json, "r", encoding="utf-8") as f:
        current = json.load(f)

    print("当前 API 数据逐日分析:")
    print("=" * 70)

    for item in current:
        if item.get("type") == "app_stats":
            rows = item.get("data", {}).get("row", {}).get("rows", [])
            uosai_by_date = {}
            for row in rows:
                date = row.get("xAxis")
                if date:
                    uosai_by_date[date] = row.get("UOSAI", 0)

            ordered_dates = sorted(uosai_by_date.keys())
            for date in ordered_dates:
                print(f"  {date}: UOSAI = {uosai_by_date[date]}")

            if ordered_dates:
                last_date = ordered_dates[-1]
                total_uosai = sum(uosai_by_date.values())
                subtotal = total_uosai - uosai_by_date.get(last_date, 0)
                print(f"\n  总和: {total_uosai}")
                print(f"  除最后一天外的总和: {subtotal}")
                print(f"  最后一天({last_date}): {uosai_by_date.get(last_date, 0)}")
                print()

        if item.get("type") == "template_usage":
            rows = item.get("data", {}).get("row", {}).get("rows", [])
            dates = sorted(r.get("xAxis") for r in rows if r.get("xAxis"))
            print("写作模板数据天数:")
            print(f"  日期: {dates}")
            print(f"  天数: {len(dates)}")
            print()


if __name__ == "__main__":
    main()
