# ADR-0007: Transition Claim Manifest

Date: 2026-05-17

Status: Accepted

## Context

ADR-0005 introduced named predicates over Universal Cell transition results.
ADR-0006 ranked formalizing those predicates as the highest-leverage next
problem. AS now needs a machine-readable bridge from predicate code to explicit
claims, preconditions, and examples.

## Decision

Add:

- `claims/transition_claims.json`: a machine-readable manifest of transition
  claims.
- `autarkic_systems/claim_manifest.py`: loader and evaluator for claim
  examples.
- `tests/test_claim_manifest.py`: fast tests proving the manifest is valid and
  the examples execute against the predicate functions.

## Success Criteria

- Tests fail before the loader/manifest exist and pass afterward.
- Every claim references an implemented predicate checker.
- Each claim has at least one positive and one negative executable example.
- The manifest remains JSON so it can later be consumed by proof or report
  tools.

## Consequences

- Transition predicates become first-class AS claims instead of only Python
  functions.
- Future ADRs can add proof objects or proof-apparatus clauses behind the same
  stable claim IDs.

## After Action Report

Red step:

- `python -m unittest tests.test_claim_manifest` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems.claim_manifest'`
  before the loader existed.

Green step:

- `python -m unittest tests.test_claim_manifest` passed 4 tests.
- `python -m unittest discover` passed 20 tests.
- `jq -e claims/transition_claims.json` passed.
- `git diff --check` passed.

Coverage limits:

- The manifest names executable claims and examples; it does not yet encode
  proof objects or connect to an external proof apparatus.
- Claim examples are intentionally small fixtures for the current fixed-role
  transition probe.
