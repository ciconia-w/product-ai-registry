# Project-Scoped Materialization

Some capabilities must not be installed into a user-global Agent directory.

Examples:

- repo-specific build scripts
- repo-specific skills
- repository-local wrappers

The Linglong deepin-color-correction assets are the first concrete example.

## Rules

1. If a capability uses repository-relative paths such as `scripts/` or depends on repository-local build files, it must be marked `install_scope: project`.
2. Project-scoped capabilities must declare `target_path` or `target_path_hint`.
3. Adapters must materialize them inside the target repository, not into a generic home-directory skill bucket.
4. Project-scoped installation must not overwrite unrelated repository files without explicit ownership and validation.

## Supported project-scoped modes

- `project_native_skill_dir`
- `project_generated_subagent`
- `project_generated_rules`
- `project_local_copy`

## Non-goal

This document does not yet define the final installer implementation. It defines the contract that implementation must follow.
