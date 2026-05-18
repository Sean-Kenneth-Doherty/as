# ADR-0201: Network Sequence Object Language

Date: 2026-05-18

## Status

Accepted.

## Context

Network-sequence claims now have an executable witness, predicate checker,
claim/proof manifests, an evidence bundle, and aggregate project-status
coverage. They still lack the explicit object-language layer already present
for base transition claims and transition-chain claims.

Without that layer, the sequence claim surface is checked operationally but is
not yet made syntactically explicit: allowed terms, sequence statuses,
predicate symbols, sentence kinds, claim ID prefixes, proof-object rules, and
manifest pointers are implicit in Python and JSON conventions.

## Decision

Add a minimal object language for current network-sequence claims:

- `language/network_sequence_claim_language.json`;
- `autarkic_systems/network_sequence_object_language.py`;
- text and JSON CLI validation;
- manifest validation for required syntax classes and vocabulary;
- claim/proof validation against the language; and
- operator documentation updates.

This does not add new sequence behavior, claims, evidence bundles, project
status fields, proof rules, scheduler semantics, topology, timing, or command
semantics.

## Success Criteria

- Red tests fail before implementation because the sequence object-language
  module and language manifest do not exist.
- The checked-in language validates successfully against the current sequence
  claim and proof certificate.
- Unknown sequence predicates, unknown proof rules, and missing sequence-status
  vocabulary are rejected.
- Text and JSON CLIs expose accepted validation.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_object_language`.
- Green: the same focused suite passes after implementation.
- Regression: run adjacent sequence claim/evidence tests, `compileall`,
  `git diff --check`, and the full default suite.

## After Action Report

Implemented.

The red focused run failed immediately because
`autarkic_systems.network_sequence_object_language` and
`language/network_sequence_claim_language.json` did not exist.

The implementation adds the language manifest and validator/CLI. The validator
checks required syntax classes, term vocabulary, sequence predicate symbols,
sentence kind and claim ID prefix, proof-object rules, substrate manifest
pointers, current sequence claim examples, evaluated sequence statuses,
delivery chain statuses, follow-up transition statuses, and proof objects.

Focused verification passed 12 sequence object-language tests. Adjacent
verification across sequence object-language, sequence claims, and sequence
evidence passed 32 tests. The JSON CLI reported accepted
`as-network-sequence-claim-v1` with one claim and one certificate.
`compileall`, `git diff --check`, and the full default suite passed. The full
suite ran 860 tests.
