#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from core_data_common import WorkbookSnapshot, build_compare_item, canonical_block_name, normalise_matrix


def _live_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    return payload.get("live_result", {}).get("body_json", {}).get("row", {}).get("rows", []) or []


def _sorted_rows(rows: list[list[Any]], key_indexes: tuple[int, ...]) -> list[list[Any]]:
    return sorted(rows, key=lambda row: tuple(row[index] for index in key_indexes))


def _live_error_item(snapshot: WorkbookSnapshot, block: str, payload: dict[str, Any]) -> list[dict[str, Any]] | None:
    live_result = payload.get("live_result", {})
    status_code = live_result.get("status")
    if status_code == 401:
        return [
            build_compare_item(
                snapshot,
                block,
                status="unauthorized",
                reason="opencli 会话未处于有效登录态，真实请求返回 401",
                page_value=live_result,
            )
        ]
    rows = _live_rows(payload)
    if not rows:
        return [
            build_compare_item(
                snapshot,
                block,
                status="interface_empty",
                reason="真实请求已执行，但当前返回空结果",
                page_value=live_result,
            )
        ]
    return None


def _taskbar_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    pro = {row["minor_version_category"]: [row["efficient_model_nums"], row["fashion_model_nums"]] for row in rows if row.get("edition_name") == "Professional"}
    workbook_value = {
        "106x": normalise_matrix(snapshot.block_matrix("任务栏模式配置"))[0][2:4],
        "107x": normalise_matrix(snapshot.block_matrix("任务栏模式配置"))[1][2:4],
    }
    page_value = {"106x": pro.get("106x"), "107x": pro.get("107x")}
    status = "matched" if workbook_value == page_value else "mismatch"
    reason = "真实请求层按指定日期回放后已与 workbook 对齐" if status == "matched" else "真实请求层返回与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            "任务栏模式配置",
            status=status,
            reason=reason,
            key_dims="Professional / 106x,107x",
            workbook_value=workbook_value,
            page_value=page_value,
            request_value=page_value,
        )
    ]


def _plugin_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    workbook_value = normalise_matrix(snapshot.block_matrix("单个插件的被移除率"))
    page_value = [
        [
            row.get("xAxis"),
            row.get("disable_rate_106x"),
            row.get("disable_nums_106x"),
            row.get("total_nums_106x"),
            row.get("disable_rate_107x"),
            row.get("disable_nums_107x"),
            row.get("total_nums_107x"),
        ]
        for row in rows
    ]
    status = "matched" if workbook_value == page_value else "mismatch"
    reason = "真实请求层按指定日期与 Professional 口径回放后已与 workbook 对齐" if status == "matched" else "真实请求层返回与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            "单个插件的被移除率",
            status=status,
            reason=reason,
            key_dims="Professional / 106x,107x",
            page_value=page_value,
            request_value=page_value,
        )
    ]


def _smb_cause_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    keep_versions = {"1070u3", "1070u4", "1070u5"}
    keep_arch = {"AMD64", "ARM64", "LoongArch"}
    page_value = [
        [
            row.get("minor_version"),
            row.get("architecture"),
            row.get("total_error_times"),
            row.get("three_error_times"),
            row.get("three_error_times_rate"),
            row.get("five_error_times"),
            row.get("five_error_times_rate"),
        ]
        for row in rows
        if row.get("minor_version") in keep_versions and row.get("architecture") in keep_arch
    ]
    workbook_value = normalise_matrix(snapshot.block_matrix("smb挂载失败原因分布-周累计"))
    status = "matched" if _sorted_rows(workbook_value, (0, 1)) == _sorted_rows(page_value, (0, 1)) else "mismatch"
    reason = "真实请求层已返回 1070u3/u4/u5 × 架构明细，当前结果与 workbook 对齐" if status == "matched" else "真实请求层已返回明细，但与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            "smb挂载失败原因分布-周累计",
            status=status,
            reason=reason,
            key_dims="Professional / 20 / 107x / 周 / 1070u3,u4,u5 × AMD64,ARM64,LoongArch",
            page_value=_sorted_rows(page_value, (0, 1)),
            request_value=_sorted_rows(page_value, (0, 1)),
        )
    ]


