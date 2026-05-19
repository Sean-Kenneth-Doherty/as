# Substitution Graph Meta-Substitution Semantics

Status: finite graph-domain meta-substitution evidence, not a general proof,
2026-05-19.

ADR-0259 adds `claims/substitution_graph_meta_substitution_semantics.json` and
`autarkic_systems/substitution_graph_meta_substitution_semantics.py`. It checks
the concrete meta-level substitutions currently exercised by the substitution
graph formula candidate and finite evaluation examples.

## Purpose

The third substitution graph correctness case asks for assurance that the
meta-level substitution operation used by the evaluator behaves as expected on
the current graph domain before a future proof treats that operation as
generally valid.

The current subject set contains 6 substitutions:

- three formula-candidate graph-variable substitutions that close the witness
  instance; and
- three finite-evaluation substitutions over the current example formulae.

## Run

```sh
python -m autarkic_systems.substitution_graph_meta_substitution_semantics
python -m autarkic_systems.substitution_graph_meta_substitution_semantics --format json
```

The validator checks that:

- the formal codebook, formal substitution examples, formula candidate, and
  finite evaluation dependencies remain accepted;
- the expected source kinds are covered;
- the derived subject count matches the manifest;
- every replacement quotation term is closed;
- every output free-variable set follows the closed-replacement rule;
- every output agrees with the existing expected surface when such a surface
  exists;
- substitutions for variables not free in the input behave as no-ops;
- future work and non-claims remain explicit; and
- stale subject counts fail closed.

## Boundary

This is not a general capture-avoiding substitution proof, not a formula
correctness proof, not a substitution representability proof, not a diagonal
lemma, not a fixed-point equation proof, and not a self-consistency theorem.
It is finite executable evidence for the meta-substitution-semantics
correctness case.
