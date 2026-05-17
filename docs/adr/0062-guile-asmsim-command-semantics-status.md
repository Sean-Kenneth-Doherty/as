# ADR-0062: Guile ASMSIM Command Semantics Status

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0061 completed the current multi-command rejection evidence ladder and
returned the command-execution frontier to source resolution for
`standard-signal` and write-buffer command semantics.

The local PRC source tree contains another relevant simulator witness:
`practice/legacy/guile-asmsim.scm`. It has a compact Universal Cell abstract
state machine with command-buffer, self-mailbox, special-message, and buffer
append code. Before AS uses it to widen runtime behavior, the witness needs a
source-status record because it appears to diverge from both the formal command
table and the older RAA/SEMSIM/FSMSIM sketches.

## Decision

Add `sources/guile_asmsim_command_semantics_status.json` and a human-facing
note that record the command-semantics evidence in `guile-asmsim.scm`.

This ADR will record:

- the init-family-only `special-messages` list;
- the exclusion of `standard-signal`, `write-buf-zero`, and `write-buf-one`
  from that list;
- the binary-input `write-buf` helper;
- the self-mailbox numeric append path for `0` and `1`;
- the command-buffer list expression that appends `special-messages` and
  `standard-signals`;
- the conclusion that this witness strengthens the source blocker instead of
  unlocking runtime execution.

This ADR does not change Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `sources/guile_asmsim_command_semantics_status.json` is absent.
- The source-status artifact records the relevant local witness path and loci.
- Tests verify that `guile-asmsim.scm` names only init-family special messages.
- Tests verify that write-buffer evidence is numeric/binary rather than named
  `write-buf-zero` / `write-buf-one` command tokens.
- Tests verify that the existing standard-signal, write-buffer, and stem
  command source-status files reference this ADR-0062 evidence.
- Runtime behavior remains unchanged.

## Consequences

`guile-asmsim.scm` is useful as evidence, but not as executable authority for
the unresolved command semantics. It increases confidence that AS should keep
`standard-signal` and write-buffer command execution blocked until a later ADR
chooses a source-backed representation and clearing boundary.

## Test Plan

- Red: `python -m unittest tests.test_guile_asmsim_command_semantics_status`
  fails because the source-status artifact is absent.
- Green: the same focused test passes after adding the artifact and
  cross-links.
- Regression: run adjacent command source-status tests and the full default
  suite before commit.

## After Action Report

Implemented in `sources/guile_asmsim_command_semantics_status.json` and
`docs/guile-asmsim-command-semantics-status.md`.

The focused red run failed because
`sources/guile_asmsim_command_semantics_status.json` was absent. The green
implementation records `guile-asmsim.scm` as command-semantics evidence, but
not execution authority: it names only init-family special messages, omits
named write-buffer commands, appends binary/numeric `0`/`1` values, and uses a
command-list expression that diverges from the formal named command table.

Existing standard-signal, write-buffer, and stem command source-status
artifacts now cross-link this evidence. Runtime behavior remains unchanged.
