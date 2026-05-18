# ADR-0188: Proof Rule Status Summary

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0172 through ADR-0187 migrated the checked transition and transition-chain
proof-certificate manifests away from implicit `manifest-example` steps and
toward explicit `predicate-result` steps. The verifiers and tests now enforce
that migration, but the aggregate project status report still only reports
claim and certificate counts.

That leaves an operator-visible gap: a status reader can see that proof
certificates are green, but cannot see which proof rules the checked manifests
actually use without opening the JSON files or reading individual verifier
details.

## Decision

Add a proof-rule audit summary to the aggregate project status report. The
summary will count proof-certificate steps by rule for the checked transition
manifest, the checked transition-chain manifest, and their combined surface.
The text status report will render the combined count compactly so the
`predicate-result` migration is visible from the operator command.

## Success Criteria

- Red tests fail before implementation because project status JSON has no
  proof-rule audit summary and text status does not render one.
- Project status JSON includes `proof_rule_audit` with transition, chain, and
  combined step counts.
- The default checked manifests report zero `manifest-example` steps and 49
  `predicate-result` steps across transition and chain certificates.
- Text status renders `Proof rule audit: predicate-result=49,
  manifest-example=0`.
- If a certificate manifest cannot be loaded, the audit reports a rejected
  source with the corresponding failure subject instead of raising a traceback.
- Full repository tests remain green.

## Test Plan

- Red:
  `python -m unittest tests.test_project_status_report`
  fails before status summary implementation.
- Green: the same focused suite passes after implementing the audit.
- Regression: run `python -m autarkic_systems.project_status --format json`,
  `python -m autarkic_systems.project_status`, `python -m compileall -q
  autarkic_systems tests`, `git diff --check`, and the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_project_status_report` run executed 74 tests and
failed because project status still reported `schema_version: 15`, had no
`proof_rule_audit` JSON payload, and did not render a proof-rule text line.

The implementation added a project-status proof-rule audit that loads the
checked transition and transition-chain proof-certificate manifests through the
existing certificate loader, counts steps by rule, reports transition, chain,
and combined counts, and fails closed with source-specific failed subjects when
a certificate manifest cannot be loaded. It bumped project status to
`schema_version: 16` and renders the accepted combined audit as
`Proof rule audit: predicate-result=49, manifest-example=0`.

The focused project-status suite then passed with 74 tests. Text and JSON
project-status commands accepted the updated surface. JSON parsing for both
checked proof-certificate manifests, `compileall`, `git diff --check`, and the
full default suite also passed; the full suite ran 789 tests.
