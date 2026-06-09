import json
import re
import time


def markdown_to_html(text):
    """Convert common Markdown to HTML for ZenTao KindEditor.

    Supports: headings (#/##/###), bold (**), unordered/ordered lists,
    horizontal rules (---), blockquotes (>), and paragraphs.
    If the input already contains HTML tags, returns it as-is.
    """
    if not text:
        return text

    # If input already looks like HTML, return as-is
    if re.search(r'<[a-zA-Z]', text):
        return text

    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # Horizontal rule
        if re.match(r'^\s*---+\s*$', line):
            result.append('<hr/>')
            i += 1
            continue

        # Headings
        heading_match = re.match(r'^\s*(#{1,3})\s+(.+)$', line)
        if heading_match:
            level = len(heading_match.group(1))
            content = heading_match.group(2).strip()
            result.append(f'<h{level}>{content}</h{level}>')
            i += 1
            continue

        # Unordered list block
        if re.match(r'^\s*[-*+]\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\s*[-*+]\s+', lines[i]):
                item_content = re.sub(r'^\s*[-*+]\s+', '', lines[i])
                item_content = _md_inline(item_content)
                items.append(f'<li>{item_content}</li>')
                i += 1
            result.append('<ul>')
            result.extend(items)
            result.append('</ul>')
            continue

        # Ordered list block
        if re.match(r'^\s*\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\s*\d+\.\s+', lines[i]):
                item_content = re.sub(r'^\s*\d+\.\s+', '', lines[i])
                item_content = _md_inline(item_content)
                items.append(f'<li>{item_content}</li>')
                i += 1
            result.append('<ol>')
            result.extend(items)
            result.append('</ol>')
            continue

        # Blockquote
        bq_match = re.match(r'^\s*>\s*(.*)$', line)
        if bq_match:
            quote_lines = []
            while i < len(lines) and re.match(r'^\s*>\s*', lines[i]):
                quote_lines.append(re.sub(r'^\s*>\s*', '', lines[i]))
                i += 1
            result.append(f'<blockquote>{" ".join(quote_lines)}</blockquote>')
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph — collect consecutive non-blank, non-structural lines
        para_lines = []
        while i < len(lines):
            ln = lines[i]
            if not ln.strip():
                break
            if re.match(r'^\s*(#{1,3}\s+|[-*+]\s+|\d+\.\s+|>\s*|---+\s*$)', ln):
                break
            para_lines.append(ln)
            i += 1
        if para_lines:
            content = ' '.join(para_lines)
            result.append(f'<p>{_md_inline(content)}</p>')

    return '\n'.join(result)


