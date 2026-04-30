#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deepin 论坛需求提取脚本 - n8n API 版
提取最近N天的论坛帖子，输出 JSON 给 skill 处理
支持进度记录，避免重复爬取
"""

import requests
import json
import os
from datetime import datetime, timedelta
import time

# 进度文件路径
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "forum_progress.json")

# n8n API 配置
API_BASE = "https://n8n.cicd.getdeepin.org/webhook/bbs/thread"

def load_progress():
    """加载已处理的帖子 ID 列表"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f).get('processed_ids', []))
        except:
            pass
    return set()

def save_progress(processed_ids):
    """保存已处理的帖子 ID"""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'processed_ids': list(processed_ids), 'last_updated': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

def fetch_posts(start_ts, end_ts, offset=0, limit=10, hot_value=50):
    """
    获取论坛帖子列表
    Args:
        start_ts/ end_ts: 闭区间时间戳 (秒)
        offset: 偏移量，用于翻页
        limit: 每页数量
        hot_value: 热度筛选，只返回大于这个热度的帖子
    Returns:
        dict: API 响应
    """
    url = f"{API_BASE}?startTs={start_ts}&endTs={end_ts}&offset={offset}&limit={limit}&hot_value={hot_value}"
    try:
        response = requests.get(url, timeout=30)
        result = response.json()
        # 检查返回格式
        if isinstance(result, dict) and 'data' in result:
            return result['data']
        return result
    except Exception as e:
        print(f"API 请求失败: {e}")
        return None

def fetch_post_detail(thread_id):
    """
    获取单个帖子详情和回复
    Args:
        thread_id: 帖子 ID
    Returns:
        dict: 帖子详情数据
    """
    url = f"https://n8n.cicd.getdeepin.org/webhook/bbs/post?thread_id={thread_id}"
    try:
        response = requests.get(url, timeout=30)
        return response.json()
    except Exception as e:
        print(f"获取帖子详情失败: {e}")
        return None

def format_post(post_data):
    """
    转换为统一 JSON 格式
    """
    return {
        "title": post_data.get("title", ""),
        "content": post_data.get("content", ""),
        "url": post_data.get("url", f"https://bbs.deepin.org/post/{post_data.get('id', '')}"),
        "author": post_data.get("author", ""),
        "publish_time": post_data.get("created_at", ""),
        "category": post_data.get("category", ""),
        "likes": post_data.get("likes", 0),
        "views": post_data.get("views", 0),
        "source": "forum",
        "post_id": post_data.get("id", "")
    }

def main(days=30, max_count=50, only_new=True, hot_value=50):
    """
    主函数
    Args:
        days: 获取最近多少天
        max_count: 最多获取多少条
        only_new: 只获取未处理的帖子
        hot_value: 热度筛选，只返回大于这个热度的帖子
    Returns:
        list: 需求数据列表
    """
    processed_ids = load_progress()

    # 计算时间范围（秒时间戳）
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    start_ts = int(start_time.timestamp())
    end_ts = int(end_time.timestamp())

    print(f"获取最近 {days} 天的帖子 ({start_time.strftime('%Y-%m-%d')} ~ {end_time.strftime('%Y-%m-%d')})")
    print(f"已处理帖子数: {len(processed_ids)}")

    all_requirements = []
    newly_processed = []
    offset = 0
    limit = 50

    # 分页获取帖子
    while len(all_requirements) < max_count:
        print(f"获取第 {offset // limit + 1} 页...")
        result = fetch_posts(start_ts, end_ts, offset=offset, limit=limit, hot_value=hot_value)

        if not result or not isinstance(result, list) or len(result) == 0:
            print(f"获取完成或无更多数据")
            break

        for post in result:
            post_id = post.get("id")
            if not post_id:
                continue

            # 跳过已处理的
            if only_new and str(post_id) in processed_ids:
                continue

            # 格式化帖子数据
            req = {
                "title": post.get("subject", ""),
                "content": "",  # 需要调用详情接口获取
                "url": f"https://bbs.deepin.org/post/{post_id}",
                "author": "",
                "publish_time": post.get("created_at", ""),
                "category": "论坛",
                "likes": post.get("like_cnt", 0),
                "views": post.get("views_cnt", 0),
                "source": "forum",
                "post_id": str(post_id),
                "hot_value": post.get("hot_value", 0)
            }

            all_requirements.append(req)
            newly_processed.append(str(post_id))

            if len(all_requirements) >= max_count:
                break

        offset += limit

    # 保存进度
    if newly_processed:
        processed_ids.update(newly_processed)
        save_progress(processed_ids)
        print(f"已保存 {len(newly_processed)} 条新记录")

    print(f"本次获取 {len(all_requirements)} 条需求")
    return all_requirements

if __name__ == "__main__":
    import sys

    # 解析命令行参数
    days = 30
    max_count = 50
    reset = False
    save_to_file = '--save' in sys.argv
    output_file = None

    # 检查 --output 参数
    for i, arg in enumerate(sys.argv):
        if arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            break

    if len(sys.argv) > 1:
        if sys.argv[1] == "recent":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            max_count = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        elif sys.argv[1] == "--reset":
            reset = True
        elif sys.argv[1] not in ['--save', '--output']:
            days = int(sys.argv[1])
            if len(sys.argv) > 2:
                max_count = int(sys.argv[2])

    # 重置进度
    if reset:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print("进度已清空")
        requirements = main(days=days, max_count=max_count, only_new=False)
    else:
        # 只爬取新的
        requirements = main(days=days, max_count=max_count, only_new=True)

    # 保存到文件或打印
    if output_file or save_to_file:
        if not output_file:
            # 生成默认文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f'requirements_forum_{timestamp}.json')

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(requirements, f, ensure_ascii=False, indent=2)
        print(f"✓ 已保存 {len(requirements)} 条需求到: {output_file}")
    else:
        print(json.dumps(requirements, ensure_ascii=False, indent=2))
