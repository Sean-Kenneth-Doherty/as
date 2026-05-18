# ADR-0180: Self Command-Buffer Init Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0172 through ADR-0179 progressively migrated early transition proof
certificates from implicit `manifest-example` steps to explicit
`predicate-result` steps. The next transition certificate in the manifest,
`UC-STEM-COMMAND-BUFFER-SELF-INIT`, still uses `manifest-example` proof steps
even though the object language already names its predicate as
`stem_command_buffer_executes_self_init`.

This claim is the completed self-target command-buffer init dispatch slice.
Migrating its certificate continues the proof-object hardening path without
changing runtime behavior, transition claims, object-language schema, evidence
bundles, source-status records, or project-status schema versions.

## Decision

Migrate `UC-STEM-COMMAND-BUFFER-SELF-INIT` from `manifest-example` proof steps
to `predicate-result` proof steps that explicitly name
`stem_command_buffer_executes_self_init`.

## Success Criteria

- Red tests fail before implementation because
  `UC-STEM-COMMAND-BUFFER-SELF-INIT` still uses `manifest-example`.
- The self command-buffer init certificate has exactly two
  `predicate-result` steps.
- Both self command-buffer init steps name
  `stem_command_buffer_executes_self_init`.
- Proof-certificate text/JSON and aggregate project-status output report the
  self command-buffer init certificate as two `predicate-result` steps.
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
ran 98 tests and failed because the self command-buffer init certificate still
used `manifest-example`, and proof-certificate/project-status reports still
rendered the self command-buffer init certificate as two `manifest-example`
steps.

The implementation migrated both `UC-STEM-COMMAND-BUFFER-SELF-INIT`
certificate steps to `predicate-result` and named
`stem_command_buffer_executes_self_init` directly on both steps. No runtime
behavior, transition claims, object-language rules, evidence bundles,
source-status records, or status schema versions changed.

The same focused suite then passed with 98 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the updated
certificate surface. JSON parsing for the touched certificate manifest,
`compileall`, `git diff --check`, and the full default suite also passed; the
full suite ran 778 tests.
