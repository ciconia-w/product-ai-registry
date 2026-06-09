---
name: pms-cli
description: 通过自然语言对话调用和执行 PMS CLI (pms_cli.py) 工具，用于与 ZenTao PMS 系统交互。当用户提到"PMS"、"禅道"、"任务"、"bug"、"产品"、"项目"、"需求"、"story"、"查询任务"、"创建任务"、"查看bug"、"添加备注"、"问题单备注"、"列出产品"、"搜索查询"、"bySearch"、"已保存查询"、"控制中心需求池"、"列表查询"、"保存的查询"等关键词时，或者用户想要自动化操作 ZenTao PMS 系统、批量处理 PMS 数据、查询或修改 PMS 中的任务/缺陷/需求/项目时，使用此 skill。支持单次操作和批量操作两种模式，支持任务、缺陷、产品、项目、需求等 20+ 种 API 操作。内置 pms_cli.py 和 Python 包装器，开箱即用。支持多种登录方式：Playwright 自动登录（推荐）、浏览器回调登录、手动 Cookie 登录；15分钟 Session 自动过期续期机制。
compatibility: Requires Python 3.7+. Required: beautifulsoup4. Optional: Playwright for automatic login, keyring for credential storage. Includes pms_cli.py, wrapper scripts, and multi-mode login module with automatic session management.
---

# PMS CLI Skill

通过自然语言与 ZenTao PMS (禅道) 系统进行交互的 CLI 工具。本 skill 包含完整的 pms_cli.py 实现、Python 包装器和多模式登录模块（支持 Playwright 自动登录、浏览器回调、手动 Cookie），开箱即用。

## 项目结构

```
pms-cli/
├── SKILL.md                          # 本文件（自然语言调度）
├── requirements.txt                  # Python 依赖清单
├── scripts/
│   ├── pms_cli.py                   # CLI 入口：argparse + dispatch + ZentaoClient 组装
│   ├── pms_client.py                # BaseClient：HTTP、Cookie、Session 管理
│   ├── pms_story.py                 # StoryMixin：需求 CRUD + 富文本排版
│   ├── pms_task.py                  # TaskMixin：任务 CRUD + 备注
│   ├── pms_bug.py                   # BugMixin：缺陷查看 + 备注
│   ├── pms_product.py               # ProductMixin：产品管理
│   ├── pms_project.py               # ProjectMixin：项目管理
│   ├── pms_search.py                # SearchMixin：bySearch 查询支持
│   ├── pms_utils.py                 # markdown_to_html + BatchRunner
│   ├── pms_cli_wrapper.py           # Python API 包装器（subprocess 调用）
│   └── pms_login.py                 # 一键登录模块
├── examples/
│   ├── example_batch_config.json    # 批量查询示例
│   └── example_create_config.json   # 批量创建示例
└── evals/
    └── evals.json                   # 测试用例
```

## 安装部署指南

### 前置条件

| 条件 | 说明 |
|------|------|
| **Python 3.7+** | 使用 dataclasses、f-string 等特性，低于 3.7 会语法报错 |
| **网络连通** | 可访问 ZenTao PMS 服务器（如 `https://pms.uniontech.com`） |
| **操作系统** | Linux / macOS / Windows 均支持 |

### 方式一：最小安装（核心功能）

仅安装必需依赖，支持所有 CLI 命令（需手动提供 Cookie 或使用浏览器回调登录）：

```bash
pip install -r requirements.txt
```

或者仅安装必需部分：

```bash
pip install beautifulsoup4
```

**能力范围**：
- 所有查询/创建/编辑/备注操作 ✓
- 手动 Cookie 登录 ✓
- 浏览器回调登录 ✓
- **Playwright 自动登录** ✗（需额外安装 playwright）

### 方式二：完整安装（推荐）

一键安装所有依赖，支持 Playwright 自动登录（无需手动复制 Cookie）：

```bash
pip install -r requirements.txt
playwright install chromium
playwright install-deps chromium
```

**注意**：`playwright install chromium` 和 `playwright install-deps chromium` 是两个独立步骤：
- `install chromium` — 下载约 300MB 的 Chromium 浏览器
- `install-deps chromium` — 安装系统级共享库（如 libnss3、libnspr4 等），内网环境需单独解决

### 方式三：内网/离线安装

在内网环境无法直接访问 PyPI 时使用。需要先在有网络的机器上准备离线包：

