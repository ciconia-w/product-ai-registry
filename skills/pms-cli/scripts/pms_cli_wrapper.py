#!/usr/bin/env python3
"""
PMS CLI Wrapper - 为 Claude 提供的 PMS CLI 包装器

提供简化的 Python API 来调用 pms_cli.py 的功能
"""

import subprocess
import json
import sys
import os
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime


try:
    from pms_login import PMSOneClickLogin, interactive_login
    LOGIN_MODULE_AVAILABLE = True
except ImportError:
    LOGIN_MODULE_AVAILABLE = False


@dataclass
class PMSConfig:
    """PMS 配置类"""
    base_url: str
    cookie: Optional[str] = None
    cookie_file: Optional[str] = None
    
    def validate(self):
        """验证配置是否有效"""
        if not self.base_url:
            raise ValueError("base_url 是必需的")
        if not self.cookie and not self.cookie_file:
            raise ValueError("需要提供 cookie 或 cookie_file 进行认证")


@dataclass
class TaskInfo:
    """任务信息"""
    project_id: str
    task_name: str
    task_type: str = "devel"
    description: str = ""
    assignee: str = ""
    estimate_hours: str = ""
    start_date: str = ""
    deadline: str = ""
    uid: str = ""


@dataclass
class StoryInfo:
    """需求信息"""
    product_id: str
    story_title: str
    specification: str = ""
    verification: str = ""
    assignee: str = ""
    estimate_hours: str = ""
    uid: str = ""


@dataclass
class ProductInfo:
    """产品信息"""
    product_name: str
    product_code: str
    description: str = ""
    uid: str = ""


