# Local Reusable Assets Curated Reference

这是一个**脱敏后的参考工作簿**，用于记录某台本地开发机上已经沉淀下来的可复用 AI 资源。

它不是一个可安装 capability，也不是团队的统一事实源。
它的用途是：

- 给团队展示“本地已经积累了哪些可复用资源”
- 为后续把这些资源整理成 `skill / script / wrapper / pack / reference` 提供素材
- 在不泄露账号、密码、收件人、主机路径等敏感信息的前提下保留分类和判断结果

## Included File

- `local_reusable_assets_must_keep_curated_sanitized_20260430.xlsx`

## Sanitization Rules

工作簿在入库前做了以下脱敏：

- 真实邮箱地址替换为占位内容
- 授权码、密码、代理主机等敏感字符串替换为 `<redacted>`
- 绝对本机路径替换为通用占位，例如：
  - `~/.claude/skills/...`
  - `~/.codex/skills/...`
  - `~/scripts/...`
  - `<local-bundle>/...`
  - `<registry-source>/...`
  - `<global-node-bin>/...`
  - `<global-node-modules>/...`

## Interpretation

这份表更接近“整理工作底稿”，而不是最终产品能力目录。

其中的条目主要分为几类：

- AI 日报与数据抓取
- 需求收集、分析、优先级评估、用户故事输出
- 邮件发送与邮件处理
- Claude Code / Codex 的基础 skills 与本地能力入口

## Non-goals

- 不承诺这些条目都已经规范化
- 不承诺这些条目都能被当前 Agent 自动安装
- 不承诺工作簿中的路径可直接在其他机器上复现

如果后续要正式纳入 registry，应以 canonical `skill / script / wrapper / reference` 形式重新建模，而不是直接把工作簿当成安装输入。
