# Fixed-Point Equation Bridge

Status: checked finite bridge target, not a fixed-point proof, 2026-05-19.

ADR-0262 adds `claims/fixed_point_equation_bridge_targets.json` and
`autarkic_systems/fixed_point_equation_bridge.py`. The bridge target computes
the exact gap between the checked diagonal instance and the direct fixed-point
target form.

## Purpose

The diagonal route builds:

```text
Phi(substitution_code(quote(seed), quote(seed)))
```

The direct fixed-point target form would be:

```text
Phi(quote(diagonal_instance))
```

Those are not syntactically identical in the current codebook. The bridge
target names the missing finite equality:

```text
substitution_code(quote(seed), quote(seed)) = quote(diagonal_instance)
```

Proving that equality is still future work. This surface only makes the
obligation executable and fail-closed. ADR-0263 decomposes that future work
into an open construction-case map at
`claims/fixed_point_construction_cases.json`. ADR-0264 checks that the
diagonal instance named by this bridge is closed, codebook-stable, and aligned
with the selected fixed-point target skeleton.

## Current Surface

`as-fixed-point-equation-bridge-v1` validates one bridge:

- `AS-FIXED-POINT-SELFCONS1-DIAGONAL-EQUATION-BRIDGE`;
- diagonal instance code length: `296`;
- direct target code length: `4528`;
- bridge equality code length: `4815`;
- bridge left term length: `291`;
- bridge right term length: `4523`; and
- syntactic diagonal/direct target equality: `false`.

The verifier checks that the diagonal instance, direct target form, and bridge
equality are closed; that the diagonal and direct forms share the selected
fixed-point target skeleton; that the diagonal slot is
`substitution_code(quote(seed), quote(seed))`; that the direct slot quotes the
diagonal instance; and that the substitution witness output still matches the
diagonal instance code.

## Run

```sh
python -m autarkic_systems.fixed_point_equation_bridge
python -m autarkic_systems.fixed_point_equation_bridge --format json
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.fixed_point_construction_cases --format json
python -m autarkic_systems.fixed_point_diagonal_instance_closure
python -m autarkic_systems.fixed_point_diagonal_instance_closure --format json
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.formal_confidence --format json
python -m autarkic_systems.project_status --format summary
```

## Boundary

This is not a substitution representability proof, not a substitution graph
correctness proof, not a fixed-point equation proof, not an arithmetized proof
predicate, and not a self-consistency theorem. The formal-confidence target
remains blocked on `fixed-point-construction`.
