#!/usr/bin/env python3
"""
PMS CLI — Zero-dependency reverse-engineered API client.

Usage:
  python pms_cli.py <operation> [--param value ...] [--base-url URL] [--cookie STR]
  python pms_cli.py --config batch.json
"""

import argparse
import json
import os
import sys

from pms_client import BaseClient
from pms_product import ProductMixin
from pms_project import ProjectMixin
from pms_task import TaskMixin
from pms_bug import BugMixin
from pms_story import StoryMixin
from pms_search import SearchMixin
from pms_utils import markdown_to_html, BatchRunner


# ──────────────────────────────────────────────────────────────────────────────
# ZentaoClient — composed from BaseClient + domain mixins
# ──────────────────────────────────────────────────────────────────────────────

class ZentaoClient(BaseClient, ProductMixin, ProjectMixin, TaskMixin, BugMixin, StoryMixin, SearchMixin):
    """Full API client assembled from base HTTP + domain mixins."""
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Operation Dispatch Table
# ──────────────────────────────────────────────────────────────────────────────

OPERATION_MAP = {
    'login': 'login',
    'list_products': 'list-products',
    'browse_product': 'browse-product',
    'view_product': 'view-product',
    'create_product': 'create-product',
    'list_projects': 'list-projects',
    'view_project': 'view-project',
    'list_project_tasks': 'list-project-tasks',
    'create_task': 'create-task',
    'view_task': 'view-task',
    'edit_task': 'edit-task',
    'list_product_stories': 'list-product-stories',
    'create_story': 'create-story',
    'view_story': 'view-story',
    'edit_story': 'edit-story',
    'my_tasks': 'my-tasks',
    'my_bugs': 'my-bugs',
    'my_stories': 'my-stories',
    'product_bugs': 'product-bugs',
    'add_bug_comment': 'add-bug-comment',
    'add_task_comment': 'add-task-comment',
    'add_story_comment': 'add-story-comment',
    'project_builds': 'project-builds',
    'project_team': 'project-team',
    'project_dynamics': 'project-dynamics',
    'product_plans': 'product-plans',
    'product_releases': 'product-releases',
    'browse_by_search': 'browse-by-search',
    'list_saved_queries': 'list-saved-queries',
}


# ──────────────────────────────────────────────────────────────────────────────
# CLI — argparse-based command-line interface
# ──────────────────────────────────────────────────────────────────────────────

def _ensure_client(args):
    """Create a ZentaoClient from CLI arguments.

    Supports auto-loading session from ~/.pms/.pms_session.json
    and validates session expiration (15 minutes TTL).
    """
    default_session_path = os.path.join(os.path.expanduser('~'), '.pms', '.pms_session.json')

    base_url = args.base_url or os.environ.get('PMS_BASE_URL', '')
    cookie_file = args.cookie_file
    cookie_string = args.cookie

    if not cookie_string and not cookie_file and os.path.exists(default_session_path):
        cookie_file = default_session_path

    if not base_url and cookie_file and os.path.exists(cookie_file):
        try:
            with open(cookie_file, 'r') as f:
                session = json.load(f)
                if isinstance(session, dict) and session.get('base_url'):
                    base_url = session['base_url']
        except Exception:
            pass

    if not base_url:
        raise RuntimeError(
            "Base URL is required. Please provide --base-url, "
            "set PMS_BASE_URL environment variable, or login "
            "using pms_login.py to create a session file."
        )

    try:
        return ZentaoClient(
            base_url=base_url,
            cookie_string=cookie_string,
            cookie_file=cookie_file
        )
    except RuntimeError as e:
        if 'expired' in str(e).lower():
            print(f"⚠️  {e}", file=sys.stderr)
            print(f"💡  Please refresh your session using: python scripts/pms_login.py --method auto", file=sys.stderr)
            sys.exit(1)
        raise