```bash
# 在有网络的机器上执行，下载所有依赖及其子依赖
mkdir pms-offline-packages
pip download -r requirements.txt -d pms-offline-packages
tar czf pms-offline-packages.tar.gz pms-offline-packages/

# 将压缩包传到内网机器，然后：
tar xzf pms-offline-packages.tar.gz
pip install --no-index --find-links=./pms-offline-packages -r requirements.txt
```

Playwright 浏览器二进制需要单独下载传输：
```bash
# 在有网络的机器上执行
playwright install chromium  # 下载到 ~/.cache/ms-playwright/
# 将 ~/.cache/ms-playwright/ 目录整体拷贝到内网机器的相同位置
```

### 依赖说明表

| 依赖 | 类型 | 用途 | 未安装时的回退 |
|------|------|------|---------------|
| `beautifulsoup4` | **必需** | `pms_search.py` 的 HTML 内容解析 | **无回退** — `list-saved-queries`、`browse-by-search` 功能不可用 |
| `playwright` | 推荐 | Playwright 自动登录（无头浏览器） | 自动降级为浏览器回调方式，需手动在浏览器中完成登录 |
| `chromium` 二进制 | 推荐 | Playwright 驱动的浏览器引擎 | 同上 |
| `keyring` | 可选 | 系统密钥环安全存储凭据 | 降级为明文文件存储 `~/.pms/.pms_session.json` |

### 验证安装

```bash
# 1. 验证 Python 版本 >= 3.7
python --version

# 2. 验证必需依赖
python -c "import bs4; print(f'beautifulsoup4 OK: {bs4.__version__}')"

# 3. 验证 CLI 帮助正常
python scripts/pms_cli.py --help

# 4. 验证搜索功能模块（依赖 bs4）
python -c "from pms_search import SearchMixin; print('SearchMixin OK')"

# 5. 如果安装了 Playwright，验证浏览器引擎
python -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"

# 6. 验证登录模块
python -c "from pms_login import PMSOneClickLogin; print('Login module OK')"
```

预期输出示例：
```
Python 3.12.3
beautifulsoup4 OK: 4.12.2
usage: pms_cli.py [-h] ...
SearchMixin OK
Playwright OK
Login module OK
```

## 核心功能

- **任务管理**: 查询我的任务、创建任务、查看任务详情、编辑任务、**添加任务备注**
- **缺陷管理**: 查询我的缺陷、查看缺陷详情、**添加问题单备注**
- **产品管理**: 列出产品、创建产品、浏览产品需求/缺陷
- **项目管理**: 列出项目、查看项目详情、查看项目任务
- **需求管理**: 列出需求、创建需求、查看需求详情、编辑需求、**添加需求备注**
- **批量操作**: 支持 JSON 配置文件批量执行多个操作
- **Session 管理**: 15分钟自动过期、活跃自动续期、无需手动传 cookie
- **多模式登录**: 
  - **Playwright 自动登录** (推荐): 完全自动化，支持无头模式
  - **浏览器回调**: 传统方式，自动捕获浏览器 Cookie
  - **手动 Cookie**: 使用已有的 Cookie 字符串

## 快速开始

### 方式一：Playwright 自动登录（推荐）

完全自动化的登录方式，无需手动操作浏览器：

```bash
# 使用 Playwright 自动登录（无头模式）
python scripts/pms_login.py \
  --method playwright \
  --username ut000508 \
  --password xxxxxx

# 或使用有头模式（显示浏览器窗口）
python scripts/pms_login.py \
  --method playwright \
  --username ut000508 \
  --password xxxxxx \
  --no-headless
```

```python
from pms_login import PMSOneClickLogin

# Playwright 自动登录
login_manager = PMSOneClickLogin("https://pms.uniontech.com")
session = login_manager.login(
    method="playwright",
    username="ut000508",
    password="xxxxxx",
    headless=True  # 无头模式
)

# 获取 Cookie 字符串
cookie_str = login_manager.get_cookie_string()
print(f"Cookie: {cookie_str}")
```

### 方式二：自动模式（智能选择）

自动选择最佳登录方式：优先使用已保存 session → Playwright → 浏览器回调：

```bash
# 自动模式（如果提供了用户名密码，会尝试 Playwright）
python scripts/pms_login.py \
  --method auto \
  --username ut000508 \
  --password xxxxxx

# 纯自动模式（仅检查已保存 session，失败则使用浏览器回调）
python scripts/pms_login.py --method auto
```

