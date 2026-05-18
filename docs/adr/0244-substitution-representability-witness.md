# ADR-0244: Substitution Representability Witness

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0242 added the first checked diagonal seed built with
`substitution_code(n,n)`, and ADR-0243 made that seed visible to aggregate
formal-confidence validation. That still leaves a proof-frontier gap: the
current repository has a syntactic diagonal seed, but it has not checked even
the concrete meta-level substitution graph point needed by a later
representability proof.

The next safe step is not to claim substitution representability. It is to
record and validate the exact graph witness
`subst_code(seed, seed) -> closed quoted seed instance` for the current
diagonal route.

## Decision

Add `claims/substitution_representability_targets.json` and
`autarkic_systems.substitution_representability`.

The new surface validates one witness:

- the formula code is the checked ADR-0242 diagonal seed code;
- the argument code is the same seed code, expressing the self-application
  graph point;
- substituting the quotation term for that code into the seed produces the
  same closed output length and prefix as the checked diagonal instance; and
- the output has no free variables.

This records a concrete witness for later formalization while preserving that
AS still has no delta0 substitution graph formula, no substitution
representability proof, no diagonal lemma, no fixed-point equation proof, and
no self-consistency theorem.

This does not change aggregate formal-confidence validation yet, does not add
runtime behavior, does not change command semantics, does not add an evidence
bundle, and does not alter GitHub submission logic.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.substitution_representability` and
  `claims/substitution_representability_targets.json` do not exist.
- The manifest names
  `AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS`.
- The validator recomputes the formula code, argument code, output length,
  output prefix, and output free variables from the current diagonal seed,
  fixed-point target, and formal codebook.
- Healthy text and JSON reports expose the accepted witness and observed
  output length `296`.
- Unknown diagonal construction IDs, stale output facts, and overclaiming
  proved statuses fail closed with specific failure subjects.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_substitution_representability`.
- Green: the same focused suite passes after implementation.
- Regression: run diagonal-construction and project-status focused suites,
  live text/JSON CLI validation, compileall, JSON checks, `git diff --check`,
  and the full default suite.

## After Action Report

Implemented on 2026-05-18.

The new manifest records
`AS-SUBSTITUTION-REPRESENTABILITY-DIAGONAL-SEED-WITNESS` as
`representability-witness-not-proof`. The validator loads the checked diagonal
construction, fixed-point target, formal codebook, and Willard map; rebuilds
the seed; self-applies the seed code as a quotation term; and verifies that
the output graph point is closed and has code length `296`.

Focused validation first failed because the module did not exist, then passed
12 tests after implementation. This moves the diagonal route one checked step
closer to a real representability proof while preserving all theorem-level
blockers.
