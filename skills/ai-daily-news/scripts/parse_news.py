#!/usr/bin/env python3
"""
AI 新闻解析工具
从 ai.hubtoday.app 的 HTML 中提取新闻条目
"""

import subprocess
import re
import json
import sys
from typing import List, Dict

def fetch_html(date_str: str) -> str:
    """获取 HTML 内容"""
    url = f"https://ai.hubtoday.app/{date_str[:7]}/{date_str}/"
    cmd = [
        "curl", "-s", "-L",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "-H", "Accept: text/html,application/xhtml+xml",
        url
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
        "开源TOP项目",
        "社媒分享"
    ]

    for i, section_name in enumerate(section_names):
        # 找到当前分类的起始位置
        start_pattern = f"<h3>{section_name}"
        start_pos = html.find(start_pattern)

        if start_pos == -1:
            print(f"Warning: Section '{section_name}' not found", file=sys.stderr)
            sections[section_name] = ""
            continue

        # 找到下一个分类的起始位置
        if i + 1 < len(section_names):
            next_section_name = section_names[i + 1]
            end_pattern = f"<h3>{next_section_name}"
            end_pos = html.find(end_pattern, start_pos)
        else:
            # 最后一个分类，找到页面结束或下一个 h2/h3
            # 查找 AI资讯日报多渠道 作为结束标记
            end_pattern = '<h2><strong>AI资讯日报多渠道</strong>'
            end_pos = html.find(end_pattern, start_pos)
            if end_pos == -1:
                # 如果没找到，就用下一个 h2
                end_pos = html.find("<h2", start_pos)

        if end_pos == -1:
            # 没找到结束标记，截取到末尾（最多 10000 字符）
            sections[section_name] = html[start_pos:start_pos + 10000]
        else:
            sections[section_name] = html[start_pos:end_pos]

    return sections

def extract_news_from_section(section_html: str) -> List[Dict[str, str]]:
    """从一个分类的 HTML 中提取新闻条目"""
    news_list = []

    # 新格式：<li><strong>标题。</strong>内容</li>（无<p>标签）
    # 同时支持旧格式：<li><p><strong>标题。</strong>内容</p></li>
    pattern_new = r'<li><strong>([^<]+)</strong>(.*?)(?:</li>|<li>|$)'
    pattern_old = r'<li><p><strong>([^<]+)</strong>(.*?)</p></li>'
    
    # 先尝试新格式
    matches = re.findall(pattern_new, section_html, re.DOTALL)
    
    # 如果新格式没匹配到，尝试旧格式
    if not matches:
        matches = re.findall(pattern_old, section_html, re.DOTALL)

    for title, content in matches:
        # 清理标题（去掉句号）
        title = title.strip().rstrip('。')

        # 提取链接（查找内容中的 <a href="...">）
        link_match = re.search(r'<a[^>]+href="([^"]+)"', content)
        link = link_match.group(1) if link_match else ""

        # 清理内容（移除 HTML 标签和多余空白，但保留关键词）
        content_clean = re.sub(r'<[^>]+>', ' ', content)
        content_clean = re.sub(r'\s+', ' ', content_clean)
        content_clean = content_clean.strip()

        if title and content_clean:
            item = {
                "title": title,
                "content": content_clean
            }
            # 只在有链接时添加 link 字段
            if link:
                item["link"] = link
            news_list.append(item)

    return news_list

def parse_news(date_str: str) -> List[Dict[str, str]]:
    """解析指定日期的新闻"""
    html = fetch_html(date_str)
    sections = extract_sections(html)

    all_news = []
    for section_name, section_html in sections.items():
        if not section_html:
            continue

        news_list = extract_news_from_section(section_html)

        # 添加分类信息
        for news in news_list:
            news["category"] = section_name
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

        # 输出为 JSON
        output = {
            "date": date_str,
            "news": news_list
        }

        print(json.dumps(output, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
