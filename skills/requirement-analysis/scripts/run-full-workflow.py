#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
执行采集 -> 合并 -> 分析 -> 飞书表头检查 -> 飞书写入。
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = SCRIPT_DIR.parent / "outputs"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行完整需求工作流")
    parser.add_argument("--days", type=int, default=3)
    parser.add_argument("--forum-max", type=int, default=10)
    parser.add_argument("--feedback-max", type=int, default=10)
    parser.add_argument("--deepin-home-page-size", type=int, default=20)
    parser.add_argument("--deepin-home-pages", type=int, default=1)
    parser.add_argument("--skip-feishu-write", action="store_true")
    parser.add_argument("--translations", help="可选，translations.json 路径；当 finalize 检测到外语队列时使用")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    run(["python3", str(SCRIPT_DIR / "check-larkcli.py")])
    run(["python3", str(SCRIPT_DIR / "check-feishu-access.py")])
    run(["python3", str(SCRIPT_DIR / "check-feishu-table-schema.py")])

    forum_path = OUTPUT_DIR / f"forum_{stamp}.json"
    feedback_path = OUTPUT_DIR / f"feedback_{stamp}.json"
    deepin_home_path = OUTPUT_DIR / f"deepin_home_{stamp}.json"
    merged_path = OUTPUT_DIR / f"merged_{stamp}.json"
    report_path = OUTPUT_DIR / f"需求分析报告-{stamp}.md"
    delivery_path = OUTPUT_DIR / f"delivery_{stamp}.json"
    finalized_delivery_path = OUTPUT_DIR / f"delivery_final_{stamp}.json"
    translation_queue_path = OUTPUT_DIR / f"translation_queue_{stamp}.json"
    report_publish_path = OUTPUT_DIR / f"report_publish_{stamp}.json"

    run(["python3", str(SCRIPT_DIR / "fetch-forum-requirements.py"), str(args.days), str(args.forum_max), "--all", "--output", str(forum_path)])
    run(["python3", str(SCRIPT_DIR / "fetch-feedback-platform-requirements.py"), str(args.days), str(args.feedback_max), "--all", "--output", str(feedback_path)])
    run(["python3", str(SCRIPT_DIR / "fetch-deepin-home-openapi.py"), "--view", "requirement_feedback", "--page-size", str(args.deepin_home_page_size), "--pages", str(args.deepin_home_pages), "--output", str(deepin_home_path)])
    run(["python3", str(SCRIPT_DIR / "merge-requirements.py"), str(forum_path), str(feedback_path), str(deepin_home_path), "--output", str(merged_path)])
    run(["python3", str(SCRIPT_DIR / "analyze-requirements.py"), "--input", str(merged_path), "--report-output", str(report_path), "--delivery-output", str(delivery_path)])
    finalize = subprocess.run([
        "python3", str(SCRIPT_DIR / "finalize-delivery.py"),
        "--input", str(delivery_path),
        "--output", str(finalized_delivery_path),
        "--translation-queue", str(translation_queue_path),
        *([ "--translations", str(args.translations) ] if args.translations else []),
    ])
    if finalize.returncode == 10:
        raise SystemExit(f"存在非中文内容，需 agent 完成 translation_queue 后再继续写飞书: {translation_queue_path}")
    if finalize.returncode != 0:
        raise SystemExit(finalize.returncode)
    publish = subprocess.run(
        [
            "python3", str(SCRIPT_DIR / "publish-feishu-report.py"),
            "--file", str(report_path),
            "--name", report_path.name,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    report_publish_path.write_text(publish.stdout, encoding="utf-8")
    report_payload = json.loads(publish.stdout)
    report_link = (((report_payload.get("data") or {}).get("url")) or "")
    if report_link:
        finalize_with_link = subprocess.run([
            "python3", str(SCRIPT_DIR / "finalize-delivery.py"),
            "--input", str(delivery_path),
            "--output", str(finalized_delivery_path),
            "--translation-queue", str(translation_queue_path),
            "--report-link", report_link,
            *([ "--translations", str(args.translations) ] if args.translations else []),
        ])
        if finalize_with_link.returncode != 0:
            raise SystemExit(finalize_with_link.returncode)
    if not args.skip_feishu_write:
        run(["python3", str(SCRIPT_DIR / "write-feishu-table.py"), "--input", str(finalized_delivery_path)])

    print(f"forum={forum_path}")
    print(f"feedback={feedback_path}")
    print(f"deepin_home={deepin_home_path}")
    print(f"merged={merged_path}")
    print(f"report={report_path}")
    print(f"report_publish={report_publish_path}")
    print(f"delivery={delivery_path}")
    print(f"finalized_delivery={finalized_delivery_path}")
    print(f"translation_queue={translation_queue_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
