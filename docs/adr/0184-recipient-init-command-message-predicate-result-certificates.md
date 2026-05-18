# ADR-0184: Recipient Init Command-Message Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0172 through ADR-0183 progressively migrated early transition proof
certificates from implicit `manifest-example` steps to explicit
`predicate-result` steps. The next transition certificate in the manifest,
`UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED`, still uses `manifest-example`
proof steps even though the object language already names its predicate as
`recipient_init_command_message_processed`.

This claim is the recipient-side init-family command-message execution slice.
Migrating its certificate continues the proof-object hardening path without
changing runtime behavior, transition claims, object-language schema, evidence
bundles, source-status records, or project-status schema versions.

## Decision

Migrate `UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED` from `manifest-example`
proof steps to `predicate-result` proof steps that explicitly name
`recipient_init_command_message_processed`.

## Success Criteria

- Red tests fail before implementation because
  `UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED` still uses `manifest-example`.
- The recipient init command-message certificate has exactly three
  `predicate-result` steps.
- All recipient init command-message steps name
  `recipient_init_command_message_processed`.
- Proof-certificate text/JSON and aggregate project-status output report the
  recipient init command-message certificate as three `predicate-result` steps.
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
ran 102 tests and failed because the recipient init command-message certificate
still used `manifest-example`, and proof-certificate/project-status reports
still rendered the recipient init command-message certificate as three
`manifest-example` steps.

The implementation migrated all three
`UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED` certificate steps to
`predicate-result` and named `recipient_init_command_message_processed`
directly on every step. No runtime behavior, transition claims, object-language
rules, evidence bundles, source-status records, or status schema versions
changed.

The same focused suite then passed with 102 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the updated
certificate surface. JSON parsing for the touched certificate manifest,
`compileall`, `git diff --check`, and the full default suite also passed; the
full suite ran 782 tests.
