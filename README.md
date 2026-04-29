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
- `addons/`
  可安装的上游增强包
- `references/`
  仅供发现和引用的外部项目或知识来源
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

## 资源角色

仓库中的资源除了按 `type` 分类，还按 **角色** 分类。

### baseline

默认基线资源。

如果当前 Agent 适用、而本地又缺失，Agent 可以直接安装。

适合：

- `oh-my-codex`
- `oh-my-claudecode`
- `superpowers`

### dependency

依赖资源。

不需要上来就安装。只有当某个 `skill / script / wrapper / addon` 依赖它时，Agent 才需要检查或安装。

适合：

- `opencli`
- 其他底层 CLI 或运行时

### reference

参考资源。

不自动安装，只在用户问到相关能力或 Agent 在检索相似方案时返回。

适合：

- `RAG-Anything`
- 外部知识库项目
- 外部实现参考

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
7. 再根据资源角色决定：
   - 直接安装
   - 仅在依赖命中时安装
   - 只作为参考返回

## 目标兼容 Agent

当前注册表面向以下 Agent 设计兼容：

- `codex`
- `claude-code`
- `cursor`
- `gemini-cli`
- `opencode`
- `openclaw`
- `hermes`

注意：

- 这个仓库统一的是**资源源头**
- 不同 Agent 的本地落地格式不一样
- 不要假设所有 Agent 都支持同一种 `skill` 安装方式
- 是否能在当前机器和当前 Agent 上实际安装、更新、运行，由执行中的 Agent 根据 `REGISTRY.md`、adapter、自检结果自行判断
- 未通过自检时，Agent 必须报告阻断，而不是继续安装
- `baseline` 资源可以主动安装
- `dependency` 资源只在命中依赖时处理
- `reference` 资源只做发现和引用，不做默认安装

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
