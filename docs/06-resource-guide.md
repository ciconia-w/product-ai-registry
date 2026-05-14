# 资源总览

这份文档是给人看的资源说明。

目标只有一个：

- 让维护者和使用者不用只靠名字猜资源作用
- 知道每个资源大概是干什么的
- 知道应该从哪里开始拼装自己的使用方式

建议先理解四类正式资源：

- `addon`
  - 安装单位。偏工具、插件、运行时。
- `skill`
  - 任务入口。偏“什么时候用、怎么用、先检查什么”。
- `script`
  - 执行动作。偏“真正跑什么命令或脚本”。
- `reference`
  - 只读资料。偏规则、映射、样例、外部知识。

## 怎么看这份表

- 如果你想“装什么”，先看 `addons`
- 如果你想“做什么任务”，先看 `skills`
- 如果你想“底层实际跑什么”，看 `scripts`
- 如果你想“查规则/查映射/查外部参考”，看 `references`
- 如果你想“看整体流程怎么拼”，看 `docs/workflows/`

---

## Addons

### `cc-switch`

Claude Code 相关的环境切换工具。适合需要在不同 provider 或运行环境之间切换的场景。

### `context-mode`

上下文增强层。主要用于上下文压缩、会话延续和路由辅助，不是业务能力本身。

### `gh-cli`

GitHub CLI。很多仓库、Issue、PR、发布相关流程都会依赖它。

### `lark-cli`

飞书 / Lark CLI。适合消息、文档、表格、流程自动化场景。

### `oh-my-claudecode`

Claude Code 的多 Agent 增强层。

### `oh-my-codex`

Codex 的多 Agent 增强层。

### `open-slide`

做演示文稿工作区的工具，输出偏 HTML/PDF 幻灯片。

### `opencli`

底层 CLI 平台。很多浏览器态、插件态、脚本态能力都依赖它。

### `opencli-browser-bridge`

OpenCLI 浏览器桥接层。需要复用登录态、走浏览器命令、抓已登录页面时要装它。

### `pm-opencli-plugin`

本地 OpenCLI 插件。它是 PMS / 禅道、产品反馈平台、BI、畅写 / UDoc 这批能力的统一安装入口。

### `superpowers`

通用增强插件层，适合多个编码 Agent 共用。

---

## Skills

### `ai-daily-news`

生成 AI 日报。负责抓中英文新闻、做整理和生成日报正文。

### `bi-export`

统信 BI 导出入口。负责选择 `bi-export` 或 `bi-export-v2` 链路，以及指导输出模式。

### `changxie-ops`

畅写 / UDoc 总入口。先看它，再决定走 objects、files、tags、shares 还是 markdown。

### `changxie-objects`

创建畅写对象，例如文档、表格、演示稿、Markdown、在线表单。

### `changxie-files`

处理畅写文件和目录，例如建目录、复制、移动、重命名、删除、收藏。

### `changxie-tags`

处理畅写系统标签和文件标签关系。

### `changxie-shares`

处理畅写分享链接生命周期，例如创建、查询、改标签、删除。

### `changxie-markdown`

处理畅写里的 Markdown 文件读写。

### `deepin-dev`

deepin v20 / v25 双版本开发约束。适合桌面应用开发前先看边界。

### `deepin-requirement-crawler`

从论坛、邮箱、产品反馈系统采集需求，并继续做分析和优先级处理。

### `deepin-ui-design`

UOS / Deepin 风格的桌面 UI 设计 skill，偏 QML / DTK。

### `desktop-help-manual-updater`

帮助手册更新 skill。基于真实运行界面、流程和截图做文档更新。

### `linglong-packaging-retrospective`

灵珑打包复盘 skill。记录一次打包过程中的坑点和处理方式。

### `linglong-uab-shortest-path`

灵珑 UAB 打包最短路径 skill。适合已经有现成打包链路的项目。

### `pm-opencli`

本地 PM 插件总入口。适合你只知道“要做 PMS / BI / 产品反馈 / changxie 相关事”，但还没决定细分入口时使用。

### `pm-batch-ops`

批处理入口。基于 JSON 配置做多步骤串行操作。

### `pm-requirement-collection`

需求收集入口。聚合论坛和产品反馈平台的数据。

### `pms-read`

PMS / 禅道只读入口。查产品、项目、任务、Bug、Story、构建、团队、动态。

### `pms-write-guarded`

PMS / 禅道写入口，但默认 preview-first，适合受保护写操作。

