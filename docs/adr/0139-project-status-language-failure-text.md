# ADR-0139: Project Status Language Failure Text

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0138 adds `transition_language` and `chain_language` summaries to project
status JSON and compact accepted/rejected lines to the default text report.
The JSON summaries include `failed_subjects`, but the text report only says a
language surface is rejected and shows zero or current counts.

That is weaker than the adjacent registry and source-status text sections,
which name missing or invalid surfaces when the first diagnostic command is
rejected.

## Decision

Add a compact `Language failures:` section to
`format_project_status_report`.

When both language summaries are accepted, the text report will render:

```text
Language failures: none
```

When one or both language summaries are rejected, the section will list the
affected language label and its failed subjects, preserving the failed-subject
names already present in JSON.

This change keeps project status JSON at `schema_version: 11`; the machine
contract already carries `failed_subjects`.

## Success Criteria

- Red tests fail before implementation because accepted text output does not
  render `Language failures: none` and rejected language text does not name
  failed subjects.
- A malformed transition language manifest makes text output include
  `Transition language failures:` and the failed syntax-class subject.
- A malformed chain language manifest makes text output include
  `Chain language failures:` and the failed syntax-class subject.
- Project status JSON remains schema version `11`.
- Full repository tests remain green.

## Consequences

Rejected language summaries become diagnosable from the default human report
without forcing every syntax-class result into the green path.

No project status JSON shape, claim, proof, evidence, or runtime semantics
change.

## Test Plan

- Red: add project-status text tests for accepted language failure absence and
  malformed base/chain language failed subjects.
- Green: add text rendering helper over `transition_language.failed_subjects`
  and `chain_language.failed_subjects`.
- Regression: run focused project-status tests, project status text/JSON,
  `py_compile`, `git diff --check`, and the full default test suite before
  commit.

## After Action Report

Implemented in `autarkic_systems/project_status.py` with focused tests in
`tests/test_project_status_report.py`.

The red test run executed 54 project-status tests and failed because the
accepted text report did not render `Language failures: none`, and malformed
base/chain language surfaces did not expose failed syntax-class subjects in
text. The green implementation adds `_language_failure_text_lines`, rendering
`Language failures: none` on the accepted path and compact failed-subject
lines for rejected transition or chain language summaries.

Project status JSON remains unchanged at `schema_version: 11`; the checked-in
status still reports `accepted: true`.

Verification passed: focused project-status tests ran 54 tests;
`python -m autarkic_systems.project_status` rendered `Language failures: none`;
`python -m autarkic_systems.project_status --format json` remained accepted at
schema version `11`; `py_compile` and `git diff --check` passed; and
`python -m unittest discover` passed 633 tests.
