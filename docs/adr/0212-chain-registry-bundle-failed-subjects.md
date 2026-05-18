# ADR-0212: Chain Registry Bundle Failed Subjects

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0211 made network-sequence registry JSON expose inner failed subjects for
loadable rejected bundles. The older transition-chain registry still reports
only registry-level subjects such as `registry-bundle-validation`.

That means a chain registry automation consumer can see that a registered
bundle rejected, but must parse a detail string or rerun bundle validation to
learn whether the failing inner layer was `chain-claim-example`,
`chain-trace`, `chain-svg`, or another validation subject.

## Decision

Extend `chain_registry_validation_report_payload` with
`bundle_failed_subjects`, an ordered list of rejected validation subjects from
each loadable registered transition-chain evidence bundle:

- accepted registries report `bundle_failed_subjects: []`;
- rejected existing bundles report `{bundle_id, failed_subjects}` entries; and
- missing registered bundle files keep the existing registry-level
  missing-path behavior and do not add bundle-level subjects.

This does not change registry acceptance semantics, text formatting, project
status schema, demo registry schema, runtime behavior, claims, proof rules,
source-status boundaries, trace/SVG rendering, scheduler, topology, timing, or
command semantics.

## Success Criteria

- Red tests fail before implementation because chain registry JSON lacks
  `bundle_failed_subjects`.
- Accepted chain registry JSON reports `bundle_failed_subjects: []`.
- A registry pointing at a drifted existing chain bundle reports its bundle ID
  and inner failed subjects.
- CLI JSON emits the same field.
- Existing missing-bundle registry behavior remains unchanged.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_chain_evidence_bundle_registry`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent chain evidence/demo/project-status tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/chain_evidence_bundle.py`, with focused
coverage in `tests/test_chain_evidence_bundle_registry.py` and operator notes
in `docs/chain-evidence-bundle-registry.md`.

The red focused run failed as intended because accepted direct and CLI chain
registry JSON lacked `bundle_failed_subjects`, and a registry pointing at a
drifted existing chain bundle could not expose `chain-claim-example` or
`chain-trace` without parsing `registry-bundle-validation`.

The implementation adds `bundle_failed_subjects` to
`chain_registry_validation_report_payload`, populated from loadable registered
bundle validation results. Missing registered bundle paths continue to report
the existing registry-level `registry-bundle-paths` and
`registry-bundle-validation` subjects while leaving `bundle_failed_subjects`
empty.

Focused chain evidence-bundle registry tests passed 14 tests. Adjacent
chain-demo/project-status tests passed 112 tests. Live chain registry JSON
reported `accepted: true`, `bundle_count: 2`, and
`bundle_failed_subjects: []`. `compileall`, `git diff --check`, and the full
default suite passed; the full suite ran 900 tests.