def _md_inline(text):
    """Convert inline Markdown: **bold** → <b>bold</b>."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return text


class BatchRunner:
    """Execute batch operations from a JSON config file.

    Supports chaining operations via $prev.field syntax, conditional
    execution, retry logic, and loops.

    Usage:
        runner = BatchRunner(client)
        runner.run('batch_config.json')
    """

    def __init__(self, client):
        self.client = client
        self.last_result = None

    def _resolve_params(self, params):
        """Resolve $prev.field references using the last operation's result."""
        if not isinstance(params, dict):
            return params
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith('$prev'):
                parts = value.split('.', 1)
                if len(parts) == 2:
                    json_path = parts[1]
                    resolved[key] = self._get_json_path(self.last_result, json_path)
                elif len(parts) == 1:
                    resolved[key] = self.last_result
            elif isinstance(value, dict):
                resolved[key] = self._resolve_params(value)
            elif isinstance(value, list):
                resolved[key] = [
                    self._resolve_params(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                resolved[key] = value
        return resolved

    @staticmethod
    def _get_json_path(data, path):
        """Extract a value from nested JSON using dot-notation path.

        Args:
            data: JSON response (dict or list).
            path: Dot-separated path (e.g. 'id', 'data.results[0].id').
        """
        if data is None:
            return None
        parts = re.split(r'\.|\[|\]', path)
        parts = [p for p in parts if p]
        current = data
        for part in parts:
            try:
                idx = int(part)
                if isinstance(current, list):
                    current = current[idx]
                else:
                    current = current[part]
            except (ValueError, TypeError):
                if isinstance(current, dict):
                    current = current.get(part)
                else:
                    return None
            if current is None:
                return None
        return current

    def _check_condition(self, condition):
        """Evaluate a condition dict."""
        if not condition:
            return True
        ctype = condition.get('type', '')
        if ctype == 'skip_if_exists':
            check_action = condition.get('check_action')
            match_field = condition.get('match_field')
            match_value = condition.get('match_value')
            if check_action and match_field and match_value:
                method = getattr(self.client, check_action, None)
                if method:
                    try:
                        result = method()
                        if isinstance(result, list):
                            for item in result:
                                if item.get(match_field) == match_value:
                                    print(f"  [skip] {match_value} already exists")
                                    return False
                        elif isinstance(result, dict):
                            items = result.get('results', result.get('data', [result]))
                            if not isinstance(items, list):
                                items = [items]
                            for item in items:
                                if item.get(match_field) == match_value:
                                    print(f"  [skip] {match_value} already exists")
                                    return False
                    except Exception as e:
                        print(f"  [warn] Condition check failed: {e}")
        return True

    def _execute_with_retry(self, method, params, retry_config):
        """Execute a method with retry logic."""
        max_attempts = retry_config.get('max_attempts', 1)
        delay = retry_config.get('delay_seconds', 1)
        backoff = retry_config.get('backoff_multiplier', 1)

        last_error = None
        for attempt in range(max_attempts):
            try:
                return method(**params)
            except Exception as e:
                last_error = e
                if attempt < max_attempts - 1:
                    print(f"  [retry] Attempt {attempt+1} failed: {e}")
                    time.sleep(delay)
                    delay *= backoff
        raise last_error

    def run(self, config_path):
        """Execute batch operations from a JSON config file."""
        with open(config_path, 'r') as f:
            config = json.load(f)

        # Override base_url from config if provided
        cfg_base_url = config.get('base_url', '')
        if cfg_base_url and cfg_base_url != self.client.base_url:
            self.client.base_url = cfg_base_url.rstrip('/')

        # Load cookies from config if provided
        auth = config.get('auth', {})
        cookie_string = auth.get('cookie_string', '')
        cookie_file = auth.get('cookie_file', '')
        if cookie_string:
            self.client._parse_cookie_string(cookie_string)
        if cookie_file:
            self.client._load_cookie_file(cookie_file)

        operations = config.get('operations', [])
        results = []
        success_count = 0
        fail_count = 0

        for i, op_spec in enumerate(operations):
            # Handle loop blocks
            if 'loop' in op_spec:
                loop_spec = op_spec['loop']
                action = loop_spec.get('action', '')
                params_list = loop_spec.get('params_list', [])
                retry = loop_spec.get('retry', None)
                for params_set in params_list:
                    method = getattr(self.client, action, None)
                    if not method:
                        print(f"  [error] Unknown action: {action}")
                        continue
                    resolved = self._resolve_params(params_set)
                    print(f"  [{i+1}] {action} {resolved}")
                    try:
                        if retry:
                            result = self._execute_with_retry(method, resolved, retry)
                        else:
                            result = method(**resolved)
                        self.last_result = result
                        results.append({'action': action, 'result': result, 'status': 'ok'})
                        success_count += 1
                    except Exception as e:
                        print(f"  [fail] {action}: {e}")
                        results.append({'action': action, 'error': str(e), 'status': 'fail'})
                        fail_count += 1
            else:
                action = op_spec.get('action', '')
                params = op_spec.get('params', {})
                condition = op_spec.get('condition', None)
                retry = op_spec.get('retry', None)

                method = getattr(self.client, action, None)
                if not method:
                    print(f"  [error] Unknown action: {action}")
                    results.append({'action': action, 'error': 'Unknown action', 'status': 'fail'})
                    fail_count += 1
                    continue

                if not self._check_condition(condition):
                    results.append({'action': action, 'status': 'skipped'})
                    continue

                resolved = self._resolve_params(params)
                print(f"  [{i+1}] {action} {resolved}")
                try:
                    if retry:
                        result = self._execute_with_retry(method, resolved, retry)
                    else:
                        result = method(**resolved)
                    self.last_result = result
                    results.append({'action': action, 'result': result, 'status': 'ok'})
                    success_count += 1
                except Exception as e:
                    print(f"  [fail] {action}: {e}")
                    results.append({'action': action, 'error': str(e), 'status': 'fail'})
                    fail_count += 1

        print(f"\nBatch complete: {success_count} succeeded, {fail_count} failed, "
              f"{len([r for r in results if r.get('status') == 'skipped'])} skipped")
        return results
