# ADR-0026: Stem Command Buffer Map

Date: 2026-05-17

Status: Accepted

## Context

ADR-0022 stops stem buffer behavior at a full-buffer boundary. The PRC formal
model gives the next layer: a five-bit command buffer maps values `0` through
`31` to target plus command pairs. The source text groups the values into four
target ranges of eight commands each: self, A neighbor, B neighbor, and C
neighbor.

AS should not implement full command execution until this encoding is explicit
and testable. Otherwise the command decoder would be hidden in transition code,
making it harder to audit against PRC's formal-model text.

## Decision

Add a structured stem command-buffer map:

- `sources/stem_command_buffer_map.json` records target ranges, the eight
  command offsets, the bit-order convention used by AS, and the PRC source
  witness;
- `autarkic_systems/stem_command_map.py` loads, validates, and decodes
  five-bit buffers into target/command pairs;
- `tests/test_stem_command_buffer_map.py` verifies source anchoring, complete
  32-value coverage, representative decodes, and rejection of bad map/buffer
  inputs;
- `docs/stem-command-buffer-map.md` explains the boundary and why command
  execution remains separate.

AS interprets the accumulated five-bit buffer in list order as a binary value
with the first accumulated bit as the most significant bit. This is a local
decoding convention for the explicit AS artifact; future execution ADRs must
preserve or revise it deliberately.

## Success Criteria

- Red tests fail before implementation because `autarkic_systems.stem_command_map`
  is absent.
- The map validates four target ranges and eight command offsets.
- Generated coverage contains exactly 32 unique values.
- Representative buffers decode as expected: `00000` self/standard-signal,
  `00101` self/proc-l-init, `01000` neighbor-a/standard-signal, `10101`
  neighbor-b/proc-l-init, and `11111` neighbor-c/write-buf-one.
- Invalid buffers and incomplete maps are rejected.

## Consequences

- Future full-buffer processing can depend on a named map rather than embedded
  magic numbers.
- This does not execute commands, mutate cells, or route neighbor messages.
- If later PRC source review changes bit order or command ordering, the map and
  its ADR must be revised before execution code changes.

## After Action Report

Red step:

- `python -m unittest tests.test_stem_command_buffer_map` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems.stem_command_map'`.

Green step:

- Added `sources/stem_command_buffer_map.json`.
- Added `autarkic_systems/stem_command_map.py`.
- Added `docs/stem-command-buffer-map.md`.
- `python -m unittest tests.test_stem_command_buffer_map` passed 8 tests.

Refinement red step:

- Added noncanonical target-range and command-name rejection tests. They failed
  until validation checked the exact four PRC target ranges and eight PRC
  command mappings.

Full verification:

- `python -m unittest discover` passed 132 tests.
- `python -m py_compile autarkic_systems/stem_command_map.py
  tests/test_stem_command_buffer_map.py` passed.
- `jq -e . sources/stem_command_buffer_map.json` passed.
- `git diff --check` passed.

Coverage limits:

- This maps command values only.
- It does not interpret special messages into `Cell` mutations.
- It does not route output to neighbors.
