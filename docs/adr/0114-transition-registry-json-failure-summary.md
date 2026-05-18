# ADR-0114: Transition Registry JSON Failure Summary

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0113 made transition evidence registry JSON self-describing by adding a
`bundles` array. The chain evidence registry JSON already has both `bundles`
and a compact `failed_subjects` list.

Transition evidence registry JSON still lacks `failed_subjects`, so automation
has to scan the full `results` array to route a rejected registry run.

## Decision

Extend `registry_validation_report_payload` for transition evidence registries
with `failed_subjects`, an ordered list of validation subjects whose result
was rejected.

This ADR does not change registry validation semantics, text output, bundle
schema, or manifest schema.

## Success Criteria

- Red tests fail before implementation because transition registry JSON lacks
  `failed_subjects`.
- Successful registry JSON reports `failed_subjects: []`.
- Drifted registry JSON reports `accepted: false` and includes rejected
  validation subjects in `failed_subjects`.
- JSON CLI output emits the same failure summary.
- Existing transition registry validation, project status, chain registry
  validation, and full repository tests remain green.

## Consequences

Transition and chain registry JSON now share the same compact failure-summary
shape. Automation can inspect either registry without reimplementing result
scanning.

## Test Plan

- Red: `python -m unittest tests.test_evidence_bundle_registry` fails before
  transition registry JSON includes `failed_subjects`.
- Green: the focused registry test passes after implementation.
- Regression: run adjacent project-status and chain-registry tests,
  transition registry JSON, chain registry JSON, project status JSON,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

The red run of `python -m unittest tests.test_evidence_bundle_registry`
failed four tests with `KeyError: 'failed_subjects'`, confirming that both
the in-process registry payload and JSON CLI output lacked the new summary.

The implementation added an ordered `failed_subjects` list to transition
registry JSON payloads. The focused green run passed 17 tests. An in-place
drifted registry fixture also reported `registry-completeness`, because
removing entries from the live registry while leaving sibling bundle files on
disk creates the same completeness failure boundary already used by the chain
registry.

Verification passed with:

- `python -m unittest tests.test_evidence_bundle_registry` (17 tests)
- `python -m unittest tests.test_evidence_bundle_registry tests.test_chain_evidence_bundle_registry tests.test_project_status_report` (62 tests)
- `python -m py_compile autarkic_systems/evidence_bundle.py tests/test_evidence_bundle_registry.py`
- `git diff --check`
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json`
- `python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json --format json`
- `python -m autarkic_systems.project_status --format json`
- `python -m unittest discover` (573 tests)
