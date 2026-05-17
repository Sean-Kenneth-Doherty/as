# ADR-0091: Neighbor Delivery Rejection Chain Claim

Date: 2026-05-17

## Status

Accepted.

## Context

The current neighbor delivery recipient chain already exercises a non-init
boundary: a sender can deliver a `write-buf-one` command token to a neighbor,
and the recipient rejects it because recipient-side non-init command execution
remains source-blocked.

That behavior is currently only a false example under the positive
`neighbor_delivery_consumed_by_recipient` claim. The negative path is important
enough to name directly, because it proves the composed chain preserves the
recipient non-init boundary after delivery rather than merely failing to
consume an init token.

## Decision

Add a second transition-chain predicate and claim:
`neighbor_delivery_rejected_by_recipient`, with claim ID
`UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`.

The claim will accept the narrow chain where:

- the sender performs a neighbor command-buffer delivery;
- the delivered output is installed as recipient upstream state;
- the recipient rejects the non-init command token; and
- the recipient remains otherwise unchanged at the rejection boundary.

This ADR does not implement non-init command execution. It only names and
checks the existing rejection boundary as a composed-chain claim.

## Success Criteria

- Red tests fail before implementation because the rejection predicate, claim,
  certificate, and language predicate symbol are missing.
- The new predicate accepts the checked non-init delivery rejection chain.
- The new predicate rejects the positive init-consumption chain.
- The chain claim manifest contains both positive-consumption and
  negative-rejection claims.
- Chain examples, proof certificates, object-language validation, chain claim
  CLI output, and the full suite remain green.

## Consequences

The first transition-chain claim surface now names both the successful
init-family handoff and the preserved non-init rejection boundary.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_chain_claim` fails
  before the rejection predicate and claim exist.
- Green: the focused claim test passes after implementation.
- Regression: run chain object-language and chain-claim CLI tests,
  `python -m autarkic_systems.chain_claims --format json`, `py_compile`,
  `git diff --check`, and the full default suite before commit.

## After Action Report

Implemented the delivered non-init rejection path as a named transition-chain
predicate and claim without widening recipient command execution semantics.

The red focused run, before implementation, failed in
`tests.test_neighbor_delivery_chain_claim` because
`neighbor_delivery_rejected_by_recipient` did not exist. After implementation:

- `python -m unittest tests.test_neighbor_delivery_chain_claim` passed 8
  tests.
- `python -m unittest tests.test_neighbor_delivery_chain_claim tests.test_chain_object_language tests.test_transition_chain_claim_cli`
  passed 20 tests.
- `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle tests.test_chain_evidence_bundle_registry tests.test_chain_demo_report`
  passed 29 tests.
- `python -m autarkic_systems.chain_claims --format json` reported
  `accepted: true`, `claim_count: 2`, `certificate_count: 2`, and
  `chain-examples: evaluated 7 examples`.
- `python -m autarkic_systems.chain_evidence_bundle --format json` still
  reported `accepted: true`, `result_count: 9`, and `failed_subjects: []`;
  its language validation detail updated to 28 language clauses and 4 surface
  clauses.
- `python -m py_compile autarkic_systems/transition_chain_predicates.py autarkic_systems/chain_claims.py tests/test_neighbor_delivery_chain_claim.py tests/test_transition_chain_claim_cli.py`
  passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 518 tests.

The chain claim surface now has both a positive consumed-handoff claim and a
positive rejection-boundary claim for the non-init delivered-token path.
