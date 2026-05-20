# ADR-0269: Fixed-Point Bridge Equality Evaluation Domain

Date: 2026-05-19

## Status

Accepted.

## Context

ADR-0267 added finite bridge-equality alignment for the fourth fixed-point
construction case, and ADR-0268 added finite equation-lifting alignment for
the fifth case. The fourth case still has a sharper executable next step:
evaluate the checked left bridge term,
`substitution_code(quote(seed), quote(seed))`, and compare its meta-level
output tokens with the right bridge term, `quote(diagonal_instance)`.

The existing equation bridge already checks that the left bridge term has the
right syntactic form and that the substitution witness output matches the
diagonal instance code. The existing bridge-equality alignment checks that the
bridge route matches the formula-schema witness relation. The next useful
surface is a finite evaluation point that connects those two facts directly
without claiming a proof of bridge equality.

## Decision

Add `claims/fixed_point_bridge_equality_evaluation.json` and
`autarkic_systems.fixed_point_bridge_equality_evaluation`.

The verifier will derive one bridge-equality evaluation point and check that:

- the bridge-equality construction case remains `proof-case-open`;
- the construction case requires the equation bridge, substitution
  representability surface, graph correctness cases, bridge-equality alignment,
  and this evaluation surface;
- the fixed-point target, equation bridge, substitution representability
  surface, bridge-equality alignment, and codebook remain accepted;
- the left bridge term is `substitution_code(quote(seed), quote(seed))`;
- the left formula quotation decodes to the current diagonal seed;
- the self-application argument quotation recovers the same seed code;
- evaluating the left substitution-code term produces the current 296-token
  diagonal instance code;
- the evaluated output matches the substitution witness output and the right
  quoted bridge term;
- the bridge-equality alignment remains accepted and route-aligned; and
- the observed bridge equation code length stays at the checked 4815-token
  surface.

Make the `bridge-equality-proof` construction case depend on this verifier
through a new `bridge_equality_evaluation_path` field in
`claims/fixed_point_construction_cases.json`.

This is finite meta-level evaluation evidence only. It does not prove the
general bridge equality, fixed-point equation, arithmetized proof predicate,
or self-consistency.

## Success Criteria

- Red tests fail before implementation because the bridge-equality evaluation
  verifier and manifest do not exist, the construction-case manifest has no
  `bridge_equality_evaluation_path`, and the fourth construction case does not
  depend on `bridge_equality_evaluation`.
- The new verifier accepts the checked bridge-equality evaluation domain.
- The verifier derives one evaluation point from the current fixed-point
  target, equation bridge, substitution representability surface,
  bridge-equality alignment, and codebook surfaces.
- Text and JSON output expose accepted status, evaluation count, source-kind
  counts, formula/argument/output lengths, bridge-equation length, evaluation
  booleans, route booleans, and no failed subjects.
- Stale evaluation counts reject.
- Stale output length facts reject.
- Stale bridge-equation length facts reject.
- Missing non-claims reject.
- The construction-case validator fails closed over the new verifier and
  reports `bridge_equality_evaluation` as an accepted dependency on the
  healthy path.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest
  tests.test_fixed_point_bridge_equality_evaluation
  tests.test_fixed_point_construction_cases`.
- Green: the same focused suite passes after implementation.
- Regression: run live bridge-equality-evaluation text/JSON, live
  construction-cases text/JSON, live formal-confidence text/JSON, live
  project-status summary, compileall, changed JSON parsing, `git diff --check`,
  adjacent fixed-point construction tests, and the full default suite.

## After Action Report

ADR-0269 added the finite bridge-equality evaluation surface intended by the
decision. The implementation derives one evaluation point from the current
construction-case map, fixed-point target, equation bridge, substitution
representability surface, bridge-equality alignment, and codebook. It checks
that the current left `substitution_code(quote(seed), quote(seed))` term
evaluates to the same 296-token diagonal instance code exposed by the
substitution witness and by the right quoted bridge term.

The construction-case validator now fails closed over the new
`bridge_equality_evaluation_path` and requires `bridge_equality_evaluation` as
the fifth dependency of the `bridge-equality-proof` case. The implementation
kept that proof case open and preserved the explicit non-claims: this is not a
general bridge equality proof, fixed-point equation proof, arithmetized proof
predicate, or self-consistency theorem.

Observed effect: the fourth fixed-point construction case now has both route
alignment evidence and a concrete meta-level evaluation point. The remaining
work is still the general proof that
`substitution_code(quote(seed), quote(seed))` denotes
`quote(diagonal_instance)` for the checked bridge target, followed by lifting
that bridge equality through the selected `pi1` target context.
