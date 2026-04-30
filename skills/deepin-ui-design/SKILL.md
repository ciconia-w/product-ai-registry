---
name: deepin-ui-design
description: Reference a deepin/DTK QML design system for DTK-first desktop UI work on Linux desktops. Use when designing, implementing, or reviewing theme variables, layout, window behavior, platform compatibility, blur effects, common desktop components, or mandatory control-center style left-sidebar desktop layouts.
---

# UOS Design

Use this skill when the user is building or reviewing a UOS or Deepin style desktop interface in QML, especially for DTK-first applications.

## When To Use

Use this skill for requests about:
- theme variables such as colors, typography, spacing, radius, and animation
- desktop layout patterns, sidebars, title bars, and window behavior
- blur effects, glass surfaces, and other UOS visual conventions
- common QML components such as buttons, inputs, dialogs, menus, tables, and forms
- auditing an interface for consistency with the UOS design language

Do not use this skill for generic web design unless the user explicitly wants the UOS or Deepin visual style.

## Workflow

1. Route the request with `references/design-system-modular.yaml` and `references/platform-compatibility.md`.
2. Before proposing or writing QML, inspect the local environment for:
   - target Qt version
   - availability of `org.deepin.dtk` / `Dtk6Declarative`
   - the local DTK export map in `references/local-dtk-controls.md`, backed by the actual `qmldir` files on disk
   - target session type (`Wayland` or `X11`) when windowing or popup behavior matters
   - build integration points (`CMakeLists.txt`, `main.cpp`, QML imports)
   - whether the current Qt/DTK/window-manager combination can actually render a unified titlebar-toolbar as a single window-manager-owned top band; do not infer this from `X11`, `Wayland`, `xcb`, or `wayland` alone
3. Read only the files needed for the task.
4. For any multi-group settings window or any request that references 设置窗口, settings dialog, 偏好设置, or 系统设置样式的应用内设置页, also read `references/components/settings.md` together with `references/components/dialog.md`.
5. Treat the deployed control-center runtime behavior as authoritative for that baseline. Startup should be interpreted as entering the persistent left-navigation split-pane layout because the runtime code disables the home page by default.
6. Map the requested UI to documented components and then to locally available DTK controls.
7. If DTK provides the control, use DTK directly instead of wrapping plain Qt Quick Controls for styling convenience.
8. Only fall back to custom QML or plain Qt Quick Controls when you can state the exact missing DTK capability, version limitation, or platform constraint.
9. Keep every fallback narrow and explicit; do not build a parallel non-DTK design system when DTK is available.
10. For top-level windows, preserve window-manager-owned decorations and behaviors first. If the validated Qt/DTK/platform combination supports a unified titlebar-toolbar presentation without giving up window-manager border, shadow, rounded corners, move, resize, maximize, snap, and related behaviors, use that. Otherwise keep the system-decorated title bar and place the app toolbar directly below it.
11. If the user explicitly requires a unified titlebar-toolbar presentation by default with a system-decorated fallback, treat that as a dual-path requirement. Implement the validated unified-by-default path plus the fallback path, or state the exact platform blocker before coding. Fallback-only is not a completed implementation for that request.
12. For requests that require unified titlebar-toolbar by default, validate the result at runtime after implementation in both normal and maximized states. A unified path is valid only if the final UI shows one top header band rather than a system title bar plus a second in-content toolbar, and the DTK main-menu / window-control cluster stays visible, clickable, and unclipped at the top-right edge in both states.
13. Reuse documented theme variables instead of inventing new values.
14. Verify that any theme variable name, property, or component name used in an answer is defined in the referenced files.
15. Run `scripts/audit_uos_qml.sh <repo-root>` before substantial UI edits and again before finishing. Treat every finding as blocking unless you fix it or add a narrow waiver that the skill allows.
16. Treat this design skill as authoritative for colors and sizes. If a product or requirement document conflicts on any color token, spacing value, size, or typography number, follow this skill first and treat the requirement document only as supplementary context.
17. For persistent sidebars, keep the sidebar/content split at zero structural gap, place the visible `1px` divider on the sidebar edge itself, hide single-group headers, keep multi-group gaps at `20px`, and dock operational cards to the sidebar bottom with `10px` outer margins.
18. Operational cards are opt-in, not mandatory decoration. Remove non-essential cards by default, remove cards whose only action is an in-app page jump, move any top-of-app operational prompt into the sidebar card area, and never repeat the same or equivalent message in multiple surfaces.
19. For variable-length lists such as file lists, app or program lists, startup-item or service lists, data lists, and other repeated result surfaces, default to compact rows that stay within one or two lines. Do not let unpredictable content expand into sprawling multi-line delegates by default.
20. Do not render those variable-length file/app/program/startup/service/data lists as one large standalone card per item with stacked sub-sections by default. Use compact responsive rows, and if you reuse a row primitive such as `SettingRow` or `SettingsOptionRow`, keep it compact and responsive instead of inheriting oversized fixed gutters or control columns.
21. In search-and-filter bands, give the search control the dominant share and keep filters secondary. Search placeholder hints should appear only while the search control is active.
22. All application dialogs must use standard DTK dialog types when they exist locally. For desktop-standard dialogs on this machine, default to `D.DialogWindow`; use `Settings.SettingsDialog` for multi-group settings and `D.AboutDialog` for About surfaces. Treat `D.Dialog` as a popup-style exception only, not as the normal desktop dialog path. Do not custom-draw dialog shells, frames, or button areas.
23. For `Settings.SettingsDialog`, follow the local settings-module path end to end: root-level `title` plus `icon`, DTK-owned title bar and shell, standard `Settings.CheckBox` / `Settings.ComboBox` / `Settings.LineEdit` where available, DTK-owned restore-default footer behavior, and a stable window instance rather than recreating the settings window on every open unless a documented waiver explains why.
24. If a persistent sidebar supports collapse, the visual motion must read as the sidebar translating out of view and back in, not as a width squeeze effect.
25. For large titles above `16px`, cap weight at `400`. Large content-area page titles must not prepend icons. For large numeric values with units, render the unit at roughly half the numeric font size.
26. All progress indicators must give the foreground fill or stroke a shadow in the same color family as that foreground. The standard DTK horizontal progress path is acceptable when the runtime result already provides it; custom circular, ring, or arc progress must add that shadow explicitly, keep that shadow light, prevent any clipping at the component edge, and cap stroke thickness at `20px` whenever center text is omitted. Any internal textless progress strip, bar, or track that visually reads as a progress indicator must also keep its visible thickness at `20px` or below regardless of the control type, component name, or local wrapper name.
27. Any scrollbar, horizontal or vertical, must keep its visible thickness at `20px` or below. Do not rely on a thick scrollbar to compensate for an unresponsive layout.
28. For the same numeric ratio on the same surface, do not render both a circular or ring-style progress graphic and a horizontal progress graphic. Choose one visual form only; do not duplicate the same proportion in ring and linear form.
29. Gradient cards must let the gradient reach the card edge. Do not leave neutral padding, white seams, or inset margins around the gradient surface. Do not repeat the same status meaning in both plain text and badge/tag form within one surface. Option and settings card lists must use explicit, scene-correct per-item icons rather than one shared placeholder icon or one repeated delegate-level constant icon. Repeated functional rows must derive icon identity from per-item data or a per-item resolver keyed by item identity. Unified titlebar-toolbar surfaces must use the standard DTK toolbar path at `50px` height with no extra divider line.
30. Charts must expose labeled `x` / `y` axes, tick marks, and animated value changes. Curve or polyline series in charts must also use a progress-like same-color shadow plus a top-to-bottom same-hue gradient treatment; do not ship flat unstyled lines.

## File Routing

Start with the smallest relevant set:

- Theme variables:
  - `references/foundations/colors.md`
  - `references/foundations/typography.md`
  - `references/foundations/radius.md`
  - `references/foundations/spacing.md`
  - `references/foundations/animation.md`
- Global rules:
  - `references/design-rules.md`
- Platform compatibility:
  - `references/platform-compatibility.md`
- Layout and windows:
  - `references/design-system-layout.md`
  - `references/design-system-window-behavior.md`
- Broad lookup:
  - `references/design-system-quick-reference.md`
- Local DTK export map:
  - `references/local-dtk-controls.md`
- Machine-readable index:
  - `references/design-system-modular.yaml`
- Bundled tools:
  - `scripts/audit_uos_qml.sh`
- Components:
  - `references/components/button.md`
  - `references/components/input.md`
  - `references/components/menu.md`
  - `references/components/dialog.md`
  - `references/components/settings.md` for any `Settings.SettingsDialog`, multi-group settings window, or settings-window code review
  - `references/components/card.md`
  - `references/components/sidebar.md`
  - `references/components/control-center-sidebar.md` for any desktop application with a persistent primary left sidebar, and always when the user explicitly references 控制中心 / `dde-control-center`
  - `references/components/switch.md`
  - `references/components/slider.md`
  - `references/components/badge.md`
  - `references/components/tab.md`
  - `references/components/combobox.md`
  - `references/components/tooltip.md`
  - `references/components/progress.md`
  - `references/components/list.md`
  - `references/components/blur.md`
  - `references/components/table.md`
  - `references/components/pagination.md`
  - `references/components/skeleton.md`
  - `references/components/drawer.md`
  - `references/components/empty.md`
  - `references/components/avatar.md`
  - `references/components/alert.md`
  - `references/components/notification.md`
  - `references/components/form.md`
  - `references/components/breadcrumb.md`
  - `references/components/stepper.md`

## Implementation Rules