def _smb_rate_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    keep_versions = {"1070u3", "1070u4", "1070u5"}
    page_value = [
        [
            row.get("xAxis"),
            row.get("LoongArch_smb_load_fail_rate"),
            row.get("LoongArch"),
            row.get("LoongArch_total_load_nums"),
            row.get("ARM64_smb_load_fail_rate"),
            row.get("ARM64"),
            row.get("ARM64_total_load_nums"),
            row.get("AMD64_smb_load_fail_rate"),
            row.get("AMD64"),
            row.get("AMD64_total_load_nums"),
        ]
        for row in rows
        if row.get("xAxis") in keep_versions
    ]
    workbook_value = normalise_matrix(snapshot.block_matrix("smb挂载失败率-周累计"))
    status = "matched" if _sorted_rows(workbook_value, (0,)) == _sorted_rows(page_value, (0,)) else "mismatch"
    reason = "真实请求层已返回 1070u3/u4/u5 行级失败率，当前结果与 workbook 对齐" if status == "matched" else "真实请求层已返回行级失败率，但与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            "smb挂载失败率-周累计",
            status=status,
            reason=reason,
            key_dims="Professional / 20 / 107x / 周 / 1070u3,u4,u5",
            page_value=_sorted_rows(page_value, (0,)),
            request_value=_sorted_rows(page_value, (0,)),
        )
    ]


def _app_start_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any], block_name: str) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    page_value = [[row.get("xAxis"), row.get("应用启动次数")] for row in rows[:50]]
    workbook_value = normalise_matrix(snapshot.block_matrix(block_name))
    status = "matched" if workbook_value == page_value[: len(workbook_value)] else "mismatch"
    reason = "真实请求层周区间排行已与 workbook 对齐" if status == "matched" else "真实请求层排行与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            block_name,
            status=status,
            reason=reason,
            key_dims=f"{payload['query'].get('edition')} / 周 / {payload['query'].get('date_from')} ~ {payload['query'].get('date_to')}",
            page_value=page_value,
            request_value=page_value,
        )
    ]


def _overview_simple_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any], block_name: str, keys: list[str]) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    workbook_value = normalise_matrix(snapshot.block_matrix(block_name))
    page_value = [[row.get(key) for key in keys] for row in rows]

    if block_name == "产品分布":
        wanted = ["Military", "Community", "Professional", "Home", "E"]
        page_value = [[row.get("edition_name"), row.get("v")] for row in rows if row.get("edition_name") in wanted]
        page_value = sorted(page_value, key=lambda row: wanted.index(row[0]))
    elif block_name == "架构分布":
        wanted = ["SW64", "MIPS64", "LoongArch", "ARM64", "AMD64"]
        page_value = [[row.get("architecture"), row.get("v")] for row in rows if row.get("architecture") in wanted]
        page_value = sorted(page_value, key=lambda row: wanted.index(row[0]))
    elif block_name == "专业版累计用户数":
        wanted = {row[0] for row in workbook_value}
        page_value = [[row.get("xAxis"), row.get("nums")] for row in rows if row.get("xAxis") in wanted]
        page_value = sorted(page_value, key=lambda row: row[0], reverse=True)
    elif block_name == "专业版日新增用户数":
        page_value = sorted([[row.get("xAxis"), row.get("nums")] for row in rows], key=lambda row: row[0], reverse=True)
    elif block_name == "专业版V25累计用户数":
        wanted = {row[0] for row in workbook_value}
        page_value = [[row.get("xAxis"), row.get("nums")] for row in rows if row.get("xAxis") in wanted]
        page_value = sorted(page_value, key=lambda row: row[0], reverse=True)
    elif block_name == "专业版1070u5累计用户数":
        wanted = {row[0] for row in workbook_value}
        page_value = [[row.get("xAxis"), row.get("nums")] for row in rows if row.get("xAxis") in wanted]
        page_value = sorted(page_value, key=lambda row: row[0], reverse=True)
    elif block_name == "专业版版本系列用户分布":
        wanted = {str(row[0]) for row in workbook_value}
        page_value = [[row.get("minor_version"), row.get("v")] for row in rows if str(row.get("minor_version")) in wanted]
        aggregated = {}
        for row in workbook_value:
            key = str(row[0])
            aggregated[key] = aggregated.get(key, 0) + row[1]
        workbook_pairs = {(key, value) for key, value in aggregated.items()}
        page_pairs = {(str(row[0]), row[1]) for row in page_value}
        status = "matched" if page_pairs.issubset(workbook_pairs) else "mismatch"
        reason = "真实请求层结果已与 workbook 对齐" if status == "matched" else "真实请求层结果与 workbook 不一致"
        return [
            build_compare_item(
                snapshot,
                block_name,
                status=status,
                reason=reason,
                key_dims=payload["query"].get("date_from", ""),
                page_value=page_value,
                request_value=page_value,
            )
        ]

    status = "matched" if workbook_value == page_value[: len(workbook_value)] else "mismatch"
    reason = "真实请求层结果已与 workbook 对齐" if status == "matched" else "真实请求层结果与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            block_name,
            status=status,
            reason=reason,
            key_dims=payload["query"].get("date_from", ""),
            page_value=page_value,
            request_value=page_value,
        )
    ]


