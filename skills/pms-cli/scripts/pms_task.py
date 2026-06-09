import re


class TaskMixin:
    """Mixin class for task-related operations."""

    def create_task(self, project_id, task_type, task_name, description, assignee, estimate_hours, start_date, deadline, uid):
        """Create a task in a project."""
        path = f"/task-create-{project_id}.html"
        headers = {}
        body = {
        "project": project_id,
        "type": task_type,
        "module": "0",
        "name": task_name,
        "desc": description,
        "pri": "3",
        "assignedTo[]": assignee,
        "estimate": estimate_hours,
        "estStarted": start_date,
        "deadline": deadline,
        "status": "wait",
        "after": "toTaskList",
        "uid": uid,
    }
        return self._request("POST", path, headers=headers, body=body, content_type="application/x-www-form-urlencoded")

    def edit_task(self, task_id, task_name=None, description=None, assignee=None,
                  estimate_hours=None, start_date=None, deadline=None, pri=None):
        """Edit an existing task.

        Note: This method uses the ZenTao web interface form submission
        rather than a REST API, as ZenTao's API requires token authentication.

        Args:
            task_id: The task ID to edit
            task_name: New task name (optional)
            description: New task description (optional)
            assignee: New assignee username (optional)
            estimate_hours: New estimated hours (optional)
            start_date: New start date YYYY-MM-DD (optional)
            deadline: New deadline YYYY-MM-DD (optional)
            pri: New priority 1-4 (optional)

        Returns:
            Dict with result status
        """
        # First get current task details to preserve unchanged fields
        current = self.view_task(task_id)
        if not current:
            return {'status': 'error', 'message': 'Task not found or access denied'}

        path = f"/task-edit-{task_id}.html"

        # Build form data with current values as defaults
        body = {
            'id': task_id,
            'name': task_name if task_name is not None else current.get('name', ''),
            'desc': description if description is not None else current.get('desc', ''),
            'assignedTo[]': assignee if assignee is not None else current.get('assignedTo', ''),
            'estimate': estimate_hours if estimate_hours is not None else current.get('estimate', ''),
            'estStarted': start_date if start_date is not None else current.get('estStarted', ''),
            'deadline': deadline if deadline is not None else current.get('deadline', ''),
            'pri': pri if pri is not None else current.get('pri', '3'),
            'after': 'toTaskView',
        }

        try:
            result = self._request("POST", path, body=body,
                                  content_type="application/x-www-form-urlencoded")
            return {'status': 'success', 'task_id': task_id, 'result': result}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def view_task(self, task_id):
        """Fetch and parse task details from task view page.

        Extracts task information from the HTML response including:
        - name: Task name/title
        - desc: Task description (HTML cleaned)
        - type: Task type
        - pri: Priority
        - assignedTo: Assignee
        - estimate: Estimated hours
        - status: Task status

        Args:
            task_id: The task ID to fetch

        Returns:
            Dict with task details, or None if not found/unauthorized
        """
        path = f"/task-view-{task_id}.html"

        try:
            html = self._request("GET", path)

            # Check if redirected to login or not found
            if isinstance(html, str) and (re.search(r'<title[^>]*>.*登录.*</title>', html, re.IGNORECASE) or len(html) < 500):
                return None

            task = {'id': task_id}

            # Extract task name from title tag
            title_match = re.search(r'TASK#(\d+)\s+(.+?)\s*/', html)
            if title_match:
                task['name'] = title_match.group(2).strip()

            # Try alternative patterns for task name
            if not task.get('name'):
                title_match = re.search(r'<title[^>]*>#(\d+)\s*-\s*(.+?)\s*-\s*禅道</title>', html, re.DOTALL)
                if title_match:
                    task['name'] = title_match.group(2).strip()

            if not task.get('name'):
                h1_match = re.search(r'<h1[^>]*>(?:\s*查看任务\s*)?#\d+\s*-\s*(.+?)</h1>', html, re.DOTALL)
                if h1_match:
                    task['name'] = h1_match.group(1).strip()

            # Extract description from content div or article
            desc_patterns = [
                r'<div[^>]*class="[^"]*content[^"]*"[^>]*>(.*?)</div>',
                r'<article[^>]*>(.*?)</article>',
            ]

            for pattern in desc_patterns:
                desc_match = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
                if desc_match:
                    desc_html = desc_match.group(1)
                    # Convert HTML to readable text with proper paragraph structure
                    desc_text = self._html_to_text(desc_html)
                    if len(desc_text) > 20:
                        task['desc'] = desc_text
                        break

            # Extract other fields
            patterns = {
                'type': r'任务类型[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'pri': r'优先级[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'assignedTo': r'指派给[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'estimate': r'最初预计[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
                'status': r'状态[：:]\s*</td>\s*<td[^>]*>(.+?)</td>',
            }

            for field, pattern in patterns.items():
                match = re.search(pattern, html, re.DOTALL)
                if match:
                    value = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                    task[field] = value

            return task

        except Exception:
            return None

    def add_task_comment(self, task_id, comment):
        """Add a comment/remark to a task.

        Args:
            task_id: The task ID to comment on
            comment: The comment text

        Returns:
            Dict with status and result, or None on failure
        """
        path = f"/action-comment-task-{task_id}.html"

        try:
            result = self._request(
                "POST",
                path,
                body={"comment": comment},
                content_type="application/x-www-form-urlencoded"
            )
            return {"status": "success", "task_id": task_id, "result": result}
        except Exception as e:
            return {"status": "error", "task_id": task_id, "message": str(e)}

    def my_tasks(self):
        """List my tasks."""
        path = "/my-task.html"
        headers = {}
        return self._request("GET", path, headers=headers)
