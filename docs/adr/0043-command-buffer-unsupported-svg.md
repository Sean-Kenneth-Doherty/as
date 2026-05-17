# ADR-0043: Command Buffer Unsupported SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0042 added a structured schematic-linked trace for one completed
neighbor-target command buffer that remains at the append boundary. The JSON
trace is executable and drift-checked, but it is not yet visible as a rendered
schematic artifact.

The existing SVG renderer has special summaries for supported self-target init
dispatch and other stem mechanisms. Unsupported completed command buffers need
their own visible summary because the important evidence is that the decoded
neighbor command is preserved at the append boundary, not routed.

## Decision

Add a generated SVG for the unsupported command-buffer trace:

- export `COMMAND_BUFFER_UNSUPPORTED_SVG_ARTIFACT`;
- render unsupported command-buffer summary fields before generic buffer
  summaries;
- add `schematics/command_buffer_unsupported_trace.svg`;
- add tests proving parseability, metadata, port/layer annotations,
  command-buffer details, exact renderer-output matching, and drift rejection.

This SVG is a view of ADR-0042's JSON trace. It does not add new Universal Cell
semantics.

## Success Criteria

- Red tests fail before implementation because
  `COMMAND_BUFFER_UNSUPPORTED_SVG_ARTIFACT` is absent.
- The committed SVG exactly matches renderer output for
  `schematics/command_buffer_unsupported_trace.json`.
- Existing schematic SVG tests still pass.
- The SVG exposes artifact ID, trace ID, ports, interpretive layers, transition
  status, command-buffer before/after state, cleared input, and recorded decode
  flow.
- Validation rejects a drifted SVG.

## Consequences

- P7 gains a visible render for the unsupported completed command-buffer trace.
- The renderer now distinguishes unsupported completed-buffer append from
  generic buffer accumulation.
- Neighbor routing, self-target non-init execution, larger GELC, and physical
  simulation remain out of scope.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_command_buffer_unsupported_svg`
failed because `COMMAND_BUFFER_UNSUPPORTED_SVG_ARTIFACT` was absent from
`autarkic_systems.schematic_svg`.

The green implementation added the SVG artifact path, an unsupported
command-buffer-specific summary branch in `render_schematic_svg`, and a
checked-in SVG generated from
`schematics/command_buffer_unsupported_trace.json`.

Final verification is recorded in `LOG.md`.
