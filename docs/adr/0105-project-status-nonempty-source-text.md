# ADR-0105: Project Status Nonempty Source Text

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0100 made project status reject source-status records missing `decision`
or `safe_next_slice`, and ADR-0104 made command-token fields reject blank
strings.

The `decision` and `safe_next_slice` checks still accept whitespace-only text.
That lets a source-status artifact pass the project status report while
presenting an empty decision or empty next-step field to operators and
automation.

## Decision

Treat whitespace-only `decision` and `safe_next_slice` values as
`source-status-schema` failures.

This tightens validation of the existing project status JSON contract without
changing the JSON shape, so `schema_version` remains `2`.

## Success Criteria

- Red tests fail before implementation because blank `decision` and
  `safe_next_slice` strings are accepted.
- Blank `decision` and `safe_next_slice` values report
  `frontier.failed_subjects: ["source-status-schema"]`.
- Accepted source-status entries still expose the checked-in decisions,
  safe-next slice, and per-source command attribution.
- Existing missing, malformed, commandless, and blank-command source-status
  failure behavior remains unchanged.

## Consequences

The project status frontier cannot carry empty operator text. Source-status
records must provide meaningful non-whitespace decision and next-step fields
before they are accepted into the project-level report.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  nonempty text check exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because source-status records with whitespace-only `decision` or
`safe_next_slice` text were accepted as valid frontier contributors.

`autarkic_systems.project_status` now requires both fields to be non-whitespace
text before accepting a source-status record. The project status JSON shape
remains `schema_version: 2`.

Verification:

- `python -m unittest tests.test_project_status_report` passed 20 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 45 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 2`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 556 tests.
