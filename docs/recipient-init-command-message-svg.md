# Recipient Init Command-Message SVG

Status: tenth rendered schematic view, 2026-05-17.

This SVG is the rendered view of the structured recipient init command-message
trace. It is not a separate design source. The authoritative artifact remains
`schematics/recipient_init_command_message_trace.json`, and the checked-in SVG
must match `autarkic_systems/schematic_svg.py` renderer output exactly.

The rendered artifact lives in
`schematics/recipient_init_command_message_trace.svg`.

## Render Boundary

The SVG shows:

- the triangular RLEM/Universal Cell node;
- north, east, and west ports from the structured trace;
- processor role before and wire role after the transition;
- `step_fixed_cell` as the transition function;
- the `recipient-init-command-message-processed` transition status;
- upstream before `[wire-r-init, _, _]`;
- upstream, input, and output cleared after the transition;
- empty self-mailbox, control, and buffer state after the transition;
- the recorded upstream command-message flow;
- the four interpretive layer IDs from the shared schematic schema.

The SVG does not claim `standard-signal`, write-buffer, or multi-command input
semantics. It renders the one recipient init command-message trace from
ADR-0051.

## Verification

Run:

```sh
python -m unittest tests.test_recipient_init_command_message_svg
```

The test parses the SVG as XML, checks its trace metadata, port and layer data
attributes, confirms the recipient command-message details are visible, and
verifies that the committed SVG exactly matches renderer output for the
current JSON trace.

## Regeneration

If the JSON trace changes, regenerate the SVG through `render_schematic_svg()`
and keep the test output green. Do not edit the SVG by hand unless the
renderer is updated in the same ADR.
