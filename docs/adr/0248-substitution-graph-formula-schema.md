# ADR-0248: Substitution Graph Formula Schema

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0246 recorded the target boundary for a future delta0 formula representing
the `substitution_code` graph, and ADR-0247 made that target visible to
aggregate formal-confidence validation. That still left the target at
`graph-formula-target-not-constructed`.

The next useful step is to construct the first checked syntactic formula
schema for that target while preserving the proof boundary. The candidate can
state the intended graph relation as `substitution_code(x,y) = z`, but AS has
not yet proved that this formula correctly represents meta-level substitution.

## Decision

Add `claims/substitution_graph_formula_candidates.json` and
`autarkic_systems.substitution_graph_formula`.

The new surface validates one formula candidate:

- candidate ID `AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA`;
- target ID `AS-SUBSTITUTION-GRAPH-DELTA0-TARGET`;
- witness ID `AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS`;
- formula node `substitution_code(x,y) = z`;
- expected formula code `[21, 18, 11, 1, 11, 2, 11, 3]`; and
- a closed witness instance produced by substituting quoted witness codes for
  `x`, `y`, and `z`.

This records the first concrete formula schema candidate without proving
formula correctness, substitution representability, a diagonal lemma, a
fixed-point equation, or self-consistency.

This does not change aggregate formal-confidence validation yet, does not add
runtime behavior, does not change command semantics, does not add an evidence
bundle, and does not alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.substitution_graph_formula` and
  `claims/substitution_graph_formula_candidates.json` do not exist.
- The manifest names `AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA`.
- The validator checks formal-language, codebook, substitution-graph target,
  and substitution-representability witness dependencies.
- The formula schema is exactly `substitution_code(x,y) = z` over the graph
  variables from ADR-0246.
- Healthy text and JSON reports expose formula code length `8` and witness
  instance code length `4815`.
- Unknown target IDs, stale formula codes, stale witness-instance facts,
  missing `substitution_code`, and proved-status overclaims fail closed with
  specific failure subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_formula`.
- Green: the same focused suite passes after implementation.
- Regression: run substitution-graph formula text/JSON, related
  substitution-graph target and project-status suites, live project-status
  summary, compileall, JSON checks, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented on 2026-05-18.

The new manifest records `AS-SUBSTITUTION-GRAPH-DELTA0-SCHEMA` as
`formula-schema-not-proved`. The validator loads the formal arithmetic
language, formal codebook, substitution graph target, substitution
representability witness, and Willard map; checks that the formula node is
exactly `substitution_code(x,y) = z`; verifies the formula code
`[21, 18, 11, 1, 11, 2, 11, 3]`; and constructs the closed witness instance
with code length `4815`.

Focused validation first failed because the module did not exist, then passed
13 tests after implementation. This moves the representability route from a
named graph target to a checked syntactic formula schema while preserving all
proof-level blockers.
