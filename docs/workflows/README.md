# Workflows

这里不再把 workflow 建模为正式 registry 资源类型。

这个目录只负责说明：

- 哪些原子资源应组合使用
- 推荐执行顺序
- 前置检查
- 阻断条件
- 输出与完成定义

当前保留的 workflow 文档：

- `ai-daily-news.md`

当前只保留明确需要组合说明的 workflow 文档。

如果某项能力本身已经能由单个 `skill` 或一组紧耦合原子资源自行表达，就不额外建立 workflow 文档。
