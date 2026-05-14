---
name: company-pm-opencli
description: Use the local OpenCLI `company-pm` plugin when the user wants to inspect or automate UnionTech PMS/禅道, internal BI export, or requirement collection through `opencli company-pm ...`. Use this skill for PMS/Zentao product, project, task, bug, story, build, team, dynamic, status, batch, and guarded create/preview workflows.
---

# Company PM OpenCLI

Use this skill when the task should run through the local `opencli company-pm ...` command set.

## Dependencies

Required:
- `opencli`
- the OpenCLI browser bridge / browser extension
- a browser profile that is already logged into `https://pms.uniontech.com` for PMS/Zentao commands

Also note:
- PMS/Zentao commands reuse browser login state
- product feedback commands require `COMPANY_PM_APP_KEY` and `COMPANY_PM_SIGN`

## Safety

Default posture:
- read-only or preview-first

Write protection:
- `create-product`
- `create-task`
- `create-story`

These commands stay non-destructive unless:
- the command is given `--apply true`
- and `COMPANY_PM_ALLOW_WRITE=1` is set

## Preferred workflow

1. Check command surface:
   - `opencli company-pm --help -f yaml`
2. Check PMS login state:
   - `opencli company-pm status -f json`
3. Use read commands first:
   - `list-products`
   - `list-projects`
   - `browse-product`
   - `view-product`
   - `project-tasks`
   - `project-team`
4. Use preview before write:
   - `create-task ... -f json`
   - `create-story ... -f json`
   - `create-product ... -f json`
5. Use `batch --file ...` for multi-step execution
   - supports `$prev...`
   - supports basic skip conditions
   - supports simple retry
6. Treat `product-bugs`, `product-stories`, `product-plans`, and `product-releases` as permission-sensitive
