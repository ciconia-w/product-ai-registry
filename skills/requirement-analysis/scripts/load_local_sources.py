#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取本地数据源配置。

优先级：
1. ~/.config/requirement-analysis/local_sources.json
2. 环境变量
3. 代码默认公共值（仅限非敏感字段）
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_DIR = Path.home() / ".config" / "requirement-analysis"
LOCAL_CONFIG_PATH = CONFIG_DIR / "local_sources.json"


def _read_local_file() -> dict[str, Any]:
    if not LOCAL_CONFIG_PATH.exists():
        return {}
    return json.loads(LOCAL_CONFIG_PATH.read_text(encoding="utf-8"))


def load_forum_config() -> dict[str, Any]:
    file_cfg = _read_local_file().get("forum", {})
    return {
        "thread_api": os.environ.get("REQ_FORUM_THREAD_API") or file_cfg.get("thread_api") or "",
        "detail_api": os.environ.get("REQ_FORUM_DETAIL_API") or file_cfg.get("detail_api") or "",
        "contact_hint": os.environ.get("REQ_FORUM_CONTACT_HINT") or file_cfg.get("contact_hint") or "论坛接口异常，请联系内部接口维护人排查。",
    }


def load_feedback_platform_config() -> dict[str, Any]:
    file_cfg = _read_local_file().get("feedback_platform", {})
    return {
        "base_url": os.environ.get("REQ_FEEDBACK_BASE_URL") or file_cfg.get("base_url") or "https://cooperation.uniontech.com/api/v2/open/worksheet/getFilterRows",
        "app_key": os.environ.get("REQ_FEEDBACK_APP_KEY") or file_cfg.get("app_key") or "",
        "sign": os.environ.get("REQ_FEEDBACK_SIGN") or file_cfg.get("sign") or "",
        "worksheet_id": os.environ.get("REQ_FEEDBACK_WORKSHEET_ID") or file_cfg.get("worksheet_id") or "",
        "view_id": os.environ.get("REQ_FEEDBACK_VIEW_ID") or file_cfg.get("view_id") or "",
    }


def load_deepin_home_config() -> dict[str, Any]:
    file_cfg = _read_local_file().get("deepin_home_openapi", {})
    return {
        "base_url": os.environ.get("REQ_DEEPIN_HOME_BASE_URL") or file_cfg.get("base_url") or "https://cooperation.uniontech.com",
        "app_key": os.environ.get("REQ_DEEPIN_HOME_APP_KEY") or file_cfg.get("app_key") or "",
        "sign": os.environ.get("REQ_DEEPIN_HOME_SIGN") or file_cfg.get("sign") or "",
        "worksheet_id": os.environ.get("REQ_DEEPIN_HOME_WORKSHEET_ID") or file_cfg.get("worksheet_id") or "",
        "view_ids": file_cfg.get("view_ids") or {},
    }


def require_keys(config: dict[str, Any], keys: list[str], source_name: str) -> None:
    missing = [key for key in keys if not config.get(key)]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"{source_name} 缺少必要配置: {joined}。请在 scripts/local_sources.json 或环境变量中提供。"
        )
