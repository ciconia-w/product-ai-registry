#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path


def main():
    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1]).expanduser().resolve()
    else:
        project_root = Path.cwd()

    payload = json.load(sys.stdin)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = project_root / ".ai-registry" / "linglong-retrospectives"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"{stamp}.json"
    md_path = out_dir / f"{stamp}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        f"# Linglong Retrospective {stamp}",
        "",
        f"- Result: {payload.get('result', 'unknown')}",
        f"- Project root: {payload.get('project_root', str(project_root))}",
        f"- Package id: {payload.get('package_id', 'unknown')}",
        f"- Package version: {payload.get('package_version', 'unknown')}",
        f"- Build path used: {payload.get('build_path_used', 'unknown')}",
        "",
        "## Pitfalls",
    ]
    pitfalls = payload.get("pitfalls", [])
    if pitfalls:
        md_lines.extend([f"- {item}" for item in pitfalls])
    else:
        md_lines.append("- None recorded")

    md_lines.append("")
    md_lines.append("## Workarounds")
    workarounds = payload.get("workarounds", [])
    if workarounds:
        md_lines.extend([f"- {item}" for item in workarounds])
    else:
        md_lines.append("- None recorded")

    md_lines.append("")
    md_lines.append("## Verification")
    verification = payload.get("verification", [])
    if verification:
        md_lines.extend([f"- {item}" for item in verification])
    else:
        md_lines.append("- None recorded")

    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(json.dumps({"json": str(json_path), "markdown": str(md_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
