# ADR-0199: Project Status Sequence Evidence

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0198 added a checked network-sequence evidence registry for the
post-handoff signal witness. The aggregate project-status command still checks
only transition evidence, transition-chain evidence, claim/language/proof
surfaces, and source-status frontiers. That leaves the main operator report
blind to the newest evidence surface.

The status command should not report the project accepted while ignoring a
malformed or missing network-sequence evidence registry.

## Decision

Add network-sequence evidence to `autarkic_systems.project_status`:

- load and validate `evidence/sequences/manifest.json`;
- expose `sequence_evidence` in JSON;
- include sequence evidence in the aggregate accepted state;
- render sequence evidence in full text and compact summary modes;
- add a CLI `--sequence-registry` override; and
- bump project-status schema version.

This does not add new sequence behavior, evidence artifacts, or command
semantics.

## Success Criteria

- Red tests fail before implementation because project status still reports
  schema version `16`, has no `sequence_evidence`, and rejects
  `--sequence-registry`.
- JSON project status includes accepted sequence evidence with one bundle.
- Text project status renders sequence evidence and bundle listing.
- Summary mode includes the sequence evidence count.
- Missing sequence registry makes project status rejected with structured
  `registry-file` failure.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run project-status text/summary/JSON, refreshed handoff,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented.

The red project-status run executed 78 tests and failed because aggregate
status still reported schema version `16`, had no `sequence_evidence`, omitted
network-sequence evidence from text and summary output, rejected
`--sequence-registry`, and did not accept `sequence_registry_path` in the
builder.

The implementation reuses the existing network-sequence evidence-bundle
registry validator, exposes `sequence_evidence` in JSON, includes that registry
in aggregate acceptance, renders the accepted one-bundle sequence registry in
text and summary output, and makes missing sequence registries a structured
`registry-file` failure.

Focused verification passed 78 project-status tests after implementation. The
first full regression run then exposed stale handoff test fixtures that built
schema-16-shaped project-status payloads; updating those fixtures to include
`sequence_evidence` restored the suite. Final verification passed 845 tests.
