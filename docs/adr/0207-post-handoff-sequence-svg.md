# ADR-0207: Post-Handoff Sequence SVG

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0205 added a checked JSON trace for the accepted post-handoff sequence, and
ADR-0206 made the network-sequence evidence bundle fail closed over that trace.
The trace is auditable, but it is still a JSON-only artifact. The transition
and transition-chain layers both have renderer-locked SVG views for their
checked traces, which makes the evidence stack easier to inspect.

The post-handoff sequence should have the same kind of deterministic visual
artifact: not as a new simulator or semantic authority, but as a checked
projection of the trace.

## Decision

Add a rendered SVG view for the post-handoff sequence trace:

- `autarkic_systems.network_sequence_svg`;
- `schematics/sequences/post_handoff_signal_sequence_trace.svg`;
- renderer-locked validation against the checked sequence trace;
- visible metadata, delivery tuple, follow-up input/status, recipient
  before/after follow-up state, and routed signal-flow text; and
- tests for XML validity, metadata, visible labels, committed render equality,
  validator acceptance, and drift rejection.

This does not add runtime behavior, claims, proof rules, evidence-bundle
fields, project-status fields, scheduler, topology, timing, or command
semantics.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.network_sequence_svg` does not exist.
- The renderer emits nonblank SVG with trace artifact ID, claim ID, and helper
  metadata.
- The SVG visibly names the accepted delivery, follow-up, recipient state, and
  routed signal-flow notes from the trace.
- The committed SVG exactly matches renderer output.
- The SVG validator accepts the committed SVG and rejects drifted text.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_post_handoff_sequence_svg`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent sequence trace/SVG/demo/evidence tests,
  `python -m compileall -q autarkic_systems tests`, `git diff --check`, and
  the full default suite.

## After Action Report

Implemented in `autarkic_systems/network_sequence_svg.py` and
`schematics/sequences/post_handoff_signal_sequence_trace.svg`, with operator
notes in `docs/post-handoff-sequence-svg.md`.

The red focused run failed as intended because
`autarkic_systems.network_sequence_svg` did not exist. The green focused run
passed 6 tests after the renderer, validator, and committed SVG artifact were
added.

Adjacent sequence SVG/trace/witness/demo/evidence tests passed 46 tests. Direct
SVG validation accepted 5 subjects: XML, metadata, renderer output, sequence
labels, and follow-up flow. The committed SVG is nonblank at 4206 bytes. The
full default suite passed 891 tests.
