---
name: pms-read
version: 0.1.0
description: 通过 company-pm OpenCLI 插件复用浏览器登录态，读取 PMS或禅道中的产品、项目、任务与详情信息
---

# Company PM PMS Read

适用场景：

- 查看当前账号的产品、项目、任务、Bug、Story
- 浏览产品页、项目页、构建页、团队页、动态页
- 先确认登录态和权限范围

## 先检查

```bash
opencli company-pm status -f json
```

## 常用命令

- `opencli company-pm list-products -f json`
- `opencli company-pm list-projects -f json`
- `opencli company-pm my-tasks -f json`

## 前置条件

- `addon:opencli`
- `addon:opencli-browser-bridge`
- `addon:pm-opencli-plugin`
- 浏览器 profile 已经登录 `https://pms.uniontech.com`

## 阻断条件

- browser bridge 不可用
- 浏览器未登录
- 页面权限不足
