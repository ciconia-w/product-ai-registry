#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
    cat <<'EOF'
Usage: audit_deepin_qml.sh [repo-root]

Heuristic audit for UOS/Deepin QML desktop projects.
It reports blocking findings for:
- missing DTK imports/build hooks when DTK is installed locally
- misuse of locally exported DTK controls such as rebuilding window buttons despite local WindowButtonGroup
- WindowButtonGroup clusters offset away from the actual top-right edge
- titlebar content or drag zones that span the full D.TitleBar width without reserving the DTK trailing control strip
- D.TitleBar or WindowButtonGroup paths nested inside clipped ancestors that can crop top-right controls when maximized
- DTK main windows that still use Qt.CustomizeWindowHint or explicitly drop Qt.WindowTitleHint from the title-bar flag set
- transparent DTK main windows whose live title-band background is left visually transparent instead of using a theme surface token
- transparent DTK main windows whose right-side content base surface starts only below the title-band height, leaving the toolbar to blend against the desktop
- forced non-DTK global styles
- frameless top-level windows without waivers
- transparent top-level windows without an explicit theme-backed base surface
- full-window opaque base surfaces placed underneath blurred persistent sidebars
- Popup.Window usage without waivers
- full-width D.TitleBar in persistent-left-sidebar applications
- sidebar components that never establish an explicit sidebar panel surface
- persistent-sidebar splits that leave a visible seam or consume width between sidebar and content instead of keeping zero gap with a divider on the sidebar edge
- single-group sidebars that still render a group header, or multi-group sidebar groups that do not keep a 20px gap
- operational unlock/pay/service notices rendered outside a sidebar-bottom card area
- sidebar navigation items that still draw separate icon background tiles or use selected icon colors that differ from selected text
- sidebar operational-card buttons that do not maximize the usable card width
- full-window blur in persistent-left-sidebar applications without waivers
- page skeletons that never consume theme background tokens
- theme background tokens defined but never used by live surfaces
- self-drawn visual overlays stacked above DTK/system blur surfaces
- top-of-app operational or restricted-mode banners that should instead use sidebar-bottom operational cards
- sidebar operational cards whose only action is an in-app page jump
- reusable container implicitHeight contracts derived from anchored plain Item wrappers
- self-referential property bindings inside delegates or row primitives
- fake table screens with separate header/row width plans
- DTK controls left on default palette while the project uses a separate custom theme layer
- application main menus missing `System` / `Light` / `Dark` theme switching
- repeated trailing-control rows that do not expose a dedicated right-side control slot
- shadowed delegate role names that can blank or corrupt repeated rows
- multi-line list rows that omit the required leading icon or use a nonstandard icon size
- standalone in-content settings buttons when the app already exposes a main menu
- oversized card shells with obviously large fixed heights
- focal card content that binds to zero-padding card edges without an inner safe area
- focal graphic wrappers that advertise less height than the contained focal visual and therefore collapse surrounding spacing
- fill-anchored layout children inside column-flow card primitives that rely on Layout.fillHeight spacers and therefore bypass the card sizing flow
- repeated functional-row delegates that hardcode one literal bundled icon for all rows
- functional list models that reuse one bundled icon asset across distinct item identities
- action buttons with uncapped or oversized widths
- explicit horizontal-scrolling list/table patterns in primary desktop surfaces
- scrollbars whose visible thickness exceeds 20px
- internal textless progress indicators whose visible thickness exceeds 20px or lacks an explicit cap
- dense icon/text/button clusters with explicit zero spacing
- selected sidebar items that add a border or outline
- persistent-sidebar collapse toggles that use generic chevrons or arrows
- moving or duplicated top-left logo slots across sidebar expand/collapse
- unified-toolbar page titles that were not explicitly requested
- detailed center text inside rings, gauges, or chart-center overlays
- oversized default desktop window shells
- undersized DTK settings dialogs
- `Settings.SettingsDialog` roots that omit the standard top-left icon slot
- standard DTK About/settings surfaces that are forced back to a system title bar
- checkbox-style settings rows that bypass local `Settings.CheckBox`
- restore-default actions incorrectly surfaced as ordinary rows inside settings groups
- custom settings-row fallback primitives that inject project theme rhythm into DTK settings content
- theme baselines that drift away from the documented neutral DTK/UOS palette
- sidebar blur tint values that are too opaque or too chromatic to read as control-center-like glass
- circular score widgets with fixed large typography consumed below their safe size
- app-side top-level window decoration tuning for radius, border, or shadow
- hex color literals outside Theme.qml without waivers
- interactive icon tint using Theme.textMuted without waivers
- DTK controls with replaced structural templates without waivers
- custom in-app notifications without waivers
- rasterized functional-icon pipelines without waivers
- inline derived navigation colors in sidebar/nav files without waivers
- custom main-menu triggers without waivers
- application main menus that do not use D.TitleBar.menu
- D.TitleBar-based windows that still add a separate self-drawn main-menu trigger
- main-menu triggers next to the minimize cluster that still use project SVG assets or custom chrome
- manual main-menu popup coordinates without waivers
- large title labels above 16px that exceed 400 weight
- content-area page headers or other large in-content titles that still prepend icons
- large numeric labels with units rendered as one full-size text run instead of a value-plus-half-size-unit treatment
- custom progress components whose foreground fill or stroke lacks a same-color shadow treatment
- circular or ring progress shadows that are too strong, clip at the component edge, or allow no-text strokes above 20px
- gradient cards that leave neutral padding or inset seams around the live gradient surface
- duplicated badge/tag status and plain-text status within one surface
- option/settings rows that still rely on a shared placeholder icon or omit explicit per-item icons
- list rows that keep generic placeholder icons where a real app/file icon should be used
- charts without labeled axes, tick marks, or animated data changes
- chart curves or polylines rendered as flat lines without a same-color shadow and top-to-bottom same-hue gradient
- search edits whose placeholder hints remain visible while inactive
- search/filter bands where the search control does not clearly dominate the layout share
- variable-length file/app/data list rows or reusable cards that allow wrapped text to sprawl beyond a compact 1-2 line baseline
- variable-length file/app/program/startup/service/data page lists that still use per-item standalone cards or legacy oversized settings-row templates instead of compact responsive rows
- one surface rendering the same numeric ratio through both circular/ring progress and horizontal progress
- popup-style `D.Dialog` usage in desktop app code when local `DialogWindow` exists and no waiver explains the exception
- `DialogButtonBox` usage inside app dialog code even though the local `DialogWindow` standard path expects DTK button rows
- vertically stacked multi-button action areas inside normal cards or dialogs
- self-drawn overlay layers inside DTK dialogs
- non-DTK dialogs or dialog shells in projects where DTK dialogs are available locally
- DTK dialogs whose body restyles normal text colors, adds oversized secondary headings, centers hero text, or embeds page-style widgets
- collapsible sidebars that visually collapse by width squeeze instead of translate-out / translate-in motion
- list surfaces that are artificially capped to a few rows instead of consuming the remaining available height
- unified toolbars whose merged top band is not 50px high or still adds an extra divider line
- custom About dialogs without waivers
EOF
    exit 0
fi

ROOT_INPUT="${1:-$PWD}"
if [[ ! -d "$ROOT_INPUT" ]]; then
    echo "repo root does not exist: $ROOT_INPUT" >&2
    exit 64
fi

ROOT="$(cd "$ROOT_INPUT" && pwd)"
findings=0
main_menu_candidates=()
settings_button_candidates=()
surface_token_pattern='Theme\.(bg|bgPanel|bgToolbar|surface|panelBg|titlebarBg)([^A-Za-z0-9_]|$)'
dtk_qmldir=""
dtk_settings_qmldir=""

log_fail() {
    local code="$1"
    local detail="$2"
    printf 'FAIL [%s] %s\n' "$code" "$detail"
    findings=$((findings + 1))
}

grep_repo() {
    local pattern="$1"
    shift
    grep -RInE \
        --exclude-dir=.git \
        --exclude-dir=.idea \
        --exclude-dir=.vscode \
        --exclude-dir=.cache \
        --exclude-dir=.codex \
        --exclude-dir=build \
        --exclude-dir=cmake-build-debug \
        --exclude-dir=cmake-build-release \
        --exclude-dir=dist \
        --exclude-dir=node_modules \
        "$pattern" \
        "$ROOT" \
        "$@" 2>/dev/null || true
}

list_qml_files() {
    find "$ROOT" \
        \( -path "$ROOT/.git" \
        -o -path "$ROOT/.idea" \
        -o -path "$ROOT/.vscode" \
        -o -path "$ROOT/.cache" \
        -o -path "$ROOT/.codex" \
        -o -path "$ROOT/build" \
        -o -path "$ROOT/cmake-build-debug" \
        -o -path "$ROOT/cmake-build-release" \
        -o -path "$ROOT/dist" \
        -o -path "$ROOT/node_modules" \) -prune \
        -o -type f -name '*.qml' -print0
}

list_source_files() {
    find "$ROOT" \
        \( -path "$ROOT/.git" \
        -o -path "$ROOT/.idea" \
        -o -path "$ROOT/.vscode" \
        -o -path "$ROOT/.cache" \
        -o -path "$ROOT/.codex" \
        -o -path "$ROOT/build" \
        -o -path "$ROOT/cmake-build-debug" \
        -o -path "$ROOT/cmake-build-release" \
        -o -path "$ROOT/dist" \
        -o -path "$ROOT/node_modules" \) -prune \
        -o -type f \( -name '*.cpp' -o -name '*.cc' -o -name '*.cxx' -o -name '*.h' -o -name '*.hpp' \) -print0
}

dtk_has_export() {
    local export_name="$1"
    [[ -n "$dtk_qmldir" ]] && grep -qE "^${export_name}[[:space:]]" "$dtk_qmldir"
}

dtk_settings_has_export() {
    local export_name="$1"
    [[ -n "$dtk_settings_qmldir" ]] && grep -qE "^${export_name}[[:space:]]" "$dtk_settings_qmldir"
}

max3() {
    local a="$1"
    local b="$2"
    local c="$3"
    local max="$a"
    (( b > max )) && max="$b"
    (( c > max )) && max="$c"
    printf '%s\n' "$max"
}

min3() {
    local a="$1"
    local b="$2"
    local c="$3"
    local min="$a"
    (( b < min )) && min="$b"
    (( c < min )) && min="$c"
    printf '%s\n' "$min"
}

