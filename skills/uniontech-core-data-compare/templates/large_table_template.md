# 核心数据大表模板

| block_name | query_path | query_rule | key_dims | workbook_value | page_value | request_value | export_value | status | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 示例 | 系统埋点->文件管理器->smb挂载失败原因分布 | 系统产品=专业版，系统版本=20，系统小版本=107x，日期=按周 | 1070u3 / ARM64 | 1369 / 1319 / 96.35 / 50 / 3.65 | 1844 / 1774 / 96.2 / 70 / 3.8 | 同 page | 同导出 | mismatch | 明细值存在，但与 workbook 不同 |
