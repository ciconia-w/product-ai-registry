# 产品需求反馈系统 API 调用脚本

import requests
import json
import os
from datetime import datetime, timedelta
import time

# API 配置
API_CONFIG = {
    "base_url": "https://cooperation.uniontech.com/api/v2/open/worksheet",
    "app_key": "b185c6f1c2ff915f",
    "sign": "ZGRmODhlOGZlNmM2OGE2NDljYTU5ZGEzZjZiNTI5YjUxOWIyNzA4YzlhMzk5ODc5MmRjMTdlNDA5OGU1ZjgxNQ==",
    "worksheet_id": "5fb771127addad0b2d846190",
    # 可用的视图ID
    "view_ids": {
        "all": "5fb771127addad0b2d846191",          # 全部
        "需求池": "63857124f76dc9142412dfdf",     # 🙂需求池 (推荐用于获取需求)
        "反馈视图": "61dbc35c965f3398ac72ea7f",     # ☆反馈视图
        "处理视图": "61dc17af965f3398ac72f192",     # ★处理视图
        "已完结视图": "61dc1c22965f3398ac72f1aa",    # ★已完结视图
    }
}

# 进度记录文件路径
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "product_progress.json")

# 字段ID映射（根据字段对照表）
FIELD_MAPPING = {
    "5fb771127addad0b2d846173": "反馈主题",
    "5fb771127addad0b2d846174": "需求描述",
    "5fb771127addad0b2d846178": "需求标签",
    "5fb771127addad0b2d846177": "闭环状态",
    "5fb771127addad0b2d846184": "审核结论",
    "5fb771127addad0b2d846180": "产品经理",
    "5fb771127addad0b2d846182": "需求分析信息",
    "60a20b9db1202390d1ce46bc": "是否接受",
    "60cb13c4d659ba7cc9714dc9": "可行性分析结论",
    "61dc112c965f3398ac72ea21": "重要程度",
    "61dc112c965f3398ac72ea22": "紧急程度",
    "61dc112c965f3398ac72ea23": "实现成本",
    "61dc112c965f3398ac72ea20": "硬件环境",
    "61dc112c965f3398ac72f15f": "处理状态",
    "611c9210f57e92b2566ffc2a": "所属产品线（模块分类）",
    "5fb771127addad0b2d846175": "附件",
    "60a20b9db1202390d1ce46bd": "是否接受",
    "rowid": "记录ID",
    "ctime": "创建时间",
}

def load_progress():
    """加载已处理的rowid列表"""
    if not os.path.exists(PROGRESS_FILE):
        return set()
    try:
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('processed_rowids', []))
    except:
        return set()

