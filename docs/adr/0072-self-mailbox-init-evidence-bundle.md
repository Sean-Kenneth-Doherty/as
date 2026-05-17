# ADR-0072: Self-Mailbox Init Evidence Bundle

Date: 2026-05-17

## Status

Accepted.

## Context

ADR-0065 through ADR-0071 created a registry and CLI for integrated transition
evidence bundles. The registry currently covers recipient-side command-message
execution and rejection boundaries, but it does not yet cover the earlier
self-mailbox init-family execution surface from ADR-0030 through ADR-0033.

That surface already has a runtime transition, named claim, proof certificate,
schematic trace, rendered SVG, and source-status boundary. It should be a
registered bundle so the evidence registry includes both the self-target and
recipient command-message fronts.

While integrating it, the bundle must require the schematic trace and claim
example to describe the same concrete transition, including incidental
control/buffer values. If those artifacts drift, the bundle should fail rather
than silently treating two nearby examples as one proof path.

## Decision

Add `evidence/self_mailbox_init_bundle.json` and register it in
`evidence/manifest.json`.

The bundle will point to:

- `UC-STEM-SELF-MAILBOX-INIT-COMMAND`;
- the positive manifest example `processor left mailbox init`;
- `claims/transition_claims.json`;
- `claims/proof_certificates.json`;
- `schematics/self_mailbox_init_trace.json`;
- `schematics/self_mailbox_init_trace.svg`;
- `sources/prc_hardware_witness_map.json`; and
- the source-status files that keep self-mailbox init-family execution,
  recipient non-init, `standard-signal`, and write-buffer boundaries explicit.

The checked-in self-mailbox trace and SVG will be aligned with the named claim
example so the integrated validator proves one exact transition path.

This ADR does not add Universal Cell runtime behavior.

## Success Criteria

- Red tests fail before implementation because the self-mailbox init bundle is
  absent.
- The bundle records the claim ID, predicate, positive example, transition
  function, status, trace path, SVG path, proof certificate path, hardware
  witness map, and source-status paths.
- Validation proves the claim example exists and evaluates as expected.
- Validation proves the proof certificate for the claim is accepted.
- Validation proves the schematic trace executes, validates against the PRC
  hardware witness map, and exactly matches the named claim example.
- Validation proves the committed SVG matches renderer output.
- The evidence registry contains four bundles and the CLI validates all four.
- Runtime behavior remains unchanged.

## Consequences

The evidence registry now covers the direct self-mailbox init-family execution
surface alongside recipient command-message bundles. The trace/claim alignment
also removes a small documentation drift path around incidental control and
buffer fixture values.

## Test Plan

- Red: `python -m unittest tests.test_self_mailbox_init_evidence_bundle` fails
  before the bundle artifact is added.
- Green: the same focused test passes after adding the bundle, registry entry,
  and trace/SVG alignment.
- Regression: run evidence registry/CLI tests, adjacent self-mailbox tests, and
  the full default suite before commit.

## After Action Report

Implemented in `evidence/self_mailbox_init_bundle.json` and registered in
`evidence/manifest.json`.

The focused red run failed because
`evidence/self_mailbox_init_bundle.json` was absent. The green implementation
adds the bundle for the positive `processor left mailbox init` example under
`UC-STEM-SELF-MAILBOX-INIT-COMMAND`.

The integration exposed a small fixture drift: the existing self-mailbox trace
and the claim example used different incidental control/buffer values. The
trace and generated SVG now match the named claim example exactly, so bundle
validation proves one concrete transition across claim, proof, trace, render,
hardware witness map, and source-status boundaries.

The evidence registry and CLI now validate four bundles: recipient init
execution, recipient single-token non-init rejection, recipient
simultaneous-token rejection, and direct self-mailbox init execution.

Runtime behavior remains unchanged. AS still does not execute self-mailbox
non-init, recipient non-init, `standard-signal` command-token, or write-buffer
command-token semantics.
