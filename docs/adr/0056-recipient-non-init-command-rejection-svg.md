# ADR-0056: Recipient Non-Init Command Rejection SVG

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0055 added the structured schematic trace for one recipient-side non-init
command-message rejection. The trace is executable and source-linked, but the
project convention is to follow each stable schematic trace with a checked SVG
view generated exactly from the JSON trace.

The rejection case is visually easy to misread as inactivity because role,
memory, output, control, and buffer are all preserved. The SVG must therefore
show the rejected upstream token and the clearing boundary explicitly.

## Decision

Add a rendered SVG view for
`schematics/recipient_non_init_command_rejection_trace.json`.

The renderer will expose:

- the rejected `standard-signal` upstream command-message token;
- preserved recipient role and memory;
- cleared upstream, input, and output channels;
- preserved self-mailbox, control, and buffer state;
- the trace's routed signal flow.

## Consequences

The recipient non-init rejection boundary becomes visible and drift-checked in
the same way as the recipient init command-message trace. This keeps the
blocked frontier legible without implying that `standard-signal` or
write-buffer command-message execution has landed.

## Test Plan

- Red: `python -m unittest tests.test_recipient_non_init_command_rejection_svg`
  fails because the SVG artifact path is absent from
  `autarkic_systems.schematic_svg`.
- Green: the same focused test passes after adding the renderer branch and
  checked SVG artifact.
- Regression: run adjacent recipient trace/source-status tests and the full
  default suite before commit.

## After Action Report

Implemented in `autarkic_systems/schematic_svg.py`,
`schematics/recipient_non_init_command_rejection_trace.svg`, and
`docs/recipient-non-init-command-rejection-svg.md`.

The focused red run failed because
`RECIPIENT_NON_INIT_COMMAND_REJECTION_SVG_ARTIFACT` was absent from
`autarkic_systems.schematic_svg`. After adding the renderer branch, the test
failed only because the checked SVG artifact was missing. Generating the SVG
from `render_schematic_svg()` made the focused SVG suite pass.
