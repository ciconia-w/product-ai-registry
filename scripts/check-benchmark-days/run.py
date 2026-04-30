#!/usr/bin/env python3
import argparse
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Inspect benchmark workbook row count and date column values.")
    parser.add_argument("benchmark_xlsx", help="path to the benchmark Excel workbook")
    parser.add_argument("--date-column", default="日期", help="column name containing dates")
    args = parser.parse_args()

    df = pd.read_excel(args.benchmark_xlsx)
    print("标杆 Excel 行数:", len(df))
    print()
    print("Excel 内容预览:")
    print(df.to_string())
    print()
    print("=" * 70)
    if args.date_column in df.columns:
        print("日期列:")
        print(df[args.date_column].tolist())
        print()
    print(f"总共有 {len(df)} 天的数据")


if __name__ == "__main__":
    main()
