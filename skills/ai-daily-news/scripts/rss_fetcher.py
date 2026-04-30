#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS新闻获取引擎
支持多RSS源批量获取、标准化输出
"""

import feedparser
import requests
import json
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

# 导入翻译器
sys.path.append(str(Path(__file__).parent))
from translator import Translator

# 配置文件路径
SKILL_DIR = Path(__file__).parent.parent
CONFIG_PATH = SKILL_DIR / "references" / "sources.yaml"

class RSSFetcher:
    """RSS新闻获取器"""

    def __init__(self, config_path=None, translate=False):
        """初始化配置"""
        self.config_path = config_path or CONFIG_PATH
        self.sources = self.load_config()
        self.translate = translate
        # 初始化翻译器（只有在需要翻译的时候才初始化）
        if self.translate:
            self.translator = Translator()
        else:
            self.translator = None

    def load_config(self):
        """加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: 加载配置失败 {e}, 使用默认配置", file=sys.stderr)
            return self._default_config()

    def _default_config(self):
        """默认配置"""
        return {
            "sources": {
                "english": {
                    "primary": [
                        {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
                        {"name": "AI News", "url": "https://www.artificialintelligence-news.com/feed/"},
                        {"name": "MIT News AI", "url": "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"}
                    ]
                },
                "chinese": {
                    "fallback": [
                        {"name": "量子位", "url": "https://www.qbitai.com/feed"}
                    ]
                }
            }
        }

    def fetch_single_rss(self, url, name, max_items=10, timeout=30):
        """获取单个RSS源"""
        try:
            feed = feedparser.parse(url)

            if feed.bozo:
                raise Exception(f"RSS解析错误: {feed.bozo_exception}")

            items = []
            for entry in feed.entries[:max_items]:
                # 解析发布时间
                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6]).isoformat()
                elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                    pub_date = datetime(*entry.updated_parsed[:6]).isoformat()

                # 获取标题
                title = entry.get("title", "").strip()

                # 获取内容
                content = entry.get("description", entry.get("summary", ""))

                # 清理HTML标签
                import re
                content = re.sub(r'<[^>]+>', ' ', content)
                content = re.sub(r'\s+', ' ', content).strip()

                # 限制内容长度
                if len(content) > 500:
                    content = content[:497] + "..."

                # 翻译英文新闻（仅在translate=True时翻译）
                title_zh = title
                content_zh = content
                if self.translate and ("MIT" in name or "AI News" in name):
                    # 翻译标题
                    if hasattr(self, 'translator') and self.translator:
                        title_zh = self.translator.translate(title, "en", "zh")
                        if not title_zh:
                            title_zh = title

                        # 翻译内容（限制长度避免超时）
                        content_zh = self.translator.translate(content, "en", "zh")
                        if not content_zh:
                            content_zh = content

                items.append({
                    "title": title_zh if self.translate else title,  # 如果translate=True则使用翻译版
                    "title_en": title,  # 保留英文原标题
                    "content": content_zh if self.translate else content,  # 如果translate=True则使用翻译版
                    "content_en": content,  # 保留英文原内容
                    "link": entry.get("link", ""),
                    "source": name,
                    "language": "en" if "MIT" in name or "AI News" in name else "zh",
                    "pub_date": pub_date,
                    "type": "news",
                    "translated": bool(title_zh != title or content_zh != content) if self.translate else False
                })

            print(f"✓ {name}: 获取 {len(items)} 条新闻", file=sys.stderr)
            return items

        except Exception as e:
            print(f"✗ {name}: 获取失败 - {str(e)}", file=sys.stderr)
            return []

    def fetch_english(self):
        """获取英文新闻源"""
        print("\n获取英文新闻源...", file=sys.stderr)

        english_sources = self.sources.get("sources", {}).get("english", {}).get("primary", [])

        all_news = []
        for source in english_sources:
            name = source["name"]
            url = source["url"]
            max_items = source.get("max_items", 10)
            if not isinstance(max_items, int):
                max_items = int(max_items) if str(max_items).isdigit() else 10

            news_items = self.fetch_single_rss(url, name, max_items)
            all_news.extend(news_items)

        # 按发布时间排序
        all_news.sort(key=lambda x: x.get("pub_date", ""), reverse=True)

        print(f"英文源总计: {len(all_news)} 条", file=sys.stderr)
        return all_news

    def fetch_chinese_fallback(self):
        """获取中文备用源（量子位RSS）"""
        print("\n获取中文备用源...", file=sys.stderr)

        chinese_sources = self.sources.get("sources", {}).get("chinese", {}).get("fallback", [])

        all_news = []
        for source in chinese_sources:
            name = source["name"]
            url = source["url"]
            max_items = source.get("max_items", 20)
            if not isinstance(max_items, int):
                max_items = int(max_items) if str(max_items).isdigit() else 20

            news_items = self.fetch_single_rss(url, name, max_items)
            all_news.extend(news_items)

        print(f"中文备用源总计: {len(all_news)} 条", file=sys.stderr)
        return all_news

    def balance_news(self, english_news, chinese_news, chinese_ratio=0.65):
        """
        按照配比控制新闻数量

        Args:
            english_news: 英文新闻列表
            chinese_news: 中文新闻列表
            chinese_ratio: 中文占比 (0.65 = 65%)
        """
        chinese_ratio = min(chinese_ratio, 0.85)  # 最多85%
        english_ratio = 1.0 - chinese_ratio

        # 计算总目标数量
        total_possible = len(chinese_news) + len(english_news)
        if total_possible == 0:
            return []

        # 按配比计算目标数量
        max_chinese = int(total_possible * chinese_ratio)
        max_english = int(total_possible * english_ratio)

        # 限制实际数量
        final_chinese = chinese_news[:max_chinese]
        final_english = english_news[:max_english]

        print(f"\n配比控制: 中文 {len(final_chinese)} 条 ({int(len(final_chinese)/(len(final_chinese)+len(final_english))*100) if len(final_chinese)+len(final_english)>0 else 0}%), 英文 {len(final_english)} 条", file=sys.stderr)

        return final_chinese + final_english


