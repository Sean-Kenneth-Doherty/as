# Fixed-Point Construction Cases

Status: open proof-case map, not a fixed-point proof, 2026-05-19.

ADR-0263 adds `claims/fixed_point_construction_cases.json` and
`autarkic_systems/fixed_point_construction_cases.py`. The surface decomposes
the remaining `fixed-point-construction` blocker into checked open proof
cases.

## Purpose

ADR-0262 names the finite bridge equality still needed between the checked
diagonal instance and the direct fixed-point target form. The construction
case map records what is still missing before that bridge can become a
fixed-point equation proof. ADR-0264 adds finite closure evidence for the
first case, `diagonal-instance-closure`, without closing the construction
blocker.

The checked cases are:

- diagonal instance closure;
- substitution representability proof;
- substitution graph correctness proof;
- bridge equality proof; and
- fixed-point equation lifting.

Each case remains `proof-case-open`.

## Run

```sh
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.fixed_point_construction_cases --format json
python -m autarkic_systems.fixed_point_diagonal_instance_closure
python -m autarkic_systems.fixed_point_diagonal_instance_closure --format json
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.formal_confidence --format json
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the fixed-point target, diagonal construction, substitution witness,
  substitution graph correctness target, substitution graph correctness cases,
  fixed-point equation bridge, fixed-point diagonal-instance closure, and
  formal codebook dependencies remain accepted;
- all five expected construction proof cases are present in order;
- each case keeps `proof-case-open`;
- each case names the expected checked dependency subjects;
- future work and non-claims remain explicit; and
- overclaiming statuses reject.

## Boundary

This is not a substitution representability proof, not a substitution graph
correctness proof, not a bridge equality proof, not a fixed-point equation
proof, not an arithmetized proof predicate, and not a self-consistency theorem.
The formal-confidence target remains blocked on `fixed-point-construction`.
