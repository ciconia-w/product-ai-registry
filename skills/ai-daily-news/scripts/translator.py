#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译工具 - 使用MyMemory免费翻译API
"""

import requests
import json
import sys
import time
from typing import Optional

class Translator:
    """翻译器"""

    def __init__(self):
        self.api_url = "http://api.mymemory.translated.net/get"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.last_request_time = 0
        self.min_request_interval = 1.0  # 最小请求间隔（秒）

    def translate(self, text: str, source: str = "en", target: str = "zh-CN") -> Optional[str]:
        """
        翻译文本

        Args:
            text: 要翻译的文本
            source: 源语言 (en, zh等)
            target: 目标语言 (en, zh等)

        Returns:
            翻译后的文本，失败返回None
        """
        try:
            # 检查输入
            if not text or not text.strip():
                return None

            # 限制长度
            if len(text) > 500:
                text = text[:500]

            # 速率限制：确保两次请求间隔至少1秒
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last_request)

            # 构建参数
            params = {
                'q': text,
                'langpair': f'{source}|{target}'
            }

            # 发送请求
            response = requests.get(
                self.api_url,
                params=params,
                headers=self.headers,
                timeout=15
            )

            # 更新最后请求时间
            self.last_request_time = time.time()

            # 检查响应状态
            if response.status_code == 429:
                print(f"API速率限制，跳过翻译", file=sys.stderr)
                return None

            response.raise_for_status()

            # 解析响应
            result = response.json()

            # 提取翻译结果
            if result.get('responseStatus') == 200:
                translated_text = result.get('responseData', {}).get('translatedText')
                return translated_text
            else:
                return None

        except requests.exceptions.Timeout:
            print(f"翻译超时", file=sys.stderr)
            return None
        except requests.exceptions.RequestException as e:
            print(f"翻译失败: {str(e)}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"翻译失败: {str(e)}", file=sys.stderr)
            return None

    def translate_batch(self, texts: list, source: str = "en", target: str = "zh-CN") -> list:
        """
        批量翻译

        Args:
            texts: 文本列表
            source: 源语言
            target: 目标语言

        Returns:
            翻译结果列表（失败的元素为None）
        """
        results = []
        for i, text in enumerate(texts, 1):
            print(f"翻译 {i}/{len(texts)}...", file=sys.stderr, end='\r')
            translated = self.translate(text, source, target)
            results.append(translated)
        print(file=sys.stderr)
        return results

    def translate_news_item(self, title: str, content: str, link: str = "") -> dict:
        """
        翻译新闻条目

        Args:
            title: 标题
            content: 内容
            link: 链接

        Returns:
            包含翻译结果的字典
        """
        translated_title = self.translate(title, "en", "zh")
        translated_content = self.translate(content, "en", "zh")

        return {
            "title_zh": translated_title if translated_title else title,
            "title_en": title,
            "content_zh": translated_content if translated_content else content,
            "content_en": content,
            "link": link,
            "translated": bool(translated_title or translated_content)
        }


def main():
    """测试函数"""
    translator = Translator()

    # 测试翻译
    test_texts = [
        "DeepMind launches new AI model",
        "Tech companies invest in AI infrastructure",
        "OpenAI releases GPT-5 features"
    ]

    print("测试翻译功能...", file=sys.stderr)
    print(file=sys.stderr)
    for text in test_texts:
        translated = translator.translate(text, "en", "zh")
        print(f"原文: {text}", file=sys.stderr)
        print(f"译文: {translated}\n", file=sys.stderr)

    print("✓ 测试完成", file=sys.stderr)


if __name__ == "__main__":
    main()
