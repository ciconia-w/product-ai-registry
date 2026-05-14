---
name: bi-export
version: 0.1.0
description: 通过 company-pm OpenCLI 插件执行 BI 登录、认证、取数、模板输出与探索型导出
---

# Company PM BI Export

适用场景：

- 导出统信 BI 中的 AI 指标数据
- 选择 `bi-export` 或 `bi-export-v2`
- 选择 `raw / template / custom` 输出

## 链路选择

- 默认优先 `bi-export-v2`
- 需要回退时再用 `bi-export`
- 输出模式细节看 `reference:bi-output-modes`

## 常用命令

- `opencli company-pm bi-export-v2 -f json`
- `opencli company-pm bi-export -f json`

## 前置条件

- `addon:opencli`
- `addon:pm-opencli-plugin`
- `python3`
- BI 账号
- BI 密码或 keychain 中已有可用凭据
- 如果验证码自动识别不稳定，允许手动补输

## 阻断条件

- 插件未安装
- BI 账号不可用
- 密码或 keychain 不可用
- 验证码无法通过自动或手动方式完成
- 目标模板路径缺失