hex_rgb_metrics() {
    local hex="${1#\#}"
    local alpha="-1"
    local rgb="$hex"
    if [[ ${#hex} -eq 8 ]]; then
        alpha=$((16#${hex:0:2}))
        rgb="${hex:2:6}"
    fi
    local r=$((16#${rgb:0:2}))
    local g=$((16#${rgb:2:2}))
    local b=$((16#${rgb:4:2}))
    local max_v
    local min_v
    max_v="$(max3 "$r" "$g" "$b")"
    min_v="$(min3 "$r" "$g" "$b")"
    printf '%s %s %s %s %s\n' "$r" "$g" "$b" "$alpha" "$((max_v - min_v))"
}

hex_is_neutral_light() {
    local metrics
    metrics="$(hex_rgb_metrics "$1")"
    local r g b alpha spread
    read -r r g b alpha spread <<<"$metrics"
    (( r >= 244 && g >= 244 && b >= 244 && spread <= 8 ))
}

hex_is_neutral_dark() {
    local metrics
    metrics="$(hex_rgb_metrics "$1")"
    local r g b alpha spread
    read -r r g b alpha spread <<<"$metrics"
    (( r <= 24 && g <= 24 && b <= 24 && spread <= 8 ))
}

hex_alpha_is_sidebar_blend() {
    local metrics
    metrics="$(hex_rgb_metrics "$1")"
    local r g b alpha spread
    read -r r g b alpha spread <<<"$metrics"
    (( alpha >= 184 && alpha <= 216 ))
}

theme_property_line() {
    local file="$1"
    local token="$2"
    grep -nE "^[[:space:]]*(readonly[[:space:]]+)?property[[:space:]]+color[[:space:]]+${token}[[:space:]]*:" "$file" | head -n 1 || true
}

detect_manual_blur_overlay_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_blur = 0
            blur_depth = 0
            watch_after_blur = 0
            in_rect = 0
            rect_depth = 0
            rect_fill_parent = 0
            rect_color = ""
            rect_color_line = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_blur && line ~ /StyledBehindWindowBlur[[:space:]]*\{/) {
                in_blur = 1
                blur_depth = delta
                watch_after_blur = 48
                next
            }

            if (in_blur) {
                blur_depth += delta
                if (blur_depth <= 0) {
                    in_blur = 0
                }
                watch_after_blur = 48
                next
            }

            if (watch_after_blur > 0) {
                if (!in_rect && line ~ /^[[:space:]]*Rectangle[[:space:]]*\{/) {
                    in_rect = 1
                    rect_depth = delta
                    rect_fill_parent = 0
                    rect_color = ""
                    rect_color_line = 0
                    next
                }

                if (in_rect) {
                    if (rect_depth == 1 && line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/) {
                        rect_fill_parent = 1
                    }
                    if (rect_depth == 1 && line ~ /^[[:space:]]*color[[:space:]]*:/) {
                        rect_color = line
                        rect_color_line = NR
                    }

                    rect_depth += delta
                    if (rect_depth <= 0) {
                        if (rect_fill_parent && rect_color_line > 0 && rect_color !~ /transparent/) {
                            print rect_color_line ":" rect_color
                        }
                        in_rect = 0
                    }
                    next
                }

                watch_after_blur--
            }
        }
    ' "$file"
}

detect_dialog_overlay_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_dialog = 0
            dialog_depth = 0
            in_rect = 0
            rect_depth = 0
            rect_fill_parent = 0
            rect_color = ""
            rect_color_line = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_dialog && line ~ /^[[:space:]]*D\.(Dialog|DialogWindow)[[:space:]]*\{/) {
                in_dialog = 1
                dialog_depth = 0
            }

            if (in_dialog) {
                if (line ~ /StyledBehindWindowBlur[[:space:]]*\{/)
                    printf "%s: DTK dialog adds a manual blur layer inside the dialog surface\n", NR

                if (!in_rect && line ~ /^[[:space:]]*Rectangle[[:space:]]*\{/) {
                    in_rect = 1
                    rect_depth = delta
                    rect_fill_parent = 0
                    rect_color = ""
                    rect_color_line = 0
                } else if (in_rect) {
                    if (rect_depth == 1 && line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/)
                        rect_fill_parent = 1
                    if (rect_depth == 1 && line ~ /^[[:space:]]*color[[:space:]]*:/) {
                        rect_color = line
                        rect_color_line = NR
                    }

                    rect_depth += delta
                    if (rect_depth <= 0) {
                        if (rect_fill_parent && rect_color_line > 0 && rect_color !~ /transparent/)
                            printf "%s: DTK dialog adds a self-drawn full-surface Rectangle overlay\n", rect_color_line
                        in_rect = 0
                    }
                }

                dialog_depth += delta
                if (dialog_depth <= 0) {
                    in_dialog = 0
                    in_rect = 0
                }
            }
        }
    ' "$file"
}

detect_sidebar_blur_covered_by_base_surface_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            nest = 0
            in_rect = 0
            rect_depth = 0
            rect_parent_nest = 0
            rect_fill_parent = 0
            rect_color_line = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_rect && line ~ /^[[:space:]]*Rectangle[[:space:]]*\{/) {
                in_rect = 1
                rect_depth = delta
                rect_parent_nest = nest
                rect_fill_parent = 0
                rect_color_line = 0
                nest += delta
                next
            }

            if (in_rect) {
                if (rect_depth == 1 && line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/) {
                    rect_fill_parent = 1
                }
                if (rect_depth == 1 && line ~ /^[[:space:]]*color[[:space:]]*:[[:space:]]*Theme\.(bg|bgPanel|bgToolbar|surface|panelBg|titlebarBg)([^A-Za-z0-9_]|$)/) {
                    rect_color_line = NR
                    rect_color_text = line
                }

                rect_depth += delta
                nest += delta
                if (rect_depth <= 0) {
                    if (rect_parent_nest <= 2 && rect_fill_parent && rect_color_line > 0) {
                        print rect_color_line ":" rect_color_text
                    }
                    in_rect = 0
                }
                next
            }

            nest += delta
        }
    ' "$file"
}

file_has_root_dtk_template_control() {
    local file="$1"
    awk '
        /^[[:space:]]*(import|pragma)([[:space:]]|$)/ { next }
        /^[[:space:]]*$/ { next }
        /^[[:space:]]*\/\// { next }
        {
            if ($0 ~ /^[[:space:]]*D\.(Switch|CheckBox|ComboBox|Button|TextField|Menu|Dialog|ProgressBar)[[:space:]]*\{/) {
                print "yes"
            }
            exit
        }
    ' "$file"
}

file_has_root_application_window() {
    local file="$1"
    awk '
        /^[[:space:]]*(import|pragma)([[:space:]]|$)/ { next }
        /^[[:space:]]*$/ { next }
        /^[[:space:]]*\/\// { next }
        {
            if ($0 ~ /^[[:space:]]*((D\.)?ApplicationWindow|Window)[[:space:]]*\{/) {
                print "yes"
            }
            exit
        }
    ' "$file"
}

file_has_root_item() {
    local file="$1"
    awk '
        /^[[:space:]]*(import|pragma)([[:space:]]|$)/ { next }
        /^[[:space:]]*$/ { next }
        /^[[:space:]]*\/\// { next }
        {
            if ($0 ~ /^[[:space:]]*Item[[:space:]]*\{/) {
                print "yes"
            }
            exit
        }
    ' "$file"
}

file_has_fill_parent_rectangle() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_rect = 0
            rect_depth = 0
            rect_fill_parent = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_rect && line ~ /^[[:space:]]*Rectangle[[:space:]]*\{/) {
                in_rect = 1
                rect_depth = 0
                rect_fill_parent = 0
            }

            if (in_rect) {
                if (line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/) {
                    rect_fill_parent = 1
                }

                rect_depth += delta
                if (rect_depth <= 0) {
                    if (rect_fill_parent) {
                        print "yes"
                        exit
                    }
                    in_rect = 0
                }
            }
        }
    ' "$file"
}

looks_like_fake_table() {
    local file="$1"
    local header_count
    local right_align_count

    header_count=$(grep -Ec 'Layout\.preferredWidth[[:space:]]*:' "$file" || true)
    right_align_count=$(grep -Ec 'horizontalAlignment[[:space:]]*:[[:space:]]*Text\.AlignRight' "$file" || true)

    if grep -q 'Repeater' "$file" \
        && (( header_count >= 3 )) \
        && (( right_align_count >= 2 )) \
        && ! grep -qE 'TableView|HorizontalHeaderView|columnWidths|columnPlan|sharedColumn' "$file"
    then
        return 0
    fi

    return 1
}

detect_full_window_blur_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_blur = 0
            blur_depth = 0
            blur_start = 0
            blur_fill_parent = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_blur && line ~ /StyledBehindWindowBlur[[:space:]]*\{/) {
                in_blur = 1
                blur_depth = 0
                blur_start = NR
                blur_fill_parent = 0
            }

            if (in_blur) {
                if (line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/) {
                    blur_fill_parent = 1
                }

                blur_depth += delta
                if (blur_depth <= 0) {
                    if (blur_fill_parent) {
                        print blur_start ": StyledBehindWindowBlur fills parent"
                    }
                    in_blur = 0
                }
            }
        }
    ' "$file"
}

detect_anchored_item_implicit_height_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_item() {
            in_item = 0
            item_depth = 0
            item_id = ""
            item_start = 0
            item_fill_parent = 0
        }

        BEGIN {
            reset_item()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_item && line ~ /^[[:space:]]*Item[[:space:]]*\{/) {
                in_item = 1
                item_depth = 0
                item_id = ""
                item_start = NR
                item_fill_parent = 0
            }

            if (in_item) {
                if (item_id == "" && line ~ /id[[:space:]]*:[[:space:]]*[A-Za-z_][A-Za-z0-9_]*/) {
                    item_id = line
                    sub(/.*id[[:space:]]*:[[:space:]]*/, "", item_id)
                    sub(/[^A-Za-z0-9_].*/, "", item_id)
                }
                if (line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/) {
                    item_fill_parent = 1
                }

                item_depth += delta
                if (item_depth <= 0) {
                    if (item_id != "" && item_fill_parent) {
                        anchored_item[item_id] = item_start
                    }
                    reset_item()
                }
            }

            if (line ~ /^[[:space:]]*implicitHeight[[:space:]]*:[[:space:]]*[A-Za-z_][A-Za-z0-9_]*\.implicitHeight/) {
                print_refs[NR] = line
                sub(/^[[:space:]]*implicitHeight[[:space:]]*:[[:space:]]*/, "", print_refs[NR])
                sub(/\.implicitHeight.*/, "", print_refs[NR])
            }
        }

        END {
            for (line_no in print_refs) {
                if (print_refs[line_no] in anchored_item) {
                    printf "%s: implicitHeight references anchored Item '%s'\n", line_no, print_refs[line_no]
                }
            }
        }
    ' "$file"
}

detect_self_binding_hits() {
    local file="$1"
    grep -nE '^[[:space:]]*(title|description|subtitle|text|label|name|statusText|iconName|value|checked|enabled|visible|selected|currentIndex|source|modelData)[[:space:]]*:[[:space:]]*\1([[:space:]]*(//.*)?$)' "$file" || true
}

detect_custom_window_button_hits() {
    local file="$1"
    if grep -qE 'showMinimized\(|showMaximized\(|showNormal\(' "$file" \
        && grep -qE '(^|[[:space:]])(D\.)?ToolButton([[:space:]]|\{)|(^|[[:space:]])(D\.)?Button([[:space:]]|\{)' "$file" \
        && ( grep -qE 'text[[:space:]]*:[[:space:]]*"(最小化|最大化|还原|关闭)"' "$file" \
            || grep -qE 'icon\.source[[:space:]]*:[[:space:]]*".*(minus|square|close|x)\.svg"' "$file" \
            || [[ "$(basename "$file")" == *WindowControls*.qml ]] ) \
        && ! grep -q 'WindowButtonGroup' "$file"
    then
        grep -nE 'showMinimized\(|showMaximized\(|showNormal\(' "$file" || true
    fi
}

detect_window_button_group_placement_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_block = 0
            depth = 0
            start = 0
            has_top = 0
            has_right = 0
            has_layout_align = 0
            has_center = 0
            top_margin = -1
            right_margin = -1
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line ~ /^[[:space:]]*D\.WindowButtonGroup[[:space:]]*\{/) {
                in_block = 1
                depth = 0
                start = NR
                has_top = 0
                has_right = 0
                has_layout_align = 0
                has_center = 0
                top_margin = -1
                right_margin = -1
            }

            if (in_block) {
                if (depth == 1 && line ~ /anchors\.top[[:space:]]*:[[:space:]]*parent\.top/)
                    has_top = 1
                if (depth == 1 && line ~ /anchors\.right[[:space:]]*:[[:space:]]*parent\.right/)
                    has_right = 1
                if (depth == 1 && line ~ /Layout\.alignment[[:space:]]*:.*Qt\.AlignRight/ && line ~ /Qt\.AlignTop/)
                    has_layout_align = 1
                if (depth == 1 && line ~ /anchors\.centerIn[[:space:]]*:/)
                    has_center = 1
                if (depth == 1 && line ~ /anchors\.topMargin[[:space:]]*:[[:space:]]*[0-9]+/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    top_margin = value + 0
                }
                if (depth == 1 && line ~ /anchors\.rightMargin[[:space:]]*:[[:space:]]*[0-9]+/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    right_margin = value + 0
                }

                depth += delta
                if (depth <= 0) {
                    if (has_center)
                        printf "%s: WindowButtonGroup is centered inside a wrapper instead of sitting on the top-right edge\n", start
                    if (top_margin > 0 || right_margin > 0)
                        printf "%s: WindowButtonGroup uses positive top/right margins and therefore leaves a visible edge gap\n", start
                    if (!has_center && !has_layout_align && !(has_top && has_right))
                        printf "%s: WindowButtonGroup is not explicitly aligned to the top-right edge\n", start
                    in_block = 0
                }
            }
        }
    ' "$file"
}

detect_titlebar_safe_area_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_content() {
            in_content = 0
            content_depth = 0
            content_start = 0
            content_fill_parent = 0
            content_has_trailing_reserve = 0
            in_mouse = 0
            mouse_depth = 0
            mouse_start = 0
            mouse_fill_parent = 0
        }

        BEGIN {
            in_titlebar = 0
            depth = 0
            direct_mouse = 0
            direct_mouse_depth = 0
            direct_mouse_start = 0
            direct_mouse_fill_parent = 0
            reset_content()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_titlebar && line ~ /^[[:space:]]*D\.TitleBar[[:space:]]*\{/) {
                in_titlebar = 1
                depth = 0
                direct_mouse = 0
                direct_mouse_depth = 0
                direct_mouse_start = 0
                direct_mouse_fill_parent = 0
                reset_content()
            }

            if (in_titlebar) {
                if (!in_content && depth == 1 && line ~ /^[[:space:]]*content[[:space:]]*:[[:space:]]*[A-Za-z_][A-Za-z0-9_.]*[[:space:]]*\{/) {
                    in_content = 1
                    content_depth = 0
                    content_start = NR
                    content_fill_parent = 0
                    content_has_trailing_reserve = 0
                    in_mouse = 0
                    mouse_depth = 0
                    mouse_start = 0
                    mouse_fill_parent = 0
                }

                if (!direct_mouse && depth == 1 && line ~ /^[[:space:]]*MouseArea[[:space:]]*\{/) {
                    direct_mouse = 1
                    direct_mouse_depth = 0
                    direct_mouse_start = NR
                    direct_mouse_fill_parent = 0
                }

                if (in_content) {
                    if (!in_mouse && line ~ /^[[:space:]]*MouseArea[[:space:]]*\{/) {
                        in_mouse = 1
                        mouse_depth = 0
                        mouse_start = NR
                        mouse_fill_parent = 0
                    }

                    if (content_depth == 1 && line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/)
                        content_fill_parent = 1

                    if (content_depth == 1 && line ~ /anchors\.rightMargin[[:space:]]*:/)
                        content_has_trailing_reserve = 1
                    if (content_depth == 1 && line ~ /Layout\.rightMargin[[:space:]]*:/)
                        content_has_trailing_reserve = 1
                    if (content_depth == 1 && line ~ /rightPadding[[:space:]]*:/)
                        content_has_trailing_reserve = 1
                    if (content_depth == 1 && line ~ /anchors\.right[[:space:]]*:[[:space:]]*[A-Za-z_][A-Za-z0-9_]*\.left/)
                        content_has_trailing_reserve = 1
                    if (content_depth == 1 && line ~ /width[[:space:]]*:[[:space:]]*parent\.width[[:space:]]*-/)
                        content_has_trailing_reserve = 1
                    if (content_depth == 1 && line ~ /Layout\.maximumWidth[[:space:]]*:/)
                        content_has_trailing_reserve = 1
                    if (content_depth == 1 && line ~ /maximumWidth[[:space:]]*:/)
                        content_has_trailing_reserve = 1

                    if (in_mouse) {
                        if (mouse_depth == 1 && line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/)
                            mouse_fill_parent = 1

                        mouse_depth += delta
                        if (mouse_depth <= 0) {
                            if (mouse_fill_parent)
                                printf "%s: MouseArea fills D.TitleBar.content and can cover the DTK trailing control strip\n", mouse_start
                            in_mouse = 0
                        }
                    }

                    content_depth += delta
                    if (content_depth <= 0) {
                        if (content_fill_parent && !content_has_trailing_reserve)
                            printf "%s: D.TitleBar.content fills the full titlebar width without reserving the DTK trailing control safe area\n", content_start
                        reset_content()
                    }
                }

                if (direct_mouse) {
                    if (direct_mouse_depth == 1 && line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/)
                        direct_mouse_fill_parent = 1

                    direct_mouse_depth += delta
                    if (direct_mouse_depth <= 0) {
                        if (direct_mouse_fill_parent)
                            printf "%s: MouseArea fills the full D.TitleBar and can steal the DTK trailing control strip\n", direct_mouse_start
                        direct_mouse = 0
                    }
                }

                depth += delta
                if (depth <= 0) {
                    in_titlebar = 0
                    reset_content()
                    direct_mouse = 0
                }
            }
        }
    ' "$file"
}

detect_titlebar_clipped_ancestor_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function object_type(s,   line) {
            line = s
            sub(/^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*:[[:space:]]*/, "", line)
            if (line ~ /^[[:space:]]*[A-Za-z_][A-Za-z0-9_.]*([[:space:]]+on[[:space:]]+[A-Za-z_][A-Za-z0-9_]*)?[[:space:]]*\{/) {
                sub(/^[[:space:]]*/, "", line)
                sub(/[[:space:]]*\{.*/, "", line)
                sub(/[[:space:]].*/, "", line)
                return line
            }
            return ""
        }

        BEGIN {
            level = 0
        }

        {
            line = $0
            type = object_type(line)
            if (type != "") {
                level++
                stack_type[level] = type
                stack_start[level] = NR
                stack_clip[level] = 0

                if (type == "D.TitleBar" || type == "TitleBar" || type == "D.WindowButtonGroup" || type == "WindowButtonGroup") {
                    for (i = level - 1; i >= 1; --i) {
                        if (stack_clip[i]) {
                            printf "%s: %s is nested inside clipped ancestor %s from line %s\n", NR, type, stack_type[i], stack_start[i]
                            break
                        }
                    }
                }
            }

            if (level > 0 && line ~ /^[[:space:]]*clip[[:space:]]*:[[:space:]]*true/)
                stack_clip[level] = 1

            delta = brace_delta(line)
            if (delta < 0) {
                for (i = 0; i < -delta; ++i) {
                    delete stack_type[level]
                    delete stack_start[level]
                    delete stack_clip[level]
                    level--
                }
            }
        }
    ' "$file"
}

detect_risky_titlebar_flag_hits() {
    local file="$1"
    if [[ "$(file_has_root_application_window "$file")" != "yes" ]]; then
        return
    fi

    if ! grep -qE '(^|[[:space:]])D\.TitleBar([[:space:]]|\{)' "$file"; then
        return
    fi

    if grep -qE '^[[:space:]]*flags[[:space:]]*:.*Qt\.CustomizeWindowHint' "$file"; then
        grep -nE '^[[:space:]]*flags[[:space:]]*:.*Qt\.CustomizeWindowHint' "$file" \
            | sed 's/$/: DTK main window uses Qt.CustomizeWindowHint in the normal title-bar path/'
    fi

    if grep -qE '^[[:space:]]*flags[[:space:]]*:' "$file" \
        && ! grep -qE '^[[:space:]]*flags[[:space:]]*:.*Qt\.WindowTitleHint' "$file"
    then
        grep -nE '^[[:space:]]*flags[[:space:]]*:' "$file" \
            | sed 's/$/: explicit DTK main-window flags omit Qt.WindowTitleHint/'
    fi
}

detect_transparent_titlebar_background_hits() {
    local file="$1"
    if [[ "$(file_has_root_application_window "$file")" != "yes" ]]; then
        return
    fi

    if ! grep -qE '(^|[[:space:]])D\.TitleBar([[:space:]]|\{)' "$file"; then
        return
    fi

    if ! grep -qE '^[[:space:]]*color[[:space:]]*:[[:space:]]*["'\'']transparent["'\'']' "$file"; then
        return
    fi

    if ! grep -qE 'Theme\.(titlebarBg|bgToolbar)([^A-Za-z0-9_]|$)' "$file"; then
        grep -nE '^[[:space:]]*D\.TitleBar[[:space:]]*\{' "$file" \
            | sed 's/$/: transparent main window uses D.TitleBar but no explicit title-band background surface token was found/'
    fi
}

detect_titleband_underlay_gap_hits() {
    local file="$1"
    if [[ "$(file_has_root_application_window "$file")" != "yes" ]]; then
        return
    fi

    if ! grep -qE '(^|[[:space:]])D\.TitleBar([[:space:]]|\{)' "$file"; then
        return
    fi

    if ! grep -qE '^[[:space:]]*color[[:space:]]*:[[:space:]]*["'\'']transparent["'\'']' "$file"; then
        return
    fi

    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_block = 0
            depth = 0
            start = 0
            has_top = 0
            has_top_margin = 0
            has_right = 0
            has_theme_base = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line ~ /^[[:space:]]*(Rectangle|Item)[[:space:]]*\{/) {
                in_block = 1
                depth = 0
                start = NR
                has_top = 0
                has_top_margin = 0
                has_right = 0
                has_theme_base = 0
            }

            if (in_block) {
                if (depth == 1 && line ~ /anchors\.top[[:space:]]*:[[:space:]]*parent\.top/)
                    has_top = 1
                if (depth == 1 && line ~ /anchors\.topMargin[[:space:]]*:[[:space:]]*.*chromeHeight/)
                    has_top_margin = 1
                if (depth == 1 && line ~ /anchors\.right[[:space:]]*:[[:space:]]*parent\.right/)
                    has_right = 1
                if (depth == 1 && line ~ /color[[:space:]]*:[[:space:]]*Theme\.(panelBg|bg|bgPanel)/)
                    has_theme_base = 1

                depth += delta
                if (depth <= 0) {
                    if (has_top && has_top_margin && has_right && has_theme_base)
                        printf "%s: content-side base surface starts below chromeHeight instead of extending under the title band\n", start
                    in_block = 0
                }
            }
        }
    ' "$file"
}

detect_large_window_size_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_root = 0
            depth = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_root && line ~ /^[[:space:]]*((D\.)?ApplicationWindow|Window)[[:space:]]*\{/) {
                in_root = 1
                depth = 0
            }

            if (in_root) {
                if (depth == 1 && line ~ /^[[:space:]]*(width|height|minimumWidth|minimumHeight)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    prop = line
                    sub(/^[[:space:]]*/, "", prop)
                    split(prop, parts, ":")
                    key = parts[1]
                    value = parts[2]
                    gsub(/[^0-9]/, "", value)
                    num = value + 0

                    if (key == "width" && num > 1280)
                        printf "%s: width %d exceeds 1280 baseline\n", NR, num
                    if (key == "height" && num > 840)
                        printf "%s: height %d exceeds 840 baseline\n", NR, num
                    if (key == "minimumWidth" && num > 1040)
                        printf "%s: minimumWidth %d exceeds 1040 baseline\n", NR, num
                    if (key == "minimumHeight" && num > 720)
                        printf "%s: minimumHeight %d exceeds 720 baseline\n", NR, num
                }

                depth += delta
                if (depth <= 0)
                    in_root = 0
            }
        }
    ' "$file"
}

detect_small_settings_dialog_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_root = 0
            depth = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_root && line ~ /^[[:space:]]*((Settings\.)?SettingsDialog)[[:space:]]*\{/) {
                in_root = 1
                depth = 0
            }

            if (in_root) {
                if (depth == 1 && line ~ /^[[:space:]]*(width|height)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    prop = line
                    sub(/^[[:space:]]*/, "", prop)
                    split(prop, parts, ":")
                    key = parts[1]
                    value = parts[2]
                    gsub(/[^0-9]/, "", value)
                    num = value + 0

                    if (key == "width" && num < 960)
                        printf "%s: settings dialog width %d is below 960 baseline\n", NR, num
                    if (key == "height" && num < 680)
                        printf "%s: settings dialog height %d is below 680 baseline\n", NR, num
                }

                depth += delta
                if (depth <= 0)
                    in_root = 0
            }
        }
    ' "$file"
}

detect_settings_dialog_missing_icon_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_root = 0
            depth = 0
            root_line = 0
            has_icon = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_root && line ~ /^[[:space:]]*((Settings\.)?SettingsDialog)[[:space:]]*\{/) {
                in_root = 1
                depth = 0
                root_line = NR
                has_icon = 0
            }

            if (in_root) {
                if (depth == 1 && line ~ /^[[:space:]]*icon[[:space:]]*:/)
                    has_icon = 1

                depth += delta
                if (depth <= 0) {
                    if (!has_icon)
                        printf "%s: Settings.SettingsDialog root omits icon; populate the standard top-left icon slot\n", root_line
                    in_root = 0
                }
            }
        }
    ' "$file"
}

detect_standard_dtk_surface_system_titlebar_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_target = 0
            depth = 0
            root_line = 0
            target_type = ""
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_target && line ~ /^[[:space:]]*((D\.)?AboutDialog|(Settings\.)?SettingsDialog)[[:space:]]*\{/) {
                in_target = 1
                depth = 0
                root_line = NR
                target_type = line
                sub(/^[[:space:]]*/, "", target_type)
                sub(/[[:space:]]*\{.*/, "", target_type)
            }

            if (in_target) {
                if (depth == 1 && line ~ /^[[:space:]]*D\.DWindow\.enabled[[:space:]]*:[[:space:]]*false\b/) {
                    printf "%s: %s should keep the local DTK title bar; do not force a system title bar with D.DWindow.enabled: false\n", NR, target_type
                }

                depth += delta
                if (depth <= 0) {
                    in_target = 0
                    target_type = ""
                }
            }
        }
    ' "$file"
}

detect_settings_checkbox_fallback_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_root = 0
            depth = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_root && line ~ /^[[:space:]]*((Settings\.)?SettingsDialog)[[:space:]]*\{/) {
                in_root = 1
                depth = 0
            }

            if (in_root) {
                if (line ~ /(^|[^A-Za-z0-9_.])(D\.)?CheckBox[[:space:]]*\{/) {
                    printf "%s: checkbox-style settings rows should use Settings.CheckBox when it is exported locally\n", NR
                }

                depth += delta
                if (depth <= 0)
                    in_root = 0
            }
        }
    ' "$file"
}

detect_settings_option_delegate_theme_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_delegate = 0
            depth = 0
            theme_line = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_delegate && line ~ /Settings\.OptionDelegate[[:space:]]*\{/) {
                in_delegate = 1
                depth = 0
                theme_line = 0
            }

            if (in_delegate) {
                if (!theme_line && line ~ /Theme\./)
                    theme_line = NR

                depth += delta
                if (depth <= 0) {
                    if (theme_line)
                        printf "%s: custom settings fallback row uses project Theme metrics instead of staying on DTK settings rhythm\n", theme_line
                    in_delegate = 0
                }
            }
        }
    ' "$file"
}

detect_shadowed_delegate_role_hits() {
    local file="$1"
    if grep -qE 'SettingRow[[:space:]]*\{|SectionCard[[:space:]]*\{|MetricCard[[:space:]]*\{|PageHeader[[:space:]]*\{|StatusBadge[[:space:]]*\{|CircularScore[[:space:]]*\{' "$file" \
        && grep -qE 'required[[:space:]]+property[[:space:]]+[A-Za-z0-9_.]+[[:space:]]+(title|description|subtitle|text|statusText|label|name|valueText|captionText|secondaryText|primaryText)\b' "$file" \
        && grep -qE '^[[:space:]]*(title|description|subtitle|text|statusText|label|name|valueText|captionText|secondaryText|primaryText)[[:space:]]*:' "$file"
    then
        grep -nE 'required[[:space:]]+property[[:space:]]+[A-Za-z0-9_.]+[[:space:]]+(title|description|subtitle|text|statusText|label|name|valueText|captionText|secondaryText|primaryText)\b' "$file" || true
    fi
}

