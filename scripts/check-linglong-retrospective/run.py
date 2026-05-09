#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUIRED_KEYS = {
    "date",
    "project_root",
    "host_summary",
    "package_id",
    "package_version",
    "base_runtime",
    "artifacts",
    "build_path_used",
    "result",
    "pitfalls",
    "workarounds",
    "verification",
    "open_questions",
}


def main():
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1]).expanduser().resolve()
    else:
        project_root = Path.cwd()

    out_dir = project_root / ".ai-registry" / "linglong-retrospectives"
    if not out_dir.exists():
        print("missing retrospective directory", file=sys.stderr)
        raise SystemExit(1)

    json_files = sorted(out_dir.glob("*.json"))
    if not json_files:
        print("missing retrospective json", file=sys.stderr)
        raise SystemExit(1)

    latest = json_files[-1]
    payload = json.loads(latest.read_text(encoding="utf-8"))
    missing = sorted(REQUIRED_KEYS - set(payload.keys()))
    if missing:
        print(f"retrospective missing keys: {', '.join(missing)}", file=sys.stderr)
        raise SystemExit(1)

    print(json.dumps({"latest": str(latest), "status": "ok"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
