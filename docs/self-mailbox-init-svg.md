# Self Mailbox Init SVG

Status: fifth rendered schematic view, 2026-05-17.

This SVG is the rendered view of the structured self-mailbox init trace. It is
not a separate design source. The authoritative artifact remains
`schematics/self_mailbox_init_trace.json`, and the checked-in SVG must match
`autarkic_systems/schematic_svg.py` renderer output exactly.

The rendered artifact lives in `schematics/self_mailbox_init_trace.svg`.

## Render Boundary

The SVG shows:

- the triangular RLEM/Universal Cell node;
- north, east, and west ports from the structured trace;
- stem role and `step_stem_cell` transition function;
- `self_mailbox` before `proc-l-init` and after `_`;
- role after `proc`;
- memory before `right` and after `left`;
- control and buffer state before and after clearing;
- the recorded mailbox-flow text;
- the four interpretive layer IDs from the shared schematic schema.

The SVG does not claim write-buffer execution, `standard-signal` command
execution, neighbor delivery, dynamic GELC reconfiguration, or physical
circulator verification. It renders the one `proc-l-init` self-mailbox trace
from ADR-0032.

## Verification

Run:

```sh
python -m unittest tests.test_self_mailbox_init_svg
```

The test parses the SVG as XML, checks its trace metadata, port and layer data
attributes, confirms the self-mailbox and clearing details are visible, and
verifies that the committed SVG exactly matches renderer output for the current
JSON trace.

## Regeneration

If the JSON trace changes, regenerate the SVG through `render_schematic_svg()`
and keep the test output green. Do not edit the SVG by hand unless the renderer
is updated in the same ADR.
