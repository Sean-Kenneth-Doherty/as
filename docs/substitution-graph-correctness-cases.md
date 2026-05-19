# Substitution Graph Correctness Cases

Status: open proof-case decomposition, no case proved, 2026-05-18.

ADR-0254 adds `claims/substitution_graph_correctness_cases.json` and
`autarkic_systems/substitution_graph_correctness_cases.py`. It decomposes the
ADR-0252 substitution graph correctness target into the proof cases that must
be discharged before the checked `substitution_code(x,y) = z` schema can be
treated as correct.

ADR-0255 makes this case map visible to aggregate formal-confidence validation:
if the case map disappears or drifts, the formal-confidence target now rejects
instead of silently treating the correctness route as aligned.

ADR-0257 adds a finite codebook-roundtrip verifier for the graph-domain codes
currently exercised by the formula candidate and finite evaluation examples,
then makes the `codebook-roundtrip` case depend on that verifier.

ADR-0258 adds a finite quotation-term-closure verifier over the same graph
domain, then makes the `quotation-term-closure` case depend on that accepted
closure evidence.

ADR-0259 adds a finite meta-substitution-semantics verifier over the concrete
substitutions currently used by the formula candidate and finite evaluator,
then makes the `meta-substitution-semantics` case depend on that accepted
semantic evidence.

ADR-0260 adds a finite formula-schema-relation verifier over the witness
instance and finite evaluator examples, then makes the
`formula-schema-relation` case depend on that accepted relation evidence.

ADR-0261 adds a finite diagonal-witness-composition verifier over the current
self-application route, then makes the `diagonal-witness-composition` case
depend on that accepted composition evidence.

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
python -m autarkic_systems.substitution_graph_codebook_roundtrip
python -m autarkic_systems.substitution_graph_codebook_roundtrip --format json
python -m autarkic_systems.substitution_graph_quotation_term_closure
python -m autarkic_systems.substitution_graph_quotation_term_closure --format json
python -m autarkic_systems.substitution_graph_meta_substitution_semantics
python -m autarkic_systems.substitution_graph_meta_substitution_semantics --format json
python -m autarkic_systems.substitution_graph_formula_schema_relation
python -m autarkic_systems.substitution_graph_formula_schema_relation --format json
python -m autarkic_systems.substitution_graph_diagonal_witness_composition
python -m autarkic_systems.substitution_graph_diagonal_witness_composition --format json
```

The validator checks that:

- the correctness target, codebook, quotation-term, formal-substitution,
  formula-candidate, and substitution-representability dependencies remain
  accepted;
- the codebook-roundtrip domain dependency remains accepted for the first case;
- the quotation-term-closure domain dependency remains accepted for the second
  case;
- the meta-substitution-semantics domain dependency remains accepted for the
  third case;
- the formula-schema-relation domain dependency remains accepted for the fourth
  case;
- the diagonal-witness-composition domain dependency remains accepted for the
  fifth case;
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
