# Self Mailbox Init Trace

Status: schematic-linked trace artifact, 2026-05-17.

ADR-0032 adds `schematics/self_mailbox_init_trace.json`, a structured
schematic-linked Universal Cell trace for the self-mailbox init-command subset
implemented in ADR-0030 and named as a claim in ADR-0031.

## Trace Boundary

The trace records a stem cell with `self_mailbox` set to `proc-l-init`, empty
input/output channels, empty automail, and non-empty control/buffer state. One
`step_stem_cell` activation must:

- return `self-mailbox-processed`;
- reconfigure the cell to `proc` with `left` memory;
- clear `self_mailbox`;
- keep input/output/automail empty;
- clear control and buffer state.

This is not full command-buffer execution. It does not cover
`standard-signal`, `write-buf-zero`, `write-buf-one`, neighbor delivery, larger
GELC examples, or physical simulation.

ADR-0072 aligns this trace with the exact positive claim example used by
`evidence/self_mailbox_init_bundle.json`, so the integrated evidence validator
checks one concrete transition rather than a nearby fixture variant.

## Schematic Role

The artifact uses the same triangular RLEM/GELC schematic vocabulary as the
earlier single-node, processor, stem automail, and stem buffer traces. Its
interpretive layers keep symbolic RLEM behavior, GELC geometry, UC state, and
candidate physical implementation distinct.

## Verification

Run:

```sh
python -m unittest tests.test_self_mailbox_init_trace
```

The tests verify artifact identity, schema vocabulary, recorded mailbox flow,
execution replay through `step_stem_cell`, PRC witness-map validation, and drift
rejection for wrong target role, uncleared mailbox state, and changed flow.
