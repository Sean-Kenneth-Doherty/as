# ADR-0125: Project Status Source-Status Cross-Link Paths

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0123 and ADR-0124 make source-status cross-links visible in project status
JSON and text. Those cross-links are now part of the first diagnostic surface
for the blocked standard-signal and write-buffer frontier.

The source-status schema currently checks the cross-link container shape and
requires `adr`, `path`, and `summary` text, but it does not prove that the
linked `path` exists. A dead cross-link would still be accepted and displayed,
weakening the source-review trail exactly where the operator needs it most.

## Decision

Require every `additional_source_statuses[].path` consumed by project status to
point to an existing file. Missing cross-link paths will reject the owning
source-status record as `source-status-schema`.

This ADR does not change project status JSON, which remains
`schema_version: 8`, and does not change the default text layout introduced by
ADR-0124.

## Success Criteria

- Red tests fail before implementation because a source-status record with a
  missing `additional_source_statuses[].path` is still accepted.
- Accepted checked-in project status still reports the standard-signal and
  write-buffer cross-links.
- Malformed or missing cross-link paths report `source-status-schema`.
- Project status JSON remains `schema_version: 8`.
- Existing source-status validation, project-status text/JSON, and full
  repository tests remain green.

## Consequences

The first diagnostic report can no longer display a source-status cross-link
that points nowhere. This keeps the source-review trail actionable without
expanding command-token execution semantics.

## Test Plan

- Red: run `python -m unittest tests.test_project_status_report` after adding
  a missing-cross-link-path assertion.
- Green: update project-status source-status schema validation to require
  existing cross-link files.
- Regression: run focused project-status tests, adjacent referenced
  source-status tests, project status text/JSON, `py_compile`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by extending
source-status schema validation so every `additional_source_statuses[].path`
must resolve to an existing file. Missing targets now reject the owning
source-status record as `source-status-schema`.

The red project-status run executed 41 tests and failed because a
source-status record with a missing cross-link path was still accepted. The
green focused run passed 41 project-status tests after implementation.

Regression verification passed: focused project-status and referenced
source-status tests ran 66 tests; `py_compile` and `git diff --check` passed;
default project status text remained accepted with the standard-signal and
write-buffer cross-links; project status JSON remained accepted at
`schema_version: 8`; and `python -m unittest discover` passed 585 tests.
