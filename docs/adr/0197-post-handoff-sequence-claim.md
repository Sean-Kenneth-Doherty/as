# ADR-0197: Post-Handoff Sequence Claim

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0196 added a post-handoff signal witness showing that an accepted
`proc-l-init` neighbor delivery has a later behavioral consequence: the
recipient becomes `proc/left`, a binary follow-up input routes through the
existing fixed-cell logic, and processor memory toggles back to `right`.

That witness is currently executable and inspectable, but it is not yet a named
claim surface with manifest examples and proof-certificate checks. The project
already uses this pattern for transition and transition-chain behavior; the
post-handoff sequence should receive the same first proof-object layer before
it is promoted into any evidence bundle or aggregate status surface.

## Decision

Add a small network-sequence claim surface:

- a predicate over `PostHandoffSignalWitness`;
- a JSON claim manifest with positive and negative examples;
- proof certificates using `predicate-result` steps;
- a validator/CLI that checks examples and certificates together.

This will not add scheduler, timing, topology, output-clearing, or new command
semantics. It only names and checks the ADR-0196 witness behavior.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.network_sequence_claims` does not exist.
- The positive example proves a delivered `proc-l-init` handoff routes a later
  binary signal and toggles processor memory.
- Negative examples cover consumed write-buffer handoff and malformed follow-up
  input.
- Predicate-result proof certificates cover every claim example and reject
  incomplete certificate manifests.
- Text and JSON CLI output expose accepted claim/certificate status.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_claims`.
- Green: the same focused suite passes after implementation.
- Regression: run `python -m autarkic_systems.network_sequence_claims`, its JSON
  mode, `python -m compileall -q autarkic_systems tests`, `git diff --check`,
  and the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_network_sequence_claims` run failed because
`autarkic_systems.network_sequence_claims` did not exist.

The implementation added `autarkic_systems/network_sequence_predicates.py` with
`post_handoff_signal_routed`, plus `autarkic_systems/network_sequence_claims.py`
for loading, evaluating, proof-certificate checking, text output, and JSON
output. It also added `claims/network_sequence_claims.json` and
`claims/network_sequence_proof_certificates.json` with one positive
post-handoff routing example and two negative examples.

The focused network-sequence claim suite passed with 10 tests. Live text and
JSON claim validation accepted the checked-in claim surface. `compileall`, `git
diff --check`, and the full default suite also passed; the full suite ran 833
tests.
