#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from core_data_common import OUTPUT_DIR, pretty_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compare-json", default=str(OUTPUT_DIR / "core_data_compare.json"))
    parser.add_argument("--output-md", default=str(OUTPUT_DIR / "core_data_large_table.md"))
    args = parser.parse_args()

    items = json.loads(Path(args.compare_json).read_text(encoding="utf-8"))
    lines = [
        "# 核心数据大表输出",
        "",
        "| block_name | query_path | query_rule | key_dims | workbook_value | page_value | request_value | export_value | status | reason |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        lines.append(
            f"| {item.get('block_name','')} |  |  |  | "
            f"`{pretty_json(item.get('workbook_value', item.get('workbook_rows','')))}` | "
            f"`{pretty_json(item.get('page_value',''))}` | "
            f"`{pretty_json(item.get('request_value',''))}` | "
            f"`{pretty_json(item.get('export_rows', item.get('export_value','')))}` | "
            f"{item.get('status','')} | {item.get('reason','')} |"
        )
    Path(args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(args.output_md)


if __name__ == "__main__":
    main()