```python
from pms_cli_wrapper import PMSClient

# 自动登录 - 智能选择最佳方式
client = PMSClient(auto_login=True, base_url="https://pms.uniontech.com")

# 现在可以直接使用
tasks = client.get_my_tasks()
print(f"你有 {len(tasks)} 个任务")
```

### 方式三：浏览器回调登录（传统方式）

适合已登录浏览器的场景：

```bash
# 启动浏览器回调登录
python scripts/pms_login.py --method browser

# 登录成功后，会显示 Cookie 字符串，可直接使用
python scripts/pms_cli.py my-tasks \
  --base-url https://pms.uniontech.com \
  --cookie "zentaosid=xxx..."
```

### 方式二：使用 Python API

```python
# 从 skill 目录导入
import sys
sys.path.insert(0, 'scripts')
from pms_cli_wrapper import PMSClient, PMSConfig, TaskInfo

# 配置认证信息
config = PMSConfig(
    base_url="https://pms.uniontech.com",
    cookie="zentaosid=YOUR_SESSION_ID"
)

# 创建客户端
client = PMSClient(config)

# 查询我的任务
tasks = client.get_my_tasks()
print(f"Found {len(tasks)} tasks")

# 创建任务
task = TaskInfo(
    project_id="123",
    task_name="实现登录功能",
    task_type="devel",
    assignee="zhangsan",
    estimate_hours="8"
)
result = client.create_task(task)
print(f"Created task: {result}")
```

### 方式三：直接执行 CLI 命令

```bash
# 使用包装器
python scripts/pms_cli_wrapper.py \
  --base-url https://pms.uniontech.com \
  --cookie "zentaosid=YOUR_SESSION_ID" \
  --query my-tasks

# 或直接使用 pms_cli.py
python scripts/pms_cli.py \
  my-tasks \
  --base-url https://pms.uniontech.com \
  --cookie "zentaosid=YOUR_SESSION_ID"
```

### 方式四：批量操作

```bash
python scripts/pms_cli.py \
  --config examples/example_batch_config.json \
  --base-url https://pms.uniontech.com \
  --cookie "zentaosid=YOUR_SESSION_ID"
```

## 登录方式详解

### 方式一：Playwright 自动登录（推荐）

使用 Playwright 自动化浏览器完成登录，完全无需人工干预。

#### 特点
- ✅ 完全自动化，无需手动操作
- ✅ 可获取完整 cookies（包括 httpOnly）
- ✅ 支持无头模式（后台运行）
- ✅ 支持有头模式（可视化调试）
- ⚠️ 需要安装 Playwright: `pip install playwright && playwright install chromium && playwright install-deps chromium`

#### 工作原理
1. Playwright 启动浏览器（Chromium）
2. 自动访问 PMS 登录页
3. 自动填写用户名密码
4. 自动提交登录表单
5. 等待登录成功，获取所有 cookies
6. 保存 session 供后续使用

#### Python API

```python
from pms_login import PMSOneClickLogin

login_manager = PMSOneClickLogin("https://pms.uniontech.com")

# Playwright 自动登录（无头模式）
session = login_manager.login(
    method="playwright",
    username="ut000508",
    password="your_password",
    headless=True
)

# 获取 Cookie 字符串
cookie_str = login_manager.get_cookie_string()
print(f"Cookie: {cookie_str}")
```

#### 命令行

```bash
# Playwright 自动登录（无头模式）
python scripts/pms_login.py \
  --method playwright \
  --username ut000508 \
  --password your_password

# Playwright 自动登录（有头模式，显示浏览器）
python scripts/pms_login.py \
  --method playwright \
  --username ut000508 \
  --password your_password \
  --no-headless
```

---

### 方式二：浏览器回调登录

基于 OAuth 2.0 风格的本地回调机制，适合已登录浏览器的场景。

#### 特点
- ✅ 无需安装额外依赖
- ✅ 可利用浏览器已保存的密码
- ⚠️ 需要用户手动完成登录
- ⚠️ 依赖回调机制，可能超时

#### 工作原理
1. 启动本地 HTTP 服务器
2. 打开系统默认浏览器访问 PMS 登录页
3. 用户在浏览器中完成登录
4. 登录成功后回调到本地服务器
5. 捕获 Cookie 并保存

#### Python API

