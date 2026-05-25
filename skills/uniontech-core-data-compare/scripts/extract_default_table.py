#!/usr/bin/env python3
from __future__ import annotations

import argparse

from block_extractors import (
    extract_app_start_rank,
    extract_appstore_deb_install_fail,
    extract_appstore_deb_new,
    extract_appstore_deb_update,
    extract_appstore_linglong_install_fail,
    extract_appstore_linglong_new,
    extract_appstore_linglong_update,
    extract_default_plugin_remove,
    extract_fulltext_open,
    extract_overview_arch,
    extract_overview_major_version_total,
    extract_overview_minor_version,
    extract_overview_new_users,
    extract_overview_product,
    extract_overview_specific_minor_total,
    extract_overview_total_users,
    extract_safe_box_open,
    extract_smb_cause,
    extract_smb_rate,
    extract_system_update_fail_rate,
    extract_system_update_fail_cause,
    extract_taskbar,
)
from compare_live_result import compare_live_result
from core_data_common import (
    OUTPUT_DIR,
    WorkbookSnapshot,
    build_compare_item,
    discover_workbook,
    write_json,
)
from opencli_live_common import close_session


def build_default_compare(snapshot: WorkbookSnapshot) -> list[dict[str, Any]]:
    items = []
    for block_name in [
        "产品分布",
        "架构分布",
        "专业版日新增用户数",
        "专业版累计用户数",
        "专业版1070u5累计用户数",
        "专业版V25累计用户数",
        "专业版版本系列用户分布",
        "任务栏模式配置",
        "单个插件的被移除率",
        "专业版用户-保险箱功能开启率（万分之）",
        "专业版用户-全文搜索功能开启率（万分之）",
        "专业版应用启动排行Top50-周累计",
        "教育版应用启动排行Top50-周累计",
        "专业版检查更新失败率-周累计",
        "检查更新失败原因分布-周累计",
        "smb挂载失败率-周累计",
        "smb挂载失败原因分布-周累计",
        "应用商店deb应用新增下载应用排行Top30及下载失败率-周累计",
        "应用商店deb应用更新下载应用排行Top30及下载失败率-周累计",
        "应用商店deb应用安装失败次数排行Top5及安装失败率-周累计",
        "应用商店玲珑应用新增下载应用排行Top10及下载失败率-周累计",
        "应用商店玲珑应用更新下载应用排行Top10及下载失败率-周累计",
        "应用商店玲珑应用安装失败次数排行Top5及安装失败率-周累计",
    ]:
        items.append(
            build_compare_item(
                snapshot,
                block_name,
                status="pending_live",
                reason="等待实时抓取覆盖",
            )
        )
    return items


