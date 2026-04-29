# Registry Contract

## 1. Registry purpose

This repository is the canonical source for shared AI resources.

Resource types:

- `skill`
- `script`
- `wrapper`
- `pack`
- `addon`
- `reference`

This repository is **not** a promise that every Agent supports the same local installation format.
It is also **not** a promise that every indexed resource should be installed by default.

## 2. Required execution order

When asked to configure, update, or validate local resources, follow this order:

1. Detect the current Agent type
2. Detect the current OS
3. Read `manifest.json`
4. Read `adapters/<agent-id>/adapter.yaml`
5. Select the target `pack`
6. Evaluate each item's `policy`
7. Materialize only the items supported by that adapter and policy
8. Validate results
9. Output a summary

## 3. Detecting the current Agent

Use the best available evidence:

- current CLI name
- current runtime metadata
- current instruction file conventions
- explicit user statement

If the current Agent type is unknown:

- stop
- report `blocked`
- do not guess a random adapter

## 4. Adapter-first rule

Never install directly from canonical paths unless the adapter explicitly says so.

Correct flow:

`manifest.json -> adapter.yaml -> policy -> local materialization`

Incorrect flow:

`manifest.json -> copy files to a guessed location`

## 5. Supported outcomes

Per item, one of:

- `installed`
- `updated`
- `already-current`
- `skipped-unsupported`
- `skipped-missing-dependency`
- `blocked`

## 6. Resource policy roles

Each resource may define a policy role.

Supported roles:

- `baseline`
- `dependency`
- `reference`
- `optional`

Interpretation:

- `baseline`: install proactively when the current Agent and OS match
- `dependency`: install or validate only when another item requires it
- `reference`: do not auto-install; only surface it as a relevant upstream resource
- `optional`: available to install, but not required

## 7. Action on missing

Each resource may define `action_on_missing`.

Supported actions:

- `install`
- `block`
- `suggest`
- `ignore`

Recommended behavior:

- `baseline` usually pairs with `install`
- `dependency` usually pairs with `install` or `block`
- `reference` usually pairs with `suggest`

## 6. Safety rules

- Do not overwrite user-owned config files
- Do not delete unknown files
- Use namespaced managed paths where possible
- If a host file must reference managed content, make the change minimal, reversible, and identifiable
- If you cannot safely merge, stop and report

## 8. Health checks

When asked to validate local state:

- check that the current Agent has a matching adapter
- check that required CLI dependencies exist
- check that target files exist
- check that managed files do not conflict with user files
- check that installed versions match or exceed the local pinned state
- if an item is `reference` only, do not fail health because it is not installed

## 9. Prompt-first, helper-optional

The preferred entrypoint is a prompt or repository URL.

If the current Agent lacks the necessary combination of:

- network access
- filesystem write access
- shell execution

then a helper script or minimal manual step is allowed as a fallback.

Fallback must be clearly reported, not hidden.

## 10. What not to do

- Do not assume all Agents support `AGENTS.md`
- Do not assume all Agents support `SKILL.md`
- Do not assume all Agents share one skill directory layout
- Do not store shared plaintext credentials in local state files
- Do not mark experimental support as production-ready without real validation
- Do not auto-install `reference` items
- Do not treat every indexed upstream as a mandatory baseline
