# WorkBuddy Input Dropdown Audit

Verified on `2026-07-13` against `WorkBuddy` macOS desktop `v5.2.5`.

## Inventory

Observed explicit dropdowns inside or directly attached to the composer:

1. `+号菜单` (`更多操作`)
2. `选择工作空间`
3. `默认权限`
4. `自动` model selector

Observed dynamic triggers:

1. `@` reference current-conversation files
2. `/` call skills or instructions

## Verified behaviors

### 1. `+` menu (`更多操作`)

- Trigger: click the `+` button at the lower-left corner of the composer.
- Open result: a floating menu above the composer.
- First-level items: `添加文件`, `模式`, `专家`, `技能`, `连接器`.
- Interaction shape: every item shows a chevron, so the menu behaves as an entry hub rather than a one-shot action list.
- Close: `Esc` verified; opening another dropdown also hides it.

### 2. Workspace selector

- Trigger: click `选择工作空间` in the lower-left bar of the new-task composer.
- Open result: a popup with an auto-focused `搜索工作空间` field.
- Empty-state content: `未找到工作空间`.
- Follow-up actions: `新建工作空间`, `打开本地文件夹`.
- Interaction implication: this is a combined chooser plus creation/import entry, not a simple select.

### 3. Permission selector

- Trigger: click `默认权限`.
- Open result: a compact explanatory popover.
- Contents:
  - default sandbox explanation
  - `允许完全访问` toggle
- Interaction implication: this is a risk-control switch, not a cosmetic setting.

### 4. Model selector

- Trigger: click `自动`.
- Open result: a large model panel anchored to the right side of the composer.
- Verified content:
  - `Max 模式` toggle
  - `Auto` as the default selected mode
  - model list with capability or pricing badges
  - `配置自定义模型`
- Observed models include `Hy3`, `GLM-5.2`, `GLM-5.1`, `GLM-5v-Turbo`, `MiniMax-M3`, `Kimi-K2.7-Code`, `Kimi-K2.6`, `Deepseek-V4-Flash`, `Deepseek-V4-Pro`.

## State-dependent dynamic triggers

### 5. `@`

- In an existing conversation with no files, typing `@` opens a strip-like reference panel saying `当前对话中暂无文件`.
- In a fresh new-task composer, typing `@` only inserted the character during this run and did not consistently show the same panel.
- Interpretation: `@` is scoped to current conversation resources and its visible feedback depends on whether the current thread has already materialized referenceable objects.

### 6. `/`

- Placeholder text explicitly promises `/ 调用技能与指令`.
- In this verification run on desktop `v5.2.5`, typing `/` did not reliably surface a visible command panel in either the history-thread composer or the fresh new-task composer.
- Possible explanations:
  - the command list appears only after additional characters
  - it depends on conversation or workspace context
  - the desktop build has unstable first-trigger behavior here
- Product takeaway: the promise in placeholder copy is stronger than the immediate feedback observed in this run.

## Competitor-analysis takeaways

### Strengths

- The composer concentrates files, workspace, permissions, models, and capability routing in one place.
- The design follows a good pattern of safe or automatic defaults with deeper expandable control.
- The workspace popup handles empty state well by offering creation and import next steps.

### Risks

- Entry density is high, so discoverability depends on prior user knowledge.
- `@` feedback is inconsistent across thread states.
- `/` currently reads as an advertised affordance with unstable first feedback.
- `更多操作` centralizes many capabilities efficiently, but its labels are abstract for exploratory users.

### Reusable one-line assessment

WorkBuddy's composer behaves less like a plain input box and more like a lightweight task-orchestration surface: high capability density, but still uneven in state consistency for `@` and `/`.
