---
name: pm-requirement-collection
version: 0.1.0
description: 通过 company-pm OpenCLI 插件和独立脚本收集论坛与产品需求反馈平台需求
---

# Company PM Requirement Collection

适用场景：

- 收集论坛需求
- 收集产品需求反馈平台记录
- 聚合多个内部来源形成统一需求列表

## 推荐入口

- 聚合：`opencli company-pm collect-requirements -f json`
- 论坛：`opencli company-pm forum-requirements -f json`
- 产品反馈：`opencli company-pm product-requirements -f json`

## 前置条件

论坛来源：

- 网络可访问

产品反馈平台来源：

- `COMPANY_PM_APP_KEY`
- `COMPANY_PM_SIGN`

## 后续处理

原始结果拿到后，再交给 `requirement-analyzer` 与 `requirement-prioritizer`。

## 阻断条件

- 插件未安装
- 产品反馈平台凭据缺失
- 目标来源不可访问
