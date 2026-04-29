# 产品 AI 注册表 — 产品规格

## 1. 文档信息

- 项目名称：`product-ai-registry`
- 状态：`草稿 v3`
- 面向环境：`UOS / Deepin V25`
- 核心目标：`Agent 优先的 GitHub 资源注册表`
- 本文用途：交给 V25 机器上的开发 Agent，作为实现与评审依据

## 2. 一句话定义

一个为多种本地 AI 编码 Agent 提供共享资源的 GitHub 注册表。  
团队成员只需把一个链接或一段固定提示词发给自己的 Agent，Agent 即可读取注册表、选择适配方案、安装或更新本地资源，并汇报健康状态。

## 3. 解决的问题

团队里至少会有一个可用 Agent，但 Agent 并不统一，常见包括：

- Claude Code
- Codex
- Cursor
- Gemini CLI
- OpenCode
- OpenClaw
- Hermes

当前痛点不是 Agent 不够多，而是：

- 共享提示词、脚本、封装器和工作流散落在不同机器和聊天记录里
- 没有统一的版本源头
- 没有统一的更新方式
- 没有人知道自己本机到底装了什么、缺了什么
- 不同 Agent 的资源格式并不相同，无法假设“一套文件到处通用”

## 4. 核心判断

### 4.1 Agent 是用户界面

第一阶段不做 GUI。  
团队成员主要操作是把固定提示词发给自己的 Agent。

### 4.2 资源源头必须统一

GitHub 仓库是唯一事实来源。  
人不负责同步资源，Agent 负责同步资源。

### 4.3 兼容多 Agent 的关键不是统一格式，而是统一源格式 + 分发适配层

这条是本版规格最重要的修正：

- **不能**假设所有 Agent 都支持 `AGENTS.md + SKILL.md + 固定安装路径`
- **不能**假设所有 Agent 都支持把 GitHub 仓库远程安装为“技能”
- **必须**把注册表设计成“**规范化资源源头**”，再根据 Agent 类型生成或复制到各自原生格式

也就是说：

**注册表统一，落地格式不统一。**

## 5. 产品边界

### 5.1 必须实现

- 任何团队成员通过粘贴一段提示词或给出一个注册表链接，让 Agent 完成本机资源同步
- 注册表能够管理四类规范化资源：
  - `skill`
  - `script`
  - `wrapper`
  - `pack`
- 对多种 Agent 提供明确、可验证的适配策略
- Agent 在使用某项资源前，能判断本机环境是否满足要求
- 更新由 GitHub 变更驱动，资源版本可以被 Agent 检查并汇报
- 安装过程不能破坏用户已有的 agent 本地配置

### 5.2 可以有

- 用户锁定特定资源版本
- 角色能力包
- Agent 启动时做更新提示
- 轻量兜底安装脚本

### 5.3 不做的事

- GUI 或桌面应用
- 自己实现模型层
- 后端服务器或数据库
- 实时多人协作
- 企业级 SSO
- 强制要求所有团队成员自己打开终端执行复杂步骤

## 6. 规范化资源模型

注册表只管理四类规范化对象：

| 类型 | 含义 |
|---|---|
| `skill` | 可复用的任务能力定义 |
| `script` | 带元数据的独立脚本 |
| `wrapper` | 对本地 CLI 的受控封装 |
| `pack` | 一组角色化资源的集合 |

注意：

- `skill` 是**规范化资源类型**
- 它不等于每个 Agent 的“原生技能格式”
- 对不同 Agent，规范化 `skill` 可能被落地成不同产物：
  - `SKILL.md`
  - `CLAUDE.md` 引用块
  - `.claude/agents/*.md`
  - `.cursor/rules/*.mdc`
  - `GEMINI.md`
  - Gemini extension 中的 `skills/`

## 7. 兼容性设计原则

### 7.1 三层模型

每个资源经过三层：

1. **Canonical Source**
   注册表里的规范化定义
2. **Agent Adapter**
   针对目标 Agent 的转换规则
3. **Local Materialization**
   写入本地磁盘的实际格式和路径

### 7.2 不覆盖用户现有配置

适配器必须遵守以下规则：

