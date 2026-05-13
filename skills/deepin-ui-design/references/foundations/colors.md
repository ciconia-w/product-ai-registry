---
inclusion: manual
---

# 颜色系统

## 主题模式
```qml
property string mode: "system" // "system" | "light" | "dark"

readonly property bool dark: mode === "dark" ||
    (mode === "system" && Qt.styleHints.colorScheme === Qt.ColorScheme.Dark)
```

## DTK / 系统调色板映射
- 优先把下列主题变量绑定到 DTK 或系统调色板。
- 文档中的字面量色值是自定义组件的 fallback，不应优先覆盖系统主题。
- 根据参考图，交互色分成 4 个语义层级：
  - 普通状态
  - 悬停 / 强调状态
  - 激活状态前景
  - 激活状态背景
- 不要把纯黑 / 纯白作为默认正文色；它们更适合强调、悬停或高对比标题。
- 所有蓝色语义都必须从 `systemAccent` 派生，不直接在业务组件中写死蓝色值。

## 强制基线

- 生产代码默认必须从本文件给出的浅色 / 深色中性基线开始，不要自行发明带明显蓝、青、绿、紫倾向的桌面底色。
- 对于 UOS / Deepin 桌面工具型应用，`bg`、`bgPanel`、`popupBg`、`textPrimary`、`textStrong`、`iconNormal`、`iconStrong`、`sidebarBlurBlend`、`sidebarBlurFallback` 这些核心 token 默认不得偏离本文件语义。
- 如果产品真的需要偏离这些中性基线，必须写明平台和品牌原因，并加 `deepin-design: allow-theme-baseline-deviation`。没有这个 waiver，就按“颜色实现错误”处理，而不是按“风格选择”处理。
- `systemAccent` 必须直接来自 `D.DTK.palette.highlight` 或等效 DTK / 系统活动色来源；不要自己写一个近似蓝色代替系统活动色。
- `textPrimary` / `iconNormal` 应回到 70% 黑白语义，`textStrong` / `iconStrong` 应回到 100% 黑白语义。不要把正文和基础图标改成偏蓝、偏灰蓝、偏青或偏彩色前景。
- 对持久左侧栏应用，侧边栏 blur 层必须呈现为“中性近白玻璃”或“中性近黑玻璃”，而不是带色偏的实心面板：
  - 浅色主题默认接近 `rgba(255, 255, 255, 0.80)`
  - 深色主题默认接近 `rgba(16, 16, 16, 0.80)`
- 如果你实现出来的浅色侧栏看起来像浅蓝卡片、深色侧栏看起来像海军蓝 / 墨蓝面板，就应视为未通过，而不是“可接受的主题变体”。

### 黑白前景基准
- 以下色值用于描述浅色 / 深色主题中的基础前景语义，实际落地时优先映射到现有主题变量。
- **70% 黑**：`rgba(0, 0, 0, 0.70)`。用于所有浅色主题下 UI 场景的普通状态，例如正文文字、默认功能图标等常规前景内容。
- **70% 白**：`rgba(255, 255, 255, 0.70)`。用于所有深色主题下 UI 场景的普通状态，例如正文文字、默认功能图标等常规前景内容。
- **100% 黑**：`rgba(0, 0, 0, 1.00)`。用于浅色主题下的悬停态或强调内容，例如鼠标悬停后的文字、图标，或需要提升视觉权重的信息。
- **100% 白**：`rgba(255, 255, 255, 1.00)`。用于深色主题下的悬停态或强调内容，例如鼠标悬停后的文字、图标，或需要提升视觉权重的信息。

## 背景色