- Treat `org.deepin.dtk` as mandatory when the needed control exists locally. `Prefer DTK` here means `use DTK unless you can prove it is unavailable or insufficient`.
- For main windows, first check whether the locally exported DTK set in `references/local-dtk-controls.md` includes `ApplicationWindow`, `TitleBar`, `WindowButtonGroup`, `Menu`, `ThemeMenu`, `Dialog`, `AboutDialog`, `FloatingMessage`, `StyledBehindWindowBlur`, `SearchEdit`, and `SettingsDialog`. If the local map says the control exists, treat it as available.
- If the local DTK export map includes `WindowButtonGroup`, any top-level minimize / maximize / close cluster must use `D.WindowButtonGroup` by default. Do not rebuild those buttons from `D.ToolButton`, `Button`, icon rows, or custom wrappers unless an exact local DTK limitation is documented with `uos-design: allow-custom-window-buttons`.
- When `D.WindowButtonGroup` is used in a unified top band or split-pane header, place it at the actual top-right edge of that header region. Do not center it inside a wrapper item, offset it inward with decorative gaps, or leave extra right-side dead space between the button group and the window edge unless an explicit `uos-design: allow-offset-window-button-group` waiver explains the platform reason.
- `D.WindowButtonGroup` does not include the application main-menu button. Treat it only as the standard minimize / maximize / close cluster.
- The local DTK export map on this machine does not expose a separate public standalone `MenuButton` type. Therefore, when a main menu exists and local `D.TitleBar` is available, the menu button must be provided by `D.TitleBar.menu` following the same DTK path used by `dde-control-center` in `src/dde-control-center/plugin/DccWindow.qml`. Do not add a separate `ToolButton`, `ActionButton`, custom icon item, or manual `popup()` call for that menu button in any layout.
- The local `D.ThemeMenu` export is not a public top-level button item. Do not misclassify it as the menu trigger itself in split-pane headers; use it as menu content or a DTK menu object where appropriate.
- Do not replace the standard trigger path with a custom `AppButton`, plain `Button`, self-drawn template, or arbitrary icon-only hamburger implementation.
- Application main-menu placement must follow DTK menu-button behavior and attachment conventions. Do not hardcode window-relative `x` or `y` coordinates for the application main menu unless a validated platform constraint is documented.
- In any window that uses `D.TitleBar` or `D.WindowButtonGroup`, treat the top-right DTK main-menu / window-control strip as a reserved safe area in both normal and maximized states. App-side titlebar content, drag zones, search bars, labels, and overlay items must stop before that strip; do not let `D.TitleBar.content`, a `MouseArea`, or another child fill the entire titlebar width unless an explicit trailing reserve keeps that DTK strip unobstructed.
- Do not place `D.TitleBar`, `D.WindowButtonGroup`, or the DTK-owned top-right control strip inside a clipped ancestor chain, and do not cover that strip with a higher-`z` app-side overlay. If page content needs clipping, keep that clipping below the titlebar band instead of around it.
- On this machine, a `D.ApplicationWindow` + `D.TitleBar` main-window path must keep the standard title-bar flag semantics. Do not use `Qt.CustomizeWindowHint` as part of the normal DTK main-window path, and do not drop `Qt.WindowTitleHint` when flags are explicitly set, unless an exact platform defect is documented with `uos-design: allow-customized-window-flags`.
- For persistent-sidebar applications that embed `D.TitleBar` into the right-side top band, keep that top band as a direct window-level sibling region rather than burying it inside the main content column flow. The title bar must stay at the live top edge of the window band in maximized state.
- If the main window itself is transparent and the UI uses a unified or embedded `D.TitleBar` top band, provide an explicit theme-backed title-band surface under that band on the content side, typically `Theme.titlebarBg` or `Theme.bgToolbar`. Do not leave the live toolbar background visually transparent just because the top-level window is transparent.
- In that same transparent-window path, the right-side content base surface must extend underneath the full title-band height. Do not start the content-side base panel only below `chromeHeight`, otherwise the semi-transparent title-band surface will blend with the desktop instead of the app surface and read as an unintended translucent toolbar.
- If the user requests network-downloaded SVG icons, keep icon loading separate from control choice. Custom icon sourcing is not a reason to abandon DTK controls.
- Do not implement custom wrappers around plain Qt Quick Controls for `Button`, `TextField`, `ComboBox`, `Switch`, `CheckBox`, `Menu`, `Dialog`, `ProgressBar`, or window buttons when DTK already provides the control.
- When DTK provides a control, do not replace its standard DTK visual template by overriding structural sub-items such as `background`, `contentItem`, `indicator`, `handle`, `popup`, or `delegate` on `D.Button`, `D.TextField`, `D.ComboBox`, `D.Switch`, `D.CheckBox`, `D.Menu`, `D.Dialog`, `D.ProgressBar`, or related DTK controls unless a narrow platform-specific waiver explains the exact missing DTK capability. Inheriting from a DTK control and then redrawing its template still counts as a custom control implementation.
- All application dialogs, including confirmation, warning, destructive-action, progress, and form dialogs, must use DTK-provided dialog types when they are available locally. On this machine, standard desktop dialogs must default to window-level DTK types: `D.DialogWindow` for general dialogs, `Settings.SettingsDialog` for settings surfaces, and `D.AboutDialog` for About surfaces. These are the paths that preserve the standard DTK dialog result with real window decoration, shadow, rounded corners, blur, move behavior, a top-left icon slot, and a top-right close control. Treat `D.Dialog` as a popup-style or in-content exception only; it is not the normal desktop dialog shell when local `DialogWindow` exists.
- On this machine, standard `D.AboutDialog` and `Settings.SettingsDialog` keep the DTK-owned title bar by default. Do not force either of them back to a window-manager system title bar with `D.DWindow.enabled: false` unless an explicit `uos-design: allow-system-titlebar-on-standard-dtk-surface` waiver explains the exact platform defect.
- When local `org.deepin.dtk.settings` exports `SettingsDialog`, `CheckBox`, `ComboBox`, and `LineEdit`, treat those exact controls as the standard path for multi-group settings windows. Do not rebuild a settings surface from generic dialog content plus custom form rows when the local settings module already exposes the needed controls.
- Every `Settings.SettingsDialog` root must populate the standard window identity fields that affect the runtime shell: keep a root `title`, provide a root `icon` for the top-left icon slot, and preserve the DTK-owned shell and title bar without additional app-side dialog chrome or a forced fallback to the system title bar.
- Inside `Settings.SettingsDialog`, checkbox-style boolean options must use `Settings.CheckBox` when it exists locally. Do not emulate that path with `Settings.OptionDelegate + D.CheckBox` unless an exact local export gap is documented with `uos-design: allow-settings-checkbox-fallback`.
- Inside `Settings.SettingsDialog`, `Settings.ComboBox` and `Settings.LineEdit` remain the preferred path for enum selection and single-line text entry. Reserve `Settings.OptionDelegate` fallback rows for controls the local settings module does not wrap directly, such as `D.Switch`, `D.SpinBox`, a read-only value label, or one explicit action button.
- Any custom fallback row used inside `Settings.SettingsDialog` must still inherit from `Settings.OptionDelegate`, expose one shared trailing control slot or aligned trailing control column, and remain layout-only. Do not inject project-specific fonts, body text colors, hero headings, or visible spacing rhythm through project theme tokens such as `Theme.spacing*` unless an explicit `uos-design: allow-custom-settings-row-metrics` waiver explains the missing DTK metric path.
- If a multi-group settings window offers restore-default behavior, route that behavior through the standard `Settings.SettingsDialog` footer / `SettingsContainer.resetSettings()` path or another DTK-owned bottom restore action. Do not surface “恢复默认设置” as a normal `Settings.SettingsOption` row inside the settings groups unless an explicit `uos-design: allow-custom-settings-reset-entry` waiver explains the local DTK limitation.
- Treat a multi-group settings window as a stable desktop window instance by default. Create it once and reopen or show it again as needed instead of destroying it on close and recreating it on the next open, unless an explicit `uos-design: allow-ephemeral-settings-dialog` waiver explains the ownership or resource constraint.
- Project code should provide only the dialog's text content, semantic state, and action signals; let DTK own the dialog frame, title bar, spacing, buttons, shadow, and other visual styling. Do not build a custom dialog container or dialog frame with `Popup`, plain Qt Quick Controls `Dialog`, a popup-style `D.Dialog`, or a restyled DTK dialog unless a narrow platform-specific waiver explains the exact missing DTK capability.
- For `D.DialogWindow` on this machine, follow the local DTK action-row baseline used by shipped system code: a bottom `RowLayout` with DTK `Button` / `WarningButton` actions, standard spacing, and no `DialogButtonBox` path. Do not substitute a custom footer widget, a plain Qt button box, or a `D.DialogButtonBox` footer for standard desktop dialogs.
- Using `D.Dialog` alone is not sufficient if the runtime result still reads as a custom dialog. Even inside standard DTK dialogs, do not add a second page-style heading, centered hero typography, custom body palette for normal text, faux card sections, dashboard widgets, badge-heavy compositions, or other project-specific dialog styling patterns that make the surface stop looking and behaving like the standard DTK dialog baseline. Let DTK own not only the shell but also the default body rhythm for normal explanatory text and actions.
- Any About entry that opens an About window or dialog must use the DTK standard `AboutDialog` when it is available locally. Do not replace it with a custom about popup or a custom `AppDialog` implementation.
- Any in-app toast, floating message, or transient application notification must use the DTK standard `FloatingMessage` when it is available locally. Do not replace it with a custom `ToastStack`, a custom repeater of notification cards, or another custom in-app notification container unless a narrow platform-specific waiver explains the exact missing DTK capability.
- Do not force `QQuickStyle::setStyle("Basic")`, `Fusion`, `Material`, `Imagine`, or similar non-DTK styles for UOS/Deepin tasks unless the user explicitly asks for that or DTK is unavailable.
- Do not treat `Qt.FramelessWindowHint` or a self-drawn title bar as the default implementation path for UOS/Deepin desktop windows.
- Default to window-manager-owned top-level decorations and behaviors. Use a visually unified header only when the target Qt/DTK/platform combination has been validated to preserve window-manager border, shadow, rounded corners, move, resize, maximize, snap, and related behaviors.
- When the requirement says window rounded corners, border, and shadow must be owned by the window manager, do not tune those effects from app-side QML or application-side DTK decoration properties. Do not use `D.DWindow.windowRadius`, `D.DWindow.borderWidth`, `D.DWindow.borderColor`, `D.DWindow.shadowRadius`, `D.DWindow.shadowOffset`, or `D.DWindow.shadowColor` to visually approximate window-manager decoration ownership unless the user explicitly allows that fallback.
- If a visually unified header path still depends on app-side decoration tuning for top-level rounded corners, border, or shadow, classify that path as not meeting the `window-manager-owned decoration` requirement and fall back to system decorations instead.
- Treat platform identifiers such as `X11`, `Wayland`, `xcb`, `wayland`, Qt version, or DTK version as routing hints only. They are not proof that a unified titlebar-toolbar path is available.
- For desktop applications with a persistent left sidebar, use a mandatory two-panel left-right split layout with no discretionary deviation: the left panel is the sidebar navigation panel and the right panel is the main content panel. This is a hard requirement, not a stylistic suggestion. Do not reinterpret it as a loose `Row`, a top-bottom layout, a sidebar-above-content stack, a floating navigation layer, or any other softened variant.
- For desktop applications with a persistent left sidebar, both panels must be visually explicit. The left side must read as a dedicated sidebar panel, and the right side must read as a dedicated content panel. Do not leave either side as bare transparent space, an implied region, or a content stack that merely happens to sit to the right of navigation.
- For desktop applications with a persistent left sidebar, do not use a full-width `D.TitleBar` or any other full-width top band as the primary top-level structure. The required baseline is the control-center style full-window left-right split, not `full-width title bar + lower content area`. An embedded standard `D.TitleBar` confined to the right-side top band is acceptable when it is used to preserve the standard DTK main-menu path and window controls without collapsing the left-right split.
- For desktop applications with a persistent left sidebar, the sidebar side must own an explicit sidebar panel surface. That surface may be a validated sidebar blur surface, a validated blur-plus-tint composition, or another documented sidebar panel layer, but it cannot be only navigation content placed on bare transparent space.
- For desktop applications with a persistent left sidebar, the right side must own an explicit content-panel surface or page-base surface driven by documented theme background tokens. It is not acceptable for the right side to be only a stack of cards floating directly on transparent window content.
- For desktop applications with a persistent left sidebar, the sidebar surface must use a window-manager or compositor-provided blur path validated for the target environment. Do not fake the sidebar blur with a self-drawn shader, screenshot blur, plain translucent fill, or a local content blur substitute when the requirement is window-manager blur.
- For desktop applications with a persistent left sidebar, sidebar blur is not considered complete unless the runtime visual result still reads as a control-center-like neutral glass surface. If the result reads as a light blue card, a navy panel, or a nearly solid fill with no visible blur, treat it as incorrect even when `StyledBehindWindowBlur` appears in code.
- Even when a top-level window uses transparency or a blur-capable composition path, the main content area must still sit on an explicit theme-backed base surface such as `Theme.bg`, `Theme.bgPanel`, `Theme.panelBg`, `Theme.surface`, or another documented surface token. Do not let wallpaper bleed, bare transparency, or the blur layer become the only visible background behind primary content unless the whole window is an explicitly validated blur-first product requirement.
- For desktop applications with a persistent left sidebar that rely on sidebar blur, do not satisfy the right-side base-surface requirement by drawing one opaque or theme-backed full-window `Rectangle` across both sidebar and content. Scope the documented base surface to the right content panel or another non-sidebar region so the blurred sidebar still composes against the transparent or blur-capable window path.
- When fixing seams, splitter gaps, or drag-hit areas between a blurred sidebar and the right content panel, use a `1px` divider, splitter, or invisible hit-target overlay. Do not solve that seam by adding a shared full-window background slab underneath both panels; doing so suppresses the sidebar blur and is incorrect by default.
- For desktop applications with a persistent left sidebar, that divider must sit on the sidebar edge rather than opening a visible gap between sidebar and content. A splitter or resize hit-target may overlap that edge, but it must not consume visible inter-panel spacing.
- For desktop applications with a persistent left sidebar, sidebar blur is the baseline. Do not blur the entire application window by default. Use full-window blur only when the product requirement explicitly calls for it and the runtime result has been validated for that exact environment.
- For any window or region that is intentionally presented as a blur surface, treat its visual stack as DTK or system-owned composition. Prefer blur primitives that already bundle tint or fallback behavior, such as `blendColor`, a documented system fallback tint, or an equivalent validated platform composition path.
- For all dialogs and blur-capable windows or regions, do not add any extra self-drawn visual overlay layer above that surface. Do not stack a translucent `Rectangle`, `ShaderEffect`, screenshot tint, hand-painted mask, or any other manual overlay above a DTK dialog, `DialogWindow`, `AboutDialog`, `SettingsDialog`, `StyledBehindWindowBlur`, `D.DWindow`, or another validated blur path.
- If the target blur path cannot provide the needed result without a manual overlay, treat that as a platform limitation and switch to another DTK or system path, or fall back to the documented non-blur surface. Do not solve it by painting an extra overlay layer in app code.
- Do not assume that the window manager or compositor "probably" provides an overlay or tint layer. Rely only on a validated runtime result or a documented DTK/system primitive contract.
- Structural `1px` dividers, splitters, and invisible hit-target overlays used only for seam repair or resize behavior are allowed; they are not the same as a visual self-drawn overlay layer.
- For desktop applications with a persistent left sidebar, the sidebar navigation list and its items must keep a 10px horizontal inset from the sidebar background on both the left and right sides. Do not increase, decrease, or visually absorb that inset unless the user explicitly requires a different spacing rule.
- For desktop applications with a persistent left sidebar, navigation-item icons must render directly on the item surface without a separate icon background block, capsule, or tinted icon tile. Active-state emphasis belongs to the item background fill, not to a second icon background layer.
- For desktop applications with a persistent left sidebar, the active navigation icon color must match the active navigation text color exactly. Do not tint the selected icon with a different semantic foreground than the selected label.
- For desktop applications with a persistent left sidebar, do not show a group title when the navigation only has one group. When multiple groups exist, the vertical gap between adjacent groups must be `20px`.
- Unlock, paywall, subscription, service-upgrade, and similar operational notices must dock to the sidebar bottom as cards. Do not render them as floating body alerts or mix them into the main content list by default.
- Sidebar operational-card action buttons must maximize the usable card width by default. In the standard sidebar-card path, do not leave that button as a content-width chip when one primary action is present.
- For desktop applications with a persistent left sidebar, sidebar width may be adjustable. Do not encode a universal rule that collapse means a fixed `60px` icon rail.
- For sidebars with many entries, collapse support is recommended but optional. If collapse is provided, place the collapse toggle `20px` to the right of the top-left logo.
- For a resizable collapsible sidebar, reaching a minimum width of `100px` through resize, or explicitly activating the collapse toggle, must transition the sidebar to a hidden state. Expand and collapse must use a short animation.
- For a collapsible persistent sidebar, the collapse/expand affordance must use the control-center-style dedicated sidebar-toggle button and dedicated toggle glyph. Do not substitute a bare `chevron-left`, `chevron-right`, back arrow, text label, or another generic directional icon for that control unless an explicit `uos-design: allow-nonstandard-sidebar-toggle-icon` waiver explains the product reason.
- For a persistent-sidebar application with a unified top band, the top-left app logo must occupy one stable slot anchored to the window's top-left edge. Expanding or collapsing the sidebar must not make the logo jump, fade between two different coordinates, or switch between separate sidebar and content-header logo instances. Do not place the authoritative app logo inside a width-animated sidebar panel unless an explicit `uos-design: allow-moving-logo-slot` waiver explains the product reason.
- When the user explicitly requires a unified titlebar-toolbar presentation by default with a system-decorated fallback, do not stop at the fallback implementation. Either implement a validated unified-by-default path plus the fallback path, or state the exact platform blocker before coding.
- A unified titlebar-toolbar path is valid only if the final runtime UI shows a single top header band containing the app logo, the main-menu trigger, and the window-manager controls in that same band while window-manager border, shadow, rounded corners, move, resize, maximize, snap, and related behaviors remain intact.
- If the final runtime UI still shows a separate system title bar above an in-content toolbar, classify that result as fallback-only rather than a unified titlebar-toolbar implementation.
- If the system-decorated title bar still shows an application name, the implementation fails the `logo-only top-left identity` requirement even when the QML `title` is empty.
- If a true merged titlebar-toolbar cannot coexist with window-manager-owned decorations on the target platform, keep the system title bar and place the toolbar immediately below it as the default fallback.
- When a unified titlebar-toolbar path is used, the toolbar controls and visual language must stay on the standard local DTK path. Do not self-draw bespoke toolbar buttons, menu triggers, faux titlebar capsules, or custom button chrome when DTK already provides the relevant controls and titlebar style hooks unless an explicit `uos-design: allow-custom-toolbar-style` waiver explains the exact missing DTK capability.
- By default, a unified titlebar-toolbar must not show the current page title, page subtitle, or section heading inside the top band. Put page titles in the page content header instead. Only place a page title in the toolbar when the user explicitly asks for it, and document that exception with `uos-design: allow-toolbar-page-title`.
- If a product requirement document conflicts with this design skill, follow this design skill first. Call out the exact conflict and keep the implementation aligned with the design skill unless the user explicitly overrides the skill.
- Only use a frameless main window when the user explicitly accepts client-side decoration tradeoffs or when a platform-specific DTK path has been validated for that exact environment.
- Prefer system-managed popups unless the request clearly requires window-managed popups and the target platform has been validated.
- Do not use `Popup.Window` by default. If you use it, also define the `Popup.Item` fallback path.
- Keep color, radius, and spacing choices aligned with the documented theme variables.
- For option-card groups or list-like setting cards that have left-aligned descriptive content and right-aligned controls or affordances, the layout must be split-aligned: the left content block aligns to the left edge, the right content block aligns to the right edge, the left block keeps a 10px inset from the card background's left edge, and the right block keeps a 10px inset from the card background's right edge.
- For repeated option rows, setting rows, startup-item rows, or similar list-like cards that place toggles, checkboxes, combo boxes, or trailing action buttons on the right, use a dedicated trailing control slot or control column anchored to the same right inset for every row in that group. Do not place the trailing control directly after variable-width content without an explicit shared trailing slot.
- In a repeated row group with trailing controls, the right edges of those controls must resolve to the same visual column across the whole group, regardless of differences in title length, badges, descriptions, disabled state, or current value text.
- Prefer a reusable split-row primitive for these patterns, such as a `SettingRow`-style component with a left info area and a right control slot, rather than rebuilding each row ad hoc with freeform `RowLayout` children.
- For list-like rows, setting rows, repeated cards, or any other list entries that show two lines or more of descriptive content, add a leading icon by default unless the user explicitly requires no icon. Treat this as a baseline affordance, not an optional embellishment.
- Default leading-icon size for those double-line or multi-line list entries must be `24px` or `32px`. Do not improvise `14px`, `16px`, `18px`, `20px`, `28px`, `30px`, or other intermediate icon sizes for that list-entry pattern unless an explicit waiver explains the reason.
- When a reusable row primitive such as `SettingRow` carries multi-line descriptive content, its leading-icon slot must be explicit rather than implied. Do not leave a two-line row visually unanchored with only text on the left.
- Reusable cards, panels, and container primitives must expose a valid height contract. Do not compute a container `implicitHeight` from a plain `Item` wrapper whose descendants are expected to size it only through anchors. Use a sizing layout, an item with intrinsic size, or an explicit content-height property instead.
- When passing model data into repeated delegates, row primitives, or card primitives, do not use self-referential bindings such as `title: title`, `description: description`, or similar shadowed property names. Rename the incoming property, bind directly from `model`, or alias the source property explicitly so the source and target stay unambiguous.
- For table-like screens, headers and rows must share one column-width plan or one reusable row primitive. Do not build a fake table with separate ad hoc width values for the header and body that can drift out of alignment.
- Inside option groups, setting groups, and cards, keep white space purposeful. Beyond the spacing needed for hierarchy, alignment, readability, and hit targets, do not add large decorative empty gaps or oversized padding with no structural meaning.
- Card and panel shells must not be oversized relative to their actual content. Avoid fixed heights or oversized padding that leave obvious empty space on the left, right, top, or bottom sides of the card.
- Card content must keep a stable visual center of gravity. Do not push the primary chart, hero graphic, key score, summary number, or other focal content too close to any card edge; keep an explicit inner safe area so the composition does not read as top-heavy, side-heavy, or edge-crowded.
- Do not wrap a focal chart, hero graphic, key score, or similar primary visual inside a plain `Item` or `Rectangle` that advertises a fixed or implicit layout height smaller than the focal visual's actual consumed height. The layout slot must truthfully reserve the visual footprint instead of letting the focal content overflow and silently collapse surrounding spacing.
- When using a `SectionCard`-style container whose content flow is column-based, do not place a direct `ColumnLayout` or `RowLayout` child on `anchors.fill: parent` and then rely on `Layout.fillHeight` spacers to center the composition. Use a content-driven wrapper item or a layout-aware container end to end instead of mixing the two sizing systems.
- Treat the visible content inside the main content area as one composition that must be centered as a whole within that content area. When the content width is capped or otherwise narrower than the available content area, the outer left and right margins must resolve to the same value.
- Do not pin a max-width page column, card stack, dashboard band, or primary content composition to one side of the content area while leaving a visibly different margin on the other side unless the user explicitly requests that asymmetry.
- When multiple cards or dashboard panels share one horizontal content band, use an explicit grid or span plan so the group aligns on the outer top, bottom, left, and right edges. If one side stacks multiple cards while the other side uses a larger card, the stacked side must resolve to the same total height as the adjacent larger card instead of leaving uneven bottoms or floating gaps.
- In wide horizontal header, summary, or action rows, balance visual weight across the row. Do not cluster a large title, key metadata, and a primary action on one side while leaving the opposite side as a visually empty block; redistribute widths, add a counterweight block, or realign actions until the row reads balanced from left to right.
- Between icons, charts, badges, hint text, primary text, and action buttons, always reserve explicit spacing. Do not let graphic elements, descriptive text, and buttons touch or visually collapse into each other because spacing was omitted or reduced to zero.
- Inside cards, the minimum horizontal spacing between an icon and adjacent text is `10px`.
- If the application exposes a main menu, every main-interface settings entry must route through that main menu. Do not place a standalone `设置` button in the sidebar, page body, dashboard card, or top-level content area unless the user explicitly asks for a second visible settings entry.
- Action buttons must use a capped width strategy. Do not allow a normal button to expand to a width that is obviously more than about twice the width needed by its label or icon-plus-label content, and do not use unconstrained full-width buttons in desktop content areas unless a specific layout pattern requires it.
- In normal cards and dialogs, multi-button action areas must default to one horizontal row and should use the available horizontal space before wrapping. Do not use `Flow` for a normal multi-button action row, because automatic wrapping can degrade into one button per line. Do not stack each button as its own full-width row by default. Only an explicitly oversized card or dialog may use a vertical action stack, and that exception requires a narrow `uos-design: allow-vertical-action-stack` waiver with the exact reason.
- When a button is allowed to stretch with `Layout.fillWidth`, `width: parent.width`, or a similar expression, also define `Layout.maximumWidth` or `maximumWidth` unless the user explicitly requires a full-width button treatment for that surface.
- Bind theme values to DTK or system palette first. If a page needs a new semantic color, add it to the theme layer first instead of hardcoding business colors in page files.
- Theme baselines are not freeform art direction. Unless an explicit reviewed brand reason overrides them with `uos-design: allow-theme-baseline-deviation`, desktop tool surfaces must stay on the documented neutral UOS / Deepin baseline from `references/foundations/colors.md`:
  - `bg` must stay near `#F8F8F8` / `#181818`
  - sidebar blur blend and fallback colors must stay near neutral white / neutral near-black at about `0.80` alpha
  - `textPrimary` and `iconNormal` must resolve back to 70% black / white semantics
  - `textStrong` and `iconStrong` must resolve back to 100% black / white semantics
  - `systemAccent` must come from `D.DTK.palette.highlight` or an equivalent DTK / system accent source
