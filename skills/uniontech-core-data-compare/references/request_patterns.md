# 请求模式

## 目标域名

- `https://datan.uniontech.com`

## 常见请求头

页面上下文中常见需要：

- `token: <raw token>`
- `authtoken: Bearer <raw token>`

某些场景 `AuthToken` 也可能出现，但当前 workspace 里最常见的是上面两项。

## 已确认 endpoint

### 数据源概览

- 路径：`/v1/dream-io/app-store/overview`
- 典型 sql:
  - `121`

### 个性化配置

- 路径：`/v1/dream-io/system-events/personalized-configuration`
- 典型 sql:
  - `107` 任务栏模式配置
  - `108` 任务栏高效模式用户切换波动
  - `109` 单个默认插件的被移除率 / 单个非默认插件的主动添加率

### 文件管理器

- 路径：`/v1/dream-io/system-events/file-manager`
- 典型 sql:
  - `115` 保险箱功能开启率
  - `118` 全文搜索功能开启率
  - `117` smb挂载失败率
  - `116` smb挂载失败原因分布

### 系统更新

- 路径：`/v1/dream-io/system-events/system-update`
- 典型 sql:
  - `106`

### 应用启动

- 路径：`/v1/dream-io/system-events/app-start`
- 典型 sql:
  - `113`

## 关键经验

- 页面显示筛选值不等于真实请求层值
- 必须优先抓真实请求体
- 对日期异常的块，优先通过 request rewrite 验证，而不是只信 UI
