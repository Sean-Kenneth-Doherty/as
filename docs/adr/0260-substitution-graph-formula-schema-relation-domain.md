# ADR-0260: Substitution Graph Formula Schema Relation Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0254 decomposed substitution graph correctness into five open proof cases.
ADR-0257, ADR-0258, and ADR-0259 added finite evidence surfaces for the first
three cases: codebook roundtrip, quotation-term closure, and
meta-substitution semantics.

The fourth case, `formula-schema-relation`, still depends only on the checked
formula candidate. That candidate proves useful syntax facts and one witness
evaluation, but the case map does not yet name a finite domain that checks
whether the candidate schema, graph target, witness instance, and finite
evaluation examples all state the same substitution-code graph relation.

## Decision

Add `claims/substitution_graph_formula_schema_relation.json` and
`autarkic_systems.substitution_graph_formula_schema_relation`.

The verifier will derive finite relation points from:

- the checked diagonal witness instance used by the formula candidate; and
- the three finite substitution graph evaluation examples.

For each point, it instantiates the current formula schema
`substitution_code(x,y) = z` with a formula code, argument code, and expected
output code. It then checks that the schema instance is closed, that decoding
the formula code and applying the current meta-level substitution yields the
same output code named on the right side, and that the output agrees with the
existing expected witness/example surface.

The verifier also checks that the graph target and formula candidate agree on
relation name, formula class, graph variables, and schema shape.

Make the `formula-schema-relation` correctness case depend on this verifier via
a new `formula_schema_relation_path` field in
`claims/substitution_graph_correctness_cases.json`.

This is finite relation evidence only. It does not prove general formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the formula-schema relation
  verifier and manifest do not exist, the correctness-case manifest has no
  `formula_schema_relation_path`, and the fourth case does not depend on
  `formula_schema_relation`.
- The new verifier accepts the checked finite relation point set.
- The verifier derives 4 relation points: one witness instance and three
  finite-evaluation examples.
- Text and JSON output expose accepted relation status, relation point counts,
  source-kind counts, and no relation failures.
- Stale relation point counts reject the verifier.
- The correctness-case validator fails closed over the new verifier and
  reports `formula_schema_relation` as an accepted dependency on the healthy
  path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_formula_schema_relation
  tests.test_substitution_graph_correctness_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live formula-schema-relation text/JSON, live
  correctness-cases text/JSON, live formal-confidence text, live project-status
  summary, compileall, `git diff --check`, and the full default suite.

## After Action Report

Implemented in `claims/substitution_graph_formula_schema_relation.json` and
`autarkic_systems/substitution_graph_formula_schema_relation.py`.

The red run failed for the intended reasons: the verifier module and manifest
were absent, `SubstitutionGraphCorrectnessCaseManifest` had no
`formula_schema_relation_path`, and the `formula-schema-relation` case still
listed only `correctness_target` and `formula_candidate`.

The finished verifier derives 4 relation points: one witness instance from the
formula candidate's diagonal witness and three finite-evaluation examples. It
checks graph-target/formula-candidate alignment, closed schema instances,
formula-code roundtrip, instantiated relation truth, and agreement with the
existing witness/example output surfaces. The correctness-case validator now
reports `formula_schema_relation` as an accepted dependency for the fourth
open case.

Validation passed:

```sh
python -m unittest tests.test_substitution_graph_formula_schema_relation tests.test_substitution_graph_correctness_cases
python -m unittest tests.test_substitution_graph_formula_schema_relation tests.test_substitution_graph_correctness_cases tests.test_substitution_graph_formula tests.test_substitution_graph_evaluation tests.test_substitution_graph_correctness_target
python -m autarkic_systems.substitution_graph_formula_schema_relation
python -m autarkic_systems.substitution_graph_formula_schema_relation --format json
python -m autarkic_systems.substitution_graph_correctness_cases --format json
python -m autarkic_systems.formal_confidence
python -m autarkic_systems.project_status --format summary
python -m compileall autarkic_systems tests
jq -e . claims/substitution_graph_formula_schema_relation.json claims/substitution_graph_correctness_cases.json
git diff --check
python -m unittest discover
```

The full default suite passed 1,222 tests in 347.404s. This adds finite
relation evidence for the fourth correctness case. It still does not prove
general formula correctness, substitution representability, the diagonal
lemma, a fixed-point equation, or self-consistency.
