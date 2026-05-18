# ADR-0111: Project Status Resolution Question Summaries

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0108 exposed source-status resolution question IDs in project status JSON,
ADR-0109 validated the question metadata shape, and ADR-0110 rendered those
IDs in the default text report.

The source-status records already carry concise summaries for those resolution
questions. Project status still drops those summaries. That means both humans
and automation can see stable question IDs but must re-open source-status files
to learn what each question actually asks.

## Decision

Add a `resolution_questions` list to each accepted
`frontier.source_statuses` entry in project status JSON. Each entry contains:

- `question_id`, the stable question identifier; and
- `summary`, the concise source-status summary of the unresolved decision.

Preserve the existing `required_resolution_questions` ID list for compatibility
with ADR-0108 consumers. Because this adds a JSON field to accepted
source-status entries, bump `PROJECT_STATUS_SCHEMA_VERSION` from `3` to `4`.

The text report will render each resolution question as
`question_id: summary`, grouped under the source-status command label.

## Success Criteria

- Red tests fail before implementation because project status remains
  `schema_version: 3`, lacks `resolution_questions`, and text output omits
  question summaries.
- In-process status reports include `schema_version: 4`.
- JSON CLI output includes `schema_version: 4`.
- Accepted standard-signal and write-buffer source-status entries include
  summary-bearing `resolution_questions`.
- The default text report names the question IDs and their summaries.
- Existing `required_resolution_questions` ID lists remain present.
- Existing registry and source-status failure behavior remains unchanged.

## Consequences

Project status becomes a more complete blocker work queue. Future agents can
read the default status report or schema-versioned JSON and see the decision
questions without a second pass through the source-status artifacts.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  summary-bearing question surface exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI text and JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
because project status still emitted `schema_version: 3`, had no per-source
`resolution_questions` list, and text output listed question IDs without their
summaries.

`autarkic_systems.project_status` now emits `schema_version: 4` and includes
summary-bearing `resolution_questions` objects on each accepted
`frontier.source_statuses` entry. The existing
`required_resolution_questions` ID lists remain present. The default text
status report now renders each blocker question as `question_id: summary`
under its command label.

Verification:

- `python -m unittest tests.test_project_status_report` passed 29 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 54 tests.
- `python -m autarkic_systems.project_status` reported accepted transition
  evidence with 8 bundles, accepted chain evidence with 2 bundles, blocked
  commands `standard-signal`, `write-buf-zero`, and `write-buf-one`, and
  summary-bearing text resolution-question lines for standard-signal and
  write-buffer blockers.
- `python -m autarkic_systems.project_status --format json` reported
  `schema_version: 4`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution,
  preserved `required_resolution_questions` ID lists, summary-bearing
  `resolution_questions`, and `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 565 tests.
