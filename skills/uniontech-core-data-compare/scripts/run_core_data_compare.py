#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from core_data_common import OUTPUT_DIR, ensure_output_dir, slugify, today_stamp


BASE = Path(__file__).resolve().parent


def call(script: str, *args: str) -> None:
    subprocess.run([sys.executable, str(BASE / script), *args], check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("preflight")

    p_default = sub.add_parser("default_table")
    p_default.add_argument("--workbook", default="")

    p_custom = sub.add_parser("custom_query")
    p_custom.add_argument("--block", required=True)
    p_custom.add_argument("--route", default="")
    p_custom.add_argument("--edition", default="")
    p_custom.add_argument("--major-version", default="")
    p_custom.add_argument("--minor-version", default="")
    p_custom.add_argument("--date-type", default="")
    p_custom.add_argument("--date-from", default="")
    p_custom.add_argument("--date-to", default="")
    p_custom.add_argument("--workbook", default="")
    p_custom.add_argument("--session", default="core-data-skill")
    p_custom.add_argument("--output-json", default="")

    sub.add_parser("bundle")
    p_excel = sub.add_parser("excel")
    p_excel.add_argument("--compare-json", default=str(OUTPUT_DIR / "core_data_compare.json"))
    p_excel.add_argument("--workbook", default="")
    p_excel.add_argument("--output-xlsx", default="")

    args = parser.parse_args()
    stamp = today_stamp()
    output_dir = ensure_output_dir()

    if args.cmd == "preflight":
        call("preflight_local.py")
        call("preflight_browser.py")
        return

    if args.cmd == "custom_query":
        block_slug = slugify(args.block)
        raw_json = args.output_json or str(output_dir / f"{block_slug}_custom_raw_{stamp}.json")
        compare_json = str(output_dir / f"{block_slug}_compare_{stamp}.json")
        large_md = str(output_dir / f"{block_slug}_large_table_{stamp}.md")
        final_xlsx = str(output_dir / f"{block_slug}_final_{stamp}.xlsx")
        call(
            "extract_custom_query.py",
            "--block", args.block,
            "--route", args.route,
            "--edition", args.edition,
            "--major-version", args.major_version,
            "--minor-version", args.minor_version,
            "--date-type", args.date_type,
            "--date-from", args.date_from,
            "--date-to", args.date_to,
            "--workbook", args.workbook,
            "--session", args.session,
            "--output-json", raw_json,
        )
        call("compare_workbook.py", "--source-json", raw_json, "--output-json", compare_json)
        call("render_large_table.py", "--compare-json", compare_json, "--output-md", large_md)
        call("write_final_excel.py", "--compare-json", compare_json, "--workbook", args.workbook, "--output-xlsx", final_xlsx)
        return

    if args.cmd == "bundle":
        call("bundle_delivery.py")
        return

    if args.cmd == "excel":
        output_xlsx = args.output_xlsx or str(output_dir / f"core_data_final_table_{stamp}.xlsx")
        call("write_final_excel.py", "--compare-json", args.compare_json, "--workbook", args.workbook, "--output-xlsx", output_xlsx)
        return

    default_json = str(output_dir / f"core_data_default_extract_{stamp}.json")
    compare_json = str(output_dir / f"core_data_compare_{stamp}.json")
    large_md = str(output_dir / f"core_data_large_table_{stamp}.md")
    final_xlsx = str(output_dir / f"core_data_final_table_{stamp}.xlsx")

    call("extract_default_table.py", "--workbook", args.workbook, "--output-json", default_json)
    call("compare_workbook.py", "--source-json", default_json, "--output-json", compare_json)
    call("render_large_table.py", "--compare-json", compare_json, "--output-md", large_md)
    call("write_final_excel.py", "--compare-json", compare_json, "--workbook", args.workbook, "--output-xlsx", final_xlsx)


if __name__ == "__main__":
    main()
