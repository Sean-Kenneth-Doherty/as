# Substitution Graph Codebook Roundtrip Frontier Status

ADR-0279 adds a compact status surface for the `codebook-roundtrip` proof case
inside the substitution graph correctness case map.

The checked manifest is
`claims/substitution_graph_codebook_roundtrip_frontier_status.json`; the
validator is
`autarkic_systems.substitution_graph_codebook_roundtrip_frontier_status`.

The surface loads these current artifacts:

- `claims/substitution_graph_correctness_cases.json`;
- `claims/substitution_graph_codebook_roundtrip.json`;
- `language/formal_codebook.json`;
- `claims/substitution_graph_formula_candidates.json`; and
- `claims/substitution_graph_evaluation_examples.json`.

It requires the correctness case with kind `codebook-roundtrip` to remain
`proof-case-open`. The frontier remains `blocked` by `codebook-roundtrip`, and
the finite roundtrip support surface remains accepted over 12 graph-domain
code subjects.

This surface is intentionally non-promotional. It does not prove formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.substitution_graph_codebook_roundtrip_frontier_status
python -m autarkic_systems.substitution_graph_codebook_roundtrip_frontier_status --format json
```
