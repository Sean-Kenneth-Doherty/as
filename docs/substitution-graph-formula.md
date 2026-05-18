# Substitution Graph Formula Schema

Status: checked formula schema, not a correctness proof, 2026-05-18.

ADR-0248 adds `claims/substitution_graph_formula_candidates.json` and
`autarkic_systems/substitution_graph_formula.py`. It records the first checked
syntactic formula candidate for the ADR-0246 substitution graph target:
`substitution_code(x,y) = z`. ADR-0249 makes this candidate a structured
dependency of the aggregate formal-confidence target, so formal-confidence
validation fails closed if this surface drifts.

## Purpose

The substitution graph target names the relation AS needs for the diagonal
route, but the target alone is not a formula. This surface constructs the
first candidate formula schema and checks that it is stable under the current
formal codebook and witness data.

The schema records:

- relation target `subst_code_graph`;
- formula class `delta0`;
- graph variables `x`, `y`, and `z`;
- formula node `substitution_code(x,y) = z`;
- code for that formula node; and
- one closed witness instance formed by substituting the checked witness codes
  into the formula.

## Current Candidate

`AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA` is
`formula-schema-not-proved`.

The formula node is:

```text
substitution_code(x,y) = z
```

The checked formula code is:

```text
[21, 18, 11, 1, 11, 2, 11, 3]
```

The checked formula free variables are:

```text
x, y, z
```

The witness instance substitutes quoted formula, argument, and output codes
from `AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS`. The resulting
instance is closed, has code length `4815`, and begins:

```text
[21, 18, 17, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13, 13]
```

## Run

```sh
python -m autarkic_systems.substitution_graph_formula
python -m autarkic_systems.substitution_graph_formula --format json
```

The validator checks that:

- the formal arithmetic language, formal codebook, substitution graph target,
  and substitution-representability witness dependencies remain accepted;
- candidate IDs are unique;
- the candidate preserves `formula-schema-not-proved`;
- the relation name is `subst_code_graph`;
- the formula class is `delta0`;
- the formula node is exactly `substitution_code(x,y) = z`;
- the formula code and free variables match the manifest; and
- the checked witness instance length, prefix, and free-variable boundary
  match the manifest.

## Boundary

This is not a formula correctness proof, not a substitution representability
proof, not a diagonal lemma, not a fixed-point equation proof, and not a
self-consistency theorem. The next AS step is to prove that this formula
schema correctly represents the checked `substitution_code` graph before using
it in the diagonal lemma route.
