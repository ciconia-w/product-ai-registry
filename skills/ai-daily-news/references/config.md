# AI日报配置

## 默认配置

- **收件人**: 通过环境变量 `EMAIL_RECIPIENT` 或宿主配置提供
- **发件人名称**: 通过环境变量 `EMAIL_SENDER_NAME` 自定义
- **SMTP**: 使用宿主环境中的 `SMTP_SERVER`、`SMTP_PORT`、`SMTP_USERNAME`、`SMTP_PASSWORD`

## 新闻源

### 当前架构（2026-05-09）

#### 中文源

- **脚本主源（优先级1，必试）**：
  - hex2077.dev（原 ai.hubtoday.app）- 使用脚本自动解析 HTML
  - URL格式: `https://hex2077.dev/docs/YYYY-MM/YYYY-MM-DD/`
  - 包含5大分类：产品与功能更新、前沿研究、行业展望与社会影响、开源TOP项目、社媒分享

- **强制中文源（优先级2，必试）**：
  - AI HOT (https://aihot.virxact.com/daily)
  - 优先使用 `scripts/aihot_fetcher.py`
  - 若直连抓取失败，必须改用当前 agent 的网页抓取或浏览器能力获取页面文本，再交给 `scripts/aihot_parser.py`
  - AI HOT 是强制中文源，不能静默跳过

- **可选补充源（按能力启用）**：
  - AI HOT MP 热文榜
  - 新智元微信公众号（示例文章页）
  - 只有当前 agent 具备网页抓取、浏览器自动化、或稳定网页读取能力时才使用

- **备用源（脚本主源失败时使用）**：
  - 量子位 (https://www.qbitai.com/feed) - RSS格式
  - 仅当脚本主源失败时使用
  - 不能替代 AI HOT

#### 英文源（RSS）
- MIT Technology Review (https://www.technologyreview.com/feed/)
  - MIT旗下权威技术媒体
  - 每小时更新
  - 内容质量极高

- AI News (https://www.artificialintelligence-news.com/feed/)
  - 专业AI新闻网站
  - 每日更新
  - 覆盖企业AI、机器学习等

- MIT News AI (https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml)
  - MIT官方新闻AI版块
  - 每日更新
  - 学术研究动态

#### 研究源
- arXiv AI (https://export.arxiv.org/rss/cs.AI)
  - 全球最大AI论文预印本服务器
  - 每日更新数百篇
  - 每日只取Top 3最新论文
  - 注意：可能存在网络访问限制，已添加异常处理

### 旧架构（已废弃）
- ~~smol.ai~~ - 因更新频率低（每周更新）已移除

## 内容配比

- 中文新闻: 65%
- 英文新闻: 35%
- arXiv论文: Top 3（不计入配比，额外添加）
- 总计: 约40-45条新闻

### 英文新闻处理

翻译时机：在生成日报时由当前 Agent 直接翻译，而非在 RSS 获取阶段翻译。

最终格式：

```
【MIT Tech Review】物理AI成为制造业下一个优势（中文标题）
几十年来，制造商一直追求自动化来提高效率、降低成本...（中文摘要）
原文: Why physical AI is becoming manufacturing's next advantage
链接: https://www.technologyreview.com/...
```

处理规则：
- ✅ RSS获取时保留原文（--no-translation参数）
- ✅ 生成日报时由当前 Agent 翻译标题和内容
- ✅ 保留英文原文标题
- ✅ 包含原文链接
- ✅ 标注来源
- ✅ 英文新闻放在中文新闻之后

### 获取流程

```
Step 1: 获取新闻源（原文模式）
   ├─ 中文脚本主源: python3 scripts/parse_news.py {date}
   │   └─ 失败 → python3 scripts/rss_fetcher.py chinese (量子位fallback)
   │
   ├─ 中文强制源: python3 scripts/aihot_fetcher.py daily
   │   └─ 失败 → 用当前 agent 的网页抓取能力获取 https://aihot.virxact.com/daily 文本，再执行:
   │      python3 scripts/aihot_parser.py daily < /tmp/aihot-text.txt
   │
   ├─ 合并中文源: python3 scripts/merge_sources.py --primary ... --aihot ...
   │
   ├─ 英文源: python3 scripts/rss_fetcher.py english --no-translation
   │   ├─ MIT Technology Review
   │   ├─ AI News
   │   └─ MIT News AI
   │
   └─ 研究源: python3 scripts/arxiv_fetcher.py
       └─ arXiv Top 3

Step 2: 内容配比控制
   - 中文65% / 英文35% (中文: 25条, 英文: 17条)
   - total = len(chinese_news) + len(english_news)

Step 3: 去重
   - python3 scripts/dedupe.py

Step 4: 使用当前 Agent 翻译英文新闻
   - 遍历英文新闻列表
   - 由当前 Agent 翻译标题和内容
   - 保留原文和链接

Step 5: 生成日报（中文优先）
   - 中文AI资讯在前（5大分类）
   - 英文AI资讯在后（翻译后）
   - 纯文本格式，无Markdown

Step 6: 发送邮件
   - python3 scripts/send-email/run.py "$EMAIL_RECIPIENT" "<subject>" "<body>"

Step 7: 保存历史
   - 保存到history/YYYY-MM-DD.json
```

## KOL列表（只记录有实质内容的动态）

### 头部公司
- @OpenAI
- @AnthropicAi
- @GoogleDeepMind
- @huggingface

### 创始人/CEO
- @sama (Sam Altman) - OpenAI CEO
- @karpathy (Andrej Karpathy) - 前特斯拉AI总监、OpenAI创始成员
- @Kimi Product - 月之暗面Kimi

### KOL/开发者
- @xiaohu (李rumor) - AI投资人
- @idoubi - 开发者

## 撰写规范

### 数字格式
- 统一使用阿拉伯数字：680亿美元、200亿美元
- 千分位分隔符：400,000 token、24,000个
- 金额：4.20美元/分钟、60美元

### 产品思考标识
- 必须使用：💡 产品思考：

### 邮件格式
- 不添加签名
- 新闻顺序：中文在前，英文在后
- 分类前放置对应emoji
- 纯文本格式，不使用Markdown

### 中文源优先级
```
优先级1: hex2077.dev (脚本主源，必须尝试)
优先级2: AI HOT (强制中文源，必须尝试)
优先级3: 量子位 (仅当脚本主源失败时)
优先级4: AI HOT MP / 新智元 (可选补充)
```

## 农历计算

- 使用本 capability 内的脚本：`python3 scripts/lunar.py YYYY MM DD`
- 例如：`python3 scripts/lunar.py 2026 2 26` → 输出"正月初十"

## 脚本说明

### 核心脚本
- `scripts/parse_news.py` - 解析当前脚本主源 HTML（默认 hex2077.dev）
- `scripts/aihot_fetcher.py` - 直接抓取并解析 AI HOT
- `scripts/aihot_parser.py` - 解析 AI HOT 纯文本输出
- `scripts/merge_sources.py` - 合并脚本主源与 AI HOT
- `scripts/rss_fetcher.py` - RSS新闻获取引擎
- `scripts/arxiv_fetcher.py` - arXiv论文获取器（Top 3）
- `scripts/dedupe.py` - 新闻去重工具
- `scripts/lunar.py` - 农历日期计算

### 测试命令
```bash
# 测试RSS获取（原文模式）
python3 scripts/rss_fetcher.py english --no-translation

# 测试中文备用源
python3 scripts/rss_fetcher.py chinese

# 测试arXv获取
python3 scripts/arxiv_fetcher.py

# 测试所有RSS源
python3 scripts/rss_fetcher.py --test

# 完整流程测试（手动触发）
python3 scripts/parse_news.py 2026-03-16 > /tmp/chinese.json
python3 scripts/rss_fetcher.py english --no-translation > /tmp/english.json
python3 scripts/arxiv_fetcher.py > /tmp/arxiv.json
```

## 定时任务

- **执行时间**: 每日10:55 (UTC+8)
- **定时配置**: 由宿主环境的 cron 或 scheduler 自行维护
