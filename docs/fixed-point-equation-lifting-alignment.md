# Fixed-Point Equation Lifting Alignment

Status: finite equation-lifting alignment evidence, not a fixed-point equation
proof, 2026-05-19.

ADR-0268 adds `claims/fixed_point_equation_lifting_alignment.json` and
`autarkic_systems.fixed_point_equation_lifting_alignment`. The surface checks
the fifth fixed-point construction proof case against the current selected
`pi1` fixed-point target, fixed-point equation bridge, bridge-equality
alignment, and formal codebook.

## Purpose

ADR-0263 made `fixed-point-equation-lifting` the fifth open construction case.
ADR-0268 narrows that case from broad dependency names to a finite checked
alignment point.

The verifier derives the current equation-lifting alignment and checks that:

- the fixed-point construction case remains open;
- the construction case requires the fixed-point target, equation bridge,
  codebook, and equation-lifting alignment;
- the fixed-point target, equation bridge, bridge-equality alignment, and
  codebook remain accepted;
- the selected target remains the current `pi1` template over free code
  variable `n`;
- the equation bridge direct target remains closed, target-skeleton matched,
  and filled by quoting the checked diagonal instance;
- the bridge-equality alignment remains route-aligned and schema-instance
  aligned; and
- the direct target code length remains 4528.

## Run

```sh
python -m autarkic_systems.fixed_point_equation_lifting_alignment
python -m autarkic_systems.fixed_point_equation_lifting_alignment --format json
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the construction-case, fixed-point target, equation bridge,
  bridge-equality alignment, and codebook dependencies remain accepted;
- exactly one equation-lifting alignment point is derived;
- the direct target code length remains 4528;
- the target/context and bridge/alignment booleans hold; and
- future work and non-claims remain explicit.

## Boundary

This is not a bridge equality proof, not a fixed-point equation proof, not an
arithmetized proof predicate, and not a self-consistency theorem. The
formal-confidence target remains blocked on `fixed-point-construction`.
