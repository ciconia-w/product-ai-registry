# 子批次输出契约

并行分析时，每个子 agent 必须遵守同一份输出契约。

## 输入

- 一个 `batch_XX.json`

## 输出

每个批次固定产出两个文件：

1. `batch_XX_delivery.json`
2. `batch_XX_report.md`

## `batch_XX_delivery.json` 结构

必须是 JSON 数组，数组中的每一项至少包含：

- `来源`
- `发布时间`
- `标题`
- `模块`
- `分类`
- `作者`
- `点赞`
- `浏览`
- `回复数`
- `热度`
- `链接`
- `内容`
- `AI需求分析`
- `_source`
- `_source_label`
- `_record_id`
- `_raw_content`
- `_raw_title`

## `batch_XX_report.md` 结构

允许是局部报告，但建议保留以下块：

- `## 需求清单`
- `## 需求穿透分析`
- `## 当前产品能力判断`
- `## 需求聚类`
- `## 优先级与产品建议`

## 约束

- 不允许子 agent 直接写飞书。
- 不允许子 agent 跳过原始文本保留。
- 不允许子 agent 私自修改批次边界。
- 最终汇总、翻译、补链接和写飞书由主 agent 完成。
