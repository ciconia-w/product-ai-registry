import re
from pms_utils import markdown_to_html


class StoryMixin:
    """Mixin class for story-related operations."""

    def list_product_stories(self):
        """List stories in a product."""
        path = f"/product-story-{product_id}.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def create_story(self, product_id, story_title, specification, verification, assignee, estimate_hours, uid, module="0"):
        """Create a story in a product."""
        path = f"/story-create-{product_id}.html"
        headers = {}
        body = {
        "product": product_id,
        "module": module,
        "plan": "",
        "source": "",
        "title": story_title,
        "spec": specification,
        "verify": verification,
        "pri": "3",
        "assignedTo": assignee,
        "estimate": estimate_hours,
        "uid": uid,
    }
        return self._request("POST", path, headers=headers, body=body, content_type="application/x-www-form-urlencoded")

    def view_story(self, story_id):
        """Fetch and parse story details from story view page.

        Args:
            story_id: The story ID to fetch

        Returns:
            Dict with story details, or None if not found/unauthorized
        """
        path = f"/story-view-{story_id}.html"

        try:
            html = self._request("GET", path)

            if isinstance(html, str) and (re.search(r'<title[^>]*>.*登录.*</title>', html, re.IGNORECASE) or len(html) < 500):
                return None

            story = {'id': story_id}

            # Extract title
            title_match = re.search(r"<title[^>]*>#\d+\s*-\s*(.+?)\s*-\s*禅道</title>", html, re.DOTALL)
            if title_match:
                story['title'] = title_match.group(1).strip()

            # Extract spec (需求描述)
            spec_match = re.search(
                r'<div class="detail-title">需求描述</div>\s*<div class="detail-content article-content">(.*?)</div>',
                html, re.DOTALL
            )
            if spec_match:
                story['spec'] = spec_match.group(1).strip()

            # Extract verify (验收标准)
            verify_match = re.search(
                r'<div class="detail-title">验收标准</div>\s*<div class="detail-content article-content">(.*?)</div>',
                html, re.DOTALL
            )
            if verify_match:
                story['verify'] = verify_match.group(1).strip()

            # Extract other fields from detail table
            field_patterns = {
                'product': r'所属产品[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'module': r'所属模块[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'plan': r'所属计划[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'source': r'来源[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'pri': r'优先级[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'assignedTo': r'指派给[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'estimate': r'预计工时[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'status': r'状态[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'keywords': r'关键词[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
            }

            for field, pattern in field_patterns.items():
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    value = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                    if value:
                        story[field] = value

            return story

        except Exception:
            return None

    def _get_story_edit_tokens(self, story_id):
        """Fetch lastEditedDate and uid from the story edit page.

        Returns:
            Tuple of (lastEditedDate, uid) strings
        """
        path = f"/story-edit-{story_id}.html"
        html = self._request("GET", path)

        last_edited = '0000-00-00 00:00:00'
        uid = ''

        m = re.search(r'name=["\x27]lastEditedDate["\x27][^>]*value=["\x27]([^"\x27]*)["\x27]', html)
        if m:
            last_edited = m.group(1)

        m = re.search(r'kuid\s*=\s*["\x27]([^"\x27]*)["\x27]', html)
        if m:
            uid = m.group(1)

        return last_edited, uid

    def edit_story(self, story_id, title=None, specification=None, verification=None,
                   assignee=None, estimate_hours=None, pri=None, module=None, plan=None):
        """Edit an existing story.

        Args:
            story_id: The story ID to edit (required)
            title: New title (optional)
            specification: New specification text (optional, Markdown or HTML)
            verification: New verification text (optional, Markdown or HTML)
            assignee: New assignee username (optional)
            estimate_hours: New estimated hours (optional)
            pri: New priority 1-4 (optional)
            module: New module ID (optional)
            plan: New plan ID (optional)

        Returns:
            Dict with result status
        """
        current = self.view_story(story_id)
        if not current:
            return {'status': 'error', 'message': 'Story not found or access denied'}

        last_edited, uid = self._get_story_edit_tokens(story_id)

        # Apply markdown_to_html to specification/verification
        spec = markdown_to_html(specification) if specification is not None else current.get('spec', '')
        verify = markdown_to_html(verification) if verification is not None else current.get('verify', '')

        body = {
            'uid': uid,
            'color': '',
            'title': title if title is not None else current.get('title', ''),
            'spec': spec,
            'verify': verify,
            'comment': '',
            'lastEditedDate': last_edited,
            'product': current.get('product', ''),
            'module': module if module is not None else current.get('module', '0'),
            'plan': plan if plan is not None else current.get('plan', ''),
            'rr[]': '',
            'ir[]': '',
            'sf[]': '',
            'source': current.get('source', ''),
            'sourceNote': '',
            'pri': pri if pri is not None else current.get('pri', '3'),
            'estimate': estimate_hours if estimate_hours is not None else current.get('estimate', ''),
            'keywords': current.get('keywords', ''),
            'assignedTo': assignee if assignee is not None else current.get('assignedTo', ''),
        }

        path = f"/story-edit-{story_id}.html"
        try:
            result = self._request("POST", path, body=body,
                                   content_type="application/x-www-form-urlencoded")
            return {'status': 'success', 'story_id': story_id, 'result': result}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def my_stories(self):
        """List my stories."""
        path = "/my-story.html"
        headers = {}
        return self._request("GET", path, headers=headers)

    def add_story_comment(self, story_id, comment):
        """Add a comment/remark to a story.

        Args:
            story_id: The story ID to comment on
            comment: The comment text

        Returns:
            Dict with status and result, or None on failure
        """
        path = f"/action-comment-story-{story_id}.html"

        try:
            result = self._request(
                "POST",
                path,
                body={"comment": comment},
                content_type="application/x-www-form-urlencoded"
            )
            return {"status": "success", "story_id": story_id, "result": result}
        except Exception as e:
            return {"status": "error", "story_id": story_id, "message": str(e)}