def _file_manager_open_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any], block_name: str) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    overview_rows = payload.get("joined_overview_rows", [])
    overview_map = {str(row["minor_version"]): row["v"] for row in overview_rows}
    workbook_value = normalise_matrix(snapshot.block_matrix(block_name))
    wanted = {str(row[0]) for row in workbook_value}
    page_value = []
    for row in rows:
        minor_version = str(row.get("minor_version"))
        if minor_version not in overview_map or minor_version not in wanted:
            continue
        open_nums = row.get("open_nums")
        total_nums = overview_map[minor_version]
        open_rate = round(open_nums * 10000 / total_nums, 2) if total_nums else 0
        page_value.append([minor_version, open_rate, open_nums, total_nums])
    order = [str(row[0]) for row in workbook_value]
    page_value = sorted(page_value, key=lambda row: order.index(str(row[0])))
    wb_norm = [[str(row[0]), row[1], row[2], row[3]] for row in workbook_value]
    pv_norm = [[str(row[0]), row[1], row[2], row[3]] for row in page_value[: len(workbook_value)]]
    status = "matched" if wb_norm == pv_norm else "mismatch"
    reason = "真实请求层已取到 open_nums，并用 overview 用户数拼出 workbook 口径" if status == "matched" else "真实请求层组合口径与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            block_name,
            status=status,
            reason=reason,
            key_dims=f"{payload['query'].get('edition')} / {payload['query'].get('major_version')} / {payload['query'].get('date_from')}",
            page_value=page_value,
            request_value=page_value,
        )
    ]


def _appstore_rank_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any], block_name: str, keys: list[str]) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    workbook_value = normalise_matrix(snapshot.block_matrix(block_name))
    page_value = []
    for row in rows:
        if keys == ["xAxis", "下载成功", "下载失败"]:
            success = row.get("下载成功")
            fail = row.get("下载失败")
            rate = round(fail / (success + fail), 15) if (success + fail) else None
            page_value.append([row.get("xAxis"), success, fail, rate])
        elif keys == ["xAxis", "安装失败次数", "安装失败率"]:
            rate = row.get("安装失败率")
            if isinstance(rate, str) and rate.endswith("%"):
                try:
                    rate = round(float(rate[:-1]) / 100, 4)
                except Exception:
                    pass
            page_value.append([row.get("xAxis"), row.get("安装失败次数"), rate])
        else:
            page_value.append([row.get(key) for key in keys])
    if keys == ["xAxis", "下载成功", "下载失败"]:
        page_value = sorted(page_value, key=lambda row: (-row[1], row[0]))
    elif keys == ["xAxis", "安装失败次数", "安装失败率"]:
        page_value = sorted(page_value, key=lambda row: (-row[1], row[0]))
    if block_name == "应用商店玲珑应用更新下载应用排行Top10及下载失败率-周累计":
        wb_names = [row[0] for row in workbook_value]
        page_map = {row[0]: row for row in page_value}
        page_value = [page_map[name] for name in wb_names if name in page_map]
    else:
        page_value = page_value[: len(workbook_value)]

    def normalise_rate(v):
        if isinstance(v, float):
            return round(v, 12)
        return v

    wb_norm = [[row[0], row[1], row[2], normalise_rate(row[3]) if len(row) > 3 else row[2]] if len(row) > 3 else row for row in workbook_value]
    pv_norm = [[row[0], row[1], row[2], normalise_rate(row[3]) if len(row) > 3 else row[2]] if len(row) > 3 else row for row in page_value]
    status = "matched" if wb_norm == pv_norm else "mismatch"
    reason = "真实请求层应用商店排行已与 workbook 对齐" if status == "matched" else "真实请求层应用商店排行与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            block_name,
            status=status,
            reason=reason,
            key_dims=f"{payload['query'].get('os')} / {payload['query'].get('date_from')} ~ {payload['query'].get('date_to')}",
            page_value=page_value,
            request_value=page_value,
        )
    ]


