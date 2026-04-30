---
name: uniontech-ai-point-export
description: Extract UnionTech datan AI point statistics from https://datan.uniontech.com/#/ai-point/statics after the user is already logged in, capture the page's real authenticated XHR requests, sum daily rows into totals, and optionally fill the V20 AI point Excel template. Use when the user asks to fetch UnionTech AI埋点统计 data, compare page values, export and sum the last 7 days, or write those values into the workbook.
---

# UnionTech AI Point Export

Use this skill for the UnionTech AI point dashboard at `datan.uniontech.com`.

Assumptions:
- The user has already opened Chrome and logged into the dashboard.
- The target page is `#/ai-point/statics`.
- The dashboard query mode is `按日`.

Default date rule:
- If the user gives an explicit date range, use it.
- If the user says "今天取数" or does not specify dates, use the previous 7 complete natural days, excluding today.
- Example on `2026-04-17`: use `2026-04-10` through `2026-04-16`.

## Output contract

Always report:
- The exact filter used:
  - `系统产品`
  - `系统版本`
  - `日期粒度`
  - `开始`
  - `结束`
- The extracted metric totals.
- Whether values were only previewed or also written into an Excel file.
- If written into Excel, the workbook must be saved beside the active template workbook in `AI-output/data`, not in `Downloads` or another ad-hoc directory unless the user explicitly asks for that.

## Preferred extraction path

Do not rely on screenshots for numeric extraction unless no better path remains.

Preferred order:
1. Use the live logged-in page.
2. Capture the page's own authenticated XHR requests after clicking `查询`.
3. Reuse the real request headers exactly as observed.
4. Sum per-day rows into final totals.
5. Fill the workbook, leaving formula columns untouched.

## Auth details

When intercepting the page's real XHR requests, expect headers shaped like:
- `token: <raw token>`
- `AuthToken: Bearer <raw token>`

Do not assume command-line replay with only one auth header will work.
Prefer using the page's own query requests and harvested headers.

## Query workflow

1. Ensure the real page is open on `https://datan.uniontech.com/#/ai-point/statics`.
2. Confirm `按日` mode.
3. Set or verify the requested date range.
4. Intercept XHR:
   - method
   - URL
   - headers
   - body
   - response text
5. Trigger the page's `查询`.
6. Collect all `/v1/dream-io/system-events/uos-ai` responses.
7. Parse and sum daily rows by metric family.

## Known metric families

The dashboard requests map to these groups:
- `tid=1001600006`: `UOS AI助手应用启动次数`
- `tid=1001600001`: `随航打开次数`
- `tid=1001600003`: `写作功能打开次数`
- `tid=1001600002`: `随航各功能点击次数`
- `tid=1001600007`: `UOS AI助手指令使用次数`
- `tid=1001600008`: `UOS AI助手各智能体使用次数`
- `tid=1001600004`: `写作各功能点点击次数`
- `sql_template_id=124`: active and used users summary card

## Excel fill rules

Current workbook header mapping:
- Formula columns must be preserved:
  - `AI 助手PV`
  - `随航使用次数`
  - `写作PV`
- Default workbook location:
  - Read the template workbook from `AI-output/data`.
  - Write the filled workbook back into the same directory as the template workbook.
- Fill only non-formula numeric columns you can map from extracted data.
- If a column has no confirmed source value, leave it blank rather than reusing stale data.

Header mapping notes:
- `Multimedia Control` -> `多媒体控制`
- `add to knowledge base` -> `加入知识库`
- `润色-亲切友善` may be absent; if absent in the returned schema, write `0` only when the request family is otherwise complete and the column is clearly not returned.

## Validation

Before claiming completion:
- Confirm the intercepted requests used the intended date range.
- Confirm every summed field came from the matching request family.
- Read back the filled workbook row after writing.
- State the final file path, and make sure that path is the workbook path under `AI-output/data` when a workbook was produced.

## Failure handling

If extraction fails:
- Report whether the blocker is:
  - wrong page
  - not logged in
  - page context drift
  - missing query requests
  - workbook mapping gap
- Prefer retrying the page-intercept path before falling back to manual export clicking.
