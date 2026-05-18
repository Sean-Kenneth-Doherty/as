# ADR-0161: Write-Buffer Command Execution

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0160 resolves the final write-buffer source-status blocker:
`post-append-clearing`. The selected rule is
`preserve-appended-buffer-clear-command-source`.

The next executable slice can now move the two source-resolved write-buffer
command tokens out of the old unsupported boundaries:

- direct stem `self_mailbox` commands `write-buf-zero` and `write-buf-one`;
- completed self-target command buffers decoding to `write-buf-zero` and
  `write-buf-one`.

Recipient write-buffer command-message inputs remain under the existing
recipient non-init rejection boundary. Neighbor-target command buffers still
deliver the decoded command token to the output channel for the neighbor to
consume or reject.

## Decision

Implement direct self-mailbox and completed self-target command-buffer
write-buffer execution.

For direct self-mailbox commands, AS appends literal `0` or `1` to the current
stem buffer when the buffer is not full, clears `self_mailbox`, preserves the
stem role, memory, upstream, output, and control rail, and returns a dedicated
write-buffer status.

For completed self-target command buffers, AS treats the completed five-bit
buffer as the command source, clears that source, appends the literal command
bit as the new buffer content, preserves the control rail, and returns a
dedicated self-command-buffer write-buffer status.

AS preserves the existing full-buffer boundary for direct self-mailbox
write-buffer commands: a full target buffer does not append and the cell is
reported as `stem-buffer-full`.

## Consequences

The unsupported self-mailbox and self-target command-buffer claims narrow to
`standard-signal` only. Write-buffer behavior moves to new explicit transition
claims and proof-certificate examples.

The write-buffer source-status record no longer lists self-mailbox or
self-target command-buffer as blocked runtime surfaces. Recipient-side
write-buffer command messages remain rejected by the recipient non-init
boundary.

This does not implement `standard-signal` command-token execution, neighbor
write-buffer consumption, or recipient non-init write-buffer command-message
execution.

## Verification Plan

- Red: add runtime tests for direct and self-target command-buffer
  write-buffer append behavior, and update unsupported-boundary tests to prove
  write-buffer is no longer covered there.
- Green: implement the Universal Cell behavior, new predicates, claim/proof
  examples, language vocabulary, and adjusted status/evidence artifacts.
- Regression: run the focused write-buffer/unsupported/status tests, evidence
  registry validation, project/source status JSON checks, `py_compile`,
  `git diff --check`, and the full unittest suite.

## After Action Report

Implemented. The red focused suite failed before runtime support because
write-buffer commands still used the old unsupported boundaries and the new
statuses, predicates, claim examples, and language vocabulary were absent.

The implementation adds direct self-mailbox and completed self-target
command-buffer write-buffer append behavior, adds explicit write-buffer
transition claims/proof certificates, narrows the old unsupported artifacts to
`standard-signal`, and updates source/project status to mark the write-buffer
self-target surfaces implemented while recipient command-message input remains
rejected.

Verification passed:

- focused runtime/claim/status/evidence suites;
- transition claim manifest, proof certificates, base and chain object
  languages;
- transition and chain evidence registries;
- source-status and project-status CLIs;
- `python -m compileall -q autarkic_systems tests`;
- `git diff --check`;
- `python -m unittest discover` ran 687 tests.
