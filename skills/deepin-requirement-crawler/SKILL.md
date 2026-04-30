---
name: deepin-requirement-crawler
description: 从 Deepin 论坛、企业邮箱、产品需求反馈系统采集需求数据，自动分析评估优先级，生成 Markdown 和 Excel 两种格式的标准化需求清单。集成 requirement-analyzer 和 requirement-prioritizer，支持两种调用模式（AI skill 独立脚本）。触发词：把P0优先级处理了、分析社区需求、筛选高优先级需求、从论坛收集用户反馈、处理uosai相关需求。
---

# 工作流程

1. 采集需求 → 2. 分析 → 3. 评分 → 4. 生成清单

## 采集需求

直接用户：需要采集哪些数据源（论坛/邮箱/产品系统）？最近多少天的数据？

然后调用相应脚本：

| 数据源 | 脚本命令 |
|--------|----------|
| 论坛 | `python3 scripts/fetch-forum-requirements.py recent <天数>` |
| 邮箱 | `python3 scripts/fetch-email-requirements.py` |
| 产品系统 | `python3 scripts/fetch-product-requirements.py recent <天数>` |

命令参数详见 scripts/commands.md

## 分析与评分

⚠️ **重要**：必须使用 AI 推断方式，真正调用 `requirement-analyzer` 和 `requirement-prioritizer` skills。

调用方式：
```bash
# 1. 分析需求
/requirement-analyzer <合并后的需求.json>

# 2. 评估优先级
/requirement-prioritizer <分析后的需求.json>
```

AI 分析会自动填充所有必需字段：
- 需求类型、模块、复杂度
- 用户角色、使用场景、期望行为
- 产品名称、操作系统、系统版本、硬件架构

## 生成清单

```bash
python3 scripts/generate-excel.py <输入.json> [产品名] [输出目录]
```

产品名可选，默认自动推断或使用"deepin"

输出位置：
- 过程数据：output/temp/ （中间文件）
- 结果数据：output/results/ （最终清单）

生成文件：
- Excel: <产品名>-需求清单-YYYYMMDD.xlsx
- CSV: <产品名>-需求清单-YYYYMMDD.csv

Excel 字段映射见 scripts/field-mapping.md

## 进度去重

- 论坛: scripts/forum_progress.json
- 邮箱: scripts/email_progress.json
- 产品系统: scripts/product_progress.json

进度清空可重新采集。
