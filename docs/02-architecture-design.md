# 产品 AI 注册表 — 架构设计

## 1. 设计目标

这个系统不是桌面应用，也不是后端服务。  
它是一个 **GitHub 上的规范化资源源头**，再通过不同 Agent 的本地适配机制，把资源落到各自真正支持的格式与路径上。

核心目标：

- 统一资源定义
- 分化安装格式
- 允许不同 Agent 用自己的原生方式消费同一份资源

## 2. 总体架构

```text
Canonical Registry (GitHub)
  ├─ manifest.json
  ├─ REGISTRY.md
  ├─ skills/
  ├─ scripts/
  ├─ wrappers/
  ├─ addons/
  ├─ references/
  └─ packs/

Agent-specific adapters
  ├─ codex
  ├─ claude-code
  ├─ cursor
  ├─ gemini-cli
  ├─ opencode
  ├─ openclaw (experimental)
  └─ hermes (experimental)

Local materialization
  ├─ AGENTS.md
  ├─ CLAUDE.md
  ├─ GEMINI.md
  ├─ .cursor/rules/*.mdc
  ├─ .claude/agents/*.md
  ├─ .gemini/agents/*.md
  ├─ .opencode/skills/*/SKILL.md
  └─ executable scripts / wrappers
```

一句话：

**注册表只存 canonical 资源；真正落地时由 adapter 决定写成什么。**

## 3. 核心架构原则

### 3.1 Canonical over Local

GitHub 仓库中的资源定义是唯一事实来源。  
本地目录只是 materialization 结果，不是源头。

### 3.2 Adapter over Uniform Path

不能使用“统一路径对照表”的架构。  
不同 Agent 必须由独立 adapter 负责。

### 3.3 Prompt-first, helper-optional

默认入口是 prompt 或链接。  
如果 Agent 缺少能力，允许使用轻量 helper 作为兜底。

### 3.4 Verify before claiming success

如果某 Agent 没有在真实机器上验证通过，文档中必须标记为实验性或适配中，而不是“已支持”。

## 4. 兼容性研究结论

这部分是本版设计的基础结论。

### 4.1 Codex

根据 OpenAI 官方和主仓资料：

- 使用 `AGENTS.md` 作为项目指令入口
- 支持 Codex Skills，即 `SKILL.md` 形式的技能目录
- `openai/skills` 提供技能目录与 `skill-installer`

因此：

- `codex` 适合作为一等支持对象
- canonical `skill` 可直接 materialize 成 `SKILL.md` 目录

### 4.2 Claude Code

根据 Anthropic 官方文档：

- 主指令入口是 `CLAUDE.md`
- 可使用 `.claude/agents/*.md` 定义 subagents
- 可使用 hooks 和 settings 扩展行为

但没有官方“远程技能仓库安装协议”。

因此：

- `claude-code` 不能被设计成与 Codex 共用技能安装路径
- 对 Claude Code 的正确架构是：
  - 生成 `CLAUDE.md` 导航或导入
  - 视需要生成 `.claude/agents/*.md`
  - 把脚本与 wrapper 落到本地受控路径

### 4.3 Cursor

根据 Cursor 官方文档：

- 支持 repo-root `AGENTS.md`
- 更原生的方式是 `.cursor/rules/*.mdc`

没有官方 `SKILL.md` 安装机制。
规则体系本质上是项目作用域，而不是成熟的全局技能仓库机制。

因此：

- `cursor` 应以“规则文件适配”而不是“技能目录适配”为主
- canonical `skill` 可以被转换为：
  - `.cursor/rules/*.mdc`
  - 或较弱的 repo-root `AGENTS.md` 说明
- 第一阶段应明确把 Cursor 支持限定在项目作用域消费

### 4.4 Gemini CLI

根据 Google Gemini CLI 主仓文档：

- 使用 `GEMINI.md` 作为层级 memory 文件
- 支持 `.gemini/agents/*.md`
- 支持 `gemini-extension.json`
- Extension 可自带 `skills/`、`agents/`、`hooks/`、`commands/`
- 可通过 `gemini extensions install <git-url>` 安装和更新

因此：

- `gemini-cli` 是一等支持对象
- registry 可以为 Gemini 输出原生 extension 包

### 4.5 OpenCode

