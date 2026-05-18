# ADR-0119: Self Non-Init Boundary Coverage

Date: 2026-05-18

## Status

Accepted.

## Context

AS already has named unsupported-boundary claims for two self-command surfaces:

- `UC-STEM-SELF-MAILBOX-UNSUPPORTED-PRESERVED`, covering unresolved
  self-mailbox commands; and
- `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED`, covering unresolved
  self-target completed command buffers.

Both claims describe the same non-init command frontier:
`standard-signal`, `write-buf-zero`, and `write-buf-one`. Their current
positive manifest coverage is thinner than the prose boundary, however. The
self-mailbox claim has one positive `write-buf-one` preservation example, and
the command-buffer claim has one positive self `write-buf-one` append-boundary
example.

That is enough to test the predicate shape, but it leaves the manifest/proof
surface less explicit than the AS boundary now reported by project status.

## Decision

Expand the existing manifest examples and proof-certificate steps so both
self-command unsupported-boundary claims have positive examples for all three
currently blocked non-init command tokens:

- `standard-signal`;
- `write-buf-zero`; and
- `write-buf-one`.

This ADR does not change Universal Cell runtime behavior and does not resolve
the command-token semantics frontier. It strengthens the current rejection and
preservation boundary by making each blocked self-command token explicit in the
claim/proof surface.

## Success Criteria

- Red tests fail before artifact updates because the self-mailbox unsupported
  claim lacks positive manifest examples for `standard-signal` and
  `write-buf-zero`.
- Red tests fail before artifact updates because the self-target command-buffer
  unsupported claim lacks positive manifest examples for self
  `standard-signal` and self `write-buf-zero`.
- The proof-certificate manifest covers every new manifest example.
- Manifest examples evaluate to their declared expectations.
- Existing evidence bundles, project status, and full repository tests remain
  green.
- Project status continues to report the same blocked command-token frontier.

## Consequences

The executable claim surface now matches the stated AS boundary more closely:
each unresolved self-command token has an explicit positive preservation or
append-boundary example. Later work that executes any of these commands must
replace or refine a specific manifest/proof example instead of treating the
old `write-buf-one` example as a loose representative.

## Test Plan

- Red: run
  `python -m unittest tests.test_self_mailbox_unsupported_claim tests.test_command_buffer_unsupported_claim`
  after adding tests that require all three non-init positive examples.
- Green: update `claims/transition_claims.json` and
  `claims/proof_certificates.json`, then rerun the focused claim tests.
- Regression: run proof-certificate, evidence-bundle, project-status,
  `py_compile`, `git diff --check`, status text/JSON, and full default suite
  before commit.

## After Action Report

The red run of
`python -m unittest tests.test_self_mailbox_unsupported_claim tests.test_command_buffer_unsupported_claim`
ran 13 tests and failed the two new coverage assertions because the manifest
positive examples named only `write-buf-one`, not `standard-signal` or
`write-buf-zero`.

The implementation added positive manifest examples for all three unsupported
self-mailbox commands and all three unsupported self-target command-buffer
completions. It also added matching `manifest-example` proof-certificate steps
for every new example. Universal Cell runtime behavior was unchanged.

Verification passed with:

- `python -m unittest tests.test_self_mailbox_unsupported_claim tests.test_command_buffer_unsupported_claim tests.test_proof_certificates` (19 tests)
- `python -m unittest tests.test_self_mailbox_unsupported_evidence_bundle tests.test_command_buffer_unsupported_evidence_bundle tests.test_evidence_bundle_registry tests.test_project_status_report` (62 tests)
- `python -m py_compile autarkic_systems/claim_manifest.py autarkic_systems/proof_certificates.py tests/test_self_mailbox_unsupported_claim.py tests/test_command_buffer_unsupported_claim.py`
- `python -m json.tool claims/transition_claims.json`
- `python -m json.tool claims/proof_certificates.json`
- `git diff --check`
- `python -m autarkic_systems.project_status`
- `python -m autarkic_systems.project_status --format json`
- `python -m autarkic_systems.evidence_bundle --registry evidence/manifest.json --format json`
- `python -m unittest discover` (577 tests)
