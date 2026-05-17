# ADR-0048: Recipient Command Consumption Source Status

Date: 2026-05-17

Status: Accepted

## Context

ADR-0044 through ADR-0047 deliver neighbor-target command buffers onto output
channels and give that behavior claim, trace, and SVG evidence. The remaining
neighbor-side question is what recipient cells should do when those command
tokens arrive as input-channel special messages.

The source-status artifact currently says recipient-side command-message
consumption must be promoted into a source-status decision before AS executes
delivered neighbor commands. The PRC source cache has been restored at the
pinned PRC commit, so AS can now record the relevant witnesses without
implementing execution yet.

## Decision

Add a structured recipient command-consumption source-status artifact:

- add `sources/recipient_command_consumption_source_status.json`;
- add tests that record the formal model's input-channel special-message
  process path;
- add tests that record legacy RAA/FSM/Sem simulator support for init-family
  and write-buffer special messages;
- record that `standard-signal` remains excluded from the legacy
  special-message set and therefore remains unresolved as a command-message
  input;
- update the stem command execution source-status next-slice list so the next
  implementation can target recipient-side init-family command-message
  consumption rather than the source-status decision itself.

This is a source-status decision only. It does not change Universal Cell
runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `sources/recipient_command_consumption_source_status.json` is absent.
- The artifact records the formal process-special-message input-channel anchor.
- The artifact records the legacy special-message sets and primitive operation
  witnesses.
- The artifact permits recipient-side init-family command-message consumption
  as the next executable slice.
- The artifact keeps `standard-signal` command-message consumption and
  write-buffer semantics out of the next executable slice.
- The existing stem command execution source-status artifact points to the new
  next slice instead of asking for this source-status decision again.

## Consequences

- AS can move from neighbor delivery evidence toward recipient-side command
  consumption without guessing from the delivered-token tests alone.
- Init-family command-message inputs have a source-backed path to
  implementation.
- `standard-signal` and write-buffer command-message inputs remain blocked
  until their divergent or incomplete semantics are resolved.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_recipient_command_consumption_source_status`
failed because `sources/recipient_command_consumption_source_status.json` was
absent.

The PRC source cache was restored at
`/home/sean/Projects/_upstream/prc` on commit
`7e82c73fac8f108faac801a5c65e2c2b92653ba5`, matching the manifest-pinned PRC
snapshot. Source inspection confirmed the formal model's input-channel
`process-special-message` path and the legacy seven-message special-message
sets.

The green implementation added the structured recipient command-consumption
source-status artifact, its human-facing note, and tests that keep
`standard-signal`, write-buffer, and multi-command input policy outside the
next executable slice. The stem command execution source-status artifact now
points to recipient-side init-family command-message consumption as the next
runtime slice.

Final verification is recorded in `LOG.md`.
