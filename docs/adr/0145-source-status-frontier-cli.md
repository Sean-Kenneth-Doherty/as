# ADR-0145: Source-Status Frontier CLI

Date: 2026-05-18

## Status

Accepted.

## Context

The project status command is now a broad operator surface: it validates
transition evidence, transition-chain evidence, claim/proof surfaces, object
languages, and the command-token source-status frontier. That breadth is useful
for release-style checks, but agents often need a narrower diagnostic while
working specifically on the blocked command-token semantics.

After ADR-0144, the source-status frontier carries enough information to guide
work by itself: blocked commands, runtime surfaces, AS boundaries, unresolved
questions, source evidence for those questions, resolved sub-decisions, and the
source-review cross-links. At present the only first-class CLI for that combined
frontier is the full project status report.

## Decision

Add `python -m autarkic_systems.source_status` as a focused source-status
frontier CLI over the same command-frontier records consumed by project status:

- `sources/recipient_non_init_command_source_status.json`;
- `sources/standard_signal_command_semantics_status.json`; and
- `sources/write_buffer_command_semantics_status.json`.

The new CLI will support text and JSON output. JSON output will report
`schema_version: 1`, an `accepted` boolean, and the existing frontier payload.
Text output will render the accepted/rejected state, failed subjects, blocked
commands, blocked runtime surfaces, AS boundaries, unresolved questions, source
evidence, resolved questions, source-status cross-links, safe next slice, and
missing or invalid source-status paths.

The CLI reuses the existing project-status source-status frontier validation so
there is one command-frontier schema contract rather than two competing
validators.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.source_status` does not exist.
- The checked-in source-status frontier reports accepted text and JSON output.
- Missing source-status paths report `source-status-file` and return a rejected
  CLI status.
- Schema-invalid source-status JSON reports `source-status-schema` and returns a
  rejected CLI status.
- Module execution works with `python -m autarkic_systems.source_status`.
- Project status remains accepted and runtime behavior remains unchanged.
- Full repository tests remain green.

## Consequences

Agents can inspect the blocked command-token frontier without paying the visual
and cognitive overhead of the full project status report. This should make the
next semantic slices easier to choose while preserving the current fail-closed
validation behavior.

This does not resolve any command-token question and does not change Universal
Cell behavior.

## Test Plan

- Red: add focused source-status CLI tests and run them before implementation.
- Green: add the CLI module as a thin wrapper around the existing frontier
  validation and rendering helpers.
- Regression: run focused source-status CLI tests, project status text/JSON
  checks, `py_compile`, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `autarkic_systems/source_status.py`.

The red focused run failed because `tests/test_source_status_frontier_cli.py`
could not import `autarkic_systems.source_status`.

The green implementation added a focused text/JSON CLI around the existing
project-status frontier validator. The checked-in frontier now reports
accepted text output, JSON `schema_version: 1`, the expected blocked commands,
and the current safe next slice. Missing-path and schema-invalid scratch
fixtures return rejected status with `source-status-file` and
`source-status-schema` failed subjects.

Runtime behavior remains unchanged.

Verification passed: focused source-status CLI tests ran 9 tests; source-status
text and JSON CLI output were accepted; project status text and JSON remained
accepted at `schema_version: 14`; `py_compile` and `git diff --check` passed;
and `python -m unittest discover` passed 650 tests.
