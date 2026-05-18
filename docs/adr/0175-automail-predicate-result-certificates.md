# ADR-0175: Automail Predicate Result Certificates

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0133 introduced `predicate-result` proof-certificate steps for the first
fixed-cell claim. ADR-0172 through ADR-0174 completed that explicit
predicate-named proof-step shape for the four original fixed-cell transition
predicates. The next certificate in the transition claim manifest,
`UC-STEM-AUTOMAIL-RECONFIGURES`, still relies on `manifest-example` proof
steps.

Stem automail reconfiguration is the first reconfiguration predicate in the AS
runtime surface. Migrating its certificate keeps proof objects moving from
implicit manifest lookup toward directly named predicate results without
changing runtime behavior, transition claims, object-language schema, evidence
bundles, source-status records, or project-status schema versions.

## Decision

Migrate `UC-STEM-AUTOMAIL-RECONFIGURES` from `manifest-example` proof steps to
`predicate-result` proof steps that explicitly name
`automail_reconfigures_stem`.

## Success Criteria

- Red tests fail before implementation because `UC-STEM-AUTOMAIL-RECONFIGURES`
  still uses `manifest-example`.
- The automail certificate has exactly two `predicate-result` steps.
- Both automail steps name `automail_reconfigures_stem`.
- Proof-certificate text/JSON and aggregate project-status output report the
  automail certificate as two `predicate-result` steps.
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
ran 93 tests and failed because the automail certificate still used
`manifest-example`, and proof-certificate/project-status reports still rendered
the automail certificate as two `manifest-example` steps.

The implementation migrated both `UC-STEM-AUTOMAIL-RECONFIGURES` certificate
steps to `predicate-result` and named `automail_reconfigures_stem` directly on
both steps. No runtime behavior, transition claims, object-language rules,
evidence bundles, source-status records, or status schema versions changed.

The same focused suite then passed with 93 tests. The proof-certificate CLI
JSON, project-status JSON, and object-language JSON checks accepted the
updated certificate surface. JSON parsing for the touched certificate
manifest, `compileall`, `git diff --check`, and the full default suite also
passed; the full suite ran 773 tests.
