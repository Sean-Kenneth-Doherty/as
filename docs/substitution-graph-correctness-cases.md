# Substitution Graph Correctness Cases

Status: open proof-case decomposition, no case proved, 2026-05-18.

ADR-0254 adds `claims/substitution_graph_correctness_cases.json` and
`autarkic_systems/substitution_graph_correctness_cases.py`. It decomposes the
ADR-0252 substitution graph correctness target into the proof cases that must
be discharged before the checked `substitution_code(x,y) = z` schema can be
treated as correct.

## Purpose

The correctness target is useful because it names the theorem. The case
surface makes the theorem operational: it identifies the checked dependency
surfaces that future proof work must turn into actual proof obligations. The
cases remain explicitly open.

The checked cases are:

- `AS-SUBST-GRAPH-CORRECTNESS-CODEBOOK-ROUNDTRIP`;
- `AS-SUBST-GRAPH-CORRECTNESS-QUOTATION-TERM-CLOSURE`;
- `AS-SUBST-GRAPH-CORRECTNESS-META-SUBSTITUTION-SEMANTICS`;
- `AS-SUBST-GRAPH-CORRECTNESS-FORMULA-SCHEMA-RELATION`; and
- `AS-SUBST-GRAPH-CORRECTNESS-DIAGONAL-WITNESS-COMPOSITION`.

## Run

```sh
python -m autarkic_systems.substitution_graph_correctness_cases
python -m autarkic_systems.substitution_graph_correctness_cases --format json
```

The validator checks that:

- the correctness target, codebook, quotation-term, formal-substitution,
  formula-candidate, and substitution-representability dependencies remain
  accepted;
- case IDs are unique;
- each case targets `AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET`;
- each case preserves `proof-case-open`;
- each case lists the dependencies required for its case kind;
- future work and non-claims are explicit; and
- overclaiming statuses fail closed.

## Boundary

This is not a formula correctness proof, not a substitution representability
proof, not a diagonal lemma, not a fixed-point equation proof, and not a
self-consistency theorem. It is the checked case map for the next proof work.