- 不直接覆盖用户已有的 `CLAUDE.md`
- 不直接覆盖用户已有的 `GEMINI.md`
- 不直接覆盖项目中已有的 `AGENTS.md`
- 不清空用户原有的 `.cursor/rules/`
- 不覆盖用户已有的技能目录，除非当前 capability 明确归自己管理且版本升级已通过校验

推荐做法：

- 所有注册表落地资源都放到带命名空间的 managed 目录
- 主配置文件只追加受控导入或受控引用
- 无法安全合并时，明确报告并停止，不要猜测写入

### 7.3 支持等级

| 等级 | 含义 |
|---|---|
| `A` | 有官方或主仓文档支持，且有明确的本地资源落地方式 |
| `B` | 可通过适配实现，但不是官方原生分发格式 |
| `C` | 只有部分能力或生态线索，视为实验性支持 |

## 8. 多 Agent 兼容矩阵

这是第一阶段真正要照着做的兼容表。

| Agent | 官方/主仓原生指令入口 | 官方/主仓原生扩展面 | 推荐适配方式 | 支持等级 |
|---|---|---|---|---|
| `codex` | `AGENTS.md` | `SKILL.md` / Codex Skills | 原生 `SKILL.md` + `AGENTS.md` | `A` |
| `claude-code` | `CLAUDE.md` | `.claude/agents/*.md`、hooks、settings | 生成 `CLAUDE.md` 导航 + 可选 `.claude/agents` | `B` |
| `cursor` | `AGENTS.md` 或 `.cursor/rules` | `.mdc` 规则文件 | 生成 `.cursor/rules/*.mdc` 或 repo-root `AGENTS.md`，以项目作用域为主 | `B` |
| `gemini-cli` | `GEMINI.md` | `gemini-extension.json`、`skills/`、`agents/` | 原生 Gemini Extension | `A` |
| `opencode` | `AGENTS.md` | `.opencode/skills/*/SKILL.md` | 原生 `SKILL.md` 或兼容目录 | `A` |
| `openclaw` | `AGENTS.md` | ClawHub / plugin / skill 生态 | 第二阶段再验证 | `C` |
| `hermes` | `AGENTS.md` / workspace instructions | `~/.hermes/skills` 与技能生态 | 第二阶段再验证 | `C` |

### 8.1 不能再继续使用的错误假设

以下假设在本规格中被明确否定：

- “所有 Agent 都支持 `AGENTS.md`”
- “所有 Agent 都支持 `SKILL.md`”
- “所有 Agent 都能安装到统一的 `~/.agents/...` 路径”
- “只靠一个 `AGENTS.md` 就能覆盖所有 Agent”

## 9. 第一阶段验证范围

为了确保“真的能用”，MVP 不追求一次性覆盖所有 Agent。

### 9.1 Phase 1 硬支持

- `codex`
- `gemini-cli`
- `opencode`

这三类有较明确的本地扩展或技能能力，最适合先打通。

### 9.2 Phase 1 适配支持

- `claude-code`
- `cursor`

这两类通过适配实现，但不能假设它们原生支持统一的 skill 安装机制。

其中：

- `claude-code` 主要依赖 memory 与 subagent 适配
- `cursor` 主要依赖项目作用域规则适配，不应设计成“全局技能目录”

### 9.3 Phase 2 实验支持

- `openclaw`
- `hermes`

只有在目标机器上完成真实验证后，才能升为正式支持。

## 10. 用户流程

### 10.1 首次配置

1. AI 负责人分享一段固定提示词或注册表链接
2. 用户把它粘贴给自己的 Agent
3. Agent 读取 `REGISTRY.md` 与 `manifest.json`
4. Agent 识别当前 Agent 类型、OS、可用 CLI
5. Agent 选择适配器和默认 `pack`
6. Agent 安装或更新本地资源
7. Agent 输出健康摘要

### 10.2 更新

1. AI 负责人更新 GitHub 仓库
2. 用户发出“更新资源”提示词
3. Agent 比较本地记录与最新 manifest
4. Agent 更新变更项并输出结果

### 10.3 健康检查

1. 用户要求 Agent 进行健康检查
2. Agent 检查资源目录、依赖 CLI、版本、入口文件
3. Agent 输出阻断项、警告项和通过项

