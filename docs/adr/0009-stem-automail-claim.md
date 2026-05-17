# ADR-0009: Stem Automail Claim

Date: 2026-05-17

Status: Accepted

## Context

ADR-0008 added an executable stem automail transition subset. ADR-0005 and
ADR-0007 established the pattern that executable substrate behavior should be
named as predicate-backed AS claims. The automail reconfiguration behavior now
needs the same treatment.

## Decision

Add:

- an `automail_reconfigures_stem` predicate;
- tests for true and false automail reconfiguration cases;
- a corresponding `UC-STEM-AUTOMAIL-RECONFIGURES` claim in
  `claims/transition_claims.json`.

## Success Criteria

- Predicate tests fail before implementation and pass after implementation.
- The full manifest evaluator still passes all claim examples.
- The new claim has positive and negative executable examples.

## Consequences

- The first stem/reconfiguration behavior is now part of the machine-readable
  AS claim surface, not just a transition helper.

## After Action Report

Red step:

- `python -m unittest tests.test_transition_predicates` failed because
  `automail_reconfigures_stem` was not importable.

Green step:

- `python -m unittest tests.test_transition_predicates` passed 10 tests after
  implementation.
- `python -m unittest tests.test_claim_manifest` initially failed because the
  manifest loader did not preserve `automail` on parsed cells. After fixing the
  loader, it passed 4 tests.
- `python -m unittest discover` passed 30 tests.
- `jq -e claims/transition_claims.json` and `jq -e sources/manifest.json`
  passed.
- `git diff --check` passed.

Coverage limits:

- The claim covers automail commands `wr`, `wl`, `pr`, and `pl` through one
  representative positive and one representative negative manifest example.
- It still does not model full stem buffer semantics or a theorem-prover proof
  of the claim.
