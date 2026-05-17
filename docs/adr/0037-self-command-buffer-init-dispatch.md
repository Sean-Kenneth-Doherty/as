# ADR-0037: Self Command Buffer Init Dispatch

Date: 2026-05-17

Status: Accepted

## Context

ADR-0026 added the source-backed five-bit stem command-buffer map. ADR-0030
through ADR-0036 then made direct self-mailbox init execution and unsupported
preservation explicit, claim-backed, and visible in schematic artifacts.

The next safe command-buffer step is not full command execution. Neighbor
routing and unresolved self commands still need care. A narrow slice can,
however, use the existing decoder to dispatch self-target init-family commands
when the fifth command-buffer bit is appended. That path is source-backed by
the formal command table and reuses the already tested direct self-mailbox init
semantics.

## Decision

When a stem buffer grows from four bits to five bits during a standard-signal
append, decode the five-bit buffer. If and only if the decoded command is:

- target `self`; and
- one of `stem-init`, `wire-r-init`, `wire-l-init`, `proc-r-init`,
  `proc-l-init`;

then clear input, output, automail, self mailbox, control, and buffer, apply
the commanded role/memory reconfiguration, and return
`stem-command-buffer-self-processed`.

All other completed buffers remain at the existing `stem-buffer-appended`
boundary for now. This includes neighbor-target commands and self-target
`standard-signal`, `write-buf-zero`, and `write-buf-one`.

## Success Criteria

- Red tests fail before implementation because completing a self-target init
  command buffer only appends the fifth bit.
- A completed self `proc-l-init` buffer reconfigures to processor-left and
  clears transient command state.
- A completed self `stem-init` buffer resets to stem/right and clears transient
  command state.
- Completed neighbor-target buffers do not route through output channels.
- Completed self non-init buffers do not execute.
- The transition-claim language names the new status.

## Consequences

- AS gains its first command-buffer-to-behavior path without claiming full
  command-buffer execution.
- The route still excludes neighbor delivery and unresolved write-buffer or
  `standard-signal` semantics.
- A later ADR should promote this behavior into a named claim once the behavior
  is stable.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_self_command_buffer_init_dispatch`
showed that completed self `proc-l-init` and self `stem-init` buffers still
returned `stem-buffer-appended`, and that
`stem-command-buffer-self-processed` was absent from the transition-language
status vocabulary.

The green implementation added the narrow dispatch path in `step_stem_cell`,
using the ADR-0026 command map constants and the ADR-0030 direct self-mailbox
init behavior. Neighbor-target buffers and self-target non-init buffers remain
at the append boundary.

Final verification is recorded in `LOG.md`.
