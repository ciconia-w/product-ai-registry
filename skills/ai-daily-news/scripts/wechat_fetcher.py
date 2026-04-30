#!/usr/bin/env python3
"""
微信公众号新闻获取工具
从新智元微信文章中提取AI新闻
"""

import subprocess
import re
import json
import sys
from typing import List, Dict

def fetch_wechat_article(url: str) -> str:
    """获取微信文章 HTML 内容"""
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

def extract_news_from_html(html: str) -> List[Dict[str, str]]:
    """从微信公众号 HTML 中提取新闻条目"""
    news_list = []

    # 微信公众号文章通常使用 section标签或 p 标签包含内容
    # 尝试匹配常见的新闻格式

    # 方法1: 查找带粗体标题的段落
    pattern1 = r'<section[^>]*>.*?<strong>([^<]+)</strong>(.*?)</section>'
    matches = re.findall(pattern1, html, re.DOTALL)

    for title, content in matches:
        cleaned_title = title.strip()

        # 清理内容
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()

        # 过滤过短的内容
        if cleaned_title and len(content) > 10:
            news_list.append({
                "title": cleaned_title,
                "content": content,
                "source": "新智元",
                "link": ""
            })

    # 方法2: 如果方法1没找到数据，尝试查找 p 标签中的内容
    if not news_list:
        # 查找文章主体内容区域
        body_match = re.search(r'<div[^>]*class="[^"]*js_content[^"]*"[^>]*>(.*?)</div>', html, re.DOTALL)
        if body_match:
            body_text = body_match.group(1)

            # 分割成段落
            paragraphs = re.split(r'</p>|<br[^>]*>', body_text)

            current_title = None
            current_content = []

            for para in paragraphs:
                # 移除HTML标签
                clean_para = re.sub(r'<[^>]+>', '', para).strip()

                if not clean_para:
                    continue

                # 搜索粗体标题
                if '<strong>' in para or '**' in clean_para:
                    # 保存之前的新闻
                    if current_title and current_content:
                        full_content = ' '.join(current_content)
                        news_list.append({
                            "title": current_title,
                            "content": full_content,
                            "source": "新智元",
                            "link": ""
                        })

                    # 提取新标题
                    title_match = re.search(r'>([^<]+)</', para)
                    if title_match:
                        current_title = title_match.group(1).strip()
                    else:
                        current_title = re.sub(r'\*\*', '', clean_para).strip()

                    current_content = []
                elif current_title:
                    current_content.append(clean_para)

            # 保存最后一条
            if current_title and current_content:
                full_content = ' '.join(current_content)
                news_list.append({
                    "title": current_title,
                    "content": full_content,
                    "source": "新智元",
                    "link": ""
                })

    return news_list

def parse_wechat_news(url: str = None) -> List[Dict[str, str]]:
    """解析微信公众号文章"""
    if url is None:
        url = "https://mp.weixin.qq.com/s/sC39X7EsSzy79usg8am64w"

    html = fetch_wechat_article(url)
    news_list = extract_news_from_html(html)

    # 添加元数据
    for news in news_list:
        if not news.get("link"):
            news["link"] = url
        news["language"] = "zh"
        news["pub_date"] = ""
        news["type"] = "news"

    return news_list

if __name__ == "__main__":
    try:
        news_list = parse_wechat_news()

        # 输出为 JSON，格式与 rss_fetcher.py 一致
        output = {
            "source": "新智元",
            "count": len(news_list),
            "datetime": news_list[0].get("pub_date", "") if news_list else "",
            "news": news_list
        }

        print(json.dumps(output, ensure_ascii=False, indent=2))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
