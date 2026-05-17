# ADR-0060: Multi-Command Recipient Rejection Trace

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0059 selected reject-and-clear for multiple simultaneous recipient
command-message inputs. The policy is machine-checkable as source-status and
claim-manifest evidence, but the visible schematic trace layer still shows only
a single upstream `standard-signal` rejection.

The next useful artifact is a direct multi-command rejection trace that shows
two command-message tokens present at once and proves that AS rejects the
activation without prioritizing either command.

## Decision

Add a schematic-linked multi-command recipient rejection trace:

- `schematics/multi_command_recipient_rejection_trace.json`;
- `MULTI_COMMAND_RECIPIENT_REJECTION_TRACE_ARTIFACT_ID` in the trace loader;
- validator routing through the existing recipient non-init rejection alignment
  check;
- tests proving replay, claim satisfaction, flow wording, and drift rejection;
- source-status frontier updates that make the rendered SVG the next safe
  slice.

This ADR does not change Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because
  `MULTI_COMMAND_RECIPIENT_REJECTION_TRACE_ARTIFACT_ID` is absent.
- The trace records a fixed direct input conflict with `wire-r-init` and
  `proc-l-init` both present.
- The trace replays through `step_fixed_cell` to `rejected-input`.
- The trace satisfies `recipient_non_init_command_message_rejected`.
- The validator rejects drifted flow or uncleared input.
- Adjacent source-status frontiers move from trace to SVG.

## Consequences

The selected multi-command policy becomes visible in the schematic evidence
layer. The next slice should render this trace as SVG without widening command
execution.

## After Action Report

The green implementation added
`MULTI_COMMAND_RECIPIENT_REJECTION_TRACE_ARTIFACT_ID`,
`schematics/multi_command_recipient_rejection_trace.json`, and
`docs/multi-command-recipient-rejection-trace.md`. The existing recipient
non-init rejection alignment validator was reused because it already handles
conflicting command-message input.

Runtime behavior was intentionally unchanged. The trace replays a fixed
`wire/right` recipient rejecting simultaneous `wire-r-init` and `proc-l-init`
tokens, satisfies `recipient_non_init_command_message_rejected`, and is checked
for drifted flow and uncleared input. Source-status frontiers now point to a
rendered SVG for this trace.
