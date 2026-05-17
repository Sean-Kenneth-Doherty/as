# ADR-0090: Chain Demo Artifact Presence

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0089 added a vertical chain demo report that lists the evidence layers for
the current neighbor delivery recipient-consumption chain. The underlying chain
evidence validator checks the loaded artifacts, but the demo payload itself
does not say whether each listed evidence path exists.

For a first-run report, implicit artifact presence is too indirect. A user or
automation consumer should be able to inspect the demo output and immediately
see whether the listed claim, proof, language, trace, SVG, transition-bundle,
and source-status files are present.

## Decision

Extend the vertical chain demo payload so every evidence layer includes an
`exists` flag, and add a top-level `missing_evidence_paths` list. Text output
will summarize missing paths explicitly.

This ADR does not change chain evidence validation semantics. The demo remains
a reporting surface over the existing validator.

## Success Criteria

- Red tests fail before implementation because demo evidence layers lack
  `exists` and the report lacks `missing_evidence_paths`.
- The checked-in demo reports all evidence layers present and
  `missing_evidence_paths: []`.
- A drifted bundle that points at a missing source-status file reports that
  path in `missing_evidence_paths` and marks the corresponding layer
  `exists: false`.
- Text output reports `Missing evidence paths: none` for the checked-in
  bundle.
- Existing demo tests, adjacent chain evidence tests, and the full default
  suite remain green.

## Consequences

The vertical demo becomes a stronger operator-facing artifact: it no longer
asks readers to infer artifact presence from validator internals.

## Test Plan

- Red: `python -m unittest tests.test_chain_demo_report` fails before the
  presence fields are added.
- Green: the same focused test passes after implementation.
- Regression: run adjacent chain demo/evidence tests, demo CLI text/JSON,
  `py_compile`, `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented artifact-presence reporting in `autarkic_systems.chain_demo`
without changing the underlying chain evidence validation semantics.

The red focused run, before implementation, failed in
`tests.test_chain_demo_report` because demo evidence layers lacked `exists`,
the report lacked `missing_evidence_paths`, and text output did not summarize
missing paths. After implementation:

- `python -m unittest tests.test_chain_demo_report` passed 7 tests.
- `python -m unittest tests.test_chain_demo_report tests.test_neighbor_delivery_chain_evidence_bundle tests.test_chain_evidence_bundle_registry tests.test_chain_evidence_cli_target_selection`
  passed 31 tests.
- `python -m autarkic_systems.chain_demo` printed `Missing evidence paths:
  none` for the checked-in bundle.
- `python -m autarkic_systems.chain_demo --format json` reported
  `missing_evidence_paths: []` and `exists: true` for every listed evidence
  layer.
- `python -m py_compile autarkic_systems/chain_demo.py tests/test_chain_demo_report.py`
  passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 515 tests.

The demo report now makes artifact presence part of the first-run surface
instead of leaving it implicit in lower-level validator details.
