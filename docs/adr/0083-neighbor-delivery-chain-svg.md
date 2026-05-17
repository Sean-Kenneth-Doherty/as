# ADR-0083: Neighbor Delivery Chain SVG

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0082 records the first composed transition-chain trace as JSON. The trace
is machine-checkable, but operators still have to read nested sender,
handoff, and recipient records to see the two-cell shape.

The single-transition schematic traces already have generated SVG views whose
checked-in artifacts must exactly match renderer output. The chain trace
should get the same drift-resistant visual treatment, while keeping the JSON
trace as the source of truth.

## Decision

Add a deterministic renderer and checked SVG artifact for the neighbor delivery
recipient chain:

- `autarkic_systems/chain_svg.py`;
- `schematics/chains/neighbor_delivery_recipient_chain_trace.svg`; and
- `tests/test_neighbor_delivery_chain_svg.py`.

The renderer will expose the sender step, delivered tuple, recipient step,
whole-chain status, and both recorded routed-signal-flow lists.

Update the ADR-0081 chain evidence bundle so it names and validates the new
chain SVG. This keeps the composed-chain evidence object aligned with its
human-facing visual artifact.

This ADR does not add a scheduler, topology model, multi-cell timing, new
Universal Cell behavior, or a general SVG renderer for arbitrary chain graphs.

## Success Criteria

- Red tests fail before implementation because `autarkic_systems.chain_svg`
  and the checked SVG artifact are absent.
- The rendered SVG is nonblank XML with chain trace metadata.
- The SVG exposes sender, recipient, handoff, delivered tuple, whole-chain
  status, and both routed signal-flow lists.
- The checked SVG exactly matches renderer output.
- The SVG validator rejects drifted handoff text.
- The ADR-0081 chain evidence bundle validates the new chain SVG.
- Existing chain trace, chain evidence, single-transition evidence registry,
  and full repository tests remain green.

## Consequences

The first composed chain now has a human-readable visual artifact with the same
renderer-output drift protection as the existing single-transition schematic
SVGs. The renderer is deliberately narrow; future chain shapes should widen it
through new ADRs rather than silently pretending the current two-cell view is a
general topology renderer.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_chain_svg
  tests.test_neighbor_delivery_chain_evidence_bundle` fails before the module
  and SVG artifact exist.
- Green: the same focused tests pass after adding the renderer, SVG, and
  evidence-bundle linkage.
- Regression: run adjacent chain trace/evidence tests, both chain CLIs, the
  existing evidence registry CLI, `py_compile`, XML parsing, `git diff
  --check`, and the full default suite before commit.

## After Action Report

Implemented in `schematics/chains/neighbor_delivery_recipient_chain_trace.svg`
and `autarkic_systems/chain_svg.py`, with focused tests in
`tests/test_neighbor_delivery_chain_svg.py`.

The focused red run failed because `autarkic_systems.chain_svg` was absent,
`chain_svg_path` was missing from the ADR-0081 evidence bundle model, and
`chain-svg` was not yet a chain evidence validation subject.

The green implementation adds a narrow two-cell SVG renderer for the ADR-0082
chain trace. The renderer exposes sender step, recipient step, whole-chain
status, output-to-upstream handoff, delivered tuple, and both routed-signal
flow lists. The checked SVG must exactly match renderer output.

The first focused green attempt caught a trailing blank-line mismatch in the
committed SVG, which confirmed that exact-render validation is doing useful
work. After fixing the artifact, the chain evidence bundle accepted the SVG
through the new `chain-svg` subject.

Verification passed:

- focused red:
  `python -m unittest tests.test_neighbor_delivery_chain_svg
  tests.test_neighbor_delivery_chain_evidence_bundle` failed before
  implementation;
- focused green:
  `python -m unittest tests.test_neighbor_delivery_chain_svg
  tests.test_neighbor_delivery_chain_evidence_bundle` passed 14 tests;
- adjacent chain/trace/SVG/evidence stack passed 105 tests;
- XML parsing passed for
  `schematics/chains/neighbor_delivery_recipient_chain_trace.svg`;
- `jq` parsed the updated chain evidence bundle;
- `py_compile` passed for the new/touched modules and focused tests;
- `python -m autarkic_systems.chain_evidence_bundle --format json` reported
  `accepted: true`, `result_count: 9`, and an accepted `chain-svg` subject;
- `python -m autarkic_systems.chain_claims --format json` still reported
  `accepted: true`;
- the existing transition evidence registry JSON CLI still reported
  `accepted: true` and `bundle_count: 8`;
- `git diff --check` passed; and
- `python -m unittest discover` passed 492 tests.
