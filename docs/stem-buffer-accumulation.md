# Stem Buffer Accumulation

Status: first standard-signal stem buffer subset, 2026-05-17.

This note records the first `step_stem_cell` behavior beyond explicit automail
reconfiguration. PRC's formal model describes stem cells using standard signals
to select a high rail and accumulate a five-bit command buffer before later
command processing. ADR-0022 implements only that accumulation boundary.
ADR-0037 later adds a narrow exception for just-completed self-target
init-family command buffers.

The implementation lives in `autarkic_systems/universal_cell.py`. ADR-0023
promotes the implemented subset into the named claim
`UC-STEM-BUFFER-ACCUMULATES`. ADR-0024 records one matching-input append as
`schematics/stem_buffer_accumulation_trace.json`. ADR-0026 maps the full
five-bit command buffer values without executing them.

## Implemented Behavior

When a stem cell has no automail command and its output is empty:

- a one-hot standard input selects the control rail if no control rail is set;
- a matching one-hot input appends `1` to a non-full buffer;
- a non-matching one-hot input appends `0` to a non-full buffer;
- if the append completes a self-target init-family command buffer, the command
  is processed as `stem-command-buffer-self-processed`;
- a full five-bit buffer returns `stem-buffer-full` without consuming input;
- malformed stem input is rejected and cleared.

Automail reconfiguration still has priority over standard-signal buffering.

## Source Boundary

This slice follows the PRC formal-model text that describes the constant-count
five-bit command buffer and the `stem-process-standard-signal` transitions.
ADR-0037 adds the first narrow `process-buffer` slice for self-target init
commands only. Neighbor delivery, write-buffer commands, `standard-signal`
command semantics, and dynamic GELC reconfiguration remain out of scope.

## Verification

Run:

```sh
python -m unittest tests.test_stem_buffer_accumulation tests.test_stem_automail
```

The tests cover high-rail selection, matching and non-matching bit append,
full-buffer boundary behavior, malformed-input rejection, and automail priority.
