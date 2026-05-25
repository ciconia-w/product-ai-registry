#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from core_data_common import OUTPUT_DIR, SKILL_DIR, today_stamp


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--delivery-dir", default=str(OUTPUT_DIR / f"core_data_skill_delivery_{today_stamp()}"))
    parser.add_argument("--files", nargs="*", default=[])
    args = parser.parse_args()

    delivery = Path(args.delivery_dir)
    delivery.mkdir(parents=True, exist_ok=True)
    files = args.files or [
        OUTPUT_DIR / f"core_data_large_table_{today_stamp()}.md",
        OUTPUT_DIR / f"core_data_compare_{today_stamp()}.json",
        OUTPUT_DIR / f"core_data_final_table_{today_stamp()}.xlsx",
        SKILL_DIR / "SKILL.md",
        SKILL_DIR / "agents" / "openai.yaml",
        SKILL_DIR / "references" / "block_registry.yaml",
        SKILL_DIR / "references" / "known_findings.md",
        SKILL_DIR / "scripts" / "run_core_data_compare.py",
    ]
    for file in files:
        src = Path(file)
        if src.exists():
            shutil.copy2(src, delivery / src.name)
    print(delivery)


if __name__ == "__main__":
    main()
