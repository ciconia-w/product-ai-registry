# Registry Contract

## 1. Registry purpose

This repository is the canonical source for shared AI resources.

Resource types:

- `skill`
- `script`
- `wrapper`
- `pack`

This repository is **not** a promise that every Agent supports the same local installation format.

## 2. Required execution order

When asked to configure, update, or validate local resources, follow this order:

1. Detect the current Agent type
2. Detect the current OS
3. Read `manifest.json`
4. Read `adapters/<agent-id>/adapter.yaml`
5. Select the target `pack`
6. Materialize only the items supported by that adapter
7. Validate results
8. Output a summary

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

`manifest.json -> adapter.yaml -> local materialization`

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

## 6. Safety rules

- Do not overwrite user-owned config files
- Do not delete unknown files
- Use namespaced managed paths where possible
- If a host file must reference managed content, make the change minimal, reversible, and identifiable
- If you cannot safely merge, stop and report

## 7. Health checks

When asked to validate local state:

- check that the current Agent has a matching adapter
- check that required CLI dependencies exist
- check that target files exist
- check that managed files do not conflict with user files
- check that installed versions match or exceed the local pinned state

## 8. Prompt-first, helper-optional

The preferred entrypoint is a prompt or repository URL.

If the current Agent lacks the necessary combination of:

- network access
- filesystem write access
- shell execution

then a helper script or minimal manual step is allowed as a fallback.

Fallback must be clearly reported, not hidden.

## 9. What not to do

- Do not assume all Agents support `AGENTS.md`
- Do not assume all Agents support `SKILL.md`
- Do not assume all Agents share one skill directory layout
- Do not store shared plaintext credentials in local state files
- Do not mark experimental support as production-ready without real validation
