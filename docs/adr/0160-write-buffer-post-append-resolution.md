# ADR-0160: Write-Buffer Post-Append Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0159 leaves one live write-buffer source-status question:
`post-append-clearing`.

The remaining source disagreement is about what state is cleared after a
write-buffer command appends its literal bit:

- RAA dispatches `write-buf-zero` and `write-buf-one` to `write-buf`, appends
  when the buffer is not full, and then clears the active input/output
  channels in the surrounding input-processing path.
- FSMSIM appends the literal bit and clears `smb` plus input channels.
- SEMSIM appends the literal bit but then wraps the operation in `zero-hig` and
  `zero-buf`, erasing the appended buffer.
- The formal model's standard-signal write-to-buffer rule clears input and
  preserves control/buffer state after `write-buf`; its special-message rule
  preserves `hig` and clears the self-mailbox command source, but does not
  define a full named write-buffer primitive.

## Decision

Resolve `post-append-clearing` as:
`preserve-appended-buffer-clear-command-source`.

AS will treat a write-buffer command token as source-ready to implement when
the command source is cleared and the appended literal bit remains in the stem
buffer. This selects the RAA/FSMSIM buffer-preservation side, aligns with the
formal model's write-to-buffer preservation of buffer/control state, and
records SEMSIM's buffer-clearing wrapper as legacy divergence.

This is a source-status resolution only. It does not implement write-buffer
command execution or change Universal Cell runtime behavior.

## Consequences

The write-buffer source-status record has no live
`required_resolution_questions`.

`execution_readiness` changes to `ready`, with
`execution_change_allowed: true` and no blockers.

The next safe executable slice is to implement direct self-mailbox and
self-target command-buffer write-buffer append behavior from this resolved
source boundary.

Project-status remains schema 15, and source-status frontier remains schema 2.

## Verification Plan

- Red: add focused source-status tests proving `post-append-clearing` is
  resolved, no write-buffer unresolved questions remain, and write-buffer
  execution readiness is ready.
- Green: update the write-buffer source-status artifact and documentation.
- Regression: run focused write-buffer/status tests, both status CLIs in JSON
  mode, `py_compile`, `git diff --check`, and the full unittest suite.

## After Action Report

Implemented.

Added red write-buffer, project-status, and source-status frontier tests before
changing the source artifact. The focused red run executed 99 tests and failed
because `post-append-clearing` was still live, absent from resolved questions,
and still blocked execution readiness.

Updated `sources/write_buffer_command_semantics_status.json` so
`post-append-clearing` resolves to
`preserve-appended-buffer-clear-command-source`, with RAA/FSMSIM buffer
preservation selected and SEMSIM's buffer-clearing wrapper recorded as legacy
divergence. The write-buffer source-status record now has no live
`required_resolution_questions`, no unresolved evidence entries, and ready
execution-readiness for a later implementation ADR.

Verification passed:

- focused ADR-0160 status tests: 99 tests;
- adjacent multi-command/status focused tests: 103 tests;
- write-buffer JSON parse;
- source-status JSON schema 2 with write-buffer ready;
- project-status JSON schema 15 with write-buffer ready;
- `py_compile`;
- `git diff --check`; and
- full unittest discovery: 676 tests.

Universal Cell runtime behavior did not change.
