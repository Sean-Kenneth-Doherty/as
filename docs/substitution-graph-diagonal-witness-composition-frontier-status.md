# Substitution Graph Diagonal-Witness-Composition Frontier Status

ADR-0283 adds a compact status surface for the substitution graph correctness
`diagonal-witness-composition` proof case.

The checked manifest is
`claims/substitution_graph_diagonal_witness_composition_frontier_status.json`;
the validator is
`autarkic_systems.substitution_graph_diagonal_witness_composition_frontier_status`.

The surface loads:

- `claims/substitution_graph_correctness_cases.json`; and
- `claims/substitution_graph_diagonal_witness_composition.json`.

It requires the matching correctness case to remain `proof-case-open`, the
frontier to remain `blocked` by `diagonal-witness-composition`, and the
existing diagonal-witness-composition support validator to accept with no
failed subjects. The compact support facts preserve the current single
composition subject and the `diagonal-witness` source kind.

This surface is intentionally non-promotional. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.substitution_graph_diagonal_witness_composition_frontier_status
python -m autarkic_systems.substitution_graph_diagonal_witness_composition_frontier_status --format json
```
