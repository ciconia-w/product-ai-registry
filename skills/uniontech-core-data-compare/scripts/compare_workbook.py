#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from core_data_common import OUTPUT_DIR, write_json


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-json", default=str(OUTPUT_DIR / "core_data_default_extract.json"))
    parser.add_argument("--output-json", default=str(OUTPUT_DIR / "core_data_compare.json"))
    args = parser.parse_args()

    source = Path(args.source_json)
    payload = __import__("json").loads(source.read_text(encoding="utf-8"))
    compare_items = payload.get("compare_items", payload if isinstance(payload, list) else [])
    out = write_json(args.output_json, compare_items)
    print(out)


if __name__ == "__main__":
    main()
