# Registry Schemas

This document defines the schema files used by the registry.

## Included schemas

- `schemas/manifest.schema.json`
- `schemas/tool.schema.json`
- `schemas/adapter.schema.json`
- `schemas/pack.schema.json`
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
