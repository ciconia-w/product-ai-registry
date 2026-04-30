---
inclusion: manual
---

# 设计系统 - 快速参考指南

## 快速开始

- 优先使用 DTK 原生控件；以下模板主要用于无法直接复用 DTK 时的 fallback。
- 窗口化弹窗、frameless 标题栏和 blur 都需要先参考 `platform-compatibility.md`。
- 字体默认跟随系统 UI 字体和系统字号层级；不要在常规业务界面里写死字体族或固定 px 字号。

### 导入主题
- 在主题对象中统一暴露 `Theme.bg`、`Theme.textPrimary`、`Theme.fontSans`、`Theme.bodySize` 等主题变量。
- 这里的“主题变量”指 `Theme` 对象上的命名属性，例如颜色变量、字号变量、圆角变量和间距变量。
- 普通业务界面直接消费这些主题变量，不在业务组件里重复定义颜色、字号和圆角。
- `Theme.fontSans` 和 `Theme.bodySize` 应绑定到系统字体与系统字号层级，而不是写死具体数值。

---

## 常用颜色速查

### 背景色
- `Theme.bg`：主窗口背景。
- `Theme.bgPanel`：侧边栏或附属面板背景。
- `Theme.bgToolbar`：自绘标题栏与工具栏合一场景的背景。
- `Theme.surface`：控件表面背景。
- `Theme.surfaceHover`：通用悬停背景。
- `Theme.surfaceActive`：按下、激活或选中背景。
- `Theme.popupBg`：菜单等轻量弹出层背景。
- `Theme.panelBg`：对话框和浮层面板背景。
- `Theme.cardBg`：卡片背景。

### 文字色
- `Theme.textPrimary`：普通正文、默认图标文字。
- `Theme.textStrong`：标题、悬停强调、关键数值。
- `Theme.textSecondary`：次要说明文字。
- `Theme.textMuted`：弱化文本、元信息。
- `Theme.textDisabled`：禁用态文字。

### 强调色
- `Theme.systemAccent`：系统活动色源。
- `Theme.accentForeground`：激活态前景，如链接、当前步骤、选中图标。
- `Theme.accentBackground`：激活态背景，如主按钮、当前页、选中填充。
- `Theme.accent`：`accentBackground` 的兼容别名。
- `Theme.success`：成功态。
- `Theme.warning`：警告态。
- `Theme.danger`：危险或错误态。

### 边框色
- `Theme.border`：常规边框。
- `Theme.borderStrong`：强调边框。
- `Theme.divider`：分割线。

---

## 常用尺寸速查

### 圆角
- `Theme.radiusSm`：小控件圆角，建议值 `6`。
- `Theme.radiusMd`：中型容器圆角，建议值 `12`。
- `Theme.radiusLg`：大型浮层或对话框圆角，建议值 `18`。
- `Theme.radiusXl`：超大容器的保留档位，按场景单独评估。
- `Theme.radiusPill`：胶囊形或全圆角，建议值 `50%`。

### 间距
- `Theme.spacingXS`：超小间距，建议值 `4`。
- `Theme.spacingS`：小间距，建议值 `6`。
- `Theme.spacingM`：常规间距，建议值 `10`。
- `Theme.spacingL`：区块间距，建议值 `20`。
- `Theme.spacingXL`：页面级边距，建议值 `30`。

### 动画时长
- `Theme.animFast`：悬停、点击等快速反馈，建议值 `120`。
- `Theme.animNormal`：展开、切换等常规过渡，建议值 `200`。
- `Theme.animSlow`：大型布局变化或慢速反馈，建议值 `350`。

---

## 常用组件模板

### 按钮
- 优先使用 DTK 按钮。
- 自定义 fallback 按钮以内容驱动宽度，并保留足够点击热区。
- 主按钮使用 `Theme.accentBackground`，次要按钮使用 `Theme.surface` 或透明背景。
- 交互上覆盖悬停、按下、焦点、键盘激活和无障碍语义。

### 输入框
- 结构上通常由输入区域、占位提示和焦点边框构成。
- 高度应与按钮、下拉框等基础控件保持统一。
- 焦点态优先通过边框和光标清晰表达，而不是靠过强的背景变化。

### 列表项
- 列表项默认占满可用宽度，高度按单行或双行信息层级决定。
- 悬停使用 `Theme.surfaceHover`，选中使用更明确的激活态背景或指示条。
- 列表项必须支持键盘导航和无障碍名称。

### 卡片
- 卡片用于承载缩略图、标题、描述和轻量操作。
- 标题与描述保持明确层级，容器圆角使用 `Theme.radiusMd`。
- 可在悬停时提供轻微抬升或阴影变化，但不应破坏整体稳定感。

---

## 动画模板

### 颜色过渡
- `color` 变化优先使用 `Theme.animFast`。
- 颜色动画主要用于 hover、pressed 和轻量状态切换。

### 尺寸变化
- `width`、`height` 或布局相关属性变化优先使用 `Theme.animNormal`。
- 缓动曲线以 `Easing.OutCubic` 一类直接、平稳的曲线为主。

### 淡入淡出
- 进入阶段使用短时淡入。
- 退出阶段通常略短于进入阶段，避免界面响应拖慢。

