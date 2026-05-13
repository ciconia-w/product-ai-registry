---
name: changxie-ops
version: 0.1.0
description: 用本地插件提供的 opencli changxie 命令面处理畅写或 UDoc 相关操作
---

# Changxie Ops

适用场景：

- 想知道当前 changxie 命令面有哪些能力
- 需要在 objects、files、tags、shares、markdown 之间选入口

## 先检查

```bash
opencli changxie --help -f yaml
```

## 当前命令组

- `opencli changxie objects`
- `opencli changxie files`
- `opencli changxie tags`
- `opencli changxie shares`
- `opencli changxie markdown`

## 子 skill 路由

- `changxie-objects`
- `changxie-files`
- `changxie-tags`
- `changxie-shares`
- `changxie-markdown`

## 前置条件

- `addon:opencli`
- `addon:pm-opencli-plugin`
- `addon:opencli-browser-bridge`
- 已登录 `https://udoc.uniontech.com`
