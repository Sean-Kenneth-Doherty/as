# ADR-0103: Project Status Source Command Attribution

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0102 made source-status records name at least one command token before the
project status command accepts them as part of the blocked frontier. The JSON
status report still exposes those commands only as a single aggregate
`frontier.blocked_commands` list.

That aggregate is useful for first-run status, but automation cannot tell
which source-status artifact contributed which blocked command without
re-reading the individual source-status JSON files.

## Decision

Add a `commands` list to each accepted `frontier.source_statuses` entry in the
project status JSON report.

The per-source command list uses the same extraction rules as the aggregate
frontier:

- `command`, for a single command token;
- `commands`, for a command-token list; and
- `blocked_runtime_commands`, for aggregate frontier records.

Because this changes the JSON report shape, bump
`PROJECT_STATUS_SCHEMA_VERSION` from `1` to `2`.

## Success Criteria

- Red tests fail before implementation because source-status entries do not
  include `commands` and the report still has `schema_version: 1`.
- In-process status reports include `schema_version: 2`.
- JSON CLI output includes `schema_version: 2`.
- Accepted source-status entries report the command tokens contributed by that
  source-status file.
- The checked-in project status remains accepted with the same aggregate
  blocked-command frontier.

## Consequences

Agents and scripts can inspect the project status report alone to see both the
whole blocked frontier and the source-status artifact responsible for each
frontier term.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  source command attribution exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because project status still reported `schema_version: 1`; the pre-change JSON
also had no per-source `commands` entries.

`autarkic_systems.project_status` now emits `schema_version: 2` and includes a
`commands` list on each accepted `frontier.source_statuses` entry. The
aggregate blocked-command frontier remains unchanged.

Verification:

- `python -m unittest tests.test_project_status_report` passed 17 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 42 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 2`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, and per-source command attribution.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 553 tests.
