# Substitution Graph Formula-Schema-Relation Frontier Status

ADR-0282 adds a compact status surface for the substitution graph correctness
`formula-schema-relation` proof case.

The checked manifest is
`claims/substitution_graph_formula_schema_relation_frontier_status.json`; the
validator is
`autarkic_systems.substitution_graph_formula_schema_relation_frontier_status`.

The surface loads:

- `claims/substitution_graph_correctness_cases.json`; and
- `claims/substitution_graph_formula_schema_relation.json`.

It requires the matching correctness case to remain `proof-case-open`, the
frontier to remain `blocked` by `formula-schema-relation`, and the existing
formula-schema-relation support validator to accept with no failed subjects.
The compact support facts preserve the current four relation points and the
witness-instance / finite-evaluation source-kind split.

This surface is intentionally non-promotional. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.substitution_graph_formula_schema_relation_frontier_status
python -m autarkic_systems.substitution_graph_formula_schema_relation_frontier_status --format json
```
