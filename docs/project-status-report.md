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

JSON mode emits the same surface for automation and includes top-level
`schema_version: 2`. If a registry file is missing, the corresponding registry
summary reports `registry-file`; if a registry file is present but malformed,
it reports `registry-json`. Missing or invalid source-status files are also
reported as structured rejected output instead of a traceback. ADR-0099 adds
`frontier.failed_subjects`, which reports `source-status-file` for missing
source-status files and `source-status-json` for malformed source-status
files. ADR-0100 adds `source-status-schema` for source-status JSON that parses
but is not a usable source-status object. ADR-0101 adds the schema version.
ADR-0102 requires accepted source-status records to expose at least one
blocked command token through `command`, `commands`, or
`blocked_runtime_commands`. ADR-0103 adds those extracted commands to each
accepted `frontier.source_statuses` entry and bumps the schema version to `2`.
ADR-0104 rejects blank command-token strings as `source-status-schema`
failures. ADR-0105 rejects whitespace-only `decision` and `safe_next_slice`
text as source-status schema failures.

## Boundary

This is not a simulator, proof checker, registry replacement, or source-status
authority. It delegates registry validation to the existing validators and
reads the current source-status records only to summarize the blocked
command-token frontier.
