# ADR-0036: Self Mailbox Unsupported SVG

Date: 2026-05-17

Status: Accepted

## Context

ADR-0035 added a structured schematic-linked trace for one unsupported
`write-buf-one` self-mailbox command. The JSON trace is executable and
drift-checked, but it is not yet visible as a rendered schematic artifact.

The existing renderer shows special summary fields for self-mailbox init
execution, automail reconfiguration, and buffer accumulation. Unsupported
self-mailbox preservation needs its own summary path because the important
facts are that the mailbox, control, and buffer are preserved and the command
is not executed.

## Decision

Add a generated SVG for the unsupported self-mailbox trace:

- export `SELF_MAILBOX_UNSUPPORTED_SVG_ARTIFACT`;
- render unsupported-mailbox summary fields before generic trace summaries;
- add `schematics/self_mailbox_unsupported_trace.svg`;
- add tests proving parseability, metadata, port/layer annotations, mailbox
  preservation visibility, control/buffer preservation visibility, exact
  renderer-output matching, and drift rejection.

This SVG is a view of ADR-0035's JSON trace. It does not add new Universal Cell
semantics.

## Success Criteria

- Red tests fail before implementation because
  `SELF_MAILBOX_UNSUPPORTED_SVG_ARTIFACT` is absent.
- The committed SVG exactly matches renderer output for
  `schematics/self_mailbox_unsupported_trace.json`.
- Existing schematic SVG tests still pass.
- The SVG exposes artifact ID, trace ID, ports, interpretive layers,
  `self_mailbox` before/after, control/buffer before/after, transition status,
  and unsupported flow.
- Validation rejects a drifted SVG.

## Consequences

- P7 gains a visible render for the unsupported self-mailbox preservation
  trace.
- The renderer now distinguishes unsupported mailbox preservation from mailbox
  init execution.
- Write-buffer semantics, `standard-signal` execution, neighbor delivery,
  larger GELC, and physical simulation remain out of scope.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_self_mailbox_unsupported_svg`
failed because `SELF_MAILBOX_UNSUPPORTED_SVG_ARTIFACT` was absent from
`autarkic_systems.schematic_svg`.

The green implementation added the SVG artifact path, an
unsupported-mailbox-specific summary branch in `render_schematic_svg`, and a
checked-in SVG generated from `schematics/self_mailbox_unsupported_trace.json`.

Final verification is recorded in `LOG.md`.
