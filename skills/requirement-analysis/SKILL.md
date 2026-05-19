---
name: requirement-analysis
description: 当需要执行 Linux 桌面操作系统需求的采集、分析和飞书写入全流程时使用本 skill，适用于 deepin 论坛、产品需求反馈平台、deepin Home 开放接口等多渠道需求场景。该 skill 先检查依赖、授权和飞书表头，再采集、分析、补链接与外语翻译，最后写入飞书文档表格。
---

# 需求采集、分析与飞书写入

这个 skill 的正确顺序只有一条：

1. 先检查
2. 再采集和分析
3. 再写飞书
4. 最后才允许打包、入 registry、产出 showcase

## 入口

- 一条龙：`python3 scripts/run-full-workflow.py ...`
- 分步：先读 `references/workflow.md`

## 检查优先

在任何采集动作之前，先完成：

- `python3 scripts/check-larkcli.py`
- `python3 scripts/check-feishu-access.py`
- `python3 scripts/check-feishu-table-schema.py`

如果缺依赖或 scope，不要继续采集。  
如果表头发生变化，不要继续采集。先修正输出字段，再继续。

## 执行规则

- 论坛、需求反馈平台、deepin Home 的敏感配置通过本地 `~/.config/requirement-analysis/` 或环境变量提供，不写进公开包。
- 飞书链路只使用本地 `lark-cli`。
- 本地 `lark-cli` 授权要复用，不要反复清空；如果缺少新的 scope，需要重新授权，并明确告诉用户这是补权限，不是授权丢失。
- 最终写飞书前，必须经过 `finalize-delivery.py`。
- 如果存在非中文内容，由 agent 在 finalize 阶段把它改成“原文 + 中文翻译”后，再允许写飞书。
- `K/L/M` 三列未补齐时，不允许写飞书。

## 详细说明

- 工作流：见 `references/workflow.md`
- 分析规则：见 `references/analysis-rules.md`
- 采集命令：见 `scripts/commands.md`
- 飞书流程：见 `scripts/feishu_flow.md`