def _system_update_rate_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    keep_versions = {"1070u3", "1070u4", "1070u5"}
    page_value = []
    for row in rows:
        if row.get("xAxis") not in keep_versions:
            continue
        page_value.append([
            row.get("xAxis"),
            row.get("LoongArch_check_fail_rate"),
            row.get("LoongArch"),
            row.get("LoongArch_total_check_nums"),
            row.get("ARM64_check_fail_rate"),
            row.get("ARM64"),
            row.get("ARM64_total_check_nums"),
            row.get("AMD64_check_fail_rate"),
            row.get("AMD64"),
            row.get("AMD64_total_check_nums"),
        ])
    workbook_value = normalise_matrix(snapshot.block_matrix("专业版检查更新失败率-周累计"))
    order = {row[0]: i for i, row in enumerate(workbook_value)}
    page_value = sorted(page_value, key=lambda row: order.get(row[0], 999))
    status = "matched" if workbook_value == page_value else "mismatch"
    reason = "真实请求层系统更新失败率已与 workbook 对齐" if status == "matched" else "真实请求层系统更新失败率与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            "专业版检查更新失败率-周累计",
            status=status,
            reason=reason,
            key_dims=f"{payload['query'].get('edition')} / {payload['query'].get('major_version')} / {payload['query'].get('minor_version')} / {payload['query'].get('date_from')} ~ {payload['query'].get('date_to')}",
            page_value=page_value,
            request_value=page_value,
        )
    ]


