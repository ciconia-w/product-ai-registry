# AI Daily News Workflow

资源组成：

- `skill:ai-daily-news`
- `skill:send-email`
- `script:send-email`

## 推荐执行顺序

1. 先运行 `skill:ai-daily-news`，生成日报标题和正文。
2. 再运行 `skill:send-email`，检查 SMTP 条件是否满足。
3. 最后调用 `script:send-email` 完成实际发送。

## 前置条件

- `python3` 可用
- 技能引用的抓取脚本和历史目录可正常访问
- 新闻源在当前网络环境下可访问

必须具备：

- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

## 阻断条件

遇到以下情况时，不应宣称 workflow 已完成：

- 新闻源不可达且没有可用 fallback
- 日报正文未成功生成
- SMTP 环境变量缺失
- 邮箱服务未启用 SMTP
- 授权码 / app password 无效
- `script:send-email` 执行失败

## 完成定义

- 日报正文已生成
- 邮件脚本明确报告发送成功
