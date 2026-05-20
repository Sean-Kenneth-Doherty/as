# Fixed-Point Construction Frontier Status

ADR-0273 adds a compact status surface for the post-ADR-0270 fixed-point
construction stack.

The checked manifest is
`claims/fixed_point_construction_frontier_status.json`; the validator is
`autarkic_systems.fixed_point_construction_frontier_status`.

The surface loads the current construction/frontier dependencies:

- `claims/fixed_point_construction_cases.json`;
- `claims/fixed_point_diagonal_instance_candidate_surface.json`;
- `claims/fixed_point_substitution_witness_bridge.json`;
- `claims/fixed_point_substitution_graph_correctness_bridge.json`;
- `claims/fixed_point_bridge_equality_alignment.json`;
- `claims/fixed_point_bridge_equality_evaluation.json`; and
- `claims/fixed_point_equation_lifting_alignment.json`.

It reports per-case finite support and requires all five construction cases to
remain `proof-case-open`. The aggregate frontier remains `blocked` by
`fixed-point-construction`.

This surface is intentionally non-promotional. It does not prove substitution
representability, substitution graph correctness, bridge equality, a
fixed-point equation, an arithmetized proof predicate, or self-consistency.

Run:

```sh
python -m autarkic_systems.fixed_point_construction_frontier_status
python -m autarkic_systems.fixed_point_construction_frontier_status --format json
```
