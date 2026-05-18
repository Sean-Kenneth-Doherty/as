# ADR-0211: Sequence Registry Bundle Failed Subjects

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0209 added inner network-sequence bundle failure subjects to project
status, and ADR-0210 added the same legibility to the network-sequence demo
registry. Those callers currently have to recover bundle-level subjects from
per-bundle reports or by revalidating registered bundles.

The source registry validation payload in
`autarkic_systems.network_sequence_evidence_bundle` still only reports
registry-level failed subjects such as `registry-bundle-validation`. That is
structured, but too coarse for automation that wants to know whether a
registered existing bundle failed at `sequence-witness`, `sequence-trace`,
`sequence-svg`, or another inner evidence layer.

## Decision

Extend `network_sequence_registry_validation_report_payload` with
`bundle_failed_subjects`, an ordered list of rejected validation subjects from
each loadable registered network-sequence evidence bundle:

- accepted registries report `bundle_failed_subjects: []`;
- rejected existing bundles report `{bundle_id, failed_subjects}` entries; and
- missing registered bundle files keep the existing registry-level
  missing-path behavior.

This does not change registry acceptance semantics, text formatting, project
status schema, demo registry schema, runtime behavior, claims, proof rules,
source-status boundaries, trace/SVG rendering, scheduler, topology, timing, or
command semantics.

## Success Criteria

- Red tests fail before implementation because registry JSON lacks
  `bundle_failed_subjects`.
- Accepted registry JSON reports `bundle_failed_subjects: []`.
- A registry pointing at a drifted existing bundle reports its bundle ID and
  inner failed subjects.
- CLI JSON emits the same field.
- Existing missing-bundle registry behavior remains unchanged.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_evidence_bundle`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent network-sequence evidence/demo/project-status tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/network_sequence_evidence_bundle.py`, with
focused coverage in `tests/test_network_sequence_evidence_bundle.py` and
operator notes in `docs/network-sequence-evidence-bundles.md`.

The red focused run failed as intended because accepted direct and CLI registry
JSON lacked `bundle_failed_subjects`, and a registry pointing at a drifted
existing sequence bundle could not expose `sequence-witness` or
`sequence-trace` without parsing `registry-bundle-validation`.

The implementation adds `bundle_failed_subjects` to
`network_sequence_registry_validation_report_payload`, populated from
loadable registered bundle validation results. Missing registered bundle paths
continue to report the existing registry-level `registry-bundle-paths` and
`registry-bundle-validation` subjects while leaving `bundle_failed_subjects`
empty. Project status now consumes the source payload and preserves its
existing flattened `sequence_evidence.bundle_failed_subjects` contract.

Focused network-sequence evidence-bundle tests passed 16 tests. Adjacent
evidence/demo/project-status tests passed 115 tests. Live sequence registry
JSON reported `accepted: true`, `bundle_count: 1`, and
`bundle_failed_subjects: []`; live project-status JSON remained accepted at
`schema_version: 20` with accepted-path `bundle_failed_subjects: []`.
`compileall`, `git diff --check`, and the full default suite passed; the full
suite ran 898 tests.
