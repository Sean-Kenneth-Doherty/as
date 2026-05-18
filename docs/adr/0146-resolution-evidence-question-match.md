# ADR-0146: Resolution Evidence Question Matching

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0144 defined `resolution_question_evidence` entries as evidence whose
`question_id` matches an unresolved resolution question. The current validator
checks that each evidence entry is an object with non-empty `question_id` and
`evidence` text, but it does not enforce that the evidence points at one of the
record's `required_resolution_questions`.

That leaves a drift path: a source-status record can render source evidence for
a misspelled or stale question ID while the real unresolved question has no
evidence attached. The focused source-status CLI introduced by ADR-0145 reuses
the same validator, so the gap affects both the aggregate project status report
and the narrower frontier report.

## Decision

Make `resolution_question_evidence[].question_id` fail closed unless it matches
one of the source-status record's unresolved `required_resolution_questions`
IDs.

This preserves project status `schema_version: 14` and source-status frontier
`schema_version: 1` because the emitted JSON shape is unchanged. Only the
validation contract is tightened.

## Success Criteria

- Red tests fail before implementation because a scratch source-status record
  with evidence for a nonexistent unresolved question is still accepted.
- Project status rejects unmatched evidence IDs as `source-status-schema`.
- The focused source-status frontier report rejects the same drift through the
  shared validator.
- Checked-in source-status records remain accepted.
- Runtime behavior remains unchanged.
- Full repository tests remain green.

## Consequences

The unresolved-question evidence trail becomes harder to corrupt by typo or
stale metadata. A status report that displays evidence for a blocker now also
proves that the evidence is attached to a live unresolved question in the same
source-status record.

This does not resolve any command-token question and does not change Universal
Cell behavior.

## Test Plan

- Red: add project-status and source-status frontier tests with mismatched
  evidence question IDs.
- Green: tighten the shared source-status frontier validator.
- Regression: run focused project-status/source-status tests, project status
  and source-status text/JSON checks, `py_compile`, `git diff --check`, and the
  full default suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py`.

The red focused run executed 71 tests and failed because project status and the
focused source-status frontier report still accepted scratch source-status
records with `resolution_question_evidence` attached to a misspelled
`question_id`.

The green implementation makes the shared frontier validator reject evidence
IDs that are not present in the same record's unresolved
`required_resolution_questions` list. Because `autarkic_systems.source_status`
reuses that validator, the focused report now fails closed on the same drift.

Runtime behavior remains unchanged.

Verification passed: focused project-status and source-status frontier tests
ran 71 tests; source-status JSON was accepted at `schema_version: 1`; project
status JSON remained accepted at `schema_version: 14`; `py_compile` and
`git diff --check` passed; and `python -m unittest discover` passed 652 tests.
