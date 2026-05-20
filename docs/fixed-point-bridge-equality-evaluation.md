# Fixed-Point Bridge Equality Evaluation

Status: finite bridge-equality evaluation evidence, not an equality proof,
2026-05-19.

ADR-0269 adds `claims/fixed_point_bridge_equality_evaluation.json` and
`autarkic_systems.fixed_point_bridge_equality_evaluation`. The surface checks
the fourth fixed-point construction proof case by evaluating the current left
bridge term, `substitution_code(quote(seed), quote(seed))`, and comparing its
meta-level output tokens with the right bridge term,
`quote(diagonal_instance)`.

## Purpose

ADR-0267 aligned the bridge-equality case with the checked equation bridge,
witness bridge, graph correctness bridge, and formula-schema witness relation.
ADR-0269 adds the narrower finite evaluation point needed by that same case.

The verifier derives the current bridge-equality evaluation and checks that:

- the fixed-point construction case remains open;
- the construction case requires the equation bridge, substitution
  representability surface, graph correctness cases, bridge-equality alignment,
  and bridge-equality evaluation;
- the fixed-point target, equation bridge, substitution representability
  surface, bridge-equality alignment, and codebook remain accepted;
- the left bridge term is `substitution_code(quote(seed), quote(seed))`;
- the left formula quotation decodes to the current diagonal seed;
- the self-application argument quotation recovers the same seed code;
- evaluating the left substitution-code term produces the 296-token diagonal
  instance code;
- the evaluated output matches the substitution witness output and the right
  quoted bridge term; and
- the bridge equation code length remains 4815.

## Run

```sh
python -m autarkic_systems.fixed_point_bridge_equality_evaluation
python -m autarkic_systems.fixed_point_bridge_equality_evaluation --format json
python -m autarkic_systems.fixed_point_construction_cases
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
```

The validator checks that:

- the construction-case, fixed-point target, equation bridge, substitution
  representability, bridge-equality alignment, and codebook dependencies remain
  accepted;
- exactly one bridge-equality evaluation point is derived;
- the formula and argument code lengths remain 10;
- the evaluated output code length remains 296;
- the bridge equation code length remains 4815;
- the evaluation and route booleans hold; and
- future work and non-claims remain explicit.

## Boundary

This is not a bridge equality proof, not a fixed-point equation proof, not an
arithmetized proof predicate, and not a self-consistency theorem. The
formal-confidence target remains blocked on `fixed-point-construction`.
