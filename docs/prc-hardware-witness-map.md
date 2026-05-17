# PRC Hardware Witness Map

Status: first hardware/schematic evidence map, 2026-05-17.

This map defines the source constraints for AS's first hardware/schematic
evidence path. It is not a circuit design. It is the guardrail that prevents
future hardware work from quietly dropping PRC's actual commitments.

The structured source lives in `sources/prc_hardware_witness_map.json`.

## Recommended Next Artifact

`single-node-triangular-rlem-schematic-and-uc-transition-trace`

The first artifact should be a small AS-owned schematic key for one triangular
RLEM/Universal Cell node, paired with one executable UC transition trace. It
should show:

- three ports and their orientation;
- role: wire, proc, or stem;
- memory direction: right or left;
- input, upstream, output, automail, control, and buffer fields;
- the signal-routing transition being traced;
- which parts are symbolic RLEM behavior, geometric GELC convention, and
  candidate physical circulator implementation.

This is deliberately smaller than a complete GELC circuit or hardware
simulation. The point is to make one node inspectable before scaling up.

## Witnesses

| Witness | Role | AS Constraint |
| --- | --- | --- |
| `PRC-README-UC-CRITERIA` | Abstract cell requirements | Preserve reversible logic, asynchronous operation, explicit signal/power routing, and component-wise reconfigurability. |
| `PRC-GELC-GEOMETRY` | Geometric circuit model | Treat wire geometry as part of the formal circuit definition, not as drawing decoration. |
| `PRC-RLEM-LITERATURE` | Reversible logic foundation | Keep the behavior tied to RLEM-style reversible memory elements. |
| `PRC-CIRCULATOR-PHYSICAL` | Physical implementation candidate | Mark circulators as a candidate physical hypothesis, not verified AS hardware. |
| `PRC-RALA-RECONFIGURATION` | Prior-art reconfiguration pressure | Separate UC core behavior from auxiliary buffering and reconfiguration support. |
| `PRC-UC-FORMAL-MODEL` | Formal transition model | Reuse the PRC field vocabulary and Mealy-machine activation frame. |
| `PRC-ASM-SIMULATOR` | Executable transition semantics | Treat `asmsim.scm` as an implementation witness, not an oracle. |
| `PRC-SCHEMATIC-FIGURES` | Schematic source | Redraw only the minimum single-node/port-orientation key needed for trace work. |

## Immediate Constraints

The first schematic must distinguish four layers:

- symbolic behavior: RLEM signal redirection and memory;
- geometry: triangular nodes, ports, wire paths, and memory orientation;
- UC state: role, upstream, input, output, memory, automail, control, buffer;
- physical hypothesis: switchable latching circulator plus auxiliary
  electronics.

The first simulation trace should connect to the existing AS Universal Cell
probe rather than bypassing it. If a new transition behavior is needed, it
should be added by ADR with red tests first.

## Verification

Run:

```sh
python -m unittest tests.test_prc_hardware_witness_map
```

The test validates required witness coverage, pinned PRC source paths, AS
relevance, simulation constraints, and the recommended next artifact.

## Open Follow-Ups

- Draw the single-node triangular RLEM schematic key as an AS-owned artifact.
- Add one schematic-linked UC transition trace over the existing Python Cell
  fields.
- Decide whether larger GELC examples should be copied/redrawn from
  `figures.pdf` or reconstructed from a structured circuit description.
- Keep physical circulator simulation separate until symbolic RLEM/GELC
  behavior is stable.
