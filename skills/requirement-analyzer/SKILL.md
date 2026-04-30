---
name: requirement-analyzer
description: 智能分析用户需求，提取需求类型、模块、复杂度、用户场景等关键信息，为后续优先级评估和产品化提供结构化数据。支持AI推断（推荐）或独立脚本调用。触发词：分析需求、提取需求信息、识别需求类型、分析需求复杂度、从需求文本中提取用户场景。
---

# 需求分析

## 工作流程

输入需求文本 → 分析 → 输出结构化数据

### 分析维度

| 维度 | 说明 |
|------|------|
| type | 需求类型（功能需求/非功能需求/问题反馈/建议优化） |
| module | 涉及模块（优先使用输入数据中的 module 字段，如无则从内容推断或标注"其他"） |
| complexity | 技术复杂度（高/中/低） |
| user_role | 用户角色 |
| scenario | 使用场景 |
| expected_behavior | 期望行为 |
| core_value | 核心价值（一句话概括） |
| product_name/os/os_version/hardware_arch | 产品环境信息 |

详见 references/analysis-dimensions.md

## 输入格式

**JSON列表**（推荐批量）:
```json
[{"title": "...", "content": "...", "likes": 10, "views": 1000}]
```

**纯文本**（单需求）: 直接粘贴描述

## 输出格式

```json
{
  "analyzed_at": "2026-03-23T14:30:00Z",
  "total_count": 1,
  "requirements": [{
    "analysis": {
      "type": "功能需求",
      "module": "文件管理",
      "complexity": "中",
      "user_role": "普通用户",
      "scenario": "在复制大文件时",
      "expected_behavior": "显示详细的复制进度和剩余时间",
      "core_value": "提升文件操作的可预见性和用户体验"
    }
  }]
}
```

## 特殊情况

| 情况 | 处理 |
|------|------|
| 信息不足 | 模块="未知"，复杂度="未知"，core_value标注"建议补充" |
| 描述问题实际是需求 | is_bug=true，is_feature_request=true |
| 多个需求混合 | title添加`[含多个需求]`标记 |

详见 references/special-cases.md