### 缩放动画
- 缩放只作为轻微辅助，不作为主表现手段。
- 弹窗、卡片或提示层可配合淡入做很小幅度的缩放。

---

## 布局模式

### 水平布局
- 适用于图标 + 文本、操作按钮组、表单行内组合等场景。
- 项之间使用 `Theme.spacingM` 或更小间距保持节奏。

### 垂直布局
- 适用于标题 + 描述、卡片内容、表单分组等场景。
- 垂直间距优先使用 `Theme.spacingS` 或 `Theme.spacingM`。

### 网格布局
- 适用于卡片墙、资源列表和数据面板。
- 列数、卡片宽度和间距需跟随窗口宽度变化，而不是写死固定网格。

---

## 响应式设计

### 断点定义
- 桌面应用至少区分紧凑、中等和宽屏三个档位。
- 断点主要用来控制侧边栏折叠、工具栏简化、内容显隐和间距压缩。

### 自适应布局
- 窗口变窄时，优先折叠侧边栏、次级面板和说明区。
- 不要优先缩小字号或压缩点击热区。

---

## 性能优化清单

### 推荐做法
- 使用 `Behavior` 而非手动堆叠过多动画对象。
- 使用 `Loader` 延迟加载重型组件。
- 避免深层嵌套绑定和频繁重算。
- 对只读主题变量使用 `readonly property`。

### 避免做法
- 不要在循环中创建大量对象。
- 避免频繁调用 `grabToImage`。
- 除承担桌面主导航的持久左侧栏外，不要把 blur 当作所有界面的默认必选项。
- 避免把复杂业务逻辑直接塞进属性绑定。

---

## 可访问性清单

### 键盘导航
- 所有交互组件支持 `Tab` 聚焦。
- `Enter` / `Space` 激活当前控件，`Esc` 关闭相关浮层。
- 菜单、列表和标签页还要支持方向键导航。

### 对比度要求
- 正文文字至少 `4.5:1`。
- 大号文字至少 `3:1`。
- 图标和控件至少 `3:1`。

### 焦点指示
- 焦点样式应清晰可见，优先使用 `Theme.focusRing` 或等价边框。
- 焦点不应只靠文字颜色变化表达。

---

## 调试技巧

### 显示边界
- 调试布局时可临时打开边框或背景层，确认间距、裁切和对齐关系。

### 性能计时
- 在组件初始化、列表首次渲染和大图加载等关键节点记录耗时。

### 属性监控
- 对窗口宽度、布局断点、弹窗开关和滚动状态做最小必要监控，便于定位布局异常。

---

## 设计决策流程

### 选择颜色
1. 背景层：`Theme.bg` / `Theme.bgPanel`
2. 控件表面：`Theme.surface`
3. 交互状态：`Theme.surfaceHover` / `Theme.surfaceActive`
4. 系统活动色源：`Theme.systemAccent`
5. 激活前景：`Theme.accentForeground`
6. 激活背景：`Theme.accentBackground`
7. 功能色：`Theme.success` / `Theme.warning` / `Theme.danger`

### 选择圆角
- 小控件：`radiusSm`
- 中型容器：`radiusMd`
- 大型浮层：`radiusLg`
- 胶囊或状态点：`radiusPill`

### 选择间距
- 紧密元素：`spacingXS`
- 相关元素：`spacingS`
- 常规间距：`spacingM`
- 区块间距：`spacingL`
- 页面边距：`spacingXL`

### 选择动画
- 即时反馈：`Theme.animFast`
- 状态切换：`Theme.animNormal`
- 布局变化：`Theme.animSlow`

---

## 常见问题

### Q: 如何实现毛玻璃效果？
- 先提供纯色或半透明背景回退。
- 在 compositor 支持且性能允许时，再启用 `GlassLayer`、`WindowBlur` 或 `MultiEffect`。
- 毛玻璃更适合侧边栏、抽屉和浮动面板，不适合全局滥用。

### Q: 如何实现深浅主题切换？
- `Theme.mode` 默认使用 `system`。
- 根据 `dark` 状态切换中性色、表面色和前景色，不直接在业务组件里写死浅深两套颜色。

### Q: 如何优化列表性能？
- 数据量较大时使用 `ListView`，并开启合适的缓存和项复用。
- 列表项 delegate 保持轻量，避免在每一项内叠加复杂效果。

### Q: 如何实现拖动排序？
- 拖拽排序适合卡片、标签或列表项等同层级元素。
- 拖动反馈要和普通点击反馈区分开，并明确放置目标位置。

---

## 资源链接

### 相关文档
- `references/foundations/colors.md` - 颜色与主题变量
- `references/foundations/typography.md` - 字体、字号、字重
- `references/foundations/radius.md` - 圆角规范
- `references/foundations/spacing.md` - 间距规范
- `references/foundations/animation.md` - 动画时长与缓动
- `references/design-system-window-behavior.md` - 窗口行为规范
- `references/design-system-layout.md` - 布局模式与响应式规范
- `references/components/` - 各组件的独立参考文档

### 示例项目
- 笔记应用设计参考
- 浏览器界面设计参考

---

## 版本历史

**v1.0** - 2026-03-17
- 基于团队项目整理
- 完整的颜色系统
- 排版和间距规范
- 圆角和动画系统
- 模糊效果实现
- 窗口行为规范
- 完整的控件库
- 最佳实践指南
