# ADR-0223: Source Review Frontier Summary

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0171 added a dated source-review snapshot for the remaining
`standard-signal` command-token boundary. Current project status and focused
source-status reports validate the source-status records and list the snapshot
as an additional source-status link, but the dated review gate is not exposed as
its own first-class frontier field.

That weakens operator legibility: the report says standard-signal execution
requires new source evidence, but automation must know the internal
`latest_source_review` shape to inspect which review closed that gate.

## Decision

Expose optional `latest_source_review` metadata in the source-status frontier
summary, both through aggregate project status and the focused
`autarkic_systems.source_status` CLI.

When present, `latest_source_review` will be schema-checked, will point to an
existing JSON review artifact, and will render as a compact text section naming
the reviewed date, review ID, decision, execution-change allowance, and path.

This does not change runtime behavior, command semantics, claim/proof
validation, evidence-bundle acceptance, source-status decisions, the active
standard-signal boundary, GitHub submission status, or handoff readiness.

## Success Criteria

- Red tests fail before implementation because source-status frontier JSON/text
  lacks first-class `latest_source_review` output.
- Project status bumps its schema version and carries the same frontier field.
- Focused source-status output bumps its schema version and carries the same
  frontier field.
- Malformed `latest_source_review` metadata rejects as `source-status-schema`.
- Text output renders a `Latest source reviews:` section for the
  standard-signal source-status record.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_source_status_frontier_cli
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live source-status text/JSON, live project-status
  summary/JSON, live handoff with `--refresh-remotes`, compileall,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented in `autarkic_systems/project_status.py` and
`autarkic_systems/source_status.py`, with focused coverage in
`tests/test_source_status_frontier_cli.py` and
`tests/test_project_status_report.py`.

The red focused run failed as intended because the focused source-status schema
was still `2`, project status was still schema `20`, source-status frontier
JSON lacked `latest_source_review`, source/project text lacked `Latest source
reviews:`, and a missing linked review path did not reject.

The implementation adds a checked optional `latest_source_review` object to
each accepted frontier source-status entry, reads `reviewed_at` from the linked
review JSON, rejects missing or malformed linked review artifacts, and rejects
review ID, decision, or execution-change drift against the linked review where
that information is present. Aggregate project status now reports
`schema_version: 21`; the focused source-status CLI now reports
`schema_version: 3`.

Focused source-status and project-status tests passed 98 tests. Live
source-status text/JSON rendered the dated standard-signal source review, live
project-status summary/JSON reported accepted status and schema version `21`,
and live handoff with refreshed remotes remained ready. `compileall`,
`git diff --check`, and the full default suite passed; the full suite ran 911
tests.
