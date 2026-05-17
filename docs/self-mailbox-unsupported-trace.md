# Self Mailbox Unsupported Trace

Status: schematic-linked trace artifact, 2026-05-17.

ADR-0035 adds `schematics/self_mailbox_unsupported_trace.json`, a structured
schematic-linked Universal Cell trace for the unsupported self-mailbox command
boundary named in ADR-0034.

## Trace Boundary

The trace records a stem cell with `self_mailbox` set to `write-buf-one`,
empty input/output channels, empty automail, and non-empty control/buffer
state. One `step_stem_cell` activation must:

- return `self-mailbox-unsupported`;
- preserve the entire cell unchanged;
- leave `self_mailbox` set to `write-buf-one`;
- leave control and buffer state unchanged.

This is not write-buffer execution. It records that AS currently refuses to
execute `write-buf-one` from the self mailbox until source-backed semantics are
resolved.

## Schematic Role

The artifact uses the same triangular RLEM/GELC schematic vocabulary as the
other schematic traces. Its validator path is separate from self-mailbox init
execution: `self-mailbox-unsupported` traces must prove preservation rather
than role/memory reconfiguration.

## Verification

Run:

```sh
python -m unittest tests.test_self_mailbox_unsupported_trace
```

The tests verify artifact identity, schema vocabulary, recorded preservation
flow, execution replay through `step_stem_cell`, PRC witness-map validation,
and drift rejection for cleared mailbox state, changed control state, and
changed flow.