class PMSClient:
    """PMS CLI 客户端，支持一键登录"""
    
    def __init__(self, config: Optional[PMSConfig] = None, cli_path: Optional[str] = None, 
                 auto_login: bool = False, base_url: Optional[str] = None):
        """
        初始化 PMS 客户端
        
        Args:
            config: PMSConfig 配置对象（可选，如果启用自动登录）
            cli_path: pms_cli.py 的路径
            auto_login: 是否启用自动登录（当没有有效 session 时自动触发）
            base_url: 基础 URL（用于自动登录）
        """
        self.auto_login = auto_login
        self.base_url = base_url or (config.base_url if config else None)
        
        if config is None:
            if auto_login and base_url and LOGIN_MODULE_AVAILABLE:
                config = self._auto_login(base_url)
            else:
                raise ValueError("需要提供 config 或启用 auto_login 并提供 base_url")
        
        self.config = config
        self.config.validate()
        
        if cli_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.cli_path = os.path.join(script_dir, "pms_cli.py")
        else:
            self.cli_path = cli_path
        
        if not os.path.exists(self.cli_path):
            raise FileNotFoundError(f"找不到 pms_cli.py: {self.cli_path}")
    
    def _auto_login(self, base_url: str) -> PMSConfig:
        """自动登录获取 session"""
        if not LOGIN_MODULE_AVAILABLE:
            raise RuntimeError("一键登录模块不可用")
        
        login_manager = PMSOneClickLogin(base_url)
        # login(method="auto") 内部会自动处理 session 加载和过期检查
        session = login_manager.login(method="auto")
        
        if not session:
            raise RuntimeError("自动登录失败")
        
        cookie_str = login_manager.get_cookie_string()
        if not cookie_str:
            raise RuntimeError("无法获取登录 Cookie")
        
        return PMSConfig(base_url=base_url, cookie=cookie_str)
    
    def ensure_login(self) -> bool:
        """确保已登录，如果 session 过期则重新登录"""
        if not LOGIN_MODULE_AVAILABLE:
            return False
        
        login_manager = PMSOneClickLogin(self.config.base_url)
        # login(method="auto") 会检查 session，失效则触发一键登录
        session = login_manager.login(method="auto")
        
        if session:
            cookie_str = login_manager.get_cookie_string()
            if cookie_str:
                self.config.cookie = cookie_str
                return True
        
        return False
    
    def _build_base_args(self) -> List[str]:
        """构建基础命令参数"""
        args = [
            sys.executable,
            self.cli_path,
            "--base-url", self.config.base_url
        ]
        
        if self.config.cookie:
            args.extend(["--cookie", self.config.cookie])
        elif self.config.cookie_file:
            args.extend(["--cookie-file", self.config.cookie_file])
        
        return args
    
    def _execute(self, args: List[str]) -> Dict[str, Any]:
        """执行 CLI 命令并返回结果"""
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip() or result.stdout.strip()
                raise RuntimeError(f"命令执行失败: {error_msg}")
            
            output = result.stdout.strip()
            if output:
                try:
                    return json.loads(output)
                except json.JSONDecodeError:
                    return {"_raw_output": output}
            
            return {}
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("命令执行超时")
        except Exception as e:
            raise RuntimeError(f"执行错误: {e}")
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """登录并获取会话"""
        args = self._build_base_args()
        args.extend([
            "login",
            "--username", username,
            "--password", password
        ])
        return self._execute(args)
    
    def get_my_tasks(self) -> List[Dict[str, Any]]:
        """获取分配给我的任务列表"""
        args = self._build_base_args()
        args.append("my-tasks")
        result = self._execute(args)
        return self._extract_list(result, ["tasks", "data", "results", "items", "list"])
    
    def get_my_bugs(self) -> List[Dict[str, Any]]:
        """获取分配给我的缺陷列表"""
        args = self._build_base_args()
        args.append("my-bugs")
        result = self._execute(args)
        return self._extract_list(result, ["bugs", "data", "results", "items", "list"])
    
    def get_my_stories(self) -> List[Dict[str, Any]]:
        """获取我的需求列表"""
        args = self._build_base_args()
        args.append("my-stories")
        result = self._execute(args)
        return self._extract_list(result, ["stories", "data", "results", "items", "list"])
    
    def list_products(self) -> List[Dict[str, Any]]:
        """获取产品列表"""
        args = self._build_base_args()
        args.append("list-products")
        result = self._execute(args)
        return self._extract_list(result, ["products", "data", "results", "items", "list"])
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """获取项目列表"""
        args = self._build_base_args()
        args.append("list-projects")
        result = self._execute(args)
        return self._extract_list(result, ["projects", "data", "results", "items", "list"])
    
    def get_bug_detail(self, bug_id: str) -> Dict[str, Any]:
        """获取 Bug 详情"""
        args = self._build_base_args()
        args.extend(["view-bug", "--bug_id", str(bug_id)])
        return self._execute(args)

    def get_task_detail(self, task_id: str) -> Dict[str, Any]:
        """获取任务详情"""
        args = self._build_base_args()
        args.extend(["view-task", "--task_id", str(task_id)])
        return self._execute(args)

    def add_task_comment(self, task_id: str, comment: str) -> Dict[str, Any]:
        """为任务添加备注"""
        args = self._build_base_args()
        args.extend(["add-task-comment", "--task_id", str(task_id), "--comment", comment])
        return self._execute(args)

    def add_bug_comment(self, bug_id: str, comment: str) -> Dict[str, Any]:
        """为问题单添加备注"""
        args = self._build_base_args()
        args.extend(["add-bug-comment", "--bug_id", str(bug_id), "--comment", comment])
        return self._execute(args)

    def add_story_comment(self, story_id: str, comment: str) -> Dict[str, Any]:
        """为需求添加备注"""
        args = self._build_base_args()
        args.extend(["add-story-comment", "--story_id", str(story_id), "--comment", comment])
        return self._execute(args)
    
    def _extract_list(self, result: Any, keys: List[str]) -> List[Dict[str, Any]]:
        """从结果中提取列表"""
        if isinstance(result, list):
            return result
        elif isinstance(result, dict):
            for key in keys:
                if key in result:
                    return result[key]
            return [result] if result else []
        return []
    
    def create_task(self, task: TaskInfo) -> Dict[str, Any]:
        """创建任务"""
        if not task.uid:
            task.uid = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        args = self._build_base_args()
        args.extend([
            "create-task",
            "--project_id", task.project_id,
            "--task_name", task.task_name,
            "--task_type", task.task_type,
        ])
        
        if task.description:
            args.extend(["--description", task.description])
        if task.assignee:
            args.extend(["--assignee", task.assignee])
        if task.estimate_hours:
            args.extend(["--estimate_hours", str(task.estimate_hours)])
        if task.start_date:
            args.extend(["--start_date", task.start_date])
        if task.deadline:
            args.extend(["--deadline", task.deadline])
        if task.uid:
            args.extend(["--uid", task.uid])
        
        return self._execute(args)
    
    def create_story(self, story: StoryInfo) -> Dict[str, Any]:
        """创建需求"""
        if not story.uid:
            story.uid = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        args = self._build_base_args()
        args.extend([
            "create-story",
            "--product_id", story.product_id,
            "--story_title", story.story_title,
        ])
        
        if story.specification:
            args.extend(["--specification", story.specification])
        if story.verification:
            args.extend(["--verification", story.verification])
        if story.assignee:
            args.extend(["--assignee", story.assignee])
        if story.estimate_hours:
            args.extend(["--estimate_hours", str(story.estimate_hours)])
        if story.uid:
            args.extend(["--uid", story.uid])
        
        return self._execute(args)
    
    def create_product(self, product: ProductInfo) -> Dict[str, Any]:
        """创建产品"""
        if not product.uid:
            product.uid = f"product_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        args = self._build_base_args()
        args.extend([
            "create-product",
            "--product_name", product.product_name,
            "--product_code", product.product_code,
        ])
        
        if product.description:
            args.extend(["--description", product.description])
        if product.uid:
            args.extend(["--uid", product.uid])
        
        return self._execute(args)
    
    def execute_batch(self, config_path: str) -> List[Dict[str, Any]]:
        """执行批量操作"""
        args = [
            sys.executable,
            self.cli_path,
            "--base-url", self.config.base_url,
            "--config", config_path
        ]

        if self.config.cookie:
            args.extend(["--cookie", self.config.cookie])
        elif self.config.cookie_file:
            args.extend(["--cookie-file", self.config.cookie_file])

        result = self._execute(args)

        if isinstance(result, list):
            return result
        return [result] if result else []

    def browse_by_search(self, product_id: str, query_id: str, branch: str = "0",
                         save_path: Optional[str] = None) -> Dict[str, Any]:
        """按已保存查询浏览需求

        Args:
            product_id: 产品 ID
            query_id: 已保存查询 ID (如 506)
            branch: 产品分支，默认 "0"
            save_path: 可选，将 HTML 保存到文件路径

        Returns:
            包含结果的字典，或 HTML 文件信息
        """
        args = self._build_base_args()
        args.extend([
            "browse-by-search",
            "--product_id", product_id,
            "--query_id", query_id,
            "--branch", branch,
        ])
        if save_path:
            args.extend(["--output", save_path])

        return self._execute(args)

    def list_saved_queries(self, module: str = "story",
                           query_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """列出可用的已保存查询

        Args:
            module: 模块类型: story/bug/task (默认 story)
            query_id: 可选参考查询 ID

        Returns:
            查询列表 [{"id": 506, "name": "控制中心需求池"}, ...]
        """
        args = self._build_base_args()
        args.extend([
            "list-saved-queries",
            "--module", module,
        ])
        if query_id:
            args.extend(["--query_id", query_id])

        result = self._execute(args)
        if isinstance(result, list):
            return result
        return result if isinstance(result, list) else []


def quick_query(base_url: str, cookie: str, query_type: str = "my-tasks") -> Union[List[Dict], Dict]:
    """快速查询函数"""
    config = PMSConfig(base_url=base_url, cookie=cookie)
    client = PMSClient(config)
    
    query_methods = {
        "my-tasks": client.get_my_tasks,
        "my-bugs": client.get_my_bugs,
        "my-stories": client.get_my_stories,
        "list-products": client.list_products,
        "list-projects": client.list_projects,
    }
    
    method = query_methods.get(query_type)
    if method:
        return method()
    else:
        raise ValueError(f"未知的查询类型: {query_type}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PMS CLI Wrapper")
    parser.add_argument("--base-url", required=True, help="PMS 基础 URL")
    parser.add_argument("--cookie", help="认证 Cookie")
    parser.add_argument("--cookie-file", help="Cookie 文件路径")
    parser.add_argument("--query", choices=["my-tasks", "my-bugs", "my-stories", "list-products", "list-projects"],
                       default="my-tasks", help="查询类型")
    
    args = parser.parse_args()
    
    try:
        result = quick_query(args.base_url, args.cookie or "", args.query)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
