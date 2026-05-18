# ADR-0130: Project Status Resolved Resolution Questions

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0128 resolved the `standard-signal` `command-table-offset` question in
favor of the formal PRC stem command-buffer map. That progress is recorded in
`sources/standard_signal_command_semantics_status.json`, but the operator-facing
project status only carries unresolved resolution questions.

That makes the first-run status weaker than the source-status artifact. A
future agent can see what remains blocked, but not which blocker questions were
already settled and where the settled decision points.

## Decision

Expose optional `resolved_resolution_questions` metadata from accepted
source-status records through project status JSON and text.

The JSON report will bump to `schema_version: 9` and carry a
`resolved_resolution_questions` array on each accepted
`frontier.source_statuses` entry. Each entry records at least `question_id` and
`decision`, plus optional `source_status` when the source-status artifact names
the checked artifact that settled the question.

The default text report will render a `Resolved resolution questions:` section
so operators can see settled blocker questions without opening the underlying
source-status JSON.

Malformed `resolved_resolution_questions` metadata will reject the owning
source-status record as `source-status-schema`, matching the fail-closed policy
already used for unresolved question metadata.

## Success Criteria

- Red tests fail before implementation because project status remains at
  `schema_version: 8`, omits resolved question metadata, and does not render a
  resolved-question text section.
- Project status JSON includes the standard-signal `command-table-offset`
  resolved question with its decision and source-status path.
- Project status text renders that resolved question.
- Source-status records without resolved questions report an empty array in
  JSON and `Resolved resolution questions: none` in text when no accepted
  source-status record has resolved questions.
- Malformed resolved-question metadata is reported as `source-status-schema`.
- Full repository tests remain green.

## Consequences

The first diagnostic command now reports both sides of the command-token
frontier: unresolved work still blocking execution, and resolved source-backed
decisions that should not be reopened without new evidence.

This ADR does not change runtime behavior or any source-status decision.

## Test Plan

- Red: update project-status tests for schema version 9, JSON
  `resolved_resolution_questions`, text rendering, absent-field fallback, and
  malformed metadata.
- Green: update `autarkic_systems.project_status` to validate and expose the
  resolved-question metadata.
- Regression: run focused project-status tests, status text/JSON, and the full
  default test suite before commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` by adding project-status
schema version `9`, JSON `resolved_resolution_questions` entries, validation for
malformed resolved-question metadata, and a default text
`Resolved resolution questions:` section.

The red focused run executed 47 tests and failed because project status still
reported `schema_version: 8`, omitted resolved-question JSON/text, and accepted
malformed resolved-question metadata. The green focused run passed 47 tests
after implementation.

Runtime behavior and source-status decisions remain unchanged. The status report
now shows `command-table-offset` as a settled standard-signal question while
leaving the remaining command-token frontier open.

Verification passed: adjacent project-status and standard-signal tests ran 54
tests; `py_compile` and `git diff --check` passed; project status text and JSON
were accepted at `schema_version: 9`; and `python -m unittest discover` passed
594 tests.
