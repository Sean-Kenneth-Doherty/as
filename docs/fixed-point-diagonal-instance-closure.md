# Fixed-Point Diagonal Instance Closure

Status: finite closure evidence, not a fixed-point proof, 2026-05-19.

ADR-0264 adds `claims/fixed_point_diagonal_instance_closure.json` and
`autarkic_systems/fixed_point_diagonal_instance_closure.py`. The surface checks
the first fixed-point construction proof case against the current diagonal
instance, codebook, target, and bridge surfaces.

## Purpose

ADR-0263 made `diagonal-instance-closure` the first open construction case.
This evidence narrows that case from broad dependency names to a finite checked
closure point.

The verifier derives the current diagonal instance and checks that it:

- is closed;
- round-trips through the checked formal codebook;
- preserves the selected fixed-point target skeleton;
- places `substitution_code(quote(seed), quote(seed))` in the target slot; and
- matches the diagonal instance recorded by the fixed-point equation bridge.

## Run

```sh
python -m autarkic_systems.fixed_point_diagonal_instance_closure
python -m autarkic_systems.fixed_point_diagonal_instance_closure --format json
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the fixed-point target, diagonal construction, fixed-point equation bridge,
  and formal codebook dependencies remain accepted;
- exactly one closure point is derived;
- the diagonal instance length and prefix remain current;
- the diagonal instance is closed and codebook-stable;
- the fixed-point target skeleton and diagonal slot are preserved;
- the bridge observation names the same closed diagonal instance; and
- future work and non-claims remain explicit.

## Boundary

This is not a substitution representability proof, not a substitution graph
correctness proof, not a bridge equality proof, not a fixed-point equation
proof, not an arithmetized proof predicate, and not a self-consistency theorem.
The formal-confidence target remains blocked on `fixed-point-construction`.
