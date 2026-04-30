# AI资讯日报生成技能

自动获取多源AI新闻、内容去重聚合、生成结构化日报、发送邮件。

## 快速使用

```
用户: "生成今天的AI日报"
→ 自动执行完整流程
→ 发送到配置好的收件人地址（例如通过 `EMAIL_RECIPIENT` 提供）
```

## 核心脚本

| 脚本 | 用途 |
|------|------|
| `scripts/parse_news.py` | 解析 ai.hubtoday.app |
| `scripts/rss_fetcher.py` | RSS新闻获取 |
| `scripts/arxiv_fetcher.py` | arXiv论文 (Top 3) |
| `scripts/dedupe.py` | 新闻去重 |
| `scripts/lunar.py` | 农历计算 |

## 测试命令

```bash
# 测试英文RSS（原文）
python3 scripts/rss_fetcher.py english --no-translation

# 测试中文源
python3 scripts/parse_news.py 2026-04-24

# 测试arXiv
python3 scripts/arxiv_fetcher.py

# 测试农历
python3 scripts/lunar.py 2026 4 24
```

## 配置

- 收件人: 通过环境变量或宿主配置提供
- 配比: 中文65% / 英文35%
- 详细配置: `references/sources.yaml`

## 目录结构

```
ai-daily-news/
├── SKILL.md          # 技能说明
├── README.md         # 本文件
├── requirements.txt  # Python依赖
├── scripts/          # 核心脚本
├── references/       # 配置文件
├── history/          # 历史数据
└── archive/          # 归档文件
```
