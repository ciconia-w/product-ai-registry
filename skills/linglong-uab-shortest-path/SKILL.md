---
name: linglong-uab-shortest-path
version: 0.2.0
description: Generic Linglong packaging workflow for Linux projects that already contain a linglong.yaml manifest or an equivalent Linglong build path
---

# Linglong Packaging Workflow

This skill is a **generic Linglong packaging workflow** for Linux projects.
It is not limited to one repository.

Use it when the goal is:

- rebuild or export a Linglong `.layer` or `.uab`
- clean stale local Linglong builder state before packaging
- validate the produced artifacts
- hand off a reusable Linglong package to another agent or teammate

## Activation conditions

Use this workflow when at least one of the following is true:

- the repository contains `linglong.yaml`
- the repository contains `build-linglong.sh` or `build-linglong-*.sh`
- the user asks to package an app as Linglong or export a `.uab`
- the user mentions `ll-builder`, `ll-cli`, `linyaps`, or `Linglong`

## Preconditions

Before you run any packaging command, check:

1. current host is Linux
2. target repository exists and is writable
3. repository contains `linglong.yaml` or a known Linglong build script
4. required CLIs exist:
   - `ll-builder`
   - `ll-cli`
   - `bash`
5. if the repo depends on a custom build script, confirm that script exists

If the repository has neither `linglong.yaml` nor a recognizable Linglong build script, stop and report `blocked`.

## Workflow

### Path A: project already has a Linglong build script

If the repository contains one of these, prefer it:

- `scripts/build-linglong.sh`
- `scripts/build-linglong-*.sh`

Then run:

```bash
reset-linglong-builder-env.sh
rebuild-linglong-uab-shortest-path.sh
```

This path preserves project-local packaging knowledge and should be your default.

### Path B: project has `linglong.yaml` but no build script

Use the generic workflow:

1. reset stale Linglong builder state
2. run `ll-builder build -f ./linglong.yaml`
3. export a `.layer`
4. attempt `.uab` export if the host runtime supports it
5. verify metadata and extracted payload

## Generic verification checklist

After packaging, verify whichever artifacts were produced:

```bash
find ./dist -maxdepth 1 \( -name '*.layer' -o -name '*.uab' \) | sort
```

If a `.uab` exists, verify:

```bash
./dist/<name>.uab --print-meta
./dist/<name>.uab --extract=/tmp/linglong-uab-check
sha256sum ./dist/<name>.uab
```

If only a `.layer` exists, report that clearly and keep the layer path.

## Fallback rules

- If direct `ll-builder export` fails but the `.layer` exists, keep the `.layer` and report partial success.
- If the host has stale Linglong mounts or cache residue, always reset first.
- If the project has custom vendoring or runtime patching inside its own build script, do not replace that logic with the generic path unless the user asks.

## Common pitfalls

Keep these checks in mind across projects:

- stale `~/.cache/linglong-builder`, repository-local `linglong/`, or `/tmp/linglong-runtime-*` can break export even when build steps look correct
- stale Linglong mounts can keep old payloads alive; reset before retrying difficult failures
- a project-specific `build-linglong*.sh` often contains critical vendoring, launcher patching, or runtime-path fixes; prefer it over generic `ll-builder build`
- `.uab` export may fail on one host while `.layer` export still succeeds; keep the `.layer` and report partial success instead of discarding work
- packaging can succeed but runtime can still fail if the app misses vendored Python, Qt, plugin, or icon assets inside the package payload
- if the project already has a validated base/runtime combination in `linglong.yaml`, do not casually switch it during troubleshooting

## When not to use this skill

Do not use this skill:

- for non-Linux hosts
- for projects that have no `linglong.yaml` and no recognizable Linglong build path
- to redesign an app’s package manifest from zero without project context

## Output contract

Return:

- which path you used: project build script or generic manifest path
- produced artifact paths
- SHA-256 if a `.uab` was produced
- whether the result is full success, partial success (`layer` only), or blocked

## Completion gate

Linglong packaging is **not complete** until a retrospective has been written and validated.

After the build or export step, the packaging agent must:

1. produce a retrospective payload
2. pipe it into `write-linglong-retrospective`
3. run `check-linglong-retrospective`

If `check-linglong-retrospective` fails, the overall Linglong workflow must be reported as `incomplete` or `blocked`, not `complete`.
