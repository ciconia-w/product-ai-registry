#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 requirement-analysis 原始 skill 框架生成结构化分析报告与交付 JSON。
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


def classify_problem(text: str) -> str:
    lowered = text.lower()
    if any(key in text for key in ["打不开", "启动失败", "崩溃", "报错", "异常"]) or "fail" in lowered or "error" in lowered or "crash" in lowered:
        return "兼容性/稳定性"
    if any(key in text for key in ["慢", "卡", "性能", "占用", "流畅"]) or "performance" in lowered:
        return "性能"
    if any(key in text for key in ["入口", "找不到", "步骤", "复杂"]) or "difficult" in lowered:
        return "流程低效/入口不明显"
    if any(key in text for key in ["希望", "建议", "支持", "新增", "增加", "优化"]) or "support" in lowered or "allow" in lowered:
        return "功能缺失/体验优化"
    return "待人工判断"


def infer_user_role(item: dict) -> str:
    text = f"{item.get('title', '')} {item.get('content', '')}"
    if any(key in text for key in ["私有化", "工商银行", "政务", "企业", "招标", "客户"]):
        return "政企客户/交付角色"
    if any(key in text for key in ["arm64", "应用名称", "版本", "启动失败"]):
        return "终端用户/测试反馈者"
    return "普通桌面用户"


def infer_scene(item: dict) -> str:
    text = f"{item.get('title', '')} {item.get('content', '')}"
    if "应用商店" in text or "Flatpak" in text or "安装" in text:
        return "应用安装与软件获取"
    if "桌面" in text or "图标" in text or "任务栏" in text:
        return "桌面交互与视觉体验"
    if "指纹" in text or "生物识别" in text:
        return "安全与身份认证"
    if "启动失败" in text or "兼容" in text:
        return "应用兼容与运行"
    return "日常桌面使用"


def infer_expected_result(item: dict) -> str:
    content = item.get("content", "") or ""
    for marker in ["【产品期望】：", "[Desired Product]:", "需求：", "建议："]:
        if marker in content:
            return content.split(marker, 1)[1].strip().splitlines()[0]
    return (item.get("title", "") or content[:60]).strip()


def infer_cluster(item: dict) -> str:
    text = f"{item.get('title', '')} {item.get('content', '')}"
    if any(key in text for key in ["桌面", "图标", "任务栏"]):
        return "桌面与多任务操作效率提升"
    if any(key in text for key in ["应用商店", "安装", "Flatpak", "软件包"]):
        return "应用安装、更新与兼容"
    if any(key in text for key in ["指纹", "生物识别", "证书", "安全"]):
        return "安全、权限与企业管控"
    if any(key in text for key in ["性能", "内核", "toolchain", "GCC", "Treeland"]):
        return "性能、稳定性与资源占用"
    return "其他待归类需求"


def infer_priority(item: dict, problem_type: str) -> str:
    text = f"{item.get('title', '')} {item.get('content', '')}"
    if any(key in text for key in ["工商银行", "私有化", "证书", "客户"]):
        return "P0"
    if problem_type in {"兼容性/稳定性", "性能"}:
        return "P1"
    if problem_type == "功能缺失/体验优化":
        return "P2"
    return "P3"


def psych_portrait(problem_type: str) -> str:
    mapping = {
        "兼容性/稳定性": "初始心理状态偏焦虑和不信任，担心关键任务无法完成；满足后的心理收益是安心感与可控感。",
        "性能": "初始心理状态偏烦躁和低效率感，核心诉求是更流畅和更省时；满足后的收益是效率感与顺手感。",
        "流程低效/入口不明显": "初始心理状态偏困惑，核心问题是认知负担高；满足后的收益是明确感与可预测性。",
        "功能缺失/体验优化": "初始心理状态偏麻烦和将就，核心诉求是少走弯路；满足后的收益是完成任务的成就感。",
    }
    return mapping.get(problem_type, "初始心理状态与触发因素待进一步用户研究确认。")


