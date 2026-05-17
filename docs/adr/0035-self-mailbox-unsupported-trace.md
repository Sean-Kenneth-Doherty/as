# ADR-0035: Self Mailbox Unsupported Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0034 promoted the unsupported self-mailbox command boundary into a named
claim. The boundary is now checkable at the predicate/proof-certificate layer,
but the schematic-trace layer still routes every non-empty self mailbox through
the init-command alignment path.

That is now too coarse. A stem trace with `self_mailbox` set to
`write-buf-one` and status `self-mailbox-unsupported` should validate as an
unsupported-preservation trace, not as a failed init trace.

## Decision

Add a schematic-linked trace for one unsupported self-mailbox command:

- add `schematics/self_mailbox_unsupported_trace.json`;
- add a schematic trace artifact id for unsupported self-mailbox preservation;
- route `self-mailbox-unsupported` traces through a dedicated alignment check;
- add tests for artifact identity, schema vocabulary, preservation flow,
  execution replay, witness-map validation, and drift rejection.

The trace will use `write-buf-one` because write-buffer behavior is explicitly
unresolved and already part of the unsupported boundary claim.

## Success Criteria

- Red tests fail before implementation because the unsupported trace artifact
  id is absent.
- The trace maps every current `Cell` field.
- Replaying the trace through `step_stem_cell` reaches
  `self-mailbox-unsupported`.
- The recorded after-cell exactly preserves the before-cell.
- Validation rejects cleared mailbox state, changed control/buffer state, or
  drifted unsupported flow.

## Consequences

- P7 gains executable schematic evidence for the unsupported command boundary.
- The trace validator distinguishes init execution from unsupported
  preservation.
- This still does not implement write-buffer, `standard-signal`, neighbor
  delivery, or full command-buffer execution.

## After Action Report

Implemented.

The red run for
`python -m unittest tests.test_self_mailbox_unsupported_trace` failed because
`SELF_MAILBOX_UNSUPPORTED_TRACE_ARTIFACT_ID` was absent from
`autarkic_systems.schematic_trace`.

The green implementation added the unsupported mailbox trace artifact,
registered the artifact id, and routed `self-mailbox-unsupported` traces with
non-empty `self_mailbox` through a dedicated preservation alignment check.

Final verification is recorded in `LOG.md`.