## 11. 引导提示词

建议的统一引导提示词：

```text
请使用以下资源注册表配置或更新我的本机 AI 资源：
https://github.com/your-org/product-ai-registry

按 REGISTRY.md 执行：
1. 识别当前 Agent 类型和操作系统
2. 读取 manifest.json，选择兼容的安装适配方式
3. 安装或更新适用的资源
4. 输出健康状态摘要

如果当前 Agent 不具备所需的文件或命令能力，请明确指出阻断原因，不要编造已完成状态。
```

## 12. 安装与更新方式

### 12.1 主要路径

主要路径仍然是：

- 一个链接
- 或一段固定提示词

### 12.2 现实兜底

为了确保“真的能用”，规格必须允许一个**可选兜底路径**：

- 轻量 bootstrap 脚本
- 或按 Agent 分类的最小安装说明

原因：

- 部分 Agent 不一定能可靠写入用户家目录
- 部分 Agent 不一定具备网页读取、文件写入、shell 执行三者同时可用的能力
- 企业网络可能限制 GitHub 访问

因此文档必须承认：

**理想入口是 prompt-first，但不能排斥 helper-first 兜底。**

### 12.3 用户配置共存

“真的能用”还要求资源与用户原有配置共存。

因此：

- 每个 materialized 资源都必须带命名空间前缀
- 例如技能目录和规则文件不能使用过于通用的名称
- 任何自动修改主 memory 文件的行为都必须可逆、可识别、可重复执行

## 13. 本地状态

Agent 需要在本地记录同步状态，但本地状态文件不得保存共享明文令牌。

建议状态文件：

- `~/.ai-registry/installed.json`
- `~/.ai-registry/health-report.json`

最小字段：

- `registry_url`
- `last_synced`
- `active_pack`
- `agent_type`
- `os`
- `items`

每个 item 至少记录：

- `version`
- `installed_at`
- `path`
- `materialization_mode`
- `pinned`
- `source_commit`
- `managed_by_registry`

## 14. 安全要求

### 14.1 不允许的设计

以下做法不允许出现在正式规格里：

- 在共享提示词里直接附带团队共用 PAT
- 在 `installed.json` 中明文保存共享 PAT
- 把私人 Token 作为仓库文件的一部分提交

### 14.2 合理做法

- 优先公开 registry
- 如果必须私有：
  - 使用用户自己的只读 Token
  - 或企业统一下发的只读凭据，但不写入仓库
  - 或未来切换为 deploy key / internal mirror

## 15. 风险

- 不同 Agent 的本地资源格式差异很大
- `claude-code` 和 `cursor` 没有官方“统一远程 skill 安装”机制
- `cursor` 的官方原生能力更偏项目作用域，不适合作为全局安装模型的基准
- `openclaw` 和 `hermes` 在这一套分发模型上还缺少实证
- GitHub 网络可达性会直接影响可用性
- 用户 Agent 的文件权限和 shell 能力可能不一致

## 16. 待确认问题

- registry 公开还是私有
- 是否提供轻量 bootstrap 兜底
- `pack` 按角色还是按团队维护
- 是否要在仓库中提供每种 Agent 的安装适配模板
- Phase 1 是否必须包含 `claude-code` 与 `cursor` 的真实验证

## 17. MVP 范围

MVP 必须包含：

- `AGENTS.md`
- `REGISTRY.md`
- `manifest.json`
- `packs/product-default.json`
- 一个 `skill`
- 一个 `script`
- 一个 `wrapper`
- 至少一个 Agent 适配模板目录

MVP 完成的判据不是“文档写完”，而是：

1. `codex` 能成功消费一个 `skill`
2. `gemini-cli` 能通过 extension 方式消费一个资源包
3. `opencode` 能发现一个本地 skill
4. `claude-code` 或 `cursor` 至少有一个完成适配式落地验证

## 18. 验收标准

- 不再出现“所有 Agent 都共用同一格式”的表述
- 每个正式支持的 Agent 都有明确的适配路径
- manifest 能表达按 Agent 的支持矩阵
- 状态文件不要求保存共享密钥
- 至少一个默认 `pack` 可以被真实安装并验证
