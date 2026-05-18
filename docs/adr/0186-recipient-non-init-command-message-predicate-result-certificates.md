# ADR-0186: Recipient Non-Init Command-Message Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0172 through ADR-0185 progressively migrated transition proof certificates
from implicit `manifest-example` steps to explicit `predicate-result` steps.
The final remaining transition certificate in the manifest,
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED`, still uses
`manifest-example` proof steps even though the object language already names its
predicate as `recipient_non_init_command_message_rejected`.

This claim is the recipient-side blocked non-init and command-conflict rejection
boundary. Migrating its certificate completes the current transition
proof-certificate hardening path without changing runtime behavior, transition
claims, object-language schema, evidence bundles, source-status records, or
project-status schema versions.

## Decision

Migrate `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` from
`manifest-example` proof steps to `predicate-result` proof steps that explicitly
name `recipient_non_init_command_message_rejected`.

## Success Criteria

- Red tests fail before implementation because
  `UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` still uses
  `manifest-example`.
- The recipient non-init command-message certificate has exactly four
  `predicate-result` steps.
- All recipient non-init command-message steps name
  `recipient_non_init_command_message_rejected`.
- Proof-certificate text/JSON and aggregate project-status output report the
  recipient non-init command-message certificate as four `predicate-result`
  steps.
- The checked transition proof-certificate manifest no longer contains
  `manifest-example` rules.
- Full repository tests remain green.

## Test Plan

- Red:
  `python -m unittest tests.test_proof_certificates tests.test_project_status_report`
  fails before the proof-certificate manifest update.
- Green: the same focused suite passes after updating
  `claims/proof_certificates.json` and expected status output.
- Regression: run JSON parsing for touched JSON, proof-certificate CLI JSON,
  project-status JSON, object-language JSON, `compileall`, `git diff --check`,
  a direct check that transition proof certificates contain no
  `manifest-example` rules, and the full default suite before commit.

## After Action Report

Implemented. The focused red run
`python -m unittest tests.test_proof_certificates tests.test_project_status_report`
ran 104 tests and failed because the recipient non-init command-message
certificate still used `manifest-example`, proof-certificate/project-status
reports still rendered the recipient non-init certificate as four
`manifest-example` steps, and the report text still contained
`manifest-example`.

The implementation migrated all four
`UC-RECIPIENT-NON-INIT-COMMAND-MESSAGE-REJECTED` certificate steps to
`predicate-result` and named `recipient_non_init_command_message_rejected`
directly on every step. No runtime behavior, transition claims, object-language
rules, evidence bundles, source-status records, or status schema versions
changed.

The same focused suite then passed with 104 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the updated
certificate surface. A direct `rg` check confirmed the transition
proof-certificate manifest no longer contains `manifest-example` rules. JSON
parsing for the touched certificate manifest, `compileall`, `git diff --check`,
and the full default suite also passed; the full suite ran 784 tests.
