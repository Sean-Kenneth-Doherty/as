# ADR-0053: Recipient Non-Init Command Source Status

Date: 2026-05-17

Status: Accepted

## Context

ADR-0049 through ADR-0052 completed the recipient-side init-family
command-message ladder: executable behavior, named claim, schematic-linked
trace, and rendered SVG. The remaining recipient command-message inputs are
`standard-signal`, `write-buf-zero`, `write-buf-one`, and simultaneous
multi-command inputs.

ADR-0048 recorded these as blockers. Before AS either executes or claims their
current rejection boundary, the source status should be explicit and
machine-checkable.

## Decision

Add a structured source-status artifact for recipient non-init command-message
inputs:

- add `sources/recipient_non_init_command_source_status.json`;
- record that `standard-signal` remains unresolved because the formal command
  table includes it while the legacy special-message sets exclude it;
- record that write-buffer command-message inputs remain unresolved because
  legacy sketches disagree about buffer clearing, input clearing, and
  buffer-full behavior;
- record that multi-command input policy remains unresolved;
- move the safe next slice to a named claim for the current rejection boundary,
  not runtime execution.

This is a source-status decision only. It does not change Universal Cell
runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `sources/recipient_non_init_command_source_status.json` is absent.
- The artifact records the formal command-table and input-special-message
  witnesses.
- The artifact records the legacy exclusion of `standard-signal` from special
  messages.
- The artifact records divergent write-buffer behavior across RAA, SEMSIM, and
  FSMSIM witnesses.
- The artifact blocks runtime execution for `standard-signal`, write-buffer,
  and multi-command inputs.
- The stem and recipient source-status frontiers move to a named rejection
  boundary claim rather than implementation.

## Consequences

- AS avoids smuggling unresolved non-init semantics into the transition probe.
- The next safe runtime-adjacent slice is to claim the current rejection
  boundary for non-init recipient command-message inputs.
- Actual `standard-signal` and write-buffer execution still requires a later
  semantics decision.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_recipient_non_init_command_source_status`
failed because `sources/recipient_non_init_command_source_status.json` was
absent.

The green implementation added the structured source-status artifact, recorded
the standard-signal and write-buffer blockers, and moved the safe next slice to
a named rejection-boundary claim.

Final verification is recorded in `LOG.md`.
