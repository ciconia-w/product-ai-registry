---
name: pms-write-guarded
version: 0.1.0
description: 通过 company-pm OpenCLI 插件在 preview-first 与显式放行前提下执行 PMS或禅道写操作
---

# Company PM PMS Write Guarded

适用场景：

- 预览或创建产品
- 预览或创建任务
- 预览或创建需求 Story

## 默认规则

所有写操作先 preview。

只有同时满足下面两点，才允许真正提交：

- 命令里有 `--apply true`
- 环境里有 `COMPANY_PM_ALLOW_WRITE=1`

## 常用命令

- `opencli company-pm create-product -f json`
- `opencli company-pm create-task <project-id> ... -f json`
- `opencli company-pm create-story <product-id> ... -f json`

## 前置条件

- `addon:opencli`
- `addon:opencli-browser-bridge`
- `addon:pm-opencli-plugin`
- 浏览器 profile 已登录 PMS

## 阻断条件

- 用户没有明确要求写入
- 缺少 `--apply true`
- 缺少 `COMPANY_PM_ALLOW_WRITE=1`
- 页面权限不足
