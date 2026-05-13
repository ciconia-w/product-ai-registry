---
name: linglong-uab-shortest-path
version: 0.1.0
description: Repo-specific playbook for rebuilding the deepin-color-correction Linglong UAB on a Linux host using the shortest known-good path
---

# deepin-color-correction Linglong UAB: Shortest Correct Path

This skill is **repo-specific**. It is not a general Linglong packaging guide.

Use it when the goal is:

- rebuild `deepin-color-correction` as Linglong
- export a fresh UAB on this machine
- avoid the previously observed failure classes:
  - stale `~/.cache/linglong-builder`
  - stale `linglong/` project cache
  - stale `/tmp/linglong-runtime-0`
  - repeated mount residue
  - "install success but kontainer misses Qt Python runtime"

## What already converged

Do **not** re-infer the package from scratch unless asked.

The repository already contains the converged inputs:

- `linglong.yaml`
- `scripts/build-linglong.sh`
- `scripts/build-linglong-pica.sh`
- `docs/linglong-packaging.md`

Current known-good package metadata target:

- package id: `org.deepin.deepin-color-correction`
- version: `0.1.0.6`
- base: `main:org.deepin.base/25.2.2/x86_64`
- runtime: `main:org.deepin.runtime.dtk/25.2.2/x86_64`

## Important repo-specific facts

1. `scripts/build-linglong.sh` is the primary build path on this host.
2. The script currently vendors:
   - `dbus`
   - `Xlib`
   - `PIL`
   - `six`
   - `PySide6`
   - `shiboken6`
   - their Qt runtime subtree
3. The previous "UAB can install but run fails with `ModuleNotFoundError: PySide2`" issue was addressed by vendoring `PySide6/shiboken6` into the layer/UAB.
4. The previous "cannot export UAB" issue was addressed by resetting the HOME builder repo and stale runtime/mount state before export.

## Shortest path

### Path A: Rebuild UAB from a dirty host

If this host has already been used for Linglong export/debugging, do this exact sequence:

1. Stop lingering Linglong-related processes.
2. Reset the local builder environment.
3. Rebuild the layer/UAB using the in-repo script.
4. Validate the rebuilt UAB locally.
5. Capture a local retrospective for this exact run.
6. Validate that the retrospective was saved correctly.
7. Report the run's pitfalls back into the shared reference surface.
8. Hand the UAB to the field-validation agent.

### Commands

From repo root:

```bash
./scripts/reset-linglong-builder-env.sh
./scripts/rebuild-linglong-uab-shortest-path.sh
```

## Validation checklist

After rebuild, verify:

```bash
./dist/deepin-color-correction_x86_64_0.1.0.6_main.uab --print-meta
./dist/deepin-color-correction_x86_64_0.1.0.6_main.uab --extract=/tmp/dcc-uab-check
sha256sum ./dist/deepin-color-correction_x86_64_0.1.0.6_main.uab
```

Expected high-level signals:

- `--print-meta` succeeds
- metadata still reports `0.1.0.6 / 25.2.2 / 25.2.2`
- extracted payload contains:
  - `files/lib/python3/dist-packages/PySide6`
  - `files/lib/python3/dist-packages/shiboken6`
- package size is much larger than the earlier "thin" UAB because the Qt Python runtime is now included

## Mandatory retrospective closeout

This skill is not complete after the UAB rebuild alone.

After the rebuild and local validation:

1. collect the facts from this exact run
2. write a retrospective under the target repository
3. immediately validate that retrospective

The retrospective must stay local to the target repository under:

- `.ai-registry/linglong-retrospectives/`

Record only things that were actually observed in this run, including:

- whether the reset step was required
- whether stale mounts or cache residue existed
- what build path was used
- whether `.layer` and `.uab` both succeeded
- what verification commands proved success
- what pitfalls or workarounds were necessary on this host

Use the local retrospective helpers that materialize with this workflow:

- `write-linglong-retrospective`
- `check-linglong-retrospective`

If retrospective validation fails, do **not** report this packaging workflow as complete.

## Shared reporting rule

Besides the local retrospective, this workflow must also report the run's observed pitfalls into the shared reference surface so later agents can discover them.

The required behavior is:

1. save the complete run-specific retrospective locally in the target repository
2. produce a concise shared-facing summary of:
   - host summary
   - build path used
   - result
   - top pitfalls
   - top workarounds
   - verification signals
3. append or submit that summary to the shared Linglong reference maintenance path used by this registry

The local retrospective remains the full-fidelity source of truth for the run.
The shared report is the cross-run discovery layer for future agents.

If the shared reporting step is skipped, do **not** treat the workflow as fully complete.

## Field handoff rule

If the rebuilt UAB exceeds Slock attachment size, do **not** waste time retrying upload.

Instead:

1. provide the absolute local path
2. provide the SHA-256
3. tell the field agent to:

```bash
sudo ll-cli uninstall org.deepin.deepin-color-correction
sudo ll-cli install /absolute/path/to/deepin-color-correction_x86_64_0.1.0.6_main.uab
ll-cli info org.deepin.deepin-color-correction
ll-cli run org.deepin.deepin-color-correction
```

## When not to use this skill

Do not use this skill:

- to re-design the package layout from zero
- to switch base/runtime families casually
- to replace the in-repo manifest with a generic auto-generated one

This skill exists specifically to preserve the already-converged packaging path.
