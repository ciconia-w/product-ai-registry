#!/usr/bin/env python3
"""
AI 新闻解析工具
从当前配置中的中文主源 HTML 中提取新闻条目。
默认主源为 hex2077.dev（原 ai.hubtoday.app）。
"""

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

import yaml

SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "references" / "sources.yaml"
DEFAULT_PRIMARY_SOURCE = {
    "name": "hex2077.dev",
    "url": "https://hex2077.dev/docs/{date:YYYY-MM}/{date:YYYY-MM-DD}/",
    "parser": "parse_news.py",
}


def load_primary_source() -> Dict[str, str]:
    """从 sources.yaml 中读取当前脚本对应的中文主源定义。"""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
        primary_sources = config.get("sources", {}).get("chinese", {}).get("primary", [])
        for source in primary_sources:
            if source.get("parser") == "parse_news.py":
                return source
        if primary_sources:
            return primary_sources[0]
    except Exception as e:
        print(f"Warning: failed to load primary source config: {e}", file=sys.stderr)
    return DEFAULT_PRIMARY_SOURCE


def build_source_url(template: str, date_str: str) -> str:
    """将日期占位符替换为具体日期。"""
    return (
        template
        .replace("{date:YYYY-MM}", date_str[:7])
        .replace("{date:YYYY-MM-DD}", date_str)
    )


def fetch_html(date_str: str) -> str:
    """获取 HTML 内容"""
    primary_source = load_primary_source()
    template = primary_source.get("url", DEFAULT_PRIMARY_SOURCE["url"])
    url = build_source_url(template, date_str)
    cmd = [
        "curl", "-s", "-L",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-H", "Accept: text/html,application/xhtml+xml",
        url,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to fetch {url}")
    return result.stdout


def extract_sections(html: str) -> Dict[str, str]:
    """从 HTML 中提取各个分类的 HTML 内容"""
    sections: Dict[str, str] = {}

    section_names = [
        "产品与功能更新",
        "前沿研究",
        "行业展望与社会影响",
        "开源top项目",
        "社媒分享",
    ]

    for i, section_name in enumerate(section_names):
        pattern = rf'<h3[^>]*id="{section_name}"[^>]*>'
        match = re.search(pattern, html)
        if not match:
            print(f"Warning: Section '{section_name}' not found", file=sys.stderr)
            sections[section_name] = ""
            continue
        start_pos = match.start()

        if i + 1 < len(section_names):
            next_section_name = section_names[i + 1]
            end_pattern = rf'<h3[^>]*id="{next_section_name}"[^>]*>'
            end_match = re.search(end_pattern, html[start_pos:])
            end_pos = start_pos + end_match.start() if end_match else -1
        else:
            end_match = re.search(r'<h2|AI资讯日报多渠道|<footer', html[start_pos:])
            end_pos = start_pos + end_match.start() if end_match else -1

        if end_pos == -1:
            sections[section_name] = html[start_pos:start_pos + 15000]
        else:
            sections[section_name] = html[start_pos:end_pos]

    return sections


def extract_news_from_section(section_html: str) -> List[Dict[str, str]]:
    """从一个分类的 HTML 中提取新闻条目"""
    news_list = []

    li_pattern = r'<li[^>]*>(.*?)</li>'
    li_matches = re.findall(li_pattern, section_html, re.DOTALL)

    for li_content in li_matches:
        if "<p" not in li_content:
            continue

        title_match = re.search(r'<strong[^>]*>([^<]+)</strong>', li_content)
        if not title_match:
            continue
        title = title_match.group(1).strip().rstrip("。")

        link_match = re.search(r'<a[^>]+href="([^"]+)"[^>]*>', li_content)
        link = link_match.group(1) if link_match else ""

        p_match = re.search(r'<p[^>]*>(.*?)</p>', li_content, re.DOTALL)
        content_html = p_match.group(1) if p_match else li_content

        content = re.sub(r'<a[^>]*>([^<]*)</a>', r"\1", content_html)
        content = re.sub(r"<[^>]+>", " ", content)
        content = re.sub(r"\s+", " ", content).strip()
        if len(content) > 300:
            content = content[:300] + "..."

        if title and content:
            item = {"title": title, "content": content}
            if link:
                item["link"] = link
            news_list.append(item)

    return news_list


def parse_news(date_str: str) -> List[Dict[str, str]]:
    """解析指定日期的新闻"""
    html = fetch_html(date_str)
    sections = extract_sections(html)

    section_display_names = {
        "产品与功能更新": "产品与功能更新",
        "前沿研究": "前沿研究",
        "行业展望与社会影响": "行业展望与社会影响",
        "开源top项目": "开源TOP项目",
        "社媒分享": "社媒分享",
    }

    all_news = []
    for section_name, section_html in sections.items():
        if not section_html:
            continue

        news_list = extract_news_from_section(section_html)
        display_name = section_display_names.get(section_name, section_name)
        for news in news_list:
            news["category"] = display_name
            all_news.append(news)

    return all_news


if __name__ == "__main__":
    if len(sys.argv) > 1:
        date_str = sys.argv[1]
    else:
        from datetime import datetime
        date_str = datetime.now().strftime("%Y-%m-%d")

    try:
        news_list = parse_news(date_str)
        output = {
            "date": date_str,
            "count": len(news_list),
            "news": news_list,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
