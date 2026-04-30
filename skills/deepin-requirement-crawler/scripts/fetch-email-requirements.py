#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
腾讯企业邮箱邮件提取脚本 - Skill 集成版
提取【AI】种子用户群邮件中的需求信息，输出 JSON 给 skill 处理
支持 UID 进度记录，避免重复爬取
"""

import imaplib
import email
from email.header import decode_header
import os
import json
from datetime import datetime
import re

# 配置
EMAIL_CONFIG = {
    "host": "imap.exmail.qq.com",
    "port": 993,
    "email": "product_rep_for_ai@uniontech.com",
    "password": "BjHXDJh7BUDjjA89"
}

# 进度文件路径
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "email_progress.json")

def load_progress():
    """加载已处理的 UID 列表"""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f).get('processed_uids', [])
        except:
            pass
    return []

def save_progress(uids):
    """保存已处理的 UID"""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'processed_uids': uids, 'last_updated': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)

def decode_str(h):
    """解码邮件头字符串"""
    if not h: return ''
    d = decode_header(h)
    r = ''
    for c, e in d:
        if isinstance(c, bytes):
            r += c.decode(e or 'utf-8', errors='ignore')
        else:
            r += c
    return r

def get_body(msg):
    """获取邮件正文"""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain' and 'attachment' not in str(part.get('Content-Disposition')):
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(part.get_content_charset() or 'utf-8', errors='ignore')
    return ''

def parse_requirements(body):
    """解析邮件正文中的需求"""
    results = []
    lines = body.split('\n')

    section = ""
    priority = ""

    # 移除历史邮件引用
    for i, line in enumerate(lines):
        if line.startswith('---') and i > 10:
            lines = lines[:i]
            break

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or '张鹏' in line or '写道' in line:
            continue

        # 识别章节
        if '功能缺陷' in line and len(line) < 20:
            section = "Bug"
            continue
        elif '体验槽点' in line and len(line) < 20:
            section = "体验槽点"
            continue
        elif '新增需求' in line and len(line) < 20:
            section = "新需求"
            continue
        elif '需整理入产品需求池' in line:
            section = "需求池"
            continue
        elif line in ['高频咨询', '深度洞察', '待办清单', '说明']:
            section = ""
            continue

        # 处理需求行
        if section in ['Bug', '体验槽点', '新需求']:
            if line.startswith('●'):
                line = line[1:].strip()

            if '：' in line:
                parts = line.split('：', 1)
                title, desc = parts[0].strip(), parts[1].strip() if len(parts) > 1 else ""

                title = re.sub(r'^[\d.\s]+', '', title).strip()

                if title and desc:
                    results.append({"type": section, "title": title, "description": desc})

        elif section == "需求池":
            if line.endswith('：'):
                priority = line[:-1].strip().replace('●', '').replace('○', '').strip()
                continue

            if '（' in line or '(' in line:
                open_idx = line.find('（') if '（' in line else line.find('(')
                close_idx = line.find('）') if '）' in line else line.find(')')

                title = line[:open_idx].strip().replace('●', '').replace('○', '').strip()
                desc = line[close_idx+1:].strip() if close_idx > open_idx else ""

                if title.startswith('说明') or '总结严格基于' in line:
                    continue

                if title and desc:
                    priority_str = f"需求池-{priority}" if priority else "需求池"
                    results.append({"type": priority_str, "title": title, "description": desc})

    return results

def main(only_new=True):
    """
    主函数
    Args:
        only_new: True=只爬取未处理的新邮件， False=爬取所有邮件
    Returns:
        list: 需求数据列表
    """
    # 加载进度
    processed_uids = load_progress()

    # 连接邮箱
    mail = imaplib.IMAP4_SSL(EMAIL_CONFIG['host'], EMAIL_CONFIG['port'])
    mail.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
    mail.select("INBOX")

    try:
        # 获取所有邮件 UID（最新在前）
        status, result = mail.search(None, 'ALL')
        email_ids = result[0].split() if result[0] else []

        all_requirements = []
        newly_processed = []

        # 遍历邮件
        for eid in reversed(email_ids):
            # 获取 UID
            status, data = mail.fetch(eid, '(UID)')
            match = re.search(r'UID (\d+)', data[0].decode())
            if not match:
                continue
            uid = match.group(1)

            # 跳过已处理的
            if only_new and uid in processed_uids:
                continue

            try:
                # 获取邮件内容
                m = mail.fetch(eid, '(RFC822)')[1][0][1]
                msg = email.message_from_bytes(m)
                subject = decode_str(msg['Subject'])

                # 只处理【AI】种子用户群邮件
                if '【AI】种子用户群' not in subject:
                    continue

                body = get_body(msg)
                reqs = parse_requirements(body)

                try:
                    date_obj = email.utils.parsedate_to_datetime(msg['Date'])
                    date = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    date = msg['Date'] or ''

                if reqs:
                    for r in reqs:
                        # 统一格式输出给 skill
                        all_requirements.append({
                            "title": r['title'],
                            "content": r['description'],
                            "url": f"mailto:{EMAIL_CONFIG['email']}?subject={subject}",
                            "author": "种子用户群",
                            "publish_time": date,
                            "category": r['type'],
                            "likes": 0,
                            "views": 0,
                            "source": "email",
                            "uid": uid
                        })

                    newly_processed.append(uid)

            except Exception as e:
                continue

        # 保存进度
        if newly_processed:
            save_progress(processed_uids + newly_processed)

        return all_requirements

    finally:
        mail.close()
        mail.logout()

if __name__ == "__main__":
    # 命令行使用：输出 JSON
    import sys

    # 解析命令行参数
    only_new = '--all' not in sys.argv
    save_to_file = '--save' in sys.argv
    output_file = None

    # 检查 --output 参数
    for i, arg in enumerate(sys.argv):
        if arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            break

    requirements = main(only_new=only_new)

    # 保存到文件或打印
    if output_file or save_to_file:
        if not output_file:
            # 生成默认文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, f'requirements_email_{timestamp}.json')

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(requirements, f, ensure_ascii=False, indent=2)
        print(f"✓ 已保存 {len(requirements)} 条需求到: {output_file}")
    else:
        print(json.dumps(requirements, ensure_ascii=False, indent=2))
