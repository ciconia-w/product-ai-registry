# uos-design-skill

## Source Of Truth

- Primary instructions: `SKILL.md`
- Reference rules: `references/`
- UI metadata: `agents/openai.yaml`

## Current Baseline

- Any Linux desktop application with a persistent primary left sidebar must use a control-center style left-right split layout.
- Startup for that layout is interpreted as entering the persistent left-navigation split pane directly, not a homepage-first flow.
- The left sidebar must use a validated window-manager, compositor, or DTK blur path in the target environment.
- Pure-color fallback for that sidebar is a compatibility fallback only, not the intended finished design.
- Sidebar navigation content keeps a `10px` horizontal inset on both sides.
- Sidebar width may be resizable and remembered; collapse does not imply a fixed `60px` icon rail.

## Terminology

- Use `theme variables`, `semantic variables`, `color variables`, `spacing variables`, and `radius variables` instead of vague `token` wording.
- Use explicit terms such as `left-navigation split-pane layout`, `window structure`, `top-level window container`, and `dialog container` instead of vague `shell` wording.
