# ADR-0126: Project Status Source-Status Cross-Link JSON Targets

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0125 requires every project-status source-status cross-link path to exist.
That prevents dead links, but it still allows an existing junk file to pass as
part of the operator source-review trail.

Project status presents `additional_source_statuses` as source-status evidence.
If a linked path is not parseable JSON, or parses to a non-object JSON value,
the report can still display a trail that is real only as a filesystem path and
not as a usable source-status artifact.

## Decision

Require every `additional_source_statuses[].path` consumed by project status to
point to a file that contains parseable JSON whose top-level value is an
object. Invalid JSON or non-object JSON rejects the owning source-status record
as `source-status-schema`.

This ADR does not validate the linked artifact's full source-status schema.
The current requirement is deliberately narrower: a project-status cross-link
must at least be a readable JSON object before it is displayed as a
source-status trail entry.

Project status JSON remains `schema_version: 8`, and the default text layout
from ADR-0124 is unchanged.

## Success Criteria

- Red tests fail before implementation because existing non-JSON cross-link
  targets are still accepted.
- Non-object JSON cross-link targets also report `source-status-schema`.
- Accepted checked-in project status still reports the standard-signal and
  write-buffer cross-links.
- Project status JSON remains `schema_version: 8`.
- Existing source-status validation, project-status text/JSON, and full
  repository tests remain green.

## Consequences

The source-review trail now rejects paths that exist but cannot be consumed as
source-status JSON objects. This improves operator trust in the report without
claiming any new command-token execution semantics.

## Test Plan

- Red: run `python -m unittest tests.test_project_status_report` after adding
  invalid-JSON and non-object-JSON cross-link target assertions.
- Green: update project-status source-status schema validation to load each
  cross-link target as JSON and require a top-level object.
- Regression: run focused project-status tests, adjacent referenced
  source-status tests, project status text/JSON, `py_compile`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by extending source-status
schema validation so every `additional_source_statuses[].path` target must load
as JSON and have a top-level object value. Existing files with invalid JSON or
non-object JSON now reject the owning source-status record as
`source-status-schema`.

The red project-status run executed 43 tests and failed because invalid-JSON
and non-object JSON cross-link targets were still accepted. The green focused
run passed 43 project-status tests after implementation.

Regression verification passed: focused project-status and referenced
source-status tests ran 68 tests; `py_compile` and `git diff --check` passed;
default project status text remained accepted with the standard-signal and
write-buffer cross-links; project status JSON remained accepted at
`schema_version: 8`; and `python -m unittest discover` passed 587 tests.
