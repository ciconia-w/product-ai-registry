import re


class BugMixin:
    """Mixin class for bug-related operations."""

    def view_bug(self, bug_id):
        """Fetch and parse bug details from bug view page.

        Args:
            bug_id: The bug ID to fetch

        Returns:
            Dict with bug details, or None if not found/unauthorized
        """
        path = f"/bug-view-{bug_id}.html"

        try:
            html = self._request("GET", path)

            # Check if redirected to login or not found
            if isinstance(html, str) and (re.search(r'<title[^>]*>.*登录.*</title>', html, re.IGNORECASE) or len(html) < 500):
                return None

            bug = {'id': bug_id}

            # Extract bug title
            title_patterns = [
                r'<span class="text" title="([^"]+)"',
                r'<span class="text" [^>]*title="([^"]+)"',
                r'<title[^>]*>(.+?)</title>',
            ]

            for pattern in title_patterns:
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if match:
                    title = match.group(1).strip()
                    # Remove " - 禅道" or similar if from <title>
                    title = re.sub(r'\s*-\s*禅道$', '', title)
                    title = re.sub(r'^BUG\s*#\d+\s*', '', title)
                    bug['title'] = title
                    break

            # Extract description from content div or article
            desc_patterns = [
                r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
                r'<article[^>]*>(.*?)</article>',
                r'<div[^>]*class="detail-content"[^>]*>(.*?)</div>'
            ]

            for pattern in desc_patterns:
                desc_match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if desc_match:
                    desc_html = desc_match.group(1)
                    desc_text = self._html_to_text(desc_html)
                    if len(desc_text) > 5:
                        bug['desc'] = desc_text
                        break

            # Extract other fields
            patterns = {
                'product': r'<th>所属产品</th>\s*<td>(.*?)</td>',
                'module': r'<th>所属模块</th>\s*<td[^>]*>(.*?)</td>',
                'type': r'<th>Bug类型</th>\s*<td>(.*?)</td>',
                'severity': r'<th>严重程度</th>\s*<td>\s*<span[^>]*data-severity=[\'"](\d+)[\'"]',
                'pri': r'<th>优先级</th>\s*<td>\s*<span[^>]*title=[\'"](\d+)[\'"]',
                'status': r'<th>Bug状态</th>\s*<td>(.*?)</td>',
                'assignedTo': r'<th>当前指派</th>\s*<td>(.*?)</td>',
                'openedBy': r'<th>由谁创建</th>\s*<td>(.*?)</td>',
                'resolvedBy': r'<th>由谁解决</th>\s*<td>(.*?)</td>',
                'resolution': r'<th>解决方案</th>\s*<td>(.*?)</td>',
                'os': r'<th>操作系统</th>\s*<td>(.*?)</td>',
                'browser': r'<th>浏览器</th>\s*<td>(.*?)</td>',
            }

            for field, pattern in patterns.items():
                match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if match:
                    value = self._html_to_text(match.group(1))
                    bug[field] = value

            return bug

        except Exception:
            return None

    def add_bug_comment(self, bug_id, comment):
        """Add a comment/remark to a bug.

        Args:
            bug_id: The bug ID to comment on
            comment: The comment text

        Returns:
            Dict with status and result, or None on failure
        """
        path = f"/action-comment-bug-{bug_id}.html"

        try:
            result = self._request(
                "POST",
                path,
                body={"comment": comment},
                content_type="application/x-www-form-urlencoded"
            )
            return {"status": "success", "bug_id": bug_id, "result": result}
        except Exception as e:
            return {"status": "error", "bug_id": bug_id, "message": str(e)}

    def my_bugs(self):
        """List my bugs."""
        path = "/my-bug.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def product_bugs(self):
        """List bugs in a product."""
        path = f"/product-bug-{product_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)