detect_small_circular_score_usage_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_block = 0
            depth = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line ~ /^[[:space:]]*CircularScore[[:space:]]*\{/) {
                in_block = 1
                depth = 0
            }

            if (in_block) {
                if (depth == 1 && line ~ /^[[:space:]]*(width|height|Layout\.preferredWidth|Layout\.preferredHeight)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    num = value + 0
                    if (num > 0 && num < 220)
                        printf "%s: CircularScore consumed at %d, below 220 safe-size baseline\n", NR, num
                }

                depth += delta
                if (depth <= 0)
                    in_block = 0
            }
        }
    ' "$file"
}

detect_multiline_setting_row_missing_icon_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_row = 0
            depth = 0
            start = 0
            has_multiline = 0
            has_leading = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_row && line ~ /^[[:space:]]*SettingRow[[:space:]]*\{/) {
                in_row = 1
                depth = 0
                start = NR
                has_multiline = 0
                has_leading = 0
            }

            if (in_row) {
                if (depth == 1 && line ~ /^[[:space:]]*description[[:space:]]*:/ && line !~ /""[[:space:]]*$/) {
                    has_multiline = 1
                }
                if (depth == 1 && (line ~ /^[[:space:]]*leading[[:space:]]*:/ || line ~ /^[[:space:]]*leadingWidth[[:space:]]*:[[:space:]]*[1-9][0-9]*/)) {
                    has_leading = 1
                }

                depth += delta
                if (depth <= 0) {
                    if (has_multiline && !has_leading) {
                        printf "%s: SettingRow with multi-line description lacks a leading icon slot\n", start
                    }
                    in_row = 0
                }
            }
        }
    ' "$file"
}

detect_multiline_setting_row_icon_size_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_row = 0
            depth = 0
            start = 0
            has_multiline = 0
            leading_width = -1
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_row && line ~ /^[[:space:]]*SettingRow[[:space:]]*\{/) {
                in_row = 1
                depth = 0
                start = NR
                has_multiline = 0
                leading_width = -1
            }

            if (in_row) {
                if (depth == 1 && line ~ /^[[:space:]]*description[[:space:]]*:/ && line !~ /""[[:space:]]*$/) {
                    has_multiline = 1
                }
                if (depth == 1 && line ~ /^[[:space:]]*leadingWidth[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    leading_width = value + 0
                }

                depth += delta
                if (depth <= 0) {
                    if (has_multiline && leading_width > 0 && leading_width != 24 && leading_width != 32) {
                        printf "%s: multi-line SettingRow uses leadingWidth %d; expected 24 or 32 icon baseline\n", start, leading_width
                    }
                    in_row = 0
                }
            }
        }
    ' "$file"
}

detect_secondary_settings_entry_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_button = 0
            depth = 0
            start = 0
            has_settings_text = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_button && line ~ /^[[:space:]]*((D\.)?(Button|RecommandButton|WarningButton|ToolButton|IconButton)|QQC\.Button)[[:space:]]*\{/) {
                in_button = 1
                depth = 0
                start = NR
                has_settings_text = 0
            }

            if (in_button) {
                if (depth == 1 && line ~ /^[[:space:]]*text[[:space:]]*:[[:space:]]*"设置"[[:space:]]*$/) {
                    has_settings_text = 1
                }

                depth += delta
                if (depth <= 0) {
                    if (has_settings_text) {
                        printf "%s: standalone settings button found outside the main menu path\n", start
                    }
                    in_button = 0
                }
            }
        }
    ' "$file"
}

detect_wide_button_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_button = 0
            depth = 0
            start = 0
            has_fill = 0
            has_max = 0
            wide_width = -1
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_button && line ~ /^[[:space:]]*((D\.)?(Button|RecommandButton|WarningButton)|QQC\.Button|Button)[[:space:]]*\{/) {
                in_button = 1
                depth = 0
                start = NR
                has_fill = 0
                has_max = 0
                wide_width = -1
            }

            if (in_button) {
                if (depth == 1 && line ~ /^[[:space:]]*(Layout\.fillWidth|fillWidth)[[:space:]]*:[[:space:]]*true[[:space:]]*$/) {
                    has_fill = 1
                }
                if (depth == 1 && line ~ /^[[:space:]]*width[[:space:]]*:[[:space:]]*[^0-9]*parent\.width/) {
                    has_fill = 1
                }
                if (depth == 1 && line ~ /^[[:space:]]*(Layout\.maximumWidth|maximumWidth)[[:space:]]*:/) {
                    has_max = 1
                }
                if (depth == 1 && line ~ /^[[:space:]]*(width|Layout\.preferredWidth)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    num = value + 0
                    if (num > 260)
                        wide_width = num
                }

                depth += delta
                if (depth <= 0) {
                    if (wide_width > 0) {
                        printf "%s: button width %d exceeds the capped-width baseline\n", start, wide_width
                    }
                    if (has_fill && !has_max) {
                        printf "%s: fill-width button lacks maximumWidth or Layout.maximumWidth\n", start
                    }
                    in_button = 0
                }
            }
        }
    ' "$file"
}

detect_horizontal_scroll_risk_hits() {
    local file="$1"
    {
        grep -nE 'flickableDirection[[:space:]]*:[[:space:]]*Flickable\.(HorizontalFlick|AutoFlickDirection)' "$file" || true
        grep -nE 'ScrollBar\.horizontal\.(policy|visible)[[:space:]]*:[[:space:]]*(true|ScrollBar\.(AsNeeded|AlwaysOn))' "$file" || true
        grep -nE 'contentWidth[[:space:]]*:[[:space:]]*([0-9]+|.*childrenRect\.width|.*implicitWidth)' "$file" || true
    } | awk '!seen[$0]++'
}

detect_horizontal_scrollbar_thickness_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function flush_bar() {
            if (in_bar) {
                if (orientation == "horizontal" && max_height > 20)
                    printf "%s: horizontal ScrollBar thickness %d exceeds the 20px limit\n", start, max_height
                else if (orientation == "vertical" && max_width > 20)
                    printf "%s: vertical ScrollBar thickness %d exceeds the 20px limit\n", start, max_width
            }

            in_bar = 0
            depth = 0
            start = 0
            orientation = ""
            max_height = 0
            max_width = 0
        }

        BEGIN {
            flush_bar()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_bar && line ~ /ScrollBar\.horizontal[[:space:]]*:[[:space:]]*(QQC\.)?ScrollBar[[:space:]]*\{/) {
                in_bar = 1
                depth = 0
                start = NR
                orientation = "horizontal"
                max_height = 0
                max_width = 0
            } else if (!in_bar && line ~ /ScrollBar\.vertical[[:space:]]*:[[:space:]]*(QQC\.)?ScrollBar[[:space:]]*\{/) {
                in_bar = 1
                depth = 0
                start = NR
                orientation = "vertical"
                max_height = 0
                max_width = 0
            } else if (!in_bar && line ~ /^[[:space:]]*(QQC\.)?ScrollBar[[:space:]]*\{/) {
                in_bar = 1
                depth = 0
                start = NR
                orientation = ""
                max_height = 0
                max_width = 0
            }

            if (in_bar) {
                if (depth == 1 && line ~ /^[[:space:]]*orientation[[:space:]]*:[[:space:]]*Qt\.Horizontal/)
                    orientation = "horizontal"
                else if (depth == 1 && line ~ /^[[:space:]]*orientation[[:space:]]*:[[:space:]]*Qt\.Vertical/)
                    orientation = "vertical"

                if (line ~ /(^|[^A-Za-z0-9_])(height|implicitHeight)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    num = value + 0
                    if (num > max_height)
                        max_height = num
                }

                if (line ~ /(^|[^A-Za-z0-9_])(width|implicitWidth)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    num = value + 0
                    if (num > max_width)
                        max_width = num
                }

                depth += delta
                if (depth <= 0)
                    flush_bar()
            }
        }

        END {
            if (in_bar)
                flush_bar()
        }
    ' "$file"
}

detect_duplicate_progress_mode_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function normalize_expr(s,   expr) {
            expr = s
            sub(/^[^:]*:[[:space:]]*/, "", expr)
            sub(/[[:space:]]*(\/\/.*)?$/, "", expr)
            gsub(/[[:space:]]+/, "", expr)
            gsub(/\/100(\.0+)?/, "", expr)
            gsub(/[()]/, "", expr)
            return expr
        }

        function start_block(kind_name) {
            in_block = 1
            block_kind = kind_name
            depth = 0
            start = NR
        }

        BEGIN {
            in_block = 0
            block_kind = ""
            depth = 0
            circular_count = 0
            linear_count = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line ~ /^[[:space:]]*CircularScore[[:space:]]*\{/) {
                start_block("circular")
            } else if (!in_block && line ~ /^[[:space:]]*(D\.)?ProgressBar[[:space:]]*\{/) {
                start_block("linear")
            }

            if (in_block) {
                if (depth == 1 && line ~ /^[[:space:]]*value[[:space:]]*:/) {
                    expr = normalize_expr(line)
                    if (expr != "") {
                        if (block_kind == "circular") {
                            circular_count++
                            circular_expr[circular_count] = expr
                            circular_line[circular_count] = start
                        } else if (block_kind == "linear") {
                            linear_count++
                            linear_expr[linear_count] = expr
                            linear_line[linear_count] = start
                        }
                    }
                }

                depth += delta
                if (depth <= 0) {
                    in_block = 0
                    block_kind = ""
                }
            }
        }

        END {
            for (i = 1; i <= circular_count; ++i) {
                for (j = 1; j <= linear_count; ++j) {
                    if (circular_expr[i] != "" && circular_expr[i] == linear_expr[j]) {
                        printf "%s: same ratio is rendered by both circular/ring and horizontal progress in this file; choose one form only\n", circular_line[i]
                        exit
                    }
                }
            }
        }
    ' "$file"
}

detect_legacy_page_list_row_hits() {
    local file="$1"
    case "$file" in
        */pages/*.qml) ;;
        *) return ;;
    esac

    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_repeat() {
            in_repeat = 0
            repeat_depth = 0
            repeat_targets_object_list = 0
        }

        function is_object_list_signal(s) {
            return s ~ /(software|startup|service|program|file|data)[A-Za-z0-9_]*(Items|Model|List|Results|Entries)/ \
                || s ~ /(visibleItems|filteredSoftwareItems|softwareItems|startupItemsModel)/
        }

        BEGIN {
            reset_repeat()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_repeat && line ~ /^[[:space:]]*(Repeater|ListView|GridView|PathView)[[:space:]]*\{/) {
                in_repeat = 1
                repeat_depth = 0
                repeat_targets_object_list = 0
            }

            if (in_repeat) {
                if (is_object_list_signal(line))
                    repeat_targets_object_list = 1

                if (repeat_targets_object_list && line ~ /^[[:space:]]*(SettingRow|SettingsOptionRow)[[:space:]]*\{/) {
                    row_type = line
                    sub(/^[[:space:]]*/, "", row_type)
                    sub(/[[:space:]]*\{.*$/, "", row_type)
                    printf "%s: variable-length page list should not rely on legacy %s defaults; use a compact responsive row plan\n", NR, row_type
                }

                repeat_depth += delta
                if (repeat_depth <= 0)
                    reset_repeat()
            }
        }
    ' "$file"
}

detect_variable_object_list_card_hits() {
    local file="$1"
    case "$file" in
        */pages/*.qml) ;;
        *) return ;;
    esac

    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_repeat() {
            in_repeat = 0
            repeat_depth = 0
            repeat_targets_object_list = 0
        }

        function is_object_list_signal(s) {
            return s ~ /(software|startup|service|program|file|data)[A-Za-z0-9_]*(Items|Model|List|Results|Entries)/ \
                || s ~ /(visibleItems|filteredSoftwareItems|softwareItems|startupItemsModel)/
        }

        BEGIN {
            reset_repeat()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_repeat && line ~ /^[[:space:]]*(Repeater|ListView|GridView|PathView)[[:space:]]*\{/) {
                in_repeat = 1
                repeat_depth = 0
                repeat_targets_object_list = 0
            }

            if (in_repeat) {
                if (is_object_list_signal(line))
                    repeat_targets_object_list = 1

                if (repeat_targets_object_list && line ~ /^[[:space:]]*SectionCard[[:space:]]*\{/) {
                    printf "%s: variable-length page list should not render each item as a standalone SectionCard; use compact responsive rows instead\n", NR
                }

                repeat_depth += delta
                if (repeat_depth <= 0)
                    reset_repeat()
            }
        }
    ' "$file"
}

detect_textless_progress_thickness_hits() {
    local file="$1"
    local base
    base="$(basename "$file")"

    awk -v base="$base" '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_block() {
            in_block = 0
            depth = 0
            start = 0
            has_text = 0
            has_cap = 0
            max_cap = -1
        }

        function line_is_linear_progress_decl(s) {
            return s ~ /^[[:space:]]*((D\.)?ProgressBar|[A-Za-z0-9_]*Progress(Bar|Strip|Track|Line|Rail|Indicator)?)[[:space:]]*\{/ \
                && s !~ /(Circular|Ring|Arc|Busy|Score|Gauge)/
        }

        function line_is_root_progress_shell(s) {
            return base ~ /Progress\.qml$/ \
                && base !~ /(Circular|Ring|Arc|Busy|Score|Gauge)/ \
                && s ~ /^[[:space:]]*(Item|Rectangle|Control)[[:space:]]*\{/
        }

        function capture_cap(s,   value, num) {
            has_cap = 1
            if (s ~ /:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                value = s
                sub(/.*:[[:space:]]*/, "", value)
                gsub(/[^0-9]/, "", value)
                num = value + 0
                if (num > max_cap)
                    max_cap = num
            } else if (s ~ /Math\.min\([^)]*20/ || s ~ /:[[:space:]]*20([[:space:]]*(\/\/.*)?$)/) {
                if (20 > max_cap)
                    max_cap = 20
            }
        }

        function flush_block() {
            if (in_block && !has_text) {
                if (!has_cap) {
                    printf "%s: textless progress indicator lacks an explicit <=20px thickness cap\n", start
                } else if (max_cap > 20) {
                    printf "%s: textless progress indicator thickness %d exceeds the 20px limit\n", start, max_cap
                }
            }
            reset_block()
        }

        BEGIN {
            reset_block()
            root_checked = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line_is_linear_progress_decl(line)) {
                in_block = 1
                depth = 0
                start = NR
            } else if (!in_block && !root_checked && line_is_root_progress_shell(line)) {
                in_block = 1
                depth = 0
                start = NR
                root_checked = 1
            }

            if (in_block) {
                if (depth >= 1 && line ~ /^[[:space:]]*((D\.)?Label|Text|MetricValueLabel)[[:space:]]*\{/)
                    has_text = 1

                if (depth == 1 && line ~ /^[[:space:]]*(height|implicitHeight|maximumHeight|minimumHeight|Layout\.preferredHeight|Layout\.maximumHeight|Layout\.minimumHeight)[[:space:]]*:/)
                    capture_cap(line)

                depth += delta
                if (depth <= 0)
                    flush_block()
            }
        }

        END {
            if (in_block)
                flush_block()
        }
    ' "$file"
}

detect_fixed_score_hero_card_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function flush_card() {
            if (in_card && fixed_height >= 360 && has_score && has_centered_layout)
                printf "%s: fixed tall score hero card should use content-driven spacing instead of a large static shell\n", start

            in_card = 0
            depth = 0
            start = 0
            fixed_height = 0
            has_score = 0
            has_centered_layout = 0
        }

        BEGIN {
            flush_card()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_card && line ~ /^[[:space:]]*SectionCard[[:space:]]*\{/) {
                in_card = 1
                depth = 0
                start = NR
                fixed_height = 0
                has_score = 0
                has_centered_layout = 0
            }

            if (in_card) {
                if (depth == 1 && line ~ /^[[:space:]]*(height|implicitHeight|Layout\.preferredHeight)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    num = value + 0
                    if (num > fixed_height)
                        fixed_height = num
                }

                if (line ~ /CircularScore[[:space:]]*\{/)
                    has_score = 1
                if (line ~ /anchors\.centerIn[[:space:]]*:[[:space:]]*parent/)
                    has_centered_layout = 1

                depth += delta
                if (depth <= 0)
                    flush_card()
            }
        }

        END {
            if (in_card)
                flush_card()
        }
    ' "$file"
}

detect_focal_wrapper_mismatch_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function numeric_value(s,   value) {
            value = s
            sub(/.*:[[:space:]]*/, "", value)
            gsub(/[^0-9.]/, "", value)
            return value + 0
        }

        function reset_wrapper() {
            in_wrapper = 0
            wrapper_depth = 0
            wrapper_start = 0
            wrapper_height = -1
            in_focal = 0
            focal_depth = 0
            focal_height = -1
        }

        BEGIN {
            reset_wrapper()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_wrapper && line ~ /^[[:space:]]*(Item|Rectangle)[[:space:]]*\{/) {
                in_wrapper = 1
                wrapper_depth = 0
                wrapper_start = NR
                wrapper_height = -1
                in_focal = 0
                focal_depth = 0
                focal_height = -1
            }

            if (in_wrapper) {
                if (wrapper_depth == 1 && line ~ /^[[:space:]]*(height|implicitHeight|Layout\.preferredHeight)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = numeric_value(line)
                    if (value > wrapper_height)
                        wrapper_height = value
                }

                if (!in_focal && wrapper_depth == 1 && line ~ /^[[:space:]]*(CircularScore|PerformanceChart)[[:space:]]*\{/) {
                    in_focal = 1
                    focal_depth = 0
                    focal_height = -1
                }

                if (in_focal) {
                    if (focal_depth == 1 && line ~ /^[[:space:]]*(height|implicitHeight|Layout\.preferredHeight)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                        value = numeric_value(line)
                        if (value > focal_height)
                            focal_height = value
                    }

                    focal_depth += delta
                    if (focal_depth <= 0) {
                        if (wrapper_height > 0 && focal_height > wrapper_height)
                            printf "%s: focal wrapper height %d is smaller than contained focal visual height %d\n", wrapper_start, wrapper_height, focal_height
                        in_focal = 0
                        focal_depth = 0
                        focal_height = -1
                    }
                }

                wrapper_depth += delta
                if (wrapper_depth <= 0)
                    reset_wrapper()
            }
        }
    ' "$file"
}

detect_fill_anchored_card_layout_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_card() {
            in_card = 0
            card_depth = 0
            card_start = 0
            in_layout = 0
            layout_depth = 0
            layout_start = 0
            layout_fill_anchor = 0
            layout_fill_spacer = 0
        }

        BEGIN {
            reset_card()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_card && line ~ /^[[:space:]]*SectionCard[[:space:]]*\{/) {
                in_card = 1
                card_depth = 0
                card_start = NR
                in_layout = 0
            }

            if (in_card) {
                if (!in_layout && card_depth == 1 && line ~ /^[[:space:]]*(ColumnLayout|RowLayout)[[:space:]]*\{/) {
                    in_layout = 1
                    layout_depth = 0
                    layout_start = NR
                    layout_fill_anchor = 0
                    layout_fill_spacer = 0
                }

                if (in_layout) {
                    if (layout_depth == 1 && line ~ /^[[:space:]]*anchors\.fill[[:space:]]*:[[:space:]]*parent/)
                        layout_fill_anchor = 1
                    if (line ~ /Layout\.fillHeight[[:space:]]*:[[:space:]]*true/)
                        layout_fill_spacer = 1

                    layout_depth += delta
                    if (layout_depth <= 0) {
                        if (layout_fill_anchor && layout_fill_spacer)
                            printf "%s: direct fill-anchored layout inside SectionCard uses Layout.fillHeight spacers and may bypass the card sizing flow\n", layout_start
                        in_layout = 0
                    }
                }

                card_depth += delta
                if (card_depth <= 0)
                    reset_card()
            }
        }
    ' "$file"
}

