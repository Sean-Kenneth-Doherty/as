# ADR-0209: Project Status Sequence Evidence Failure Detail

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0208 made the post-handoff sequence SVG part of the sequence evidence
bundle. Project status now consumes the network-sequence evidence registry, but
its JSON and text summaries still stop at the registry validation subject when
a registered bundle fails. A drifted checked trace or SVG therefore appears as
`registry-bundle-validation` without preserving the inner bundle subject that
actually failed.

That is too coarse for the operator-facing status surface. The status report
should tell a reviewer whether the sequence bundle rejected because of
`sequence-trace`, `sequence-svg`, `sequence-language`, or another inner
evidence layer.

## Decision

Extend project status sequence-evidence summaries with
`bundle_failed_subjects`, an ordered list of rejected validation subjects from
the registered network-sequence evidence bundles.

When the list is non-empty, the text status will render:

`Network sequence evidence failures: ...`

This only enriches aggregate project status. It does not change runtime
behavior, sequence claims, proof certificates, evidence-bundle validation
authority, registry validation authority, trace/SVG rendering, source-status
boundaries, or the compact summary digest.

Because this adds a project-status JSON field, bump project status to
`schema_version: 20`.

## Success Criteria

- Red tests fail before implementation because project status does not expose
  `sequence_evidence.bundle_failed_subjects`, still reports schema version
  `19`, and does not render inner sequence evidence subjects in text output.
- Checked-in accepted status reports `bundle_failed_subjects: []`.
- A registry pointing at a drifted sequence SVG rejects project status and
  reports `sequence-svg` in `sequence_evidence.bundle_failed_subjects`.
- Default text output remains unchanged for the accepted path, while rejected
  sequence evidence text names the inner failed subject.
- JSON CLI output carries the same field.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run project-status CLI text/JSON/summary, sequence evidence
  bundle validation, `python -m compileall -q autarkic_systems tests`,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py`, with focused coverage in
`tests/test_project_status_report.py` and documentation in
`docs/project-status-report.md`.

The red focused run failed as intended: project status still reported
`schema_version: 19`, direct and CLI JSON lacked
`sequence_evidence.bundle_failed_subjects`, and the drifted sequence SVG path
could not surface `sequence-svg` through project status.

The implementation bumps project status to `schema_version: 20`, records
`bundle_failed_subjects` for sequence evidence summaries, and renders
`Network sequence evidence failures: ...` only on rejected sequence-bundle
paths. The checked-in accepted path reports `bundle_failed_subjects: []`,
while a temporary registry pointing at a drifted sequence SVG reports
`["sequence-svg"]`.

Focused project-status tests passed 85 tests. Live project-status JSON reported
`schema_version: 20` and an empty accepted-path `bundle_failed_subjects` list;
summary output remained the same six-line digest; direct sequence registry
validation remained accepted. `compileall`, `git diff --check`, and the full
default suite passed; the full suite ran 894 tests.
