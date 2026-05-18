# ADR-0250: Substitution Graph Witness Evaluator

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0248 added the first checked syntactic formula schema candidate for the
substitution graph target, `substitution_code(x,y) = z`, and ADR-0249 made
that candidate visible to aggregate formal-confidence validation. The schema
validator checked that the formula can be encoded and that the checked witness
instance is closed, but it still did not evaluate even the concrete witness
relation inside that closed instance.

The next useful step is not a general formula correctness proof. It is a
small executable evaluator for the checked witness instance: decode the quoted
formula code, decode the quoted argument code, substitute the argument
quotation into the decoded formula at the witness variable, encode the result,
and compare that output code with the quoted right-hand side.

## Decision

Extend `claims/substitution_graph_formula_candidates.json` and
`autarkic_systems.substitution_graph_formula` with one concrete witness
evaluation check.

The validator now records and checks:

- whether the closed witness relation evaluates true;
- the evaluated output code length `296`; and
- the evaluated output prefix
  `[41, 1, 22, 11, 1, 18, 17, 13, 13, 13, 13, 13]`.

The evaluator uses only the existing formal codebook decoder, quotation-term
decoder, and capture-avoiding substitution helper. It does not prove that the
formula correctly represents all meta-level substitutions.

This does not prove formula correctness, prove substitution representability,
prove the diagonal lemma, prove a fixed-point equation, implement an
arithmetized proof predicate, claim self-consistency, change runtime behavior,
change command semantics, add an evidence bundle, or alter GitHub submission
logic.

## Success Criteria

- Red tests fail before implementation because formula candidates do not
  expose witness-relation truth, evaluated output code length, or evaluated
  output prefix.
- The manifest records expected witness relation truth and evaluated output
  code facts.
- The validator evaluates the concrete checked witness relation from the
  closed formula instance rather than only checking that the instance encodes.
- Healthy text and JSON reports expose the relation truth and evaluated output
  length.
- Stale evaluated output facts and false expected relation truth fail closed
  as `substitution-graph-formula-witness-evaluation`.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_graph_formula`.
- Green: the same focused suite passes after implementation.
- Regression: run live substitution-graph formula text/JSON, live
  formal-confidence text/JSON, live project-status summary, compileall, JSON
  checks, `git diff --check`, and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The formula candidate manifest now records that the checked witness relation
holds and that its evaluated output code has length `296` with the expected
prefix. The validator decodes the witness instance quotation terms, replays
the concrete substitution through the current formal codebook, compares the
evaluated output code with the quoted right-hand side, and reports
`concrete witness relation evaluated true` on the healthy path.

Focused validation first failed because the candidate dataclass, JSON payload,
text report, and stale-evaluation rejection path did not exist, then passed
15 tests after implementation. This strengthens the checked formula schema
surface while preserving all proof-level blockers.
