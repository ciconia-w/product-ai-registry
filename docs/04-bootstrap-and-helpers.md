# Bootstrap and Helpers

This repository supports a prompt-first workflow, but that is not enough for every Agent and environment.

## Helper scripts included in the skeleton

- `scripts/bootstrap/doctor-registry-env.sh`
- `scripts/bootstrap/sync-registry-pack.sh`
- `scripts/bootstrap/install-project-capability.sh`
- `scripts/bootstrap/install-agent-capability.sh`

## Purpose

These are not complete installers yet.

They exist so future implementation work has fixed entrypoints for:

- doctor
- sync
- project-scoped materialization
- agent-scoped materialization

## Why this matters

Different Agents have different capabilities:

- some can read GitHub and write files
- some can read but not safely install
- some work best with helper scripts

These helpers are the minimal skeleton for a fallback path without forcing the entire system to become helper-first.
