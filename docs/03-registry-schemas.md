# Registry Schemas

This document defines the schema files used by the registry.

## Included schemas

- `schemas/manifest.schema.json`
- `schemas/tool.schema.json`
- `schemas/adapter.schema.json`
- `schemas/pack.schema.json`
- `schemas/addon.schema.json`
- `schemas/reference.schema.json`
- `schemas/installed.schema.json`
- `schemas/health-report.schema.json`

## Intent

These schemas are part of the repository skeleton so that future Agents do not need to invent structure while implementing:

- validation
- install helpers
- CI checks
- local state handling

## Rules

- `manifest.json` is the source of capability indexing
- `tool.yaml` applies to both `script` and `wrapper`
- `adapter.yaml` defines per-Agent materialization strategy
- local state files must stay separate from the canonical registry

## Resource roles

Every indexed resource can also carry a policy role.

Recommended roles:

- `baseline`
- `dependency`
- `reference`
- `optional`

These roles answer a different question than `type`.

- `type` answers: what kind of thing is this
- `role` answers: how should an Agent treat it during install and update

Examples:

- `superpowers` -> likely `addon + baseline`
- `oh-my-codex` -> likely `addon + baseline`
- `oh-my-claudecode` -> likely `addon + baseline`
- `opencli` -> likely `addon + dependency`
- `RAG-Anything` -> likely `reference + suggest`

## Suggested metadata additions

To support this behavior, registry items should be allowed to define:

- `source`
- `policy`
- `requires.items`

### source

Example:

```json
{
  "kind": "external_git",
  "url": "https://github.com/HKUDS/RAG-Anything",
  "ref": "main"
}
```

Supported `source.kind` values:

- `local`
- `external_git`
- `external_release`
- `external_package`
- `reference`

### policy

Example:

```json
{
  "role": "baseline",
  "action_on_missing": "install"
}
```

Supported `policy.role` values:

- `baseline`
- `dependency`
- `reference`
- `optional`

Supported `policy.action_on_missing` values:

- `install`
- `block`
- `suggest`
- `ignore`

### requires.items

Use this when one registry item depends on another registry item.

Example:

```json
{
  "requires": {
    "items": ["addon:opencli"]
  }
}
```
