---
name: linglong-packaging-retrospective
version: 0.1.0
description: Capture a structured Linglong packaging pitfall report after a build or export run so future agents can reuse the host and project-specific lessons
---

# Linglong Packaging Retrospective

Use this skill after a Linglong packaging attempt finishes, whether it succeeded, partially succeeded, or failed.

Its job is to preserve the useful lessons from one packaging run so later agents do not repeat the same dead ends.

## When to use

Activate this skill when:

- a Linglong `.layer` or `.uab` build just completed
- a Linglong packaging attempt failed or produced a partial result
- the user asks to record packaging pitfalls, build notes, or a reusable sample
- another packaging agent needs a structured handoff

## Required output

Produce two artifacts:

1. a machine-readable JSON summary
2. a short Markdown note for humans and future agents

## Output fields

The JSON summary must contain:

- `date`
- `project_root`
- `host_summary`
- `package_id`
- `package_version`
- `base_runtime`
- `artifacts`
- `build_path_used`
- `result`
- `pitfalls`
- `workarounds`
- `verification`
- `open_questions`

## Pitfall capture checklist

Record only things that were actually observed in this run:

- stale mounts or cache residue
- project-specific vendoring requirements
- launcher or runtime-path patching
- missing Python, Qt, plugin, icon, or desktop-entry payloads
- `.layer` success with `.uab` failure
- host-specific builder behavior
- manual verification commands that proved success

## Storage rule

Write the outputs under the target repository in:

- `.ai-registry/linglong-retrospectives/<timestamp>.json`
- `.ai-registry/linglong-retrospectives/<timestamp>.md`

Create the directory if missing.

## Reporting rule

In the final user-facing summary, include:

- artifact paths
- top 1-3 pitfalls
- whether the retrospective was saved successfully

## Validation rule

After writing the retrospective, immediately run `check-linglong-retrospective`.

If the check fails:

- do not report the packaging workflow as complete
- report the missing retrospective as a blocker
