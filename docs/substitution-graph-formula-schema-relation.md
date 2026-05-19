# Substitution Graph Formula Schema Relation

Status: finite graph-domain formula-schema relation evidence, not a general
proof, 2026-05-19.

ADR-0260 adds `claims/substitution_graph_formula_schema_relation.json` and
`autarkic_systems/substitution_graph_formula_schema_relation.py`. It checks
that the current substitution graph formula candidate, graph target, witness
instance, and finite evaluation examples all state the same concrete
`substitution_code` graph relation.

## Purpose

The fourth substitution graph correctness case asks for assurance that the
checked `substitution_code(x,y) = z` schema is actually aligned with the graph
relation before a future proof treats the schema as generally correct.

The current relation set contains 4 relation points:

- one diagonal witness instance; and
- three finite-evaluation examples.

## Run

```sh
python -m autarkic_systems.substitution_graph_formula_schema_relation
python -m autarkic_systems.substitution_graph_formula_schema_relation --format json
```

The validator checks that:

- the formal codebook, graph target, formula candidate, finite evaluation
  examples, and substitution-representability witness remain accepted;
- the graph target and formula candidate agree on relation name, formula class,
  graph variables, and schema shape;
- the expected source kinds are covered;
- the derived relation point count matches the manifest;
- each schema instance is closed after inserting formula, argument, and output
  codes;
- each formula code decodes and re-encodes through the formal codebook;
- each instantiated schema relation evaluates true under the current finite
  substitution semantics;
- each output agrees with the existing expected witness/example surface;
- future work and non-claims remain explicit; and
- stale relation point counts fail closed.

## Boundary

This is not a general formula correctness proof, not a substitution
representability proof, not a diagonal lemma, not a fixed-point equation
proof, and not a self-consistency theorem. It is finite executable evidence
for the formula-schema-relation correctness case.
