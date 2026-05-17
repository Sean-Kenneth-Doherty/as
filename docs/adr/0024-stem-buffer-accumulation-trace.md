# ADR-0024: Stem Buffer Accumulation Trace

Date: 2026-05-17

Status: Accepted

## Context

ADR-0022 added stem buffer accumulation behavior and ADR-0023 promoted that
behavior into the named claim surface. P7's schematic evidence path currently
has traces for fixed-role wire, fixed-role processor, and stem automail
reconfiguration. It does not yet have a schematic-linked trace for the
standard-signal stem buffer subset.

The existing schematic trace validator treats every stem trace as automail
reconfiguration. That was correct for ADR-0019, but it would reject the
automail-empty buffer path. The validator now needs to distinguish stem
automail traces from stem buffer accumulation traces.

## Decision

Add a structured schematic-linked trace for one stem buffer append:

- `schematics/stem_buffer_accumulation_trace.json` records a stem cell with an
  active control rail, one matching one-hot input, and expected buffer append
  of `1`;
- `autarkic_systems/schematic_trace.py` gains
  `STEM_BUFFER_ACCUMULATION_TRACE_ARTIFACT_ID` and validates stem buffer
  alignment separately from stem automail alignment;
- `tests/test_stem_buffer_accumulation_trace.py` checks schema reuse, recorded
  buffer flow, executable replay through `step_stem_cell`, and rejection of
  drifted buffer or drifted flow;
- `docs/stem-buffer-accumulation-trace.md` explains the trace boundary.

This trace does not add command decoding, target routing, or a rendered SVG.

## Success Criteria

- Red tests fail before implementation because the stem buffer trace artifact
  or artifact ID export is absent.
- The new artifact reuses the same Cell field list and interpretive layer
  vocabulary as the existing schematic traces.
- The trace records control `[0, 1, 0]`, input `[0, 1, 0]`, buffer `[0]`, and
  expected buffer `[0, 1]`.
- Replaying the trace through `step_stem_cell` produces the recorded status and
  after-cell.
- Validation rejects a drifted expected buffer.
- Validation rejects a drifted routed-signal-flow description.

## Consequences

- P2/P7 gain a schematic-linked witness for the first non-automail stem
  behavior.
- The trace validator becomes less automail-specific without weakening the
  automail trace checks.
- Full buffer command decoding, target routing, rendered stem-buffer SVG, and
  dynamic reconfiguration remain separate ADRs.

## After Action Report

Red step:

- `python -m unittest tests.test_stem_buffer_accumulation_trace` failed with
  `ImportError: cannot import name 'STEM_BUFFER_ACCUMULATION_TRACE_ARTIFACT_ID'`
  from `autarkic_systems.schematic_trace`.

Green step:

- Added `STEM_BUFFER_ACCUMULATION_TRACE_ARTIFACT_ID`.
- Added `schematics/stem_buffer_accumulation_trace.json`.
- Split stem alignment validation between automail reconfiguration and buffer
  accumulation traces.
- Added `docs/stem-buffer-accumulation-trace.md`.

Full verification:

- `python -m unittest tests.test_stem_buffer_accumulation_trace
  tests.test_stem_automail_reconfiguration_trace` passed 16 tests.
- `python -m unittest discover` passed 117 tests.
- `python -m py_compile autarkic_systems/schematic_trace.py
  tests/test_stem_buffer_accumulation_trace.py` passed.
- `jq -e . schematics/stem_buffer_accumulation_trace.json` passed.
- `git diff --check` passed.

Coverage limits:

- This records one matching-input buffer append only.
- It does not cover control selection, non-matching append, or full-buffer
  boundary as schematic traces.
- It does not render an SVG.
