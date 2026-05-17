# ADR-0033: Self Mailbox Init SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0032 added a structured schematic-linked trace for one `proc-l-init`
self-mailbox command. The trace is executable and drift-checked, but it is not
yet visible as a rendered schematic artifact.

The existing renderer treats any role-changing trace as generic
reconfiguration. For self-mailbox init, that is too weak: the visible SVG must
show the mailbox before/after fields and the cleared control/buffer state that
distinguish mailbox execution from automail reconfiguration.

## Decision

Add a generated SVG for the self-mailbox init trace:

- export `SELF_MAILBOX_INIT_SVG_ARTIFACT`;
- render mailbox-specific summary fields before generic reconfiguration fields;
- add `schematics/self_mailbox_init_trace.svg`;
- add tests proving parseability, metadata, port/layer annotations, mailbox
  before/after visibility, control/buffer clearing, flow text, exact
  renderer-output matching, and drift rejection.

This SVG is a view of ADR-0032's JSON trace. It does not add new Universal Cell
semantics.

## Success Criteria

- Red tests fail before implementation because
  `SELF_MAILBOX_INIT_SVG_ARTIFACT` is absent.
- The committed SVG exactly matches renderer output for
  `schematics/self_mailbox_init_trace.json`.
- Existing schematic SVG tests still pass.
- The SVG exposes artifact ID, trace ID, ports, interpretive layers, role and
  memory before/after, `self_mailbox` before/after, control/buffer before and
  after, transition status, and mailbox flow.
- Validation rejects a drifted SVG.

## Consequences

- P7 gains a visible render for the self-mailbox init-command trace.
- The renderer now distinguishes mailbox execution from automail
  reconfiguration when deciding trace-summary fields.
- Write-buffer, `standard-signal`, neighbor delivery, larger GELC, and
  physical simulation remain out of scope.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_self_mailbox_init_svg` failed
because `SELF_MAILBOX_INIT_SVG_ARTIFACT` was absent from
`autarkic_systems.schematic_svg`.

The green implementation added the SVG artifact path, a mailbox-specific
summary branch in `render_schematic_svg`, and a checked-in SVG generated from
`schematics/self_mailbox_init_trace.json`.

Final verification is recorded in `LOG.md`.
