---
name: pm-opencli
version: 0.1.0
description: 用本地 company-pm OpenCLI 插件处理 PMS或禅道、产品需求反馈平台、BI 导出、畅写或UDoc以及内部 PM 自动化任务
---

# Company PM OpenCLI

适用场景：

- PMS / 禅道
- 产品需求反馈平台
- BI 导出
- 畅写 / UDoc
- `opencli company-pm batch`

## 使用前先检查

1. `opencli company-pm --help -f yaml`
2. PMS / 禅道浏览器命令先跑 `opencli company-pm status -f json`
3. 产品需求反馈平台确认 `COMPANY_PM_APP_KEY` 与 `COMPANY_PM_SIGN`
4. BI 确认账号、密码、keychain 或验证码 fallback

## 默认使用顺序

1. 优先读，不要先写
2. 优先 preview，不要先 apply
3. 多步骤操作优先 `batch --file ...`
4. 写操作只有在用户明确要求时才继续

## 子 skill 路由

- PMS / 禅道只读：`pms-read`
- PMS / 禅道写入：`pms-write-guarded`
- 产品反馈读：`pm-requirement-collection`
- 产品反馈写：`worksheet-write-guarded`
- BI：`bi-export`
- batch：`pm-batch-ops`
- 畅写 / UDoc：`changxie-ops`

## 阻断条件

- OpenCLI 本体不存在
- company-pm 插件未安装
- browser bridge 不可用但调用了浏览器命令
- 浏览器登录态缺失
- 产品反馈平台凭据缺失
- BI 登录条件不足

## 参考

- 插件仓库：本地 `OPENCLI_PLUGIN_PM_LAB_PATH`
- 详细命令行为：`$OPENCLI_PLUGIN_PM_LAB_PATH/README.md`
- 畅写 / UDoc：`skill:changxie-ops`
