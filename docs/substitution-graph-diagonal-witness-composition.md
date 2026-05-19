# Substitution Graph Diagonal Witness Composition

Status: finite graph-domain diagonal-witness composition evidence, not a
general proof, 2026-05-19.

ADR-0261 adds `claims/substitution_graph_diagonal_witness_composition.json`
and `autarkic_systems/substitution_graph_diagonal_witness_composition.py`. It
checks that the substitution graph correctness target, formula-schema relation
witness point, substitution-representability witness, diagonal seed, and
fixed-point target all identify the same concrete self-application route.

## Purpose

The fifth substitution graph correctness case asks for assurance that the graph
correctness route composes with the checked diagonal witness before future work
uses it as part of a representability or fixed-point proof.

The current composition set contains 1 composition:

- the diagonal witness self-application for
  `AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS`.

## Run

```sh
python -m autarkic_systems.substitution_graph_diagonal_witness_composition
python -m autarkic_systems.substitution_graph_diagonal_witness_composition --format json
```

The validator checks that:

- the formal codebook, correctness target, formula candidate,
  formula-schema relation, substitution-representability witness, diagonal
  construction, and fixed-point target remain accepted;
- target IDs, candidate IDs, witness IDs, construction IDs, and fixed-point
  target IDs align;
- the witness formula code, argument code, and diagonal seed code are the same
  self-application input;
- the substitution witness output code and diagonal instance code are
  identical;
- the witness output and diagonal instance agree with the existing expected
  surfaces;
- the formula-schema relation witness point is present and accepted;
- future work and non-claims remain explicit; and
- stale composition counts fail closed.

## Boundary

This is not a general formula correctness proof, not a substitution
representability proof, not a diagonal lemma, not a fixed-point equation
proof, and not a self-consistency theorem. It is finite executable evidence
for the diagonal-witness-composition correctness case.
