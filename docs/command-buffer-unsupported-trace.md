# Command Buffer Unsupported Trace

Status: schematic-linked trace artifact, 2026-05-17.

ADR-0042 adds `schematics/command_buffer_unsupported_trace.json`, a structured
schematic-linked Universal Cell trace for the unsupported completed
command-buffer append boundary named as a claim in ADR-0041.
ADR-0043 adds the rendered SVG view of this trace.

## Trace Boundary

The trace records a stem cell with empty `automail` and `self_mailbox`, a
matching one-hot input/control pair, and a four-bit command buffer
`[0, 1, 0, 0]`. One `step_stem_cell` activation appends bit `1`, producing the
five-bit buffer `01001`. The ADR-0026 map decodes that value as
`neighbor-a/stem-init`, and the transition must:

- return `stem-buffer-appended`;
- keep the cell in the `stem` role with `right` memory;
- keep output/automail/`self_mailbox` empty;
- preserve the control rail;
- preserve the completed five-bit buffer.

This is not neighbor routing. It does not cover self-target non-init command
execution, larger GELC examples, or physical simulation.

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
