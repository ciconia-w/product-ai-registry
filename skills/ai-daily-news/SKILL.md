---
name: ai-daily-news
description: 生成AI日报！自动抓取中英文AI新闻，Agent直接翻译英文内容，按中文65%/英文35%配比生成结构化日报，自动发送邮件。适合：AI日报、今日AI资讯、生成新闻日报、发送AI新闻、新闻汇总等场景。
---

# AI资讯日报生成

自动获取多源AI新闻、内容去重聚合、KOL动态追踪、产品思考撰写、定时邮件发送。

## 默认配置

- **收件人**: 通过环境变量 `EMAIL_RECIPIENT` 或宿主调用参数提供
- **发件人名称**: 可通过环境变量 `EMAIL_SENDER_NAME` 自定义
- **SMTP 配置**: 使用宿主环境中的 `SMTP_SERVER`、`SMTP_PORT`、`SMTP_USERNAME`、`SMTP_PASSWORD`

## 工作流程

### Step 1: 获取新闻源（原文模式）

```bash
# 中文主源（ai.hubtoday.app）
python3 scripts/parse_news.py YYYY-MM-DD > /tmp/chinese_news.json

# 中文备用源（仅主源失败时）
python3 scripts/rss_fetcher.py chinese > /tmp/chinese_fallback.json

# 英文源（原文，由Agent翻译）
python3 scripts/rss_fetcher.py english --no-translation > /tmp/english_news.json

# 研究源（arXiv Top 3）
python3 scripts/arxiv_fetcher.py > /tmp/arxiv_papers.json
```

**新闻源优先级：**
- 优先级1: ai.hubtoday.app（主要源，5大分类：产品更新、前沿研究、行业展望、开源项目、社媒分享）
- 优先级2: 量子位RSS（仅主源失败时fallback）

### Step 2: 内容配比与去重

```python
# 配比控制：中文65% / 英文35% / arXv Top 3（额外）
total = len(chinese_news) + len(english_news)
max_chinese = int(total * 0.65)
max_english = int(total * 0.35)

# 去重：使用 scripts/dedupe.py
# - 读取昨日历史（history/YYYY-MM-DD.json）
# - 跨语言关键词匹配去重
# - arXv论文基于ID去重（保留7天历史）
```

### Step 3: 翻译英文新闻

**由 Agent 直接翻译，不调用外部 API。**

Agent 获取英文原文后，自行翻译标题和内容摘要，保留原文标题和链接。

**翻译格式要求：**
- 中文标题（简练准确，AI术语专业）
- 中文内容摘要（200字以内）
- 保留原文标题（`原文:`）
- 保留链接（`链接:`）

### Step 4: 生成日报

**结构要求（纯文本，无Markdown）：**

1. 邮件标题：`【AI】X月XX日 AI资讯日报`（必须包含【AI】前缀）

2. 农历问候：使用 `python3 scripts/lunar.py YYYY MM DD`

3. 今日摘要（来源概述）

4. 🇨🇳 中文AI资讯（按5大分类+emoji标识）

5. 🇺🇸 英文AI资讯（中文翻译+原文+链接）

6. 💡 产品思考

**格式规范：**
- ❌ 禁用所有Markdown语法（#, **, -, >, ```等）
- ❌ 禁用无序列表（禁止 `- ` 开头的行）
- ✅ 中文新闻格式：每条新闻之间用空行分隔，标题用全角冒号结尾
  ```
  📰 产品与功能更新

  Seedance 2.0 API助力一键视频生成：Seedance 2.0 接口正式上线...

  阿里Qwen3.6-Plus正式发布：阿里重磅推出 Qwen3.6-Plus 模型...
  ```
- ✅ 英文新闻格式：
  ```
  【来源】中文标题
  中文摘要内容
  原文: English Title
  链接: https://...
  ```
- ✅ 使用emoji分类：📰产品、🔬研究、🏢行业、🔥开源、💬社媒
- ✅ 数字用千分位：400,000、24,000个

### Step 5: 发送邮件与保存

```bash
# 发送邮件（发件人名可选，正文仍为纯文本）
python3 scripts/send-email/run.py \
  "${EMAIL_RECIPIENT}" \
  "【AI】X月XX日 AI资讯日报" \
  "日报正文"

# 自定义发件人名称（可选）
EMAIL_SENDER_NAME='自定义名称' python3 scripts/send-email/run.py \
  "${EMAIL_RECIPIENT}" \
  "【AI】X月XX日 AI资讯日报" \
  "日报正文"

# 保存历史（自动清理>3天）
echo "{news_json}" > history/YYYY-MM-DD.json
```

## 新闻源架构

### 中文源
- **ai.hubtoday.app**（主源）: https://ai.hubtoday.app/YYYY-MM/YYYY-MM-DD/
- **量子位**（备用）: https://www.qbitai.com/feed

### 英文源
- MIT Technology Review: https://www.technologyreview.com/feed/
- AI News: https://www.artificialintelligence-news.com/feed/
- MIT News AI: https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml

### 研究源
- arXiv AI: http://export.arxiv.org/rss/cs.AI（取Top 3）

详细配置见 `references/config.md`

## 使用示例

```
用户："生成今天的AI日报"
→ 执行Step 1-5完整流程
→ 发送到 `${EMAIL_RECIPIENT}`

用户："发送AI资讯"
→ 同上

用户："翻译这段英文"
→ 直接用GLM翻译，不调用脚本
```

## 错误处理

- ai.hubtoday.app失败 → 自动fallback到量子位
- arXv网络超时 → 跳过该源，继续生成日报
- 邮件发送失败 → 保存日报到文件，记录错误日志

## KOL追踪

只记录有实质内容的动态（@OpenAI, @AnthropicAi, @GoogleDeepMind, @sama, @karpathy等）
