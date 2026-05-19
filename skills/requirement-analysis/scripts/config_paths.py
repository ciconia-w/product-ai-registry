#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path


PACKAGE_SCRIPT_DIR = Path(__file__).resolve().parent
LOCAL_CONFIG_DIR = Path.home() / ".config" / "requirement-analysis"
LOCAL_FEISHU_TARGET = LOCAL_CONFIG_DIR / "feishu-target.json"
LOCAL_SOURCES_CONFIG = LOCAL_CONFIG_DIR / "local_sources.json"