根据 OpenCode 官方文档：

- 支持 `AGENTS.md`
- 支持 `.opencode/skills/*/SKILL.md`
- 也兼容 `.claude/skills` 和 `.agents/skills`

因此：

- `opencode` 是一等支持对象
- canonical `skill` 可直接 materialize 成 `SKILL.md`

### 4.6 OpenClaw 与 Hermes

从公开主仓和生态资料看：

- 两者都与 `AGENTS.md`、skills、插件生态有关
- 但在“团队 registry -> 自动安装 -> 一致更新”这条链路上，尚不足以作为第一阶段的硬承诺

因此：

- 第一阶段只标记为 `experimental`
- 需要在真实目标机器上完成独立验证后才能升格

## 5. 用户本地配置保护

这是多 Agent 兼容里最容易漏掉的一条：

**registry 不能假设自己拥有用户主配置文件。**

因此必须遵守：

- 不覆盖用户原有 `CLAUDE.md`
- 不覆盖用户原有 `GEMINI.md`
- 不删除用户已有 `.cursor/rules`
- 不重写用户已有 `AGENTS.md`
- 不抢占未命名空间隔离的 skills 目录

正确做法：

- 使用 registry 自己的 managed 目录
- 使用导入、引用、独立规则文件或独立 extension
- 让主配置文件只承担“挂载点”角色，而不是存放全部内容

## 6. 支持策略

### 6.1 正式支持对象

第一阶段正式支持：

- `codex`
- `gemini-cli`
- `opencode`

### 6.2 适配支持对象

第一阶段适配支持：

- `claude-code`
- `cursor`

### 6.3 实验对象

- `openclaw`
- `hermes`

## 7. 仓库目录结构

推荐目录结构：

```text
product-ai-registry/
  AGENTS.md
  REGISTRY.md
  README.md
  CHANGELOG.md
  manifest.json

  skills/
    prd-review/
      SKILL.md
      references/
      scripts/

  scripts/
    forum-demand-crawler/
      tool.yaml
      run.sh

  wrappers/
    opencode-review/
      tool.yaml
      run.sh

  packs/
    product-default.json

  adapters/
    codex/
      adapter.yaml
    claude-code/
      adapter.yaml
      templates/
    cursor/
      adapter.yaml
      templates/
    gemini-cli/
      adapter.yaml
      extension-template/
    opencode/
      adapter.yaml
```

关键变化：

- 新增 `adapters/`
- 不再假设 canonical 目录直接等于本地安装路径

## 8. Canonical 资源模型

### 8.1 skill

规范化 skill 的职责：

- 描述能力名称
- 描述触发条件
- 描述参考资料
- 描述支持的目标 Agent

它不是任何 Agent 的“唯一原生形态”。

### 8.2 script

规范化 script 的职责：

- 描述入口文件
- 描述运行时
- 描述依赖 CLI
- 描述输入输出

### 8.3 wrapper

规范化 wrapper 的职责：

- 绑定某个本地 CLI
- 固定受控参数
- 定义允许的调用方式

### 8.4 pack

规范化 pack 的职责：

- 聚合一组 capability
- 标记默认角色或场景
- 为不同 Agent 指定不同 materialization 目标

### 8.5 addon

规范化 addon 的职责：

- 表示一个可安装的上游增强包
- 自身可能不是单文件 skill 或脚本
- 常见为外部 git 仓库、release 或 package manager 目标

### 8.6 reference

规范化 reference 的职责：

- 表示一个可供 Agent 发现和引用的上游项目
- 默认不自动安装
- 用于“有没有这类能力可以参考”这种问题

## 9. Adapter 模型

每个 Agent adapter 至少包含：

- `agent_id`
- `support_level`
- `instruction_mode`
- `skill_mode`
- `script_mode`
- `wrapper_mode`
- `install_strategy`
- `supported_os`

推荐 `adapter.yaml` 结构：

```yaml
agent_id: claude-code
support_level: B
instruction_mode: claude_md
skill_mode: generated_subagent
script_mode: local_copy
wrapper_mode: local_copy
install_strategy: prompt_or_helper
supported_os:
  - linux
paths:
  claude_md: "~/.claude/CLAUDE.md"
  agents_dir: "~/.claude/agents"
  managed_root: "~/.ai-registry/materialized/claude-code"
```

