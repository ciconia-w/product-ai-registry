# 采集命令详解

## 论坛

### 调用方式

```bash
python3 scripts/fetch-forum-requirements.py recent <天数> <数量>
```

### 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 天数 | 获取最近N天的帖子 | 30 |
| 数量 | 最多获取N条 | 50 |

### API

- **接口**: `https://n8n.cicd.getdeepin.org/webhook/bbs/thread?startTs={startTs}&endTs={endTs}`
- **方法**: GET
- **参数**:
  - `startTs`: 起始时间戳（毫秒）
  - `endTs`: 结束时间戳（毫秒）

### 重置进度

```bash
python3 scripts/fetch-forum-requirements.py --reset 30 50
```

---

## 邮箱

### 调用方式

```bash
# 只爬取新的（默认）
python3 scripts/fetch-email-requirements.py

# 重新爬取所有
python3 scripts/fetch-email-requirements.py --all
```

### 配置

- **服务器**: imap.exmail.qq.com (IMAP SSL, 端口 993)
- **账户**: product_rep_for_ai@uniontech.com
- **文件夹**: INBOX
- **过滤**: 只处理标题包含 `【AI】种子用户群` 的邮件

---

## 产品需求反馈系统

### 调用方式

```bash
python3 scripts/fetch-product-requirements.py recent <天数> <数量>
```

### 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 天数 | 获取最近N天的需求 | 30 |
| 数量 | 最多获取N条 | 50 |

### API

- **接口**: `https://cooperation.uniontech.com/api/v2/open/worksheet/getFilterRows`
- **方法**: POST
- **认证**:
  - AppKey: `b185c6f1c2ff915f`
  - Sign: 固定签名
- **视图**: 需求池 (viewId: `63857124f76dc9142412dfdf`)

### 输出字段

| 字段 | 说明 |
|------|------|
| title | 反馈主题 |
| content | 需求描述 |
| status | 处理状态 |
| priority | 原始优先级 |
| category | 类别 |
| source | 固定为 "产品需求反馈系统" |

---

## 进度文件

| 数据源 | 进度文件 | 记录内容 |
|--------|----------|----------|
| 论坛 | scripts/forum_progress.json | 已处理帖子 ID |
| 邮箱 | scripts/email_progress.json | 已处理邮件 UID |
| 产品系统 | scripts/product_progress.json | 已处理 rowid |

清空进度文件可重新采集所有数据。
