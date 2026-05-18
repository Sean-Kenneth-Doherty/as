# ADR-0179: Self-Mailbox Write-Buffer Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0172 through ADR-0178 progressively migrated early transition proof
certificates from implicit `manifest-example` steps to explicit
`predicate-result` steps. The next transition certificate in the manifest,
`UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED`, still uses `manifest-example`
proof steps even though the object language already names its predicate as
`self_mailbox_write_buffer_appends_literal`.

This claim is the direct self-mailbox write-buffer append slice added after
the source-status boundary was resolved. Migrating its certificate continues
the proof-object hardening path without changing runtime behavior, transition
claims, object-language schema, evidence bundles, source-status records, or
project-status schema versions.

## Decision

Migrate `UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED` from `manifest-example`
proof steps to `predicate-result` proof steps that explicitly name
`self_mailbox_write_buffer_appends_literal`.

## Success Criteria

- Red tests fail before implementation because
  `UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED` still uses
  `manifest-example`.
- The self-mailbox write-buffer certificate has exactly three
  `predicate-result` steps.
- All self-mailbox write-buffer steps name
  `self_mailbox_write_buffer_appends_literal`.
- Proof-certificate text/JSON and aggregate project-status output report the
  self-mailbox write-buffer certificate as three `predicate-result` steps.
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
ran 97 tests and failed because the self-mailbox write-buffer certificate still
used `manifest-example`, and proof-certificate/project-status reports still
rendered the self-mailbox write-buffer certificate as three `manifest-example`
steps.

The implementation migrated all three
`UC-STEM-SELF-MAILBOX-WRITE-BUFFER-APPENDED` certificate steps to
`predicate-result` and named `self_mailbox_write_buffer_appends_literal`
directly on each step. No runtime behavior, transition claims,
object-language rules, evidence bundles, source-status records, or status
schema versions changed.

The same focused suite then passed with 97 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the updated
certificate surface. JSON parsing for the touched certificate manifest,
`compileall`, `git diff --check`, and the full default suite also passed; the
full suite ran 777 tests.
