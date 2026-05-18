# ADR-0195: Complete Network Witness Fixture Surface

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0194 added a bounded two-cell network witness with tests covering five
behavioral shapes: consumed init delivery, consumed write-buffer delivery,
standard-signal rejection, recipient-not-ready blocked handoff, and
sender-not-delivered failure. The CLI exposes the three installed-delivery
cases, but not the two failure-shape witnesses.

That leaves an operator-visible gap: the text/JSON witness command cannot show
the same failure boundaries that the module already records and tests.

## Decision

Add named CLI fixture cases for `recipient-not-ready` and
`sender-not-delivered`. These fixtures will use the existing witness executor
and will not add new transition behavior.

## Success Criteria

- Red tests fail before implementation because the new fixture names are not
  accepted by the CLI.
- `recipient-not-ready` JSON output reports status `recipient-not-ready`,
  `accepted: false`, no delivered tuple, no recipient-before-step state, and no
  recipient step.
- `sender-not-delivered` text output reports status `sender-not-delivered`,
  `accepted: false`, and only a sender-step event.
- The operator note lists all five checked fixture cases.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_two_cell_network_witness`.
- Green: the same focused suite passes after implementation.
- Regression: run both new CLI fixture cases, `python -m compileall -q
  autarkic_systems tests`, `git diff --check`, and the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_two_cell_network_witness` run failed because
`recipient-not-ready` and `sender-not-delivered` were rejected by the witness
CLI fixture parser.

The implementation added both fixture constructors to
`autarkic_systems/network_witness.py` and documented the full five-case fixture
surface in `docs/two-cell-network-witness.md`. The new fixtures reuse the
existing witness executor and do not add transition behavior.

The focused witness suite passed with 11 tests. Live JSON/text runs for both
new fixture cases returned nonzero witness status while emitting the expected
operator payloads. `compileall`, `git diff --check`, and the full default suite
also passed; the full suite ran 816 tests.
