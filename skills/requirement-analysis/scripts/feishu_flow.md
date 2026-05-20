# 飞书写入流程

仅在需要把结果写入飞书文档表格时读取本文件。

约束：

- 飞书相关操作只允许使用本地 `lark-cli`。
- 不要尝试 OpenClaw 插件、OpenClaw 凭据绑定或其他替代通道。

本地配置与授权路径统一说明见：

`references/local-config.md`

## 前置检查

1. 运行：

```bash
python3 scripts/check-larkcli.py
python3 scripts/check-feishu-access.py
python3 scripts/check-feishu-table-schema.py
```

2. 如果返回 `missing`：

```bash
npm install -g @larksuite/cli
```

3. 如果返回 `unconfigured`：

```bash
lark-cli config init --new
```

该命令会给出扫码或授权链接。完成授权后再次运行 `python3 scripts/check-larkcli.py`。

如果是首次为本 skill 配置飞书能力，用户授权时应一次性拿够当前流程需要的 scope：

```bash
lark-cli auth login --scope "wiki:wiki wiki:wiki:readonly wiki:node:read wiki:space:retrieve sheets:spreadsheet:read sheets:spreadsheet.meta:read sheets:spreadsheet:write_only drive:drive drive:file:upload docx:document:create docx:document:readonly docs:permission.setting:write_only"
```

如果后续执行时提示缺少新的 scope，需要重新触发 `lark-cli auth login`。原因要明确告知用户：

- 本地 `lark-cli` 授权仍然存在，但当前 app 的 user scope 不足以覆盖新动作。
- 例如从“读取 wiki / 表头”切换到“实际写入 spreadsheet”时，需要补 `sheets:spreadsheet:write_only`。
- 例如从“能创建报告”切换到“把报告改成公网链接可见”时，需要补 `docs:permission.setting:write_only`。
- 这类“重新授权”是补权限，不是本地授权丢失。

授权说明：

- `lark-cli` 的本地授权需要保存在当前机器上，后续流程默认复用已有授权。
- 不要在每次执行时重复初始化、切换 profile 或清理授权，除非用户明确要求。
- 当前机器上的配置文件默认位于：`~/.lark-cli/config.json`
- 不要提交、复制或对外分发 `~/.lark-cli/config.json`、本地 token、cookie 或其他授权产物。
- 如果是飞书开放平台 scope 不足，优先根据 `check-feishu-access.py` 输出中的 `console_url` 去补权限，不要误判为本地授权丢失。

## 每次执行前必须先做的事

职责边界：

- `check-feishu-access.py`：检查本地 `lark-cli` 是否具备读取 wiki、读取 spreadsheet、写 spreadsheet、发布分析报告、以及把报告设为公网链接可见所需的权限
- `check-feishu-table-schema.py`：检查当前 spreadsheet 表头是否与输出契约一致
- 两者都通过，才允许继续

在采集开始前，先检查目标飞书表头是否发生变化：

```bash
python3 scripts/check-feishu-table-schema.py
```

规则：

- 如果表头未变化，继续采集和写入。
- 如果表头有变化，先根据最新表头重新对齐输出字段，再开始本次采集。
- 不允许在未完成字段对齐前直接写入旧格式数据。

## 写入

如果 `finalize-delivery.py` 生成了翻译队列，先由 agent 按 `translations.example.json` 的格式补出译文，再重新执行 finalize：

```bash
python3 scripts/finalize-delivery.py \
  --input outputs/delivery.json \
  --output outputs/delivery_final.json \
  --translation-queue outputs/translation_queue.json \
  --translations outputs/translations.json
```

发布分析报告并把链接写入最终交付 JSON：

```bash
python3 scripts/publish-feishu-report.py \
  --file outputs/report.md \
  --name '需求分析报告-测试.md'
```

默认行为：

- 报告发布后，会把链接分享权限设为 `anyone_readable`
- 也就是“互联网获得链接的用户都可见”

确认 `K/L/M` 已补齐后，再执行正式写入：

```bash
python3 scripts/write-feishu-table.py \
  --input outputs/requirements_delivery.json
```

## 定时任务

如果用户要求设置定时任务，使用：

```bash
python3 scripts/install-scheduler.py \
  --schedule "0 9 * * *"
```

调度约束：

- 定时任务入口必须先执行表头检查。
- 表头异常时终止本次采集，并输出修正提示。
- 表头通过后，才允许执行采集、分析、写入飞书。
