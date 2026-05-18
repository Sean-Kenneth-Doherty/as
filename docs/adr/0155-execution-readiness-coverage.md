# ADR-0155: Execution Readiness Coverage

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0154 added `execution_readiness` to source-status records and required
readiness blockers to match live unresolved `required_resolution_questions`.

That prevents stale blocker IDs, but it still permits partial blocker lists.
For write-buffer, a malformed record could say execution is blocked only by
`buffer-full-boundary` while leaving `post-append-clearing` unresolved and
unmentioned in the execution gate.

## Decision

When a source-status record has `execution_readiness.decision` set to
`blocked`, its `blocked_by_resolution_questions` list must cover every live
unresolved `required_resolution_questions[].question_id`.

This tightens validation only. It does not change the accepted JSON shape or
runtime behavior.

## Consequences

Future source-status records cannot present execution readiness as blocked
while omitting one of the live unresolved execution questions from the
readiness gate.

Project-status remains schema 15, and source-status frontier remains schema 2.

## Verification Plan

- Red: add a schema test where a blocked readiness object covers only one of
  two unresolved questions and confirm project status rejects it.
- Green: tighten execution-readiness validation to require full blocker
  coverage for blocked readiness decisions.
- Regression: run focused status tests, both status CLIs in JSON mode,
  `py_compile`, `git diff --check`, and the full unittest suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py` and
`tests/test_project_status_report.py`.

The red focused run executed 81 project-status and source-status frontier
tests and failed only the new partial-readiness coverage fixture, proving the
previous validator accepted a blocked execution gate that omitted one live
unresolved question.

The green focused run passed 81 tests after the validator required blocked
execution-readiness blockers to cover every unresolved
`required_resolution_questions` ID. The accepted JSON shape did not change:
project-status remains schema 15 and source-status frontier remains schema 2.
`py_compile`, `git diff --check`, and `python -m unittest discover` passed;
the full suite ran 667 tests.
