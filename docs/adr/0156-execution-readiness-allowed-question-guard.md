# ADR-0156: Execution Readiness Allowed-Question Guard

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0154 added source-status `execution_readiness` gates, and ADR-0155
required blocked readiness gates to cover every live unresolved question.

The inverse guard is still missing: a source-status record can currently set
`execution_change_allowed` to `true` while live
`required_resolution_questions` remain present, as long as the readiness
blocker list is empty.

## Decision

Reject any source-status record that allows execution changes while it still
has unresolved `required_resolution_questions`.

This is a validation-only tightening. It does not change accepted JSON shape,
status schema versions, or Universal Cell runtime behavior.

## Consequences

Execution readiness cannot declare a command ready for implementation until
the source-status record has no live unresolved questions.

Project-status remains schema 15, and source-status frontier remains schema 2.

## Verification Plan

- Red: add a schema test where `execution_change_allowed` is `true` while one
  unresolved question remains and confirm project status rejects it.
- Green: tighten execution-readiness validation to fail closed in that case.
- Regression: run focused status tests, both status CLIs in JSON mode,
  `py_compile`, `git diff --check`, and the full unittest suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py` and
`tests/test_project_status_report.py`.

The red focused run executed 82 project-status and source-status frontier
tests and failed only the new allowed-with-unresolved-questions fixture,
proving the previous validator accepted `execution_change_allowed: true` while
an unresolved question remained.

The green focused run passed 82 tests after the validator rejected execution
readiness that allows execution changes while unresolved
`required_resolution_questions` remain. The accepted JSON shape did not
change: project-status remains schema 15 and source-status frontier remains
schema 2. `py_compile`, `git diff --check`, and `python -m unittest discover`
passed; the full suite ran 668 tests.
