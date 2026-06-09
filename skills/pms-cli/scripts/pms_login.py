#!/usr/bin/env python3
"""
PMS 一键登录模块

通过本地 HTTP 服务器监听登录回调，自动捕获 Cookie，
实现类似 OAuth 2.0 的一键登录体验。

工作流程：
1. 启动本地 HTTP 服务器监听 127.0.0.1:random_port
2. 打开系统浏览器访问 PMS 登录页面
3. 用户完成登录后，浏览器自动回调到本地服务器
4. 本地服务器捕获 Cookie 并保存
5. 后续 API 调用使用捕获的 Cookie
"""

import http.server
import socketserver
import webbrowser
import json
import os
import sys
import time
import threading
import urllib.parse
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class LoginCallbackHandler(http.server.BaseHTTPRequestHandler):
    """处理登录回调的 HTTP 处理器"""
    
    captured_cookies: Dict[str, Any] = {}
    login_success: bool = False
    server_ready: threading.Event = threading.Event()
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        """处理 GET 请求 - 捕获回调参数"""
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        path = parsed_path.path
        
        if path == '/callback':
            self._handle_callback(query_params)
        elif path == '/':
            self._handle_index()
        elif path == '/success':
            self._handle_success()
        else:
            self._send_404()
    
    def do_POST(self):
        """处理 POST 请求 - 接收 Cookie 数据"""
        parsed_path = urllib.parse.urlparse(self.path)
        
        if parsed_path.path == '/capture':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_data)
                self._capture_cookies(data)
                self._send_json_response({"status": "ok"})
            except json.JSONDecodeError:
                self._send_json_response({"status": "error", "message": "Invalid JSON"}, 400)
        else:
            self._send_404()
    
    def _handle_callback(self, params: Dict[str, list]):
        """处理 OAuth 回调"""
        code = params.get('code', [''])[0]
        state = params.get('state', [''])[0]
        error = params.get('error', [''])[0]
        
        if error:
            self._send_html_response(f"""
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h2 style="color: red;">登录失败</h2>
                <p>错误: {error}</p>
                <p>请关闭此窗口并重试。</p>
            </body>
            </html>
            """)
            LoginCallbackHandler.login_success = False
        elif code:
            LoginCallbackHandler.captured_cookies['auth_code'] = code
            LoginCallbackHandler.captured_cookies['state'] = state
            LoginCallbackHandler.login_success = True
            
            self._send_html_response(f"""
            <html>
            <head>
                <title>PMS 登录成功</title>
                <script>
                    // 尝试从浏览器获取 Cookie 并发送到本地服务器
                    async function captureAndRedirect() {{
                        try {{
                            // 获取所有可用的 cookies
                            const allCookies = document.cookie;
                            const cookieNames = ['zentaosid', 'csrftoken', 'lang', 'theme'];
                            const cookieData = {{}};

                            // 尝试解析 cookie 字符串
                            if (allCookies) {{
                                allCookies.split(';').forEach(cookie => {{
                                    const [name, value] = cookie.trim().split('=');
                                    if (name && value) {{
                                        cookieData[name] = value;
                                    }}
                                }});
                            }}

                            // 发送 cookie 数据到本地服务器
                            const response = await fetch('/capture', {{
                                method: 'POST',
                                headers: {{'Content-Type': 'application/json'}},
                                body: JSON.stringify({{
                                    cookies: allCookies,
                                    cookieData: cookieData,
                                    timestamp: new Date().toISOString(),
                                    userAgent: navigator.userAgent
                                }})
                            }});

                            if (!response.ok) {{
                                console.error('Failed to capture cookies:', response.status);
                            }}

                            // 等待一小段时间确保数据发送完成
                            await new Promise(resolve => setTimeout(resolve, 500));
                        }} catch (error) {{
                            console.error('Error capturing cookies:', error);
                        }} finally {{
                            // 无论成功与否都跳转到成功页面
                            window.location.href = '/success';
                        }}
                    }}

                    // 立即执行
                    captureAndRedirect();
                </script>
            </head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h2 style="color: green;">登录成功！</h2>
                <p>正在完成授权...</p>
                <p style="color: #666; font-size: 12px;">如果页面没有自动跳转，请<a href="/success">点击这里</a></p>
            </body>
            </html>
            """)
        else:
            self._send_html_response("""
            <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h2>无效的回调</h2>
                <p>缺少授权码参数。</p>
            </body>
            </html>
            """)
    
    def _handle_index(self):
        """处理首页请求"""
        self._send_html_response("""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2>PMS 登录服务</h2>
            <p>等待登录回调...</p>
        </body>
        </html>
        """)
    
    def _handle_success(self):
        """处理成功页面"""
        self._send_html_response("""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h2 style="color: green;">✓ 登录完成</h2>
            <p>您已成功登录 PMS 系统。</p>
            <p>可以关闭此窗口并返回终端。</p>
            <script>
                // 通知服务器可以关闭了
                fetch('/shutdown', {method: 'POST'});
            </script>
        </body>
        </html>
        """)
    
    def _capture_cookies(self, data: Dict[str, Any]):
        """捕获 Cookie 数据"""
        if 'cookies' in data:
            LoginCallbackHandler.captured_cookies['browser_cookies'] = data['cookies']
        if 'cookieData' in data:
            LoginCallbackHandler.captured_cookies['parsed_cookies'] = data['cookieData']
        if 'timestamp' in data:
            LoginCallbackHandler.captured_cookies['timestamp'] = data['timestamp']
        if 'userAgent' in data:
            LoginCallbackHandler.captured_cookies['user_agent'] = data['userAgent']
    
    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_html_response(self, html: str, status_code: int = 200):
        """发送 HTML 响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def do_OPTIONS(self):
        """处理预检请求"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_404(self):
        """发送 404 响应"""
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Not Found')


