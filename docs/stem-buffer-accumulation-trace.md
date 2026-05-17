# Stem Buffer Accumulation Trace

Status: fourth schematic-linked Universal Cell trace, 2026-05-17.

This artifact adds a schematic-linked witness for the first standard-signal
stem buffer behavior. It records a stem cell with an active control rail
`[0, 1, 0]`, a matching one-hot input `[0, 1, 0]`, and the expected append of
bit `1` to buffer `[0]`, producing buffer `[0, 1]`.

The structured artifact lives in
`schematics/stem_buffer_accumulation_trace.json`.

## Trace Shape

The stem starts with:

```json
{
  "role": "stem",
  "memory": "right",
  "input": [0, 1, 0],
  "automail": "_",
  "control": [0, 1, 0],
  "buffer": [0]
}
```

The recorded accumulation flow is:

```text
control[0,1,0] active
input[0,1,0] matches control -> append 1
buffer[0] -> buffer[0,1]
```

Running that cell through `step_stem_cell` produces status
`stem-buffer-appended`, clears input, preserves control, and appends `1` to the
buffer. The validator recomputes that result instead of trusting the JSON
record.

## Boundary

This trace covers one matching-input append from the ADR-0022 accumulation
subset. It does not trace control selection, non-matching append, full-buffer
boundary, five-bit command interpretation, target routing, or dynamic
reconfiguration.

## Verification

Run:

```sh
python -m unittest tests.test_stem_buffer_accumulation_trace
```

The test validates schema reuse, buffer append details, PRC witness references,
recorded flow, replay through the existing Universal Cell stem probe, and
rejection of drifted expected buffer or flow.
