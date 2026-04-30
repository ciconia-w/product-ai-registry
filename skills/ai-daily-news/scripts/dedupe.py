#!/usr/bin/env python3
"""
AI日报去重工具
用于比对历史日报，去除重复话题
"""

import os
import json
import re
from datetime import datetime, timedelta

# 历史日报存储目录（动态获取）
import pathlib
HISTORY_DIR = str(pathlib.Path(__file__).parent.parent / "history")

# 关键词映射表 - 统一不同表述
KEYWORD_MAP = {
    "grok": ["grok", "grok视频", "grok imagine"],
    "qwen": ["qwen", "qwen3.5", "qwen3", "qwen3.5"],
    "gpt-5": ["gpt-5", "gpt5", "gpt-5.3", "gpt5.3", "codex"],
    "claude": ["claude", "anthropic"],
    "gemini": ["gemini", "谷歌"],
    "nvidia": ["nvidia", "英伟达", "黄仁勋"],
    "广告": ["广告", "ads", "商业化"],
    "蒸馏": ["蒸馏", "distillation", "数据战争"],
    "摩根大通": ["摩根大通", "jpmorgan"],
    "月之暗面": ["月之暗面", "moonshot", "kimi"],
    "宇树": ["宇树", "机器狗", "as2"],
    "阿里": ["阿里", "alibaba", "阿里云"],
    "英伟达营收": ["英伟达营收", "680亿"],
}

def ensure_history_dir():
    """确保历史目录存在"""
    os.makedirs(HISTORY_DIR, exist_ok=True)

def get_history_file(date_str):
    """获取历史文件路径"""
    return os.path.join(HISTORY_DIR, f"{date_str}.json")

def save_daily_news(date_str, news_data):
    """保存当日新闻到历史"""
    ensure_history_dir()
    history_file = get_history_file(date_str)
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    # 清理三天前的历史数据
    cleanup_old_history(keep_days=3)

def cleanup_old_history(keep_days=3):
    """清理三天前的历史数据"""
    if not os.path.exists(HISTORY_DIR):
        return
    today = datetime.now()
    for filename in os.listdir(HISTORY_DIR):
        if not filename.endswith('.json'):
            continue
        date_str = filename.replace('.json', '')
        try:
            file_date = datetime.strptime(date_str, "%Y-%m-%d")
            if (today - file_date).days > keep_days:
                os.remove(os.path.join(HISTORY_DIR, filename))
        except:
            pass

def load_yesterday_news():
    """加载昨日新闻用于比对"""
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    history_file = get_history_file(yesterday_str)

    if os.path.exists(history_file):
        with open(history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def extract_keywords(text):
    """提取文本中的关键词"""
    text = text.lower()
    keywords = set()

    # 添加更多通用关键词
    for key, variants in KEYWORD_MAP.items():
        for variant in variants:
            if variant.lower() in text:
                keywords.add(key)
                break

    # 添加常见实体作为关键词
    entities = ["grok", "qwen", "gpt", "claude", "gemini", "nvidia", "openai", "anthropic",
                "google", "阿里", "英伟达", "摩根", "月之暗面", "宇树", "字节", "meta", "微软"]
    for entity in entities:
        if entity in text:
            keywords.add(entity)

    return keywords

def is_duplicate(title, content, yesterday_news):
    """判断是否为重复新闻"""
    if not yesterday_news:
        return False

    # 核心话题关键词 - 只要有一个相同就是重复
    core_topics = {"grok", "qwen", "gpt", "claude", "gemini", "nvidia", "openai", "anthropic",
                   "谷歌", "阿里", "英伟达", "摩根", "月之暗面", "宇树", "字节", "meta", "微软"}

    # 提取当前新闻关键词
    current_keywords = extract_keywords(title + " " + content)

    # 比对昨日新闻
    for old_item in yesterday_news.get("news", []):
        old_keywords = extract_keywords(old_item.get("title", "") + " " + old_item.get("content", ""))

        # 核心话题有重叠
        current_core = current_keywords & core_topics
        old_core = old_keywords & core_topics
        if current_core & old_core:
            return True

        # 计算关键词重叠 >= 2
        overlap = current_keywords & old_keywords
        if len(overlap) >= 2:
            return True

        # 检查标题相似度 - 共同词 >= 2
        if old_item.get("title") and title:
            old_words = set(re.findall(r'\w+', old_item["title"].lower()))
            new_words = set(re.findall(r'\w+', title.lower()))
            common = old_words & new_words
            if len(common) >= 2:
                return True

    return False

def deduplicate_news(news_list):
    """对新闻列表去重"""
    yesterday_news = load_yesterday_news()

    if not yesterday_news:
        return news_list, []

    deduplicated = []
    duplicates = []

    for item in news_list:
        title = item.get("title", "")
        content = item.get("content", "")

        if is_duplicate(title, content, yesterday_news):
            duplicates.append(item)
        else:
            deduplicated.append(item)

    return deduplicated, duplicates

def main():
    """命令行接口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法:", file=sys.stderr)
        print("  python3 dedupe.py <news.json>        # 对JSON文件去重", file=sys.stderr)
        print("  python3 dedupe.py --test             # 运行测试", file=sys.stderr)
        sys.exit(1)
    
    if sys.argv[1] == "--test":
        # 测试去重功能
        yesterday_data = {
            "date": "2026-02-26",
            "news": [
                {"title": "Grok视频模型登顶盲测榜", "content": "xAI的Grok视频模型在LMSYS盲测竞技场拿下第一"},
                {"title": "英伟达季度营收680亿美元", "content": "英伟达季度营收680亿美元创历史纪录"},
                {"title": "GPT-5.3发布超大窗口", "content": "OpenAI发布GPT-5.3-Codex版本，拥有400,000 token"},
            ]
        }

        today_news = [
            {"title": "Grok视频模型持续霸榜", "content": "xAI的Grok视频模型继续在LMSYS盲测竞技场保持领先"},
            {"title": "GPT-5.3编程能力进化", "content": "OpenAI的GPT-5.3-Codex编程速度提升25%"},
            {"title": "新产品发布", "content": "今日发布全新产品"},
        ]

        deduped, duplicates = deduplicate_news(today_news)

        print("去重后新闻:")
        for item in deduped:
            print(f"  - {item['title']}")
        print("\n重复新闻:")
        for item in duplicates:
            print(f"  - {item['title']}")
        return
    
    # 对JSON文件去重
    news_file = sys.argv[1]
    try:
        with open(news_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        news_list = data.get("news", data) if isinstance(data, dict) else data
        deduped, duplicates = deduplicate_news(news_list)
        
        # 输出去重后的结果
        result = {
            "date": data.get("date", datetime.now().strftime("%Y-%m-%d")) if isinstance(data, dict) else datetime.now().strftime("%Y-%m-%d"),
            "news": deduped,
            "duplicates_count": len(duplicates),
            "kept_count": len(deduped)
        }
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
