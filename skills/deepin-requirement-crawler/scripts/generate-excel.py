#!/usr/bin/env python3
# 将需求优先级评估结果转换为 Excel/CSV
# 输入: prioritized_requirements.json
# 输出: xxx-需求清单.xlsx, xxx-需求清单.csv

import json
import pandas as pd
import sys
import os
from datetime import datetime

# 默认输入输出路径
INPUT_FILE = "prioritized_requirements.json"
OUTPUT_DIR = "output/results"  # 结果数据存放在 output/results/

def map_requirement_to_row(req):
    """
    将单个需求映射为 Excel 行数据
    基于 product_feedback 系统的字段映射
    """
    analysis = req.get("analysis", {})
    priority = req.get("priority", {})
    source_info = req.get("source_info", {})

    # 计算优先级等级
    score = priority.get("score", 0)
    if score >= 85:
        level = "P0"
    elif score >= 70:
        level = "P1"
    elif score >= 50:
        level = "P2"
    elif score >= 30:
        level = "P3"
    else:
        level = "P4"

    # 拼装用户故事
    user_role = analysis.get("user_role", "")
    scenario = analysis.get("scenario", "")
    expected_behavior = analysis.get("expected_behavior", "")
    user_story = f"作为{user_role}，{scenario}，我希望{expected_behavior}" if all([user_role, scenario, expected_behavior]) else ""

    # 验收标准（基于 expected_behavior 生成）
    acceptance_criteria = f"①{expected_behavior}" if expected_behavior else ""

    # 产品环境信息（都有就写，没有就空）
    product_name = analysis.get("product_name", "")
    os = analysis.get("os", "")
    os_version = analysis.get("os_version", "")
    hardware_arch = analysis.get("hardware_arch", "")

    return {
        "类别": analysis.get("type", ""),
        "所属产品": product_name,
        "所属模块": analysis.get("module", ""),
        "优先级": level,
        "评分": score,
        "需求标题": req.get("title", ""),
        "需求描述": req.get("content", ""),
        "用户故事": user_story,
        "验收标准": acceptance_criteria,
        "来源": req.get("source", ""),
        "来源地址": req.get("url", ""),
        "需求分析": analysis.get("complexity", ""),
        "操作系统": os,
        "系统版本": os_version,
        "硬件架构": hardware_arch
    }

def generate_excel(data, output_path):
    """生成 Excel 文件"""
    df = pd.DataFrame(data)

    # 设置列顺序
    column_order = [
        "类别", "所属产品", "所属模块", "优先级", "评分", "需求标题",
        "需求描述", "用户故事", "验收标准", "来源", "来源地址",
        "需求分析", "操作系统", "系统版本", "硬件架构"
    ]
    df = df[column_order]

    # 导出到 Excel
    df.to_excel(output_path, index=False, engine='openpyxl')
    print(f"✓ 生成 Excel: {output_path}")

def generate_csv(data, output_path):
    """生成 CSV 文件"""
    df = pd.DataFrame(data)

    # 设置列顺序
    column_order = [
        "类别", "所属产品", "所属模块", "优先级", "评分", "需求标题",
        "需求描述", "用户故事", "验收标准", "来源", "来源地址",
        "需求分析", "操作系统", "系统版本", "硬件架构"
    ]
    df = df[column_order]

    # 导出到 CSV（UTF-8 BOM 以支持 Excel 中文）
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✓ 生成 CSV: {output_path}")

def main():
    """主函数"""
    # 解析命令行参数
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = INPUT_FILE

    # 产品名称：优先使用命令行参数，否则从数据推断，最后使用默认值
    if len(sys.argv) > 2:
        product_name = sys.argv[2]
    else:
        product_name = None  # 稍后从数据推断

    if len(sys.argv) > 3:
        output_dir = sys.argv[3]
    else:
        output_dir = OUTPUT_DIR

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    # 读取 JSON 输入
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到输入文件 {input_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: {input_file} 不是有效的 JSON 文件")
        sys.exit(1)

    # 处理数据
    if isinstance(data, dict) and "requirements" in data:
        requirements = data["requirements"]
    elif isinstance(data, list):
        requirements = data
    else:
        print(f"错误: 输入数据格式不正确")
        sys.exit(1)

    # 如果没有指定产品名称，尝试从数据推断
    if product_name is None:
        # 尝试从需求中推断产品名称
        product_name = ""  # 推断失败则留空
        for req in requirements[:5]:  # 检查前5条
            title = req.get("title", "")
            content = req.get("content", "")
            text = (title + " " + content).lower()

            if "uosai" in text or "uos-ai" in text or "uos ai" in text:
                product_name = "uosai"
                break
            elif "deepin" in text:
                product_name = "deepin"
                break
            elif "uos" in text:
                product_name = "uos"
                break

        # 如果推断失败，使用"需求清单"作为文件名
        if not product_name:
            product_name = "需求清单"

    # 转换为行数据
    rows = []
    for req in requirements:
        rows.append(map_requirement_to_row(req))

    # 生成文件名（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d")
    base_name = f"{product_name}-需求清单-{timestamp}"

    excel_path = os.path.join(output_dir, f"{base_name}.xlsx")
    csv_path = os.path.join(output_dir, f"{base_name}.csv")

    # 生成 Excel 和 CSV
    generate_excel(rows, excel_path)
    generate_csv(rows, csv_path)

    print(f"\n✓ 完成！共处理 {len(rows)} 条需求")

if __name__ == "__main__":
    main()
