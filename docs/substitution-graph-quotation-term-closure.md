# Substitution Graph Quotation Term Closure

Status: finite graph-domain quotation-term closure evidence, not a general
proof, 2026-05-19.

ADR-0258 adds `claims/substitution_graph_quotation_term_closure.json` and
`autarkic_systems/substitution_graph_quotation_term_closure.py`. It reuses the
ADR-0257 graph-domain code subject derivation, quotes each code sequence as a
nested `sequence_cons` / `sequence_nil` term, and checks that every resulting
term is closed, recovers the original token sequence, and round-trips through
`language/formal_codebook.json`.

## Purpose

The second substitution graph correctness case asks for assurance that the
current graph-domain code sequences can be quoted as the closed term shape used
by the evaluator before a future proof treats that quotation operation as
generally valid.

The current subject set contains 12 codes:

- three formula-candidate subjects; and
- nine finite-evaluation subjects.

The largest current subject is the checked witness instance code with 4,815
tokens. The verifier handles that finite deep quotation explicitly while
leaving the shared formal encoder unchanged.

## Run

```sh
python -m autarkic_systems.substitution_graph_quotation_term_closure
python -m autarkic_systems.substitution_graph_quotation_term_closure --format json
```

The validator checks that:

- the formal codebook, quotation-term examples, formula candidate, and finite
  evaluation dependencies remain accepted;
- the expected source kinds are covered;
- the derived subject count matches the manifest;
- every derived code quotes to a closed term;
- every quoted term recovers the original code-token sequence;
- every quoted term encodes and decodes through the formal codebook;
- future work and non-claims remain explicit; and
- stale subject counts fail closed.

## Boundary

This is not a formula correctness proof, not a substitution representability
proof, not a diagonal lemma, not a fixed-point equation proof, and not a
self-consistency theorem. It is finite executable evidence for the
quotation-term-closure correctness case.
