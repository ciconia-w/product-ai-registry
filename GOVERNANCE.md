# Governance

## Repository intent

This repository governs shared AI resources for the team.

It is a controlled registry, not a free-form prompt dump.

## Support levels

- `A`: officially documented or strongly validated on target machines
- `B`: adapter-based support, usable but not fully native
- `C`: experimental, do not present as production-ready

## High-risk paths

Changes to these areas require extra scrutiny:

- `manifest.json`
- `REGISTRY.md`
- `AGENTS.md`
- `adapters/**`
- `packs/**`
- `.github/**`
- `GOVERNANCE.md`
- `CONTRIBUTING.md`

## Approval policy

- all changes merge by PR only
- high-risk paths require code owner review
- support-level upgrades require explicit review
- CI must pass before merge

## Required evidence

The following changes require validation notes in the PR:

- adding a new Agent adapter
- changing local materialization mode
- changing pack composition
- changing dependency or install assumptions
- promoting an adapter from experimental to supported

## Default safety stance

If safe installation cannot be guaranteed:

- stop
- report the blocker
- do not guess

## Semantic changes

If a PR changes resource semantics, it must update both machine-readable and human-readable layers:

- manifest and schemas
- README
- relevant docs under docs/
- addon or reference install guidance when upstream behavior changes

