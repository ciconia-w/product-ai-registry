#!/usr/bin/env python3
from __future__ import annotations

from typing import Any

from opencli_live_common import ensure_page, live_fetch


def extract_taskbar(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/personalization", session=session)
    body = {
        "sql_template_id": 107,
        "columns": "edition_name, minor_version_category,  efficient_model_nums, fashion_model_nums",
        "filters": [
            {"col": "dt", "op": "=", "val": query["date_from"]},
            {"col": "dt", "op": "!=", "val": "任务栏模式配置"},
            {"col": "date_type", "op": "=", "val": "日"},
        ],
        "order_by": [
            {"col": "edition_name", "sort": "asc"},
            {"col": "minor_version_category", "sort": "asc"},
        ],
    }
    return live_fetch("/v1/dream-io/system-events/personalized-configuration", body, session=session)


def extract_default_plugin_remove(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/personalization", session=session)
    body = {
        "sql_template_id": 109,
        "columns": "plugin_name_cn as xAxis",
        "filters": [
            {"col": "dt", "op": "=", "val": query["date_from"]},
            {"col": "dt", "op": "!=", "val": "单个默认插件的被移除率"},
            {"col": "default_plugin", "op": "=", "val": "default"},
            {"col": "date_type", "op": "=", "val": "日"},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
        ],
        "order_by": [{"col": "plugin_name_cn", "sort": "desc"}],
        "group_by": "plugin_name_cn",
        "pivot_query_data": {
            "is_valid": True,
            "column": "minor_version_category",
            "aggregate_function": "Custom",
            "custom_sql_tpl": "COALESCE(ROUND(disable_nums_sql_tpl * 100.0 / NULLIF(total_nums_sql_tpl, 0), 2), 0) AS disable_rate_sql_tpl, SUM(CASE WHEN minor_version_category = 'sql_tpl' THEN disable_apt_nums ELSE 0 END) AS disable_nums_sql_tpl, SUM(CASE WHEN minor_version_category = 'sql_tpl' THEN enable_apt_nums ELSE 0 END) + SUM(CASE WHEN minor_version_category = 'sql_tpl' THEN disable_apt_nums ELSE 0 END) as total_nums_sql_tpl",
        },
    }
    return live_fetch("/v1/dream-io/system-events/personalized-configuration", body, session=session)


def extract_smb_cause(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/file-manager", session=session)
    body = {
        "sql_template_id": 116,
        "columns": """minor_version,
         architecture,
         SUM(error_times) as total_error_times,
         SUM(case when error_id = '1' then error_times ELSE 0 end) as one_error_times,
         CASE WHEN total_error_times = 0 THEN 0.00 ELSE ROUND(one_error_times * 100.0 / total_error_times, 2) END AS one_error_times_rate,
         SUM(case when error_id = '2' then error_times ELSE 0 end) as two_error_times,
         CASE WHEN total_error_times = 0 THEN 0.00 ELSE ROUND(two_error_times * 100.0 / total_error_times, 2) END AS two_error_times_rate,
         SUM(case when error_id = '3' then error_times ELSE 0 end) as three_error_times,
         CASE WHEN total_error_times = 0 THEN 0.00 ELSE ROUND(three_error_times * 100.0 / total_error_times, 2) END AS three_error_times_rate,
         SUM(case when error_id = '4' then error_times ELSE 0 end) as four_error_times,
         CASE WHEN total_error_times = 0 THEN 0.00 ELSE ROUND(four_error_times * 100.0 / total_error_times, 2) END AS four_error_times_rate,
         SUM(case when error_id = '5' then error_times ELSE 0 end) as five_error_times,
         CASE WHEN total_error_times = 0 THEN 0.00 ELSE ROUND(five_error_times * 100.0 / total_error_times, 2) END AS five_error_times_rate""",
        "filters": [
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "date_type", "op": "=", "val": query["date_type"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
            {"col": "major_version", "op": "=", "val": query["major_version"]},
            {"col": "minor_version_category", "op": "=", "val": query["minor_version"]},
            {"col": "minor_version", "op": "!=", "val": ""},
            {"col": "dt", "op": "!=", "val": "smb挂载失败原因分布"},
            {"col": "architecture", "op": "!=", "val": ""},
        ],
        "order_by": [{"col": "minor_version_category", "sort": "asc"}],
        "group_by": "architecture,minor_version_category,edition_name,major_version,minor_version",
    }
    return live_fetch("/v1/dream-io/system-events/file-manager", body, session=session)


def extract_smb_rate(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/file-manager", session=session)
    body = {
        "sql_template_id": 117,
        "columns": "minor_version as xAxis",
        "filters": [
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "date_type", "op": "=", "val": query["date_type"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
            {"col": "major_version", "op": "=", "val": query["major_version"]},
            {"col": "minor_version_category", "op": "=", "val": query["minor_version"]},
            {"col": "minor_version", "op": "!=", "val": ""},
            {"col": "dt", "op": "!=", "val": "smb挂载失败率"},
            {"col": "architecture", "op": "!=", "val": ""},
        ],
        "order_by": [{"col": "minor_version", "sort": "asc"}],
        "group_by": "minor_version_category,edition_name,major_version,minor_version",
        "pivot_query_data": {
            "is_valid": True,
            "column": "architecture",
            "aggregate_function": "Custom",
            "custom_sql_tpl": (
                "CASE WHEN "
                "(SUM(CASE WHEN architecture = 'sql_tpl' THEN smb_load_success_nums ELSE 0 END) + "
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN smb_load_failed_nums ELSE 0 END)) = 0 "
                "THEN 0.00 "
                "ELSE ROUND("
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN smb_load_failed_nums ELSE 0 END) * 100.0 / "
                "(SUM(CASE WHEN architecture = 'sql_tpl' THEN smb_load_failed_nums ELSE 0 END) + "
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN smb_load_success_nums ELSE 0 END)), 2) END AS sql_tpl_smb_load_fail_rate, "
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN smb_load_failed_nums ELSE 0 END) as sql_tpl, "
                "(SUM(CASE WHEN architecture = 'sql_tpl' THEN smb_load_failed_nums ELSE 0 END) + "
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN smb_load_success_nums ELSE 0 END)) AS sql_tpl_total_load_nums"
            ),
        },
    }
    return live_fetch("/v1/dream-io/system-events/file-manager", body, session=session)


