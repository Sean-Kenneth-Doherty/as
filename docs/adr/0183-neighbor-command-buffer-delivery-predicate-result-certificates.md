# ADR-0183: Neighbor Command-Buffer Delivery Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0172 through ADR-0182 progressively migrated early transition proof
certificates from implicit `manifest-example` steps to explicit
`predicate-result` steps. The next transition certificate in the manifest,
`UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED`, still uses `manifest-example`
proof steps even though the object language already names its predicate as
`stem_command_buffer_delivers_neighbor_command`.

This claim is the completed neighbor-target command-buffer delivery slice.
Migrating its certificate continues the proof-object hardening path without
changing runtime behavior, transition claims, object-language schema, evidence
bundles, source-status records, or project-status schema versions.

## Decision

Migrate `UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` from
`manifest-example` proof steps to `predicate-result` proof steps that explicitly
name `stem_command_buffer_delivers_neighbor_command`.

## Success Criteria

- Red tests fail before implementation because
  `UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` still uses `manifest-example`.
- The neighbor command-buffer delivery certificate has exactly two
  `predicate-result` steps.
- All neighbor command-buffer delivery steps name
  `stem_command_buffer_delivers_neighbor_command`.
- Proof-certificate text/JSON and aggregate project-status output report the
  neighbor command-buffer delivery certificate as two `predicate-result` steps.
- Full repository tests remain green.

## Test Plan

- Red:
  `python -m unittest tests.test_proof_certificates tests.test_project_status_report`
  fails before the proof-certificate manifest update.
- Green: the same focused suite passes after updating
  `claims/proof_certificates.json` and expected status output.
- Regression: run JSON parsing for touched JSON, proof-certificate CLI JSON,
  project-status JSON, object-language JSON, `compileall`, `git diff --check`,
  and the full default suite before commit.

## After Action Report

Implemented. The focused red run
`python -m unittest tests.test_proof_certificates tests.test_project_status_report`
ran 101 tests and failed because the neighbor command-buffer delivery
certificate still used `manifest-example`, and proof-certificate/project-status
reports still rendered the neighbor delivery certificate as two
`manifest-example` steps.

The implementation migrated both
`UC-STEM-COMMAND-BUFFER-NEIGHBOR-DELIVERED` certificate steps to
`predicate-result` and named `stem_command_buffer_delivers_neighbor_command`
directly on every step. No runtime behavior, transition claims, object-language
rules, evidence bundles, source-status records, or status schema versions
changed.

The same focused suite then passed with 101 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the updated
certificate surface. JSON parsing for the touched certificate manifest,
`compileall`, `git diff --check`, and the full default suite also passed; the
full suite ran 781 tests.