class CredentialManager:
    """凭证管理器 - 优先使用系统原生 Keyring，回退到本地文件"""
    
    def __init__(self, base_url: str, fallback_path: Path):
        self.base_url = base_url.rstrip('/')
        self.fallback_path = fallback_path
        self.service_name = "pms-cli-skill"
        self.account_name = self.base_url
        
        self.use_keyring = False
        try:
            import keyring
            # 检查是否有可用的后端
            if not isinstance(keyring.get_keyring(), keyring.backends.fail.Keyring):
                self.use_keyring = True
        except (ImportError, Exception):
            pass

    def save_session(self, session_data: Dict[str, Any]):
        """保存 Session"""
        session_str = json.dumps(session_data)
        success = False
        
        if self.use_keyring:
            try:
                import keyring
                keyring.set_password(f"{self.service_name}-session", self.account_name, session_str)
                success = True
            except Exception as e:
                print(f"  ! 写入 Keyring 失败: {e}，将回退到文件存储")
        
        # 无论 keyring 是否成功，都写入一份文件作为双保险/回退
        try:
            self.fallback_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.fallback_path, 'w', encoding='utf-8') as f:
                f.write(session_str)
            os.chmod(self.fallback_path, 0o600)
        except Exception as e:
            if not success:
                print(f"  ! 写入文件失败: {e}")

    def load_session(self) -> Optional[Dict[str, Any]]:
        """加载 Session"""
        # 1. 优先尝试从 Keyring 加载
        if self.use_keyring:
            try:
                import keyring
                session_str = keyring.get_password(f"{self.service_name}-session", self.account_name)
                if session_str:
                    return json.loads(session_str)
            except Exception:
                pass
        
        # 2. 回退到文件加载
        if self.fallback_path.exists():
            try:
                with open(self.fallback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return None

    def clear_session(self):
        """清除 Session"""
        if self.use_keyring:
            try:
                import keyring
                keyring.delete_password(f"{self.service_name}-session", self.account_name)
            except Exception:
                pass
        
        if self.fallback_path.exists():
            self.fallback_path.unlink()

    def save_password(self, username: str, password: str):
        """安全保存用户密码"""
        if self.use_keyring:
            try:
                import keyring
                keyring.set_password(f"{self.service_name}-auth", f"{self.base_url}:{username}", password)
                print(f"  ✓ 密码已安全存入系统凭证管理器")
            except Exception as e:
                print(f"  ! 无法保存密码到 Keyring: {e}")
        else:
            print("  ! 当前环境不支持原生凭证管理器，密码将不会被持久化保存")

    def get_password(self, username: str) -> Optional[str]:
        """获取已保存的密码"""
        if self.use_keyring:
            try:
                import keyring
                return keyring.get_password(f"{self.service_name}-auth", f"{self.base_url}:{username}")
            except Exception:
                pass
        return None


class PMSOneClickLogin:
    """PMS 一键登录管理器"""
    
    DEFAULT_PORT = 8765
    COOKIE_FILE = '.pms_session.json'
    
    def __init__(self, base_url: str, cookie_dir: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.port = self._find_free_port()
        self.redirect_uri = f"http://127.0.0.1:{self.port}/callback"
        
        if cookie_dir:
            self.cookie_path = Path(cookie_dir) / self.COOKIE_FILE
        else:
            self.cookie_path = Path.home() / '.pms' / self.COOKIE_FILE
            
        self.creds = CredentialManager(self.base_url, self.cookie_path)
    
    def _check_already_logged_in(self) -> Optional[Dict[str, Any]]:
        import urllib.request
        import http.cookiejar
        
        session = self.load_session()
        if not session:
            return None
        
        jar = http.cookiejar.CookieJar()
        cookies = session.get('cookies', {})
        
        if 'zentaosid' in cookies:
            cookie = http.cookiejar.Cookie(
                version=0, name='zentaosid', value=cookies['zentaosid'],
                port=None, port_specified=False,
                domain='', domain_specified=False,
                domain_initial_dot=False,
                path='/', path_specified=True,
                secure=False, expires=None,
                discard=True, comment=None,
                comment_url=None, rest={}, rfc2109=False
            )
            jar.set_cookie(cookie)
        
        try:
            opener = urllib.request.build_opener(
                urllib.request.HTTPCookieProcessor(jar)
            )
            opener.addheaders = [
                ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'),
            ]
            
            url = f"{self.base_url}/my-task.html"
            with opener.open(url, timeout=10) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
                
                if 'user-login' not in html and len(html) > 1000:
                    if '任务列表' in html or 'my-task' in html or 'zentaosid' in str(cookies):
                        return session
        except Exception:
            pass
        
        return None
    
    def _find_free_port(self) -> int:
        """查找可用端口"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def start_login_flow(self, timeout: int = 120) -> Optional[Dict[str, Any]]:
        existing_session = self._check_already_logged_in()
        if existing_session:
            print("✓ 检测到已登录的 session，直接使用")
            return existing_session
        
        LoginCallbackHandler.captured_cookies = {}
        LoginCallbackHandler.login_success = False
        LoginCallbackHandler.server_ready.clear()
        
        server = socketserver.TCPServer(('127.0.0.1', self.port), LoginCallbackHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"✓ 本地登录服务已启动: http://127.0.0.1:{self.port}")
        
        try:
            login_url = self._build_login_url()
            
            print(f"✓ 正在打开浏览器...")
            print(f"  登录地址: {login_url}")
            webbrowser.open(login_url)
            
            print(f"✓ 请在浏览器中完成登录...")
            print(f"  (超时时间: {timeout}秒)")
            
            start_time = time.time()
            while time.time() - start_time < timeout:
                if LoginCallbackHandler.login_success:
                    print("✓ 登录成功！")
                    
                    session_data = {
                        'base_url': self.base_url,
                        'cookies': LoginCallbackHandler.captured_cookies,
                        'login_time': datetime.now().isoformat(),
                        'last_used': datetime.now().isoformat(),
                        'ttl_minutes': 15
                    }
                    self._save_session(session_data)
                    
                    return session_data
                
                time.sleep(0.5)
            
            print("✗ 登录超时")
            return None
            
        finally:
            server.shutdown()
            server.server_close()
    
    def _build_login_url(self) -> str:
        """构建登录 URL"""
        params = {
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'state': self._generate_state()
        }
        query = urllib.parse.urlencode(params)
        return f"{self.base_url}/user-login.html?{query}"
    
    def _generate_state(self) -> str:
        """生成 state 参数（防 CSRF）"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _save_session(self, session_data: Dict[str, Any]):
        """保存 session"""
        self.creds.save_session(session_data)
        # print(f"✓ Session 已保存: {self.cookie_path}") # 信息已由 CredentialManager 处理

    def load_session(self, auto_refresh: bool = True) -> Optional[Dict[str, Any]]:
        """加载已保存的 session（15分钟 TTL）

        Args:
            auto_refresh: 是否自动更新 last_used 时间戳以延长 TTL
        """
        session = self.creds.load_session()
        if not session:
            return None

        # 检查是否过期（使用 last_used 或 login_time）
        timestamp = session.get('last_used') or session.get('login_time')
        if timestamp:
            try:
                last_time = datetime.fromisoformat(timestamp)
                elapsed = datetime.now() - last_time
                ttl_minutes = session.get('ttl_minutes', 15)

                if elapsed > timedelta(minutes=ttl_minutes):
                    print("✗ Session 已过期（15分钟有效期），需要重新登录")
                    return None
            except Exception:
                pass

        # 更新 last_used 时间戳以延长 TTL
        if auto_refresh:
            session['last_used'] = datetime.now().isoformat()
            self.creds.save_session(session)

        return session

    def get_cookie_string(self) -> Optional[str]:
        session = self.load_session()
        if not session:
            return None
        
        cookies = session.get('cookies', {})
        cookie_parts = []
        
        if 'zentaosid' in cookies:
            cookie_parts.append(f"zentaosid={cookies['zentaosid']}")
        
        if 'browser_cookies' in cookies:
            browser_cookies = cookies['browser_cookies']
            if isinstance(browser_cookies, str):
                for part in browser_cookies.split(';'):
                    part = part.strip()
                    if 'zentaosid' in part or 'csrftoken' in part:
                        if part not in cookie_parts:
                            cookie_parts.append(part)
            elif isinstance(browser_cookies, dict):
                for key, value in browser_cookies.items():
                    if 'zentaosid' in key or 'csrftoken' in key:
                        cookie_parts.append(f"{key}={value}")
        
        return '; '.join(cookie_parts) if cookie_parts else None

    def clear_session(self):
        self.creds.clear_session()
        print("✓ Session 已清除")
    
    def login_with_playwright(self, username: Optional[str] = None, password: Optional[str] = None, 
                               headless: bool = True) -> Optional[Dict[str, Any]]:
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            print("✗ Playwright 未安装，请先安装: pip install playwright")
            print("  然后运行: playwright install chromium")
            return None
        
        # 尝试从凭证管理器恢复密码
        if username and not password:
            password = self.creds.get_password(username)
            if password:
                print(f"  ✓ 已从系统凭证管理器自动获取密码")
        
        # 如果依然没有用户名密码，强制使用有头模式进行观察者模式登录
        is_observer_mode = not (username and password)
        if is_observer_mode:
            headless = False
            print("使用 Playwright 观察者模式（Watcher Mode）...")
            print("  请在弹出的浏览器窗口中手动完成登录")
        else:
            print(f"使用 Playwright 自动登录...")
            print(f"  用户名: {username}")
            print(f"  模式: {'无头' if headless else '有头'}")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context()
                page = context.new_page()
                
                print("  正在打开登录页面...")
                page.goto(f"{self.base_url}/user-login.html", wait_until="networkidle")
                
                if not is_observer_mode:
                    print("  填写登录表单...")
                    page.fill('input#account', username)
                    page.fill('input#password', password)
                    
                    print("  提交登录...")
                    page.click('input#submit')
                
                try:
                    # 等待登录成功的特征 URL，如果是观察者模式则不设超时
                    timeout = 0 if is_observer_mode else 10000
                    print(f"  等待登录成功 (检测到跳转至 /my/)...")
                    page.wait_for_url("**/my/**", timeout=timeout)
                    print("  ✓ 登录成功")
                    
                    # 登录成功后，如果是手动输入的密码，则保存到凭证管理器
                    if not is_observer_mode and username and password:
                        self.creds.save_password(username, password)
                        
                except Exception as e:
                    if not is_observer_mode:
                        error_msg = page.locator('.alert-danger').text_content(timeout=3000) or str(e)
                        print(f"  ✗ 登录失败: {error_msg}")
                    else:
                        print(f"  ✗ 观察者模式等待超时或中断: {e}")
                    browser.close()
                    return None
                
                # 关键：Playwright context.cookies() 可以获取所有 cookies，包括 HttpOnly
                cookies = context.cookies()
                browser.close()
                
                cookie_dict = {c['name']: c['value'] for c in cookies}
                
                session_data = {
                    'base_url': self.base_url,
                    'cookies': cookie_dict,
                    'login_time': datetime.now().isoformat(),
                    'last_used': datetime.now().isoformat(),
                    'ttl_minutes': 15,
                    'method': 'playwright_observer' if is_observer_mode else 'playwright'
                }
                
                self._save_session(session_data)
                print(f"  ✓ Session 已保存")
                
                return session_data
                
        except Exception as e:
            print(f"✗ Playwright 登录流程异常: {e}")
            return None
    
    def login(self, method: str = "auto", username: str = None, password: str = None, 
              headless: bool = True, timeout: int = 120) -> Optional[Dict[str, Any]]:
        if method == "auto":
            existing = self._check_already_logged_in()
            if existing:
                print("✓ 使用已保存的有效 session")
                return existing
            
            # 自动模式下，如果有用户名密码则尝试自动登录
            if username and password:
                print("尝试 Playwright 自动登录...")
                result = self.login_with_playwright(username, password, headless)
                if result:
                    return result
            
            # 否则检查是否安装了 Playwright，若有则尝试观察者模式（体验更好，且能穿透 HttpOnly）
            try:
                import playwright
                print("检测到 Playwright，尝试观察者模式登录（手动在浏览器操作）...")
                result = self.login_with_playwright(headless=False)
                if result:
                    return result
            except ImportError:
                pass
            
            print("回退至浏览器回调登录...")
            return self.start_login_flow(timeout)
        
        elif method == "playwright":
            # 如果提供了用户名密码则自动登录，否则进入观察者模式
            return self.login_with_playwright(username, password, headless)
        
        elif method == "browser":
            return self.start_login_flow(timeout)
        
        elif method == "manual":
            existing = self.load_session()
            if existing:
                return existing
            raise ValueError("手动模式需要预先保存的 session")
        
        else:
            raise ValueError(f"未知的登录方式: {method}")


def interactive_login(base_url: str = "https://pms.uniontech.com", method: str = "auto",
                       username: str = None, password: str = None, headless: bool = True):
    login_manager = PMSOneClickLogin(base_url)
    
    print(f"PMS 登录管理")
    print(f"目标: {base_url}")
    print(f"模式: {method}")
    print()
    
    if method == "auto":
        session = login_manager.login(method="auto", username=username, password=password, headless=headless)
    elif method == "playwright":
        if not username or not password:
            username = input("请输入用户名: ").strip()
            password = input("请输入密码: ").strip()
        session = login_manager.login(method="playwright", username=username, password=password, headless=headless)
    elif method == "browser":
        session = login_manager.login(method="browser")
    elif method == "manual":
        session = login_manager.login(method="manual")
    else:
        print(f"✗ 未知的登录方式: {method}")
        return None
    
    if session:
        cookie_str = login_manager.get_cookie_string()
        if cookie_str:
            print(f"\n✓ 登录成功！")
            print(f"  Cookie: {cookie_str[:50]}...")
            print(f"\n使用示例:")
            print(f"  python pms_cli.py my-tasks \\")
            print(f"    --base-url {base_url} \\")
            print(f"    --cookie \"{cookie_str}\"")
        return session
    else:
        print("\n✗ 登录失败")
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PMS 一键登录工具")
    parser.add_argument("--base-url", default="https://pms.uniontech.com",
                       help="PMS 基础 URL")
    parser.add_argument("--method", default="auto",
                       choices=["auto", "playwright", "browser", "manual"],
                       help="登录方式 (默认: auto)")
    parser.add_argument("--username", help="PMS 用户名 (Playwright 模式)")
    parser.add_argument("--password", help="PMS 密码 (Playwright 模式)")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Playwright 无头模式 (默认: True)")
    parser.add_argument("--no-headless", dest="headless", action="store_false",
                       help="Playwright 有头模式 (显示浏览器)")
    parser.add_argument("--clear", action="store_true",
                       help="清除已保存的 session")
    parser.add_argument("--show", action="store_true",
                       help="显示当前 session")
    
    args = parser.parse_args()
    
    if args.clear:
        login_manager = PMSOneClickLogin(args.base_url)
        login_manager.clear_session()
    elif args.show:
        login_manager = PMSOneClickLogin(args.base_url)
        # Load without auto-refresh to show actual remaining time
        session = login_manager.load_session(auto_refresh=False)
        if session:
            from datetime import datetime, timedelta

            timestamp = session.get('last_used') or session.get('login_time')
            ttl_minutes = session.get('ttl_minutes', 15)
            remaining = "未知"

            if timestamp:
                try:
                    last_time = datetime.fromisoformat(timestamp)
                    elapsed = datetime.now() - last_time
                    remaining_td = timedelta(minutes=ttl_minutes) - elapsed
                    if remaining_td.total_seconds() > 0:
                        mins = int(remaining_td.total_seconds() // 60)
                        secs = int(remaining_td.total_seconds() % 60)
                        remaining = f"{mins}分{secs}秒"
                    else:
                        remaining = "已过期"
                except Exception:
                    pass

            print(f"Session 信息:")
            print(f"  Base URL:  {session.get('base_url')}")
            print(f"  登录时间:  {session.get('login_time')}")
            print(f"  上次使用:  {session.get('last_used', session.get('login_time'))}")
            print(f"  TTL:       {ttl_minutes} 分钟")
            print(f"  剩余时间:  {remaining}")
            print(f"  登录方式:  {session.get('method', 'unknown')}")
            cookie_str = login_manager.get_cookie_string()
            if cookie_str:
                print(f"  Cookie:    {cookie_str[:50]}...")
        else:
            print("没有找到已保存的 session 或 session 已过期")
    else:
        interactive_login(
            args.base_url, 
            method=args.method,
            username=args.username,
            password=args.password,
            headless=args.headless
        )