- Do not invent slightly blue, cyan, teal, navy, or other chromatic desktop base surfaces for the main background, title bar, panel base, or sidebar blur just because they "feel modern". If the result no longer reads like UOS / Deepin, it is wrong by default.
- Theme surface tokens are not documentation-only. If the theme defines root, panel, toolbar, or page background tokens, wire those tokens into the actual root, page, and panel surfaces instead of leaving the live UI on default transparency or unrelated ad hoc colors.
- If the product defines a custom theme layer and also uses raw DTK controls such as `D.ProgressBar`, `D.Switch`, `D.CheckBox`, or `D.ComboBox`, route those controls through one coherent palette strategy. Do not leave them on unrelated default DTK accent styling while adjacent panels, cards, and navigation use a separate custom color system.
- In production QML, keep hex color literals inside the central theme file only. If a non-theme file needs a literal color for a validated platform-specific reason, add a narrow `uos-design: allow-literal-color` waiver comment in that file and explain the reason in the response.
- For interactive icons, use `Theme.iconNormal` for default state, `Theme.iconStrong` for hover or emphasis, `Theme.accentForeground` for selected or current state, and `Theme.textDisabled` for disabled state. Do not use `Theme.textMuted` as the default tint for navigation, toolbar, button, menu, or list action icons.
- For 16px functional icons, prefer downloading SVG assets from the internet as the default sourcing strategy. Choose assets whose visual language stays consistent with, or at least closely approximates, the target UOS/Deepin/DTK system style. Do not rasterize such icons to PNG or rely on baked source colors for selected, hover, current, or disabled states.
- Downloaded 16px functional icons must preserve recolorable alpha-mask semantics end-to-end, remain visually compatible with adjacent system-style controls, and support using the exact same semantic foreground variable as neighboring text.
- For sidebar, navigation, tab, stepper, and list-current states, selected and hover backgrounds plus selected foregrounds must come from named semantic theme variables such as `Theme.navItemSelectedBg`, `Theme.navItemHoverBg`, and `Theme.navItemSelectedFg`. Do not derive those state colors inline in page or component files with `Theme.mix(...)`, `Theme.withAlpha(...)`, or similar expressions.
- For persistent sidebar navigation items, the active state must read as a filled background only. Do not add a selected-state outline, stroke, or border around the active sidebar item unless an explicit `uos-design: allow-sidebar-active-border` waiver explains the requirement.
- When an application exposes a main menu, that main menu must include theme switching with `System`, `Light`, and `Dark` modes or localized equivalents. Do not hide theme switching only inside a settings page when a main menu exists.
- The main-menu `System` theme mode must stay bound to live system theme changes. Do not implement "follow system" as a one-time snapshot taken only at launch.
- Desktop settings-style main windows should start near `1200 x 800`. Do not ship a default size above roughly `1280 x 840`, and do not set a minimum width above roughly `1040` or a minimum height above roughly `720`, unless an explicit content-density reason is documented with `uos-design: allow-large-window-default`.
- Multi-group application settings surfaces using `Settings.SettingsDialog` should default to a desktop viewport around `960 x 720` or larger. Do not squeeze them into undersized fixed shells that clip content or force awkward truncation unless an explicit `uos-design: allow-compact-settings-dialog` waiver explains the constraint.
- List, table, and repeated-row screens must use responsive column or slot widths. Do not let fixed column widths create clipped cells, visually truncated list content, or horizontal scrolling in the primary desktop layout.
- Do not rely on horizontal scrolling to rescue a desktop list or settings table whose columns no longer fit. Prefer responsive breakpoints, column collapse, stacked metadata, or a different row plan.
- Do not keep scrollable lists artificially short with fixed row-count caps when the surrounding surface still has obvious unused height. Let the scroll region consume the remaining space whenever the layout allows it.
- In repeated delegates, do not declare required model roles such as `title`, `description`, `subtitle`, `text`, `statusText`, or similar names directly on the same component instance that also exposes those names as public API properties unless you rename the model role or alias it explicitly. Ambiguous role-to-component shadowing must be treated as a bug risk, not as harmless shorthand.
- Score rings, circular gauges, and similar summary widgets must keep their internal typography and text layout responsive to the actual rendered size. Do not hardcode a large font and then place the component at a smaller width or height where the text overlaps the ring or escapes the intended safe area.
- Score rings, circular gauges, and chart-center overlays may show only a primary numeric value or a primary numeric value plus one short status title inside the graphic. Do not place explanatory sentences, timestamps, hints, or third-line caption text inside the ring or chart body; all descriptive content must be laid out outside the graphic.
- Large numeric labels with units such as `%`, `分`, bandwidth, latency, or storage units must not render the unit at the same size as the number.
- Chart surfaces must include readable `x` / `y` axes, tick labels, and animated data changes; a bare unlabeled canvas line is incomplete by default.
- Search controls should reveal placeholder hints only on activation. Do not keep static inactive placeholder copy visible in the resting state.
- List rows that represent concrete apps, files, or similar objects must not use generic placeholder icons when a real object icon is available.
- For repeated settings, option, startup-item, service, or similar functional rows with leading icons, the icon must come from item-level data such as `iconSource`, `iconName`, `desktopId`, or from a resolver function keyed by the item identity. Do not hardcode one literal icon asset directly inside the repeated delegate body for all rows.
- If you must use frameless windows, `Popup.Window`, literal colors outside the theme file, `Theme.textMuted` on an interactive icon, rasterized functional icons, inline derived navigation colors, a custom main-menu button, manual main-menu positioning, custom window buttons despite local `WindowButtonGroup`, an inward-offset `WindowButtonGroup`, customized DTK main-window flags, a theme baseline deviation, an oversized default main window, a compact settings dialog, a settings dialog without a root icon, a checkbox-style settings fallback that bypasses `Settings.CheckBox`, a custom restore-default row inside settings groups, a custom settings-row metric or visible rhythm override, an ephemeral recreate-on-open settings dialog, a forced system title bar on standard DTK About or Settings surfaces, a shadowed delegate role, a custom About dialog, a popup-style `D.Dialog` in a desktop app despite local `DialogWindow` availability, a custom dialog container or dialog frame, a custom in-app notification container, a DTK control with a replaced structural template, a fully transparent main window without an explicit theme-backed base surface, a full-window opaque base surface underneath a blurred persistent sidebar, full-window blur in a persistent-left-sidebar application, a reusable container that derives height from an anchored plain `Item`, a freeform repeated trailing-control row that cannot use a dedicated control slot, a multi-line list row without a leading icon, a nonstandard multi-line list leading-icon size, a secondary in-content settings entry despite an application main menu, an oversized card shell, focal card content intentionally pushed to the card edge, an unconstrained wide button, a vertical multi-button action stack inside a normal card or dialog, horizontal list scrolling in a primary desktop surface, a bordered active sidebar item, detailed center text inside a ring or chart, a nonstandard persistent-sidebar toggle icon, a moving or duplicated top-left logo slot across sidebar states, a custom unified-toolbar style despite local DTK controls, a shared bundled icon intentionally reused across distinct functional rows, a DTK dialog body intentionally restyled away from the standard DTK content rhythm, or a toolbar page title that was not explicitly requested, add a narrow waiver comment in the touched file: `uos-design: allow-frameless`, `uos-design: allow-popup-window`, `uos-design: allow-literal-color`, `uos-design: allow-textMuted-icon`, `uos-design: allow-icon-rasterization`, `uos-design: allow-derived-nav-color`, `uos-design: allow-custom-main-menu-button`, `uos-design: allow-manual-main-menu-position`, `uos-design: allow-custom-window-buttons`, `uos-design: allow-offset-window-button-group`, `uos-design: allow-customized-window-flags`, `uos-design: allow-theme-baseline-deviation`, `uos-design: allow-large-window-default`, `uos-design: allow-compact-settings-dialog`, `uos-design: allow-settings-dialog-without-icon`, `uos-design: allow-settings-checkbox-fallback`, `uos-design: allow-custom-settings-reset-entry`, `uos-design: allow-custom-settings-row-metrics`, `uos-design: allow-ephemeral-settings-dialog`, `uos-design: allow-system-titlebar-on-standard-dtk-surface`, `uos-design: allow-shadowed-delegate-role`, `uos-design: allow-custom-about-dialog`, `uos-design: allow-popup-style-dialog`, `uos-design: allow-custom-dialog-container`, `uos-design: allow-custom-in-app-notification`, `uos-design: allow-dtk-template-override`, `uos-design: allow-transparent-main-window`, `uos-design: allow-full-window-base-under-sidebar-blur`, `uos-design: allow-full-window-blur`, `uos-design: allow-anchored-item-implicit-height`, `uos-design: allow-freeform-trailing-control-row`, `uos-design: allow-list-without-leading-icon`, `uos-design: allow-nonstandard-list-icon-size`, `uos-design: allow-secondary-settings-entry`, `uos-design: allow-oversized-card`, `uos-design: allow-card-edge-focal-content`, `uos-design: allow-wide-button`, `uos-design: allow-vertical-action-stack`, `uos-design: allow-horizontal-list-scroll`, `uos-design: allow-sidebar-active-border`, `uos-design: allow-detailed-gauge-center-text`, `uos-design: allow-nonstandard-sidebar-toggle-icon`, `uos-design: allow-moving-logo-slot`, `uos-design: allow-custom-toolbar-style`, `uos-design: allow-shared-functional-list-icon`, `uos-design: allow-custom-dialog-content-style`, `uos-design: allow-toolbar-page-title`, or `uos-design: allow-app-side-window-decoration-tuning`. Every waiver must include the exact platform, version, or component reason.
- Preserve keyboard navigation, focus states, and contrast requirements.
- State any Qt/DTK version or Wayland/X11 assumptions when they affect windowing, popup behavior, blur, or drag handling.
- Use the window and title-bar rules for desktop window layouts instead of inventing new chrome.
- When a requested component is not documented, say so plainly instead of pretending it exists.

