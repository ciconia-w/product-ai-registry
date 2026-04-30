#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求分析独立脚本
调用 requirement-analyzer skill 对需求进行分析
"""

import sys
import json
import subprocess
import os
from datetime import datetime

# Skill路径
SKILL_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "SKILL.md")

def read_input(input_file):
    """读取输入JSON文件"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                # 如果是单个字典，包装成列表
                data = [data]
            return data
    except Exception as e:
        print(f"读取输入文件失败: {e}", file=sys.stderr)
        sys.exit(1)

def call_claude_skill(requirements):
    """
    调用Claude CLI执行skill

    构造提示词，让Claude使用requirement-analyzer分析需求
    """
    # 将需求数据转为紧凑的JSON
    prompt_data = json.dumps(requirements, ensure_ascii=False, indent=2)

    prompt = f"""请使用 requirement-analyzer skill 分析以下用户需求：

{prompt_data}

请直接输出分析结果的JSON，不要有其他内容。"""

    try:
        # 调用claude CLI
        result = subprocess.run(
            ['claude', '-p', prompt],
            capture_output=True,
            text=True,
            check=True,
            timeout=120
        )
        return result.stdout
    except subprocess.TimeoutExpired:
        print("调用Claude超时", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"调用Claude失败: {e}", file=sys.stderr)
        print(f"stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)

def parse_output(claude_output):
    """解析Claude的输出，提取JSON"""
    # 尝试找到JSON部分
    import re
    json_pattern = r'\{[\s\S]*\}'
    matches = re.findall(json_pattern, claude_output)

    for match in matches:
        try:
            # 尝试找到最外层的JSON对象
            # 跳过数组和嵌套对象
            if match.count('{') == match.count('}'):
                data = json.loads(match)
                return data
        except:
            continue

    # 如果没找到，尝试直接解析整个输出
    try:
        return json.loads(claude_output)
    except:
        pass

    # 还是没找到，返回解析失败
    return None

def write_output(data, output_file):
    """写入输出文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_file}")
    except Exception as e:
        print(f"写入输出文件失败: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    if len(sys.argv) < 3:
        print("用法: python3 analyze.py <input.json> <output.json>")
        print("\n示例:")
        print("  python3 analyze.py requirements.json analyzed.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # 检查输入文件
    if not os.path.exists(input_file):
        print(f"输入文件不存在: {input_file}", file=sys.stderr)
        sys.exit(1)

    print(f"读取输入文件: {input_file}")
    requirements = read_input(input_file)
    print(f"共 {len(requirements)} 条需求")

    print("调用 requirement-analyzer skill...")
    claude_output = call_claude_skill(requirements)

    print("解析输出...")
    result = parse_output(claude_output)

    if result is None:
        print("无法解析输出内容", file=sys.stderr)
        print("原始输出:", claude_output[:500], file=sys.stderr)
        sys.exit(1)

    write_output(result, output_file)

    # 打印摘要
    if 'total_count' in result:
        print(f"\n分析完成，共 {result['total_count']} 条需求")

if __name__ == "__main__":
    main()
