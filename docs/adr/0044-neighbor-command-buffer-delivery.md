# ADR-0044: Neighbor Command Buffer Delivery

Date: 2026-05-17

Status: Accepted

## Context

ADR-0029 made command-message channel tokens representable. ADR-0037 executed
only completed self-target init-family command buffers. ADR-0041 through
ADR-0043 made the remaining completed-buffer append boundary explicit, with a
neighbor-target trace as the visible blocker.

The source-status artifact now names the next narrow execution slice:
neighbor-target command delivery onto output channels without executing
neighbor-side commands. The PRC formal model's process-buffer sketch places
self-target messages in the self mailbox and neighbor-target messages on the
three output channels. AS already has the token representation needed for that
delivery, while command-message input execution remains intentionally absent.

## Decision

Implement neighbor-target command-buffer delivery:

- add `stem-command-buffer-neighbor-delivered` to transition status vocabulary;
- when a just-completed five-bit command buffer decodes to `neighbor-a`,
  `neighbor-b`, or `neighbor-c`, place the decoded command token on output
  channel 0, 1, or 2 respectively;
- clear consumed input, control, and buffer state after delivery;
- preserve role, memory, upstream, automail, and `self_mailbox`;
- keep self-target non-init commands at the existing append boundary;
- keep command-message input execution out of scope.

This is delivery only. It does not execute the command on a neighbor cell.

## Success Criteria

- Red tests fail before implementation because completed neighbor buffers still
  return `stem-buffer-appended` and the status vocabulary lacks
  `stem-command-buffer-neighbor-delivered`.
- Neighbor A, B, and C buffers deliver to output channels 0, 1, and 2.
- Delivery clears transient command state.
- Blocked output still prevents delivery.
- Self-target non-init command buffers still remain at `stem-buffer-appended`.
- Command-message input tokens are still rejected rather than executed.
- Source-status docs/artifact record neighbor delivery as implemented while
  keeping full command execution blocked.

## Consequences

- One major ADR-0027 blocker moves from "not routed" to "delivered but not
  consumed by neighbors."
- ADR-0041's unsupported append-boundary claim must narrow to self-target
  non-init command buffers.
- ADR-0042/ADR-0043 unsupported command-buffer trace/render must be updated to
  a self-target non-init example, because the previous neighbor example becomes
  delivered behavior.
- Full command-buffer execution remains out of scope.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_neighbor_command_buffer_delivery`
failed because neighbor-target completed buffers still returned
`stem-buffer-appended` and the transition status vocabulary lacked
`stem-command-buffer-neighbor-delivered`.

The green implementation added neighbor-target delivery in `step_stem_cell`:
completed `neighbor-a`, `neighbor-b`, and `neighbor-c` command buffers now place
the decoded command token on output channels 0, 1, and 2 respectively, clear
transient command state, and preserve the non-command cell state. Command-message
input execution remains rejected.

ADR-0041 through ADR-0043 were revised so the unsupported append-boundary claim,
trace, and SVG now cover self-target non-init command-buffer completion rather
than the former neighbor-target example.

Final verification is recorded in `LOG.md`.
