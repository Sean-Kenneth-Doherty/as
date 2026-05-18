# ADR-0254: Substitution Graph Correctness Cases

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0252 named the substitution graph formula-correctness proof target, and
ADR-0253 made that target visible to aggregate formal-confidence validation.
The target still says only that the proof is missing. That is true, but it is
not yet operational enough for the next proof work: future agents need to know
which checked surfaces must be turned into proof cases before the target can
move.

The project should decompose the correctness target into explicit open cases
without pretending the cases are proved.

## Decision

Add `claims/substitution_graph_correctness_cases.json` and
`autarkic_systems.substitution_graph_correctness_cases`.

The new surface records five open proof cases:

- codebook round-trip and decoding boundary;
- quotation-term closure for argument-code insertion;
- meta-level capture-avoiding substitution semantics;
- formula-schema relation to the checked graph target; and
- diagonal-witness composition.

Each case is tied to the checked correctness target and to the existing
dependency surface that currently provides executable evidence. The validator
loads and validates those dependencies, checks each case target, required
dependency list, status, future work, and non-claims, and rejects any proved
status.

This does not prove formula correctness, prove substitution representability,
prove the diagonal lemma, prove a fixed-point equation, implement an
arithmetized proof predicate, claim self-consistency, change runtime behavior,
change command semantics, add an evidence bundle, or alter GitHub submission
logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.substitution_graph_correctness_cases` and
  `claims/substitution_graph_correctness_cases.json` do not exist.
- The manifest records five open proof cases with explicit dependency paths.
- The validator checks the correctness target, formal codebook, quotation-term
  examples, formal substitution examples, formula candidate, and substitution
  representability witness dependencies.
- Healthy text and JSON reports expose five open cases and their dependency
  coverage.
- Unknown target IDs, missing case dependencies, missing non-claims, and
  proved-status overclaims fail closed with specific failure subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_correctness_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live substitution-graph correctness-cases text/JSON, live
  substitution-graph correctness text/JSON, live project-status summary,
  compileall, JSON checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The new manifest records five `proof-case-open` proof cases and binds each to
`AS-SUBSTITUTION-GRAPH-CORRECTNESS-TARGET`. The validator checks the formal
codebook, quotation-term examples, formal-substitution examples, formula
candidate, correctness target, and substitution-representability witness
dependencies, then verifies each case kind, dependency list, future work, and
non-claim boundary.

Focused validation first failed because the module did not exist, then passed
12 tests after implementation. This gives future proof work a concrete case
map without claiming any case is proved.