## 10. Materialization 模式

定义几个固定的落地模式：

| mode | 含义 |
|---|---|
| `native_skill_dir` | 原生 `SKILL.md` 技能目录 |
| `project_native_skill_dir` | 写入目标仓库内部的技能目录 |
| `generated_subagent` | 生成某 Agent 的 subagent 文件 |
| `project_generated_subagent` | 在目标仓库上下文内生成 subagent 入口 |
| `generated_rules` | 生成规则文件，例如 `.cursor/rules/*.mdc` |
| `project_generated_rules` | 在目标仓库内生成规则文件 |
| `memory_import` | 写入主 memory 文件并导入其他内容 |
| `extension_bundle` | 生成原生 extension 包 |
| `local_copy` | 复制脚本或 wrapper 到本地目录 |
| `project_local_copy` | 复制脚本或 wrapper 到目标仓库路径 |

例子：

- Codex skill -> `native_skill_dir`
- OpenCode skill -> `native_skill_dir`
- Claude Code skill -> `generated_subagent` 或 `memory_import`
- Cursor skill -> `generated_rules`
- Gemini CLI skill pack -> `extension_bundle`
- Repo-specific build assets -> `project_*` modes

## 11. Materialization 路径策略

每个 adapter 都必须使用可共存的路径策略。

推荐规则：

- `codex`: 使用 registry 命名空间前缀的 skill 目录
- `opencode`: 使用 registry 命名空间前缀的 skill 目录
- `claude-code`: 使用 `~/.ai-registry/materialized/claude-code/...` 存放主体内容，再通过 `CLAUDE.md` 导入或 `.claude/agents` 引用
- `cursor`: 使用 `.cursor/rules/lody-*.mdc`，不碰其他规则
- `gemini-cli`: 使用独立 extension 名称，不与用户其他 extension 冲突

禁止：

- 无命名空间的全局覆盖
- 删除未知来源的用户文件
- 直接重写现有主配置文件的全部内容

## 12. manifest.json 结构

`manifest.json` 必须表达：

- canonical 资源定义
- 支持的 Agent
- 每个 Agent 的 materialization 方式
- 依赖和版本信息
- 上游来源信息
- 资源角色和缺失时策略

推荐结构：

```json
{
  "registry_version": "1.0.0",
  "generated_at": "2026-04-29T00:00:00Z",
  "default_pack": "product-default",
  "agents": {
    "codex": { "support_level": "A" },
    "claude-code": { "support_level": "B" },
    "cursor": { "support_level": "B" },
    "gemini-cli": { "support_level": "A" },
    "opencode": { "support_level": "A" },
    "openclaw": { "support_level": "C" },
    "hermes": { "support_level": "C" }
  },
  "packs": [
    {
      "id": "product-default",
      "version": "1.0.0",
      "items": [
        "skill:prd-review",
        "script:forum-demand-crawler",
        "wrapper:opencode-review"
      ]
    }
  ],
  "items": [
    {
      "type": "skill",
      "id": "prd-review",
      "version": "1.0.3",
      "path": "skills/prd-review",
      "source": { "kind": "local" },
      "policy": {
        "role": "optional",
        "action_on_missing": "install"
      },
      "support": {
        "codex": { "mode": "native_skill_dir" },
        "opencode": { "mode": "native_skill_dir" },
        "claude-code": { "mode": "generated_subagent" },
        "cursor": { "mode": "generated_rules" },
        "gemini-cli": { "mode": "extension_bundle" }
      },
      "checksum": "sha256-abc123"
    }
  ]
}
```

Interpretation rules:

- `baseline + install`: install proactively when compatible
- `dependency + block/install`: only resolve when another item requires it
- `reference + suggest`: never auto-install, only surface to the user or agent

## 13. REGISTRY.md 的职责

`REGISTRY.md` 是 Agent 读取入口，但不能承担“跨 Agent 统一安装器”的幻想。

它必须做的事是：

1. 让 Agent 先识别自己是什么类型
2. 告诉 Agent 去读取对应 adapter
3. 告诉 Agent 依据 adapter 进行 materialization
4. 要求 Agent 在失败时明确报告限制

正确流程不是：

`读 REGISTRY.md -> 按统一路径复制`

而是：