def _system_update_cause_compare(snapshot: WorkbookSnapshot, payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = _live_rows(payload)
    keep_versions = {"1070u3", "1070u4", "1070u5"}
    keep_arch = {"AMD64", "ARM64", "LoongArch"}
    page_value = []
    for row in rows:
        if row.get("minor_version") not in keep_versions or row.get("architecture") not in keep_arch:
            continue
        page_value.append([
            row.get("minor_version"),
            row.get("architecture"),
            row.get("total_error_nums"),
            row.get("IndexDownloadFailed"),
            row.get("IndexDownloadFailed_rate"),
            row.get("JobError::IndexDownloadFailed"),
            row.get("JobError::IndexDownloadFailed_rate"),
            row.get("platformUnreachable"),
            row.get("platformUnreachable_rate"),
            row.get("insufficientSpace"),
            row.get("insufficientSpace_rate"),
            row.get("JobError::ErrorUnknown"),
            row.get("JobError::ErrorUnknown_rate"),
            row.get("JobError::insufficientSpace"),
            row.get("JobError::insufficientSpace_rate"),
            row.get("JobError::unmetDependencies"),
            row.get("JobError::unmetDependencies_rate"),
            row.get("JobError::fetchFailed"),
            row.get("JobError::fetchFailed_rate"),
            row.get("dpkgError"),
            row.get("dpkgError_rate"),
            row.get("JobError::invalidSourceList"),
            row.get("JobError::invalidSourceList_rate"),
            row.get("ErrorUnknown"),
            row.get("ErrorUnknown_rate"),
            row.get("fetchFailed"),
            row.get("fetchFailed_rate"),
            row.get("invalidSourceList"),
            row.get("invalidSourceList_rate"),
        ])
    workbook_value = normalise_matrix(snapshot.block_matrix("检查更新失败原因分布-周累计"))
    order = {(row[0], row[1]): i for i, row in enumerate(workbook_value)}
    page_value = sorted(page_value, key=lambda row: order.get((row[0], row[1]), 999))
    status = "matched" if workbook_value == page_value else "mismatch"
    reason = "真实请求层系统更新失败原因分布已与 workbook 对齐" if status == "matched" else "真实请求层系统更新失败原因分布与 workbook 不一致"
    return [
        build_compare_item(
            snapshot,
            "检查更新失败原因分布-周累计",
            status=status,
            reason=reason,
            key_dims=f"{payload['query'].get('edition')} / {payload['query'].get('major_version')} / {payload['query'].get('minor_version')} / {payload['query'].get('date_from')} ~ {payload['query'].get('date_to')}",
            page_value=page_value,
            request_value=page_value,
        )
    ]


def compare_live_result(snapshot: WorkbookSnapshot, payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = canonical_block_name(payload["block"])
    error_items = _live_error_item(snapshot, block, payload)
    if error_items is not None:
        return error_items
    if block == "任务栏模式配置":
        return _taskbar_compare(snapshot, payload)
    if block == "单个插件的被移除率":
        return _plugin_compare(snapshot, payload)
    if block == "产品分布":
        return _overview_simple_compare(snapshot, payload, block, ["edition_name", "v"])
    if block == "架构分布":
        return _overview_simple_compare(snapshot, payload, block, ["architecture", "v"])
    if block == "专业版累计用户数":
        return _overview_simple_compare(snapshot, payload, block, ["xAxis", "nums"])
    if block == "专业版日新增用户数":
        return _overview_simple_compare(snapshot, payload, block, ["xAxis", "nums"])
    if block == "专业版V25累计用户数":
        return _overview_simple_compare(snapshot, payload, block, ["xAxis", "nums"])
    if block == "专业版1070u5累计用户数":
        return _overview_simple_compare(snapshot, payload, block, ["xAxis", "nums"])
    if block == "专业版版本系列用户分布":
        return _overview_simple_compare(snapshot, payload, block, ["minor_version", "v"])
    if block == "专业版用户-保险箱功能开启率（万分之）":
        return _file_manager_open_compare(snapshot, payload, block)
    if block == "专业版用户-全文搜索功能开启率（万分之）":
        return _file_manager_open_compare(snapshot, payload, block)
    if block == "专业版检查更新失败率-周累计":
        return _system_update_rate_compare(snapshot, payload)
    if block == "检查更新失败原因分布-周累计":
        return _system_update_cause_compare(snapshot, payload)
    if block == "应用商店deb应用新增下载应用排行Top30及下载失败率-周累计":
        return _appstore_rank_compare(snapshot, payload, block, ["xAxis", "下载成功", "下载失败"])
    if block == "应用商店deb应用更新下载应用排行Top30及下载失败率-周累计":
        return _appstore_rank_compare(snapshot, payload, block, ["xAxis", "下载成功", "下载失败"])
    if block == "应用商店deb应用安装失败次数排行Top5及安装失败率-周累计":
        return _appstore_rank_compare(snapshot, payload, block, ["xAxis", "安装失败次数", "安装失败率"])
    if block == "应用商店玲珑应用新增下载应用排行Top10及下载失败率-周累计":
        return _appstore_rank_compare(snapshot, payload, block, ["xAxis", "下载成功", "下载失败"])
    if block == "应用商店玲珑应用更新下载应用排行Top10及下载失败率-周累计":
        return _appstore_rank_compare(snapshot, payload, block, ["xAxis", "下载成功", "下载失败"])
    if block == "应用商店玲珑应用安装失败次数排行Top5及安装失败率-周累计":
        return _appstore_rank_compare(snapshot, payload, block, ["xAxis", "安装失败次数", "安装失败率"])
    if block == "专业版应用启动排行Top50-周累计":
        return _app_start_compare(snapshot, payload, block)
    if block == "教育版应用启动排行Top50-周累计":
        return _app_start_compare(snapshot, payload, block)
    if block == "smb挂载失败率-周累计":
        return _smb_rate_compare(snapshot, payload)
    if block == "smb挂载失败原因分布-周累计":
        return _smb_cause_compare(snapshot, payload)
    return [
        build_compare_item(
            snapshot,
            block,
            status="unsupported",
            reason="当前 block 尚未接入 live 对照规范化器",
            page_value=payload.get("live_result", {}),
        )
    ]