def main():
    """主函数 - 命令行调用"""

    if len(sys.argv) < 2:
        print("用法:", file=sys.stderr)
        print("  python3 rss_fetcher.py english                 # 获取英文源（带翻译）", file=sys.stderr)
        print("  python3 rss_fetcher.py english --no-translation # 获取英文源（不翻译）", file=sys.stderr)
        print("  python3 rss_fetcher.py chinese                 # 获取中文备用源", file=sys.stderr)
        print("  python3 rss_fetcher.py --test                  # 测试所有源", file=sys.stderr)
        sys.exit(1)

    command = sys.argv[1]

    # 检查是否启用翻译
    enable_translation = "--no-translation" not in sys.argv and "--no-tran" not in sys.argv

    fetcher = RSSFetcher(translate=enable_translation)

    if command == "english":
        news = fetcher.fetch_english()
        print(json.dumps(news, ensure_ascii=False, indent=2))

    elif command == "chinese":
        news = fetcher.fetch_chinese_fallback()
        print(json.dumps(news, ensure_ascii=False, indent=2))

    elif command == "--test":
        print("测试所有RSS源...", file=sys.stderr)

        # 测试英文源
        print("\n=== 英文源 ===", file=sys.stderr)
        english_sources = [
            {"name": "MIT Technology Review", "url": "https://www.technologyreview.com/feed/"},
            {"name": "AI News", "url": "https://www.artificialintelligence-news.com/feed/"},
            {"name": "MIT News AI", "url": "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"}
        ]

        for source in english_sources:
            fetcher.fetch_single_rss(source["url"], source["name"], max_items=3)

        # 测试中文源
        print("\n=== 中文源 ===", file=sys.stderr)
        chinese_sources = [
            {"name": "量子位", "url": "https://www.qbitai.com/feed"}
        ]

        for source in chinese_sources:
            fetcher.fetch_single_rss(source["url"], source["name"], max_items=3)

        print("\n✓ 测试完成", file=sys.stderr)

    else:
        print(f"未知命令: {command}", file=sys.stderr)
        print("可用命令: english [--no-translation], chinese, --test", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
