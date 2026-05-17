# Single-Node Schematic Trace

Status: first schematic-linked Universal Cell trace, 2026-05-17.

This artifact is the first concrete step after the PRC hardware witness map. It
does not attempt a full GELC circuit or physical hardware simulation. It defines
one triangular RLEM/Universal Cell node and connects that node to one existing
AS Universal Cell transition.

The structured artifact lives in
`schematics/single_node_triangular_rlem_trace.json`.

Status update: ADR-0017 renders this structured trace as
`schematics/single_node_triangular_rlem_trace.svg`. The SVG is generated from
the JSON trace and checked against renderer output.

Status update: ADR-0018 adds the next schematic-linked trace,
`schematics/processor_memory_toggle_trace.json`, covering processor routing and
memory toggle behavior with the same schema.

Status update: ADR-0019 adds
`schematics/stem_automail_reconfiguration_trace.json`, covering one `pl`
automail reconfiguration from stem to processor-left.

## Schematic Key

The node is a triangular RLEM/Universal Cell key with three oriented ports:

```text
          p0 north
             /\
            /  \
 p2 west  /____\  p1 east
```

The first trace uses a wire cell with right memory. The schematic therefore
records a right-rotation of the three input channels:

```text
input[2] -> output[0]
input[0] -> output[1]
input[1] -> output[2]
```

## Interpretive Layers

The artifact keeps four layers separate:

- symbolic RLEM behavior: signal redirection and memory orientation;
- GELC geometry: triangular node, port orientation, and wire geometry;
- UC state: role, memory, upstream, input, output, automail, control, buffer;
- candidate physical implementation: switchable circulator hardware remains an
  unverified hypothesis.

This separation matters. A later diagram can be visually neat and still be
wrong if it silently turns a symbolic RLEM convention into a verified physical
claim.

## Executable Trace

The recorded initial cell is:

```json
{
  "role": "wire",
  "memory": "right",
  "upstream": ["_", "_", "_"],
  "input": [1, 0, 1],
  "output": ["_", "_", "_"],
  "automail": "_",
  "control": [],
  "buffer": []
}
```

Running that cell through `step_fixed_cell` produces status `routed` and output
`[1, 1, 0]`, with input cleared and memory unchanged. The validator recomputes
that result from the Python Universal Cell probe rather than trusting the JSON
record.

## Verification

Run:

```sh
python -m unittest tests.test_single_node_schematic_trace
```

The test validates the artifact ID, three-port schematic vocabulary,
interpretive layers, complete Cell field mapping, PRC witness references, and
the executable transition result.

## Open Follow-Ups

- Add a rendered SVG for the processor memory-toggle trace.
- Add a rendered SVG for the stem automail trace.
- Improve the generated SVG rendering while preserving JSON-as-source tests.
- Decide whether larger GELC examples should be reconstructed as structured
  diagrams or redrawn from `figures.pdf`.
