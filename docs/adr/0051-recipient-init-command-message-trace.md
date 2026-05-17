# ADR-0051: Recipient Init Command-Message Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0049 made recipient-side init-family command-message inputs executable.
ADR-0050 promoted the behavior into
`UC-RECIPIENT-INIT-COMMAND-MESSAGE-PROCESSED`. The next evidence step should
be a schematic-linked trace over that named claim, not a wider command
execution slice.

The trace should show one recipient consuming a delivered init-family
command-message token and should replay through the existing Universal Cell
transition probe. Because neighbor delivery produces output-channel command
tokens that become another cell's upstream/input surface, the trace should
exercise the fixed-cell upstream-pull path from ADR-0049.

## Decision

Add a structured schematic-linked trace for one fixed recipient:

- artifact ID:
  `recipient-init-command-message-schematic-and-uc-transition-trace`;
- trace file: `schematics/recipient_init_command_message_trace.json`;
- transition function: `step_fixed_cell`;
- before state: a processor-left recipient with
  `upstream = ["wire-r-init", "_", "_"]`;
- after state: a wire-right recipient with upstream/input/output and command
  state cleared;
- status: `recipient-init-command-message-processed`.

Extend the schematic-trace validator with a dedicated recipient init
command-message alignment path so drift in role/memory target, upstream
clearing, command-state clearing, or routed flow is rejected.

## Success Criteria

- Red tests fail before implementation because the artifact ID and trace file
  are absent.
- The trace uses the existing schematic trace schema, required PRC witness IDs,
  required interpretive layers, and full `Cell` field list.
- The trace records the upstream `wire-r-init` command-message input, expected
  `wire/right` target, cleared upstream/input/output, and
  `recipient-init-command-message-processed` status.
- The trace replays against `step_fixed_cell`.
- Validation accepts the trace against the PRC hardware witness map.
- Drift tests reject wrong target role, uncleared upstream, and mismatched
  routed flow.

## Consequences

- Recipient command-message consumption gains schematic-linked evidence without
  widening command semantics.
- A later SVG render can be generated from the structured trace.
- Non-init command messages remain blocked.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_recipient_init_command_message_trace` failed
because `RECIPIENT_INIT_COMMAND_MESSAGE_TRACE_ARTIFACT_ID` was absent from
`autarkic_systems.schematic_trace`.

The green implementation added the artifact ID, schematic-trace validator
alignment for recipient init command-message traces, the structured JSON trace,
and source-status updates that move the next slice to a rendered SVG.

Final verification is recorded in `LOG.md`.
