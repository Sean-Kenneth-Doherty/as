# Recipient Init Command-Message Trace

Status: schematic-linked trace artifact, 2026-05-17.

ADR-0051 adds `schematics/recipient_init_command_message_trace.json`, a
structured schematic-linked Universal Cell trace for the recipient init
command-message behavior implemented in ADR-0049 and named as a claim in
ADR-0050.
ADR-0052 adds the rendered SVG view of this trace.

## Trace Boundary

The trace records a processor-left recipient with empty direct input and a
single upstream command-message token, `wire-r-init`, on channel 0. One
`step_fixed_cell` activation pulls the upstream token into input, consumes it
as an init-family command message, and must:

- return `recipient-init-command-message-processed`;
- reconfigure the cell to `wire` with `right` memory;
- clear upstream, input, and output;
- keep automail and `self_mailbox` empty;
- keep control and buffer empty.

This does not execute `standard-signal`, write-buffer, or multi-command inputs.
It also does not render the trace as SVG yet.

## Schematic Role

The artifact uses the same triangular RLEM/GELC schematic vocabulary as the
earlier single-node, processor, stem automail, stem buffer, mailbox,
command-buffer, and neighbor-delivery traces. Its interpretive layers keep
symbolic RLEM behavior, GELC geometry, UC state, and candidate physical
implementation distinct.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_init_command_message_trace
```

The tests verify artifact identity, schema vocabulary, upstream command flow,
execution replay through `step_fixed_cell`, PRC witness-map validation, and
drift rejection for wrong target role, uncleared upstream, and changed flow.
