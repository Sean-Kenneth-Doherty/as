# ADR-0115: Project Status Registry Bundles

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0113 and ADR-0114 made transition registry JSON self-describing by adding
registered bundle entries and compact failure subjects. Chain registry JSON
already exposes the same operator-useful bundle list and failure summary.

The project status JSON report still collapses each registry to counts,
results, and failed subjects. That keeps the first diagnostic command from
answering which concrete transition and chain bundles were checked.

## Decision

Add `bundles` arrays to `transition_evidence` and `chain_evidence` sections in
project status JSON. Each section reuses the bundle entries from the
corresponding registry validator payload. Missing or malformed registry files
report `bundles: []`.

Because the project status JSON contract changes, bump
`PROJECT_STATUS_SCHEMA_VERSION` from `5` to `6`.

This ADR does not change registry validation semantics, source-status
validation semantics, or the default text status report.

## Success Criteria

- Red tests fail before implementation because project status remains
  `schema_version: 5` and registry summaries lack `bundles`.
- In-process project status reports include `schema_version: 6`.
- `transition_evidence.bundles` lists all registered transition evidence
  bundle entries in registry order.
- `chain_evidence.bundles` lists all registered chain evidence bundle entries
  in registry order.
- Missing or malformed registry summaries include `bundles: []`.
- JSON CLI output emits the same bundle arrays.
- Existing registry validation, frontier reporting, and full repository tests
  remain green.

## Consequences

Project status JSON becomes a complete first diagnostic for current evidence
coverage: it names both the accepted/rejected state and the concrete registry
entries that were checked.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report` fails before
  project status exposes registry bundle arrays and schema version `6`.
- Green: focused project-status tests pass after implementation.
- Regression: run adjacent transition and chain registry tests, project status
  JSON, registry JSON commands, `py_compile`, `git diff --check`, and the full
  default suite before commit.

## After Action Report

The red run of `python -m unittest tests.test_project_status_report` ran 33
tests and failed with two schema-version assertions plus five
`KeyError: 'bundles'` errors. That confirmed project status still emitted
`schema_version: 5` and did not provide bundle arrays on accepted or
registry-load failure summaries.

The implementation bumped project status JSON to `schema_version: 6`, carried
the underlying registry payload `bundles` entries into both registry
summaries, and returned `bundles: []` for missing or malformed registry files.

Verification passed with:

- `python -m unittest tests.test_project_status_report` (33 tests)
- `python -m unittest tests.test_project_status_report tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry` (62 tests)
- `python -m py_compile autarkic_systems/project_status.py tests/test_project_status_report.py`
- `git diff --check`
- `python -m autarkic_systems.project_status --format json`
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json`
- `python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json --format json`
- `python -m unittest discover` (573 tests)
