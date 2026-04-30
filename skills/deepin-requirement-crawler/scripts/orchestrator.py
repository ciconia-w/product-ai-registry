#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
需求流程协调脚本
支持调用Skill或独立脚本进行分析和优先级评估
"""

import sys
import json
import subprocess
import os
import argparse
from pathlib import Path

# 仓库内相对路径，避免绑定到某台机器的 ~/.claude
BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR.parent.parent
ANALYZER_SCRIPT = SKILLS_DIR / "requirement-analyzer" / "scripts" / "analyze.py"
PRIORITIZER_SCRIPT = SKILLS_DIR / "requirement-prioritizer" / "scripts" / "prioritize.py"

def read_input(input_file):
    """读取输入JSON文件"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = [data]
            return data
    except Exception as e:
        print(f"读取输入文件失败: {e}", file=sys.stderr)
        sys.exit(1)

def write_output(data, output_file):
    """写入输出文件"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到: {output_file}")
    except Exception as e:
        print(f"写入输出文件失败: {e}", file=sys.stderr)
        sys.exit(1)

def analyze_with_script(input_file, output_file):
    """使用独立脚本进行分析"""
    print(f"使用分析脚本: {ANALYZER_SCRIPT}")
    try:
        subprocess.run(["python3", str(ANALYZER_SCRIPT), input_file, output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"分析脚本执行失败: {e}", file=sys.stderr)
        sys.exit(1)

def analyze_with_skill(requirements):
    """使用Skill进行分析（在当前会话中直接调用）"""
    print("使用 requirement-analyzer skill 进行分析...")
    # 这里需要通过Skill工具调用，暂时返回None，说明需要手动调用
    print("请在会话中使用 requirement-analyzer skill 进行分析", file=sys.stderr)
    return None

def prioritize_with_script(input_file, output_file):
    """使用独立脚本进行优先级评估"""
    print(f"使用评分脚本: {PRIORITIZER_SCRIPT}")
    try:
        subprocess.run(["python3", str(PRIORITIZER_SCRIPT), input_file, output_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"评分脚本执行失败: {e}", file=sys.stderr)
        sys.exit(1)

def prioritize_with_skill(requirements):
    """使用Skill进行优先级评估（在当前会话中直接调用）"""
    print("使用 requirement-prioritizer skill 进行评估...")
    # 这里需要通过Skill工具调用，暂时返回None，说明需要手动调用
    print("请在会话中使用 requirement-prioritizer skill 进行评估", file=sys.stderr)
    return None

def main():
    parser = argparse.ArgumentParser(description='需求流程协调工具')
    parser.add_argument('input', help='输入JSON文件路径')
    parser.add_argument('--method', choices=['skill', 'script'], default='skill',
                       help='调用方式：skill（AI推断）或 script（独立脚本）')
    parser.add_argument('--step', choices=['analyze', 'prioritize', 'full'], default='full',
                       help='执行步骤：analyze（分析）、prioritize（评分）、full（完整流程）')
    parser.add_argument('--output', help='输出文件路径（默认自动生成）')

    args = parser.parse_args()

    # 检查输入文件
    if not os.path.exists(args.input):
        print(f"输入文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    requirements = read_input(args.input)
    print(f"共 {len(requirements)} 条需求")

    # 生成输出文件路径
    input_base = os.path.splitext(os.path.basename(args.input))[0]
    output_dir = os.path.dirname(args.output) if args.output else os.path.dirname(args.input)

    if args.step in ['analyze', 'full']:
        anal_output = args.output if args.step == 'analyze' else os.path.join(output_dir, f"{input_base}_analyzed.json")
        print(f"\n=== 需求分析 ===")
        if args.method == 'script':
            analyze_with_script(args.input, anal_output)
        else:
            # skill模式: 需要在会话中手动调用
            print(f"请手动调用 requirement-analyzer skill，输入文件: {args.input}")
            anal_output = None

    if args.step in ['prioritize', 'full']:
        prior_input = anal_output if anal_output and args.step == 'full' else args.input
        prior_output = args.output if args.step == 'prioritize' else os.path.join(output_dir, f"{input_base}_prioritized.json")
        if not prior_input:
            print("未找到分析结果，无法进行优先级评估", file=sys.stderr)
            sys.exit(1)
        print(f"\n=== 优先级评估 ===")
        if args.method == 'script':
            prioritize_with_script(prior_input, prior_output)
        else:
            # skill模式: 需要在会话中手动调用
            print(f"请手动调用 requirement-prioritizer skill，输入文件: {prior_input}")

if __name__ == "__main__":
    main()