`读 REGISTRY.md -> 识别 agent -> 读 adapters/<agent>/adapter.yaml -> 执行该 agent 的本地落地方案`

## 14. 本地状态文件

本地状态文件建议为：

- `~/.ai-registry/installed.json`
- `~/.ai-registry/health-report.json`

### 14.1 installed.json

```json
{
  "registry_url": "https://github.com/your-org/product-ai-registry",
  "last_synced": "2026-04-29T10:40:00Z",
  "active_pack": "product-default",
  "agent_type": "codex",
  "items": {
    "skill:prd-review": {
      "version": "1.0.3",
      "materialization_mode": "native_skill_dir",
      "path": "~/.agents/skills/prd-review",
      "source_commit": "abcde12345",
      "pinned": false,
      "managed_by_registry": true
    }
  }
}
```

### 14.2 不允许保存的内容

- 共享明文 GitHub Token
- 任何仓库外泄后会造成横向风险的长期密钥

## 15. 安装流程

### 15.1 标准流程

1. 读取 `manifest.json`
2. 识别 `agent_type`
3. 加载该 Agent 的 `adapter.yaml`
4. 选择默认 `pack`
5. 对 pack 中每项执行：
   - 取 canonical 资源
   - 根据 adapter 选择 materialization 模式
   - 选择 namespaced 路径
   - 写入本地目录
   - 校验结果

### 15.2 兜底流程

如果 Agent 无法完成：

- 访问 GitHub
- 写入家目录
- 执行 shell

则允许 fallback 到一个 helper 脚本或人工一步，但这一条不应写成主路径。

## 16. 健康检查

健康检查必须是按 Agent 适配路径执行，而不是按统一格式执行。

健康检查至少验证：

- 当前 Agent 是否属于支持矩阵
- 当前 Agent 的 adapter 是否存在
- pack 中每个项目是否对当前 Agent 可 materialize
- 本地入口文件或目标文件是否存在
- 依赖 CLI 是否可用
- 用户主配置文件是否仍然保留且可解析
- registry 受管文件是否与用户文件发生冲突

状态分为：

- `ok`
- `warning`
- `blocked`

## 17. 版本与分支策略

### 17.1 分支

- `main`：稳定版
- `beta`：预发布测试
- `dev`：开发分支

### 17.2 版本策略

每个 capability 单独语义化版本。  
每个 adapter 也要独立版本化。

这意味着：

- skill 更新不一定需要 adapter 更新
- 新增某 Agent 支持时，可能只改 adapter

## 18. 主要漏洞与已修正点

本轮评审中已确认需要修正的高风险点：

1. 不能再声称“所有 Agent 都支持 AGENTS.md”
2. 不能再声称“所有 Agent 都支持 SKILL.md”
3. 不能再使用统一安装路径表作为主设计
4. 不能建议在共享提示词或本地状态文件中保存共享 PAT
5. 不能把 `openclaw` 与 `hermes` 直接列为正式支持而不做实测
6. 不能覆盖用户现有的 agent 本地配置文件

## 19. MVP 实施顺序

1. 建立 canonical registry 结构
2. 建立 `manifest.json` 与 `adapter.yaml` 结构
3. 先完成 `codex`、`gemini-cli`、`opencode` 的 materialization
4. 再完成 `claude-code`、`cursor` 的适配
5. 最后评估 `openclaw`、`hermes`

## 20. MVP 完成标准

MVP 真正完成的标准：

- `codex` 在真实机器上能安装并识别至少一个 skill
- `gemini-cli` 能通过 extension 安装并更新至少一个资源包
- `opencode` 能发现并使用至少一个 skill
- `claude-code` 或 `cursor` 至少有一个成功完成适配式落地
- 已验证 materialization 不会覆盖用户既有配置
- 文档中不再存在统一格式误导

## 21. 参考依据

本架构的兼容性判断基于各工具官方或主仓资料：

- OpenAI Codex / `AGENTS.md` / `openai/skills`
- Anthropic Claude Code `CLAUDE.md`、subagents、hooks、settings
- Cursor 官方 Rules 文档
- Google Gemini CLI `GEMINI.md`、extensions、skills、agents
- OpenCode 官方 `AGENTS.md` 与 Skills 文档
- OpenClaw 与 Hermes 主仓公开资料
