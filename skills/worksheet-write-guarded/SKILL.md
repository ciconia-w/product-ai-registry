---
name: worksheet-write-guarded
version: 0.1.0
description: 通过 company-pm OpenCLI 插件以 preview-first 方式对产品需求反馈平台执行新增、编辑、删除等受保护写操作
---

# Worksheet Write Guarded

适用场景：

- 新增产品需求反馈平台记录
- 编辑已有记录
- 删除已有记录

## 对应命令

- `opencli company-pm product-add-row -f json`
- `opencli company-pm product-edit-row -f json`
- `opencli company-pm product-delete-row -f json`

## 默认规则

- 所有写操作默认只做 preview
- 只有传入 `--apply true` 才允许真实写入

## 前置条件

- `addon:opencli`
- `addon:pm-opencli-plugin`
- `reference:worksheet-auth-guide`
- `reference:worksheet-product-line-enum`
- `reference:worksheet-product-line-rule-notes`

## 阻断条件

- 缺少 `COMPANY_PM_APP_KEY`
- 缺少 `COMPANY_PM_SIGN`
- 产品线取值不明确
- 用户没有明确要求写入
