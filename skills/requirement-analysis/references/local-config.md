# 本地配置总说明

本 skill 的本地私有配置与授权状态分三类：

## 1. 采集源私有配置

路径：

- `~/.config/requirement-analysis/local_sources.json`

用途：

- 论坛 webhook 地址
- 需求反馈平台 `app_key` / `sign` / `worksheet_id` / `view_id`
- deepin Home 开放接口 `app_key` / `sign` / `worksheet_id` / `view_ids`

来源：

- 可参考 `scripts/local_sources.example.json`

注意：

- 不要提交这个文件
- 不要放进公开分发包

## 2. 飞书目标配置

路径：

- `~/.config/requirement-analysis/feishu-target.json`

用途：

- `wiki_token`
- `spreadsheet_token`
- `sheet_id`
- `start_row`

来源：

- 可参考 `scripts/feishu-target.example.json`

注意：

- 不要提交这个文件
- 不要放进公开分发包

## 3. 本地 lark-cli 授权状态

路径：

- `~/.lark-cli/config.json`

用途：

- 保存本机 `lark-cli` 的 app 配置、用户授权状态与刷新信息

注意：

- 这是本机个人/组织授权状态，不是 skill 的一部分
- 不要复制给别人
- 不要提交到仓库
- 缺少新的 scope 时，补授权即可；不要误判为授权文件失效
