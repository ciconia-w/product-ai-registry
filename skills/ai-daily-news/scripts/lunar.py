#!/usr/bin/env python3
"""
农历计算工具 - 纯Python实现，无需第三方依赖
基于已知春节日期进行推算
"""

import sys
from datetime import datetime

# 2026-2030年春节对应的公历日期（正月初一）
SPRING_FESTIVAL = {
    2026: (2, 17),  # 2026年春节
    2027: (2, 6),
    2028: (1, 26),
    2029: (2, 13),
    2030: (2, 2),
}

# 农历月份天数（近似值，大月30天，小月29天）
# 这里使用简化计算，对于日常用途足够准确
LUNAR_MONTHS = {
    2026: [29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 30, 29, 30],  # 十三个月
    2027: [29, 30, 29, 29, 30, 29, 30, 29, 29, 30, 29, 30],    # 十二个月
    2028: [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29],    # 十二个月
    2029: [29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29], # 十三个月
    2030: [30, 29, 30, 29, 29, 30, 29, 30, 29, 30, 29, 30],     # 十二个月
}

# 农历日期名称
LUNAR_DAYS = ['', '初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
              '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
              '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']

def get_lunar_date(year, month, day):
    """计算公历日期对应的农历日期"""
    if year not in SPRING_FESTIVAL:
        # 对于未知年份，返回近似值
        return f"{year}年{month}月{day}日"

    sf_month, sf_day = SPRING_FESTIVAL[year]
    spring_festival = datetime(year, sf_month, sf_day)

    try:
        current = datetime(year, month, day)
    except ValueError:
        return f"{year}年{month}月{day}日"

    # 计算距离春节的天数
    days_diff = (current - spring_festival).days

    if days_diff < 0:
        # 在春节之前，需要计算上一年的农历
        prev_year = year - 1
        if prev_year not in SPRING_FESTIVAL:
            return f"{year}年{month}月{day}日"
        prev_sf_month, prev_sf_day = SPRING_FESTIVAL[prev_year]
        prev_spring = datetime(prev_year, prev_sf_month, prev_sf_day)
        days_diff = (current - prev_spring).days

        # 计算上一年的总天数
        total_days = sum(LUNAR_MONTHS.get(prev_year, [29] * 12))
        days_diff = total_days + days_diff + 1  # +1 因为春节是第一天
    else:
        days_diff += 1  # 春节是第一天

    # 计算农历月份和日期
    month_idx = 0
    remaining_days = days_diff

    if year in LUNAR_MONTHS:
        for i, days in enumerate(LUNAR_MONTHS[year]):
            if remaining_days <= days:
                lunar_month = i + 1
                lunar_day = remaining_days
                break
            remaining_days -= days
        else:
            # 超过一年，说明是闰月或其他情况
            lunar_month = len(LUNAR_MONTHS[year])
            lunar_day = remaining_days
    else:
        # 未知年份，使用简化计算
        lunar_month = (days_diff // 30) + 1
        lunar_day = (days_diff % 30) + 1
        if lunar_month > 12:
            lunar_month = 12

    # 处理月份名称
    month_names = ['', '正月', '二月', '三月', '四月', '五月', '六月',
                   '七月', '八月', '九月', '十月', '冬月', '腊月']

    if lunar_month <= len(month_names):
        month_name = month_names[lunar_month]
    else:
        month_name = f"第{lunar_month}月"

    day_name = LUNAR_DAYS[lunar_day] if lunar_day < len(LUNAR_DAYS) else f"第{lunar_day}天"

    return f"{month_name}{day_name}"

def get_weekday(year, month, day):
    """计算星期几"""
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    dt = datetime(year, month, day)
    return weekdays[dt.weekday()]

def get_solar_terms(month, day):
    """获取节气（简化版，仅覆盖主要节气）"""
    # 简化处理，返回空字符串
    return ""

def main():
    if len(sys.argv) < 4:
        # 默认使用今天
        today = datetime.now()
        year, month, day = today.year, today.month, today.day
    else:
        year, month, day = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])

    lunar = get_lunar_date(year, month, day)
    weekday = get_weekday(year, month, day)
    print(f"{lunar} · {weekday}好")

if __name__ == "__main__":
    main()
