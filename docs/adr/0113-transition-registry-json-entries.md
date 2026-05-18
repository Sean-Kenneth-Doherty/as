# ADR-0113: Transition Registry JSON Entries

Date: 2026-05-18

## Status

Accepted.

## Context

The transition-chain evidence registry JSON is self-describing: ADR-0086 added
a `bundles` array that lists each registered chain bundle ID, path, claim ID,
and expected status.

The lower-level transition evidence registry still emits only pass/fail
summary fields, bundle count, result count, and validation results. That is
enough to know the registry is green, but not enough to know which eight
transition evidence bundles were validated without re-reading
`evidence/manifest.json`.

## Decision

Extend `registry_validation_report_payload` for transition evidence registries
with a `bundles` array.

Each entry includes:

- `bundle_id`;
- `path`;
- `claim_id`; and
- `expected_status`.

This ADR does not change registry validation semantics, text output, bundle
schema, or manifest schema.

## Success Criteria

- Red tests fail before implementation because transition registry JSON lacks
  a `bundles` array.
- The in-process registry JSON payload lists all checked-in transition evidence
  bundle entries.
- The JSON CLI emits the same bundle entries.
- Existing transition registry validation, project status, and full repository
  tests remain green.

## Consequences

Transition evidence registry JSON becomes self-describing enough for operators
and future automation to connect a green bundle count to concrete transition
evidence artifacts without a second manifest pass.

## Test Plan

- Red: `python -m unittest tests.test_evidence_bundle_registry` fails before
  payload entries are added.
- Green: the focused registry test passes after implementation.
- Regression: run adjacent project-status and chain-registry tests,
  transition registry JSON, project status JSON, `py_compile`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented.

The red run of `python -m unittest tests.test_evidence_bundle_registry` failed
because transition registry JSON did not include a `bundles` key.

`autarkic_systems.evidence_bundle.registry_validation_report_payload` now adds
a `bundles` array with one entry per registered transition evidence bundle:
bundle ID, path, claim ID, and expected status. Validation semantics, text
output, and manifest schema remain unchanged.

Verification:

- `python -m unittest tests.test_evidence_bundle_registry` passed 15 tests.
- `python -m unittest tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry tests.test_project_status_report` passed 60 tests.
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json` reported `accepted: true`, `bundle_count: 8`, and all eight registered transition bundle entries.
- `python -m autarkic_systems.project_status --format json` still reported
  `schema_version: 5`, `accepted: true`, transition `bundle_count: 8`, chain
  `bundle_count: 2`, aggregate blocked commands `standard-signal`,
  `write-buf-zero`, and `write-buf-one`, per-source command attribution,
  blocked runtime surfaces, resolution questions, and
  `frontier.failed_subjects: []`.
- `python -m py_compile autarkic_systems/evidence_bundle.py tests/test_evidence_bundle_registry.py` passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 571 tests.
