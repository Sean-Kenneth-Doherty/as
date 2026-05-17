# ADR-0019: Stem Automail Reconfiguration Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0016 through ADR-0018 added schematic-linked traces for fixed-role wire and
processor behavior. P7 still lacks a schematic-linked witness for
reconfiguration, even though reconfiguration is central to PRC and AS.

The existing AS Universal Cell probe already implements a deliberately small
stem automail subset: `wr`, `wl`, `pr`, and `pl` reconfigure a stem cell into a
fixed role and memory direction. The next artifact should bind one of those
already tested transitions to the schematic trace layer without pretending to
cover full PRC stem buffering or dynamic reconfiguration.

## Decision

Add a third schematic-linked Universal Cell trace:

- `schematics/stem_automail_reconfiguration_trace.json` records one triangular
  RLEM/Universal Cell stem node with `pl` automail, expected reconfiguration to
  processor-left, and complete AS `Cell` before/after fields;
- `autarkic_systems/schematic_trace.py` recognizes the stem automail trace and
  validates its automail consumption, target role, target memory, and recorded
  reconfiguration flow;
- `tests/test_stem_automail_reconfiguration_trace.py` verifies schema reuse,
  executable replay through `step_stem_cell`, and rejection of drifted automail
  consumption or target role/memory;
- `docs/stem-automail-reconfiguration-trace.md` explains the artifact and its
  boundary.

The first stem trace uses `pl` because it demonstrates both role selection
(`proc`) and target memory selection (`left`) in one tiny transition.

## Success Criteria

- Red tests fail before implementation because the stem automail schematic trace
  artifact and constant are absent.
- The stem artifact reuses the same Cell field list and interpretive layer
  vocabulary as the wire and processor traces.
- The before-cell role is `stem`, automail is `pl`, and expected after-cell role
  is `proc`.
- Expected after-cell memory is `left`, and automail is consumed to `_`.
- Replaying the trace through `step_stem_cell` produces the recorded status and
  after-cell.
- Drifted target role, target memory, or unconsumed automail is rejected by
  validation.

## Consequences

- P7 now has schematic-linked traces for wire, processor, and the first stem
  reconfiguration subset.
- The trace schema remains shared across fixed-role and stem artifacts.
- Full stem input classification, buffer processing, rendered stem SVGs, and
  dynamic reconfiguration remain separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_stem_automail_reconfiguration_trace` failed
  because `STEM_AUTOMAIL_RECONFIGURATION_TRACE_ARTIFACT_ID` was not yet
  exported from `autarkic_systems.schematic_trace`.

Green step:

- Added `schematics/stem_automail_reconfiguration_trace.json`.
- Added stem automail validation for target role, target memory, automail
  consumption, and recorded reconfiguration flow.
- Added `docs/stem-automail-reconfiguration-trace.md`.
- `python -m unittest tests.test_stem_automail_reconfiguration_trace` passed 8
  tests.

Full verification:

- `python -m unittest tests.test_single_node_schematic_trace
  tests.test_single_node_schematic_svg tests.test_processor_memory_toggle_trace
  tests.test_stem_automail_reconfiguration_trace` passed 30 tests.
- `python -m unittest discover` passed 84 tests.
- `python -m py_compile autarkic_systems/schematic_trace.py
  tests/test_stem_automail_reconfiguration_trace.py` passed.
- `jq -e . schematics/stem_automail_reconfiguration_trace.json` passed.
- `git diff --check` passed.

Coverage limits:

- This slice covers one `pl` automail transition only.
- It does not model full stem buffering, command construction, or target
  routing.
- It does not render a stem SVG.
