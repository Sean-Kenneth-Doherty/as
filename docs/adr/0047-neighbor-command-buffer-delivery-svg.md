# ADR-0047: Neighbor Command Buffer Delivery SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0046 added a structured schematic-linked trace for one neighbor-target
command-buffer delivery. The JSON trace is executable and drift-checked, but it
is not yet visible as a rendered schematic artifact.

The existing SVG renderer has special summaries for command-buffer init
dispatch and unsupported command-buffer preservation. Neighbor delivery needs
its own visible summary because the important evidence is the decoded command
token moving to the correct output channel while recipient-side execution
remains absent.

## Decision

Add a generated SVG for the neighbor command-buffer delivery trace:

- export `NEIGHBOR_COMMAND_BUFFER_DELIVERY_SVG_ARTIFACT`;
- render neighbor-delivery command-buffer summary fields before generic buffer
  summaries;
- add `schematics/neighbor_command_buffer_delivery_trace.svg`;
- add tests proving parseability, metadata, port/layer annotations,
  command-buffer delivery details, exact renderer-output matching, and drift
  rejection.

This SVG is a view of ADR-0046's JSON trace. It does not add new Universal Cell
semantics.

## Success Criteria

- Red tests fail before implementation because
  `NEIGHBOR_COMMAND_BUFFER_DELIVERY_SVG_ARTIFACT` is absent.
- The committed SVG exactly matches renderer output for
  `schematics/neighbor_command_buffer_delivery_trace.json`.
- Existing schematic SVG tests still pass.
- The SVG exposes artifact ID, trace ID, ports, interpretive layers,
  transition status, command-buffer before/after state, output-channel
  delivery, cleared command state, and recorded decode flow.
- Validation rejects a drifted SVG.

## Consequences

- P7 gains a visible render for the neighbor command-buffer delivery trace.
- The renderer now distinguishes neighbor command-buffer delivery from generic
  buffer accumulation and unsupported command-buffer preservation.
- Recipient-side command-message consumption, self-target non-init execution,
  larger GELC, and physical simulation remain out of scope.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_neighbor_command_buffer_delivery_svg` failed
because `NEIGHBOR_COMMAND_BUFFER_DELIVERY_SVG_ARTIFACT` was absent from
`autarkic_systems.schematic_svg`.

The green implementation added the SVG artifact path, a neighbor
command-buffer-delivery summary branch in `render_schematic_svg`, and a
checked-in SVG generated from
`schematics/neighbor_command_buffer_delivery_trace.json`.

Final verification is recorded in `LOG.md`.