### 基础背景基准
- 以下色值用于描述桌面应用中最常见的背景层级，实际落地时优先映射到现有主题变量，例如 `bg`、`bgPanel`、`popupBg`、`surfaceHover` 等。
- **主窗口背景**：浅色主题使用 `#F8F8F8`，深色主题使用 `#181818`。用于应用主窗口和大面积内容画布的基础底色。
- **对话框背景**：浅色主题使用 `rgba(240, 240, 240, 0.70)`，对应基色 `#F0F0F0`；深色主题使用 `rgba(24, 24, 24, 0.70)`，对应基色 `#181818`。用于模态对话框、浮层面板等需要轻微通透感的容器背景。
- **侧边栏背景**：浅色主题使用 `rgba(255, 255, 255, 0.80)`；深色主题使用 `rgba(16, 16, 16, 0.80)`，对应基色 `#101010`。用于导航侧栏、资源面板等附属区域背景。
- **菜单背景**：浅色主题使用 `rgba(238, 238, 238, 0.80)`，对应基色 `#EEEEEE`；深色主题使用 `rgba(24, 24, 24, 0.80)`，对应基色 `#181818`。用于菜单、快捷操作面板等轻量弹出层背景。
- **Hover 背景**：浅色主题使用 `rgba(0, 0, 0, 0.10)`，深色主题使用 `rgba(255, 255, 255, 0.10)`。用于列表项、按钮、菜单项等组件在鼠标悬停时的背景反馈。
- **侧边栏 blur 混色**：浅色主题默认使用接近 `rgba(255, 255, 255, 0.80)` 的中性白玻璃，深色主题默认使用接近 `rgba(16, 16, 16, 0.80)` 的中性黑玻璃。透明度过高会把 blur 压成实心色块，颜色带明显色偏会直接偏离 UOS / Deepin 基线。

```qml
readonly property color bg: dark ? "#181818" : "#F8F8F8"
readonly property color bgPanel: dark ? Qt.rgba(16/255, 16/255, 16/255, 0.80) : Qt.rgba(1, 1, 1, 0.80)
readonly property color bgToolbar: bgPanel
readonly property color cardBg: dark ? Qt.rgba(24/255, 24/255, 24/255, 0.70) : Qt.rgba(240/255, 240/255, 240/255, 0.70)
readonly property color cardThumbBg: dark ? Qt.rgba(1, 1, 1, 0.06) : Qt.rgba(0, 0, 0, 0.04)
```

## 表面色
```qml
readonly property color surface: dark ? Qt.rgba(1,1,1,0.06) : Qt.rgba(0,0,0,0.06)
readonly property color surfaceHover: dark ? Qt.rgba(1,1,1,0.10) : Qt.rgba(0,0,0,0.10)
readonly property color surfaceActive: dark ? Qt.rgba(1,1,1,0.14) : Qt.rgba(0,0,0,0.12)
readonly property color glass: dark ? Qt.rgba(1,1,1,0.06) : Qt.rgba(0,0,0,0.04)
readonly property color glassBorder: dark ? Qt.rgba(1,1,1,0.12) : Qt.rgba(0,0,0,0.10)
readonly property color glassHover: dark ? Qt.rgba(1,1,1,0.10) : Qt.rgba(0,0,0,0.10)
```

## 弹窗色
```qml
readonly property color popupBg: dark ? Qt.rgba(24/255, 24/255, 24/255, 0.80) : Qt.rgba(238/255, 238/255, 238/255, 0.80)
readonly property color panelBg: dark ? Qt.rgba(24/255, 24/255, 24/255, 0.70) : Qt.rgba(240/255, 240/255, 240/255, 0.70)
readonly property color scrim: dark ? Qt.rgba(0, 0, 0, 0.30) : Qt.rgba(0, 0, 0, 0.16)
```


## 边框色
```qml
readonly property color border: dark ? Qt.rgba(1,1,1,0.08) : Qt.rgba(0,0,0,0.08)
readonly property color borderStrong: dark ? Qt.rgba(1,1,1,0.14) : Qt.rgba(0,0,0,0.14)
readonly property color divider: dark ? Qt.rgba(1,1,1,0.08) : Qt.rgba(0,0,0,0.08)
readonly property color focusRing: accentForeground
```

