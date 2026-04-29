# product-ai-registry

团队的 AI 资源注册表。

这个仓库不是桌面应用，也不是模型服务。它只做一件事：

- 把团队共享的 `skills`、`scripts`、`wrappers`、`packs` 统一放在一个 GitHub 仓库里
- 让不同本地 Agent 通过同一套规则读取、安装、更新、检查这些资源

## 目标

- 成员只需要把一个链接或一段提示词发给自己的 Agent
- Agent 自己读取 `REGISTRY.md` 和 `manifest.json`
- Agent 自己判断当前环境和支持等级
- Agent 自己完成适配式安装或更新

## 主要文件

- `AGENTS.md`: 仓库级入口，告诉 Agent 下一步看哪里
- `REGISTRY.md`: 操作合约，定义 Agent 应如何消费这个仓库
- `manifest.json`: 结构化索引
- `packs/`: 角色或场景资源包
- `skills/`: 规范化 skill 源定义
- `scripts/`: 团队共享脚本
- `wrappers/`: 对本地 CLI 的受控封装
- `adapters/`: 按 Agent 的适配规则

## 当前策略

- Phase 1 正式支持：`codex`、`gemini-cli`、`opencode`
- Phase 1 适配支持：`claude-code`、`cursor`
- Phase 2 实验支持：`openclaw`、`hermes`

## 维护方式

- 所有变更都必须走 Pull Request
- `main` 分支受保护
- `manifest.json`、`REGISTRY.md`、`adapters/**`、`packs/**` 等关键文件需要 owner 审批
- CI 会校验 manifest、pack 引用和关键文件结构

## 相关文档

- [REGISTRY.md](REGISTRY.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [docs/01-product-spec.md](docs/01-product-spec.md)
- [docs/02-architecture-design.md](docs/02-architecture-design.md)
