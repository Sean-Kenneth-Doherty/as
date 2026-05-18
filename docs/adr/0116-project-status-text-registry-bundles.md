# ADR-0116: Project Status Text Registry Bundles

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0115 made project status JSON list the concrete transition and chain
registry bundle entries checked by the first diagnostic command.

The default text status still reports only registry acceptance and bundle
counts. That is enough to see that the registry is green, but not enough for a
human operator to see which concrete evidence artifacts were checked without
running JSON mode or a lower-level registry command.

## Decision

Render transition and chain evidence bundle IDs in the default project status
text report. Each listed bundle also includes its path so the text report
remains directly navigable from the command output. Missing or malformed
registries render `none` for the corresponding bundle list.

This ADR changes only text output. The project status JSON contract remains
`schema_version: 6`, and validation semantics are unchanged.

## Success Criteria

- Red tests fail before implementation because text status output omits
  transition and chain bundle sections.
- Default text status includes a `Transition evidence bundles:` section with
  the checked transition bundle IDs and paths.
- Default text status includes a `Chain evidence bundles:` section with the
  checked chain bundle IDs and paths.
- Missing or malformed registry summaries render `none` for the affected
  registry bundle section.
- Project status JSON remains `schema_version: 6`.
- Existing registry validation, project-status JSON, and full repository tests
  remain green.

## Consequences

The first human diagnostic command now shows both that evidence is green and
which concrete evidence bundle artifacts were included in that green result.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before
  bundle sections are rendered in text output.
- Green: focused project-status tests pass after text rendering is added.
- Regression: run adjacent transition and chain registry tests, project status
  text and JSON commands, `py_compile`, `git diff --check`, and the full
  default suite before commit.

## After Action Report

The red run of `python -m unittest tests.test_project_status_report` ran 33
tests and failed three text-output assertions. The default status report
omitted `Transition evidence bundles:`, omitted `Chain evidence bundles:`, and
omitted the `Chain evidence bundles: none` fallback for missing or malformed
chain registry summaries.

The implementation added registry bundle text lines to
`format_project_status_report`, rendering each bundle as
`bundle_id -> path` and rendering `none` when the registry summary has no
bundle entries. Project status JSON remained `schema_version: 6`.

Verification passed with:

- `python -m unittest tests.test_project_status_report` (33 tests)
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` (62 tests)
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py`
- `git diff --check`
- `python -m autarkic_systems.project_status`
- `python -m autarkic_systems.project_status --format json`
- `python -m unittest discover` (573 tests)
