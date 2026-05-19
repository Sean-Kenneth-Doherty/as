# ADR-0261: Substitution Graph Diagonal Witness Composition Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0254 decomposed substitution graph correctness into five open proof cases.
ADR-0257 through ADR-0260 added finite evidence surfaces for the first four
cases: codebook roundtrip, quotation-term closure, meta-substitution
semantics, and formula-schema relation.

The fifth case, `diagonal-witness-composition`, still depends only on the
substitution-representability witness. That witness validates the concrete
meta-level substitution graph point, but the correctness-case map does not yet
name a finite domain that checks whether the graph correctness target,
formula-schema relation point, substitution-representability witness, diagonal
seed, and fixed-point target are all the same self-application route.

## Decision

Add `claims/substitution_graph_diagonal_witness_composition.json` and
`autarkic_systems.substitution_graph_diagonal_witness_composition`.

The verifier will derive the current diagonal witness composition point from:

- the substitution graph correctness target;
- the formula candidate and finite formula-schema relation witness point;
- the substitution-representability witness;
- the diagonal construction seed; and
- the fixed-point target.

It checks that the witness IDs, construction IDs, target IDs, variables, seed
code, self-application argument code, diagonal instance code, and formula-schema
relation witness point all align. It also checks that the witness output code
and diagonal instance code are identical.

Make the `diagonal-witness-composition` correctness case depend on this
verifier via a new `diagonal_witness_composition_path` field in
`claims/substitution_graph_correctness_cases.json`.

This is finite composition evidence only. It does not prove general formula
correctness, substitution representability, the diagonal lemma, a fixed-point
equation, or self-consistency.

## Success Criteria

- Red tests fail before implementation because the diagonal-witness composition
  verifier and manifest do not exist, the correctness-case manifest has no
  `diagonal_witness_composition_path`, and the fifth case does not depend on
  `diagonal_witness_composition`.
- The new verifier accepts the checked finite composition point set.
- The verifier derives 1 composition point for the current diagonal witness.
- Text and JSON output expose accepted composition status, composition counts,
  source-kind counts, and no composition failures.
- Stale composition counts reject the verifier.
- The correctness-case validator fails closed over the new verifier and
  reports `diagonal_witness_composition` as an accepted dependency on the
  healthy path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_substitution_graph_diagonal_witness_composition
  tests.test_substitution_graph_correctness_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live diagonal-witness-composition text/JSON, live
  correctness-cases text/JSON, live formal-confidence text, live project-status
  summary, compileall, `git diff --check`, and the full default suite.

## After Action Report

- Red run: `python -m unittest
  tests.test_substitution_graph_diagonal_witness_composition
  tests.test_substitution_graph_correctness_cases` failed before
  implementation because the new verifier module did not exist, the
  correctness-case manifest had no `diagonal_witness_composition_path`, and
  the fifth case still omitted the `diagonal_witness_composition` dependency.
- Green run: the same focused suite passed 22 tests after implementation.
- Live verifier checks: text and JSON
  `autarkic_systems.substitution_graph_diagonal_witness_composition` accepted
  1 composition with `diagonal-witness=1` and no failed subjects.
- Aggregate checks: `autarkic_systems.substitution_graph_correctness_cases
  --format json` accepted all five open cases and reported
  `diagonal_witness_composition` as an accepted dependency for the fifth case.
- Formal-confidence and status checks: `autarkic_systems.formal_confidence`
  remained accepted with the known fixed-point-construction blocker, and
  `autarkic_systems.project_status --format summary` remained accepted.
- Regression checks: the adjacent substitution-graph, representability,
  diagonal-construction, and fixed-point focused suite passed 69 tests;
  `python -m compileall autarkic_systems tests`, JSON parsing for the changed
  claim manifests, and `git diff --check` passed.
- Full suite: `python -m unittest discover` passed 1,232 tests in 429.444s.