detect_oversized_card_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_card = 0
            depth = 0
            start = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_card && line ~ /^[[:space:]]*(SectionCard|MetricCard)[[:space:]]*\{/) {
                in_card = 1
                depth = 0
                start = NR
            }

            if (in_card) {
                if (depth == 1 && line ~ /^[[:space:]]*(height|implicitHeight|Layout\.preferredHeight)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    num = value + 0
                    if (num > 400)
                        printf "%s: card shell height %d exceeds the oversized-card baseline\n", start, num
                }

                depth += delta
                if (depth <= 0)
                    in_card = 0
            }
        }
    ' "$file"
}

detect_card_focal_content_edge_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function numeric_value(s,   value) {
            value = s
            sub(/.*:[[:space:]]*/, "", value)
            gsub(/[^0-9.]/, "", value)
            return value + 0
        }

        BEGIN {
            in_card = 0
            card_depth = 0
            card_padding = -1
            in_block = 0
            block_depth = 0
            block_start = 0
            block_has_focal = 0
            block_fill = 0
            block_left = 0
            block_right = 0
            block_top = 0
            block_bottom = 0
            block_margin = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_card && line ~ /^[[:space:]]*(SectionCard|MetricCard)[[:space:]]*\{/) {
                in_card = 1
                card_depth = 0
                card_padding = -1
                in_block = 0
            }

            if (in_card) {
                if (card_depth == 1 && line ~ /^[[:space:]]*padding[[:space:]]*:[[:space:]]*([0-9]+|0\.[0-9]+)/)
                    card_padding = numeric_value(line)

                if (!in_block && line ~ /^[[:space:]]*(Item|Rectangle|Row|Column|Grid|RowLayout|ColumnLayout|GridLayout|Loader|Canvas|Image|SvgIcon|CircularScore|PerformanceChart|MetricValueLabel)[[:space:]]*\{/) {
                    in_block = 1
                    block_depth = 0
                    block_start = NR
                    block_has_focal = (line ~ /(Canvas|Image|SvgIcon|CircularScore|PerformanceChart)[[:space:]]*\{/)
                    block_fill = 0
                    block_left = 0
                    block_right = 0
                    block_top = 0
                    block_bottom = 0
                    block_margin = 0
                }

                if (in_block) {
                    if (line ~ /CircularScore[[:space:]]*\{|PerformanceChart[[:space:]]*\{|Canvas[[:space:]]*\{|Image[[:space:]]*\{|SvgIcon[[:space:]]*\{/)
                        block_has_focal = 1
                    if (line ~ /^[[:space:]]*valueSize[[:space:]]*:[[:space:]]*([2-9][8-9]|[3-9][0-9]|[1-9][0-9][0-9])([^0-9]|$)/)
                        block_has_focal = 1

                    if (block_depth == 1 && line ~ /^[[:space:]]*anchors\.fill[[:space:]]*:[[:space:]]*parent([[:space:]]*(\/\/.*)?$)/)
                        block_fill = 1
                    if (block_depth == 1 && line ~ /^[[:space:]]*anchors\.left[[:space:]]*:[[:space:]]*parent\.left/)
                        block_left = 1
                    if (block_depth == 1 && line ~ /^[[:space:]]*anchors\.right[[:space:]]*:[[:space:]]*parent\.right/)
                        block_right = 1
                    if (block_depth == 1 && line ~ /^[[:space:]]*anchors\.top[[:space:]]*:[[:space:]]*parent\.top/)
                        block_top = 1
                    if (block_depth == 1 && line ~ /^[[:space:]]*anchors\.bottom[[:space:]]*:[[:space:]]*parent\.bottom/)
                        block_bottom = 1
                    if (block_depth == 1 \
                        && line ~ /^[[:space:]]*anchors\.(margins|leftMargin|rightMargin|topMargin|bottomMargin)[[:space:]]*:/ \
                        && line !~ /:[[:space:]]*0([[:space:]]*(\/\/.*)?$)/ \
                        && line !~ /:[[:space:]]*0\.0+([[:space:]]*(\/\/.*)?$)/)
                        block_margin = 1

                    block_depth += delta
                    if (block_depth <= 0) {
                        if (card_padding == 0 && block_has_focal && !block_margin && (block_fill || (block_left && block_right) || (block_top && block_bottom)))
                            printf "%s: zero-padding card lets focal foreground content bind to parent edges without an inner safe area\n", block_start
                        in_block = 0
                    }
                }

                card_depth += delta
                if (card_depth <= 0)
                    in_card = 0
            }
        }
    ' "$file"
}

detect_dense_cluster_zero_spacing_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_block = 0
            depth = 0
            start = 0
            spacing_zero = 0
            has_graphic = 0
            has_text = 0
            has_button = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line ~ /^[[:space:]]*(Row|Column|RowLayout|ColumnLayout)[[:space:]]*\{/) {
                in_block = 1
                depth = 0
                start = NR
                spacing_zero = 0
                has_graphic = 0
                has_text = 0
                has_button = 0
            }

            if (in_block) {
                if (depth == 1 && line ~ /^[[:space:]]*spacing[[:space:]]*:[[:space:]]*0([[:space:]]*(\/\/.*)?$)/)
                    spacing_zero = 1
                if (line ~ /SvgIcon|AppLogo|CircularScore|Image[[:space:]]*\{/)
                    has_graphic = 1
                if (line ~ /D\.Label[[:space:]]*\{|Label[[:space:]]*\{/)
                    has_text = 1
                if (line ~ /((D\.)?(Button|RecommandButton|WarningButton|ToolButton|IconButton)|QQC\.Button)[[:space:]]*\{/)
                    has_button = 1

                depth += delta
                if (depth <= 0) {
                    if (spacing_zero && ((has_graphic && has_text) || (has_graphic && has_button) || (has_text && has_button))) {
                        printf "%s: dense icon/text/button cluster uses spacing 0\n", start
                    }
                    in_block = 0
                }
            }
        }
    ' "$file"
}

detect_sidebar_selected_border_hits() {
    local file="$1"
    grep -nE 'border\.(color|width)[[:space:]]*:[[:space:]].*(current(Index)?|selected|checked|active)' "$file" || true
}

detect_sidebar_nav_icon_treatment_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function extract_selected_theme_token(s,   token) {
            token = s
            if (token !~ /\?[[:space:]]*Theme\.[A-Za-z0-9_]+/)
                return ""
            sub(/.*\?[[:space:]]*Theme\./, "", token)
            sub(/[^A-Za-z0-9_].*/, "", token)
            return token
        }

        function reset_rect() {
            in_rect = 0
            rect_depth = 0
            rect_has_svg = 0
            rect_color = ""
            rect_color_line = 0
        }

        function reset_nav() {
            in_nav = 0
            nav_depth = 0
            nav_start = 0
            icon_selected = ""
            label_selected = ""
            in_icon = 0
            icon_depth = 0
            in_label = 0
            label_depth = 0
            reset_rect()
        }

        BEGIN {
            reset_nav()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_nav && line ~ /delegate[[:space:]]*:[[:space:]]*Rectangle[[:space:]]*\{/) {
                in_nav = 1
                nav_depth = 0
                nav_start = NR
                icon_selected = ""
                label_selected = ""
                in_icon = 0
                icon_depth = 0
                in_label = 0
                label_depth = 0
                reset_rect()
            }

            if (in_nav) {
                if (!in_rect && nav_depth >= 1 && line ~ /^[[:space:]]*Rectangle[[:space:]]*\{/) {
                    in_rect = 1
                    rect_depth = 0
                    rect_has_svg = 0
                    rect_color = ""
                    rect_color_line = 0
                }

                if (in_rect) {
                    if (line ~ /SvgIcon[[:space:]]*\{/)
                        rect_has_svg = 1
                    if (rect_depth == 1 && line ~ /^[[:space:]]*color[[:space:]]*:/) {
                        rect_color = line
                        rect_color_line = NR
                    }

                    rect_depth += delta
                    if (rect_depth <= 0) {
                        if (rect_has_svg && rect_color_line > 0 && rect_color !~ /transparent/)
                            printf "%s: sidebar navigation item icon must not draw its own background tile\n", rect_color_line
                        reset_rect()
                    }
                }

                if (!in_icon && line ~ /^[[:space:]]*SvgIcon[[:space:]]*\{/) {
                    in_icon = 1
                    icon_depth = 0
                }

                if (in_icon) {
                    if (icon_depth == 1 && line ~ /^[[:space:]]*color[[:space:]]*:/ && icon_selected == "")
                        icon_selected = extract_selected_theme_token(line)

                    icon_depth += delta
                    if (icon_depth <= 0) {
                        in_icon = 0
                        icon_depth = 0
                    }
                }

                if (!in_label && line ~ /^[[:space:]]*D\.Label[[:space:]]*\{/) {
                    in_label = 1
                    label_depth = 0
                }

                if (in_label) {
                    if (label_depth == 1 && line ~ /^[[:space:]]*color[[:space:]]*:/ && label_selected == "")
                        label_selected = extract_selected_theme_token(line)

                    label_depth += delta
                    if (label_depth <= 0) {
                        in_label = 0
                        label_depth = 0
                    }
                }

                nav_depth += delta
                if (nav_depth <= 0) {
                    if (icon_selected != "" && label_selected != "" && icon_selected != label_selected)
                        printf "%s: selected sidebar icon color must match selected sidebar text color\n", nav_start
                    reset_nav()
                }
            }
        }
    ' "$file"
}

detect_sidebar_operational_button_width_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_button = 0
            depth = 0
            start = 0
            has_fill = 0
            has_width = 0
            has_max = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_button && line ~ /^[[:space:]]*((D\.)?(Button|RecommandButton|WarningButton)|QQC\.Button|Button)[[:space:]]*\{/) {
                in_button = 1
                depth = 0
                start = NR
                has_fill = 0
                has_width = 0
                has_max = 0
            }

            if (in_button) {
                if (depth == 1 && line ~ /^[[:space:]]*Layout\.fillWidth[[:space:]]*:[[:space:]]*true/)
                    has_fill = 1
                if (depth == 1 && line ~ /^[[:space:]]*width[[:space:]]*:[[:space:]].*(parent|root|contentColumn|contentLayout)\.width/)
                    has_width = 1
                if (depth == 1 && line ~ /^[[:space:]]*(Layout\.maximumWidth|maximumWidth)[[:space:]]*:/)
                    has_max = 1

                depth += delta
                if (depth <= 0) {
                    if (!has_fill && !has_width) {
                        printf "%s: sidebar operational-card button should maximize the usable card width\n", start
                    } else if (has_fill && !has_max) {
                        printf "%s: fill-width sidebar operational-card button should declare a maximum width equal to the usable card width\n", start
                    }
                    in_button = 0
                }
            }
        }
    ' "$file"
}

detect_detailed_gauge_center_text_hits() {
    local file="$1"
    {
        grep -nE 'captionText[[:space:]]*:' "$file" || true
        if [[ "$(basename "$file")" == *CircularScore*.qml ]]; then
            grep -nE 'property[[:space:]]+string[[:space:]]+captionText' "$file" || true
        fi
    } | awk '!seen[$0]++'
}

detect_nonstandard_sidebar_toggle_icon_hits() {
    local file="$1"
    if grep -qE 'collapseRequested|toggleSidebar|sidebarHidden|setSidebarWidth' "$file"; then
        grep -nE 'icon\.source[[:space:]]*:[[:space:]]*".*(chevron-(left|right)|arrow-(left|right)|go-(previous|next)|caret-(left|right)|angle-(left|right)).*"' "$file" || true
    fi
}

detect_moving_logo_slot_hits() {
    local file="$1"
    {
        case "$(basename "$file")" in
            *Sidebar*.qml)
                grep -nE 'AppLogo[[:space:]]*\{' "$file" || true
                ;;
        esac

        awk '
            function brace_delta(s,   tmp, opens, closes) {
                tmp = s
                opens = gsub(/\{/, "{", tmp)
                closes = gsub(/\}/, "}", tmp)
                return opens - closes
            }

            BEGIN {
                in_logo = 0
                depth = 0
            }

            {
                line = $0
                delta = brace_delta(line)

                if (!in_logo && line ~ /^[[:space:]]*AppLogo[[:space:]]*\{/) {
                    in_logo = 1
                    depth = 0
                }

                if (in_logo) {
                    if (line ~ /(visible|opacity|x|width|Layout\.preferredWidth|anchors\.leftMargin|anchors\.horizontalCenterOffset)[[:space:]]*:.*sidebar(Hidden|Width)/) {
                        print NR ":" line
                    }
                    depth += delta
                    if (depth <= 0)
                        in_logo = 0
                }
            }
        ' "$file"
    } | awk '!seen[$0]++'
}

detect_toolbar_page_title_hits() {
    local file="$1"
    if grep -qE 'D\.WindowButtonGroup|D\.ThemeMenu|ThemeMenu|WindowButtonGroup' "$file"; then
        grep -nE 'text[[:space:]]*:[[:space:]]*(currentItem\.title|currentPageTitle|pageTitle|headerTitle|currentTitle|AppStore\.[A-Za-z0-9_]*title|AppStore\.navigationItems.*title)' "$file" || true
    fi
}

detect_sidebar_gap_hits() {
    local file="$1"
    grep -nE 'anchors\.left[[:space:]]*:[[:space:]]*(sidebarResizeHandle|sidebarSplitter|splitter|divider|separator)[A-Za-z0-9_]*\.right' "$file" || true
}

file_has_sidebar_edge_divider() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_rect = 0
            depth = 0
            has_right = 0
            has_width = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_rect && line ~ /^[[:space:]]*Rectangle[[:space:]]*\{/) {
                in_rect = 1
                depth = 0
                has_right = 0
                has_width = 0
            }

            if (in_rect) {
                if (depth == 1 && line ~ /anchors\.right[[:space:]]*:[[:space:]]*parent\.right/)
                    has_right = 1
                if (depth == 1 && line ~ /^[[:space:]]*width[[:space:]]*:[[:space:]]*1([[:space:]]*(\/\/.*)?$)/)
                    has_width = 1

                depth += delta
                if (depth <= 0) {
                    if (has_right && has_width) {
                        print "yes"
                        exit
                    }
                    in_rect = 0
                }
            }
        }
    ' "$file"
}

detect_single_group_sidebar_header_hits() {
    local file="$1"
    if grep -q 'ListView' "$file" \
        && ! grep -qE 'navigationGroups|groupModel|section\.delegate|section\.property|groupTitle|groupHeader|groupSpacing' "$file"
    then
        grep -nE 'text[[:space:]]*:[[:space:]]*"(应用导航|导航|分组|常用|全部)"' "$file" || true
    fi
}

detect_sidebar_group_spacing_hits() {
    local file="$1"
    if grep -qE 'navigationGroups|groupModel|section\.delegate|groupTitle|groupHeader|groupSpacing' "$file" \
        && ! grep -qE 'spacing[[:space:]]*:[[:space:]].*(20|Theme\.spacingL)([^A-Za-z0-9_]|$)' "$file"
    then
        printf '1: multi-group sidebar is missing the required 20px inter-group spacing\n'
    fi
}

detect_top_operational_banner_hits() {
    local file="$1"
    if [[ "$(file_has_root_application_window "$file")" != "yes" ]]; then
        return
    fi

    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_block() {
            in_block = 0
            depth = 0
            start = 0
            has_visible_gate = 0
            has_top_band_shape = 0
            has_operational_copy = 0
        }

        BEGIN {
            reset_block()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line ~ /^[[:space:]]*(Rectangle|Item|Row|Column|RowLayout|ColumnLayout)[[:space:]]*\{/) {
                in_block = 1
                depth = 0
                start = NR
                has_visible_gate = 0
                has_top_band_shape = 0
                has_operational_copy = 0
            }

            if (in_block) {
                if (line ~ /(anchors\.top|Layout\.preferredHeight|Layout\.minimumHeight|Layout\.fillWidth[[:space:]]*:[[:space:]]*true|height[[:space:]]*:)/)
                    has_top_band_shape = 1
                if (line ~ /visible[[:space:]]*:[[:space:]].*(restrictedMode|adminMode|unlock|paywall|subscribe|service|付费|订阅|会员|权益|受限|提权)/)
                    has_visible_gate = 1
                if (line ~ /text[[:space:]]*:[[:space:]]*".*(受限模式|提权|解锁|付费|订阅|会员|权益|服务|管理员权限|完整能力|升级).*"/)
                    has_operational_copy = 1

                depth += delta
                if (depth <= 0) {
                    if (has_visible_gate && has_top_band_shape && has_operational_copy)
                        printf "%s: top-of-app operational prompt should move into the sidebar operational-card area\n", start
                    reset_block()
                }
            }
        }
    ' "$file"
}

detect_large_title_weight_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_label() {
            in_label = 0
            depth = 0
            start = 0
            is_large = 0
            is_heavy = 0
            looks_numeric = 0
        }

        BEGIN {
            reset_label()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_label && line ~ /^[[:space:]]*(D\.)?(Label|Text)[[:space:]]*\{/) {
                in_label = 1
                depth = 0
                start = NR
                is_large = 0
                is_heavy = 0
                looks_numeric = 0
            }

            if (in_label) {
                if (depth == 1 && line ~ /^[[:space:]]*text[[:space:]]*:/) {
                    if (line ~ /[%分]|MB|GB|KB|TB|Mbps|Kbps|Gbps|ms|MHz|GHz|分值|得分|[0-9]/)
                        looks_numeric = 1
                }

                if (depth == 1 && line ~ /^[[:space:]]*font\.pixelSize[[:space:]]*:/) {
                    if (line ~ /Theme\.(sectionTitleSize|titleSize|headingSize)/) {
                        is_large = 1
                    } else if (line ~ /[0-9]+/) {
                        value = line
                        sub(/.*:[[:space:]]*/, "", value)
                        gsub(/[^0-9]/, "", value)
                        if ((value + 0) > 16)
                            is_large = 1
                    }
                }

                if (depth == 1 && line ~ /^[[:space:]]*font\.bold[[:space:]]*:[[:space:]]*true/)
                    is_heavy = 1

                if (depth == 1 && line ~ /^[[:space:]]*font\.weight[[:space:]]*:/) {
                    if (line !~ /(Font\.Normal|Font\.Light|Font\.ExtraLight|Font\.Thin|400([^0-9]|$))/)
                        is_heavy = 1
                }

                depth += delta
                if (depth <= 0) {
                    if (is_large && is_heavy && !looks_numeric)
                        printf "%s: large title label exceeds the 400-weight baseline\n", start
                    reset_label()
                }
            }
        }
    ' "$file"
}

detect_large_unit_label_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_label() {
            in_label = 0
            depth = 0
            start = 0
            is_large = 0
            has_unit = 0
        }

        BEGIN {
            reset_label()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_label && line ~ /^[[:space:]]*(D\.)?(Label|Text)[[:space:]]*\{/) {
                in_label = 1
                depth = 0
                start = NR
                is_large = 0
                has_unit = 0
            }

            if (in_label) {
                if (depth == 1 && line ~ /^[[:space:]]*text[[:space:]]*:/) {
                    expr = line
                    sub(/^[^:]*:[[:space:]]*/, "", expr)
                    if (expr ~ /^"[-+0-9.]+[[:space:]]*(%|分|MB|GB|KB|TB|Mbps|Kbps|Gbps|ms|MHz|GHz)/ \
                        || expr ~ /^(Math\.[A-Za-z0-9_.()[:space:]]+|[A-Za-z_][A-Za-z0-9_.()[:space:]]*)[[:space:]]*\+[[:space:]]*"(%|分|MB|GB|KB|TB|Mbps|Kbps|Gbps|ms|MHz|GHz)/)
                    {
                        has_unit = 1
                    }
                }

                if (depth == 1 && line ~ /^[[:space:]]*font\.pixelSize[[:space:]]*:/) {
                    if (line ~ /Theme\.(sectionTitleSize|titleSize|headingSize)/) {
                        is_large = 1
                    } else if (line ~ /[0-9]+/) {
                        value = line
                        sub(/.*:[[:space:]]*/, "", value)
                        gsub(/[^0-9]/, "", value)
                        if ((value + 0) > 16)
                            is_large = 1
                    }
                }

                depth += delta
                if (depth <= 0) {
                    if (is_large && has_unit)
                        printf "%s: large numeric label still renders units as part of one full-size text run\n", start
                    reset_label()
                }
            }
        }
    ' "$file"
}

detect_page_header_icon_hits() {
    local file="$1"
    case "$(basename "$file")" in
        PageHeader.qml)
            {
                grep -nE 'property[[:space:]]+(url|string)[[:space:]]+icon(Source|Name)' "$file" || true
                grep -nE 'SvgIcon[[:space:]]*\{' "$file" || true
            } | awk '!seen[$0]++'
            ;;
        *)
            awk '
                function brace_delta(s,   tmp, opens, closes) {
                    tmp = s
                    opens = gsub(/\{/, "{", tmp)
                    closes = gsub(/\}/, "}", tmp)
                    return opens - closes
                }

                BEGIN {
                    in_header = 0
                    depth = 0
                    start = 0
                    has_icon = 0
                }

                {
                    line = $0
                    delta = brace_delta(line)

                    if (!in_header && line ~ /^[[:space:]]*PageHeader[[:space:]]*\{/) {
                        in_header = 1
                        depth = 0
                        start = NR
                        has_icon = 0
                    }

                    if (in_header) {
                        if (depth == 1 && line ~ /^[[:space:]]*icon(Source|Name)[[:space:]]*:/)
                            has_icon = 1

                        depth += delta
                        if (depth <= 0) {
                            if (has_icon)
                                printf "%s: PageHeader still declares a leading icon\n", start
                            in_header = 0
                        }
                    }
                }
            ' "$file"
            ;;
    esac
}

detect_gradient_card_whitespace_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_card = 0
            card_depth = 0
            card_start = 0
            card_has_gradient = 0
            card_padding_zero = 0
            in_rect = 0
            rect_depth = 0
            rect_start = 0
            rect_has_gradient = 0
            rect_has_margin = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_card && line ~ /^[[:space:]]*SectionCard[[:space:]]*\{/) {
                in_card = 1
                card_depth = 0
                card_start = NR
                card_has_gradient = 0
                card_padding_zero = 0
            }

            if (in_card) {
                if (card_depth == 1 && line ~ /^[[:space:]]*padding[[:space:]]*:[[:space:]]*0([[:space:]]*(\/\/.*)?$)/)
                    card_padding_zero = 1

                if (!in_rect && line ~ /^[[:space:]]*Rectangle[[:space:]]*\{/) {
                    in_rect = 1
                    rect_depth = 0
                    rect_start = NR
                    rect_has_gradient = 0
                    rect_has_margin = 0
                }

                if (in_rect) {
                    if (line ~ /gradient[[:space:]]*:[[:space:]]*Gradient/)
                        rect_has_gradient = 1
                    if (rect_depth >= 1 && line ~ /anchors\.(margins|leftMargin|rightMargin|topMargin|bottomMargin)[[:space:]]*:[[:space:]]*[1-9][0-9]*/)
                        rect_has_margin = 1

                    rect_depth += delta
                    if (rect_depth <= 0) {
                        if (rect_has_gradient && rect_has_margin)
                            printf "%s: gradient background keeps inset margins and leaves visible whitespace around the card edge\n", rect_start
                        if (rect_has_gradient)
                            card_has_gradient = 1
                        in_rect = 0
                    }
                }

                card_depth += delta
                if (card_depth <= 0) {
                    if (card_has_gradient && !card_padding_zero)
                        printf "%s: SectionCard with a live gradient must set padding to 0\n", card_start
                    in_card = 0
                }
            }
        }
    ' "$file"
}

detect_status_duplication_hits() {
    local file="$1"
    if ! grep -q 'StatusBadge' "$file"; then
        return
    fi

    {
        grep -nE 'label[[:space:]]*:[[:space:]]*"状态"' "$file" || true
        grep -nE 'text[[:space:]]*:[[:space:]]*"当前状态[^"]*"' "$file" || true
    } | awk '!seen[$0]++'
}

detect_option_row_icon_hits() {
    local file="$1"
    case "$(basename "$file")" in
        SettingsOptionRow.qml)
            awk '
                /^[[:space:]]*property[[:space:]]+url[[:space:]]+iconSource[[:space:]]*:/ {
                    if ($0 !~ /""[[:space:]]*$/)
                        printf "%s: SettingsOptionRow must not define a non-empty default iconSource\n", NR
                }
            ' "$file"
            ;;
        *SettingsDialog.qml)
            awk '
                function brace_delta(s,   tmp, opens, closes) {
                    tmp = s
                    opens = gsub(/\{/, "{", tmp)
                    closes = gsub(/\}/, "}", tmp)
                    return opens - closes
                }

                BEGIN {
                    in_row = 0
                    depth = 0
                    start = 0
                    has_icon = 0
                }

                {
                    line = $0
                    delta = brace_delta(line)

                    if (!in_row && line ~ /^[[:space:]]*SettingsOptionRow[[:space:]]*\{/) {
                        in_row = 1
                        depth = 0
                        start = NR
                        has_icon = 0
                    }

                    if (in_row) {
                        if (depth == 1 && line ~ /^[[:space:]]*iconSource[[:space:]]*:/ && line !~ /""[[:space:]]*$/)
                            has_icon = 1

                        depth += delta
                        if (depth <= 0) {
                            if (!has_icon)
                                printf "%s: SettingsOptionRow is missing an explicit per-item iconSource\n", start
                            in_row = 0
                        }
                    }
                }
            ' "$file"
            ;;
    esac
}

detect_repeated_functional_row_icon_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_repeat = 0
            repeat_depth = 0
            repeat_has_model = 0
            in_row = 0
            row_depth = 0
            row_icon_line = ""
            in_leading = 0
            leading_depth = 0
            leading_icon_line = ""
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_repeat && line ~ /^[[:space:]]*(Repeater|ListView|GridView|PathView)[[:space:]]*\{/) {
                in_repeat = 1
                repeat_depth = 0
                repeat_has_model = 0
                in_row = 0
            }

            if (in_repeat) {
                if (repeat_depth == 1 && line ~ /^[[:space:]]*model[[:space:]]*:/)
                    repeat_has_model = 1

                if (!in_row && line ~ /^[[:space:]]*(SettingRow|SettingsOptionRow)[[:space:]]*\{/) {
                    in_row = 1
                    row_depth = 0
                    row_icon_line = ""
                    in_leading = 0
                    leading_depth = 0
                    leading_icon_line = ""
                }

                if (in_row) {
                    if (row_depth == 1 && line ~ /^[[:space:]]*iconSource[[:space:]]*:[[:space:]]*"qrc:[^"]+"/)
                        row_icon_line = NR ":" line

                    if (!in_leading && line ~ /^[[:space:]]*leading[[:space:]]*:[[:space:]]*Component[[:space:]]*\{/) {
                        in_leading = 1
                        leading_depth = 0
                        leading_icon_line = ""
                    }

                    if (in_leading) {
                        if (line ~ /^[[:space:]]*source[[:space:]]*:[[:space:]]*"qrc:[^"]+"/)
                            leading_icon_line = NR ":" line

                        leading_depth += delta
                        if (leading_depth <= 0)
                            in_leading = 0
                    }

                    row_depth += delta
                    if (row_depth <= 0) {
                        if (repeat_has_model && row_icon_line != "")
                            print row_icon_line " (repeated functional rows must bind icon identity from item data or a resolver, not one constant asset)"
                        if (repeat_has_model && leading_icon_line != "")
                            print leading_icon_line " (repeated functional rows must bind icon identity from item data or a resolver, not one constant asset)"
                        in_row = 0
                    }
                }

                repeat_depth += delta
                if (repeat_depth <= 0)
                    in_repeat = 0
            }
        }
    ' "$file"
}

detect_unified_toolbar_height_hits() {
    local file="$1"
    if ! grep -q 'WindowButtonGroup' "$file"; then
        return
    fi

    awk '
        /^[[:space:]]*(readonly[[:space:]]+)?property[[:space:]]+int[[:space:]]+chromeHeight[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/ {
            value = $0
            sub(/.*chromeHeight[[:space:]]*:[[:space:]]*/, "", value)
            gsub(/[^0-9]/, "", value)
            if ((value + 0) != 50)
                printf "%s: unified toolbar chromeHeight %d must be 50\n", NR, value + 0
        }
    ' "$file"

    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_block = 0
            depth = 0
            start = 0
            has_window_buttons = 0
            height_value = -1
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line ~ /^[[:space:]]*(Rectangle|Item|RowLayout|ColumnLayout)[[:space:]]*\{/) {
                in_block = 1
                depth = 0
                start = NR
                has_window_buttons = 0
                height_value = -1
            }

            if (in_block) {
                if (line ~ /WindowButtonGroup/)
                    has_window_buttons = 1

                if (depth == 1 && line ~ /^[[:space:]]*(height|implicitHeight|Layout\.preferredHeight)[[:space:]]*:[[:space:]]*[0-9]+([[:space:]]*(\/\/.*)?$)/) {
                    value = line
                    sub(/.*:[[:space:]]*/, "", value)
                    gsub(/[^0-9]/, "", value)
                    height_value = value + 0
                }

                depth += delta
                if (depth <= 0) {
                    if (has_window_buttons && height_value > 0 && height_value != 50)
                        printf "%s: unified toolbar height %d must be 50\n", start, height_value
                    in_block = 0
                }
            }
        }
    ' "$file"
}

detect_unified_toolbar_divider_hits() {
    local file="$1"
    if ! grep -q 'WindowButtonGroup' "$file"; then
        return
    fi

    {
        grep -nE 'titlebarDivider' "$file" || true
        awk '
            function brace_delta(s,   tmp, opens, closes) {
                tmp = s
                opens = gsub(/\{/, "{", tmp)
                closes = gsub(/\}/, "}", tmp)
                return opens - closes
            }

            BEGIN {
                in_rect = 0
                depth = 0
                start = 0
                has_height = 0
                has_color = 0
            }

            {
                line = $0
                delta = brace_delta(line)

                if (!in_rect && line ~ /^[[:space:]]*Rectangle[[:space:]]*\{/) {
                    in_rect = 1
                    depth = 0
                    start = NR
                    has_height = 0
                    has_color = 0
                }

                if (in_rect) {
                    if (depth == 1 && line ~ /^[[:space:]]*(height|Layout\.preferredHeight)[[:space:]]*:[[:space:]]*1([[:space:]]*(\/\/.*)?$)/)
                        has_height = 1
                    if (depth == 1 && line ~ /^[[:space:]]*color[[:space:]]*:[[:space:]]*Theme\.(divider|titlebarDivider)([^A-Za-z0-9_]|$)/)
                        has_color = 1

                    depth += delta
                    if (depth <= 0) {
                        if (has_height && has_color)
                            printf "%s: unified toolbar must not add an extra divider line\n", start
                        in_rect = 0
                    }
                }
            }
        ' "$file"
    } | awk '!seen[$0]++'
}

detect_search_placeholder_inactive_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_search = 0
            depth = 0
            start = 0
            bad_placeholder = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_search && line ~ /^[[:space:]]*D\.SearchEdit[[:space:]]*\{/) {
                in_search = 1
                depth = 0
                start = NR
                bad_placeholder = 0
            }

            if (in_search) {
                if (depth == 1 && line ~ /^[[:space:]]*placeholderText[[:space:]]*:/ && line !~ /activeFocus|focus|whenActive|whenFocused|\?/) {
                    bad_placeholder = 1
                }

                depth += delta
                if (depth <= 0) {
                    if (bad_placeholder)
                        printf "%s: SearchEdit keeps placeholder hints visible while inactive\n", start
                    in_search = 0
                }
            }
        }
    ' "$file"
}

detect_search_filter_ratio_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_block() {
            in_block = 0
            depth = 0
            block_type = ""
            block_start = 0
            search_fill = 0
            search_dominant = 0
            filter_constrained = 0
        }

        function finish_block() {
            if (block_type == "search") {
                saw_search = 1
                if (search_fill)
                    search_fill_seen = 1
                if (search_dominant)
                    search_dominant_seen = 1
            } else if (block_type == "filter") {
                saw_filter = 1
                if (filter_constrained)
                    filter_constrained_seen = 1
            }
            reset_block()
        }

        BEGIN {
            reset_block()
            saw_search = 0
            saw_filter = 0
            search_fill_seen = 0
            search_dominant_seen = 0
            filter_constrained_seen = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_block && line ~ /^[[:space:]]*D\.(SearchEdit|ComboBox)[[:space:]]*\{/) {
                in_block = 1
                depth = 0
                block_start = NR
                block_type = (line ~ /SearchEdit/) ? "search" : "filter"
                search_fill = 0
                search_dominant = 0
                filter_constrained = 0
            }

            if (in_block) {
                if (depth == 1 && block_type == "search") {
                    if (line ~ /Layout\.fillWidth[[:space:]]*:[[:space:]]*true/)
                        search_fill = 1
                    if (line ~ /Layout\.columnSpan[[:space:]]*:[[:space:]]*[2-9]/ \
                        || line ~ /Layout\.horizontalStretchFactor[[:space:]]*:[[:space:]]*[2-9]/ \
                        || line ~ /Layout\.preferredWidth[[:space:]]*:[[:space:]]*[2-9][0-9]{2,}/ \
                        || line ~ /Layout\.minimumWidth[[:space:]]*:[[:space:]]*[2-9][0-9]{2,}/)
                    {
                        search_dominant = 1
                    }
                }

                if (depth == 1 && block_type == "filter") {
                    if (line ~ /(Layout\.)?(preferredWidth|maximumWidth|minimumWidth|implicitWidth)[[:space:]]*:/)
                        filter_constrained = 1
                }

                depth += delta
                if (depth <= 0)
                    finish_block()
            }
        }

        END {
            if (saw_search && saw_filter && !(search_dominant_seen || (search_fill_seen && filter_constrained_seen))) {
                print "1: search-and-filter band does not give the search control a clearly larger share than the filters"
            }
        }
    ' "$file"
}