def main():
    parser = argparse.ArgumentParser(
        description='PMS CLI — Automated API client for reverse-engineered platform',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python pms_cli.py list-products --base-url https://pms.example.com --cookie "sessionid=abc"
  python pms_cli.py --config batch.json --base-url https://pms.example.com
        '''
    )
    parser.add_argument('--base-url', help='Base URL of the target platform')
    parser.add_argument('--cookie', help='Cookie string for authentication')
    parser.add_argument('--cookie-file', help='Path to captured_cookies.json')
    parser.add_argument('--config', help='Path to batch JSON config file')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print requests without executing them')

    subparsers = parser.add_subparsers(dest='operation', help='Available operations')

    parser_login = subparsers.add_parser('login', help='Authenticate with Zentao PMS')
    parser_login.add_argument('--username', help='username')
    parser_login.add_argument('--password', help='password')
    parser_list_products = subparsers.add_parser('list-products', help='List all products')
    parser_browse_product = subparsers.add_parser('browse-product', help='Browse stories/bugs in a product')
    parser_view_product = subparsers.add_parser('view-product', help='View product details')
    parser_create_product = subparsers.add_parser('create-product', help='Create a new product (requires permission)')
    parser_create_product.add_argument('--product_name', help='product_name')
    parser_create_product.add_argument('--product_code', help='product_code')
    parser_create_product.add_argument('--description', help='description')
    parser_create_product.add_argument('--uid', help='uid')
    parser_list_projects = subparsers.add_parser('list-projects', help='List all projects')
    parser_view_project = subparsers.add_parser('view-project', help='View project details')
    parser_list_project_tasks = subparsers.add_parser('list-project-tasks', help='List tasks in a project')
    parser_create_task = subparsers.add_parser('create-task', help='Create a task in a project')
    parser_create_task.add_argument('--project_id', help='project_id')
    parser_create_task.add_argument('--task_type', help='task_type')
    parser_create_task.add_argument('--task_name', help='task_name')
    parser_create_task.add_argument('--description', help='description')
    parser_create_task.add_argument('--assignee', help='assignee')
    parser_create_task.add_argument('--estimate_hours', help='estimate_hours')
    parser_create_task.add_argument('--start_date', help='start_date')
    parser_create_task.add_argument('--deadline', help='deadline')
    parser_create_task.add_argument('--uid', help='uid')
    parser_view_task = subparsers.add_parser('view-task', help='Fetch and parse task details')
    parser_view_task.add_argument('--task_id', help='Task ID to fetch', required=True)
    parser_view_bug = subparsers.add_parser('view-bug', help='Fetch and parse bug details')
    parser_view_bug.add_argument('--bug_id', help='Bug ID to fetch', required=True)
    parser_add_bug_comment = subparsers.add_parser('add-bug-comment', help='Add comment/remark to a bug')
    parser_add_bug_comment.add_argument('--bug_id', help='Bug ID to comment on', required=True)
    parser_add_bug_comment.add_argument('--comment', help='Comment text (or use --file)', required=False)
    parser_add_bug_comment.add_argument('--file', help='Read comment from file', required=False)
    parser_add_task_comment = subparsers.add_parser('add-task-comment', help='Add comment/remark to a task')
    parser_add_task_comment.add_argument('--task_id', help='Task ID to comment on', required=True)
    parser_add_task_comment.add_argument('--comment', help='Comment text (or use --file)', required=False)
    parser_add_task_comment.add_argument('--file', help='Read comment from file', required=False)
    parser_add_story_comment = subparsers.add_parser('add-story-comment', help='Add comment/remark to a story')
    parser_add_story_comment.add_argument('--story_id', help='Story ID to comment on', required=True)
    parser_add_story_comment.add_argument('--comment', help='Comment text (or use --file)', required=False)
    parser_add_story_comment.add_argument('--file', help='Read comment from file', required=False)
    parser_edit_task = subparsers.add_parser('edit-task', help='Edit an existing task')
    parser_edit_task.add_argument('--task_id', help='Task ID to edit', required=True)
    parser_edit_task.add_argument('--task_name', help='New task name')
    parser_edit_task.add_argument('--description', help='New task description')
    parser_edit_task.add_argument('--assignee', help='New assignee')
    parser_edit_task.add_argument('--estimate_hours', help='New estimated hours')
    parser_edit_task.add_argument('--start_date', help='New start date (YYYY-MM-DD)')
    parser_edit_task.add_argument('--deadline', help='New deadline (YYYY-MM-DD)')
    parser_edit_task.add_argument('--pri', help='New priority (1-4)')
    parser_list_product_stories = subparsers.add_parser('list-product-stories', help='List stories in a product')
    parser_create_story = subparsers.add_parser('create-story', help='Create a story in a product')
    parser_create_story.add_argument('--product_id', help='product_id')
    parser_create_story.add_argument('--story_title', help='story_title')
    parser_create_story.add_argument('--specification', help='specification')
    parser_create_story.add_argument('--verification', help='verification')
    parser_create_story.add_argument('--assignee', help='assignee')
    parser_create_story.add_argument('--estimate_hours', help='estimate_hours')
    parser_create_story.add_argument('--uid', help='uid')
    parser_create_story.add_argument('--spec_file', help='Read specification from file (.md auto-converts, .html as-is)')
    parser_create_story.add_argument('--verify_file', help='Read verification from file (.md auto-converts, .html as-is)')
    parser_view_story = subparsers.add_parser('view-story', help='Fetch and parse story details')
    parser_view_story.add_argument('--story_id', help='Story ID to fetch', required=True)
    parser_edit_story = subparsers.add_parser('edit-story', help='Edit an existing story')
    parser_edit_story.add_argument('--story_id', help='Story ID to edit', required=True)
    parser_edit_story.add_argument('--story_title', help='New story title')
    parser_edit_story.add_argument('--specification', help='New specification (Markdown or HTML)')
    parser_edit_story.add_argument('--spec_file', help='Read specification from file (.md auto-converts, .html as-is)')
    parser_edit_story.add_argument('--verification', help='New verification (Markdown or HTML)')
    parser_edit_story.add_argument('--verify_file', help='Read verification from file (.md auto-converts, .html as-is)')
    parser_edit_story.add_argument('--assignee', help='New assignee')
    parser_edit_story.add_argument('--pri', help='New priority (1-4)')
    parser_edit_story.add_argument('--estimate_hours', help='New estimated hours')
    parser_my_tasks = subparsers.add_parser('my-tasks', help='List my tasks')
    parser_my_bugs = subparsers.add_parser('my-bugs', help='List my bugs')
    parser_my_stories = subparsers.add_parser('my-stories', help='List my stories')
    parser_product_bugs = subparsers.add_parser('product-bugs', help='List bugs in a product')
    parser_project_builds = subparsers.add_parser('project-builds', help='List builds in a project')
    parser_project_team = subparsers.add_parser('project-team', help='List team members in a project')
    parser_project_dynamics = subparsers.add_parser('project-dynamics', help='View project activity log')
    parser_product_plans = subparsers.add_parser('product-plans', help='List plans in a product')
    parser_product_releases = subparsers.add_parser('product-releases', help='List releases in a product')
    parser_browse_by_search = subparsers.add_parser('browse-by-search', help='Browse stories using a saved search (bySearch) query')
    parser_browse_by_search.add_argument('--product_id', help='Product ID', required=True)
    parser_browse_by_search.add_argument('--query_id', help='Saved query ID (numeric, e.g. 506)', required=True)
    parser_browse_by_search.add_argument('--branch', help='Product branch (default 0)', default='0')
    parser_browse_by_search.add_argument('--output', help='Save HTML output to file (optional)')
    parser_list_saved_queries = subparsers.add_parser('list-saved-queries', help='List available saved queries for a module')
    parser_list_saved_queries.add_argument('--module', help='Module: story, bug, task (default story)', default='story')
    parser_list_saved_queries.add_argument('--query_id', help='Optional reference query ID')
    args = parser.parse_args()

    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)

        if not args.base_url and config.get('base_url'):
            args.base_url = config['base_url']
        if not args.cookie and config.get('cookie'):
            args.cookie = config['cookie']
        if not args.cookie_file and config.get('cookie_file'):
            args.cookie_file = config['cookie_file']

        client = _ensure_client(args)
        runner = BatchRunner(client)
        runner.run(args.config)
        return

    if not args.operation:
        parser.print_help()
        sys.exit(1)

    client = _ensure_client(args)

    if args.operation == 'login':
        if args.dry_run:
            print('DRY RUN: login(username=args.username, password=args.password)')
        else:
            result = client.login(username=args.username, password=args.password)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'list-products':
        if args.dry_run:
            print('DRY RUN: list_products()')
        else:
            result = client.list_products()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'browse-product':
        if args.dry_run:
            print('DRY RUN: browse_product()')
        else:
            result = client.browse_product()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'view-product':
        if args.dry_run:
            print('DRY RUN: view_product()')
        else:
            result = client.view_product()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'create-product':
        if args.dry_run:
            print('DRY RUN: create_product(product_name=args.product_name, product_code=args.product_code, description=args.description, uid=args.uid)')
        else:
            result = client.create_product(product_name=args.product_name, product_code=args.product_code, description=args.description, uid=args.uid)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'list-projects':
        if args.dry_run:
            print('DRY RUN: list_projects()')
        else:
            result = client.list_projects()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'view-project':
        if args.dry_run:
            print('DRY RUN: view_project()')
        else:
            result = client.view_project()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'list-project-tasks':
        if args.dry_run:
            print('DRY RUN: list_project_tasks()')
        else:
            result = client.list_project_tasks()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'create-task':
        if args.dry_run:
            print('DRY RUN: create_task(project_id=args.project_id, task_type=args.task_type, task_name=args.task_name, description=args.description, assignee=args.assignee, estimate_hours=args.estimate_hours, start_date=args.start_date, deadline=args.deadline, uid=args.uid)')
        else:
            result = client.create_task(project_id=args.project_id, task_type=args.task_type, task_name=args.task_name, description=args.description, assignee=args.assignee, estimate_hours=args.estimate_hours, start_date=args.start_date, deadline=args.deadline, uid=args.uid)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'view-task':
        if args.dry_run:
            print('DRY RUN: view_task(task_id=args.task_id)')
        else:
            result = client.view_task(task_id=args.task_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'view-bug':
        if args.dry_run:
            print('DRY RUN: view_bug(bug_id=args.bug_id)')
        else:
            result = client.view_bug(bug_id=args.bug_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'add-bug-comment':
        if args.dry_run:
            print(f'DRY RUN: add_bug_comment(bug_id={args.bug_id}, comment=...)')
        else:
            comment_text = args.comment
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    comment_text = f.read()
            if not comment_text:
                print('Error: Either --comment or --file must be provided')
                sys.exit(1)
            result = client.add_bug_comment(bug_id=args.bug_id, comment=comment_text)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'add-task-comment':
        if args.dry_run:
            print(f'DRY RUN: add_task_comment(task_id={args.task_id}, comment=...)')
        else:
            comment_text = args.comment
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    comment_text = f.read()
            if not comment_text:
                print('Error: Either --comment or --file must be provided')
                sys.exit(1)
            result = client.add_task_comment(task_id=args.task_id, comment=comment_text)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'add-story-comment':
        if args.dry_run:
            print(f'DRY RUN: add_story_comment(story_id={args.story_id}, comment=...)')
        else:
            comment_text = args.comment
            if args.file:
                with open(args.file, 'r', encoding='utf-8') as f:
                    comment_text = f.read()
            if not comment_text:
                print('Error: Either --comment or --file must be provided')
                sys.exit(1)
            result = client.add_story_comment(story_id=args.story_id, comment=comment_text)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'edit-task':
        if args.dry_run:
            print('DRY RUN: edit_task(task_id=args.task_id, task_name=args.task_name, description=args.description, assignee=args.assignee, estimate_hours=args.estimate_hours, start_date=args.start_date, deadline=args.deadline, pri=args.pri)')
        else:
            result = client.edit_task(task_id=args.task_id, task_name=args.task_name, description=args.description, assignee=args.assignee, estimate_hours=args.estimate_hours, start_date=args.start_date, deadline=args.deadline, pri=args.pri)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'list-product-stories':
        if args.dry_run:
            print('DRY RUN: list_product_stories()')
        else:
            result = client.list_product_stories()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'create-story':
        spec = args.specification
        if args.spec_file:
            with open(args.spec_file, 'r', encoding='utf-8') as f:
                spec = f.read()
        verify = args.verification
        if args.verify_file:
            with open(args.verify_file, 'r', encoding='utf-8') as f:
                verify = f.read()
        spec = markdown_to_html(spec) if spec else spec
        verify = markdown_to_html(verify) if verify else verify
        if args.dry_run:
            print('DRY RUN: create_story(product_id=args.product_id, story_title=args.story_title, specification=..., verification=..., assignee=args.assignee, estimate_hours=args.estimate_hours, uid=args.uid)')
        else:
            result = client.create_story(product_id=args.product_id, story_title=args.story_title,
                                         specification=spec, verification=verify,
                                         assignee=args.assignee, estimate_hours=args.estimate_hours,
                                         uid=args.uid)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'view-story':
        if args.dry_run:
            print('DRY RUN: view_story(story_id=args.story_id)')
        else:
            result = client.view_story(story_id=args.story_id)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'edit-story':
        spec = args.specification
        if args.spec_file:
            with open(args.spec_file, 'r', encoding='utf-8') as f:
                spec = f.read()
        verify = args.verification
        if args.verify_file:
            with open(args.verify_file, 'r', encoding='utf-8') as f:
                verify = f.read()
        if args.dry_run:
            print(f'DRY RUN: edit_story(story_id=args.story_id, story_title=args.story_title, specification=..., verification=..., assignee=args.assignee, pri=args.pri, estimate_hours=args.estimate_hours)')
        else:
            result = client.edit_story(story_id=args.story_id, title=args.story_title,
                                       specification=spec, verification=verify,
                                       assignee=args.assignee, pri=args.pri,
                                       estimate_hours=args.estimate_hours)
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'my-tasks':
        if args.dry_run:
            print('DRY RUN: my_tasks()')
        else:
            result = client.my_tasks()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'my-bugs':
        if args.dry_run:
            print('DRY RUN: my_bugs()')
        else:
            result = client.my_bugs()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'my-stories':
        if args.dry_run:
            print('DRY RUN: my_stories()')
        else:
            result = client.my_stories()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'product-bugs':
        if args.dry_run:
            print('DRY RUN: product_bugs()')
        else:
            result = client.product_bugs()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'project-builds':
        if args.dry_run:
            print('DRY RUN: project_builds()')
        else:
            result = client.project_builds()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'project-team':
        if args.dry_run:
            print('DRY RUN: project_team()')
        else:
            result = client.project_team()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'project-dynamics':
        if args.dry_run:
            print('DRY RUN: project_dynamics()')
        else:
            result = client.project_dynamics()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'product-plans':
        if args.dry_run:
            print('DRY RUN: product_plans()')
        else:
            result = client.product_plans()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'product-releases':
        if args.dry_run:
            print('DRY RUN: product_releases()')
        else:
            result = client.product_releases()
            print(json.dumps(result, indent=2, ensure_ascii=False))
    if args.operation == 'browse-by-search':
        if args.dry_run:
            print(f'DRY RUN: browse_by_search(product_id={args.product_id}, query_id={args.query_id})')
        else:
            result = client.browse_by_search(
                product_id=args.product_id,
                query_id=args.query_id,
                branch=int(args.branch)
            )
            if result is None:
                print(json.dumps({'error': 'Access denied or session expired'}, ensure_ascii=False))
            elif args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(json.dumps({'status': 'ok', 'output': args.output, 'size': len(result)}, ensure_ascii=False))
            else:
                print(json.dumps({'status': 'ok', 'size': len(result)}, ensure_ascii=False))
    if args.operation == 'list-saved-queries':
        if args.dry_run:
            print(f'DRY RUN: list_saved_queries(module={args.module})')
        else:
            query_id = int(args.query_id) if args.query_id else None
            result = client.list_saved_queries(
                module=args.module,
                query_id=query_id
            )
            print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