```python
from pms_login import PMSOneClickLogin

login_manager = PMSOneClickLogin("https://pms.uniontech.com")
session = login_manager.login(method="browser", timeout=120)
```

#### 命令行

```bash
python scripts/pms_login.py --method browser
```

---

### 方式三：自动模式（智能选择）

自动选择最佳登录方式：
1. 优先检查已保存的有效 session
2. 如有用户名密码，尝试 Playwright
3. 回退到浏览器回调方式

#### Python API

```python
from pms_login import PMSOneClickLogin

login_manager = PMSOneClickLogin("https://pms.uniontech.com")

# 自动模式（提供用户名密码时会尝试 Playwright）
session = login_manager.login(
    method="auto",
    username="ut000508",
    password="your_password",
    headless=True
)
```

#### 命令行

```bash
# 自动模式
python scripts/pms_login.py --method auto

# 自动模式（带用户名密码）
python scripts/pms_login.py \
  --method auto \
  --username ut000508 \
  --password your_password
```

---

### Session 管理

登录成功后，session 会自动保存到 `~/.pms/.pms_session.json`，包含：
- `base_url`: PMS 地址
- `cookies`: 认证 Cookie（包括 httpOnly）
- `login_time`: 登录时间
- `expires_at`: 过期时间（默认8小时）
- `method`: 登录方式（playwright/browser）

下次使用时，如果 session 未过期，会自动复用。

```bash
# 查看已保存的 session
python scripts/pms_login.py --show

# 清除 session
python scripts/pms_login.py --clear
```

### 在 PMSClient 中使用

```python
from pms_cli_wrapper import PMSClient

# 启用自动登录（智能选择最佳方式）
client = PMSClient(auto_login=True, base_url="https://pms.uniontech.com")

# 如果 session 过期，会自动触发重新登录
# 也可以手动检查
check = client.ensure_login()
```

## 使用方法

### 1. 认证方式

**方式一：Playwright 自动登录（推荐）**

完全自动化，无需手动复制 Cookie：

```python
from pms_login import PMSOneClickLogin

login_manager = PMSOneClickLogin("https://pms.uniontech.com")
session = login_manager.login(
    method="playwright",
    username="ut000508",
    password="your_password",
    headless=True
)
cookie_str = login_manager.get_cookie_string()
```

**方式二：使用 Cookie 字符串**

从浏览器开发者工具复制 Cookie：
```
--cookie "zentaosid=YOUR_SESSION_ID; device=desktop; lang=zh-cn"
```

**方式三：使用 Cookie 文件**
```
--cookie-file /path/to/captured_cookies.json
```

**方式四：环境变量**
```bash
export PMS_BASE_URL="https://pms.uniontech.com"
```

### 2. Python API 详细使用

#### 初始化客户端

```python
from pms_cli_wrapper import PMSClient, PMSConfig

config = PMSConfig(
    base_url="https://pms.uniontech.com",
    cookie="zentaosid=YOUR_SESSION_ID"
)
client = PMSClient(config)
```

#### 查询操作

```python
# 获取我的任务
tasks = client.get_my_tasks()
for task in tasks:
    print(f"Task: {task.get('name')} - Status: {task.get('status')}")

# 获取我的缺陷
bugs = client.get_my_bugs()

# 获取我的需求
stories = client.get_my_stories()

# 列出所有产品
products = client.list_products()

# 列出所有项目
projects = client.list_projects()

# 列出可用的已保存搜索查询
queries = client.list_saved_queries(module="story")
print(f"找到 {len(queries)} 个已保存查询")
for q in queries:
    print(f"  [{q['id']}] {q['name']}")

# 按已保存查询浏览需求（如 query_id=506 为"控制中心需求池"）
result = client.browse_by_search(product_id="493", query_id="506")
print(f"查询结果: {result}")
# 也可以保存 HTML 到文件
result = client.browse_by_search(product_id="493", query_id="506", save_path="/tmp/search_result.html")
```

#### 创建操作

