# ADR-0099: Project Status Frontier Failure Summary

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0096 introduced `autarkic_systems.project_status` as the top-level
operator status report. ADR-0097 and ADR-0098 made registry failures structured
and machine-readable through registry-level `failed_subjects`.

The frontier section has equivalent failure arrays for missing and invalid
source-status files, but it does not yet expose a compact `failed_subjects`
summary. Automation must infer failure categories by inspecting
`missing_source_statuses` and `invalid_source_statuses` separately.

## Decision

Add `frontier.failed_subjects` to project status output.

The frontier summary will report:

- `[]` on the checked-in accepted path;
- `["source-status-file"]` when one or more source-status files are missing;
- `["source-status-json"]` when one or more source-status files are present
  but unreadable as JSON; and
- both subjects, in that order, when both failure modes occur.

This mirrors the registry summaries without changing the source-status
authority or adding a new validator.

## Success Criteria

- Red tests fail before implementation because `frontier.failed_subjects` is
  missing.
- Checked-in JSON status includes `frontier.failed_subjects: []`.
- Missing source-status files report
  `frontier.failed_subjects: ["source-status-file"]`.
- Invalid source-status JSON reports
  `frontier.failed_subjects: ["source-status-json"]`.
- Mixed missing and invalid source-status inputs report both subjects in a
  stable order.
- Existing accepted status output remains accepted.

## Consequences

Automation can inspect the frontier section the same way it inspects registry
sections: a small subject list identifies failure categories without scanning
every detail array.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before the
  frontier failure summary exists.
- Green: focused project-status tests pass after implementation.
- Regression: run project-status CLI JSON, adjacent registry tests,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_project_status_report` failed
with `KeyError: 'failed_subjects'` in accepted, missing source-status, invalid
source-status, mixed source-status, and JSON CLI status cases.

`autarkic_systems.project_status` now includes `frontier.failed_subjects`.
The checked-in accepted path reports an empty list. Missing source-status
files report `source-status-file`; malformed source-status files report
`source-status-json`; mixed failures report both subjects in stable order.

Verification:

- `python -m unittest tests.test_project_status_report` passed 14 tests.
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` passed 39 tests.
- `python -m autarkic_systems.project_status --format json` reported
  `accepted: true`, transition `bundle_count: 8`, chain `bundle_count: 2`, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 550 tests.