## Hard Fail Conditions

Treat the task as not done if any of the following remain true:

- DTK is available locally but the project still lacks DTK QML imports or DTK build integration for controls that DTK provides.
- The project forces `QQuickStyle::setStyle("Basic")`, `Fusion`, `Material`, `Imagine`, or another non-DTK global style without a stated platform constraint.
- A top-level Linux desktop window uses `Qt.FramelessWindowHint` without a validated DTK path or an explicit `uos-design: allow-frameless` waiver.
- A popup uses `Popup.Window` without a validated need, a fallback path, or an explicit `uos-design: allow-popup-window` waiver.
- A non-theme QML file contains a hex color literal without an explicit `uos-design: allow-literal-color` waiver.
- An interactive icon uses `Theme.textMuted` as its default tint without an explicit `uos-design: allow-textMuted-icon` waiver.
- The local DTK export map includes `WindowButtonGroup`, but the project still rebuilds the top-level window button cluster from generic buttons or custom icon rows without an explicit `uos-design: allow-custom-window-buttons` waiver.
- `D.WindowButtonGroup` exists locally, but the implementation offsets it away from the actual top-right edge, centers it inside a wrapper, or leaves extra top/right gaps without an explicit `uos-design: allow-offset-window-button-group` waiver.
- The application main menu is opened by a custom button instead of the explicit locally validated DTK path for that environment without an explicit platform-specific waiver.
- A window that uses `D.TitleBar` exposes an application main menu but does not attach it through `D.TitleBar.menu`, or still adds a separate self-drawn main-menu trigger button for that same menu.
- A `D.TitleBar` or `D.WindowButtonGroup` path is covered by a full-width app-side content / drag overlay, or it does not reserve the trailing DTK menu / window-control safe area in maximized state.
- A `D.TitleBar` or `D.WindowButtonGroup` path sits inside a clipped ancestor or under a higher-`z` top-band overlay that can crop, hide, or steal input from the top-right DTK controls when maximized.
- A DTK main window still uses `Qt.CustomizeWindowHint`, or explicitly sets flags without `Qt.WindowTitleHint`, and therefore risks losing stable DTK title-bar controls in maximized state.
- A transparent main window uses a unified `D.TitleBar` top band but leaves that live title-band background visually transparent instead of binding it to a theme surface token.
- A transparent main window uses a semi-transparent `D.TitleBar` top band, but the content-side base surface starts only below the title-band height and therefore leaves the toolbar blending against the desktop.
- The application main menu uses hardcoded manual popup coordinates instead of DTK menu-button placement without an explicit platform-specific waiver.
- A persistent-sidebar application places the top-left app logo inside the width-animated sidebar, duplicates the logo across sidebar and content-header slots, or otherwise makes the logo jump between coordinates during sidebar expand/collapse without an explicit `uos-design: allow-moving-logo-slot` waiver.
- The user explicitly required a unified titlebar-toolbar presentation by default with a system-decorated fallback, but the implementation only ships the fallback path or omits the exact validated fallback conditions.
- The implementation uses a heuristic platform check such as `X11`, `Wayland`, `xcb`, or `wayland` to select a unified titlebar-toolbar path without proving that the resulting runtime window satisfies the unified-header acceptance criteria.
- The final runtime UI shows both a system title bar and a separate in-content toolbar, but the response still claims that the unified titlebar-toolbar requirement was implemented.
- A desktop application with a persistent left sidebar does not ship a left-right split layout as its primary desktop layout and no explicit user override justifies the deviation.
- A desktop application with a persistent left sidebar does not ship two explicit left-right panels, with a dedicated sidebar panel on the left and a dedicated content panel on the right, regardless of whether the code still happens to use a `Row`, `RowLayout`, or similar horizontal container.
- A desktop application with a persistent left sidebar still uses a full-width `D.TitleBar` or another full-width top band as the primary outer window structure instead of rendering the control-center style full-window left-right split.
- A desktop application with a persistent left sidebar lacks an explicit sidebar panel surface or validated sidebar blur surface and instead places navigation content directly on transparent or visually undefined space.
- A desktop application with a persistent left sidebar does not use a validated window-manager or compositor-provided blur path for that sidebar and no explicit user override justifies the deviation.
- A desktop application with a persistent left sidebar technically instantiates a blur primitive, but the chosen sidebar blur blend or fallback colors push the runtime result into an obviously chromatic or nearly solid panel instead of a neutral control-center-like glass surface, and no explicit `uos-design: allow-theme-baseline-deviation` waiver explains that deviation.
- A desktop application with a persistent left sidebar lacks an explicit right-side content-panel or page-base surface driven by documented theme background tokens.
- A desktop application with a persistent left sidebar leaves a visible structural gap between the sidebar and content, or places the divider in that gap instead of on the sidebar edge, without an explicit user override.
- A desktop application with a persistent left sidebar shows a navigation group title despite having only one group, or multi-group navigation does not keep a `20px` gap between groups, without an explicit override.
- Unlock, paywall, subscription, service-upgrade, or similar operational notices are rendered outside the sidebar-bottom card area without an explicit override.
- A top-level window uses a transparent or translucent base but does not provide an explicit theme-backed base surface for the main content composition, and no explicit `uos-design: allow-transparent-main-window` waiver justifies a fully blurred or transparent product requirement.
- A desktop application with a persistent left sidebar that relies on sidebar blur places a full-window opaque or theme-backed base surface underneath both sidebar and content, causing the sidebar blur to read as a solid panel, and no explicit `uos-design: allow-full-window-base-under-sidebar-blur` waiver justifies that composition.
- A desktop application with a persistent left sidebar blurs the whole application window by default instead of treating sidebar blur as the baseline, and no explicit `uos-design: allow-full-window-blur` waiver justifies that product requirement.
- A dialog or blur-capable window or region adds any extra self-drawn overlay layer above the DTK or system-owned surface, including translucent `Rectangle`, `ShaderEffect`, screenshot tint, or hand-painted mask, instead of relying on the standard DTK or system composition path.
- A desktop application with a persistent left sidebar does not keep the required 10px left and right inset between the sidebar background and the sidebar navigation list or items and no explicit user override justifies the deviation.
- A persistent sidebar navigation item still draws a separate icon background block, capsule, or tinted tile behind its icon, or the selected icon color does not exactly match the selected text color.
- A persistent sidebar item adds a selected-state border or outline around the active background and no explicit `uos-design: allow-sidebar-active-border` waiver justifies that deviation.
- A sidebar operational card action button does not maximize the usable card width.
- A collapsible persistent left sidebar hardcodes a universal `60px` collapsed rail, places the collapse toggle away from the required logo-adjacent position, or fails to hide the sidebar when resize reaches the `100px` minimum or the collapse toggle is activated, and no explicit user override justifies that behavior.
- A collapsible persistent left sidebar replaces the control-center-style dedicated sidebar-toggle glyph with a generic chevron, arrow, or other nonstandard directional icon and no explicit `uos-design: allow-nonstandard-sidebar-toggle-icon` waiver justifies that deviation.
- A unified titlebar-toolbar path draws custom toolbar chrome or bespoke toolbar button visuals instead of following the standard local DTK toolbar style and no explicit `uos-design: allow-custom-toolbar-style` waiver justifies that deviation.
- A unified titlebar-toolbar path shows the current page title, section title, or page subtitle inside the top band without an explicit `uos-design: allow-toolbar-page-title` waiver.
- A content-area page header or other large in-content title still prepends an icon.
- A large title above `16px` uses `bold` or a weight above `400` without an explicit override.
- A custom circular, ring, or arc progress component still uses an obviously heavy shadow, clips that shadow at the component edge, or allows a no-text stroke thicker than `20px`.
- An internal textless progress strip, bar, or track that reads as a progress indicator exceeds `20px` thickness, or ships without an explicit cap that keeps it at or below `20px`.
- A gradient card still leaves neutral padding, white seams, or inset margins around the live gradient surface.
- A surface repeats the same status meaning in both plain text and badge/tag form instead of keeping one primary status expression.
- An option-card or settings-card list still falls back to one shared placeholder icon, or ships repeated option rows without explicit per-item icons.
- A repeated settings, option, startup-item, or service-row delegate hardcodes one literal bundled icon for all rows instead of binding icon identity from item-level data or a per-item resolver, and no explicit `uos-design: allow-shared-functional-list-icon` waiver explains the reason.
- A file list, app or program list, startup-item or service list, data list, or other variable-length repeated list defaults to row text that expands past a compact one-line or two-line baseline without a content-driven reason.
- A variable-length file/app/program/startup/service/data list still renders each item as a large standalone card or multi-block card composition instead of a compact responsive row.
- A variable-length startup-item, service, software, file, program, or data list still relies on a legacy `SettingRow` / `SettingsOptionRow` default with oversized fixed gutters or control widths instead of a compact responsive row plan.
- A unified titlebar-toolbar surface uses a height other than `50px` or adds an extra divider line below or inside that unified top band.
- A scrollbar, horizontal or vertical, exceeds `20px` thickness or is used to rescue a layout that should have been made responsive instead.
- The same numeric ratio on one surface is still rendered by both a circular or ring-style progress graphic and a horizontal progress graphic instead of choosing one representation.
- A repeated option-row or list-card group with trailing controls does not use a dedicated shared trailing control slot or column, or the controls' right edges do not align to the same visual column across the group, and no explicit `uos-design: allow-freeform-trailing-control-row` waiver justifies the deviation.
- A reusable card, panel, or container computes its `implicitHeight` from a plain anchored `Item` wrapper that has no intrinsic height, and no explicit `uos-design: allow-anchored-item-implicit-height` waiver justifies that sizing contract.
- A repeated row, card, or delegate uses a self-referential binding such as `title: title`, `description: description`, or a similar property-to-itself binding.
- A repeated delegate or card instance shadows component API property names with same-named required model roles such as `title`, `description`, `subtitle`, `text`, or `statusText` without an explicit `uos-design: allow-shadowed-delegate-role` waiver.
- A double-line or multi-line list row, settings row, or repeated card entry ships without a leading icon and no explicit `uos-design: allow-list-without-leading-icon` waiver explains the omission.
- A double-line or multi-line list row, settings row, or repeated card entry uses a leading-icon size other than `24px` or `32px` without an explicit `uos-design: allow-nonstandard-list-icon-size` waiver.
- A table-like screen still uses separate drifting header and row width definitions instead of one shared column plan or one reusable row primitive.
- A list, table, or repeated-row surface in the primary desktop layout still depends on horizontal scrolling, clipped columns, or fixed widths that truncate content instead of using a responsive column or slot plan, and no explicit `uos-design: allow-horizontal-list-scroll` waiver explains the exception.
- An option-group or card composition contains large internal blank areas that do not serve hierarchy, alignment, readability, or hit targets, and no explicit user override justifies that extra empty space.
- A card shell keeps an obviously oversized fixed height or padding footprint relative to its content and no explicit `uos-design: allow-oversized-card` waiver explains the need.
- A card pushes its primary chart, hero graphic, key score, summary number, or other focal foreground content against the card edge without an explicit inner safe area, and no explicit `uos-design: allow-card-edge-focal-content` waiver explains the composition.
- A plain wrapper around a focal chart, hero graphic, score ring, or similar primary visual advertises a layout height smaller than the focal visual itself, causing the graphic to overflow its slot and collapse surrounding spacing.
- A `SectionCard`-style column-flow container mixes a direct `ColumnLayout` or `RowLayout` child on `anchors.fill: parent` with `Layout.fillHeight` spacer items, causing card content to ignore the container's real sizing flow and collapse into overlap or drift.
- A capped-width or visually grouped main-content composition is not centered within the content area as a whole and leaves visibly unequal outer left and right margins without an explicit user override.
- A horizontal dashboard or card band that is clearly intended to read as one shared composition does not align its outer top, bottom, left, and right edges or leaves stacked cards at a different total height from the adjacent larger card without an explicit user override.
- A top-level window that is required to use window-manager-owned rounded corners, border, or shadow still sets `D.DWindow.windowRadius`, `D.DWindow.borderWidth`, `D.DWindow.borderColor`, `D.DWindow.shadowRadius`, `D.DWindow.shadowOffset`, or `D.DWindow.shadowColor` from app-side QML without an explicit `uos-design: allow-app-side-window-decoration-tuning` waiver.
- A DTK control such as `D.Switch`, `D.CheckBox`, `D.ComboBox`, `D.Button`, `D.TextField`, `D.Menu`, `D.Dialog`, or `D.ProgressBar` has its structural template replaced with custom `background`, `contentItem`, `indicator`, `handle`, `popup`, or `delegate` items without an explicit `uos-design: allow-dtk-template-override` waiver.
- A main window ships a default size above roughly `1280 x 840`, or a minimum size above roughly `1040 x 720`, for a settings-style desktop tool without an explicit `uos-design: allow-large-window-default` waiver.
- A `Settings.SettingsDialog` is shipped in an undersized fixed viewport that clips content or obviously truncates multi-group settings without an explicit `uos-design: allow-compact-settings-dialog` waiver.
- A `Settings.SettingsDialog` root omits its `icon` and therefore leaves the standard DTK top-left icon slot empty without an explicit `uos-design: allow-settings-dialog-without-icon` waiver.
- A standard `D.AboutDialog` or `Settings.SettingsDialog` explicitly sets `D.DWindow.enabled: false` and therefore forces a system title bar instead of the local DTK title bar without an explicit `uos-design: allow-system-titlebar-on-standard-dtk-surface` waiver.
- A checkbox-style boolean option inside `Settings.SettingsDialog` bypasses local `Settings.CheckBox` and instead rebuilds the row with `D.CheckBox` or another fallback path without an explicit `uos-design: allow-settings-checkbox-fallback` waiver.
- A multi-group settings surface exposes restore-default behavior as a normal settings row inside `groups` instead of using the DTK-owned bottom restore entry or footer path, and no explicit `uos-design: allow-custom-settings-reset-entry` waiver explains the local DTK limitation.
- A custom fallback row inside `Settings.SettingsDialog` changes visible row rhythm with project theme spacing, custom typography, or custom normal-text styling instead of remaining a layout-only `Settings.OptionDelegate` fallback, and no explicit `uos-design: allow-custom-settings-row-metrics` waiver explains the missing DTK metric path.
- A multi-group settings window is destroyed on close and recreated on the next open instead of being kept as a stable reusable window instance, and no explicit `uos-design: allow-ephemeral-settings-dialog` waiver explains the ownership or resource constraint.
- A score ring or circular gauge keeps fixed large typography and is then consumed below its validated visual size, causing text overlap or obvious clipping.
- A score ring, circular gauge, or chart-center overlay still renders caption text, explanatory text, timestamps, or more than two lines inside the graphic and no explicit `uos-design: allow-detailed-gauge-center-text` waiver explains the requirement.
- A large numeric label with `%`, `分`, storage, bandwidth, or similar units still renders the unit at full numeric size instead of a reduced unit size.
- A custom progress component renders its foreground fill or stroke without a matching same-color shadow treatment.
- A chart or performance-curve surface omits labeled axes, tick marks, parameter detail, or animated value changes without an explicit override.
- A chart curve or polyline still renders as a flat line without a same-color shadow and a top-to-bottom same-hue gradient treatment.
- A search edit keeps placeholder guidance visible while inactive instead of revealing it only on activation.
- An app/file list still uses a generic placeholder icon where a real icon should be shown.
- A desktop application dialog still uses popup-style `D.Dialog` instead of the local standard window-level DTK path (`D.DialogWindow`, `Settings.SettingsDialog`, or `D.AboutDialog` where appropriate) without an explicit `uos-design: allow-popup-style-dialog` waiver.
- A `D.DialogWindow` still uses `DialogButtonBox` instead of the local standard DTK dialog action-row path with DTK `Button` / `WarningButton`.
- An application dialog uses a custom popup or custom dialog container/frame instead of a DTK dialog type, or product code takes over dialog chrome and styling instead of only providing content and action signals, without an explicit `uos-design: allow-custom-dialog-container` waiver.
- A DTK dialog body still uses centered hero headings, oversized body typography, project text-palette overrides for normal copy, faux card sections, or similar custom content styling that makes the runtime result stop reading as a standard DTK dialog, and no explicit `uos-design: allow-custom-dialog-content-style` waiver explains the reason.
- A normal card or dialog still stacks multiple action buttons vertically by default, still uses `Flow` for a normal multi-button action area, or makes each button occupy its own full-width row, and no explicit `uos-design: allow-vertical-action-stack` waiver explains the oversized-surface reason.
- A 16px functional icon pipeline rasterizes a downloaded or bundled SVG icon to PNG, or otherwise loses recolorable symbolic or alpha semantics without an explicit `uos-design: allow-icon-rasterization` waiver.
- Sidebar, navigation, tab, stepper, or list-current colors are derived inline outside the theme layer without an explicit `uos-design: allow-derived-nav-color` waiver.
- The project defines a custom theme layer and uses raw DTK progress, switch, checkbox, or combo-box controls, but no coherent DTK palette-routing strategy is implemented and the runtime result leaves those controls on unrelated default accent styling.
- An application main menu exists but does not expose `System`, `Light`, and `Dark` theme switching, or its `System` mode does not remain bound to live system theme changes.
- An application main menu exists, but the main interface still exposes a standalone `设置` button or equivalent secondary settings entry outside that main menu without an explicit `uos-design: allow-secondary-settings-entry` waiver.
- A desktop content-area button stretches without a maximum width or uses a visibly oversized fixed width for its content and no explicit `uos-design: allow-wide-button` waiver explains the need.
- An About entry opens a custom about dialog instead of DTK `AboutDialog` without an explicit platform-specific waiver.
- An in-app toast, floating message, or transient application notification uses a custom toast or notification container instead of DTK `FloatingMessage` without an explicit platform-specific waiver.
- An option-card group or list-like setting card with left descriptive content and right controls or affordances does not keep left-right split alignment with 10px insets on both sides and no explicit user override justifies the deviation.
- The main application header or toolbar shows an application name next to the top-left logo instead of using a logo-only presentation.
- The final runtime UI shows an application name in the top-left title bar when the skill requires a logo-only top-left identity.
- `scripts/audit_uos_qml.sh` reports findings and the response neither fixes them nor explains the exact remaining waiver.