### `prd-review`

PRD 评审入口。帮你结构化检查 PRD 的问题和缺口。

### `requirement-analyzer`

需求分析入口。把原始需求拆成结构化字段。

### `requirement-prioritizer`

需求优先级评估入口。把需求打分并映射到优先级。

### `requirement-writer`

需求写作入口。把零散需求整理成 Problem Framing、SRD 或 PRD。

### `send-email`

发信入口。先检查 SMTP 条件，再调用底层发信脚本。

### `spec-to-backlog`

把规格文档拆成 Epic 和 backlog 任务。

### `triage-issue`

Issue 分诊入口。查重复、做分类、给下一步动作建议。

### `uniontech-ai-point-export`

统信 AI 埋点/积分提取入口，依赖真实登录页面。

### `worksheet-write-guarded`

产品反馈平台写入口。默认 preview-first，适合新增、编辑、删除记录。

---

## Scripts

### `bi-auth-login`

BI 登录脚本入口。负责认证或拿到后续取数所需状态。

### `bi-fetch-uniontech-ai`

BI 取数脚本入口。负责抓取和渲染统信 AI 数据。

### `bi-export-week-legacy`

BI 旧导出链。适合保留旧路径或回退使用。

### `check-linglong-retrospective`

检查灵珑复盘文件是否存在、字段是否齐全。

### `forum-demand-crawler`

论坛需求抓取脚本。

### `forum-export-json`

把论坛需求导出成 JSON。

### `rebuild-linglong-uab-shortest-path`

灵珑重建脚本。负责实际打包动作。

### `reset-linglong-builder-env`

灵珑环境重置脚本。负责清理残留状态。

### `send-email`

SMTP 发信脚本。负责真正发送邮件。

### `worksheet-export-json`

把产品反馈平台数据导出成 JSON。

### `write-linglong-retrospective`

把灵珑打包复盘写成 JSON / Markdown。

---

## References

### `agent-skills`

外部工程技能参考库，偏规划、测试、评审、上下文工程。

### `ai-handbook-sdd-overview`

关于 SDD 和 AI 原生交付方法的参考材料。

### `awesome-design-md`

外部 DESIGN.md 参考集合，适合 UI / 设计系统方向。

### `bi-output-modes`

BI 的三种输出模式说明：`raw / template / custom`。

### `browserbase-skills`

浏览器自动化和 UI 测试相关的参考 skill 库。

### `changxie-verified-capability-matrix`

畅写 / UDoc 已验证能力矩阵。先看这份，就知道哪些操作已经做通过。

### `deepin-compat`

deepin v20 / v25 的兼容性和环境约束说明。

### `guizang-ppt-skill`

外部网页 PPT / 演讲 deck skill 参考，适合单文件 HTML slides、瑞士风版式、电子杂志风版式和封面生成场景。

### `khazix-skills`

外部实战型 skill 库，覆盖清理、研究、写作等。

### `linglong-deepin-color-correction-example`

灵珑打包案例参考，偏 `deepin-color-correction` 项目。

### `pm-batch-config-example`

PM batch JSON 配置示例，含 `$prev...` 风格串联说明。

### `pms-browser-login-model`

PMS / 禅道浏览器登录态复用说明。

### `pms-write-safety-policy`

PMS / 禅道写操作的 preview-first 和放行规则说明。

### `rag-anything`

外部多模态 RAG 项目参考。

### `ui-skills-catalog`

UI / 设计工程 skill 目录参考。

### `worksheet-auth-guide`

产品反馈平台凭据与认证说明。

### `worksheet-product-line-enum`

产品反馈平台产品线枚举表。

### `worksheet-product-line-rule-notes`

产品线字段和填表规则说明。

### `worksheet-product-line-uos-ai-mapping`

UOS AI 相关产品线映射表。

---

## Docs

### `docs/01-product-spec.md`

产品规格文档。看这个理解这个 registry 想解决什么问题。

### `docs/02-architecture-design.md`

架构设计文档。看这个理解资源怎么落地到不同 Agent。

### `docs/03-registry-schemas.md`

schema 说明文档。看这个理解 manifest / addon / reference 等结构约束。

### `docs/04-bootstrap-and-helpers.md`

bootstrap 与辅助脚本的设计说明。

### `docs/05-project-scoped-materialization.md`

项目级 materialization 的说明，适合理解资源怎样落到目标仓库。

### `docs/workflows/README.md`

给人看的 workflow 入口说明。

