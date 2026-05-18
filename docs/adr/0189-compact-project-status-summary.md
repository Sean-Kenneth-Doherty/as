# ADR-0189: Compact Project Status Summary

Date: 2026-05-18

## Status

Accepted.

## Context

The aggregate project status command is now a good audit surface, but the
default text report is intentionally detailed. It prints evidence bundle IDs,
covered examples, source-status boundaries, readiness gates, resolved
questions, and source cross-links. That is appropriate for audit work, but too
large for a quick "what is useful and what is blocked?" operator check.

ADR-0188 made the proof-rule migration visible in project status. A compact
status view can now expose the important top-level answer without hiding the
full text or JSON audit modes.

## Decision

Add a `summary` project-status output format. The summary will reuse the same
project-status payload as the default text and JSON modes, but render only the
top-level accepted state, evidence counts, claim counts, proof-rule audit,
blocked commands, and safe next slice.

## Success Criteria

- Red tests fail before implementation because `format_project_status_summary`
  is unavailable and `--format summary` is rejected.
- `format_project_status_summary` renders a compact six-line operator digest
  for the accepted default project status.
- `python -m autarkic_systems.project_status --format summary` prints the same
  compact digest and exits successfully.
- Summary output includes the proof-rule audit counts added by ADR-0188.
- Summary output omits full evidence bundle listings and source-status
  boundary paragraphs.
- Full repository tests remain green.

## Test Plan

- Red:
  `python -m unittest tests.test_project_status_report`
  fails before summary formatting and CLI support are added.
- Green: the same focused suite passes after implementation.
- Regression: run `python -m autarkic_systems.project_status --format summary`,
  `python -m autarkic_systems.project_status --format json`, `python -m
  compileall -q autarkic_systems tests`, `git diff --check`, and the full
  default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_project_status_report` run executed 76 tests and
failed because `format_project_status_summary` did not exist and
`--format summary` was rejected by the CLI parser.

The implementation added `format_project_status_summary`, wired `summary` into
the existing `--format` option, and kept the full text and JSON report payloads
unchanged. The compact summary reuses the aggregate project-status payload and
renders the accepted state, evidence counts, claim counts, proof-rule audit,
blocked commands, and safe next slice in six lines.

The focused project-status suite then passed with 76 tests. The summary CLI
printed the compact digest and omitted evidence bundle listings and source
boundary paragraphs. Summary and JSON project-status commands, `compileall`,
`git diff --check`, and the full default suite also passed; the full suite ran
791 tests.
