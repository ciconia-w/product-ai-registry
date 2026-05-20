# 采集命令

执行前先完成：

```bash
python3 scripts/check-larkcli.py
python3 scripts/check-feishu-access.py
python3 scripts/check-feishu-table-schema.py
```

只有检查通过后，才允许执行下面的采集命令。

本地配置路径统一说明见：

`references/local-config.md`

## deepin 论坛

```bash
python3 scripts/fetch-forum-requirements.py 7 50
python3 scripts/fetch-forum-requirements.py 7 50 --all
python3 scripts/fetch-forum-requirements.py 7 50 --reset
```

说明：

- 参数 1：最近多少天，默认 `30`
- 参数 2：最多采集多少条，默认 `50`
- `--all`：忽略进度文件重新采集
- `--reset`：清空进度文件后重新采集
- `--hot-value`：论坛热度阈值，默认 `0`

接口异常兜底：

- 如果论坛 webhook 返回异常、拿到的不是帖子数组，先记录错误输出。
- 如存在团队内部维护人信息，可在本地 `~/.config/requirement-analysis/local_sources.json` 中补充联系提示；不要把个人联系方式直接写进对外分发包。

## 产品需求反馈平台

```bash
python3 scripts/fetch-feedback-platform-requirements.py 7 50
python3 scripts/fetch-feedback-platform-requirements.py 7 50 --all
python3 scripts/fetch-feedback-platform-requirements.py 7 50 --reset
```

说明：

- 参数 1：最近多少天，默认 `30`
- 参数 2：最多采集多少条，默认 `50`
- `--all`：忽略进度文件重新采集
- `--reset`：清空进度文件后重新采集

前置配置：

- 需要在 `~/.config/requirement-analysis/local_sources.json` 或环境变量中提供 `app_key`、`sign`、`worksheet_id`、`view_id`

## deepin Home 开放接口

```bash
python3 scripts/fetch-deepin-home-openapi.py --view requirement_feedback --page-size 100 --pages 1
```

常用视图：

- `requirement_feedback`
- `bug_feedback`
- `all`

前置配置：

- 需要在 `~/.config/requirement-analysis/local_sources.json` 或环境变量中提供 `app_key`、`sign`、`worksheet_id` 以及 `view_ids`

## 合并原始数据

```bash
python3 scripts/merge-requirements.py \
  outputs/requirements_forum_*.json \
  outputs/requirements_feedback_*.json \
  outputs/requirements_deepin_home*.json \
  --output outputs/requirements_merged.json
```

合并后得到的 `requirements_merged.json` 可直接作为后续分析输入。

## 飞书输出

如果需要把最终结果写入飞书文档表格，先读：

`scripts/feishu_flow.md`
