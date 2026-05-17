# ADR-0015: PRC Hardware Witness Map

Date: 2026-05-17

Status: Accepted

## Context

P7 asks for the smallest schematic or simulation artifact that honors PRC's
physical implementation claims without requiring full hardware design. AS has
already extracted a small Universal Cell transition probe, but it does not yet
have a disciplined hardware/schematic evidence path.

The risk is easy to name: AS could draw something that visually resembles PRC
while silently dropping the actual PRC constraints. PRC requires reversible
logic, asynchronous operation, explicit signal and power routing, and organic
component-wise reconfigurability. It also ties Universal Cells to RLEM/GELC
geometry, possible switchable circulator physics, RALA-like reconfiguration
support, a formal Mealy-machine model, and a Scheme ASM witness.

## Decision

Add a structured PRC hardware witness map before drawing or simulating a new
hardware artifact:

- `sources/prc_hardware_witness_map.json` records the required PRC source
  witnesses and simulation constraints;
- `autarkic_systems/prc_hardware_map.py` loads and validates the map;
- `tests/test_prc_hardware_witness_map.py` verifies required witness coverage,
  source-path pinning, AS relevance, and the recommended next artifact;
- `docs/prc-hardware-witness-map.md` explains the first hardware/schematic
  path in human terms.

The recommended next artifact is:

`single-node-triangular-rlem-schematic-and-uc-transition-trace`

That artifact is deliberately smaller than a full hardware design. It should
define a single triangular RLEM/Universal Cell schematic key with ports, role,
memory direction, and signal routing, then connect it to one AS Universal Cell
transition trace.

## Success Criteria

- Red tests fail before implementation because the PRC hardware map module is
  absent.
- The structured map covers:
  - UC requirement criteria;
  - GELC geometry;
  - RLEM literature;
  - circulator physical hypothesis;
  - RALA/reconfiguration prior-art pressure;
  - UC formal model;
  - ASM simulator;
  - schematic figures.
- Every witness pins a PRC-local source path under
  `/home/sean/Projects/_upstream/prc`.
- Every witness states AS relevance and a simulation constraint.
- The map records a single recommended next artifact.

## Consequences

- P7 now has a concrete entry path into schematic/simulation work.
- AS can distinguish symbolic RLEM behavior, UC transition semantics,
  geometric circuit layout, and candidate physical circulator evidence.
- Later schematic work should not start from blank design taste; it should
  preserve the witness constraints in this map.

## After Action Report

Red step:

- `python -m unittest tests.test_prc_hardware_witness_map` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems.prc_hardware_map'`.

Green step:

- Added `autarkic_systems/prc_hardware_map.py`.
- Added `sources/prc_hardware_witness_map.json`.
- Added `docs/prc-hardware-witness-map.md`.
- `python -m unittest tests.test_prc_hardware_witness_map` passed 4 tests.

Full verification:

- `python -m unittest tests.test_prc_hardware_witness_map` passed 4 tests.
- `python -m unittest discover` passed 54 tests.
- `python -m py_compile autarkic_systems/prc_hardware_map.py
  tests/test_prc_hardware_witness_map.py` passed.
- `jq -e . sources/prc_hardware_witness_map.json` passed.
- `git diff --check` passed.

Coverage limits:

- This slice is a source-backed witness map, not a schematic, hardware model,
  or circuit simulator.
- Default fast tests validate pinned source paths rather than requiring the
  disposable `_upstream` PRC clone to exist.
- The first recommended artifact is intentionally a single-node schematic and
  trace; full GELC universality diagrams, 3-D lattice work, and circulator
  physics simulation remain later work.
