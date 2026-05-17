# Command Buffer Unsupported SVG

Status: eighth rendered schematic view, 2026-05-17.

This SVG is the rendered view of the structured unsupported command-buffer
trace. It is not a separate design source. The authoritative artifact remains
`schematics/command_buffer_unsupported_trace.json`, and the checked-in SVG must
match `autarkic_systems/schematic_svg.py` renderer output exactly.

The rendered artifact lives in
`schematics/command_buffer_unsupported_trace.svg`.

## Render Boundary

The SVG shows:

- the triangular RLEM/Universal Cell node;
- north, east, and west ports from the structured trace;
- stem role and `step_stem_cell` transition function;
- the `stem-buffer-appended` transition status;
- the active control rail `[0, 0, 1]`;
- command buffer before `[0, 1, 0, 0]` and after `[0, 1, 0, 0, 1]`;
- cleared input after the append;
- the recorded decode-flow text for `neighbor-a/stem-init`;
- the four interpretive layer IDs from the shared schematic schema.

The SVG does not claim neighbor routing, self-target non-init execution,
dynamic GELC reconfiguration, or physical circulator verification. It renders
the one completed unsupported command-buffer trace from ADR-0042.

## Verification

Run:

```sh
python -m unittest tests.test_command_buffer_unsupported_svg
```

The test parses the SVG as XML, checks its trace metadata, port and layer data
attributes, confirms the unsupported command-buffer details are visible, and
verifies that the committed SVG exactly matches renderer output for the current
JSON trace.

## Regeneration

If the JSON trace changes, regenerate the SVG through `render_schematic_svg()`
and keep the test output green. Do not edit the SVG by hand unless the renderer
is updated in the same ADR.
