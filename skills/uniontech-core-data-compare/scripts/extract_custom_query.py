#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from block_extractors import (
    extract_app_start_rank,
    extract_appstore_deb_install_fail,
    extract_appstore_deb_new,
    extract_appstore_deb_update,
    extract_appstore_linglong_install_fail,
    extract_appstore_linglong_new,
    extract_appstore_linglong_update,
    extract_default_plugin_remove,
    extract_smb_rate,
    extract_smb_cause,
    extract_fulltext_open,
    extract_overview_arch,
    extract_overview_major_version_total,
    extract_overview_minor_version,
    extract_overview_new_users,
    extract_overview_product,
    extract_overview_specific_minor_total,
    extract_overview_total_users,
    extract_safe_box_open,
    extract_system_update_fail_cause,
    extract_system_update_fail_rate,
    extract_taskbar,
)
from compare_live_result import compare_live_result
from core_data_common import OUTPUT_DIR, WorkbookSnapshot, discover_workbook
from opencli_live_common import close_session


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--block", required=True, help="块名，例如：任务栏模式配置")
    parser.add_argument("--route", default="", help="可选 route，例如 #/point/file-manager")
    parser.add_argument("--edition", default="", help="系统产品")
    parser.add_argument("--major-version", default="", help="系统版本")
    parser.add_argument("--minor-version", default="", help="系统小版本")
    parser.add_argument("--date-type", default="", help="日期粒度，例如 日/周/月")
    parser.add_argument("--date-from", default="", help="开始日期")
    parser.add_argument("--date-to", default="", help="结束日期")
    parser.add_argument("--workbook", default="", help="可选 workbook 路径")
    parser.add_argument("--session", default="core-data-skill", help="opencli 浏览器会话名")
    parser.add_argument("--output-json", default=str(OUTPUT_DIR / "core_data_custom_query.json"))
    args = parser.parse_args()

    query = {
        "edition": args.edition,
        "major_version": args.major_version,
        "minor_version": args.minor_version,
        "date_type": args.date_type,
        "date_type_ch": args.date_type,
        "date_from": args.date_from,
        "date_to": args.date_to,
        "os": args.edition,
    }

    appstore_blocks = {
        "应用商店deb应用新增下载应用排行Top30及下载失败率-周累计",
        "应用商店deb应用更新下载应用排行Top30及下载失败率-周累计",
        "应用商店deb应用安装失败次数排行Top5及安装失败率-周累计",
        "应用商店玲珑应用新增下载应用排行Top10及下载失败率-周累计",
        "应用商店玲珑应用更新下载应用排行Top10及下载失败率-周累计",
        "应用商店玲珑应用安装失败次数排行Top5及安装失败率-周累计",
    }
    if args.block in appstore_blocks and not query["os"]:
        query["os"] = "Professional"

    payload = {
        "mode": "custom_query",
        "block": args.block,
        "route": args.route,
        "session": args.session,
        "query": query,
        "note": "当前脚本已接入部分真实取数块的 opencli 页面上下文请求回放。",
    }

    extractors = {
        "任务栏模式配置": extract_taskbar,
        "单个插件的被移除率": extract_default_plugin_remove,
        "产品分布": extract_overview_product,
        "架构分布": extract_overview_arch,
        "专业版日新增用户数": extract_overview_new_users,
        "专业版累计用户数": extract_overview_total_users,
        "专业版1070u5累计用户数": extract_overview_specific_minor_total,
        "专业版V25累计用户数": extract_overview_major_version_total,
        "专业版版本系列用户分布": extract_overview_minor_version,
        "专业版用户-保险箱功能开启率（万分之）": extract_safe_box_open,
        "专业版用户-全文搜索功能开启率（万分之）": extract_fulltext_open,
        "专业版应用启动排行Top50-周累计": extract_app_start_rank,
        "教育版应用启动排行Top50-周累计": extract_app_start_rank,
        "专业版检查更新失败率-周累计": extract_system_update_fail_rate,
        "检查更新失败原因分布-周累计": extract_system_update_fail_cause,
        "应用商店deb应用新增下载应用排行Top30及下载失败率-周累计": extract_appstore_deb_new,
        "应用商店deb应用更新下载应用排行Top30及下载失败率-周累计": extract_appstore_deb_update,
        "应用商店deb应用安装失败次数排行Top5及安装失败率-周累计": extract_appstore_deb_install_fail,
        "应用商店玲珑应用新增下载应用排行Top10及下载失败率-周累计": extract_appstore_linglong_new,
        "应用商店玲珑应用更新下载应用排行Top10及下载失败率-周累计": extract_appstore_linglong_update,
        "应用商店玲珑应用安装失败次数排行Top5及安装失败率-周累计": extract_appstore_linglong_install_fail,
        "smb挂载失败率-周累计": extract_smb_rate,
        "smb挂载失败原因分布-周累计": extract_smb_cause,
    }

    try:
        if args.block in extractors:
            payload["live_result"] = extractors[args.block](query, session=args.session)
        else:
            payload["live_result"] = {
                "supported": False,
                "reason": "当前 block 尚未接入真实 opencli 提取器"
            }
    finally:
        close_session(args.session)

    snapshot = WorkbookSnapshot(discover_workbook(args.workbook))
    compare_items = compare_live_result(snapshot, payload)
    payload["compare_items"] = compare_items

    out = Path(args.output_json)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
