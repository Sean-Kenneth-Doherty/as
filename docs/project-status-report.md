# Project Status Report

ADR-0096 adds `autarkic_systems/project_status.py`, a compact status report
over the current executable evidence surface and blocked command-token
frontier.

## Purpose

AS now has separate commands for transition evidence bundles, composed-chain
evidence bundles, and chain demo reports. Those surfaces are useful, but they
do not by themselves answer the operator question:

What is green now, and what remains blocked?

The project status report answers that by reusing existing validators and
source-status records.

## Run

```sh
python -m autarkic_systems.project_status
python -m autarkic_systems.project_status --format json
```

The report validates:

- `evidence/manifest.json`, the transition evidence registry;
- `evidence/chains/manifest.json`, the transition-chain evidence registry;
- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The text report names:

- overall accepted or rejected status;
- transition evidence accepted or rejected state and bundle count;
- chain evidence accepted or rejected state and bundle count;
- blocked command tokens; and
- the safe next slice from the source-status records.

JSON mode emits the same surface for automation. If a registry file or
source-status file is missing or invalid, the command returns structured
rejected output instead of a traceback.

## Boundary

This is not a simulator, proof checker, registry replacement, or source-status
authority. It delegates registry validation to the existing validators and
reads the current source-status records only to summarize the blocked
command-token frontier.
