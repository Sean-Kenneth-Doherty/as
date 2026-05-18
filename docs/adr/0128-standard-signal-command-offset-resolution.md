# ADR-0128: Standard-Signal Command Offset Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

The standard-signal command-token frontier still lists
`command-table-offset` as an unresolved question. That was useful while AS was
only recording source divergence: the PRC formal model lists
`standard-signal` as command offset `0`, while RAA's legacy buffer table maps
its final case to `standard-signal`.

AS has already made the command-buffer ordering explicit in
`sources/stem_command_buffer_map.json`, and
`autarkic_systems.stem_command_map` validates the canonical PRC map:
`standard-signal` is offset `0` in every target range. That decision is now
checked by tests and consumed by later self/neighbor command-buffer evidence.

Leaving `command-table-offset` in the unresolved queue makes project status
less truthful: this offset question is no longer open in AS, even though the
runtime semantics of the `standard-signal` command token remain blocked.

## Decision

Resolve the standard-signal `command-table-offset` question in favor of the
formal PRC command-buffer map already encoded by ADR-0026. Record this in
`sources/standard_signal_command_semantics_status.json` as a resolved
resolution question pointing at `sources/stem_command_buffer_map.json`, and
remove `command-table-offset` from the `required_resolution_questions` list.

This ADR does not implement `standard-signal` command-token execution. The
remaining blockers are:

- whether a command token reproduces ordinary binary-input standard-signal
  behavior or remains separate;
- whether delivered recipient command-message inputs may execute
  `standard-signal`; and
- what self-mailbox and self-target command-buffer command tokens should do.

Project status JSON remains `schema_version: 8`.

## Success Criteria

- Red tests fail before implementation because `command-table-offset` still
  appears in the unresolved standard-signal question list and no resolved
  offset decision is recorded.
- Tests verify the resolved offset decision points at
  `sources/stem_command_buffer_map.json`.
- Tests verify the stem command-buffer map still decodes offset `0` as
  `standard-signal`.
- Project status no longer reports `command-table-offset` as an unresolved
  standard-signal question.
- Project status remains accepted at `schema_version: 8`.
- Full repository tests remain green.

## Consequences

The standard-signal blocker queue becomes sharper: AS keeps formal command
offset `0` and stops presenting RAA's offset-7 divergence as an open choice.
The actual execution semantics remain blocked.

## Test Plan

- Red: run standard-signal and project-status tests after adding assertions for
  the resolved offset decision and the reduced unresolved question list.
- Green: update the standard-signal source-status JSON and human-facing note.
- Regression: run stem command map, standard-signal, project-status, and full
  default tests before commit.

## After Action Report

Implemented in `sources/standard_signal_command_semantics_status.json` and
`docs/standard-signal-command-semantics-status.md` by adding a
`resolved_resolution_questions` entry for `command-table-offset` and removing
that question from the unresolved `required_resolution_questions` list.

The decision preserves the formal PRC command-buffer map already encoded by
ADR-0026: `sources/stem_command_buffer_map.json` records
`standard-signal` at offset `0`, and `autarkic_systems.stem_command_map`
continues to validate and decode that ordering. RAA's offset-7 divergence
remains recorded as legacy evidence, but not as an open AS choice.

Runtime behavior remains unchanged. `standard-signal` command-token execution
is still blocked pending the command-token/binary-input, recipient-surface, and
self-target-surface decisions.

The red focused run executed 50 tests and failed because
`resolved_resolution_questions` was absent and project status still reported
`command-table-offset` as unresolved. The green focused run passed 50
standard-signal and project-status tests after implementation.

Regression verification passed: standard-signal, project-status, and stem
command-buffer map tests ran 58 tests; `python -m json.tool` accepted the
updated standard-signal source-status JSON; `py_compile` and `git diff --check`
passed; default project status text no longer listed `command-table-offset`;
project status JSON remained accepted at `schema_version: 8`; and
`python -m unittest discover` passed 589 tests.
