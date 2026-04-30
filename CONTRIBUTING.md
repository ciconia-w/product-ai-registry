# Contributing

## Branch rules

- `main`: protected, merge by PR only
- `beta`: optional pre-release validation
- feature branches:
  - `feat/<scope>`
  - `fix/<scope>`
  - `chore/<scope>`

## PR scope

One PR should cover one concern:

- one capability
- one adapter change
- one pack change
- one governance or CI change

Do not mix unrelated work.

## Required updates

If you change a capability or pack, update all relevant files:

- resource files
- `manifest.json`
- `CHANGELOG.md`
- `README.md` when user-facing behavior changed
- `docs/01-product-spec.md`, `docs/02-architecture-design.md`, and `docs/03-registry-schemas.md` when semantics changed
- addon or reference metadata when source, install commands, or policy changed

If you change an adapter:

- update `adapters/<agent-id>/adapter.yaml`
- update any related templates
- describe compatibility impact in the PR

## Verification rules

Before opening a PR:

- `manifest.json` must be valid JSON
- all `pack` references must point to existing items
- every `skill` must have `SKILL.md`
- every `script` and `wrapper` must have `tool.yaml`
- high-risk changes must include validation notes

## Support-level changes

You may not change support level casually.

- `C -> B` requires real validation evidence
- `B -> A` requires stronger validation and owner review

## Agent maintainer rules

If you are an Agent maintaining this repository:

- work only on a feature branch
- do not push directly to `main`
- do not bypass CI
- if a compatibility fact is uncertain, downgrade the claim instead of asserting support

