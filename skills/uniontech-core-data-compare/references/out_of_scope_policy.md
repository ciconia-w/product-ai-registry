# 范围边界

## 当前 in-scope

- 只处理 workbook 中已经明确列出的块
- 当前 workbook:
  - `~/core_data_summary.xlsx`
  - `~/Downloads/核心数据汇总.xlsx`
  - `~/Downloads/核心数据汇总(1).xlsx`

## 当前 out-of-scope

- workbook 未提及的新页面、新卡片、新维度
- 为了“顺手看看”而继续做页面探索
- 与当前 workbook 无关的额外导出、额外比对、额外结论

## 执行规则

- 如果块不在 workbook 中，默认不继续探索
- 已经探索过但当前不在 workbook 中的信息，只保留在 `references/` 里作参考
- 除非用户明确要求扩范围，否则不要新增 route 探索
