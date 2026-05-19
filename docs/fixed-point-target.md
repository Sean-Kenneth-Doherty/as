# Fixed-Point Target

Status: checked target template, not a constructed fixed point, 2026-05-18.

ADR-0231 adds `claims/fixed_point_targets.json` and
`autarkic_systems/fixed_point.py`. The target selects a first `pi1`
self-reference template and validates one substitution instance over the
formal codebook.

## Purpose

AS now has a formal codebook, capture-avoiding substitution examples, token
numeral quotation examples, token-numeral sequence examples, quotation term
examples, a checked `substitution_code` term surface, a checked naive equation
candidate, a checked diagonal seed surface, a checked substitution graph
witness for that seed, a checked delta0 graph-formula target boundary, a
checked substitution graph formula schema candidate, a Level-1 consistency
target, and a selected deduction-apparatus target. Those are prerequisites for a
SelfCons-style statement, but they still do not construct a diagonal fixed
point.

The fixed-point target records the next precise obligation:

- a `pi1` template with free code variable `n`;
- a placeholder term used only to validate substitution plumbing;
- an expected substituted instance;
- the expected encoded output for that instance; and
- explicit future work before any self-consistency claim.

## Current Target

`AS-FIXED-POINT-SELFCONS1-TARGET` is
`target-selected-not-constructed`.

It names these Willard anchors as constraints:

- `W2011-D3.4-GENERIC-CONFIGURATION`;
- `W2011-D5.6-LEVEL-K-CONSISTENCY`;
- `W2011-D5.7-SELFCONSK`; and
- `W2020-D3.2-SELF-JUSTIFYING-GENAC`.

The checked instance proves only that the current substitution, codebook,
token quotation, token-numeral sequence, and quotation-term surfaces can
preserve the selected template boundary and round-trip the expected encoded
instance. ADR-0235 additionally checks the naive quotation substitution and
records that it is not a fixed point. ADR-0241 adds the coding term needed to
state a diagonal substitution route without repeating that direct
self-embedding move. ADR-0242 adds the first checked seed and quoted seed
instance for that route while leaving substitution representability and the
diagonal lemma open. ADR-0244 checks the corresponding meta-level
self-application graph witness without claiming the delta0 graph formula or
representability proof. ADR-0246 records the delta0 graph-formula target
boundary for that witness, and ADR-0248 records the first checked formula
schema candidate, while still leaving formula correctness and proof open.
ADR-0262 records the finite equality bridge target between the checked
diagonal instance and the direct fixed-point target form, while still leaving
that equality and the fixed-point equation unproved. ADR-0263 records the
open proof-case map for converting those checked finite surfaces into an
actual fixed-point construction, while keeping every case unproved. ADR-0264
adds finite closure evidence for the derived diagonal instance, while leaving
representability, bridge equality, and equation lifting open.

## Run

```sh
python -m autarkic_systems.fixed_point
python -m autarkic_systems.fixed_point --format json
python -m autarkic_systems.formal_quotation_sequence
python -m autarkic_systems.formal_quotation_term
python -m autarkic_systems.diagonal_construction
python -m autarkic_systems.substitution_representability
python -m autarkic_systems.substitution_graph_target
python -m autarkic_systems.substitution_graph_formula
python -m autarkic_systems.fixed_point_equation
python -m autarkic_systems.fixed_point_equation_bridge
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.fixed_point_diagonal_instance_closure
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- required Willard anchors are present and known;
- the codebook, substitution examples, token quotation examples,
  token-numeral sequence examples, quotation term examples,
  consistency-level target, and
  deduction-apparatus target remain accepted;
- the template is a `pi1` target with the target variable free;
- the substitution instance matches the expected node and code; and
- proved fixed-point statuses are rejected.

## Boundary

This is not a diagonal lemma, not arithmetic sequence axioms, not a
fixed-point equation proof, and not a self-consistency theorem. The
formal-confidence target remains blocked on `fixed-point-construction`.
