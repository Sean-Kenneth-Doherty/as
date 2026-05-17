# Neighbor Command Buffer Delivery SVG

Status: ninth rendered schematic view, 2026-05-17.

This SVG is the rendered view of the structured neighbor command-buffer
delivery trace. It is not a separate design source. The authoritative artifact
remains `schematics/neighbor_command_buffer_delivery_trace.json`, and the
checked-in SVG must match `autarkic_systems/schematic_svg.py` renderer output
exactly.

The rendered artifact lives in
`schematics/neighbor_command_buffer_delivery_trace.svg`.

## Render Boundary

The SVG shows:

- the triangular RLEM/Universal Cell node;
- north, east, and west ports from the structured trace;
- stem role and `step_stem_cell` transition function;
- the `stem-command-buffer-neighbor-delivered` transition status;
- the active control rail `[1, 0, 0]`;
- command buffer before `[1, 0, 1, 0]`;
- cleared input, control, and buffer after delivery;
- output after `[_, proc-l-init, _]`;
- the recorded decode-flow text for `neighbor-b/proc-l-init`;
- the four interpretive layer IDs from the shared schematic schema.

The SVG does not claim recipient-side command-message consumption, self-target
non-init execution, dynamic GELC reconfiguration, or physical circulator
verification. It renders the one neighbor command-buffer delivery trace from
ADR-0046.

## Verification

Run:

```sh
python -m unittest tests.test_neighbor_command_buffer_delivery_svg
```

The test parses the SVG as XML, checks its trace metadata, port and layer data
attributes, confirms the neighbor-delivery command-buffer details are visible,
and verifies that the committed SVG exactly matches renderer output for the
current JSON trace.

## Regeneration

If the JSON trace changes, regenerate the SVG through `render_schematic_svg()`
and keep the test output green. Do not edit the SVG by hand unless the renderer
is updated in the same ADR.