detect_compact_list_text_hits() {
    local file="$1"
    local scan_all=0
    case "$(basename "$file")" in
        *Row*.qml|*Item*.qml|*List*.qml|*Card*.qml)
            scan_all=1
            ;;
        *)
            if ! grep -qE '^[[:space:]]*(Repeater|ListView|GridView|PathView)[[:space:]]*\{|^[[:space:]]*delegate[[:space:]]*:[[:space:]].*\{' "$file"; then
                return
            fi
        ;;
    esac

    awk -v scan_all="$scan_all" '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_label() {
            in_label = 0
            depth = 0
            start = 0
            wrapped = 0
            capped = 0
        }

        BEGIN {
            reset_label()
            in_repeat = 0
            repeat_depth = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!scan_all && !in_repeat && line ~ /^[[:space:]]*(Repeater|ListView|GridView|PathView)[[:space:]]*\{/) {
                in_repeat = 1
                repeat_depth = 0
            }

            if (!scan_all && !in_repeat && line ~ /^[[:space:]]*delegate[[:space:]]*:[[:space:]].*\{/) {
                in_repeat = 1
                repeat_depth = 0
            }

            if ((scan_all || in_repeat) && !in_label && line ~ /^[[:space:]]*(D\.)?(Label|Text)[[:space:]]*\{/) {
                in_label = 1
                depth = 0
                start = NR
                wrapped = 0
                capped = 0
            }

            if (in_label) {
                if (depth == 1 && line ~ /wrapMode[[:space:]]*:[[:space:]]*Text\.(WordWrap|WrapAnywhere)/)
                    wrapped = 1
                if (depth == 1 && (line ~ /maximumLineCount[[:space:]]*:[[:space:]]*[12]/ || line ~ /elide[[:space:]]*:[[:space:]]*Text\./))
                    capped = 1

                depth += delta
                if (depth <= 0) {
                    if (wrapped && !capped)
                        printf "%s: variable-length file/app/data/reusable list text should stay on a compact 1-2 line baseline\n", start
                    reset_label()
                }
            }

            if (!scan_all && in_repeat) {
                repeat_depth += delta
                if (repeat_depth <= 0)
                    in_repeat = 0
            }
        }
    ' "$file"
}

detect_placeholder_list_icon_hits() {
    local file="$1"
    case "$(basename "$file")" in
        AppStore.qml)
            awk '
                BEGIN { in_items = 0 }
                /property var softwareItems:[[:space:]]*\[/ { in_items = 1 }
                in_items && /\][[:space:]]*$/ { in_items = 0 }
                in_items && /iconSource[[:space:]]*:[[:space:]]*"qrc:\/qml\/assets\/icons\/(apps|package|hard-drive|file|document)\.svg"/ { print NR ":" $0 }
            ' "$file"
            ;;
        *Software*.qml|*File*.qml)
            awk '
                function brace_delta(s,   tmp, opens, closes) {
                    tmp = s
                    opens = gsub(/\{/, "{", tmp)
                    closes = gsub(/\}/, "}", tmp)
                    return opens - closes
                }

                BEGIN {
                    in_repeat = 0
                    depth = 0
                }

                {
                    line = $0
                    delta = brace_delta(line)

                    if (!in_repeat && line ~ /(Repeater|delegate)[^A-Za-z0-9_]*\{/) {
                        in_repeat = 1
                        depth = 0
                    }

                    if (in_repeat) {
                        if (line ~ /(iconSource|source)[[:space:]]*:[[:space:]]*"qrc:\/qml\/assets\/icons\/(apps|package|hard-drive|file|document)\.svg"/)
                            print NR ":" line

                        depth += delta
                        if (depth <= 0)
                            in_repeat = 0
                    }
                }
            ' "$file"
            ;;
    esac
}

