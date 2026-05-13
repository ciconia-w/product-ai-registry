---
name: pm-batch-ops
version: 0.1.0
description: 通过 company-pm OpenCLI 插件执行基于配置文件的多步骤串行操作，并优先使用 preview 模式
---

# Company PM Batch Ops

适用场景：

- 需要按步骤串联多个 company-pm 命令
- 需要使用 `$prev...` 引用前一步输出
- 需要简单跳过条件和重试设置

## 对应命令

- `opencli company-pm batch --file /path/to/config.json -f json`
- `opencli company-pm batch --file /path/to/config.json --apply true -f json`

## 默认顺序

1. 先准备 batch JSON
2. 先 preview
3. 必要时再 `--apply true`

## 前置条件

- `addon:opencli`
- `addon:pm-opencli-plugin`
- 如果 batch 内含浏览器命令，还需要 `addon:opencli-browser-bridge`
- `reference:pm-batch-config-example`

## 阻断条件

- batch 文件不存在
- batch 配置不合法
- batch 中包含写命令但用户未明确允许
- batch 中包含浏览器命令但登录态或 browser bridge 不可用
