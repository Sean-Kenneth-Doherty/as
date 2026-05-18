# ADR-0168: Recipient Write-Buffer Surface Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0167 made `recipient-command-message-surface` the live write-buffer
source-status question. The question asks whether delivered recipient
`write-buf-zero` and `write-buf-one` command messages should remain in the
recipient non-init rejection boundary or become executable append behavior.

The source pressure now points one way:

- the formal model routes input-channel special messages on wire, proc, and
  stem cells through `process-special-message`;
- RAA dispatches `write-buf-zero` and `write-buf-one` to literal append
  behavior and clears input-channel state in the surrounding input processor;
- FSMSIM selects input-channel special messages and dispatches write-buffer
  commands to literal append behavior while clearing command-source channels;
- SEMSIM agrees that the named commands append literal bits, but its stem
  wrapper still clears the buffer after append, which AS already records as
  divergent legacy behavior in ADR-0160.

The AS runtime still rejects delivered recipient write-buffer command messages
under the ADR-0054/ADR-0163 recipient non-init rejection evidence. That checked
runtime boundary should remain in place until a later implementation ADR
changes the Universal Cell transition behavior, claim coverage, traces, and
evidence bundles.

## Decision

Resolve `recipient-command-message-surface` as:
`execute-recipient-write-buffer-command-message-append`.

AS treats delivered recipient `write-buf-zero` and `write-buf-one` command
messages as source-ready for append execution. This selects the formal,
RAA, and FSMSIM input-channel special-message path and preserves ADR-0160's
SEMSIM divergence record.

This ADR is source-status only. It removes the live write-buffer recipient
question, marks write-buffer execution changes as source-ready, and changes
the safe next slice to implementation of recipient write-buffer command-message
execution. It does not change Universal Cell runtime behavior, transition
claims, proof certificates, traces, SVGs, evidence bundles, or schema versions.

## Success Criteria

- Red tests fail before source-status updates because write-buffer source
  status still lists `recipient-command-message-surface` as unresolved and
  blocks execution readiness.
- Write-buffer source status resolves `recipient-command-message-surface` to
  recipient append execution.
- Write-buffer source status has no live `required_resolution_questions` or
  unresolved evidence entries.
- Project-status and source-status frontier JSON/text expose source-ready
  write-buffer readiness, no recipient write-buffer live question, and the
  implementation safe-next slice.
- Recipient-facing source-status records still say current runtime rejects
  delivered recipient write-buffer command messages until the implementation
  ADR changes the checked boundary.
- Runtime behavior remains unchanged.

## Test Plan

- Red:
  `python -m unittest tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli tests.test_recipient_non_init_command_source_status tests.test_recipient_command_consumption_source_status tests.test_multi_command_recipient_input_policy_status`
  fails before source-status records are updated.
- Green: the same focused suite passes after updating source-status records
  and expected JSON/text surfaces.
- Regression: run project-status JSON, source-status JSON, JSON parsing for
  touched source-status files, `compileall`, `git diff --check`, and the full
  default suite before commit.

## After Action Report

Implemented.

Added red write-buffer, project-status, source-status frontier, recipient
non-init, recipient command-consumption, multi-command, and standard-signal
frontier tests before changing source-status records. The focused red run
executed 126 tests and failed because the write-buffer source-status record
still listed `recipient-command-message-surface` as unresolved, blocked
recipient execution readiness, preserved the old recipient rejection decision,
and pointed safe-next guidance at semantics rather than implementation.

Updated `sources/write_buffer_command_semantics_status.json` so
`recipient-command-message-surface` resolves to
`execute-recipient-write-buffer-command-message-append`. The write-buffer
record now has no live `required_resolution_questions`, no unresolved evidence
entries, and `execution_readiness.decision:
recipient-command-message-source-ready` with execution changes allowed and no
blockers.

Updated recipient-facing source-status records to preserve the checked current
runtime rejection boundary while moving safe-next guidance to recipient
write-buffer command-message implementation. No Universal Cell runtime,
transition claims, proof certificates, traces, SVGs, evidence bundles, or
schema versions changed.

Verification passed:

- focused ADR-0168 source/status suite: 137 tests;
- touched source-status JSON parse;
- project-status JSON accepted schema `15` and reported source-ready
  write-buffer readiness;
- source-status JSON accepted schema `2` with no live resolution questions;
- `python -m compileall -q autarkic_systems tests`;
- `git diff --check`; and
- full unittest discovery: 733 tests.