def capability_judgement(item: dict, problem_type: str) -> str:
    if problem_type == "兼容性/稳定性":
        return "当前更像是已有生态或运行能力未被稳定承接，属于“当前部分支持，但体验不完整”或“兼容性链路待修复”。"
    if problem_type == "性能":
        return "当前通常存在基础能力，但缺少产品化或默认优化，属于“当前部分支持，但体验不完整”。"
    if problem_type == "功能缺失/体验优化":
        return "当前更像是需要新增产品能力或把已有底层能力图形化，默认判断为“当前不支持，需要新增产品能力”。"
    return "当前能力路径待研发和产品进一步核验，先标为“待确认”。"


def tech_feasibility(problem_type: str) -> str:
    if problem_type == "兼容性/稳定性":
        return "技术上可落地，优先沿现有运行链路排查兼容性、依赖版本、打包方式和错误恢复机制。"
    if problem_type == "性能":
        return "技术上可落地，重点在资源调优、配置策略、默认参数和关键路径优化。"
    if problem_type == "功能缺失/体验优化":
        return "技术上通常需要在现有模块上新增 UI、状态管理和策略配置，研发工作量中等。"
    return "技术可行性需结合具体模块复核，当前先给出可研结论，不直接承诺实现。"


def standards_hint(item: dict) -> str:
    text = f"{item.get('title', '')} {item.get('content', '')}"
    if any(key in text for key in ["银行", "证书", "私有化", "政企", "企业"]):
        return "建议重点检查采购与交付约束、信息安全、密码合规、兼容性和可靠性要求。"
    return "暂未识别到强行业标准约束，建议按通用产品要求补充核验。"


def publicity_hint(item: dict) -> str:
    title = item.get("title", "") or "该能力"
    return f"可对外表达为：围绕《{title}》提升系统可用性、效率感与企业可控性。"


