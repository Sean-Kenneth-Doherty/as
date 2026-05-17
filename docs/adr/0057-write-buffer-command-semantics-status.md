# ADR-0057: Write-Buffer Command Semantics Status

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0053 left recipient-side `write-buf-zero` and `write-buf-one`
command-message execution blocked because the restored PRC sources did not
agree on one complete write-buffer boundary. ADR-0054 through ADR-0056 then
claimed, traced, and rendered the current rejection boundary rather than
executing those commands.

The next safe frontier is to decide whether AS can now implement write-buffer
command execution or must keep it blocked with better evidence.

## Decision

Add a structured write-buffer command semantics status artifact:

- `sources/write_buffer_command_semantics_status.json`;
- formal-model anchors for the command table, input special-message path, and
  self-mailbox special-message path;
- RAA, SEMSIM, and FSMSIM write-buffer witnesses;
- an explicit `do-not-implement-write-buffer-command-execution-yet` decision;
- updates to the recipient and stem source-status frontiers.

This ADR does not change Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `sources/write_buffer_command_semantics_status.json` is absent.
- The artifact records that the formal model names write-buffer commands but
  does not define an executable write-buffer primitive.
- The artifact records that RAA appends with a buffer-full guard and clears
  input channels through input-processing flow.
- The artifact records that SEMSIM appends and then clears the buffer in its
  stem special-message wrapper.
- The artifact records that FSMSIM appends and clears self-mailbox/input state
  without a matching buffer-full guard.
- The artifact blocks runtime execution for recipient command messages,
  self-mailbox commands, and self-target command-buffer commands.
- Existing source-status frontiers move away from write-buffer execution and
  toward `standard-signal` / multi-command resolution.

## Consequences

AS gains a sharper source-status record for the write-buffer blocker without
laundering contradictory legacy sketches into runtime behavior. The next
non-init frontier becomes `standard-signal` command-message divergence and
multi-command conflict policy.

## After Action Report

Implemented in `sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md`.

The focused red run failed because
`sources/write_buffer_command_semantics_status.json` was absent. The green
implementation records the formal-model gap, RAA/SEMSIM/FSMSIM write-buffer
witness divergence, required resolution questions, and updated source-status
frontiers that move the next safe slice to `standard-signal` source
resolution.
