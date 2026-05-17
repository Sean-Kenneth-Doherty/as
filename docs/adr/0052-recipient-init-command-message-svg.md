# ADR-0052: Recipient Init Command-Message SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0051 added a structured schematic-linked trace for a fixed recipient
consuming an upstream `wire-r-init` command-message token. The JSON trace is
executable and drift-checked, but it is not yet visible as a rendered
schematic artifact.

The existing SVG renderer keeps rendered diagrams subordinate to JSON traces by
requiring checked-in SVG files to match renderer output exactly. Recipient init
command-message consumption needs its own visible summary because the important
evidence is upstream command-token entry, role/memory reconfiguration, and
upstream/input/command-state clearing.

## Decision

Add a generated SVG for the recipient init command-message trace:

- export `RECIPIENT_INIT_COMMAND_MESSAGE_SVG_ARTIFACT`;
- render recipient init command-message summary fields before generic role
  reconfiguration summaries;
- add `schematics/recipient_init_command_message_trace.svg`;
- add tests proving parseability, metadata, port/layer annotations, recipient
  command-message details, exact renderer-output matching, and drift
  rejection.

This SVG is a view of ADR-0051's JSON trace. It does not add new Universal
Cell semantics.

## Success Criteria

- Red tests fail before implementation because
  `RECIPIENT_INIT_COMMAND_MESSAGE_SVG_ARTIFACT` is absent.
- The committed SVG exactly matches renderer output for
  `schematics/recipient_init_command_message_trace.json`.
- Existing schematic SVG tests still pass.
- The SVG exposes artifact ID, trace ID, ports, interpretive layers,
  transition status, upstream command-message token, role/memory before and
  after, cleared upstream/input/output, cleared command state, and recorded
  flow.
- Validation rejects a drifted SVG.

## Consequences

- P7 gains a visible render for the recipient init command-message trace.
- The renderer now distinguishes recipient init command-message consumption
  from generic fixed-role reconfiguration.
- Non-init command messages, larger GELC examples, and physical simulation
  remain out of scope.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_recipient_init_command_message_svg` failed
because `RECIPIENT_INIT_COMMAND_MESSAGE_SVG_ARTIFACT` was absent from
`autarkic_systems.schematic_svg`.

The green implementation added the SVG artifact path, a recipient
init-command-message summary branch in `render_schematic_svg`, and a checked-in
SVG generated from `schematics/recipient_init_command_message_trace.json`.

Final verification is recorded in `LOG.md`.