def normalize_text(text: str) -> str:
    return re.sub(r"\\s+", " ", text or "").strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成需求分析报告与飞书交付 JSON")
    parser.add_argument("--input", required=True, help="合并后的原始需求 JSON")
    parser.add_argument("--report-output", required=True, help="Markdown 报告输出路径")
    parser.add_argument("--delivery-output", required=True, help="飞书交付 JSON 输出路径")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    raw = json.loads(Path(args.input).read_text(encoding="utf-8"))
    items = raw if isinstance(raw, list) else raw.get("rows", [])

    source_counter = Counter((item.get("source_label") or item.get("source") or "未知") for item in items)
    cluster_counter = Counter()
    analyzed_rows = []
    sections = {
        "requirements": [],
        "penetration": [],
        "capability": [],
        "cluster": [],
        "ownership": [],
        "competition": [],
        "technical": [],
        "standards": [],
        "priority": [],
        "publicity": [],
        "risks": [],
    }

    for index, item in enumerate(items, start=1):
        title = normalize_text(item.get("title", ""))
        content = (item.get("content") or "").strip()
        source = item.get("source_label") or item.get("source") or "未知来源"
        problem_type = classify_problem(f"{title} {content}")
        user_role = infer_user_role(item)
        scene = infer_scene(item)
        expected = infer_expected_result(item)
        cluster = infer_cluster(item)
        cluster_counter[cluster] += 1
        priority = infer_priority(item, problem_type)
        module = item.get("module", "") or "待确认归属"
        summary = f"来源：{source}；问题类型：{problem_type}；建议模块：{module}；优先级建议：{priority}。"

        analyzed_rows.append({
            "来源": source,
            "发布时间": item.get("publish_time", ""),
            "标题": title,
            "模块": item.get("module", ""),
            "分类": item.get("category", ""),
            "作者": item.get("author", ""),
            "点赞": item.get("likes", ""),
            "浏览": item.get("views", ""),
            "回复数": item.get("replies", ""),
            "热度": item.get("hot_value", ""),
            "链接": item.get("url", ""),
            "内容": content,
            "AI需求分析": summary,
            "_source": item.get("source", ""),
            "_source_label": item.get("source_label", ""),
            "_record_id": item.get("record_id", ""),
            "_raw_content": content,
            "_raw_title": title,
        })

        sections["requirements"].append(
            f"- R{index:02d} | 来源：{source} | 用户角色：{user_role} | 场景：{scene} | 当前问题：{problem_type} | 期望结果：{expected}"
        )
        sections["penetration"].append(
            f"### R{index:02d} {title}\n- 表层需求：{expected}\n- 用户真正要完成的任务：在 {scene} 中降低阻碍并稳定完成目标\n- 根本问题：{problem_type}\n- 产品价值判断：{summary}\n- 用户心理侧写：{psych_portrait(problem_type)}"
        )
        sections["capability"].append(f"- R{index:02d}：{capability_judgement(item, problem_type)}")
        sections["cluster"].append(f"- R{index:02d}：{cluster}")
        sections["ownership"].append(f"- R{index:02d}：主责模块 {module}；归属依据：按标题与内容关键词初判；置信度：低")
        sections["competition"].append(f"- R{index:02d}：建议对 Windows/macOS/HarmonyOS/Ubuntu/KylinOS 做同场景核验；当前结论待补证据。")
        sections["technical"].append(f"- R{index:02d}：{tech_feasibility(problem_type)}")
        sections["standards"].append(f"- R{index:02d}：{standards_hint(item)}")
        sections["priority"].append(f"- R{index:02d}：{priority}；建议动作：进入需求池并安排产品/研发复核。")
        sections["publicity"].append(f"- R{index:02d}：{publicity_hint(item)}")
        sections["risks"].append(f"- R{index:02d}：当前主要风险是证据不足与模块归属待确认，需补用户研究或研发核验。")

    report_lines = [
        "# 需求分析报告",
        "",
        "## 1. 分析范围",
        "",
        f"- 样本总数：{len(items)}",
        f"- 数据来源：{', '.join(f'{k}({v})' for k, v in source_counter.items())}",
        "",
        "## 2. 数据来源",
        "",
        *[f"- {k}: {v}" for k, v in source_counter.items()],
        "",
        "## 3. 需求清单",
        "",
        *sections["requirements"],
        "",
        "## 4. 需求穿透分析",
        "",
        *sections["penetration"],
        "",
        "## 5. 当前产品能力判断",
        "",
        *sections["capability"],
        "",
        "## 6. 需求聚类",
        "",
        *[f"- {k}: {v}" for k, v in cluster_counter.items()],
        "",
        *sections["cluster"],
        "",
        "## 7. 产品部模块归属",
        "",
        *sections["ownership"],
        "",
        "## 8. 竞品场景调研",
        "",
        *sections["competition"],
        "",
        "## 9. 技术可行性分析",
        "",
        *sections["technical"],
        "",
        "## 10. 行业标准与采购要求检查",
        "",
        *sections["standards"],
        "",
        "## 11. 优先级与产品建议",
        "",
        *sections["priority"],
        "",
        "## 12. 产品宣传建议",
        "",
        *sections["publicity"],
        "",
        "## 13. 风险、依赖与待确认问题",
        "",
        *sections["risks"],
        "",
        "## 14. 结论摘要",
        "",
        f"- 共分析 {len(items)} 条需求，当前高优先级关注点主要集中在兼容性/稳定性、性能与体验优化。",
        "- 模块归属、竞品与标准结论仍需要基于真实产品资料和研发信息继续补证据。",
    ]

    report_path = Path(args.report_output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    delivery_path = Path(args.delivery_output)
    delivery_path.parent.mkdir(parents=True, exist_ok=True)
    delivery_path.write_text(json.dumps(analyzed_rows, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"report: {report_path}")
    print(f"delivery: {delivery_path}")
    print(f"rows: {len(analyzed_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