detect_shared_functional_model_icon_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function extract_string(s,   value) {
            value = s
            sub(/^[^"]*"/, "", value)
            sub(/".*$/, "", value)
            return value
        }

        function flush_element() {
            if (elem_has_description && elem_icon != "" && elem_id != "") {
                if (!(elem_icon in seen_icon_id)) {
                    seen_icon_id[elem_icon] = elem_id
                } else if (seen_icon_id[elem_icon] != elem_id) {
                    printf "%s: distinct functional list items reuse bundled icon %s; keep per-item icon identity\n", elem_icon_line, elem_icon
                }
            }

            in_element = 0
            element_depth = 0
            elem_id = ""
            elem_icon = ""
            elem_icon_line = 0
            elem_has_description = 0
        }

        BEGIN {
            in_model = 0
            model_depth = 0
            in_element = 0
            element_depth = 0
            elem_id = ""
            elem_icon = ""
            elem_icon_line = 0
            elem_has_description = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_model && line ~ /^[[:space:]]*ListModel[[:space:]]*\{/) {
                in_model = 1
                model_depth = 0
                delete seen_icon_id
                in_element = 0
            }

            if (in_model) {
                if (!in_element && line ~ /^[[:space:]]*ListElement[[:space:]]*\{/) {
                    in_element = 1
                    element_depth = 0
                    elem_id = ""
                    elem_icon = ""
                    elem_icon_line = 0
                    elem_has_description = 0
                }

                if (in_element) {
                    if (element_depth == 1 && elem_id == "" && line ~ /^[[:space:]]*key[[:space:]]*:[[:space:]]*"/)
                        elem_id = extract_string(line)
                    if (element_depth == 1 && elem_id == "" && line ~ /^[[:space:]]*title[[:space:]]*:[[:space:]]*"/)
                        elem_id = extract_string(line)
                    if (element_depth == 1 && line ~ /^[[:space:]]*description[[:space:]]*:[[:space:]]*"/)
                        elem_has_description = 1
                    if (element_depth == 1 && line ~ /^[[:space:]]*iconSource[[:space:]]*:[[:space:]]*"qrc:[^"]+"/) {
                        elem_icon = extract_string(line)
                        elem_icon_line = NR
                    }

                    element_depth += delta
                    if (element_depth <= 0)
                        flush_element()
                }

                model_depth += delta
                if (model_depth <= 0)
                    in_model = 0
            }
        }
    ' "$file"
}

detect_list_height_cap_hits() {
    local file="$1"
    grep -nE '(height|Layout\.preferredHeight)[[:space:]]*:[[:space:]]*Math\.min\(contentHeight[[:space:]]*,' "$file" || true
}

detect_chart_missing_axes_hits() {
    local file="$1"
    if [[ "$(basename "$file")" == *Chart*.qml ]] || ( grep -q 'Canvas' "$file" && grep -qE 'cpuSeries|memorySeries|drawSeries|chart' "$file" ); then
        if ! grep -qE 'xLabels|yTicks|axis|tick|刻度|seconds|timeLabels|usageLabel' "$file"; then
            printf '1: chart surface lacks explicit axis labels or tick metadata\n'
        fi
    fi
}

detect_chart_missing_animation_hits() {
    local file="$1"
    if [[ "$(basename "$file")" == *Chart*.qml ]] || ( grep -q 'Canvas' "$file" && grep -qE 'cpuSeries|memorySeries|drawSeries|chart' "$file" ); then
        if ! grep -qE 'Behavior on|NumberAnimation|SmoothedAnimation|SequentialAnimation|ParallelAnimation|revealProgress|animated' "$file"; then
            printf '1: chart surface lacks animated data transitions\n'
        fi
    fi
}

detect_chart_curve_style_hits() {
    local file="$1"
    if [[ "$(basename "$file")" == *Chart*.qml ]] || ( grep -q 'Canvas' "$file" && grep -qE 'cpuSeries|memorySeries|drawSeries|chart' "$file" ); then
        if grep -qE 'drawSeries|ctx\.lineTo|lineTo\(' "$file"; then
            if ! grep -q 'createLinearGradient' "$file"; then
                printf '1: chart curve lacks a top-to-bottom gradient treatment\n'
            fi

            if ! grep -qE 'ctx\.shadowColor|shadowColor|ctx\.shadowBlur|shadowBlur' "$file"; then
                printf '1: chart curve lacks a same-color shadow treatment\n'
            fi

            if ! grep -qE 'Qt\.rgba\(tone\.r|tone\.r,[[:space:]]*tone\.g,[[:space:]]*tone\.b|function[[:space:]]+toneWithAlpha' "$file"; then
                printf '1: chart curve styling does not appear to derive gradient and shadow from the line color\n'
            fi
        fi
    fi
}

detect_progress_shadow_hits() {
    local file="$1"
    local base
    local has_custom_progress=0
    base="$(basename "$file")"

    if [[ "$base" != *Progress*.qml ]] \
        && [[ "$base" != *Score*.qml ]] \
        && [[ "$base" != *Gauge*.qml ]] \
        && ! grep -qE 'CircularProgress|LinearProgress|RingProgress|ProgressRing|ProgressArc|CircularScore|ringCanvas|gauge' "$file"
    then
        return
    fi

    if grep -qE 'Canvas|Shape|ShapePath|ctx\.arc|ctx\.lineTo' "$file"; then
        has_custom_progress=1
    elif [[ "$base" == *Progress*.qml ]] \
        && grep -q 'Rectangle[[:space:]]*{' "$file" \
        && grep -qE 'property[[:space:]]+(real|int)[[:space:]]+(value|progress)' "$file"
    then
        has_custom_progress=1
    fi

    if (( ! has_custom_progress )); then
        return
    fi

    if grep -qE '(^|[[:space:]])D\.ProgressBar([[:space:]]|\{)' "$file" \
        && ! grep -qE 'Canvas|Shape|ShapePath|ctx\.arc|ctx\.lineTo|layer\.effect|DropShadow|MultiEffect' "$file"
    then
        return
    fi

    if ! grep -qE 'drawSeries|cpuSeries|memorySeries|xLabels|yTicks|chartCanvas' "$file" \
        && ! grep -qE 'DropShadow|MultiEffect|layer\.effect|ctx\.shadowColor|shadowColor|shadow\.color|foregroundShadow' "$file"
    then
        printf '1: custom progress foreground lacks a same-color shadow treatment\n'
    fi
}

detect_ring_progress_style_hits() {
    local file="$1"
    local base
    base="$(basename "$file")"

    if [[ "$base" != *Progress*.qml ]] \
        && [[ "$base" != *Score*.qml ]] \
        && [[ "$base" != *Gauge*.qml ]] \
        && ! grep -qE 'CircularScore|RingProgress|ProgressRing|ProgressArc|ctx\.arc|gauge' "$file"
    then
        return
    fi

    if ! grep -qE 'ctx\.arc|ShapePath' "$file"; then
        return
    fi

    if grep -q 'showCenterText' "$file"; then
        if grep -q 'ctx\.lineWidth[[:space:]]*=[[:space:]]*root\.lineWidth' "$file"; then
            printf '1: ring progress does not hard-cap no-text stroke thickness before painting\n'
        elif ! grep -qE 'effectiveLineWidth|Math\.min\([^)]*20' "$file"; then
            printf '1: ring progress is missing an explicit no-text 20px stroke cap\n'
        fi
    fi

    if ! grep -qE 'safeStrokeInset|shadowInset|clipMargin' "$file" \
        || ! grep -qE 'radius[[:space:]]*=.*(safeStrokeInset|shadowInset|clipMargin)' "$file"
    then
        printf '1: ring progress shadow may clip because no safe inset is reserved in the radius calculation\n'
    fi

    if grep -qE 'foregroundShadowColor.*0\.(2[0-9]|[3-9][0-9])|shadowColor[[:space:]]*=.*0\.(2[0-9]|[3-9][0-9])' "$file"; then
        printf '1: ring progress shadow is heavier than the light-shadow baseline\n'
    fi
}

detect_custom_main_menu_icon_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_button = 0
            depth = 0
            start = 0
            is_main_menu = 0
            has_custom_icon = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_button && line ~ /^[[:space:]]*((D\.)?(ToolButton|Button)|QQC\.Button)[[:space:]]*\{/) {
                in_button = 1
                depth = 0
                start = NR
                is_main_menu = 0
                has_custom_icon = 0
            }

            if (in_button) {
                if (depth == 1 && (line ~ /id[[:space:]]*:[[:space:]]*mainMenuButton/ || line ~ /text[[:space:]]*:[[:space:]]*"主菜单"/))
                    is_main_menu = 1
                if (depth == 1 && (line ~ /icon\.source[[:space:]]*:/ || line ~ /SvgIcon[[:space:]]*\{/))
                    has_custom_icon = 1

                depth += delta
                if (depth <= 0) {
                    if (is_main_menu && has_custom_icon)
                        printf "%s: main-menu trigger still uses a custom project icon path or custom icon item\n", start
                    in_button = 0
                }
            }
        }
    ' "$file"
}

detect_main_menu_without_titlebar_hits() {
    local file="$1"
    if [[ "$(file_has_root_application_window "$file")" != "yes" ]]; then
        return
    fi

    if ! grep -qE '(^|[[:space:]])D\.TitleBar([[:space:]]|\{)' "$file"; then
        if grep -qE 'ThemeMenu|AboutAction|HelpAction|QuitAction|text[[:space:]]*:[[:space:]]*"(设置|关于|退出|主菜单|更多|跟随系统主题|浅色模式|深色模式)"' "$file"; then
            printf '1: application main menu exists but the window does not use D.TitleBar.menu\n'
        fi
        return
    fi

    if ! grep -qE 'D\.TitleBar[[:space:]]*\{[[:space:][:print:]]*menu[[:space:]]*:' "$file" \
        && ! grep -qE '^[[:space:]]*menu[[:space:]]*:' "$file"
    then
        if grep -qE 'ThemeMenu|AboutAction|HelpAction|QuitAction|text[[:space:]]*:[[:space:]]*"(设置|关于|退出|主菜单|更多|跟随系统主题|浅色模式|深色模式)"' "$file"; then
            printf '1: application main menu exists but is not attached through D.TitleBar.menu\n'
        fi
    fi
}

detect_titlebar_menu_attachment_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_titlebar = 0
            depth = 0
            start = 0
            has_menu_property = 0
            has_menu_content = 0
            has_custom_trigger = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_titlebar && line ~ /^[[:space:]]*D\.TitleBar[[:space:]]*\{/) {
                in_titlebar = 1
                depth = 0
                start = NR
                has_menu_property = 0
                has_menu_content = 0
                has_custom_trigger = 0
            }

            if (in_titlebar) {
                if (depth == 1 && line ~ /^[[:space:]]*menu[[:space:]]*:/)
                    has_menu_property = 1
                if (line ~ /D\.(ThemeMenu|AboutAction|HelpAction|QuitAction)[[:space:]]*\{/ \
                    || line ~ /text[[:space:]]*:[[:space:]]*"(设置|关于|退出|主菜单|更多)"/)
                    has_menu_content = 1
                if (line ~ /id[[:space:]]*:[[:space:]]*mainMenuButton/ \
                    || line ~ /text[[:space:]]*:[[:space:]]*"(主菜单|更多)"/ \
                    || line ~ /icon\.(name|source)[[:space:]]*:[[:space:]]*".*(open-menu|menu|hamburger).*"/)
                    has_custom_trigger = 1

                depth += delta
                if (depth <= 0) {
                    if ((has_menu_content || has_custom_trigger) && !has_menu_property)
                        printf "%s: D.TitleBar path exposes an application main menu but does not attach it through TitleBar.menu\n", start
                    in_titlebar = 0
                }
            }
        }
    ' "$file"
}

detect_full_width_titlebar_sidebar_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            root_seen = 0
            root_depth = 0
            in_titlebar = 0
            titlebar_depth = 0
            titlebar_start = 0
            titlebar_level = 0
            titlebar_has_fill = 0
            titlebar_has_left_parent = 0
            titlebar_has_right_parent = 0
            titlebar_has_x = 0
            titlebar_has_width = 0
            titlebar_is_full_width = 0
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!root_seen && line ~ /^[[:space:]]*((D\.)?ApplicationWindow|Window)[[:space:]]*\{/) {
                root_seen = 1
                root_depth = 0
            }

            if (root_seen) {
                if (!in_titlebar && line ~ /^[[:space:]]*D\.TitleBar[[:space:]]*\{/) {
                    in_titlebar = 1
                    titlebar_depth = 0
                    titlebar_start = NR
                    titlebar_level = root_depth
                    titlebar_has_fill = 0
                    titlebar_has_left_parent = 0
                    titlebar_has_right_parent = 0
                    titlebar_has_x = 0
                    titlebar_has_width = 0
                    titlebar_is_full_width = 0
                }

                if (in_titlebar) {
                    if (titlebar_depth == 1 && line ~ /anchors\.fill[[:space:]]*:[[:space:]]*parent/)
                        titlebar_has_fill = 1
                    if (titlebar_depth == 1 && line ~ /anchors\.left[[:space:]]*:[[:space:]]*parent\.left/)
                        titlebar_has_left_parent = 1
                    if (titlebar_depth == 1 && line ~ /anchors\.right[[:space:]]*:[[:space:]]*parent\.right/)
                        titlebar_has_right_parent = 1
                    if (titlebar_depth == 1 && line ~ /^[[:space:]]*x[[:space:]]*:/)
                        titlebar_has_x = 1
                    if (titlebar_depth == 1 && line ~ /^[[:space:]]*width[[:space:]]*:/)
                        titlebar_has_width = 1

                    titlebar_depth += delta
                    if (titlebar_depth <= 0) {
                        titlebar_is_full_width = titlebar_has_fill
                        if (!titlebar_is_full_width && titlebar_has_left_parent && titlebar_has_right_parent && !titlebar_has_x && !titlebar_has_width)
                            titlebar_is_full_width = 1

                        if (titlebar_level <= 2 && titlebar_is_full_width)
                            printf "%s: persistent-left-sidebar apps must not use a top-level full-width D.TitleBar as the primary outer shell\n", titlebar_start
                        in_titlebar = 0
                    }
                }

                root_depth += delta
            }
        }
    ' "$file"
}

detect_titlebar_custom_main_menu_trigger_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_button() {
            in_button = 0
            button_depth = 0
            button_start = 0
            button_is_menu = 0
            button_opens_menu = 0
        }

        BEGIN {
            in_titlebar = 0
            titlebar_depth = 0
            reset_button()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_titlebar && line ~ /^[[:space:]]*D\.TitleBar[[:space:]]*\{/) {
                in_titlebar = 1
                titlebar_depth = 0
                reset_button()
            }

            if (in_titlebar) {
                if (!in_button && line ~ /^[[:space:]]*((D\.)?(ToolButton|ActionButton|Button)|QQC\.Button)[[:space:]]*\{/) {
                    in_button = 1
                    button_depth = 0
                    button_start = NR
                    button_is_menu = 0
                    button_opens_menu = 0
                }

                if (in_button) {
                    if (button_depth == 1 && (line ~ /id[[:space:]]*:[[:space:]]*mainMenuButton/ \
                        || line ~ /text[[:space:]]*:[[:space:]]*"(主菜单|更多)"/ \
                        || line ~ /icon\.(name|source)[[:space:]]*:[[:space:]]*".*(open-menu|menu|hamburger).*"/))
                    {
                        button_is_menu = 1
                    }

                    if (line ~ /onClicked[[:space:]]*:[[:space:]].*\.(open|popup)\(/)
                        button_opens_menu = 1

                    button_depth += delta
                    if (button_depth <= 0) {
                        if (button_is_menu && button_opens_menu)
                            printf "%s: D.TitleBar-based window still draws a separate main-menu trigger and opens the menu manually\n", button_start
                        reset_button()
                    }
                }

                titlebar_depth += delta
                if (titlebar_depth <= 0) {
                    in_titlebar = 0
                    reset_button()
                }
            }
        }
    ' "$file"
}

detect_non_dtk_dialog_hits() {
    local file="$1"
    grep -nE '^[[:space:]]*(QQC\.)?Dialog[[:space:]]*\{' "$file" || true
}

detect_popup_style_dtk_dialog_hits() {
    local file="$1"
    grep -nE '^[[:space:]]*D\.Dialog[[:space:]]*\{' "$file" || true
}

detect_dialog_button_box_hits() {
    local file="$1"
    grep -nE 'DialogButtonBox' "$file" || true
}

detect_vertical_action_stack_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function is_context_start(s) {
            return s ~ /^[[:space:]]*(SectionCard|MetricCard|D\.(Dialog|DialogWindow)|(Settings\.)?SettingsDialog)[[:space:]]*\{/
        }

        function is_action_block_start(s) {
            return s ~ /^[[:space:]]*(Flow|Column|ColumnLayout)[[:space:]]*\{/
        }

        function is_button_decl(s) {
            return s ~ /^[[:space:]]*((D\.)?(Button|RecommandButton|WarningButton)|QQC\.Button|Button)[[:space:]]*\{/
        }

        function push_context(level) {
            context_top++
            context_level[context_top] = level
        }

        function pop_context() {
            delete context_level[context_top]
            context_top--
        }

        function push_action(kind, level, start_line) {
            action_top++
            action_kind[action_top] = kind
            action_level[action_top] = level
            action_start[action_top] = start_line
            action_button_count[action_top] = 0
            action_top_to_bottom[action_top] = 0
        }

        function pop_action(    kind, start_line, button_count, top_to_bottom) {
            kind = action_kind[action_top]
            start_line = action_start[action_top]
            button_count = action_button_count[action_top]
            top_to_bottom = action_top_to_bottom[action_top]

            if (kind == "Flow" && button_count > 1) {
                if (top_to_bottom) {
                    printf "%s: action buttons inside a normal card or dialog must stay horizontal-first; do not switch to Flow.TopToBottom by default\n", start_line
                } else {
                    printf "%s: normal card or dialog action rows must not use Flow for multiple buttons because wrapping can degrade into one button per line\n", start_line
                }
            } else if ((kind == "Column" || kind == "ColumnLayout") && button_count > 1) {
                printf "%s: multiple action buttons inside a normal card or dialog are stacked vertically; keep them on one horizontal row by default\n", start_line
            }

            delete action_kind[action_top]
            delete action_level[action_top]
            delete action_start[action_top]
            delete action_button_count[action_top]
            delete action_top_to_bottom[action_top]
            action_top--
        }

        BEGIN {
            nest = 0
            context_top = 0
            action_top = 0
        }

        {
            line = $0
            delta = brace_delta(line)
            next_nest = nest + delta

            if (context_top > 0) {
                for (i = 1; i <= action_top; i++) {
                    if (nest == action_level[i] && is_button_decl(line))
                        action_button_count[i]++
                    if (nest == action_level[i] && action_kind[i] == "Flow" && line ~ /flow[[:space:]]*:[[:space:]].*Flow\.TopToBottom/)
                        action_top_to_bottom[i] = 1
                }
            }

            if (is_context_start(line))
                push_context(next_nest)

            if (context_top > 0 && is_action_block_start(line)) {
                kind = "Column"
                if (line ~ /^[[:space:]]*Flow[[:space:]]*\{/)
                    kind = "Flow"
                else if (line ~ /^[[:space:]]*ColumnLayout[[:space:]]*\{/)
                    kind = "ColumnLayout"
                push_action(kind, next_nest, NR)
            }

            nest = next_nest

            while (action_top > 0 && nest < action_level[action_top])
                pop_action()

            while (context_top > 0 && nest < context_level[context_top])
                pop_context()
        }

        END {
            while (action_top > 0)
                pop_action()
        }
    ' "$file"
}

detect_custom_dialog_content_style_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        function reset_label() {
            in_label = 0
            label_depth = 0
            label_start = 0
            label_center = 0
            label_large = 0
            label_weight = 0
            label_custom_text_color = 0
        }

        BEGIN {
            in_dialog = 0
            dialog_depth = 0
            reset_label()
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_dialog && line ~ /^[[:space:]]*D\.(Dialog|DialogWindow)[[:space:]]*\{/) {
                in_dialog = 1
                dialog_depth = 0
                reset_label()
            }

            if (in_dialog) {
                if (dialog_depth == 1 && line ~ /^[[:space:]]*(background|header|footer|contentItem|overlay)[[:space:]]*:/)
                    printf "%s: DTK dialog overrides structural dialog chrome instead of keeping the standard DTK body\n", NR

                if (dialog_depth >= 1 && line ~ /(SectionCard|MetricCard|StatusBadge|MetricValueLabel|CircularScore|PerformanceChart|PageHeader|AppItemIcon|SvgIcon)[[:space:]]*\{/)
                    printf "%s: DTK dialog embeds a page-style widget and no longer reads like a standard DTK dialog\n", NR

                if (!in_label && line ~ /^[[:space:]]*(D\.)?(Label|Text)[[:space:]]*\{/) {
                    in_label = 1
                    label_depth = 0
                    label_start = NR
                    label_center = 0
                    label_large = 0
                    label_weight = 0
                    label_custom_text_color = 0
                }

                if (in_label) {
                    if (label_depth == 1 && line ~ /^[[:space:]]*horizontalAlignment[[:space:]]*:[[:space:]]*Text\.Align(HCenter|Right)/)
                        label_center = 1
                    if (label_depth == 1 && (line ~ /^[[:space:]]*font\.pixelSize[[:space:]]*:[[:space:]]*Theme\.(sectionTitleSize|titleSize)/ \
                        || line ~ /^[[:space:]]*font\.pixelSize[[:space:]]*:[[:space:]]*1[7-9]([[:space:]]*(\/\/.*)?$)/ \
                        || line ~ /^[[:space:]]*font\.pixelSize[[:space:]]*:[[:space:]]*[2-9][0-9]([[:space:]]*(\/\/.*)?$)/))
                        label_large = 1
                    if (label_depth == 1 && line ~ /^[[:space:]]*font\.(weight|bold)[[:space:]]*:/)
                        label_weight = 1
                    if (label_depth == 1 && line ~ /^[[:space:]]*color[[:space:]]*:[[:space:]]*Theme\.(textPrimary|textSecondary|textStrong|textMuted|inverseText|fgNormal|fgStrong|iconNormal|iconStrong|accentForeground)([^A-Za-z0-9_]|$)/)
                        label_custom_text_color = 1

                    label_depth += delta
                    if (label_depth <= 0) {
                        if (label_center)
                            printf "%s: DTK dialog body label is center/right aligned; keep standard DTK dialog text alignment\n", label_start
                        if (label_large)
                            printf "%s: DTK dialog body adds an oversized secondary heading instead of relying on the dialog title\n", label_start
                        if (label_weight && label_large)
                            printf "%s: DTK dialog body emphasizes a secondary heading with custom weight\n", label_start
                        if (label_custom_text_color)
                            printf "%s: DTK dialog body overrides normal text color with project Theme tokens\n", label_start
                        reset_label()
                    }
                }

                dialog_depth += delta
                if (dialog_depth <= 0) {
                    in_dialog = 0
                    reset_label()
                }
            }
        }
    ' "$file"
}

detect_navigation_only_sidebar_card_hits() {
    local file="$1"
    awk '
        function brace_delta(s,   tmp, opens, closes) {
            tmp = s
            opens = gsub(/\{/, "{", tmp)
            closes = gsub(/\}/, "}", tmp)
            return opens - closes
        }

        BEGIN {
            in_cards = 0
            cards_depth = 0
            current_key = ""
            in_handler = 0
            handler_depth = 0
            branch_key = ""
        }

        {
            line = $0
            delta = brace_delta(line)

            if (!in_cards && line ~ /readonly[[:space:]]+property[[:space:]]+var[[:space:]]+sidebarOperationCards[[:space:]]*:[[:space:]]*\{/) {
                in_cards = 1
                cards_depth = 0
                current_key = ""
            }

            if (in_cards) {
                if (line ~ /key[[:space:]]*:[[:space:]]*"[^"]+"/) {
                    current_key = line
                    sub(/.*key[[:space:]]*:[[:space:]]*"/, "", current_key)
                    sub(/".*/, "", current_key)
                }
                if (current_key != "" && line ~ /actionText[[:space:]]*:[[:space:]]*"(查看|打开|前往|进入|跳转)/) {
                    nav_card[current_key] = NR
                }

                cards_depth += delta
                if (cards_depth <= 0) {
                    in_cards = 0
                    current_key = ""
                }
            }

            if (!in_handler && line ~ /function[[:space:]]+handleSidebarOperationCard[[:space:]]*\(/) {
                in_handler = 1
                handler_depth = 0
                branch_key = ""
            }

            if (in_handler) {
                if (line ~ /cardKey[[:space:]]*===?[[:space:]]*"[^"]+"/) {
                    branch_key = line
                    sub(/.*cardKey[[:space:]]*===?[[:space:]]*"/, "", branch_key)
                    sub(/".*/, "", branch_key)
                }

                if (branch_key != "" && line ~ /navigate[[:space:]]*\(/)
                    branch_has_navigate[branch_key] = 1
                if (branch_key != "" && line ~ /(ensureAdmin|adminDialogRequested|Qt\.openUrlExternally|begin[A-Z]|start[A-Z]|confirm[A-Z]|complete[A-Z]|grant[A-Z]|purchase|subscribe|unlock|pay)/)
                    branch_has_non_nav_action[branch_key] = 1

                handler_depth += delta
                if (handler_depth <= 0) {
                    in_handler = 0
                    branch_key = ""
                }
            }
        }

        END {
            for (key in nav_card) {
                if (branch_has_navigate[key] && !branch_has_non_nav_action[key]) {
                    printf "%s: sidebar operational card '%s' only routes to an in-app page and should be removed by default\n", nav_card[key], key
                }
            }
        }
    ' "$file"
}

detect_sidebar_width_squeeze_hits() {
    local file="$1"
    if grep -qE 'AppSidebar|sidebarWidth|sidebarHidden|onCollapseRequested' "$file"; then
        if grep -q 'Behavior on width' "$file"; then
            grep -n 'Behavior on width' "$file" || true
        fi
    fi
}

dtk_available=0
for candidate in \
    /usr/lib/x86_64-linux-gnu/qt6/qml/org/deepin/dtk \
    /usr/lib64/qt6/qml/org/deepin/dtk \
    /usr/lib/qt6/qml/org/deepin/dtk \
    /usr/lib/qt/qml/org/deepin/dtk \
    /usr/local/lib/qt6/qml/org/deepin/dtk
do
    if [[ -d "$candidate" ]]; then
        dtk_available=1
        dtk_qmldir="$candidate/qmldir"
        if [[ -f "$candidate/settings/qmldir" ]]; then
            dtk_settings_qmldir="$candidate/settings/qmldir"
        fi
        break
    fi
done

if (( dtk_available )); then
    if [[ -z "$(grep_repo '^[[:space:]]*import[[:space:]]+org\.deepin\.dtk' --include='*.qml')" ]]; then
        log_fail "dtk-import-missing" "DTK is installed locally but no 'import org.deepin.dtk' was found in project QML."
    fi

    if [[ -z "$(grep_repo 'Dtk6|DtkDeclarative|deepin[._-]?dtk|DTK' --include='CMakeLists.txt' --include='*.cmake' --include='*.pro' --include='*.pri')" ]]; then
        log_fail "dtk-build-missing" "DTK is installed locally but no DTK build integration was found in CMake/qmake files."
    fi
fi

circular_score_fixed_typography=0
if [[ -n "$(grep_repo 'font\.pixelSize[[:space:]]*:[[:space:]]*[4-9][0-9]' --include='*CircularScore*.qml')" ]]; then
    circular_score_fixed_typography=1
fi

while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    log_fail "non-dtk-style" "$line"
done < <(grep_repo 'QQuickStyle::setStyle\(.*(Basic|Fusion|Material|Imagine|Universal|FluentWinUI3)' --include='*.cpp' --include='*.cc' --include='*.cxx' --include='*.h' --include='*.hpp')

while IFS= read -r -d '' file; do
    rel="${file#$ROOT/}"

    if ! grep -q 'deepin-design: allow-icon-rasterization' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "icon-rasterization" "$rel:$hit"
        done < <(grep -nE '\.pixmap\(|save\(.*["'\'']PNG["'\'']' "$file" || true)
    fi
done < <(list_source_files)

while IFS= read -r -d '' file; do
    rel="${file#$ROOT/}"

    if ! grep -q 'deepin-design: allow-frameless' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "frameless-window" "$rel:$hit"
        done < <(grep -nE 'Qt\.FramelessWindowHint' "$file" || true)
    fi

    if ! grep -q 'deepin-design: allow-large-window-default' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "large-window-default" "$rel:$hit"
        done < <(detect_large_window_size_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-compact-settings-dialog' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "compact-settings-dialog" "$rel:$hit"
        done < <(detect_small_settings_dialog_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-system-titlebar-on-standard-dtk-surface' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "standard-dtk-surface-system-titlebar" "$rel:$hit"
        done < <(detect_standard_dtk_surface_system_titlebar_hits "$file")
    fi

    if (( dtk_available )) && dtk_settings_has_export SettingsDialog && ! grep -q 'deepin-design: allow-settings-dialog-without-icon' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "settings-dialog-missing-icon" "$rel:$hit"
        done < <(detect_settings_dialog_missing_icon_hits "$file")
    fi

    if (( dtk_available )) && dtk_settings_has_export CheckBox && ! grep -q 'deepin-design: allow-settings-checkbox-fallback' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "settings-checkbox-fallback" "$rel:$hit"
        done < <(detect_settings_checkbox_fallback_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-custom-settings-reset-entry' "$file" \
        && grep -qE '^[[:space:]]*((Settings\.)?SettingsDialog)[[:space:]]*\{' "$file"
    then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "custom-settings-reset-entry" "$rel:$hit: restore-default actions in multi-group settings should use the DTK-owned footer path instead of a normal settings row"
        done < <(grep -nE '^[[:space:]]*(key|name)[[:space:]]*:[[:space:]]*["'\'']([^"'\'']*)(restoreDefaults|resetDefaults|Restore Defaults|恢复默认)' "$file" || true)
    fi

    if ! grep -q 'deepin-design: allow-custom-settings-row-metrics' "$file" \
        && grep -qE '^[[:space:]]*((Settings\.)?SettingsDialog)[[:space:]]*\{' "$file"
    then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "custom-settings-row-metrics" "$rel:$hit"
        done < <(detect_settings_option_delegate_theme_hits "$file")

        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "custom-settings-row-metrics" "$rel:$hit: multi-group settings should not route through project-specific SettingRow / SettingsOptionRow styling"
        done < <(grep -nE '(^|[^A-Za-z0-9_])(SettingRow|SettingsOptionRow)[[:space:]]*\{' "$file" || true)
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "non-dtk-dialog" "$rel:$hit"
    done < <(detect_non_dtk_dialog_hits "$file")

    if (( dtk_available )) && dtk_has_export DialogWindow && ! grep -q 'deepin-design: allow-popup-style-dialog' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "popup-style-dialog" "$rel:$hit"
        done < <(detect_popup_style_dtk_dialog_hits "$file")
    fi

    if (( dtk_available )) && dtk_has_export DialogWindow; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "dialog-button-box" "$rel:$hit"
        done < <(detect_dialog_button_box_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-vertical-action-stack' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "vertical-action-stack" "$rel:$hit"
        done < <(detect_vertical_action_stack_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-custom-dialog-content-style' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "custom-dialog-content-style" "$rel:$hit"
        done < <(detect_custom_dialog_content_style_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "dialog-overlay" "$rel:$hit"
    done < <(detect_dialog_overlay_hits "$file")

    if (( dtk_available )) && dtk_has_export WindowButtonGroup && ! grep -q 'deepin-design: allow-custom-window-buttons' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "custom-window-buttons" "$rel:$hit"
        done < <(detect_custom_window_button_hits "$file")
    fi

    if (( dtk_available )) && dtk_has_export WindowButtonGroup && ! grep -q 'deepin-design: allow-offset-window-button-group' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "window-button-group-placement" "$rel:$hit"
        done < <(detect_window_button_group_placement_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "titlebar-control-safe-area" "$rel:$hit"
    done < <(detect_titlebar_safe_area_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "titlebar-clipped-ancestor" "$rel:$hit"
    done < <(detect_titlebar_clipped_ancestor_hits "$file")

    if ! grep -q 'deepin-design: allow-customized-window-flags' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "customized-window-flags" "$rel:$hit"
        done < <(detect_risky_titlebar_flag_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "transparent-titlebar-background" "$rel:$hit"
    done < <(detect_transparent_titlebar_background_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "titleband-underlay-gap" "$rel:$hit"
    done < <(detect_titleband_underlay_gap_hits "$file")

    if ! grep -q 'deepin-design: allow-transparent-main-window' "$file"; then
        if [[ "$(file_has_root_application_window "$file")" == "yes" ]] \
            && grep -qE '^[[:space:]]*color[[:space:]]*:[[:space:]]*["'\'']transparent["'\'']' "$file" \
            && ! grep -qE "$surface_token_pattern" "$file"
        then
            while IFS= read -r hit; do
                [[ -z "$hit" ]] && continue
                log_fail "transparent-main-window" "$rel:$hit (transparent top-level window without an explicit theme-backed base surface)"
            done < <(grep -nE '^[[:space:]]*color[[:space:]]*:[[:space:]]*["'\'']transparent["'\'']' "$file" || true)
        fi
    fi

    if ! grep -q 'deepin-design: allow-full-window-base-under-sidebar-blur' "$file"; then
        if [[ "$(file_has_root_application_window "$file")" == "yes" ]] \
            && grep -qE '^[[:space:]]*color[[:space:]]*:[[:space:]]*["'\'']transparent["'\'']' "$file" \
            && grep -qE 'AppSidebar|sidebarWidth|sidebarHidden|sidebarHost|onCollapseRequested' "$file"
        then
            while IFS= read -r hit; do
                [[ -z "$hit" ]] && continue
                log_fail "sidebar-blur-covered-by-base-surface" "$rel:$hit (scope theme-backed base surfaces to the right content panel; do not place a full-window base underneath the blurred sidebar)"
            done < <(detect_sidebar_blur_covered_by_base_surface_hits "$file")
        fi
    fi

    if ! grep -q 'deepin-design: allow-full-window-blur' "$file"; then
        if [[ "$(file_has_root_application_window "$file")" == "yes" ]] \
            && grep -qE 'AppSidebar|sidebarWidth|sidebarHidden|sidebarHost|onCollapseRequested' "$file"
        then
            while IFS= read -r hit; do
                [[ -z "$hit" ]] && continue
                log_fail "full-width-titlebar-sidebar-app" "$rel:$hit"
            done < <(detect_full_width_titlebar_sidebar_hits "$file")
            while IFS= read -r hit; do
                [[ -z "$hit" ]] && continue
                log_fail "full-window-blur-sidebar-app" "$rel:$hit"
            done < <(detect_full_window_blur_hits "$file")
        fi
    fi

    if [[ "$(file_has_root_application_window "$file")" == "yes" ]] \
        && grep -qE 'AppSidebar|sidebarWidth|sidebarHidden|sidebarHost|onCollapseRequested' "$file"
    then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "sidebar-gap" "$rel:$hit (keep sidebar/content spacing at 0 and place the divider on the sidebar edge instead of anchoring content after a spacer item)"
        done < <(detect_sidebar_gap_hits "$file")

        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "top-operational-banner" "$rel:$hit"
        done < <(detect_top_operational_banner_hits "$file")

        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "sidebar-width-squeeze" "$rel:$hit (collapse/expand should read as translate-out / translate-in, not width squeeze)"
        done < <(detect_sidebar_width_squeeze_hits "$file")
    fi

    case "$rel" in
        *Sidebar*.qml)
            if [[ "$(file_has_root_item "$file")" == "yes" ]] \
                && grep -q 'ListView' "$file" \
                && ! grep -q 'StyledBehindWindowBlur' "$file" \
                && [[ "$(file_has_fill_parent_rectangle "$file")" != "yes" ]]
            then
                log_fail "sidebar-panel-surface-missing" "$rel: sidebar component renders navigation content but never establishes an explicit sidebar panel surface"
            fi

            if grep -q 'ListView' "$file" && [[ "$(file_has_sidebar_edge_divider "$file")" != "yes" ]]; then
                log_fail "sidebar-edge-divider-missing" "$rel: persistent sidebar lacks a 1px divider anchored to the sidebar right edge"
            fi

            while IFS= read -r hit; do
                [[ -z "$hit" ]] && continue
                log_fail "sidebar-single-group-header" "$rel:$hit"
            done < <(detect_single_group_sidebar_header_hits "$file")

            while IFS= read -r hit; do
                [[ -z "$hit" ]] && continue
                log_fail "sidebar-group-spacing" "$rel:$hit"
            done < <(detect_sidebar_group_spacing_hits "$file")

            if grep -qE 'currentPage|pageSelected|navigationGroups' "$file" && grep -q 'ListView' "$file"; then
                while IFS= read -r hit; do
                    [[ -z "$hit" ]] && continue
                    log_fail "sidebar-nav-icon-treatment" "$rel:$hit"
                done < <(detect_sidebar_nav_icon_treatment_hits "$file")
            fi

            if [[ "$(basename "$file")" == "SidebarMessageCard.qml" ]] \
                || { grep -q 'actionTriggered' "$file" && grep -q 'actionText' "$file"; }
            then
                while IFS= read -r hit; do
                    [[ -z "$hit" ]] && continue
                    log_fail "sidebar-operational-button-width" "$rel:$hit"
                done < <(detect_sidebar_operational_button_width_hits "$file")
            fi
            ;;
    esac

    if ! grep -q 'deepin-design: allow-popup-window' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "popup-window" "$rel:$hit"
        done < <(grep -nE 'Popup\.Window' "$file" || true)
    fi

    if [[ "$(basename "$file")" != "Theme.qml" ]] && ! grep -q 'deepin-design: allow-literal-color' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "hardcoded-color" "$rel:$hit"
        done < <(grep -nE '#[0-9A-Fa-f]{3,8}\b' "$file" || true)
    fi

    if ! grep -q 'deepin-design: allow-textMuted-icon' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "text-muted-icon" "$rel:$hit"
        done < <(grep -nE 'tint[[:space:]]*:.*Theme\.textMuted' "$file" || true)
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "manual-blur-overlay" "$rel:$hit"
    done < <(detect_manual_blur_overlay_hits "$file")

    if ! grep -q 'deepin-design: allow-app-side-window-decoration-tuning' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "app-side-window-decoration-tuning" "$rel:$hit"
        done < <(grep -nE 'D\.DWindow\.(windowRadius|borderWidth|borderColor|shadowRadius|shadowOffset|shadowColor)[[:space:]]*:' "$file" || true)
    fi

    if ! grep -q 'deepin-design: allow-anchored-item-implicit-height' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "anchored-item-implicit-height" "$rel:$hit"
        done < <(detect_anchored_item_implicit_height_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "self-binding" "$rel:$hit"
    done < <(detect_self_binding_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "large-title-weight" "$rel:$hit"
    done < <(detect_large_title_weight_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "page-header-icon" "$rel:$hit"
    done < <(detect_page_header_icon_hits "$file")

    if [[ "$(basename "$file")" != "MetricValueLabel.qml" ]]; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "large-unit-label" "$rel:$hit"
        done < <(detect_large_unit_label_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-shadowed-delegate-role' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "shadowed-delegate-role" "$rel:$hit"
        done < <(detect_shadowed_delegate_role_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-list-without-leading-icon' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "multiline-list-missing-icon" "$rel:$hit"
        done < <(detect_multiline_setting_row_missing_icon_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-nonstandard-list-icon-size' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "multiline-list-icon-size" "$rel:$hit"
        done < <(detect_multiline_setting_row_icon_size_hits "$file")
    fi

    if (( circular_score_fixed_typography )) && [[ "$(basename "$file")" != "CircularScore.qml" ]]; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "small-circular-score-usage" "$rel:$hit"
        done < <(detect_small_circular_score_usage_hits "$file")
    fi

    if [[ "$(basename "$file")" == "ContentPage.qml" ]] \
        && [[ "$(file_has_root_item "$file")" == "yes" ]] \
        && ! grep -qE "$surface_token_pattern" "$file"
    then
        log_fail "content-page-surface-missing" "$rel: page skeleton does not consume any documented theme background token"
    fi

    if looks_like_fake_table "$file"; then
        log_fail "fake-table-column-plan" "$rel: table-like screen appears to use separate header widths and row widths without a shared column plan"
    fi

    if ! grep -q 'deepin-design: allow-freeform-trailing-control-row' "$file"; then
        if grep -qE 'Repeater|delegate[[:space:]]*:' "$file" \
            && grep -qE '(^|[[:space:]])(AppSwitch|D\.Switch|Switch|D\.ComboBox|ComboBox)([[:space:]]|\{)' "$file" \
            && ! grep -qE 'SettingRow|SettingsOptionRow|controlSlot|trailingSlot|trailingControl|rightControl|controlColumn|actionSlot' "$file"
        then
            log_fail "freeform-trailing-control-row" "$rel: repeated rows with trailing controls should use a dedicated right-side control slot or shared control column"
        fi
    fi

    if ! grep -q 'deepin-design: allow-oversized-card' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "oversized-card" "$rel:$hit"
        done < <(detect_oversized_card_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "fixed-hero-card-shell" "$rel:$hit"
    done < <(detect_fixed_score_hero_card_hits "$file")

    if ! grep -q 'deepin-design: allow-card-edge-focal-content' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "card-focal-content-edge" "$rel:$hit"
        done < <(detect_card_focal_content_edge_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "focal-wrapper-mismatch" "$rel:$hit"
    done < <(detect_focal_wrapper_mismatch_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "fill-anchored-card-layout" "$rel:$hit"
    done < <(detect_fill_anchored_card_layout_hits "$file")

    if ! grep -q 'deepin-design: allow-wide-button' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "wide-button" "$rel:$hit"
        done < <(detect_wide_button_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-horizontal-list-scroll' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "horizontal-list-scroll" "$rel:$hit"
        done < <(detect_horizontal_scroll_risk_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "horizontal-scrollbar-thickness" "$rel:$hit"
    done < <(detect_horizontal_scrollbar_thickness_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "textless-progress-thickness" "$rel:$hit"
    done < <(detect_textless_progress_thickness_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "duplicate-progress-mode" "$rel:$hit"
    done < <(detect_duplicate_progress_mode_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "legacy-page-list-row" "$rel:$hit"
    done < <(detect_legacy_page_list_row_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "variable-list-card-shell" "$rel:$hit"
    done < <(detect_variable_object_list_card_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "list-height-cap" "$rel:$hit"
    done < <(detect_list_height_cap_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "dense-cluster-zero-spacing" "$rel:$hit"
    done < <(detect_dense_cluster_zero_spacing_hits "$file")

    if ! grep -q 'deepin-design: allow-custom-in-app-notification' "$file"; then
        case "$rel" in
            *Toast*.qml)
                if ! grep -qE '(^|[[:space:]])D\.FloatingMessage([[:space:]]|\{)' "$file"; then
                    log_fail "custom-in-app-notification" "$rel: expected DTK FloatingMessage for in-app notifications"
                fi
                ;;
        esac
    fi

    if ! grep -q 'deepin-design: allow-dtk-template-override' "$file"; then
        if [[ "$(file_has_root_dtk_template_control "$file")" == "yes" ]]; then
            while IFS= read -r hit; do
                [[ -z "$hit" ]] && continue
                log_fail "dtk-template-override" "$rel:$hit"
            done < <(grep -nE '^[[:space:]]*(background|contentItem|indicator|handle|popup|delegate)[[:space:]]*:' "$file" || true)
        fi
    fi

    if ! grep -q 'deepin-design: allow-derived-nav-color' "$file"; then
        case "$rel" in
            *Sidebar*.qml|*Nav*.qml|*Navigation*.qml|*Tab*.qml)
                while IFS= read -r hit; do
                    [[ -z "$hit" ]] && continue
                    log_fail "derived-nav-color" "$rel:$hit"
                done < <(grep -nE 'Theme\.(mix|withAlpha)\(' "$file" || true)
                ;;
        esac
    fi

    if ! grep -q 'deepin-design: allow-sidebar-active-border' "$file"; then
        case "$rel" in
            *Sidebar*.qml|*Nav*.qml|*Navigation*.qml)
                while IFS= read -r hit; do
                    [[ -z "$hit" ]] && continue
                    log_fail "sidebar-active-border" "$rel:$hit"
                done < <(detect_sidebar_selected_border_hits "$file")
                ;;
        esac
    fi

    if ! grep -q 'deepin-design: allow-custom-main-menu-button' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "titlebar-custom-main-menu-trigger" "$rel:$hit (when D.TitleBar is used, let TitleBar.menu generate and own the main-menu button; do not self-draw a trigger)"
        done < <(detect_titlebar_custom_main_menu_trigger_hits "$file")

        if grep -qE '(^|[[:space:]])(AppButton|Button|QQC\.Button|D\.ToolButton|D\.ActionButton)([[:space:]]|\{)' "$file" \
            && grep -qE 'iconName[[:space:]]*:[[:space:]]*"menu"|text[[:space:]]*:[[:space:]]*"更多"|text[[:space:]]*:[[:space:]]*"主菜单"|id[[:space:]]*:[[:space:]]*mainMenuButton' "$file" \
            && grep -qE 'onClicked[[:space:]]*:[[:space:]].*\.(open|popup)\(' "$file"
        then
            log_fail "custom-main-menu-button" "$rel: suspected custom application main-menu trigger; use DTK menu button or add waiver"
        fi
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "main-menu-without-titlebar" "$rel:$hit"
    done < <(detect_main_menu_without_titlebar_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "titlebar-menu-attachment" "$rel:$hit"
    done < <(detect_titlebar_menu_attachment_hits "$file")

    if ! grep -q 'deepin-design: allow-manual-main-menu-position' "$file"; then
        if grep -qE '(^|[[:space:]])D\.Menu([[:space:]]|\{)|(^|[[:space:]])Menu([[:space:]]|\{)' "$file" \
            && grep -qE 'iconName[[:space:]]*:[[:space:]]*"menu"|text[[:space:]]*:[[:space:]]*"更多"' "$file" \
            && grep -qE '^[[:space:]]*x[[:space:]]*:' "$file" \
            && grep -qE '^[[:space:]]*y[[:space:]]*:' "$file"
        then
            log_fail "manual-main-menu-position" "$rel: suspected manual main-menu popup coordinates; follow DTK placement or add waiver"
        fi
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "custom-main-menu-icon" "$rel:$hit"
    done < <(detect_custom_main_menu_icon_hits "$file")

    if ! grep -q 'deepin-design: allow-custom-about-dialog' "$file"; then
        case "$rel" in
            *AboutDialog*.qml)
                if ! grep -qE '(^|[[:space:]])D\.AboutDialog([[:space:]]|\{)' "$file"; then
                    log_fail "custom-about-dialog" "$rel: expected DTK AboutDialog for About surfaces"
                fi
                ;;
        esac
    fi

    if ! grep -q 'deepin-design: allow-detailed-gauge-center-text' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "detailed-gauge-center-text" "$rel:$hit"
        done < <(detect_detailed_gauge_center_text_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "search-placeholder-inactive" "$rel:$hit"
    done < <(detect_search_placeholder_inactive_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "search-filter-ratio" "$rel:$hit"
    done < <(detect_search_filter_ratio_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "compact-list-text" "$rel:$hit"
    done < <(detect_compact_list_text_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "placeholder-list-icon" "$rel:$hit"
    done < <(detect_placeholder_list_icon_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "gradient-card-whitespace" "$rel:$hit"
    done < <(detect_gradient_card_whitespace_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "status-duplication" "$rel:$hit"
    done < <(detect_status_duplication_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "option-row-icon" "$rel:$hit"
    done < <(detect_option_row_icon_hits "$file")

    if ! grep -q 'deepin-design: allow-shared-functional-list-icon' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "shared-functional-row-icon" "$rel:$hit"
        done < <(detect_repeated_functional_row_icon_hits "$file")

        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "shared-functional-model-icon" "$rel:$hit"
        done < <(detect_shared_functional_model_icon_hits "$file")
    fi

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "chart-missing-axes" "$rel:$hit"
    done < <(detect_chart_missing_axes_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "chart-missing-animation" "$rel:$hit"
    done < <(detect_chart_missing_animation_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "chart-curve-style" "$rel:$hit"
    done < <(detect_chart_curve_style_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "progress-foreground-shadow" "$rel:$hit"
    done < <(detect_progress_shadow_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "ring-progress-style" "$rel:$hit"
    done < <(detect_ring_progress_style_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "unified-toolbar-height" "$rel:$hit"
    done < <(detect_unified_toolbar_height_hits "$file")

    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "unified-toolbar-divider" "$rel:$hit"
    done < <(detect_unified_toolbar_divider_hits "$file")

    if ! grep -q 'deepin-design: allow-nonstandard-sidebar-toggle-icon' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "nonstandard-sidebar-toggle-icon" "$rel:$hit (use the control-center-style dedicated sidebar-toggle glyph/button, not a generic chevron or arrow)"
        done < <(detect_nonstandard_sidebar_toggle_icon_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-moving-logo-slot' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "moving-logo-slot" "$rel:$hit (keep the top-left logo in one stable window-relative slot; do not place it in the animated sidebar or toggle its slot across sidebar states)"
        done < <(detect_moving_logo_slot_hits "$file")
    fi

    if ! grep -q 'deepin-design: allow-toolbar-page-title' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            log_fail "toolbar-page-title" "$rel:$hit (toolbar top bands must not show page titles by default; move page titles into the page content header unless explicitly requested)"
        done < <(detect_toolbar_page_title_hits "$file")
    fi

    if grep -qE '(^|[[:space:]])D\.Menu([[:space:]]|\{)|(^|[[:space:]])Menu([[:space:]]|\{)' "$file" \
        && grep -qE '关于|About|退出|Exit|Quit|设置|Settings|applicationMenu|mainMenu' "$file"
    then
        main_menu_candidates+=("$file")
    fi

    if [[ "$(basename "$file")" != *SettingsDialog.qml ]] && ! grep -q 'deepin-design: allow-secondary-settings-entry' "$file"; then
        while IFS= read -r hit; do
            [[ -z "$hit" ]] && continue
            settings_button_candidates+=("$rel:$hit")
        done < <(detect_secondary_settings_entry_hits "$file")
    fi
done < <(list_qml_files)

app_store_file="$(find "$ROOT" \
    \( -path "$ROOT/.git" \
    -o -path "$ROOT/.idea" \
    -o -path "$ROOT/.vscode" \
    -o -path "$ROOT/.cache" \
    -o -path "$ROOT/.codex" \
    -o -path "$ROOT/build" \
    -o -path "$ROOT/cmake-build-debug" \
    -o -path "$ROOT/cmake-build-release" \
    -o -path "$ROOT/dist" \
    -o -path "$ROOT/node_modules" \) -prune \
    -o -type f -name 'AppStore.qml' -print -quit)"

if [[ -n "$app_store_file" ]]; then
    app_store_rel="${app_store_file#$ROOT/}"
    while IFS= read -r hit; do
        [[ -z "$hit" ]] && continue
        log_fail "navigation-only-sidebar-card" "$app_store_rel:$hit"
    done < <(detect_navigation_only_sidebar_card_hits "$app_store_file")
fi

operational_notice_hits="$(grep_repo '解锁|付费|订阅|会员|权益|服务升级|premium|subscribe|unlock|paywall|会员服务' --include='*.qml' || true)"
if [[ -n "$operational_notice_hits" ]]; then
    sidebar_operational_dock_hits="$(grep_repo 'anchors\.bottom|Layout\.alignment[[:space:]]*:.*Qt\.AlignBottom|bottomMargin[[:space:]]*:[[:space:]]*10' --include='*Sidebar*.qml' || true)"
    if [[ -z "$sidebar_operational_dock_hits" ]]; then
        log_fail "sidebar-operational-cards-missing" "Operational unlock/pay/service notices exist in project QML but no sidebar-bottom card docking pattern was detected."
    fi
fi

theme_file="$(find "$ROOT" \
    \( -path "$ROOT/.git" \
    -o -path "$ROOT/.idea" \
    -o -path "$ROOT/.vscode" \
    -o -path "$ROOT/.cache" \
    -o -path "$ROOT/.codex" \
    -o -path "$ROOT/build" \
    -o -path "$ROOT/cmake-build-debug" \
    -o -path "$ROOT/cmake-build-release" \
    -o -path "$ROOT/dist" \
    -o -path "$ROOT/node_modules" \) -prune \
    -o -type f -name 'Theme.qml' -print -quit)"

if [[ -n "$theme_file" ]] \
    && grep -qE 'readonly property color (bg|bgPanel|bgToolbar|panelBg|titlebarBg)[[:space:]]*:' "$theme_file"
then
    theme_usage_hits="$(grep_repo 'Theme\.(bg|bgPanel|bgToolbar|panelBg|titlebarBg)([^A-Za-z0-9_]|$)' --include='*.qml' | grep -v '/Theme.qml:' || true)"
    if [[ -z "$theme_usage_hits" ]]; then
        log_fail "theme-surface-token-unused" "Theme.qml defines background surface tokens but no live QML surface consumes Theme.bg/bgPanel/bgToolbar/panelBg/titlebarBg."
    fi
fi

if [[ -n "$theme_file" ]] && ! grep -q 'deepin-design: allow-theme-baseline-deviation' "$theme_file"; then
    system_accent_line="$(theme_property_line "$theme_file" 'systemAccent')"
    if [[ -z "$system_accent_line" || "$system_accent_line" != *'D.DTK.palette.highlight'* ]]; then
        log_fail "theme-system-accent" "Theme.qml: systemAccent must be sourced from D.DTK.palette.highlight."
    fi

    if [[ -z "$(theme_property_line "$theme_file" 'fgNormal')" ]]; then
        log_fail "theme-fgNormal-missing" "Theme.qml: expected fgNormal foreground baseline token."
    fi

    if [[ -z "$(theme_property_line "$theme_file" 'fgStrong')" ]]; then
        log_fail "theme-fgStrong-missing" "Theme.qml: expected fgStrong foreground baseline token."
    fi

    text_primary_line="$(theme_property_line "$theme_file" 'textPrimary')"
    if [[ -z "$text_primary_line" || "$text_primary_line" != *'fgNormal'* ]]; then
        log_fail "theme-textPrimary-baseline" "Theme.qml: textPrimary should resolve from fgNormal."
    fi

    text_strong_line="$(theme_property_line "$theme_file" 'textStrong')"
    if [[ -z "$text_strong_line" || "$text_strong_line" != *'fgStrong'* ]]; then
        log_fail "theme-textStrong-baseline" "Theme.qml: textStrong should resolve from fgStrong."
    fi

    icon_normal_line="$(theme_property_line "$theme_file" 'iconNormal')"
    if [[ -z "$icon_normal_line" || ( "$icon_normal_line" != *'fgNormal'* && "$icon_normal_line" != *'textPrimary'* ) ]]; then
        log_fail "theme-iconNormal-baseline" "Theme.qml: iconNormal should resolve from fgNormal or textPrimary."
    fi

    icon_strong_line="$(theme_property_line "$theme_file" 'iconStrong')"
    if [[ -z "$icon_strong_line" || ( "$icon_strong_line" != *'fgStrong'* && "$icon_strong_line" != *'textStrong'* ) ]]; then
        log_fail "theme-iconStrong-baseline" "Theme.qml: iconStrong should resolve from fgStrong or textStrong."
    fi

    bg_line="$(theme_property_line "$theme_file" 'bg')"
    if [[ -z "$bg_line" || "$bg_line" != *'#181818'* || "$bg_line" != *'#F8F8F8'* ]]; then
        log_fail "theme-bg-baseline" "Theme.qml: bg should stay on the documented #181818 / #F8F8F8 neutral baseline unless waived."
    fi

    sidebar_blend_line="$(theme_property_line "$theme_file" 'sidebarBlurBlend')"
    if [[ -z "$sidebar_blend_line" ]]; then
        log_fail "theme-sidebar-blend-missing" "Theme.qml: expected sidebarBlurBlend token for persistent-left-sidebar audits."
    else
        mapfile -t blur_hexes < <(printf '%s\n' "$sidebar_blend_line" | grep -oE '#[0-9A-Fa-f]{6,8}\b' || true)
        if (( ${#blur_hexes[@]} >= 2 )); then
            if ! hex_is_neutral_dark "${blur_hexes[0]}" || ! hex_alpha_is_sidebar_blend "${blur_hexes[0]}" \
                || ! hex_is_neutral_light "${blur_hexes[1]}" || ! hex_alpha_is_sidebar_blend "${blur_hexes[1]}"
            then
                log_fail "theme-sidebar-blend-baseline" "Theme.qml: sidebarBlurBlend must stay near neutral #CC101010 / #CCFFFFFF style glass, not an opaque or chromatic tint."
            fi
        elif ! printf '%s\n' "$sidebar_blend_line" | grep -qE 'Qt\.rgba\([[:space:]]*(16/255|0\.0627)[[:space:]]*,[[:space:]]*(16/255|0\.0627)[[:space:]]*,[[:space:]]*(16/255|0\.0627)[[:space:]]*,[[:space:]]*0\.8\)|Qt\.rgba\([[:space:]]*1[[:space:]]*,[[:space:]]*1[[:space:]]*,[[:space:]]*1[[:space:]]*,[[:space:]]*0\.8\)'; then
            log_fail "theme-sidebar-blend-baseline" "Theme.qml: sidebarBlurBlend must use the documented neutral ~0.80 blur tint baseline or an equivalent exact expression."
        fi
    fi

    sidebar_fallback_line="$(theme_property_line "$theme_file" 'sidebarBlurFallback')"
    if [[ -z "$sidebar_fallback_line" ]]; then
        log_fail "theme-sidebar-fallback-missing" "Theme.qml: expected sidebarBlurFallback token for persistent-left-sidebar audits."
    else
        mapfile -t fallback_hexes < <(printf '%s\n' "$sidebar_fallback_line" | grep -oE '#[0-9A-Fa-f]{6,8}\b' || true)
        if (( ${#fallback_hexes[@]} >= 2 )); then
            if ! hex_is_neutral_dark "${fallback_hexes[0]}" || ! hex_is_neutral_light "${fallback_hexes[1]}"; then
                log_fail "theme-sidebar-fallback-baseline" "Theme.qml: sidebarBlurFallback must stay near neutral #101010 / #FFFFFF style fallback tones."
            fi
        elif ! printf '%s\n' "$sidebar_fallback_line" | grep -qE '#101010|Qt\.rgba\([[:space:]]*(16/255|0\.0627)[[:space:]]*,[[:space:]]*(16/255|0\.0627)[[:space:]]*,[[:space:]]*(16/255|0\.0627)'; then
            log_fail "theme-sidebar-fallback-baseline" "Theme.qml: sidebarBlurFallback must use a documented neutral near-black / near-white fallback."
        fi
    fi
fi

if [[ -n "$(grep_repo '(^|[[:space:]])D\.(ProgressBar|Switch|CheckBox|ComboBox)([[:space:]]|\{)' --include='*.qml')" ]] \
    && [[ -n "$(grep_repo 'Theme\.(accentBackground|accentLight|surfaceHover|surfaceActive|navItemSelectedBg|cardBg)' --include='*.qml')" ]] \
    && [[ -z "$(grep_repo 'palette[[:space:]]*:|D\.Palette|accentColor|highlight|colorScheme' --include='*.qml')" ]]
then
    log_fail "dtk-palette-routing-missing" "Project uses raw DTK progress/switch/checkbox/combo-box controls alongside a custom theme layer, but no explicit DTK palette routing was found."
fi

for file in "${main_menu_candidates[@]}"; do
    rel="${file#$ROOT/}"

    if ! grep -qE '跟随系统|浅色|深色|(^|[^A-Za-z])(System|Light|Dark)([^A-Za-z]|$)|themeMenu|ThemeMenu|themeMode|Theme\.mode|setThemeMode' "$file"; then
        log_fail "main-menu-theme-switch" "$rel: suspected application main menu without System/Light/Dark theme switching"
    fi
done

if (( ${#main_menu_candidates[@]} > 0 )); then
    for hit in "${settings_button_candidates[@]}"; do
        log_fail "secondary-settings-entry" "$hit"
    done
fi

if (( findings )); then
    printf 'Deepin Design audit failed with %d finding(s).\n' "$findings" >&2
    exit 1
fi

echo "Deepin Design audit passed: no findings."
