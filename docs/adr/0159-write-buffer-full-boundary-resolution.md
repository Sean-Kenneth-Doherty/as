# ADR-0159: Write-Buffer Full-Boundary Resolution

Date: 2026-05-18

## Status

Accepted.

## Context

Write-buffer command-token execution remains blocked by two source-status
questions:

- `buffer-full-boundary`;
- `post-append-clearing`.

The full-buffer question can be narrowed independently of post-append clearing.
The formal model defines a less-than-full guard for writing to the stem buffer
and a separate full-buffer processing state. RAA also guards `write-buf` with
`buffer-full?`. SEMSIM and FSMSIM expose write-buffer append functions without
a matching full-buffer guard, but they do not provide a contrary full-buffer
policy for named write-buffer command-token execution.

## Decision

Resolve `buffer-full-boundary` as:
`preserve-existing-full-buffer-boundary-before-write-buffer-append`.

AS will not treat a write-buffer command token as implementation-ready when the
stem command buffer is already full. The source-status frontier should preserve
the existing full-buffer boundary and continue blocking executable write-buffer
append semantics on the remaining `post-append-clearing` question.

This is a source-status narrowing only. It does not implement write-buffer
command execution, change Universal Cell runtime behavior, or change status
JSON schema versions.

## Consequences

The write-buffer source-status queue now has one live blocker:
`post-append-clearing`.

Execution readiness remains blocked and `execution_change_allowed` remains
`false`, but its blocker list narrows to `post-append-clearing`.

Project-status remains schema 15, and source-status frontier remains schema 2.

## Verification Plan

- Red: add focused source-status tests proving `buffer-full-boundary` is
  removed from unresolved questions, added to resolved questions, and removed
  from execution-readiness blockers.
- Green: update the write-buffer source-status artifact and documentation.
- Regression: run focused write-buffer/status tests, both status CLIs in JSON
  mode, `py_compile`, `git diff --check`, and the full unittest suite.

## After Action Report

Implemented in `sources/write_buffer_command_semantics_status.json` and
`docs/write-buffer-command-semantics-status.md`, with tests in
`tests/test_write_buffer_command_semantics_status.py`,
`tests/test_project_status_report.py`, and
`tests/test_source_status_frontier_cli.py`.

The red run covered the focused write-buffer/status group and failed because
`buffer-full-boundary` was still unresolved, absent from
`resolved_resolution_questions`, and still listed as an execution-readiness
blocker.

The green implementation added a structured
`buffer_full_boundary_resolution`, moved `buffer-full-boundary` into
`resolved_resolution_questions`, removed it from
`required_resolution_questions`, removed its unresolved evidence entry, and
narrowed execution-readiness blockers to `post-append-clearing`.

This preserves project-status schema 15, source-status frontier schema 2, and
all Universal Cell runtime behavior.

Verification passed:

- `python -m unittest tests.test_write_buffer_command_semantics_status tests.test_project_status_report tests.test_source_status_frontier_cli`
  ran 97 tests;
- `python -m autarkic_systems.source_status --format json` accepted schema 2
  with write-buffer readiness blocked only by `post-append-clearing`;
- `python -m autarkic_systems.project_status --format json` accepted schema 15
  with the same narrowed blocker;
- `python -m py_compile tests/test_write_buffer_command_semantics_status.py tests/test_project_status_report.py tests/test_source_status_frontier_cli.py`;
- `git diff --check`; and
- `python -m unittest discover` ran 674 tests.
