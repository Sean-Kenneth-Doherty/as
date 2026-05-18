# ADR-0094: Neighbor Delivery Rejection Chain Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0091 through ADR-0093 promoted the delivered non-init rejection path into a
chain claim, JSON trace, and SVG view. The positive init-consumption chain has
an integrated evidence bundle, but the rejection path still lacks the same
cross-layer bundle and registry coverage.

Without a bundle, the rejection chain can drift across claim, proof, language,
trace, SVG, underlying transition bundles, and source-status files without
being batch-validated by the transition-chain evidence registry.

## Decision

Add `evidence/chains/neighbor_delivery_rejection_chain_bundle.json` and
register it in `evidence/chains/manifest.json`.

The rejection bundle ties together:

- `UC-CHAIN-NEIGHBOR-DELIVERY-RECIPIENT-REJECTED`;
- `neighbor_delivery_rejected_by_recipient`;
- the positive rejection example from the chain claim manifest;
- the rejection chain trace and SVG;
- the neighbor command-buffer delivery transition bundle;
- the recipient non-init command rejection transition bundle; and
- source-status records that keep non-init, `standard-signal`, and
  write-buffer execution blocked.

## Success Criteria

- Red tests fail before implementation because the rejection bundle and
  registry entry are missing.
- The rejection bundle validates across schema, claim example, proof,
  language, trace, SVG, transition bundles, source statuses, and boundary
  terms.
- The chain evidence registry lists and validates two bundles.
- Chain registry completeness catches any unregistered sibling bundle files.
- Full repository tests remain green.

## Consequences

Both current transition-chain claims now have integrated evidence-bundle
coverage and registry discovery.

## Test Plan

- Red: `python -m unittest tests.test_neighbor_delivery_rejection_chain_evidence_bundle tests.test_chain_evidence_bundle_registry`
  fails before the bundle and registry entry exist.
- Green: the focused rejection bundle and registry tests pass after
  implementation.
- Regression: run chain evidence CLI JSON for the rejection bundle and
  registry, `py_compile`, `git diff --check`, and the full default suite before
  commit.

## After Action Report

Implemented the rejection chain evidence bundle and registered it alongside
the consumed chain bundle.

The red focused run, before implementation, failed in
`tests.test_neighbor_delivery_rejection_chain_evidence_bundle` and
`tests.test_chain_evidence_bundle_registry` because the rejection bundle file
and registry entry were missing. After implementation:

- `python -m unittest tests.test_neighbor_delivery_rejection_chain_evidence_bundle tests.test_chain_evidence_bundle_registry`
  passed 17 tests.
- `python -m unittest tests.test_neighbor_delivery_chain_evidence_bundle tests.test_neighbor_delivery_rejection_chain_evidence_bundle tests.test_chain_evidence_bundle_registry tests.test_chain_evidence_cli_target_selection`
  passed 29 tests.
- `python -m autarkic_systems.chain_evidence_bundle --bundle evidence/chains/neighbor_delivery_rejection_chain_bundle.json --format json`
  reported `accepted: true`, `result_count: 9`, and `failed_subjects: []`.
- `python -m autarkic_systems.chain_evidence_bundle --registry evidence/chains/manifest.json --format json`
  reported `accepted: true`, `bundle_count: 2`, and `failed_subjects: []`.
- `python -m py_compile autarkic_systems/chain_evidence_bundle.py tests/test_neighbor_delivery_rejection_chain_evidence_bundle.py tests/test_chain_evidence_bundle_registry.py`
  passed.
- `git diff --check` passed.
- `python -m unittest discover` passed 530 tests.

The chain evidence registry now validates both current composed-chain paths:
init-family consumption and non-init rejection.
