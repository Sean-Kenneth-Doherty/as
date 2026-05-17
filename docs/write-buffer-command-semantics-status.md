# Write-Buffer Command Semantics Status

Status: source-status decision, 2026-05-17.

The structured status lives in
`sources/write_buffer_command_semantics_status.json`.

## Decision

Do not implement write-buffer command execution yet.

The formal model names `write-buf-zero` and `write-buf-one` in the command
table and routes special messages through generic special-message paths, but
it does not define the executable write-buffer primitive, buffer-full behavior,
or post-append clearing boundary.

The restored legacy sketches disagree:

- RAA appends 0 or 1 only when the buffer is not full, with input-processing
  flow clearing channels after special-message dispatch.
- SEMSIM defines append functions, but its stem special-message wrapper applies
  `zero-buf` after the selected operation, erasing the buffer after append.
- FSMSIM appends 0 or 1 and clears self-mailbox plus input channels, but does
  not expose the same buffer-full guard.

## AS Boundary

AS keeps write-buffer command execution blocked across these runtime surfaces:

- recipient command-message input;
- self-mailbox command;
- self-target command-buffer dispatch.

The current rejection and preservation claims remain the correct executable
boundary until a later ADR selects source-backed semantics for append,
buffer-full behavior, input/mail clearing, and high-rail interaction.

## Verification

Run:

```sh
python -m unittest tests.test_write_buffer_command_semantics_status
```

The tests check the decision, formal-model gap, legacy witness divergence,
required resolution questions, and source-status frontier updates.
