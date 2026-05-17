# Recipient Non-Init Command Rejection SVG

Status: implemented by ADR-0056 on 2026-05-17.

The rendered SVG lives in
`schematics/recipient_non_init_command_rejection_trace.svg` and is generated
from `schematics/recipient_non_init_command_rejection_trace.json`.

## Boundary

The SVG shows the ADR-0055 rejection trace as a visible proof surface. It keeps
the upstream `standard-signal` token visible before rejection, shows upstream
clearing afterward, and records role/memory preservation plus empty
input/output, self-mailbox, control, and buffer state.

This is not a runtime semantics expansion. `standard-signal`,
`write-buf-zero`, `write-buf-one`, and multi-command recipient inputs remain
blocked until the source-status frontier is resolved.

## Validation

Run:

```sh
python -m unittest tests.test_recipient_non_init_command_rejection_svg
```

The tests check parseability, trace metadata, port and layer annotations,
visible rejection details, exact renderer-output matching, validator
acceptance, and drift rejection.