```python
from pms_cli_wrapper import TaskInfo, StoryInfo, ProductInfo

# 创建任务
task = TaskInfo(
    project_id="123",
    task_name="实现登录功能",
    task_type="devel",  # devel, test, design, study, discuss, ui, affaire, misc
    description="详细描述...",
    assignee="zhangsan",
    estimate_hours="8",
    start_date="2026-05-07",
    deadline="2026-05-14"
)
result = client.create_task(task)

# 创建需求
story = StoryInfo(
    product_id="456",
    story_title="用户登录优化",
    specification="作为用户，我希望...",
    verification="验收标准...",
    assignee="lisi",
    estimate_hours="16"
)
result = client.create_story(story)

  # 编辑需求
  result = client.edit_story(
      story_id="40965",
      title="更新后的标题",
      specification="<h3>描述</h3><p>新的需求描述</p>",
      verification="<ol><li>验收标准1</li></ol>",
      assignee="zhangsan",
      pri="2"
  )

# 创建产品
product = ProductInfo(
    product_name="新产品",
    product_code="NEW_PROD",
    description="产品描述..."
)
result = client.create_product(product)
```

#### 批量操作

```python
# 创建批量配置
from pms_cli_wrapper import create_batch_config
import json

config = create_batch_config(
    base_url="https://pms.uniontech.com",
    cookie="zentaosid=YOUR_SESSION_ID",
    operations=[
        {"action": "my_tasks"},
        {"action": "list_products"},
        {
            "action": "create_task",
            "params": {
                "project_id": "123",
                "task_name": "批量创建的任务",
                "task_type": "devel"
            }
        }
    ]
)

# 保存配置
with open('batch_config.json', 'w') as f:
    json.dump(config, f, indent=2)

# 执行批量操作
results = client.execute_batch('batch_config.json')
```

### 3. CLI 命令参考

#### 认证
- `login` - 登录并获取会话

#### 任务相关
- `my-tasks` - 列出分配给我的任务
- `create-task` - 创建新任务
  - 参数: `--project_id`, `--task_name`, `--task_type`, `--description`, `--assignee`, `--estimate_hours`, `--start_date`, `--deadline`, `--uid`
- `view-task` - 查看任务详情
  - 参数: `--task_id`
- `edit-task` - 编辑已有任务
  - 参数: `--task_id`, `--task_name`, `--description`, `--assignee`, `--estimate_hours`, `--start_date`, `--deadline`, `--pri`
- `add-task-comment` - **为任务添加备注**
  - 参数: `--task_id`, `--comment` (备注文本), `--file` (从文件读取备注)

#### 缺陷相关
- `my-bugs` - 列出分配给我的缺陷
- `view-bug` - 查看问题单详情
  - 参数: `--bug_id`
- `add-bug-comment` - **为问题单添加备注**
  - 参数: `--bug_id`, `--comment` (备注文本), `--file` (从文件读取备注)

#### 产品相关
- `list-products` - 列出所有产品
- `create-product` - 创建新产品
  - 参数: `--product_name`, `--product_code`, `--description`, `--uid`

#### 项目相关
- `list-projects` - 列出所有项目

#### 查询/搜索相关（新增）
- `browse-by-search` - **按已保存搜索查询浏览需求**
  - 参数: `--product_id`, `--query_id`, `--branch`（默认0）, `--output`（HTML保存路径）
  - 示例: `python scripts/pms_cli.py browse-by-search --product_id 493 --query_id 506`
- `list-saved-queries` - **列出可用的已保存搜索查询**
  - 参数: `--module`（默认story）, `--query_id`（可选参考ID）
  - 示例: `python scripts/pms_cli.py list-saved-queries --module story`
  - 输出: `[{"id": 506, "name": "控制中心需求池"}, ...]`

#### 需求相关
- `my-stories` - 列出我的需求
- `view-story` - 查看需求详情
  - 参数: `--story_id`
- `create-story` - 创建新需求
  - 参数: `--product_id`, `--story_title`, `--specification`, `--spec_file`, `--verification`, `--verify_file`, `--assignee`, `--estimate_hours`, `--uid`
- `edit-story` - 编辑已有需求
  - 参数: `--story_id`, `--story_title`, `--specification`, `--spec_file`, `--verification`, `--verify_file`, `--assignee`, `--pri`, `--estimate_hours`
- `add-story-comment` - **为需求添加备注**
  - 参数: `--story_id`, `--comment` (备注文本), `--file` (从文件读取备注)

## 工作流示例

### 查询任务列表

```python
# 用户说："帮我查一下我的任务"
from pms_cli_wrapper import PMSClient, PMSConfig

config = PMSConfig(
    base_url="https://pms.uniontech.com",
    cookie="zentaosid=YOUR_SESSION_ID"  # 从环境或配置文件获取
)
client = PMSClient(config)
tasks = client.get_my_tasks()

# 格式化输出
for task in tasks:
    print(f"- {task.get('name')} [{task.get('status')}] 指派给: {task.get('assignedTo')}")
```