## Required Review Checks

When reviewing or generating code, explicitly check the following:

- Run `scripts/audit_uos_qml.sh <repo-root>` and report the result before closing the task.
- Whether the local DTK export map in `references/local-dtk-controls.md` matches the actual public `qmldir` exports on the machine, and whether the implementation uses those exact locally available controls instead of guessing.
- Whether `D.WindowButtonGroup`, when used, is actually placed at the top-right edge of the live header region instead of being centered inside a wrapper or offset inward with extra gap.
- Whether the build or runtime imports `org.deepin.dtk` and links the relevant DTK package when DTK is available locally.
- Whether a UOS/Deepin task incorrectly uses plain Qt Quick Controls plus custom wrappers where DTK controls exist.
- Whether a DTK control is only used as a state container while its visual template is effectively replaced by custom `background`, `contentItem`, `indicator`, `handle`, `popup`, or `delegate` items.
- Whether the code forces a non-DTK global style such as `Basic`, `Fusion`, or `Material`.
- Whether the main window strategy states the Qt version and `Wayland`/`X11` assumption when frameless behavior is used.
- Whether the chosen window strategy preserves window-manager-owned border, shadow, rounded corners, move, resize, maximize, snap, and related behaviors for top-level windows.
- Whether the code incorrectly assumes a macOS-style merged titlebar-toolbar is generically available on Linux/UOS without platform-specific validation.
- Whether any desktop application with a persistent left sidebar uses the required left-right split layout with navigation on the left and main content on the right.
- Whether any desktop application with a persistent left sidebar truly renders as two explicit panels rather than only arranging navigation and content horizontally in code.
- Whether any desktop application with a persistent left sidebar incorrectly keeps a full-width `D.TitleBar` or other full-width top band as the primary outer shell instead of using the control-center style full-window split.
- Whether any desktop application with a persistent left sidebar gives the left side its own explicit sidebar panel surface instead of only placing navigation content on transparent space.
- Whether any desktop application with a persistent left sidebar uses a validated window-manager or compositor-provided blur path for the sidebar rather than a self-drawn or fake blur substitute.
- Whether the sidebar blur still reads as a neutral control-center-like glass surface in both Light and Dark themes instead of a chromatic or overly opaque colored panel.
- Whether any desktop application with a persistent left sidebar gives the right side an explicit content-panel or page-base surface instead of leaving the page stack visually ungrounded.
- Whether a transparent or translucent top-level window still renders the main content composition on an explicit theme-backed base surface instead of exposing wallpaper bleed or bare blur behind primary content.
- Whether any desktop application with a persistent left sidebar that relies on sidebar blur scopes its theme-backed base surface to the right content panel instead of stretching one opaque full-window slab underneath the blurred sidebar.
- Whether any desktop application with a persistent left sidebar incorrectly applies blur to the whole application window by default instead of keeping sidebar blur as the baseline.
- Whether any blurred window or region incorrectly adds a second self-drawn tint or overlay layer on top of a DTK or system blur primitive that already provides `blendColor`, fallback tint, or an equivalent internal compositing layer.
- Whether any blurred window or region avoids manual tint, blur, or decorative overlay layers entirely and relies only on the validated DTK or system composition path.
- Whether any seam fix between a blurred persistent sidebar and the right content panel uses a divider, splitter, or hit-target overlay instead of a full-window background layer that suppresses the sidebar blur.
- Whether any persistent sidebar keeps zero structural gap to the content panel and places the visible divider on the sidebar edge instead of in an empty spacer.
- Whether any desktop application with a persistent left sidebar keeps the required 10px horizontal inset between the sidebar background and the sidebar navigation list or items on both sides.
- Whether a single-group sidebar incorrectly shows a group title, and whether multi-group sidebars keep a `20px` vertical gap between groups.
- Whether unlock, paywall, subscription, or service-upgrade notices are docked to the sidebar bottom as cards with `10px` outer margins.
- Whether active sidebar items rely on fill-only emphasis and incorrectly add a border or outline around the selected background.
- Whether any collapsible persistent left sidebar avoids a fixed `60px` icon-rail assumption, places the collapse toggle `20px` to the right of the top-left logo, and hides the sidebar when resize reaches `100px` minimum or the collapse toggle is activated.
- Whether any top-level menu affordance on this machine correctly uses the public DTK trigger path for the current layout baseline instead of inventing a custom button or misclassifying `D.ThemeMenu` as a visual menu button.
- Whether any `D.TitleBar`-based main window attaches its application main menu through `D.TitleBar.menu` like `dde-control-center`, rather than drawing a separate trigger button and calling `popup()` manually.
- Whether any collapsible persistent left sidebar uses the control-center-style dedicated sidebar-toggle icon/button rather than a generic chevron, arrow, or text substitute.
- Whether the top-left application logo stays in one stable window-relative slot during sidebar expand/collapse instead of moving with the sidebar or swapping between duplicate logo instances.
- Whether any unified titlebar-toolbar stays on the standard local DTK toolbar style instead of inventing self-drawn toolbar chrome.
- Whether any unified titlebar-toolbar keeps the required `50px` height and avoids adding a divider line to that merged top band.
- Whether any unified titlebar-toolbar incorrectly places page titles in the top band when the user did not explicitly request that layout.
- Whether any content-area page header or other large in-content title incorrectly prepends an icon.
- Whether large titles above `16px` stay at or below `400` weight.
- Whether every internal textless progress strip, bar, or track that reads as a progress indicator keeps an explicit thickness cap at or below `20px`.
- Whether repeated option rows, setting rows, startup-item rows, and similar list-like cards with trailing controls use a dedicated shared trailing control slot and keep the controls aligned to one right-side visual column across the entire group.
- Whether repeated settings, option, startup-item, and service rows source their leading icons from item-level data or a per-item resolver instead of hardcoding one constant icon in the delegate.
- Whether file lists, app or program lists, startup-item or service lists, data lists, and other variable-length repeated lists keep each row on a compact one-line or at most two-line baseline by default.
- Whether variable-length file/app/program/startup/service/data lists avoid per-item large standalone cards and keep a compact row baseline instead.
- Whether reused list-row primitives such as `SettingRow` / `SettingsOptionRow` stay compact and responsive when used for variable-length page-level lists instead of carrying oversized fixed gutters or control slots.
- Whether reusable card, panel, and container primitives have a valid height contract rather than deriving `implicitHeight` from a plain anchored `Item` wrapper with no intrinsic size.
- Whether repeated delegates, cards, or row primitives contain self-referential bindings such as `title: title` or `description: description`.
- Whether repeated delegates shadow component property names with same-named required model roles and therefore risk blank rows, incorrect bindings, or hard-to-debug runtime behavior.
- Whether double-line or multi-line list rows, settings rows, and repeated card entries keep a leading icon by default, and whether that icon uses the required `24px` or `32px` size unless a waiver explains otherwise.
- Whether table-like screens share one column-width plan between headers and rows instead of maintaining separate drifting width definitions.
- Whether list, table, and repeated-row screens use responsive column or slot widths and avoid horizontal scrolling or clipped content in the primary desktop layout.
- Whether every scrollbar, horizontal or vertical, stays at or below `20px` thickness.
- Whether the same numeric ratio is ever rendered twice on one surface through both circular/ring progress and horizontal progress.
- Whether option groups, setting groups, and cards avoid large internal blank areas beyond the spacing needed for hierarchy, alignment, readability, and hit targets.
- Whether card shells stay close to the size actually needed by their content rather than shipping large fixed heights or oversized padding footprints.
- Whether cards keep the primary chart, hero graphic, key score, summary number, or other focal foreground content inside a stable inner safe area instead of letting it visually stick to the card edge.
- Whether any plain wrapper around a focal chart, hero graphic, score ring, or similar primary visual truthfully reserves that visual's consumed height instead of advertising a smaller layout slot and collapsing surrounding spacing.
- Whether column-flow card primitives such as `SectionCard` avoid mixing a direct fill-anchored `ColumnLayout` / `RowLayout` child with `Layout.fillHeight` spacer items in ways that bypass the card's real sizing flow and create overlap.
- Whether the main content composition remains centered within the content area as a whole, with equal outer left and right margins whenever the visible content width is capped or otherwise narrower than the available space.
- Whether shared horizontal dashboard or card bands align their outer edges and make stacked groups resolve to the same total height as adjacent larger cards.
- Whether top-level window rounded corners, border, and shadow are truly owned by the window manager rather than tuned from app-side `D.DWindow` decoration properties.
- Whether wide horizontal header, summary, or action rows maintain left-right visual balance instead of concentrating major visual weight on one side and leaving the opposite side visually empty.
- Whether every application main-menu trigger uses a DTK menu button rather than a custom app button, and whether its popup placement is left to DTK conventions instead of hardcoded coordinates.
- Whether every application main menu includes `System`, `Light`, and `Dark` theme switching or localized equivalents, and whether the `System` mode stays synchronized with live system theme changes instead of only restoring an initial snapshot.
- Whether any main-interface `设置` entry incorrectly appears as a standalone button instead of routing through the main menu when the application already has one.
- Whether every button in desktop content areas uses a capped width strategy or explicit maximum width instead of stretching far beyond the space its label actually needs.
- Whether graphics, hint text, and action buttons keep explicit spacing instead of visually colliding because spacing was omitted or set to zero.
- When the user requests a unified titlebar-toolbar presentation by default with a fallback, whether the implementation actually contains both paths and states the exact trigger for falling back to system decorations.
- When the user requests a unified titlebar-toolbar presentation by default with a fallback, whether runtime validation confirms a single top header band rather than a system title bar plus a second in-content toolbar.
- Whether the implementation incorrectly treats `X11`, `Wayland`, `xcb`, `wayland`, Qt version, or DTK version alone as proof that a unified titlebar-toolbar path is available.
- Whether the final runtime UI still shows an application name in the system title bar despite a logo-only requirement.
- Whether dialogs, menus, and popups return focus correctly and preserve keyboard access.
- Whether every application dialog uses a DTK dialog type, and whether project code limits itself to text content, semantic state, and action signals instead of taking over dialog visual styling.
- Whether DTK dialog bodies avoid custom centered hero text, oversized secondary headings, project-specific normal-text palette overrides, and page-style widgets so the runtime result still reads as a standard DTK dialog.
- Whether `Settings.SettingsDialog` and other multi-group settings surfaces have a large enough default viewport to show their content without obvious clipping or truncation.
- Whether every `Settings.SettingsDialog` root also provides the standard DTK window identity fields, especially `title` and `icon`, so the runtime shell keeps the normal top-left icon slot and title-bar identity.
- Whether standard `D.AboutDialog` and `Settings.SettingsDialog` keep the DTK-owned title bar instead of being forced back to a window-manager system title bar with `D.DWindow.enabled: false`.
- Whether checkbox-style boolean settings inside `Settings.SettingsDialog` use local `Settings.CheckBox` instead of rebuilding the same result with `D.CheckBox` inside a fallback row.
- Whether enum settings use `Settings.ComboBox` and text-entry settings use `Settings.LineEdit` before introducing any custom `Settings.OptionDelegate` fallback.
- Whether any custom `Settings.OptionDelegate` fallback row inside a settings window stays layout-only, keeps one shared trailing control slot or column, and avoids project theme spacing, custom body colors, or custom typography that restyles the DTK settings rhythm.
- Whether restore-default behavior in a settings window is routed through the DTK-owned footer or `SettingsContainer.resetSettings()` path instead of a normal settings row inside the groups.
- Whether the settings window is created once and reused rather than being torn down and recreated on every open unless a documented waiver explains that lifecycle choice.
- Whether every About entry that opens an About surface uses DTK `AboutDialog` instead of a custom About popup.
- Whether every in-app toast, floating message, or transient application notification uses DTK `FloatingMessage` instead of a custom toast or notification container.
- Whether page code hardcodes brand or business colors instead of going through theme variables.
- Whether the theme layer actually starts from the documented neutral DTK / UOS baseline instead of a self-invented chromatic surface palette.
- Whether `textPrimary`, `textStrong`, `iconNormal`, `iconStrong`, and sidebar blur colors resolve back to the documented foreground and neutral blur semantics rather than ad hoc tinted values.
- Whether the actual root, page, and panel surfaces consume the documented theme background tokens instead of defining those tokens but leaving the live UI on default transparency or unrelated fills.
- Whether non-theme QML files contain hex color literals or waiver comments.
- Whether interactive icons incorrectly default to `Theme.textMuted` instead of `Theme.iconNormal`.
- Whether 16px functional icons are sourced from downloaded SVG assets whose style stays consistent with or close to the target system style, and whether they preserve symbolic or alpha recoloring semantics end-to-end rather than being rasterized and then tinted.
- Whether selected navigation icons visually match the same semantic foreground variable as the selected navigation text.
- Whether sidebar, navigation, tab, stepper, and list-current backgrounds and foregrounds come from semantic theme variables instead of inline derived expressions in component or page files.
- Whether custom theme surfaces and raw DTK controls are routed through one coherent palette plan rather than mixing unrelated custom backgrounds with untouched DTK default accent colors.
- Whether score rings, circular gauges, and similar summary widgets keep their typography inside the safe area at the actual consumed size rather than only at the component's design-time default size.
- Whether rings, gauges, and chart-center overlays keep only the number or number-plus-short-status inside the graphic and move all explanatory text outside.
- Whether custom linear, circular, ring, or arc progress components give their foreground fill or stroke a same-color shadow instead of a flat edge-only treatment, keep that shadow light enough to avoid muddy halos, and reserve enough safe inset that the shadow never clips.
- Whether no-text circular or ring progress states keep stroke thickness at or below `20px`.
- Whether large numeric labels reduce unit size relative to the number instead of rendering the whole value as one full-size text run.
- Whether charts expose labeled axes, tick marks, and animated data changes.
- Whether chart curves or polylines use a same-color shadow and a top-to-bottom same-hue gradient instead of shipping as flat lines.
- Whether inactive search edits suppress placeholder hints until focus.
- Whether concrete app/file rows use real icons instead of generic placeholder assets.
- Whether gradient hero cards and other gradient summary cards let the gradient reach the outer card edge without neutral padding or inset seams.
- Whether option-card and settings-card lists use explicit per-item icons that match the represented function instead of one repeated placeholder asset.
- Whether any surface duplicates one status meaning in both badge/tag and plain-text form.
- Whether option-card groups or list-like setting cards with left descriptive content and right controls or affordances keep left-right split alignment with 10px insets from both card edges.
- Whether the top-left application identity uses a logo-only presentation and incorrectly adds an application name.
- Whether icon strategy, control strategy, and window strategy are treated as separate decisions instead of being conflated.

## Conflict Resolution

If documents disagree, use this order:

1. This `SKILL.md`
2. `references/foundations/*.md` and `references/components/*.md`
3. `references/platform-compatibility.md`
4. `references/design-rules.md`
5. `references/design-system-layout.md` and `references/design-system-window-behavior.md`
6. `references/design-system-quick-reference.md`
7. `references/design-system-modular.yaml` for routing and indexing only

If a PRD or requirement document conflicts with this order, use the skill and its references first unless the user explicitly instructs otherwise.

## Response Guidance

- Cite the exact files you used.
- Keep answers implementation-oriented.
- If you choose a non-DTK fallback, say exactly why DTK could not be used in that case.
- Call out Qt/DTK version constraints and Wayland/X11 assumptions when they matter.
- Distinguish clearly between a runtime-validated unified titlebar-toolbar path and a fallback-only result. Do not describe a fallback result as unified.
- When reviewing UI code, call out mismatches against the documented theme variables or rules.
- When reviewing UI code, treat missing DTK usage as a primary finding when DTK controls are available locally.
- When generating new QML, follow the naming and state conventions already documented here.