def try_live_override(snapshot: WorkbookSnapshot, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    item_map = {item["block_name"]: item for item in items}
    live_candidates = [
        (
            "产品分布",
            extract_overview_product,
            {
                "date_from": "2026-05-10",
            },
        ),
        (
            "架构分布",
            extract_overview_arch,
            {
                "date_from": "2026-05-16",
            },
        ),
        (
            "专业版日新增用户数",
            extract_overview_new_users,
            {
                "edition": "Professional",
                "date_from": "2026-04-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "专业版累计用户数",
            extract_overview_total_users,
            {
                "edition": "Professional",
                "date_from": "2026-04-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "专业版1070u5累计用户数",
            extract_overview_specific_minor_total,
            {
                "edition": "Professional",
                "minor_version": "1070u5",
                "date_from": "2026-04-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "专业版V25累计用户数",
            extract_overview_major_version_total,
            {
                "edition": "Professional",
                "major_version": "25",
                "date_from": "2026-04-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "专业版版本系列用户分布",
            extract_overview_minor_version,
            {
                "edition": "Professional",
                "date_from": "2026-05-10",
            },
        ),
        (
            "产品分布",
            extract_overview_product,
            {
                "date_from": "2026-05-10",
            },
        ),
        (
            "架构分布",
            extract_overview_arch,
            {
                "date_from": "2026-05-16",
            },
        ),
        (
            "专业版日新增用户数",
            extract_overview_new_users,
            {
                "edition": "Professional",
                "date_from": "2026-04-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "专业版累计用户数",
            extract_overview_total_users,
            {
                "edition": "Professional",
                "date_from": "2026-04-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "专业版V25累计用户数",
            extract_overview_major_version_total,
            {
                "edition": "Professional",
                "major_version": "25",
                "date_from": "2026-04-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "专业版版本系列用户分布",
            extract_overview_minor_version,
            {
                "edition": "Professional",
                "date_from": "2026-05-10",
            },
        ),
        (
            "专业版用户-保险箱功能开启率（万分之）",
            extract_safe_box_open,
            {
                "edition": "Professional",
                "major_version": "20",
                "date_from": "2026-05-10",
            },
        ),
        (
            "专业版用户-全文搜索功能开启率（万分之）",
            extract_fulltext_open,
            {
                "edition": "Professional",
                "major_version": "20",
                "date_from": "2026-05-10",
            },
        ),
        (
            "专业版检查更新失败率-周累计",
            extract_system_update_fail_rate,
            {
                "edition": "Professional",
                "major_version": "20",
                "minor_version": "107x",
                "date_type": "周",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
            },
        ),
        (
            "检查更新失败原因分布-周累计",
            extract_system_update_fail_cause,
            {
                "edition": "Professional",
                "major_version": "20",
                "minor_version": "107x",
                "date_type": "周",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
            },
        ),
        (
            "专业版应用启动排行Top50-周累计",
            extract_app_start_rank,
            {
                "edition": "Professional",
                "date_type": "周",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
            },
        ),
        (
            "教育版应用启动排行Top50-周累计",
            extract_app_start_rank,
            {
                "edition": "E",
                "date_type": "周",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
            },
        ),
        (
            "应用商店deb应用新增下载应用排行Top30及下载失败率-周累计",
            extract_appstore_deb_new,
            {
                "os": "Professional",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
                "date_type_ch": "周",
            },
        ),
        (
            "应用商店deb应用更新下载应用排行Top30及下载失败率-周累计",
            extract_appstore_deb_update,
            {
                "os": "Professional",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
                "date_type_ch": "周",
            },
        ),
        (
            "应用商店deb应用安装失败次数排行Top5及安装失败率-周累计",
            extract_appstore_deb_install_fail,
            {
                "os": "Professional",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
                "date_type_ch": "周",
            },
        ),
        (
            "应用商店玲珑应用新增下载应用排行Top10及下载失败率-周累计",
            extract_appstore_linglong_new,
            {
                "os": "Professional",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
                "date_type_ch": "周",
            },
        ),
        (
            "应用商店玲珑应用更新下载应用排行Top10及下载失败率-周累计",
            extract_appstore_linglong_update,
            {
                "os": "Professional",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
                "date_type_ch": "周",
            },
        ),
        (
            "应用商店玲珑应用安装失败次数排行Top5及安装失败率-周累计",
            extract_appstore_linglong_install_fail,
            {
                "os": "Professional",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
                "date_type_ch": "周",
            },
        ),
        (
            "任务栏模式配置",
            extract_taskbar,
            {
                "edition": "Professional",
                "major_version": "20",
                "minor_version": "107x",
                "date_type": "日",
                "date_from": "2026-05-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "单个插件的被移除率",
            extract_default_plugin_remove,
            {
                "edition": "Professional",
                "major_version": "20",
                "minor_version": "107x",
                "date_type": "日",
                "date_from": "2026-05-10",
                "date_to": "2026-05-10",
            },
        ),
        (
            "smb挂载失败率-周累计",
            extract_smb_rate,
            {
                "edition": "Professional",
                "major_version": "20",
                "minor_version": "107x",
                "date_type": "周",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
            },
        ),
        (
            "smb挂载失败原因分布-周累计",
            extract_smb_cause,
            {
                "edition": "Professional",
                "major_version": "20",
                "minor_version": "107x",
                "date_type": "周",
                "date_from": "2026-05-04",
                "date_to": "2026-05-10",
            },
        ),
    ]

    for block_name, extractor, query in live_candidates:
        session_name = f"default-{block_name}"
        try:
            payload = {
                "block": block_name,
                "query": query,
                "live_result": extractor(query, session=session_name),
            }
            if block_name in {"专业版用户-保险箱功能开启率（万分之）", "专业版用户-全文搜索功能开启率（万分之）"}:
                overview_live = extract_overview_minor_version({"edition": "Professional", "major_version": "20", "date_from": "2026-05-10"}, session=f"{session_name}-overview")
                payload["joined_overview_rows"] = overview_live.get("body_json", {}).get("row", {}).get("rows", [])
            compare_items = compare_live_result(snapshot, payload)
            if compare_items:
                item = compare_items[0]
                if item.get("status") == "matched":
                    item_map[block_name] = item
        except Exception:
            continue
        finally:
            close_session(session_name)
            if block_name in {"专业版用户-保险箱功能开启率（万分之）", "专业版用户-全文搜索功能开启率（万分之）"}:
                close_session(f"{session_name}-overview")

    ordered: list[dict[str, Any]] = []
    for item in items:
        ordered.append(item_map[item["block_name"]])
    return ordered


def build_live_only_compare(snapshot: WorkbookSnapshot) -> list[dict[str, Any]]:
    base_items = build_default_compare(snapshot)
    return try_live_override(snapshot, base_items)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", default="")
    parser.add_argument("--output-json", default=str(OUTPUT_DIR / "core_data_default_extract.json"))
    args = parser.parse_args()

    workbook = discover_workbook(args.workbook)
    snapshot = WorkbookSnapshot(workbook)
    payload = {
        "mode": "default_table",
        "workbook": str(workbook),
        "description": "按 workbook 已提及块生成统一 compare items；优先使用实时抓取结果。",
        "compare_items": build_live_only_compare(snapshot),
    }
    out = write_json(args.output_json, payload)
    print(out)


if __name__ == "__main__":
    main()
