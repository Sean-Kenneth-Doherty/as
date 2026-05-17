# ADR-0075: Command-Buffer Unsupported Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0074 registered the completed self-target init command-buffer dispatch as
an integrated evidence bundle. The sibling self-target non-init command-buffer
boundary from ADR-0041 through ADR-0043 remains outside the evidence registry.

That boundary is the checkable reason AS does not execute completed
self-target `standard-signal`, `write-buf-zero`, or `write-buf-one`
command-buffer tokens. It already has a named claim, proof certificate,
schematic trace, rendered SVG, and source-status boundary.

The registry should cover this negative command-buffer frontier next, so
decoded self-target command buffers have both their supported init path and
unsupported non-init path represented as integrated evidence.

## Decision

Add `evidence/command_buffer_unsupported_bundle.json` and register it in
`evidence/manifest.json`.

The bundle will point to:

- `UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED`;
- the positive manifest example `self write buffer command remains appended`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/command_buffer_unsupported_trace.json`;
- `schematics/command_buffer_unsupported_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the source-status files that keep self-target non-init,
  `standard-signal`, write-buffer, and init-family boundaries explicit.

This ADR does not add Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the unsupported command-buffer
  bundle is absent.
- The bundle records the claim ID, predicate, positive example, transition
  function, status, trace path, SVG path, proof certificate path, hardware
  witness map, and source-status paths.
- Validation proves the claim example exists and evaluates as expected.
- Validation proves the proof certificate for the claim is accepted.
- Validation proves the schematic trace executes, validates against the PRC
  hardware witness map, and exactly matches the named claim example.
- Validation proves the committed SVG matches renderer output.
- The evidence registry contains seven bundles and the CLI validates all
  seven.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry now covers both decoded self-target command-buffer
outcomes: supported init-family dispatch and unsupported non-init append
preservation. Full `standard-signal` and write-buffer command-token execution
remain source-blocked.

## Test Plan

- Red: `python -m unittest tests.test_command_buffer_unsupported_evidence_bundle`
  fails before the bundle artifact is added.
- Green: the same focused test passes after adding the bundle and registry
  entry.
- Regression: run evidence registry/CLI tests, adjacent unsupported
  command-buffer tests, and the full default suite before commit.

## After Action Report

Implemented in `evidence/command_buffer_unsupported_bundle.json` and
registered in `evidence/manifest.json`.

The focused red run failed because
`evidence/command_buffer_unsupported_bundle.json` was absent. The green
implementation adds the bundle for the positive
`self write buffer command remains appended` example under
`UC-STEM-COMMAND-BUFFER-UNSUPPORTED-APPENDED`.

The command-buffer unsupported trace already matched the named claim example
exactly, so no trace or SVG regeneration was needed. The slice did correct one
human documentation drift: `docs/command-buffer-unsupported-svg.md` now names
the active control rail as `[0, 1, 0]`, matching the trace, tests, and rendered
SVG.

Bundle validation now proves one completed self-target non-init command-buffer
append boundary across claim, proof, trace, render, hardware witness map, and
source-status boundaries.

The evidence registry and CLI now validate seven bundles: recipient init
execution, recipient single-token non-init rejection, recipient
simultaneous-token rejection, direct self-mailbox init execution, direct
self-mailbox unsupported preservation, completed self-target command-buffer
init dispatch, and completed self-target non-init command-buffer append
preservation.

Runtime behavior remains unchanged. AS still does not execute self-target
non-init, recipient non-init, `standard-signal` command-token, or write-buffer
command-token semantics.
