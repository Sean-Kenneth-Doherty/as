# ADR-0042: Command Buffer Unsupported Trace

Date: 2026-05-17

Status: Accepted

Revision note: ADR-0044 later revises the live trace from the original
`neighbor-a/stem-init` example to a self-target `write-buf-one` example because
neighbor-target completed buffers now deliver onto output channels.

## Context

ADR-0041 promoted completed command buffers outside the self-target init slice
into a named append-boundary claim. The next evidence layer should make that
boundary visible as a schematic-linked trace.

The most useful first trace is a neighbor-target completion: it demonstrates
that a decoded neighbor command is not silently routed before AS defines
neighbor delivery semantics.

## Decision

Add a schematic-linked trace for one unsupported completed command buffer:

- add `schematics/command_buffer_unsupported_trace.json`;
- add a schematic trace artifact id for unsupported command-buffer completion;
- validate completed unsupported command-buffer flow separately from ordinary
  buffer accumulation and supported self-init dispatch;
- add tests for artifact identity, schema vocabulary, recorded decode flow,
  execution replay, witness-map validation, and drift rejection.

The trace will use the five-bit buffer `01001`, decoded as
`neighbor-a/stem-init`, because it names a concrete neighbor-target command
while staying inside the current append-boundary semantics.

## Success Criteria

- Red tests fail before implementation because the command-buffer unsupported
  trace artifact id is absent.
- The trace maps every current `Cell` field.
- Replaying the trace through `step_stem_cell` reaches
  `stem-buffer-appended`.
- The recorded after-cell matches current execution exactly.
- Validation rejects routed output, wrong appended buffer, or drifted decode
  flow.

## Consequences

- P7 gains visible, executable evidence for the ADR-0041 boundary.
- The trace still does not claim neighbor routing, self-target non-init command
  execution, larger GELC examples, or physical simulation.

## After Action Report

Implemented.

The red run for `python -m unittest tests.test_command_buffer_unsupported_trace`
failed because `COMMAND_BUFFER_UNSUPPORTED_TRACE_ARTIFACT_ID` was absent from
`autarkic_systems.schematic_trace`.

The green implementation added the unsupported command-buffer trace artifact,
registered the artifact id, and routed that artifact through a dedicated
completed unsupported command-buffer alignment check instead of the ordinary
stem-buffer accumulation check.

Final verification is recorded in `LOG.md`.

ADR-0044 revision: `schematics/command_buffer_unsupported_trace.json` now
records a self-target `write-buf-one` buffer preserved at the append boundary.
The original neighbor-target example became delivered behavior.
