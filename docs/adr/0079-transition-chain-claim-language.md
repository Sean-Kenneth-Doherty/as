# ADR-0079: Transition Chain Claim Language

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0078 introduced a distinct transition-chain claim and proof-certificate
surface for the ADR-0077 two-step neighbor-delivery handoff. It deliberately
kept those chain claims out of the single-transition claim language because
chain examples involve sender state, recipient state, handoff state, and a
chain result.

That separation is correct, but it leaves the chain surface relying on
implicit Python and JSON shape. The single-transition claim surface already has
`language/transition_claim_language.json` plus a validator. Chain claims should
get the same minimal syntax discipline before more chain artifacts accumulate.

## Decision

Add a minimal chain-claim language:

- `language/transition_chain_claim_language.json`;
- `autarkic_systems/chain_object_language.py`; and
- `tests/test_chain_object_language.py`.

The language will name:

- Universal Cell term vocabulary reused by chain examples;
- chain statuses from `autarkic_systems.transition_chains.ChainStatus`;
- chain predicate symbols from
  `autarkic_systems.transition_chain_predicates`;
- chain sentence prefix `UC-CHAIN-`;
- proof-object rule `manifest-example`; and
- the active chain claim and certificate manifest paths.

This ADR does not add new chain behavior or new claim examples.

## Success Criteria

- Red tests fail before implementation because the chain object-language
  module or manifest is absent.
- The chain language manifest validates its required syntax classes and term
  vocabularies.
- The current chain claim and certificate surface validates against the
  language.
- Unknown chain predicates, unknown proof rules, and incomplete chain-status
  vocabularies are rejected.
- Existing transition-claim object-language validation remains unchanged.

## Consequences

Chain claims become explicit syntax objects instead of ad hoc JSON conventions.
The chain language remains intentionally small and separate from both the
single-transition claim language and any future IS(A)/SJAS formal language.

## Test Plan

- Red: `python -m unittest tests.test_chain_object_language` fails before the
  module and manifest exist.
- Green: the same focused test passes after adding the manifest and validator.
- Regression: run the chain claim tests, existing object-language tests, and
  the full default suite before commit.

## After Action Report

Implemented in `language/transition_chain_claim_language.json` and
`autarkic_systems/chain_object_language.py`, with focused tests in
`tests/test_chain_object_language.py`.

The focused red run failed because `autarkic_systems.chain_object_language` was
absent. The green implementation adds a narrow chain object language that
validates current chain terms, chain statuses, transition statuses, implemented
chain predicates, `UC-CHAIN-` sentence prefixes, manifest-example proof rules,
and the active chain claim/certificate manifest paths.

The validator also checks the current chain claim surface by replaying its
examples through the ADR-0077 chain helper, so incomplete chain-status
vocabularies fail against real evaluated examples rather than static manifest
shape alone.

Existing single-transition claim language validation remains unchanged.

Verification passed:

- focused red:
  `python -m unittest tests.test_chain_object_language` failed before the
  module was added;
- focused green:
  `python -m unittest tests.test_chain_object_language` passed 5 tests;
- adjacent chain-language/chain-claim/object-language stack passed 20 tests;
- JSON parsing passed for `language/transition_chain_claim_language.json`;
- `py_compile` passed for the new module and focused test;
- `git diff --check` passed;
- `python -m unittest discover` passed 464 tests; and
- the evidence registry JSON CLI still reported `accepted: true` and
  `bundle_count: 8`.
