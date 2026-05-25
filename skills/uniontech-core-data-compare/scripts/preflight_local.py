#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from core_data_common import discover_workbook

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", default="")
    parser.add_argument("--opencli-runtime", default=str(Path.home() / ".opencli"))
    args = parser.parse_args()

    try:
        workbook = discover_workbook(args.workbook)
    except FileNotFoundError:
        workbook = Path(args.workbook or (Path.home() / "core_data_summary.xlsx"))
    runtime = Path(args.opencli_runtime)

    result = {
        "opencli_ready": shutil.which("opencli") is not None,
        "workbook_exists": workbook.exists(),
        "workbook_path": str(workbook),
        "opencli_runtime_exists": runtime.exists(),
        "adapter_manifest_exists": (runtime / "adapter-manifest.json").exists(),
        "plugins_lock_exists": (runtime / "plugins.lock.json").exists(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
