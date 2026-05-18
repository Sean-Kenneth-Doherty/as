# ADR-0157: Execution Readiness Blocked Consistency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0154 introduced source-status `execution_readiness`, ADR-0155 required
blocked readiness gates to cover every live unresolved question, and ADR-0156
prevented readiness from allowing execution changes while unresolved questions
remain.

One contradictory state is still possible: a source-status record can say
`execution_readiness.decision` is `blocked` while setting
`execution_change_allowed` to `true`, as long as no unresolved questions and no
blockers are present.

## Decision

Reject any source-status record whose `execution_readiness.decision` is
`blocked` and whose `execution_readiness.execution_change_allowed` is `true`.

This is a validation-only tightening. It does not change accepted JSON shape,
status schema versions, or Universal Cell runtime behavior.

## Consequences

The readiness gate cannot claim a command is blocked and implementation-ready
at the same time.

Project-status remains schema 15, and source-status frontier remains schema 2.

## Verification Plan

- Red: add a schema test where readiness is `blocked` but execution changes
  are allowed, and confirm project status rejects it.
- Green: tighten execution-readiness validation to fail closed in that case.
- Regression: run focused status tests, both status CLIs in JSON mode,
  `py_compile`, `git diff --check`, and the full unittest suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py` and
`tests/test_project_status_report.py`.

The red focused run executed 83 project-status and source-status frontier
tests and failed only the new blocked-but-allowed readiness fixture, proving
the previous validator accepted contradictory readiness metadata.

The green focused run passed 83 tests after the validator rejected
`execution_readiness.decision: blocked` when execution changes are allowed.
The accepted JSON shape did not change: project-status remains schema 15 and
source-status frontier remains schema 2. `py_compile`, `git diff --check`, and
`python -m unittest discover` passed; the full suite ran 669 tests.