### `docs/workflows/ai-daily-news.md`

日报 workflow 的具体拼装说明。适合想看“多个原子资源怎么串起来”的人。

---

## 常见场景怎么拼

### 1. 想查 PMS / 禅道里的东西

先看：

- `skill:pm-opencli`

再进入：

- `skill:pms-read`

同时要确认：

- `addon:pm-opencli-plugin`
- `addon:opencli-browser-bridge`
- `reference:pms-browser-login-model`

适合的任务：

- 查产品
- 查项目
- 查任务 / Bug / Story
- 查构建、团队、动态

### 2. 想改 PMS / 禅道里的东西

先看：

- `skill:pm-opencli`

再进入：

- `skill:pms-write-guarded`

同时要确认：

- `reference:pms-write-safety-policy`

适合的任务：

- preview 或创建产品
- preview 或创建任务
- preview 或创建 Story

### 3. 想导出 BI 数据

先看：

- `skill:pm-opencli`

再进入：

- `skill:bi-export`

底层会涉及：

- `script:bi-auth-login`
- `script:bi-fetch-uniontech-ai`
- `script:bi-export-week-legacy`
- `reference:bi-output-modes`

适合的任务：

- 导出统信 BI 数据
- 走 `raw / template / custom` 输出模式

### 4. 想收集产品需求反馈平台的数据

先看：

- `skill:pm-opencli`

再进入：

- `skill:pm-requirement-collection`

如果还要写回平台，再看：

- `skill:worksheet-write-guarded`

同时要确认：

- `reference:worksheet-auth-guide`
- `reference:worksheet-product-line-enum`
- `reference:worksheet-product-line-rule-notes`
- `reference:worksheet-product-line-uos-ai-mapping`

适合的任务：

- 抓产品反馈平台记录
- 聚合论坛和产品反馈来源
- 受保护地新增/编辑/删除反馈记录

### 5. 想处理畅写 / UDoc

先看：

- `skill:changxie-ops`

然后按任务进入：

- 建文档 / 表格 / 演示稿 / 表单：`skill:changxie-objects`
- 目录 / 文件操作：`skill:changxie-files`
- 标签：`skill:changxie-tags`
- 分享链接：`skill:changxie-shares`
- Markdown：`skill:changxie-markdown`

同时建议先查：

- `reference:changxie-verified-capability-matrix`

### 6. 想做 AI 日报

先看：

- `docs/workflows/ai-daily-news.md`

实际会用到：

- `skill:ai-daily-news`
- `skill:send-email`
- `script:send-email`

### 7. 想做需求分析和优先级排序

先看：

- `skill:requirement-analyzer`
- `skill:requirement-prioritizer`
- `skill:requirement-writer`

如果原始数据还没收集，再配合：

- `skill:pm-requirement-collection`
- `skill:deepin-requirement-crawler`

### 8. 想处理 deepin / UOS 桌面开发问题

先看：

- `skill:deepin-dev`
- `reference:deepin-compat`

如果是界面设计，再加：

- `skill:deepin-ui-design`
- `reference:ui-skills-catalog`
- `reference:awesome-design-md`

### 9. 想做灵珑打包

先看：

- `skill:linglong-uab-shortest-path`

再配：

- `script:reset-linglong-builder-env`
- `script:rebuild-linglong-uab-shortest-path`
- `skill:linglong-packaging-retrospective`
- `script:write-linglong-retrospective`
- `script:check-linglong-retrospective`
- `reference:linglong-deepin-color-correction-example`

### 10. 想做网页 PPT / 演讲 deck / 封面

先看：

- `reference:guizang-ppt-skill`

如果需要本地 slide 工作区，再配：

- `addon:open-slide`

适合的任务：

- 生成单文件 HTML 横向翻页 PPT
- 参考瑞士国际主义或电子杂志风版式
- 做公众号头图、分享卡或演讲封面

### 11. 不知道先用哪个入口

可以按这条简单规则：

- 想装东西：先看 `addon`
- 想做任务：先看 `skill`
- 想看底层执行：看 `script`
- 想查规则或映射：看 `reference`
- 想看串联方式：看 `docs/workflows/`

---

## 推荐阅读顺序

如果你是第一次看这个仓库，建议按这个顺序：

1. `README.md`
2. 本文 `docs/06-resource-guide.md`
3. `docs/01-product-spec.md`
4. `docs/02-architecture-design.md`
5. 再按需要进入具体 `skill / script / addon / reference`
