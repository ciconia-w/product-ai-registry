# Excel 字段映射 (15列)

| Excel 列 | 数据来源 | 说明 |
|-----------|----------|------|
| 类别 | analysis.type | 需求类型（功能需求/非功能需求/问题反馈/建议优化） |
| 所属产品 | analysis.product_name | UOS AI助手 / UOS V20 / UOS V25 等 |
| 所属模块 | analysis.module | 功能模块（控制中心/DDE/文件管理等） |
| 优先级 | priority.level / score | P0/P1/P2/P3/P4（基于分数计算） |
| 评分 | priority.score | 0-100 |
| 需求标题 | title | 原始需求标题 |
| 需求描述 | content | 需求详细内容 |
| 用户故事 | 拼装生成 | 作为 + 场景 + 我希望 |
| 验收标准 | analysis.expected_behavior | 验证标准（基于期望行为生成） |
| 来源 | source | 论坛 / 邮箱 / 产品需求反馈系统 |
| 来源地址 | url | 原始链接 |
| 需求分析 | analysis.complexity | 技术复杂度（高/中/低） |
| 操作系统 | analysis.os | Deepin V20 / Deepin V25 / UOS |
| 系统版本 | analysis.os_version | 版本号（20/25/1070等） |
| 硬件架构 | analysis.hardware_arch | AMD64 / ARM64 / x86_64 |

---

## 优先级等级计算

| 分数范围 | 等级 | 说明 |
|----------|------|------|
| 85-100 | P0 | 紧急且核心 |
| 70-84 | P1 | 重要 |
| 50-69 | P2 | 中等 |
| 30-49 | P3 | 低 |
| 0-29 | P4 | 暂缓 |

---

## 用户故事拼装格式

```
作为{user_role}，{scenario}，我希望{expected_behavior}
```

三个字段均来自 analysis：
- user_role: 用户角色
- scenario: 使用场景
- expected_behavior: 期望行为
