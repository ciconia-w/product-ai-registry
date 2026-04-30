#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
arXiv论文获取器
获取最新AI论文，返回Top 3条
"""

import feedparser
import json
import sys
import re
from datetime import datetime, timezone
from pathlib import Path

# 配置
ARXIV_AI_RSS = "http://export.arxiv.org/rss/cs.AI"
MAX_ITEMS = 3  # 只返回Top 3

class ArxivFetcher:
    """arXiv论文获取器"""

    def __init__(self, url=None, max_items=MAX_ITEMS):
        """初始化"""
        self.url = url or ARXIV_AI_RSS
        self.max_items = max_items

    def clean_abstract(self, abstract):
        """清理摘要"""
        # 移除HTML标签
        abstract = re.sub(r'<[^>]+>', ' ', abstract)
        # 移除多余空格
        abstract = re.sub(r'\s+', ' ', abstract).strip()
        # 限制长度
        if len(abstract) > 300:
            abstract = abstract[:297] + "..."
        return abstract

    def extract_authors(self, authors_field):
        """提取作者列表"""
        if not authors_field:
            return "Unknown"

        # feedparser的authors字段可能是列表或字符串
        if isinstance(authors_field, list):
            authors = [a.get("name", "") for a in authors_field if hasattr(a, "get")]
        else:
            authors = str(authors_field).split(",")

        # 只取前3个作者
        if len(authors) > 3:
            return ", ".join(authors[:3]) + " et al."
        return ", ".join(authors)

    def fetch_papers(self):
        """获取arXiv最新论文"""
        try:
            print(f"\n获取arXiv论文: {self.url}", file=sys.stderr)
            feed = feedparser.parse(self.url)

            if feed.bozo:
                raise Exception(f"RSS解析错误: {feed.bozo_exception}")

            papers = []
            count = 0

            for entry in feed.entries:
                # 跳过arXiv元数据文件
                arxiv_id = entry.get("id", "")
                if not arxiv_id or "arxiv.org" not in arxiv_id.lower():
                    continue

                # 提取paper ID: https://arxiv.org/abs/2401.12345 -> 2401.12345
                paper_id_match = re.search(r'/(\d{4}\.\d+)', arxiv_id)
                if not paper_id_match:
                    continue

                paper_id = paper_id_match.group(1)

                # 解析标题
                title = entry.get("title", "").strip()

                # 解析摘要
                abstract = self.clean_abstract(entry.get("description", entry.get("summary", "")))

                # 解析作者
                authors = self.extract_authors(entry.get("authors", []))

                # 解析发布时间
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d")

                # 构建论文信息
                paper = {
                    "arxiv_id": paper_id,
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "link": entry.get("link", ""),
                    "published": published,
                    "type": "paper"
                }

                papers.append(paper)
                count += 1

                # 只取Top 3
                if count >= self.max_items:
                    break

            print(f"✓ 获取 {len(papers)} 篇论文", file=sys.stderr)
            return papers

        except Exception as e:
            print(f"✗ 获取arXiv论文失败: {str(e)}", file=sys.stderr)
            return []

    def format_for_daily(self, paper):
        """格式化为日报中的格式"""
        return (
            f"{paper['arxiv_id']}: {paper['title']}\n"
            f"作者: {paper['authors']}\n"
            f"摘要: {paper['abstract']}\n"
            f"链接: {paper['link']}"
        )


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("测试arXiv获取器...", file=sys.stderr)
        fetcher = ArxivFetcher(max_items=3)
        papers = fetcher.fetch_papers()
        for paper in papers:
            print(f"\n{paper['arxiv_id']}: {paper['title']}")
            print(f"作者: {paper['authors']}")
            print(f"摘要: {paper['abstract']}")
        print("\n✓ 测试完成", file=sys.stderr)
        return

    # 正常获取
    fetcher = ArxivFetcher()
    papers = fetcher.fetch_papers()

    # 输出JSON格式
    output = {
        "papers": papers,
        "count": len(papers),
        "datetime": datetime.now().isoformat()
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
