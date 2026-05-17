# Command Buffer Unsupported Trace

Status: schematic-linked trace artifact, 2026-05-17.

ADR-0042 adds `schematics/command_buffer_unsupported_trace.json`, a structured
schematic-linked Universal Cell trace for the unsupported self-target non-init
command-buffer append boundary named as a claim in ADR-0041.
ADR-0043 adds the rendered SVG view of this trace.
ADR-0044 revises the trace from its original neighbor-target example to a
self-target `write-buf-one` example because neighbor-target completions now
deliver command tokens to output channels.

## Trace Boundary

The trace records a stem cell with empty `automail` and `self_mailbox`, a
matching one-hot input/control pair, and a four-bit command buffer
`[0, 0, 1, 1]`. One `step_stem_cell` activation appends bit `1`, producing the
five-bit buffer `00111`. The ADR-0026 map decodes that value as
`self/write-buf-one`, and the transition must:

- return `stem-buffer-appended`;
- keep the cell in the `stem` role with `right` memory;
- keep output/automail/`self_mailbox` empty;
- preserve the control rail;
- preserve the completed five-bit buffer.

This does not execute the write-buffer command. It does not cover
`standard-signal`, neighbor-side command consumption, larger GELC examples, or
physical simulation.

ADR-0075 registers this trace in
`evidence/command_buffer_unsupported_bundle.json`, so the integrated evidence
validator checks the claim example, proof certificate, JSON trace, SVG render,
and source-status boundaries together.

## Schematic Role

The artifact uses the same triangular RLEM/GELC schematic vocabulary as the
earlier single-node, processor, stem automail, stem buffer, self-mailbox, and
self command-buffer traces. Its interpretive layers keep symbolic RLEM
behavior, GELC geometry, UC state, and candidate physical implementation
distinct.

## Verification

Run:

```sh
python -m unittest tests.test_command_buffer_unsupported_trace
```

The tests verify artifact identity, schema vocabulary, recorded decode flow,
execution replay through `step_stem_cell`, PRC witness-map validation, and
drift rejection for routed output, wrong completed buffer, and changed flow.
