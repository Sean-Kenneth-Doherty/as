# Standard-Signal Command Semantics Status

Status: source-status decision, 2026-05-17.

The structured status lives in
`sources/standard_signal_command_semantics_status.json`.

## Decision

Do not implement `standard-signal` command-token execution yet.

AS already implements ordinary standard-signal behavior for binary input:
fixed wire/proc routing and stem high-rail / command-buffer accumulation. That
does not settle the separate command-token question. The formal model also
names `standard-signal` at command offset 0 for each target range, but it does
not define whether that token should replay ordinary binary-input behavior,
execute from recipient command-message input, execute from self-mailbox state,
or remain unsupported.

The restored legacy sketches do not supply a stable execution rule:

- RAA excludes `standard-signal` from `special-messages`, treats ordinary
  standard input as numeric `1`, and maps the final command-buffer case to
  `standard-signal`.
- SEMSIM excludes `standard-signal` from `special-messages` and classifies
  binary standard input separately from special-message dispatch.
- FSMSIM excludes `standard-signal` from `special-messages`, classifies
  nonzero binary input as ordinary standard input, and indexes command-buffer
  messages through the seven special messages only.

## AS Boundary

AS keeps `standard-signal` command-token execution blocked across these runtime
surfaces:

- recipient command-message input;
- self-mailbox command;
- self-target command-buffer dispatch.

The current ordinary standard-signal behavior remains valid because it is
binary-input behavior, not command-token execution. ADR-0059 selects
reject-and-clear for multi-command recipient input conflicts, and ADR-0060
adds the corresponding trace. The next visible source-status slice is a
multi-command rejection SVG.

## Verification

Run:

```sh
python -m unittest tests.test_standard_signal_command_semantics_status
```

The tests check the decision, formal-model command/binary distinction, legacy
witness divergence, required resolution questions, and source-status frontier
updates.
