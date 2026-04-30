#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
翻译工具 - 使用联众科技AI API进行翻译
"""

import requests
import json
import sys
import time
from typing import Optional

class UniontechTranslator:
    """联众科技翻译器"""

    def __init__(self, api_key: str):
        """
        初始化翻译器

        Args:
            api_key: 联众科技API密钥
        """
        self.api_key = api_key
        self.api_url = "https://ai.uniontech.com/api/v1/chat/completions"
        self.model = "glm-4-flash"  # 使用GLM-4-Flash模型（快速翻译）
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 最小请求间隔（秒）

    def translate(self, text: str, source: str = "en", target: str = "zh") -> Optional[str]:
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
            if len(text) > 1000:
                text = text[:1000]

            # 速率限制
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < self.min_request_interval:
                time.sleep(self.min_request_interval - time_since_last_request)

            # 构建翻译提示词
            lang_map = {
                "en": "English",
                "zh": "Chinese"
            }
            source_lang = lang_map.get(source, source)
            target_lang = lang_map.get(target, target)

            prompt = f"Translate {source_lang} to {target_lang}, only output the translation without any explanation: {text}"

            # 构建请求体
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # 低温度以获得更稳定的翻译
                "max_tokens": 2000
            }

            # 发送请求
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
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
            if 'choices' in result and len(result['choices']) > 0:
                translated_text = result['choices'][0]['message']['content'].strip()
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

    def translate_batch(self, texts: list, source: str = "en", target: str = "zh") -> list:
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
    # 使用联众科技API密钥
    API_KEY = "ut-6569884d-d462-4b6d-bfaf-2e9360bf45f7"

    translator = UniontechTranslator(API_KEY)

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
