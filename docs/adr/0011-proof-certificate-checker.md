# ADR-0011: Proof Certificate Checker

Date: 2026-05-17

Status: Accepted

## Context

ADR-0010 chose a minimal AS-local proof-certificate checker as the first
proof-side apparatus. The current transition claims are already machine
readable in `claims/transition_claims.json`, and every claim has executable
positive and negative examples. What is missing is a small proof object that
states why a claim is currently accepted.

This checker should not pretend to be a general theorem prover. It should
validate explicit certificates over the current claim manifest, so AS gains an
inspectable proof-object surface before attempting Proflog, LeanTAP, or
Willard-style arithmetized proof codes.

## Decision

Add:

- `claims/proof_certificates.json` as the first proof-certificate manifest;
- `autarkic_systems/proof_certificates.py` to load and verify certificates;
- tests that require certificates to cover every manifest example and reject
  unknown claims, unknown rules, missing examples, and mismatched expectations.

The first certificate rule is `manifest-example`: a named example from
`claims/transition_claims.json` is evaluated with the claim's predicate checker
and must match both the manifest expectation and the certificate expectation.

## Success Criteria

- Red tests fail before implementation because the certificate checker is
  absent.
- The fast suite passes after implementation.
- The proof-certificate manifest covers every current transition claim.
- The checker rejects malformed or dishonest certificates without treating
  them as Python import/runtime crashes.

## Consequences

- AS now has proof objects in the smallest useful sense: auditable certificate
  records tied to claim IDs and executable witnesses.
- This remains below the bar for SJAS self-justification. It is a local proof
  certificate layer, not a semantic-tableaux theorem prover.
- Future ADRs can add rule clauses such as transition-witness, syntax-code,
  substitution-code, or eventually tableaux-proof without changing the current
  claim manifest contract.

## After Action Report

Red step:

- `python -m unittest tests.test_proof_certificates` failed with
  `ModuleNotFoundError: No module named 'autarkic_systems.proof_certificates'`.

Green step:

- Added `autarkic_systems/proof_certificates.py`.
- Added `claims/proof_certificates.json`.
- `python -m unittest tests.test_proof_certificates` passed 6 tests.
- `python -m unittest discover` passed 36 tests.
- `python -m py_compile autarkic_systems/proof_certificates.py
  tests/test_proof_certificates.py` passed.
- `jq -e . claims/proof_certificates.json`,
  `jq -e . claims/transition_claims.json`, and
  `jq -e . sources/manifest.json` passed.
- `git diff --check` passed.

Coverage limits:

- The only implemented certificate rule is `manifest-example`.
- The checker validates proof certificates against current executable
  transition-claim examples. It is not a general theorem prover and does not
  encode Willard-style arithmetized proof objects.
