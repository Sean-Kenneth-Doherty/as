# ADR-0198: Network Sequence Evidence Bundle

Date: 2026-05-18

## Status

Accepted.

## Context

ADR-0197 names and checks the post-handoff signal witness as
`UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED`, with manifest examples and
predicate-result proof certificates. That makes the behavior claimable, but it
is still not discoverable through an evidence-bundle registry.

The existing transition and transition-chain evidence bundles should not be
stretched to cover this witness. A post-handoff sequence is neither one
transition nor the existing two-step transition-chain claim surface. It needs a
small dedicated bundle shape that validates the sequence claim/proof surface,
the executable witness, the underlying delivery chain evidence, and relevant
source-status boundaries.

## Decision

Add a network-sequence evidence bundle module and registry for the post-handoff
signal witness. The bundle will validate:

- schema and required artifact paths;
- the named network-sequence claim example;
- the network-sequence proof certificate;
- the executable witness status for the positive example;
- the underlying neighbor-delivery chain evidence bundle; and
- source-status and boundary records.

This will not add scheduler, timing, topology, output-clearing, project-status,
or new command semantics.

## Success Criteria

- Red tests fail before implementation because
  `autarkic_systems.network_sequence_evidence_bundle` does not exist.
- The checked-in bundle names `UC-SEQUENCE-POST-HANDOFF-SIGNAL-ROUTED`,
  `post_handoff_signal_routed`, and the positive example.
- Bundle validation accepts the sequence claim, proof certificate, witness,
  underlying chain bundle, source statuses, and boundary text.
- Drifted expected witness status is rejected.
- A registry discovers and validates the checked-in bundle and rejects
  unregistered sibling bundle files.
- Text and JSON CLI output expose accepted bundle and registry status.
- Full repository tests remain green.

## Test Plan

- Red: `python -m unittest tests.test_network_sequence_evidence_bundle`.
- Green: the same focused suite passes after implementation.
- Regression: run bundle and registry CLIs in JSON mode, `python -m compileall
  -q autarkic_systems tests`, `git diff --check`, and the full default suite.

## After Action Report

Implemented. The red
`python -m unittest tests.test_network_sequence_evidence_bundle` run failed
because `autarkic_systems.network_sequence_evidence_bundle` did not exist.

The implementation added `autarkic_systems/network_sequence_evidence_bundle.py`,
`evidence/sequences/post_handoff_signal_bundle.json`, and
`evidence/sequences/manifest.json`. The validator checks the sequence claim
example, proof certificate, executable witness status, underlying registered
neighbor-delivery chain evidence bundle, referenced source-status files, and
boundary text.

The focused network-sequence evidence-bundle suite passed with 10 tests. Live
bundle and registry JSON CLI runs accepted the checked-in artifacts. `compileall`,
`git diff --check`, and the full default suite also passed; the full suite ran
843 tests.