def save_progress(processed_rowids):
    """保存已处理的rowid列表"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'processed_rowids': list(processed_rowids)}, f, ensure_ascii=False, indent=2)

def get_requirements(page_size=50, page_index=1, view_id=None):
    """
    获取需求列表

    Args:
        page_size: 每页数量
        page_index: 页码
        view_id: 视图ID，默认使用"需求池"视图

    Returns:
        dict: API响应结果
    """
    if view_id is None:
        view_id = API_CONFIG["view_ids"]["需求池"]

    url = f"{API_CONFIG['base_url']}/getFilterRows"

    payload = {
        "appKey": API_CONFIG["app_key"],
        "sign": API_CONFIG["sign"],
        "worksheetId": API_CONFIG["worksheet_id"],
        "viewId": view_id,
        "listType": 1,
        "pageSize": page_size,
        "pageIndex": page_index,
        "getSystemControl": False
    }

    response = requests.post(url, json=payload)
    return response.json()

def format_requirement(row_data):
    """
    将API返回的行数据转换为标准格式

    Args:
        row_data: 单行数据

    Returns:
        dict: 标准化需求数据
    """
    # 提取字段信息
    theme = row_data.get("5fb771127addad0b2d846186", "")  # 反馈主题
    description = row_data.get("5fb771127addad0b2d846174", "")  # 需求描述
    topic = row_data.get("5fb771127addad0b2d846173", "")  # 反馈主题(旧字段)
    status = row_data.get("5fb771127addad0b2d84617c", "")  # 处理状态
    priority = row_data.get("61dc112c965f3398ac72ea21", "")  # 重要程度
    product_line_field = row_data.get("611c9210f57e92b2566ffc2a", [])  # 所属产品线/模块分类

    # 提取模块分类（从关联记录中提取 name 字段）
    modules = []
    if product_line_field:
        if isinstance(product_line_field, str):
            # 如果是 JSON 字符串，尝试解析
            try:
                import json
                product_line_field = json.loads(product_line_field)
            except:
                pass
        if isinstance(product_line_field, list):
            for item in product_line_field:
                if isinstance(item, dict):
                    module_name = item.get("name")
                    if module_name:
                        modules.append(module_name)
        elif isinstance(product_line_field, dict):
            module_name = product_line_field.get("name")
            if module_name:
                modules.append(module_name)

    module_str = ", ".join(modules) if modules else ""

    # 提取HTML内容
    from html.parser import HTMLParser
    import re

    def extract_text(html_content):
        """从HTML中提取纯文本"""
        if not html_content:
            return ""
        # 移除HTML标签
        clean = re.sub(r'<[^>]+>', '', html_content)
        # 移除多余空白
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean

    # 主题优先使用 feedbackSubject，否则用 description
    title = topic if topic else (theme if theme else extract_text(description)[:50])

    return {
        "title": title,
        "content": extract_text(description),
        "source": "产品需求反馈系统",
        "source_url": f"https://cooperation.uniontech.com/worksheet/{API_CONFIG['worksheet_id']}/row/{row_data.get('rowid')}",
        "category": "需求反馈",
        "status": status,
        "priority": priority,
        "module": module_str,  # 从所属产品线字段提取的模块分类
        "author": row_data.get("uaid", {}).get("fullname", ""),
        "publish_time": row_data.get("ctime", ""),
        "tags": row_data.get("5fb771127addad0b2d846184", ""),
        "row_id": row_data.get("rowid"),
    }

def get_recent_requirements(days=30, max_count=50, view_id=None):
    """
    获取最近的需求（按创建时间倒序，带时间过滤）

    Args:
        days: 获取最近多少天的需求，默认30天
        max_count: 最多获取多少条，默认50条
        view_id: 视图ID，默认使用"需求池"视图

    Returns:
        list: 最近的需求列表（未处理过）
    """
    all_requirements = []
    processed_rowids = load_progress()
    newly_processed = []

    # 计算截止时间（毫秒时间戳）
    cutoff_time = datetime.now() - timedelta(days=days)
    cutoff_timestamp = int(cutoff_time.timestamp() * 1000)

    print(f"获取最近 {days} 天的需求（截止时间: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}）")
    print(f"已处理记录数: {len(processed_rowids)}")

    # 增大每页数量以减少请求次数
    page_size = 100
    page_index = 1

    while True:
        print(f"\n获取第 {page_index} 页...")
        result = get_requirements(page_size=page_size, page_index=page_index, view_id=view_id)

        if not result.get("success"):
            print(f"获取失败: {result.get('error_msg')}")
            break

        rows = result.get("data", {}).get("rows", [])

        if not rows:
            print(f"第 {page_index} 页无数据，停止获取")
            break

        page_new_count = 0
        reached_cutoff = False

        for row in rows:
            # 检查创建时间
            ctime = row.get("ctime", "")
            if ctime:
                # ctime 格式可能是 "1719331200000" 毫秒时间戳
                try:
                    row_timestamp = int(ctime)
                    if row_timestamp < cutoff_timestamp:
                        reached_cutoff = True
                        break
                except (ValueError, TypeError):
                    pass

            # 检查去重
            rowid = row.get("rowid")
            if rowid and rowid in processed_rowids:
                continue

            req = format_requirement(row)
            all_requirements.append(req)
            if rowid:
                newly_processed.append(rowid)
                page_new_count += 1

        print(f"  本页获取到 {len(rows)} 条，新增 {page_new_count} 条")

        # 达到截止时间或数量上限，停止获取
        if reached_cutoff or len(all_requirements) >= max_count:
            if reached_cutoff:
                print(f"\n已达到时间截止点（{cutoff_time.strftime('%Y-%m-%d')}），停止获取")
            if len(all_requirements) >= max_count:
                print(f"\n已达到数量上限（{max_count}条），停止获取")
            break

        page_index += 1

    # 限制返回数量
    returned_requirements = all_requirements[:max_count]

    # 只保存实际返回的需求对应的rowid
    returned_rowids = [req.get('row_id') for req in returned_requirements if req.get('row_id')]
    if returned_rowids:
        processed_rowids.update(returned_rowids)
        save_progress(processed_rowids)
        print(f"\n已保存 {len(returned_rowids)} 条新记录到进度文件")

    return returned_requirements

def get_all_requirements(page_size=100, max_pages=10):
    """
    获取所有需求（分页），自动去重

    Args:
        page_size: 每页数量
        max_pages: 最大页数

    Returns:
        list: 所有需求（未处理过）数据列表
    """
    all_requirements = []
    processed_rowids = load_progress()
    newly_processed = []

    print(f"已处理记录数: {len(processed_rowids)}")

    for page in range(1, max_pages + 1):
        print(f"\n获取第 {page} 页...")
        result = get_requirements(page_size=page_size, page_index=page)

        if not result.get("success"):
            print(f"获取失败: {result.get('error_msg')}")
            break

        rows = result.get("data", {}).get("rows", [])

        if not rows:
            print(f"第 {page} 页无数据，停止获取")
            break

        new_count = 0
        for row in rows:
            rowid = row.get("rowid")
            if rowid and rowid in processed_rowids:
                print(f"  跳过已处理: {rowid}")
                continue
            req = format_requirement(row)
            all_requirements.append(req)
            if rowid:
                newly_processed.append(rowid)
                new_count += 1

        print(f"  本页获取到 {len(rows)} 条，新增 {new_count} 条")

    # 保存新处理的rowid
    if newly_processed:
        processed_rowids.update(newly_processed)
        save_progress(processed_rowids)
        print(f"\n已保存 {len(newly_processed)} 条新记录到进度文件")

    return all_requirements


if __name__ == "__main__":
    import sys

    # 解析命令行参数
    save_to_file = '--save' in sys.argv
    output_file = None

    # 检查 --output 参数
    for i, arg in enumerate(sys.argv):
        if arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            break

    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "recent":
        # 获取最近的需求
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        max_count = int(sys.argv[3]) if len(sys.argv) > 3 else 50

        print(f"正在获取最近 {days} 天的产品需求（最多 {max_count} 条）...")
        requirements = get_recent_requirements(days=days, max_count=max_count)

        print(f"\n=== 获取完成，共 {len(requirements)} 条需求 ===\n")
        if requirements:
            for i, req in enumerate(requirements[:5], 1):
                print(f"{i}. {req['title']}")
                print(f"   发布时间: {req['publish_time']}")
                print(f"   来源: {req['source']}")
                print()
            if len(requirements) > 5:
                print(f"   ... 还有 {len(requirements) - 5} 条需求")

        # 保存到文件或打印
        if output_file or save_to_file:
            if not output_file:
                # 生成默认文件名
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs')
                os.makedirs(output_dir, exist_ok=True)
                output_file = os.path.join(output_dir, f'requirements_product_{timestamp}.json')

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(requirements, f, ensure_ascii=False, indent=2)
            print(f"\n✓ 已保存 {len(requirements)} 条需求到: {output_file}")
    else:
        # 测试接口（旧方式）
        result = get_requirements(page_size=5, page_index=1, view_id="5fb771127addad0b2d846191")

        if result.get("success"):
            data = result.get("data", {})
            print(f"总行数: {data.get('rowCount', '未知')}")
            rows = data.get("rows", [])
            print(f"获取到 {len(rows)} 条需求")

            if rows:
                print("\n第一条需求:")
                req = format_requirement(rows[0])
                for key, value in req.items():
                    if value:
                        print(f"  {key}: {value}")
        else:
            print(f"获取失败: {result.get('error_msg')}")