def extract_app_start_rank(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/application-launch", session=session)
    body = {
        "sql_template_id": 113,
        "columns": "app_name as xAxis, app_start_num as 应用启动次数",
        "filters": [
            {"col": "date_type", "op": "=", "val": query["date_type"]},
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
        ],
        "order_by": [{"col": "app_start_num", "sort": "desc"}],
        "group_by": "app_name,date_range,app_start_num",
    }
    return live_fetch("/v1/dream-io/system-events/app-start", body, session=session)


def extract_overview_product(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/point-overview", session=session)
    body = {
        "sql_template_id": 121,
        "columns": "edition_name, sum(total_nums) as v",
        "filters": [{"col": "dt", "op": "=", "val": query["date_from"]}],
        "order_by": [{"col": "v", "sort": "desc"}],
        "group_by": "edition_name",
    }
    return live_fetch("/v1/dream-io/app-store/overview", body, session=session)


def extract_overview_arch(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/point-overview", session=session)
    body = {
        "sql_template_id": 121,
        "columns": "architecture, sum(total_nums) as v",
        "filters": [{"col": "dt", "op": "=", "val": query["date_from"]}],
        "order_by": [{"col": "v", "sort": "desc"}],
        "group_by": "architecture",
    }
    return live_fetch("/v1/dream-io/app-store/overview", body, session=session)


def extract_overview_total_users(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/point-overview", session=session)
    body = {
        "sql_template_id": 121,
        "columns": "dt as xAxis, sum(total_nums) as nums",
        "filters": [
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
        ],
        "order_by": [{"col": "xAxis", "sort": "asc"}],
        "group_by": "dt",
    }
    return live_fetch("/v1/dream-io/app-store/overview", body, session=session)


def extract_overview_new_users(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/point-overview", session=session)
    body = {
        "sql_template_id": 121,
        "columns": "dt as xAxis, sum(new_nums) as nums",
        "filters": [
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
        ],
        "order_by": [{"col": "xAxis", "sort": "asc"}],
        "group_by": "dt",
    }
    return live_fetch("/v1/dream-io/app-store/overview", body, session=session)


def extract_overview_minor_version(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/point-overview", session=session)
    filters = [
        {"col": "dt", "op": "=", "val": query["date_from"]},
        {"col": "edition_name", "op": "=", "val": query["edition"]},
    ]
    if query.get("major_version"):
        filters.append({"col": "major_version", "op": "=", "val": query["major_version"]})
    body = {
        "sql_template_id": 121,
        "columns": "minor_version, sum(total_nums) as v",
        "filters": filters,
        "order_by": [{"col": "v", "sort": "desc"}],
        "group_by": "minor_version",
    }
    return live_fetch("/v1/dream-io/app-store/overview", body, session=session)


def extract_overview_major_version_total(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/point-overview", session=session)
    body = {
        "sql_template_id": 121,
        "columns": "dt as xAxis, sum(total_nums) as nums",
        "filters": [
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
            {"col": "major_version", "op": "=", "val": query["major_version"]},
        ],
        "order_by": [{"col": "xAxis", "sort": "asc"}],
        "group_by": "dt",
    }
    return live_fetch("/v1/dream-io/app-store/overview", body, session=session)


def extract_overview_specific_minor_total(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/point-overview", session=session)
    body = {
        "sql_template_id": 121,
        "columns": "dt as xAxis, sum(total_nums) as nums",
        "filters": [
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
            {"col": "minor_version", "op": "=", "val": query["minor_version"]},
        ],
        "order_by": [{"col": "xAxis", "sort": "asc"}],
        "group_by": "dt",
    }
    return live_fetch("/v1/dream-io/app-store/overview", body, session=session)


def extract_file_manager_open_feature(query: dict, sql_template_id: int, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/file-manager", session=session)
    body = {
        "sql_template_id": sql_template_id,
        "columns": "minor_version, sum(open_nums) as open_nums",
        "filters": [
            {"col": "dt", "op": "=", "val": query["date_from"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
            {"col": "major_version", "op": "=", "val": query["major_version"]},
        ],
        "order_by": [{"col": "minor_version", "sort": "asc"}],
        "group_by": "minor_version",
    }
    return live_fetch("/v1/dream-io/system-events/file-manager", body, session=session)


def extract_safe_box_open(query: dict, session: str = "default") -> dict[str, Any]:
    return extract_file_manager_open_feature(query, 115, session=session)


def extract_fulltext_open(query: dict, session: str = "default") -> dict[str, Any]:
    return extract_file_manager_open_feature(query, 118, session=session)


def extract_appstore_rank(query: dict, clause_type: str, pkg_install_mode: str, columns: str, order_col: str, limit: int | None = None, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/app/platform-download", session=session)
    body = {
        "sql_template_id": 51,
        "columns": columns,
        "filters": [
            {"col": "clause_type", "op": "=", "val": clause_type},
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "date_type_ch", "op": "=", "val": query["date_type_ch"]},
            {"col": "os", "op": "=", "val": query["os"]},
            {"col": "pkg_install_mode", "op": "=", "val": pkg_install_mode},
        ],
        "order_by": [{"col": order_col, "sort": "desc"}],
        "group_by": "app_name",
    }
    if "LENGTH(app_name)" not in columns:
        body["filters"].append({"col": "LENGTH(app_name)", "op": ">", "val": "0"})
    if limit is not None:
        body["limit"] = limit
    return live_fetch("/v1/dream-io/app-store/total-app-download", body, session=session)


def extract_appstore_deb_new(query: dict, session: str = "default") -> dict[str, Any]:
    return extract_appstore_rank(
        query,
        clause_type="4",
        pkg_install_mode="1",
        columns="app_name as xAxis, sum(new_download_success_num) as 下载成功, sum(new_download_fail_num) as 下载失败",
        order_col="下载成功",
        session=session,
    )


def extract_appstore_deb_update(query: dict, session: str = "default") -> dict[str, Any]:
    return extract_appstore_rank(
        query,
        clause_type="4",
        pkg_install_mode="1",
        columns="app_name as xAxis, sum(update_download_success_num) as 下载成功, sum(update_download_fail_num) as 下载失败",
        order_col="下载成功",
        session=session,
    )


def extract_appstore_deb_install_fail(query: dict, session: str = "default") -> dict[str, Any]:
    return extract_appstore_rank(
        query,
        clause_type="4",
        pkg_install_mode="1",
        columns="app_name as xAxis,sum(install_fail_num) as 安装失败次数, CONCAT(CAST(ROUND(CASE WHEN sum(install_num) = 0 THEN 0 ELSE CAST(sum(install_fail_num) AS FLOAT) / CAST(sum(install_num) AS FLOAT) * 100 END, 2) AS VARCHAR), '%') AS 安装失败率",
        order_col="安装失败次数",
        limit=5,
        session=session,
    )


def extract_appstore_linglong_new(query: dict, session: str = "default") -> dict[str, Any]:
    return extract_appstore_rank(
        query,
        clause_type="4",
        pkg_install_mode="2",
        columns="app_name as xAxis, sum(new_download_success_num) as 下载成功, sum(new_download_fail_num) as 下载失败",
        order_col="下载成功",
        session=session,
    )


def extract_appstore_linglong_update(query: dict, session: str = "default") -> dict[str, Any]:
    return extract_appstore_rank(
        query,
        clause_type="4",
        pkg_install_mode="2",
        columns="app_name as xAxis, sum(update_download_success_num) as 下载成功, sum(update_download_fail_num) as 下载失败",
        order_col="下载成功",
        session=session,
    )


def extract_appstore_linglong_install_fail(query: dict, session: str = "default") -> dict[str, Any]:
    return extract_appstore_rank(
        query,
        clause_type="4",
        pkg_install_mode="2",
        columns="app_name as xAxis,sum(install_fail_num) as 安装失败次数, CONCAT(CAST(ROUND(CASE WHEN sum(install_num) = 0 THEN 0 ELSE CAST(sum(install_fail_num) AS FLOAT) / CAST(sum(install_num) AS FLOAT) * 100 END, 2) AS VARCHAR), '%') AS 安装失败率",
        order_col="安装失败次数",
        limit=5,
        session=session,
    )


def extract_system_update_fail_rate(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/system-update", session=session)
    body = {
        "sql_template_id": 106,
        "columns": "minor_version as xAxis",
        "filters": [
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "date_type", "op": "=", "val": query["date_type"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
            {"col": "major_version", "op": "=", "val": query["major_version"]},
            {"col": "minor_version_category", "op": "=", "val": query["minor_version"]},
            {"col": "minor_version", "op": "!=", "val": ""},
            {"col": "dt", "op": "!=", "val": "检查更新失败率"},
            {"col": "architecture", "op": "!=", "val": ""},
        ],
        "order_by": [{"col": "minor_version", "sort": "desc"}],
        "group_by": "minor_version",
        "pivot_query_data": {
            "is_valid": True,
            "column": "architecture",
            "aggregate_function": "Custom",
            "custom_sql_tpl": (
                "CASE WHEN (SUM(CASE WHEN architecture = 'sql_tpl' THEN check_fail_nums ELSE 0 END) + "
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN check_success_nums ELSE 0 END)) = 0 "
                "THEN 0.00 ELSE ROUND(SUM(CASE WHEN architecture = 'sql_tpl' THEN check_fail_strict_nums ELSE 0 END) * 100.0 / "
                "(SUM(CASE WHEN architecture = 'sql_tpl' THEN check_fail_nums ELSE 0 END) + "
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN check_success_nums ELSE 0 END)), 2) END AS sql_tpl_check_fail_rate, "
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN check_fail_strict_nums ELSE 0 END) as sql_tpl, "
                "(SUM(CASE WHEN architecture = 'sql_tpl' THEN check_fail_nums ELSE 0 END) + "
                "SUM(CASE WHEN architecture = 'sql_tpl' THEN check_success_nums ELSE 0 END)) AS sql_tpl_total_check_nums"
            ),
        },
    }
    return live_fetch("/v1/dream-io/system-events/system-update", body, session=session)


def extract_system_update_fail_cause(query: dict, session: str = "default") -> dict[str, Any]:
    ensure_page("https://datan.uniontech.com/#/point/system-update", session=session)
    body = {
        "sql_template_id": 122,
        "columns": "minor_version,architecture,SUM(nums) as total_error_nums",
        "filters": [
            {"col": "dt", "op": ">=", "val": query["date_from"]},
            {"col": "dt", "op": "<=", "val": query["date_to"]},
            {"col": "date_type", "op": "=", "val": query["date_type"]},
            {"col": "edition_name", "op": "=", "val": query["edition"]},
            {"col": "major_version", "op": "=", "val": query["major_version"]},
            {"col": "minor_version_category", "op": "=", "val": query["minor_version"]},
            {"col": "minor_version", "op": "!=", "val": ""},
            {"col": "dt", "op": "!=", "val": "检查更新失败原因分布"},
            {"col": "architecture", "op": "!=", "val": ""},
            {"col": "minor_version_category", "op": "IN", "val": ["106x", "107x"]},
        ],
        "order_by": [
            {"col": "minor_version", "sort": "asc"},
            {"col": "architecture", "sort": "asc"},
        ],
        "group_by": "minor_version,architecture",
        "pivot_query_data": {
            "is_valid": True,
            "column": "err_type",
            "aggregate_function": "Custom",
            "custom_sql_tpl": (
                "SUM(case when err_type = 'sql_tpl' then nums ELSE 0 end) as \"sql_tpl\",\n"
                "CASE WHEN total_error_nums = 0 THEN 0.00 ELSE ROUND(\"sql_tpl\" * 100.0 / total_error_nums, 2) END AS \"sql_tpl_rate\""
            ),
        },
    }
    return live_fetch("/v1/dream-io/system-events/system-update", body, session=session)
