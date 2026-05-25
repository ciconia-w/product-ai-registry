# 输出约定

## 必须输出

每次完整运行至少应能给出：

1. 结构化 compare JSON
2. 原表风格大表 markdown
3. 最终 Excel

如用户明确要求，才额外输出 zip / delivery 目录。

## 大表最小列

如果输出 mismatch 汇总表，至少包含：

- `block_name`
- `query_path`
- `query_rule`
- `key_dims`
- `workbook_value`
- `page_value`
- `request_value`
- `export_value`
- `status`
- `reason`

## 状态建议枚举

- `matched`
- `matched_after_request_fix`
- `mismatch`
- `page_detail_exists_but_value_differs`
- `request_chain_not_fully_reproduced`
- `interface_empty`
- `matched_under_107x_scope`
- `unsupported`
- `unauthorized`

## 结果优先级

当多种证据冲突时，优先级从高到低：

1. 真实请求层返回
2. 导出 CSV
3. 页面展示值
4. 口头规则/历史记忆

## 范围控制

- 默认只处理 workbook 已提及块
- 不继续探索 workbook 外页面
