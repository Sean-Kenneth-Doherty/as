# ADR-0087: Chain Registry JSON Failure Summary

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0084 through ADR-0086 made chain evidence registry validation available as
text and JSON. The JSON payload now identifies both the registry results and
the concrete bundle entries validated.

When validation fails, however, automation still has to scan every item in the
`results` array to find the rejected subjects. That is workable for humans but
unnecessarily awkward for callers that only need to route or summarize a
failure.

## Decision

Extend chain registry JSON output with `failed_subjects`, an ordered list of
validation subjects whose result was rejected.

This ADR does not change validation semantics, text output, or the registry
manifest schema.

## Success Criteria

- Red tests fail before implementation because the chain registry JSON payload
  lacks `failed_subjects`.
- Successful registry JSON reports `failed_subjects: []`.
- Drifted registry JSON reports `accepted: false` and includes the rejected
  subjects in `failed_subjects`.
- Module execution in JSON registry mode returns exit code `1` for a drifted
  registry and emits the same `failed_subjects`.
- Existing chain bundle JSON, chain registry JSON, and full repository tests
  remain green.

## Consequences

Automation can route failed chain registry validation without duplicating the
payload scanning logic that the validator already knows.

## Test Plan

- Red: `python -m unittest tests.test_chain_evidence_bundle_registry` fails
  before `failed_subjects` is added.
- Green: the same focused test passes after adding the field.
- Regression: run adjacent chain CLI/registry/bundle tests, both registry JSON
  and single-bundle JSON modes, `py_compile`, `git diff --check`, and the full
  default suite before commit.

## After Action Report

Implemented in `autarkic_systems/chain_evidence_bundle.py`, with focused
tests in `tests/test_chain_evidence_bundle_registry.py`.

The focused red run failed because `chain_registry_validation_report_payload`
did not include `failed_subjects`. The green implementation adds an ordered
`failed_subjects` list derived from rejected validation results.

The first green attempt showed an important boundary: a drifted in-place
registry with a missing registered bundle also leaves the real sibling bundle
unregistered, so `registry-completeness` correctly appears in
`failed_subjects` alongside the missing path and bundle-validation failures.

Verification passed:

- focused red:
  `python -m unittest tests.test_chain_evidence_bundle_registry` failed before
  `failed_subjects` was added;
- focused green:
  `python -m unittest tests.test_chain_evidence_bundle_registry` passed 12
  tests;
- adjacent chain CLI/registry/bundle tests passed 22 tests;
- `python -m autarkic_systems.chain_evidence_bundle --registry
  evidence/chains/manifest.json --format json` reported `accepted: true`,
  `bundle_count: 1`, and `failed_subjects: []`;
- `python -m autarkic_systems.chain_evidence_bundle --format json` still
  reported `accepted: true` and `result_count: 9`;
- `py_compile` passed for the touched module and focused test;
- `git diff --check` passed; and
- `python -m unittest discover` passed 506 tests.
