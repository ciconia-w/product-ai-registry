# Company PM UDoc Trace Notes

这份文件记录从本机留底中挖出来的真实操作入口，目的是帮助后续把
畅写 / UDoc 能力进一步收敛成更正式的脚本或命令面。

当前信息来源：

- `$OPENCLI_PLUGIN_PM_LAB_PATH/README.md`
- `/home/aaa/.codex/log/codex-tui.log`

## 已发现的真实入口形态

### 1. 浏览器会话入口

日志中出现过多次使用 `opencli browser` 打开 UDoc 页面：

```bash
opencli --profile rqmfj5sj browser --session crud open 'https://udoc.uniontech.com/co-web/OnlineCollaborationSystem?...'
opencli --profile rqmfj5sj browser --session editor open 'https://udoc.uniontech.com/apps/editor/1806418'
opencli --profile rqmfj5sj browser --session mydocs open 'https://udoc.uniontech.com/co-web/OnlineCollaborationSystem'
```

这说明：

- 昨天的验证过程中确实使用了 OpenCLI 浏览器桥接
- 至少存在共享页、编辑页、文档列表页三类入口

### 2. 文档创建入口

日志中出现过直接请求：

```bash
curl -s 'https://udoc.uniontech.com/apps/editor/ajax/new' \
  -H 'Authorization: basic <token>' \
  -X POST
```

这与 README 中“create a new docx via `POST /apps/editor/ajax/new`”一致。

### 3. 分享链接相关入口

日志中出现过：

```bash
curl -s 'https://udoc.uniontech.com/ocs/v2.php/apps/files_sharing/api/v1/'
curl -s 'https://udoc.uniontech.com/ocs/v2.php/apps/files_sharing/api/v1/shares/red/status' -X POST
```

这说明分享相关能力不是空口描述，至少做过真实请求探索。

### 4. 版本 / 文档历史相关入口

日志中出现过：

```bash
curl -s 'https://udoc.uniontech.com/index.php/apps/files_versions/ajax/renameVersion.php' ...
curl -s 'https://udoc.uniontech.com/index.php/apps/files_versions/ajax/deleteVersion.php' ...
```

这类接口当前没有进入 verified matrix 的主集合，但说明昨天的探索已经触达到版本维度。

### 5. 文件 / API 探测入口

日志中出现过：

```bash
curl -s 'https://udoc.uniontech.com/ocs/v2.php/apps/files/api/v1/'
curl -s 'https://udoc.uniontech.com/avatar/UT006389/24' -I
```

这说明昨天做过 API 面和基础资源可达性探测。

## 当前结论

已经确认：

- 昨天的留底不只是 README 摘要
- 还包括真实执行过的浏览器会话与 HTTP 请求痕迹

但当时尚未确认：

- 这些入口是否已经在 `opencli-plugin-company-pm-lab` 内被整理成独立的 `company-pm-changxie-*.js`
- 是否已经有稳定的本地命令面可直接映射到 registry skill

## 后续脚本化建议

如果后续要继续正式化，可以优先把下面几组入口固化：

1. 文档 CRUD
   - `POST /apps/editor/ajax/new`
   - 编辑页打开
   - 保存
   - rename
   - delete

2. 分享链接
   - create
   - query
   - update label
   - delete

3. 文件空间操作
   - WebDAV `MKCOL`
   - `COPY`
   - `MOVE`

4. 标签 / 收藏
   - systemtags create / bind / remove / delete
   - favorite / unfavorite
