# ADR-0194: Two-Cell Network Witness

Date: 2026-05-18

## Status

Accepted.

## Context

The current transition-chain helper composes one neighbor command-buffer
delivery with one recipient command-message step. That is useful claim
machinery, but it is still shaped as a predicate helper rather than as a
network execution witness an operator can inspect directly.

The next useful slice should add executable substance without widening PRC
semantics. The safe boundary is to reuse the existing `step_stem_cell`,
`step_fixed_cell`, and `execute_neighbor_delivery_recipient_chain` behavior and
record the two-cell run as a first-class witness: sender before/after,
recipient before delivery, recipient after, delivered tuple, and event trail.

## Decision

Add a small two-cell neighbor-delivery witness module. The witness will execute
the existing chain behavior, expose a structured payload, and provide a CLI for
known fixture cases. It will not implement a scheduler, timing model, output
clearing rule, topology engine, or new command semantics.

The witness records three possible shapes:

- sender does not produce a neighbor delivery;
- sender produces a neighbor delivery but the recipient cannot accept it
  because its input or upstream state is not empty; and
- sender delivery is installed as recipient upstream and the recipient step is
  executed, either consuming a supported command or preserving the existing
  rejection boundary.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.network_witness` does not exist.
- The witness records sender step, handoff, and recipient step events for a
  consumed neighbor delivery.
- The witness records delivered `write-buf-one` as a consumed recipient append
  without adding new command semantics.
- The witness records delivered `standard-signal` as the existing recipient
  rejection boundary.
- The witness does not install delivery or step the recipient when the
  recipient already has pending input/upstream state.
- The witness records sender-only failure when the sender does not complete a
  neighbor delivery.
- JSON and text renderers expose the same status, event trail, delivered tuple,
  and final cells.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_two_cell_network_witness`.
- Green: the same focused suite passes after implementation.
- Regression: run the witness CLI in JSON mode, `python -m compileall -q
  autarkic_systems tests`, `git diff --check`, and the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_two_cell_network_witness` run failed because
`autarkic_systems.network_witness` did not exist.

The implementation added `autarkic_systems/network_witness.py`, which delegates
execution to the existing neighbor-delivery chain helper and records a
network-shaped witness with sender before/after state, recipient before state,
optional recipient-before-step state, final recipient state, installed delivered
tuple, event trail, text output, JSON output, and named CLI fixture cases.

The focused two-cell network witness suite passed with 9 tests. The JSON CLI
fixture for delivered `write-buf-one` reports the same delivered tuple and final
recipient buffer as the direct witness payload. `compileall`, `git diff
--check`, and the full default suite also passed; the full suite ran 814 tests.
