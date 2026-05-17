# Multi-Command Recipient Rejection Trace

Status: schematic-linked trace, 2026-05-17.

The structured artifact lives in
`schematics/multi_command_recipient_rejection_trace.json`.

## Scope

This trace records a fixed recipient cell receiving two simultaneous
init-family command-message tokens:

- `wire-r-init` on input channel 0;
- `proc-l-init` on input channel 1.

Under ADR-0059, AS rejects and clears the active command input rather than
prioritizing either command or sequencing both commands.

## Transition

The trace replays through `step_fixed_cell` and expects `rejected-input`.

The before state is a `wire/right` recipient with empty upstream and output
channels. The after state preserves role and memory, clears input and output,
and leaves automail, self-mailbox, control, and buffer state unchanged.

The routed-flow note is explicit:

```text
input[0] carries command[wire-r-init+proc-l-init]
command[wire-r-init+proc-l-init] rejected as recipient non-init command-message
role/memory preserved
input/output cleared
command side state preserved
```

## Verification

Run:

```sh
python -m unittest tests.test_multi_command_recipient_rejection_trace
```

The tests load the artifact, replay it, check the
`recipient_non_init_command_message_rejected` claim, validate it against the
PRC hardware witness map, and reject drifted flow or uncleared input.
