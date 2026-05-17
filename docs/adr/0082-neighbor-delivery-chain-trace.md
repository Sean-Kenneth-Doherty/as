# ADR-0082: Neighbor Delivery Chain Trace

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0077 introduced the first executable two-step transition chain. ADR-0078
through ADR-0081 then added a chain claim, proof certificate, chain object
language, CLI, and evidence bundle.

The chain is now machine-checkable, but the actual two-cell handoff is still
hard to inspect. Operators can see the single sender transition and the single
recipient transition as separate schematic traces, but there is no dedicated
trace artifact that records the composed sender step, delivered tuple,
recipient pre-handoff state, recipient post-handoff state, and whole-chain
status in one place.

## Decision

Add a transition-chain trace artifact:

- `schematics/chains/neighbor_delivery_recipient_chain_trace.json`;
- `autarkic_systems/chain_trace.py`; and
- `tests/test_neighbor_delivery_chain_trace.py`.

The validator will:

- replay the sender step;
- verify the delivered output tuple;
- verify that the delivered tuple is installed as recipient upstream state;
- replay the recipient step;
- replay the complete chain helper; and
- reject drifted handoff tuples or recipient outcomes.

Update the ADR-0081 chain evidence bundle so it names and validates the new
chain trace. This keeps the composed-chain evidence object current without
adding it to the single-transition evidence registry.

This ADR does not add SVG rendering, scheduler semantics, topology semantics,
multi-cell timing, or new Universal Cell behavior.

## Success Criteria

- Red tests fail before implementation because `autarkic_systems.chain_trace`
  and the chain trace artifact are absent.
- The trace records the chain claim ID, chain helper, expected chain status,
  sender transition, handoff tuple, recipient initial state, recipient
  handoff state, and recipient transition.
- Validation rejects a drifted handoff tuple.
- Validation rejects a drifted recipient after-cell.
- The ADR-0081 chain evidence bundle validates the new chain trace.
- Existing chain claim, chain evidence, single-transition evidence registry,
  and full repository tests remain green.

## Consequences

The first transition chain becomes inspectable as a single recorded handoff
instead of only as two separate transition traces plus a Python helper. A
future ADR can render this chain trace as SVG without inventing the trace
schema at the same time.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_chain_trace
  tests.test_neighbor_delivery_chain_evidence_bundle` fails before the module
  and trace artifact exist.
- Green: the same focused tests pass after adding the trace validator and
  updating the evidence bundle.
- Regression: run adjacent chain/evidence tests, `jq` on the new trace, both
  chain CLIs, the existing evidence registry CLI, `py_compile`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented in `schematics/chains/neighbor_delivery_recipient_chain_trace.json`
and `autarkic_systems/chain_trace.py`, with focused tests in
`tests/test_neighbor_delivery_chain_trace.py`.

The focused red run failed because `autarkic_systems.chain_trace` was absent,
`chain_trace_path` was missing from the ADR-0081 evidence bundle model, and
`chain-trace` was not yet a chain evidence validation subject.

The green implementation adds a recorded two-step handoff trace with:

- sender `step_stem_cell` replay;
- delivered tuple validation from sender `output` to recipient `upstream`;
- recipient `step_fixed_cell` replay;
- full `execute_neighbor_delivery_recipient_chain` replay; and
- explicit scheduler, topology, non-init, `standard-signal`, and write-buffer
  boundaries.

The ADR-0081 evidence bundle now names
`schematics/chains/neighbor_delivery_recipient_chain_trace.json` and validates
it through `chain-trace`, while the top-level transition evidence registry
remains unchanged at eight single-transition bundles.

Verification passed:

- focused red:
  `python -m unittest tests.test_neighbor_delivery_chain_trace
  tests.test_neighbor_delivery_chain_evidence_bundle` failed before
  implementation;
- focused green:
  `python -m unittest tests.test_neighbor_delivery_chain_trace
  tests.test_neighbor_delivery_chain_evidence_bundle` passed 15 tests;
- adjacent chain/trace/evidence stack passed 85 tests;
- `jq` parsed the new chain trace and updated chain evidence bundle;
- `py_compile` passed for the new/touched modules and focused tests;
- `python -m autarkic_systems.chain_evidence_bundle --format json` reported
  `accepted: true`, `result_count: 8`, and an accepted `chain-trace` subject;
- `python -m autarkic_systems.chain_claims --format json` still reported
  `accepted: true`;
- the existing transition evidence registry JSON CLI still reported
  `accepted: true` and `bundle_count: 8`;
- `git diff --check` passed; and
- `python -m unittest discover` passed 486 tests.
