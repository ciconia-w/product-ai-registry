---
inclusion: manual
---

# 本机 DTK 控件映射

本参考用于消除“构建时盲猜本机 DTK 有没有某个控件、该从哪里导入、该优先用哪个”的问题。

## 已验证的本机 QML 模块路径

- 公共 DTK 控件模块：`/usr/lib/x86_64-linux-gnu/qt6/qml/org/deepin/dtk/qmldir`
- DTK 设置模块：`/usr/lib/x86_64-linux-gnu/qt6/qml/org/deepin/dtk/settings/qmldir`

## 导入方式

```qml
import org.deepin.dtk 1.0 as D
import org.deepin.dtk.settings 1.0 as Settings
```

## 已验证存在的公共控件

- 顶层窗口与窗口控件：
  - `D.ApplicationWindow`
  - `D.TitleBar`
  - `D.DialogTitleBar`
  - `D.WindowButton`
  - `D.WindowButtonGroup`
- 菜单与通知：
  - `D.Menu`
  - `D.MenuItem`
  - `D.MenuSeparator`
  - `D.ThemeMenu`
  - `D.FloatingMessage`
- 对话框：
  - `D.Dialog`
  - `D.AboutDialog`
  - `Settings.SettingsDialog`
- 输入与常用控件：
  - `D.SearchEdit`
  - `D.LineEdit`
  - `D.PasswordEdit`
  - `D.ComboBox`
  - `D.Switch`
  - `D.CheckBox`
  - `D.ProgressBar`
  - `D.RecommandButton`
  - `D.WarningButton`
  - `D.ToolButton`
- 视觉与表面：
  - `D.StyledBehindWindowBlur`

## 必须优先使用的映射

### 1. 主窗口按钮

- 如果顶层窗口需要最小化、最大化 / 还原、关闭按钮，并且本机 DTK 已导出 `D.WindowButtonGroup`，默认必须直接使用 `D.WindowButtonGroup`。
- 不要再用一组 `D.ToolButton`、`Button` 或自绘 icon row 重做一套窗口按钮。
- 只有在 `D.WindowButtonGroup` 明确无法满足目标布局时，才允许窄范围 fallback，并且必须写 `uos-design: allow-custom-window-buttons`。

### 2. 设置对话框

- 应用级设置页 / 设置对话框默认使用 `Settings.SettingsDialog`。
- 不要为设置界面另起自定义 `Popup`、`Dialog` 容器或自绘设置窗框。

### 3. About

- About 入口默认使用 `D.AboutDialog`。

### 4. 菜单

- 主菜单内容默认使用 `D.Menu`、`D.MenuItem`、`D.MenuSeparator`。
- 主题切换默认优先复用 `D.ThemeMenu` 或在 `D.Menu` 内组织 `System / Light / Dark` 三态菜单项。
- `D.WindowButtonGroup` 不包含主菜单按钮。它只负责最小化、最大化 / 还原、关闭这一组窗口控制。
- 本机公开导出的 `D.ThemeMenu` 不是一个可直接放进 `RowLayout` / `anchors` 的按钮控件，它更接近 DTK 提供的菜单对象或主题菜单内容，而不是公开的顶层 menu-button。
- 本机公开导出的 DTK 模块里没有单独的 `MenuButton` 类型。不要因此去发明自定义 `AppButton` 或 plain `Button`。
- 当设计基线允许使用完整 `D.TitleBar` 时，优先沿用其标准菜单 affordance。
- 当设计基线禁止完整 `D.TitleBar`，例如持久左侧栏应用必须使用控制中心式左右结构时，由于本机没有公开 `MenuButton` 导出，顶部主菜单入口默认使用一个最小化的 `D.ToolButton` 作为 `D.Menu` 或 `D.ThemeMenu` 的附着触发器。这个公开 DTK trigger 路径只能承担“触发标准 DTK 菜单”这一个职责：
  - 不得手绘按钮背景或重做模板
  - 不得手动写死菜单 `x` / `y`
  - 不得把“本机没有 MenuButton 导出”当成放弃 DTK 菜单体系的理由
  - 优先使用 `D.ToolButton` 而不是 plain `Button`、`AppButton` 或自绘模板

### 5. 侧栏 blur

- 侧栏 blur 默认使用 `D.StyledBehindWindowBlur`。
- 这只是 blur primitive，不等于你可以随意写混色层。具体颜色和透明度必须回到 `references/foundations/colors.md` 和 `references/components/control-center-sidebar.md`。

### 6. 搜索输入

- 侧栏或页面顶部搜索框默认使用 `D.SearchEdit`，不要自己拼一个 `LineEdit + icon`。

## 直接禁用的误用

- 不要因为图标要用 SVG，就把 `D.WindowButtonGroup`、`D.Menu`、`D.Dialog`、`Settings.SettingsDialog` 替换成自定义控件。
- 不要因为顶层是左右分栏，就把窗口按钮整套改写为 `ToolButton` 集合。
- 不要因为控件外观“看起来不够像设计稿”，就跳过本机 DTK 已明确存在的控件实现路径。
