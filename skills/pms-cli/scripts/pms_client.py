import http.cookiejar
import json
import os
import re
import textwrap
import urllib.error
import urllib.parse
import urllib.request


class BaseClient:
    """Zero-dependency HTTP client for the reverse-engineered API.

    Handles cookie management, CSRF tokens, and request execution
    using only Python stdlib (urllib + http.cookiejar).

    Args:
        base_url: Base URL of the target platform (e.g. https://pms.example.com).
        cookie_string: Raw Cookie header string (e.g. "sessionid=abc; csrftoken=xyz").
        cookie_file: Path to captured_cookies.json from the capture session.
    """

    def __init__(self, base_url, cookie_string=None, cookie_file=None):
        if not base_url:
            raise ValueError("base_url is required")
        self.base_url = base_url.rstrip('/')
        self.jar = http.cookiejar.CookieJar()

        if cookie_string:
            self._parse_cookie_string(cookie_string)
        if cookie_file:
            self._load_cookie_file(cookie_file)

        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar)
        )

    def _parse_cookie_string(self, cookie_string):
        """Parse a raw Cookie header string into the cookiejar.

        Handles simple key=value pairs separated by semicolons.
        """
        for part in cookie_string.split(';'):
            part = part.strip()
            if '=' in part:
                key, _, value = part.partition('=')
                key = key.strip()
                value = value.strip().strip('"')
                cookie = http.cookiejar.Cookie(
                    version=0, name=key, value=value,
                    port=None, port_specified=False,
                    domain='', domain_specified=False,
                    domain_initial_dot=False,
                    path='/', path_specified=True,
                    secure=False, expires=None,
                    discard=True, comment=None,
                    comment_url=None, rest={}, rfc2109=False
                )
                self.jar.set_cookie(cookie)

    def _load_cookie_file(self, cookie_file):
        """Load cookies from a session file or captured_cookies.json file.

        Supports two formats:
        1. PMSOneClickLogin session format:
           {"base_url": "...", "cookies": {"zentaosid": "..."}, "login_time": "...", "expires_at": "..."}
        2. CDP extraction format: list of cookie objects
        """
        with open(cookie_file, 'r') as f:
            data = json.load(f)

        # Handle PMSOneClickLogin session format
        if isinstance(data, dict) and 'cookies' in data:
            # Check session expiration (15 minutes from last use or login time)
            if not self._check_session_valid(data):
                raise RuntimeError("Session has expired. Please login again.")

            cookies_dict = data.get('cookies', {})
            domain = urllib.parse.urlparse(self.base_url).hostname or ''

            for name, value in cookies_dict.items():
                cookie = http.cookiejar.Cookie(
                    version=0, name=name, value=value,
                    port=None, port_specified=False,
                    domain='', domain_specified=False,
                    domain_initial_dot=False,
                    path='/', path_specified=True,
                    secure=False, expires=None,
                    discard=True, comment=None,
                    comment_url=None, rest={}, rfc2109=False
                )
                self.jar.set_cookie(cookie)

            # Update session last_used timestamp
            self._update_session_timestamp(cookie_file, data)
            return

        # Handle CDP extraction format (list of cookies)
        if isinstance(data, list):
            domain = urllib.parse.urlparse(self.base_url).hostname or ''

            for c in data:
                name = c.get('name', '')
                value = c.get('value', '')
                cookie_domain = c.get('domain', '')
                cookie_path = c.get('path', '/')
                secure = c.get('secure', False)
                http_only = c.get('httpOnly', False)
                expires = c.get('expires', None)
                same_site = c.get('sameSite', None)

                # Filter by domain if domain is specified in cookie
                if cookie_domain and domain:
                    cookie_domain_clean = cookie_domain.lstrip('.')
                    if not domain.endswith(cookie_domain_clean) and domain != cookie_domain_clean:
                        continue

                cookie = http.cookiejar.Cookie(
                    version=0, name=name, value=value,
                    port=None, port_specified=False,
                    domain=cookie_domain, domain_specified=bool(cookie_domain),
                    domain_initial_dot=cookie_domain.startswith('.') if cookie_domain else False,
                    path=cookie_path, path_specified=True,
                    secure=secure, expires=expires,
                    discard=False, comment=None,
                    comment_url=None, rest={'httpOnly': http_only, 'sameSite': same_site},
                    rfc2109=False
                )
                self.jar.set_cookie(cookie)

    def _check_session_valid(self, session_data):
        """Check if session is still valid (15 minutes TTL).

        Priority:
        1. Use last_used timestamp if available
        2. Fall back to login_time if last_used not available
        3. If neither available, consider valid (legacy format)
        """
        from datetime import datetime, timedelta

        SESSION_TTL_MINUTES = 15

        timestamp = session_data.get('last_used') or session_data.get('login_time')
        if not timestamp:
            return True

        try:
            last_time = datetime.fromisoformat(timestamp)
            elapsed = datetime.now() - last_time
            return elapsed < timedelta(minutes=SESSION_TTL_MINUTES)
        except (ValueError, TypeError):
            return True

    def _update_session_timestamp(self, cookie_file, session_data):
        """Update session last_used timestamp to extend TTL."""
        from datetime import datetime

        session_data['last_used'] = datetime.now().isoformat()
        session_data['ttl_minutes'] = 15  # Record the TTL setting

        try:
            with open(cookie_file, 'w') as f:
                json.dump(session_data, f, indent=2)
        except Exception:
            # Silent fail if write not permitted
            pass

    def _get_csrf_token(self):
        """Extract CSRF token from the cookie jar.

        Searches for known CSRF cookie names. Override in subclass
        or configure via the CSRF_COOKIE_NAME attribute.
        """
        csrf_names = ['csrftoken', 'XSRF-TOKEN', '_csrf', 'csrf_token',
                       'csrfmiddlewaretoken', 'authenticity_token']
        for cookie in self.jar:
            for name in csrf_names:
                if cookie.name.lower() == name.lower():
                    return cookie.value
        return None

    def _build_headers(self, extra=None):
        """Build request headers with CSRF token if available.

        Args:
            extra: Optional dict of additional headers to merge.
        """
        headers = {
            'User-Agent': 'PMS-CLI/1.0 (stdlib)',
            'Accept': 'application/json, text/plain, */*',
        }

        # Inject the CSRF header only when a mapping is defined
        if extra and isinstance(extra.get('__csrf_header__'), str):
            csrf_token = self._get_csrf_token()
            if csrf_token:
                csrf_header_name = extra.pop('__csrf_header__')
                if csrf_header_name not in headers:
                    headers[csrf_header_name] = csrf_token

        if extra:
            headers.update(extra)

        return headers

    def _request(self, method, path, headers=None, body=None, content_type=None, extra_headers=None):
        """Execute an HTTP request.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE).
            path: Request path (e.g. /api/v1/products/).
            headers: Dict of additional headers.
            body: Request body. If dict, encoded as JSON or form-urlencoded.
            content_type: Override Content-Type header.
            extra_headers: Additional headers to merge after build_headers.

        Returns:
            Parsed JSON response, or raw text if response is not JSON.

        Raises:
            urllib.error.HTTPError: On HTTP error responses.
            urllib.error.URLError: On connection errors.
        """
        url = self.base_url + path
        data = None

        if body is not None:
            if isinstance(body, dict):
                if content_type and 'x-www-form-urlencoded' in content_type:
                    data = urllib.parse.urlencode(body).encode('utf-8')
                else:
                    data = json.dumps(body).encode('utf-8')
                    if content_type is None:
                        content_type = 'application/json'
            elif isinstance(body, str):
                data = body.encode('utf-8')
            elif isinstance(body, bytes):
                data = body

        req_headers = self._build_headers(headers or {})
        if content_type:
            req_headers['Content-Type'] = content_type
        if extra_headers:
            req_headers.update(extra_headers)

        req = urllib.request.Request(
            url, data=data, headers=req_headers, method=method.upper()
        )

        try:
            with self.opener.open(req, timeout=30) as resp:
                raw = resp.read()
                try:
                    return json.loads(raw.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return raw.decode('utf-8', errors='replace')
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8', errors='replace')
            msg = f"HTTP {e.code} {e.reason} on {method} {url}: {error_body[:500]}"
            raise RuntimeError(msg) from e
        except urllib.error.URLError as e:
            raise RuntimeError(f"Connection error on {method} {url}: {e.reason}") from e

    def _html_to_text(self, html, width=80):
        """Convert HTML to readable plain text with proper paragraph structure."""
        if not html:
            return ""

        block_tags = ['p', 'div', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                      'li', 'tr', 'td', 'th', 'blockquote', 'pre']
        text = html

        for tag in block_tags:
            text = re.sub(rf'<{tag}[^>]*>\s*', '\n', text, flags=re.IGNORECASE)
            text = re.sub(rf'\s*</{tag}>\s*', '\n', text, flags=re.IGNORECASE)

        text = re.sub(r'<br\s*/?>\s*', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<li[^>]*>\s*', '\n• ', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)

        entities = [
            ('&nbsp;', ' '), ('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'),
            ('&quot;', '"'), ('&#39;', "'"), ('&hellip;', '...'),
            ('&mdash;', '—'), ('&ndash;', '-')
        ]
        for entity, char in entities:
            text = text.replace(entity, char)

        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                wrapped = textwrap.fill(line, width=width, break_long_words=False,
                                       replace_whitespace=True)
                cleaned_lines.append(wrapped)
            else:
                cleaned_lines.append('')

        text = '\n'.join(cleaned_lines)
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def login(self, username, password):
        """Authenticate with Zentao PMS.

        Submits credentials via AJAX-style POST. Returns JSON with
        {"result": "success", "locate": "..."} on success.
        On success, the zentaosid session cookie is stored in the jar.
        """
        body = {
            "account": username,
            "password": password,
            "passwordStrength": "1",
            "referer": "/my/",
            "verifyRand": "",
            "keepLogin": "1",
        }
        result = self._request("POST", "/user-login.html", body=body,
                               content_type="application/x-www-form-urlencoded",
                               extra_headers={"X-Requested-With": "XMLHttpRequest"})
        return result