## 语义前景色
```qml
readonly property color previewAccent: dark ? "#1D56C6" : "#3678E6"

// 生产代码必须绑定到 DTK / 系统活动色；previewAccent 仅用于文档预览
property color systemAccent: previewAccent

readonly property color fgNormal: dark ? Qt.rgba(1,1,1,0.70) : Qt.rgba(0,0,0,0.70)
readonly property color fgStrong: dark ? Qt.rgba(1,1,1,1.00) : Qt.rgba(0,0,0,1.00)
readonly property color accentForeground: dark
    ? Qt.lighter(systemAccent, 1.18)
    : Qt.darker(systemAccent, 1.12)
readonly property color accentBackground: systemAccent
readonly property color onAccent: "#FFFFFF"
```

## 文字色
```qml
readonly property color textPrimary: fgNormal
readonly property color textStrong: fgStrong
readonly property color textSecondary: dark ? "#9C9CA2" : "#767676"
readonly property color textMuted: dark ? "#727278" : "#A1A1A6"
readonly property color textDisabled: dark ? "#5C5C61" : "#C2C2C7"
readonly property color placeholder: textMuted
readonly property color linkText: accentForeground
```

## 强调色
```qml
readonly property color accent: accentBackground
readonly property color accentLight: Qt.lighter(systemAccent, dark ? 1.14 : 1.08)
readonly property color accentDark: Qt.darker(systemAccent, dark ? 1.16 : 1.12)
readonly property color accentGlow: Qt.rgba(
    systemAccent.r,
    systemAccent.g,
    systemAccent.b,
    dark ? 0.30 : 0.22
)
```

## 功能色
```qml
readonly property color success: dark ? "#00C853" : "#4caf7d"
readonly property color warning: dark ? "#FF9800" : "#f0a050"
readonly property color danger: dark ? "#F44336" : "#e05555"
```

## 图标色
- `Theme.iconNormal`、`Theme.iconStrong`、`Theme.iconAccent` 用于交互图标语义。
- `Theme.textMuted` 属于次要文字语义，不应用作默认导航、工具栏、按钮或列表操作图标色。
- 颜色字面量应尽量只保留在中心主题文件中；页面和组件优先消费这些图标颜色变量，而不是自己写死颜色。
```qml
readonly property color iconNormal: fgNormal
readonly property color iconStrong: fgStrong
readonly property color iconHover: fgStrong
readonly property color iconAccent: accentForeground
```

## 标题栏与标签页
```qml
readonly property color titlebarBg: bgPanel
readonly property color titlebarHover: dark ? Qt.rgba(1,1,1,0.10) : Qt.rgba(0,0,0,0.10)
readonly property color titlebarActive: dark ? Qt.rgba(1,1,1,0.14) : Qt.rgba(0,0,0,0.12)

readonly property color tabActive: surfaceActive
readonly property color tabHover: surfaceHover
readonly property color tabInactive: "transparent"
readonly property color itemHover: surfaceHover
readonly property color selectionFill: accentBackground
readonly property color selectionText: onAccent
```

## 颜色工具函数
```qml
function withAlpha(color, alpha) {
    return Qt.rgba(color.r, color.g, color.b, alpha)
}

function mix(colorA, colorB, amount) {
    const t = Math.max(0, Math.min(1, Number(amount)))
    return Qt.rgba(
        colorA.r + (colorB.r - colorA.r) * t,
        colorA.g + (colorB.g - colorA.g) * t,
        colorA.b + (colorB.b - colorA.b) * t,
        colorA.a + (colorB.a - colorA.a) * t
    )
}

function luminance(color) {
    function linearChannel(value) {
        const v = Math.max(0, Math.min(1, Number(value)))
        return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
    }
    return 0.2126 * linearChannel(color.r)
         + 0.7152 * linearChannel(color.g)
         + 0.0722 * linearChannel(color.b)
}

function contrastRatio(colorA, colorB) {
    const l1 = luminance(colorA)
    const l2 = luminance(colorB)
    const lighter = Math.max(l1, l2)
    const darker = Math.min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)
}
```
