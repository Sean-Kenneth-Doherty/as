# Substitution Graph Correctness Target

Status: correctness proof target, proof not constructed, 2026-05-18.

ADR-0252 adds `claims/substitution_graph_correctness_targets.json` and
`autarkic_systems/substitution_graph_correctness.py`. It records the proof
obligation that the checked delta0 formula schema must satisfy before the
diagonal construction can depend on the substitution graph route. ADR-0253
makes this proof target a fail-closed dependency of aggregate
formal-confidence validation. ADR-0254 decomposes this target into open proof
cases for the next proof work.

## Purpose

The existing graph target, formula schema, witness evaluation, and finite
examples are useful only if they remain separated from the theorem they have
not yet proved. This target makes that boundary explicit: it binds the current
graph target, formula candidate, and finite examples while keeping the
correctness proof open.

The checked target is:

- `AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET`.

It binds:

- graph target `AS-SUBSTITUTION-GRAPH-DELTA0-TARGET`;
- formula candidate `AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA`;
- relation `subst_code_graph`;
- formula class `delta0`; and
- the three finite evaluation examples from ADR-0251.

## Run

```sh
python -m autarkic_systems.substitution_graph_correctness
python -m autarkic_systems.substitution_graph_correctness --format json
```

The validator checks that:

- the formal arithmetic language, formal codebook, graph target, formula
  candidate, and finite evaluation dependencies remain accepted;
- target IDs are unique;
- the target preserves `correctness-proof-not-constructed`;
- the formula candidate still targets the checked graph target;
- every listed finite example exists and evaluates true;
- required future work and non-claims are explicit; and
- overclaiming statuses fail closed.

ADR-0254 adds a companion case validator:

```sh
python -m autarkic_systems.substitution_graph_correctness_cases
python -m autarkic_systems.substitution_graph_correctness_cases --format json
```

## Boundary

This is not a formula correctness proof, not a substitution representability
proof, not a diagonal lemma, not a fixed-point equation proof, and not a
self-consistency theorem. It is a checked theorem target and case map for the
next proof step.
