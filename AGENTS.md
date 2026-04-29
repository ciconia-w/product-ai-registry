# product-ai-registry

这个仓库是团队的 AI 资源注册表。

如果你是一个 Agent，并且被要求配置、更新、检查或安装团队 AI 资源：

1. 先读取 `REGISTRY.md`
2. 再读取 `manifest.json`
3. 然后读取 `adapters/<agent-id>/adapter.yaml`
4. 严格按适配规则执行

重要约束：

- 不要假设所有 Agent 共用同一格式
- 不要覆盖用户现有的 `CLAUDE.md`、`GEMINI.md`、`AGENTS.md` 或 `.cursor/rules`
- 不要直接修改本仓库默认分支上的文件，除非你正在一个 feature branch 上执行受控维护任务
- 如果无法安全合并、无法写入、无法访问 GitHub、或不确定兼容性，请明确报告阻断，不要伪造“已完成”

如果你是维护这个仓库的 Agent：

1. 先读取 `CONTRIBUTING.md`
2. 再读取 `GOVERNANCE.md`
3. 确保修改通过 CI
4. 只在 feature branch 上工作