### 创建任务

```python
# 用户说："创建一个开发任务，项目ID是123，任务名'实现登录功能'，指派给张三，预估8小时"
from pms_cli_wrapper import TaskInfo

task = TaskInfo(
    project_id="123",
    task_name="实现登录功能",
    task_type="devel",
    assignee="zhangsan",
    estimate_hours="8",
    start_date="2026-05-07",
    deadline="2026-05-14"
)
result = client.create_task(task)
print(f"任务创建成功: ID={result.get('id')}")
```

### 为问题单添加备注

```bash
# 用户说："给 bug 348299 加个备注，就说这个问题已经确认，下周修复"
python scripts/pms_cli.py add-bug-comment \
    --bug_id 348299 \
    --comment "📝 备注 (2026-05-18)：问题已确认，计划下周修复"

# 或者从文件读取长备注
python scripts/pms_cli.py add-bug-comment \
    --bug_id 348299 \
    --file remark.txt
```

### 为任务添加备注

```bash
# 用户说："给任务 389395 加个备注"
python scripts/pms_cli.py add-task-comment \
    --task_id 389395 \
    --comment "备注：已完成方案评审，待确认排期"

# 或者从文件读取长备注
python scripts/pms_cli.py add-task-comment \
    --task_id 389395 \
    --file remark.md
```

```python
# Python API
result = client.add_task_comment(task_id="389395", comment="备注内容")
```

### 为需求添加备注

```bash
# 用户说："给需求 40791 加个备注"
python scripts/pms_cli.py add-story-comment \
    --story_id 40791 \
    --comment "备注：已完成验收，存在部分遗留问题"
```

```python
# Python API
result = client.add_story_comment(story_id="40791", comment="备注内容")
```

### 批量操作配置

```json
{
  "base_url": "https://pms.uniontech.com",
  "cookie": "zentaosid=YOUR_SESSION_ID",
  "operations": [
    {
      "action": "my_tasks"
    },
    {
      "action": "list_products"
    },
    {
      "action": "add_bug_comment",
      "params": {
        "bug_id": "348299",
        "comment": "备注内容"
      }
    }
  ]
}
```

### 使用已保存搜索查询

利用 ZenTao 的 `bySearch-{queryID}` 接口浏览已保存搜索条件的结果：

```python
# 用户说："列出可用的已保存查询"
from pms_cli_wrapper import PMSClient, PMSConfig

config = PMSConfig(base_url="https://pms.uniontech.com", cookie="zentaosid=xxx")
client = PMSClient(config)

queries = client.list_saved_queries(module="story")
print(f"已保存查询 ({len(queries)}):")
for q in queries:
    print(f"  [{q['id']}] {q['name']}")
```

```bash
# CLI 方式列出已保存查询
python scripts/pms_cli.py list-saved-queries --module story

# 按已保存查询浏览需求（query_id=506 为"控制中心需求池"）
python scripts/pms_cli.py browse-by-search --product_id 493 --query_id 506

# 将结果保存到文件
python scripts/pms_cli.py browse-by-search --product_id 493 --query_id 506 --output /tmp/query_result.html
```

## 输出格式

所有 API 调用返回 Python 字典或列表：
- 成功：操作返回的数据结构
- 失败：抛出 RuntimeError 异常

CLI 命令返回 JSON 格式：
```json
{
  "id": 12345,
  "name": "任务名称",
  "status": "wait",
  "assignedTo": "zhangsan"
}
```

## 需求描述与验收标准排版建议

ZenTao 使用 KindEditor 富文本编辑器，支持 HTML 标记排版。建议 `specification` 和 `verification` 参数使用 HTML 标记排版以获得更好的阅读体验。

- 如果传入 Markdown 格式文本，CLI 会自动转换为 HTML
- 如果传入的文本已包含 HTML 标签（如 `<h3>`），CLI 会保持原样
- 也可以通过 `--spec-file` / `--verify-file` 从文件读取内容，`.md` 文件自动转 HTML，`.html` 文件直接使用

### 需求描述模板

