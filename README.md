# product-ai-registry

团队共享的 AI 资源注册表。

这个仓库的用途很简单：

- 集中存放团队共享的 `skills`、`scripts`、`wrappers`、`packs`
- 让不同本地 Agent 按统一规则读取、安装、更新这些资源
- 让新成员只需要一个链接或一段提示词，就能让自己的 Agent 自行完成配置

## 适合什么场景

适合这种团队：

- 每个人本机至少有一个可用 Agent
- 但 Agent 不统一，例如 `Claude Code`、`Codex`、`Cursor`、`Gemini CLI`、`OpenCode`
- 希望把常用提示词、脚本、封装器、能力包统一收口
- 希望后续更新直接通过 GitHub 仓库分发

## 这个仓库里有什么

- `skills/`
  规范化 skill 定义
- `scripts/`
  团队共享脚本
- `wrappers/`
  对本地 CLI 的受控封装
- `packs/`
  按角色或场景组合的资源包
- `adapters/`
  不同 Agent 的适配规则
- `manifest.json`
  结构化索引
- `AGENTS.md`
  给 Agent 的仓库入口
- `REGISTRY.md`
  给 Agent 的操作合约

## 怎么用

### 给人看

把下面这段提示词发给团队成员，让他们直接贴给自己的 Agent：

```text
请使用以下资源注册表配置或更新我的本机 AI 资源：
https://github.com/ciconia-w/product-ai-registry

按 REGISTRY.md 执行：
1. 识别当前 Agent 类型和操作系统
2. 读取 manifest.json，选择兼容的安装适配方式
3. 安装或更新适用的资源
4. 输出健康状态摘要

如果当前 Agent 不具备所需的文件或命令能力，请明确指出阻断原因，不要编造已完成状态。
```

### 给 Agent 看

Agent 进入仓库后，按这个顺序工作：

1. 读 `AGENTS.md`
2. 读 `REGISTRY.md`
3. 读 `manifest.json`
4. 识别自己是什么 Agent
5. 读对应的 `adapters/<agent-id>/adapter.yaml`
6. 再决定如何把资源落到本地

## 当前支持范围

### 第一阶段正式支持

- `codex`
- `gemini-cli`
- `opencode`

### 第一阶段适配支持

- `claude-code`
- `cursor`

### 第二阶段实验支持

- `openclaw`
- `hermes`

注意：

- 这个仓库统一的是**资源源头**
- 不同 Agent 的本地落地格式不一样
- 不要假设所有 Agent 都支持同一种 `skill` 安装方式

## 当前示例资源

目前仓库里已经有这些示例：

- `pack:product-default`
- `skill:prd-review`
- `script:forum-demand-crawler`
- `wrapper:opencode-review`
- `pack:deepin-color-correction-linglong`
- `skill:linglong-uab-shortest-path`
- `script:reset-linglong-builder-env`
- `script:rebuild-linglong-uab-shortest-path`

## 重要原则

- 资源统一，落地格式不统一
- 先看 adapter，再决定安装路径
- 不覆盖用户现有的 `CLAUDE.md`、`GEMINI.md`、`AGENTS.md` 或 `.cursor/rules`
- repo-specific 资源必须按 `project-scope` 处理

## 进一步阅读

- [REGISTRY.md](REGISTRY.md)
- [AGENTS.md](AGENTS.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [docs/01-product-spec.md](docs/01-product-spec.md)
- [docs/02-architecture-design.md](docs/02-architecture-design.md)
- [docs/03-registry-schemas.md](docs/03-registry-schemas.md)
- [docs/04-bootstrap-and-helpers.md](docs/04-bootstrap-and-helpers.md)
- [docs/05-project-scoped-materialization.md](docs/05-project-scoped-materialization.md)
