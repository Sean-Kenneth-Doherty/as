# ADR-0153: Write-Buffer Self-Target Surface Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0152 narrowed the write-buffer surface question by moving delivered
recipient `write-buf-zero` and `write-buf-one` command messages into the
existing recipient non-init rejection boundary.

The remaining `self-target-surface` question asks whether self-mailbox and
self-target command-buffer write-buffer command tokens execute, or remain
unsupported. AS already has two checked unsupported boundaries that cover
write-buffer command tokens:

- `UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED` preserves direct self-mailbox
  `write-buf-zero` and `write-buf-one` command tokens as unsupported.
- `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED` preserves completed self-target
  command-buffer `write-buf-zero` and `write-buf-one` command tokens at the
  append boundary.

Those boundaries do not implement write-buffer execution. The reviewed sources
still disagree on buffer-full behavior and post-append clearing.

## Decision

Move `self-target-surface` from unresolved to resolved in
`sources/write_buffer_command_semantics_status.json`.

The resolved decision is:

`preserve-self-target-write-buffer-as-unsupported`

This ADR does not implement write-buffer command execution. It keeps
`buffer-full-boundary` and `post-append-clearing` unresolved.

## Consequences

The write-buffer source-status frontier should still list write-buffer command
tokens as blocked, but the open questions should now be limited to the two
execution semantics conflicts: buffer-full handling and post-append clearing.

Future write-buffer execution work must replace the unsupported-preservation
boundary intentionally and select source-backed append, full-buffer, and
clearing semantics.

## Verification Plan

- Red: update write-buffer, project-status, and source-status frontier tests to
  expect `self-target-surface` as resolved and only `buffer-full-boundary` plus
  `post-append-clearing` as unresolved write-buffer questions.
- Green: update the write-buffer source-status artifact and docs.
- Regression: run focused tests, both status CLIs in JSON mode, evidence
  registry validation, `py_compile`, `git diff --check`, and the full unittest
  suite.

## After Action Report

Implemented in `sources/write_buffer_command_semantics_status.json`,
`evidence/self_mailbox_unsupported_bundle.json`, and
`evidence/command_buffer_unsupported_bundle.json`. The write-buffer
source-status record now has `self-target-surface` resolved through the
existing unsupported preservation boundaries, leaving only
`buffer-full-boundary` and `post-append-clearing` unresolved.

The red focused run executed 85 write-buffer, project-status, and source-status
frontier tests and failed because `self-target-surface` was still unresolved
and absent from write-buffer `resolved_resolution_questions`.

The green focused run passed 97 tests across write-buffer status,
project-status, source-status frontier, and the two unsupported evidence
bundles. The evidence bundle registry accepted all 8 bundles. Source-status
JSON accepted schema 1 with write-buffer unresolved questions narrowed to
`buffer-full-boundary` and `post-append-clearing`. Project-status JSON remained
accepted at schema 14. `py_compile`, `git diff --check`, and `python -m
unittest discover` passed; the full suite ran 662 tests.
