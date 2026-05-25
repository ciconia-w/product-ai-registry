---
name: uniontech-core-data-compare
description: 使用 OpenCLI 对 datan.uniontech.com 的核心 workbook 数据块取数、对照并输出最终 Excel。适用于“按原表结构直接出表”“只取某一块/某时间/某条件”“基于 workbook 参考值做页面值、请求值、导出值核对”的场景。默认只处理 workbook 已提及块，不继续探索额外页面。
---

# 统信核心数据取数与核对

这个 skill 的目标是：

- 直接按 workbook 结构输出最终 Excel
- 按用户指定块/时间/条件取数并输出 Excel
- 优先使用 `opencli` 做页面侧取数与请求层验证

## 使用边界

- 只处理 workbook 中已提及块
- 不继续探索 workbook 外页面
- 已经探索过但当前不在 workbook 中的信息，只保留在 `references/`

范围规则见：

- `references/out_of_scope_policy.md`

## 预检

先跑：

```bash
python3 ~/.codex/skills/uniontech-core-data-compare/scripts/run_core_data_compare.py preflight
```

预检覆盖：

- 本地是否有 `opencli`
- workbook 是否存在
- `opencli` runtime / plugin manifest / lock 是否存在
- 浏览器桥接、目标页、登录态、token、权限是否正常

## 默认执行模式

用途：

- 用户说“按大表取数”
- 用户要按 workbook 结构直接给最终 Excel

命令：

```bash
python3 ~/.codex/skills/uniontech-core-data-compare/scripts/run_core_data_compare.py default_table
```

默认产物：

- `output/core_data_default_extract_YYYYMMDD.json`
- `output/core_data_compare_YYYYMMDD.json`
- `output/core_data_large_table_YYYYMMDD.md`
- `output/core_data_final_table_YYYYMMDD.xlsx`

说明：

- 默认模式只处理 workbook 已提及块
- 运行时直接走已接入的真实请求回放与公式拼装规则
- workbook 只作为对照基准和最终 Excel 模板
- 不主动继续探索新块

## 自定义执行模式

用途：

- 用户只要某一块
- 用户只要某个时间窗
- 用户只要某个产品/版本/小版本

命令示例：

```bash
python3 ~/.codex/skills/uniontech-core-data-compare/scripts/run_core_data_compare.py \
  custom_query \
  --block "任务栏模式配置" \
  --route "#/point/personalization" \
  --edition "Professional" \
  --major-version "20" \
  --minor-version "107x" \
  --date-type "日" \
  --date-from "2026-05-10" \
  --date-to "2026-05-10"
```

默认产物：

- `output/<block>_custom_raw_YYYYMMDD.json`
- `output/<block>_compare_YYYYMMDD.json`
- `output/<block>_large_table_YYYYMMDD.md`
- `output/<block>_final_YYYYMMDD.xlsx`

## 当前 live extractor 覆盖

默认全表模式当前已接入 workbook 里的 23 个块，执行时统一走：

- 页面上下文真实请求回放
- 必要的请求层口径修正
- 少量派生指标拼装
  - 例如用 `overview` 总用户数拼出开启率分母

各块 route / endpoint / 当前核对状态以：

- `references/block_registry.yaml`

为准。

## opencli 运行约束

- 默认后台运行，不应抢前台
- 依赖环境变量：`OPENCLI_WINDOW_FOCUSED=0`
- 脚本公共层已默认设置该变量
- 自定义 live 取数默认使用独立 session：`core-data-skill`
- 取数结束后会主动执行 `opencli browser <session> close`

后台运行与请求规律参考：

- `references/request_patterns.md`

## 关键脚本

- `scripts/run_core_data_compare.py`
  - 统一入口
- `scripts/preflight_local.py`
  - 本地预检
- `scripts/preflight_browser.py`
  - 浏览器预检
- `scripts/extract_default_table.py`
  - 默认全表 compare items 生成
- `scripts/extract_custom_query.py`
  - 单块取数 + live compare
- `scripts/compare_workbook.py`
  - 统一 compare items 输出
- `scripts/render_large_table.py`
  - markdown 大表输出
- `scripts/write_final_excel.py`
  - workbook 风格最终 Excel 输出

## references 导航

- `references/block_registry.yaml`
- `references/sheet1_rules.md`
- `references/sheet2_rules.md`
- `references/request_patterns.md`
- `references/known_findings.md`
- `references/output_contract.md`
- `references/out_of_scope_policy.md`

只在需要时读取对应 reference，不要整包加载。
