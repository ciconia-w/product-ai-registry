---
name: triage-issue
description: 为 product-ai-registry 分诊问题，判断是文档问题、资源问题、安装问题、Agent 适配问题，还是应该提交 GitHub issue
---

# Triage Issue

适用场景：

- 不确定该不该给这个仓库提 issue
- 想先做去重，再决定补现有 issue 还是新建 issue

## 默认顺序

1. 先确认问题属于本仓库，而不是外部插件或外部平台本身。
2. 先搜索现有 GitHub issue / PR。
3. 有相同问题就补现有 issue。
4. 没有再整理成新的 GitHub issue。

## 判断规则

适合提到本仓库：

- README / docs / resource guide 写错了
- `manifest.json`、资源目录、命名、引用关系不一致
- `skill` / `script` / `addon` / `reference` 描述或依赖错误
- 某个资源入口设计不合理
- 仓库里的安装/校验/路由逻辑有问题

不应直接当成仓库 issue：

- PMS / 禅道页面本身异常
- BI 页面本身异常
- 产品反馈平台接口本身异常
- changxie / UDoc 服务本身异常
- 外部插件仓库自身 bug，但 registry 只是引用它

这类情况可以：

- 先记录在本仓库 issue 中作为“外部依赖阻断”
- 但标题和描述要明确不是 registry 自身逻辑 bug

## 去重关键词

搜索时优先使用下面几类关键词：

- 资源名
  - `pm-opencli`
  - `pms-read`
  - `bi-export`
  - `changxie-objects`
- 系统名
  - `PMS`
  - `BI`
  - `worksheet`
  - `changxie`
- 错误信号
  - 缺少依赖
  - 登录态
  - manifest
  - 命名不一致
  - README 过期

## 新 issue 最少要写什么

用“范围 + 问题”的形式：

- `README: resource guide link is stale`
- `manifest: skill id and SKILL.md name mismatch`
- `changxie: documented command group missing from registry`
- `worksheet: auth guide misses required env vars`

- 你在做什么
- 你看到的实际结果
- 你期望的结果
- 涉及哪个资源名
- 如果有，贴最小复现命令
- 如果有，贴相关文件路径

## 什么时候不要新建 issue

- 只是想问资源怎么拼，优先看 `docs/06-resource-guide.md`
- 只是想确认 workflow 怎么走，优先看 `docs/workflows/`
- 只是外部平台临时不可用，没有证据表明仓库内容有错

## 输出要求

最终给用户的建议应明确落在下面三种之一：

1. 不需要提 issue，直接看哪个文档/资源
2. 不新建，补到已有 issue
3. 新建 issue，并给出标题和建议内容骨架