````html
<h3>一、背景</h3>
<p>背景说明...</p>
<hr/>
<h3>二、需求描述</h3>
<p>需求描述...</p>
<h3>三、实现方案</h3>
<ol>
<li>方案一</li>
<li>方案二</li>
</ol>
<h3>四、影响范围</h3>
<ul>
<li>范围一</li>
</ul>
<h3>五、备注</h3>
<ul>
<li>备注信息</li>
</ul>
````

### 验收标准模板

````html
<ol>
<li><b>【标签】</b>验收内容</li>
<li><b>【标签】</b>验收内容</li>
</ol>
````

## 错误处理

```python
from pms_cli_wrapper import PMSClient, PMSConfig

try:
    config = PMSConfig(base_url="https://pms.uniontech.com", cookie="...")
    client = PMSClient(config)
    tasks = client.get_my_tasks()
except FileNotFoundError:
    print("错误: 找不到 pms_cli.py")
except ValueError as e:
    print(f"配置错误: {e}")
except RuntimeError as e:
    print(f"执行错误: {e}")
```

## 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| **401 Unauthorized** | Cookie 已过期 | 重新登录：`python scripts/pms_login.py --method playwright --username xxx --password xxx` |
| **403 Forbidden** | 权限不足或缺少 CSRF token | 检查账号权限，或使用 Playwright 登录获取完整 cookies |
| **404 Not Found** | 资源不存在 | 检查 ID 是否正确 |
| **Connection error** | 网络连接问题 | 检查 base URL 和网络连接 |
| **bs4/beautifulsoup4 not installed** | 未安装 beautifulsoup4 | 运行：`pip install beautifulsoup4` |
| **Playwright not installed** | 未安装 Playwright | 运行：`pip install playwright && playwright install chromium && playwright install-deps chromium` |
| **ImportError: No module named 'playwright'** | Playwright 未安装 | 同上（两步：pip 装包 + playwright install chromium） |
| **Browser engine error** | Chromium 浏览器二进制缺失 | 运行：`playwright install chromium && playwright install-deps chromium` |
| **Login timeout** | 浏览器回调超时 | 改用 Playwright 自动登录方式 |

## 自然语言对话示例

当用户使用以下方式提问时，使用本 skill 执行操作：

**用户**: "帮我查一下我在PMS上的任务"
**执行**: 
```python
from pms_cli_wrapper import PMSClient, PMSConfig
config = PMSConfig(base_url="...", cookie="...")
client = PMSClient(config)
tasks = client.get_my_tasks()
```

**用户**: "创建一个开发任务，项目ID是123，任务名称是'实现登录功能'，指派给张三，预估8小时"
**执行**:
```python
from pms_cli_wrapper import TaskInfo
task = TaskInfo(project_id="123", task_name="实现登录功能", 
                task_type="devel", assignee="张三", estimate_hours="8")
result = client.create_task(task)
```

**用户**: "列出所有产品"
**执行**:
```python
products = client.list_products()
```

**用户**: "帮我看看禅道上有哪些bug分配给我了"
**执行**:
```python
bugs = client.get_my_bugs()
```

**用户**: "给任务 389395 加个备注"
**执行**:
```python
result = client.add_task_comment(task_id="389395", comment="备注内容")
```

**用户**: "给需求 40791 加个备注"
**执行**:
```python
result = client.add_story_comment(story_id="40791", comment="备注内容")
```

## 集成建议

此 skill 适合集成到以下工作流：
- 每日任务报告自动生成
- 批量任务创建（从 Excel/CSV 导入）
- CI/CD 流水线中自动更新任务状态
- 与其他系统（如 GitLab、Jenkins）集成
- Slack/企微机器人集成

## 注意事项

1. **Cookie 有效期**: 会话 cookie 通常有有效期，过期后需要重新登录获取
2. **权限检查**: 某些操作（如创建产品）需要管理员权限
3. **参数完整性**: 创建操作需要完整的必填参数，否则操作会失败
4. **ID 格式**: 产品ID、项目ID等为数字字符串格式
5. **日期格式**: 使用 YYYY-MM-DD 格式
6. **Playwright 依赖**: 使用 Playwright 自动登录需两步安装：`pip install playwright && playwright install chromium && playwright install-deps chromium`
7. **登录方式选择**: 
   - 自动化场景（CI/CD）：使用 Playwright 自动登录
   - 交互式使用：使用浏览器回调或 Playwright 有头模式
   - 快速复用：使用已保存的 session（`--method manual`）
