# ADR-0249: Formal Confidence Substitution Graph Formula Dependency

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0248 added the first checked syntactic formula schema candidate for the
substitution graph target: `substitution_code(x,y) = z`. That candidate was
validated by its own CLI, but the aggregate formal-confidence target still did
not fail closed over it. Formal-confidence validation could therefore remain
accepted if `claims/substitution_graph_formula_candidates.json` disappeared or
drifted.

Because the current substitution route now depends on a formula schema
candidate as well as a graph target and witness, aggregate formal-confidence
validation should make that dependency explicit.

## Decision

Add a structured `substitution_graph_formula` configuration field to
`claims/formal_confidence_targets.json`, and make
`autarkic_systems.formal_confidence` load and validate that referenced formula
candidate surface.

This keeps formal-confidence validation aligned with the current
representability frontier while preserving the blocker on formula correctness
and real fixed-point construction.

This does not prove formula correctness, prove substitution representability,
prove the diagonal lemma, prove a fixed-point equation, implement an
arithmetized proof predicate, claim self-consistency, change runtime behavior,
change command semantics, add an evidence bundle, or alter GitHub submission
logic.

## Success Criteria

- Red tests fail before implementation because the checked target has no
  `substitution_graph_formula` required configuration field, the
  formal-confidence report does not expose an accepted substitution graph
  formula result, and missing substitution graph formula manifests do not
  reject formal-confidence validation.
- `claims/formal_confidence_targets.json` includes a structured
  `substitution_graph_formula` path.
- `autarkic_systems.formal_confidence` validates the referenced formula
  candidate surface with `autarkic_systems.substitution_graph_formula`.
- Healthy text and JSON reports expose `substitution graph formula accepted`.
- Missing or invalid substitution graph formula references fail closed as
  `target-substitution-graph-formula`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_formal_confidence_target
  tests.test_project_status_report`.
- Green: the same focused suite passes after implementation.
- Regression: run live formal-confidence text/JSON, live project-status
  summary, compileall, JSON checks, `git diff --check`, and the full default
  suite.

## After Action Report

Implemented on 2026-05-18.

The formal-confidence target now carries
`"substitution_graph_formula":
"claims/substitution_graph_formula_candidates.json"`. The validator loads
that manifest, runs the substitution-graph formula validator, reports
`substitution graph formula accepted` on the healthy path, and maps missing or
invalid references to `target-substitution-graph-formula`.

Focused validation first failed for the missing field and missing report
surface, then passed after implementation. The formal-confidence target
remains deliberately blocked on `fixed-point-construction`.
